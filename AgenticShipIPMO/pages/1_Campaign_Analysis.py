import os
import json
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _path(filename):
    return os.path.join(BASE_DIR, "model", filename)

st.set_page_config(page_title="Campaign Analysis", layout="wide")

# load model + thresholds
@st.cache_resource
def load_resources():
    with open(_path("xgb_model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(_path("feature_cols.json")) as f:
        feature_cols = json.load(f)
    with open(_path("thresholds.json")) as f:
        t = json.load(f)
    return model, feature_cols, t["HIGH_THRESHOLD"], t["MEDIUM_THRESHOLD"]

model, feature_cols, HIGH_T, MED_T = load_resources()

st.title("Campaign Analysis")
st.caption("Upload session data to see which customers to target and how.")
st.divider()

# --- file upload ---
uploaded = st.file_uploader("Upload session CSV", type=["csv"])

if not uploaded:
    # show a clear instruction with expected columns
    st.info("Upload a CSV file with session data. Use the sample below as a template.")
    sample = pd.DataFrame({
        "PageValues":              [45.2, 0.0, 120.5, 8.3, 0.0],
        "ProductRelated":          [5,    1,   12,    3,   0],
        "ProductRelated_Duration": [300,  45,  900,   180, 10],
        "BounceRates":             [0.01, 0.20,0.005, 0.05,0.35],
        "ExitRates":               [0.03, 0.25,0.02,  0.08,0.40],
        "Administrative":          [0,    2,   1,     0,   1],
        "Administrative_Duration": [0,    120, 60,    0,   30],
        "Informational":           [0,    0,   1,     0,   0],
        "Informational_Duration":  [0,    0,   30,    0,   0],
        "SpecialDay":              [0.0,  0.0, 0.4,   0.0, 0.0],
        "Month":                   ["May","Feb","Nov","Mar","Aug"],
        "VisitorType":             ["Returning_Visitor","New_Visitor","Returning_Visitor","New_Visitor","New_Visitor"],
        "Weekend":                 [False,True, False, False,True],
        "OperatingSystems":        [2,    1,    3,     2,    1],
        "Browser":                 [2,    1,    2,     2,    1],
        "Region":                  [1,    3,    2,     1,    4],
        "TrafficType":             [2,    1,    4,     2,    3],
    })
    st.download_button("Download sample CSV", sample.to_csv(index=False),
                       file_name="sample_sessions.csv", mime="text/csv")
    st.stop()

# --- load and score ---
df_raw = pd.read_csv(uploaded)
st.success(f"Loaded {len(df_raw)} sessions.")

# build feature matrix — same encoding as training
MONTH_COLS   = [c for c in feature_cols if c.startswith("Month_")]
VISITOR_COLS = [c for c in feature_cols if c.startswith("VisitorType_")]

NUMERIC = [
    'Administrative','Administrative_Duration','Informational','Informational_Duration',
    'ProductRelated','ProductRelated_Duration','BounceRates','ExitRates',
    'PageValues','SpecialDay','OperatingSystems','Browser','Region','TrafficType'
]

@st.cache_data
def score_sessions(df_raw):
    rows = []
    for _, row in df_raw.iterrows():
        r = {col: 0 for col in feature_cols}
        for col in NUMERIC:
            if col in df_raw.columns:
                r[col] = row.get(col, 0)
        r['Weekend'] = 1 if str(row.get('Weekend', 'False')).lower() == 'true' else 0
        month_col = f"Month_{row.get('Month', '')}"
        if month_col in r:
            r[month_col] = 1
        vtype_col = f"VisitorType_{row.get('VisitorType', 'New_Visitor')}"
        if vtype_col in r:
            r[vtype_col] = 1
        rows.append(r)

    X = pd.DataFrame(rows)[feature_cols]
    probs = model.predict_proba(X)[:, 1]

    tiers = []
    for p in probs:
        if p >= HIGH_T:
            tiers.append("HIGH")
        elif p >= MED_T:
            tiers.append("MEDIUM")
        else:
            tiers.append("LOW")

    result = df_raw.copy()
    result["Intent_Score"] = np.round(probs, 4)
    result["Tier"]         = tiers
    result["Action"]       = result["Tier"].map({
        "HIGH":   "Urgency Banner",
        "MEDIUM": "10% Discount",
        "LOW":    "Retargeting Ad"
    })
    result["Campaign_Cost"] = result["Tier"].map({
        "HIGH": 0.00, "MEDIUM": 5.00, "LOW": 0.50
    })
    return result

df = score_sessions(df_raw)

# --- summary metrics ---
st.divider()
st.subheader("Summary")

total  = len(df)
high   = (df["Tier"] == "HIGH").sum()
medium = (df["Tier"] == "MEDIUM").sum()
low    = (df["Tier"] == "LOW").sum()
total_cost    = df["Campaign_Cost"].sum()
baseline_cost = total * 5.0  # if you discounted everyone
saving        = baseline_cost - total_cost
saving_pct    = saving / baseline_cost * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Sessions",   total)
c2.metric("HIGH Intent",      f"{high} ({high/total:.0%})")
c3.metric("MEDIUM Intent",    f"{medium} ({medium/total:.0%})")
c4.metric("LOW Intent",       f"{low} ({low/total:.0%})")
c5.metric("Campaign Cost",    f"€{total_cost:,.2f}")
c6.metric("Saved vs Baseline",f"€{saving:,.0f} ({saving_pct:.0f}%)")

st.divider()

# --- tier breakdown table ---
st.subheader("Tier Breakdown — What to Do Per Group")

breakdown = pd.DataFrame({
    "Tier":           ["🟢 HIGH",        "🟡 MEDIUM",       "🔴 LOW"],
    "Sessions":       [high,             medium,             low],
    "Share":          [f"{high/total:.0%}", f"{medium/total:.0%}", f"{low/total:.0%}"],
    "Recommended Action": ["Urgency Banner", "10% Discount Coupon", "Retargeting Ad"],
    "Why":            [
        "Already close to buying — just needs a nudge, no discount needed",
        "Interested but hesitating — small incentive usually converts them",
        "Low engagement this session — cheaper to re-engage later via ad"
    ],
    "Cost/session":   ["€0.00",          "€5.00",            "€0.50"],
    "Total Cost":     [f"€{high*0:.0f}", f"€{medium*5:.0f}", f"€{low*0.5:.0f}"],
})
st.dataframe(breakdown, use_container_width=True, hide_index=True)

st.divider()

# --- plots side by side ---
st.subheader("Visual Breakdown")

col_left, col_right = st.columns(2)

# plot 1: tier distribution pie
with col_left:
    st.markdown("**Session distribution by intent tier**")
    fig_pie = px.pie(
        values=[high, medium, low],
        names=["HIGH", "MEDIUM", "LOW"],
        color=["HIGH", "MEDIUM", "LOW"],
        color_discrete_map={"HIGH": "#22c55e", "MEDIUM": "#f59e0b", "LOW": "#ef4444"},
        hole=0.4,
    )
    fig_pie.update_layout(margin=dict(t=10, b=10), legend_title="Intent Tier")
    st.plotly_chart(fig_pie, use_container_width=True)

# plot 2: cost comparison bar
with col_right:
    st.markdown("**Campaign cost — agent vs giving everyone a discount**")
    fig_cost = go.Figure()
    fig_cost.add_bar(
        x=["Baseline\n(discount everyone)", "Agent\n(targeted)"],
        y=[baseline_cost, total_cost],
        marker_color=["#94a3b8", "#2563EB"],
        text=[f"€{baseline_cost:,.0f}", f"€{total_cost:,.0f}"],
        textposition="outside"
    )
    fig_cost.update_layout(
        yaxis_title="Total Cost (€)",
        margin=dict(t=10, b=10),
        showlegend=False,
        yaxis=dict(range=[0, baseline_cost * 1.2])
    )
    st.plotly_chart(fig_cost, use_container_width=True)

st.divider()

# plot 3: score distribution with threshold lines
st.subheader("Intent Score Distribution")
fig_hist = px.histogram(
    df, x="Intent_Score", color="Tier", nbins=40,
    color_discrete_map={"HIGH": "#22c55e", "MEDIUM": "#f59e0b", "LOW": "#ef4444"},
    labels={"Intent_Score": "Purchase Probability Score", "count": "Sessions"},
    barmode="overlay", opacity=0.75
)
fig_hist.add_vline(x=HIGH_T, line_dash="dash", line_color="#22c55e",
                   annotation_text=f"HIGH threshold ({HIGH_T})", annotation_position="top right")
fig_hist.add_vline(x=MED_T,  line_dash="dash", line_color="#f59e0b",
                   annotation_text=f"MEDIUM threshold ({MED_T})", annotation_position="top left")
fig_hist.update_layout(margin=dict(t=30, b=10))
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# --- per-tier behavioural patterns ---
st.subheader("Behavioural Patterns by Tier")
st.caption("Average session behaviour for each intent group — helps decide targeting message.")

tier_order = ["HIGH", "MEDIUM", "LOW"]
key_cols   = ["PageValues", "ProductRelated", "ProductRelated_Duration",
              "BounceRates", "ExitRates"]

existing_cols = [c for c in key_cols if c in df.columns]
if existing_cols:
    pattern_df = (
        df.groupby("Tier")[existing_cols]
        .mean()
        .round(3)
        .reindex(tier_order)
        .reset_index()
    )
    pattern_df.columns = ["Tier"] + existing_cols
    pattern_df["Tier"] = ["🟢 HIGH", "🟡 MEDIUM", "🔴 LOW"]
    st.dataframe(pattern_df, use_container_width=True, hide_index=True)

    # radar chart — normalise each metric 0-1 for visual comparison
    st.markdown("**Normalised behaviour profile per tier**")
    norm_df = pattern_df.copy()
    for col in existing_cols:
        col_min = norm_df[col].min()
        col_max = norm_df[col].max()
        if col_max != col_min:
            norm_df[col] = (norm_df[col] - col_min) / (col_max - col_min)
        else:
            norm_df[col] = 0.5

    fig_radar = go.Figure()
    colors = {"🟢 HIGH": "#22c55e", "🟡 MEDIUM": "#f59e0b", "🔴 LOW": "#ef4444"}
    for _, row in norm_df.iterrows():
        values = [row[c] for c in existing_cols] + [row[existing_cols[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=existing_cols + [existing_cols[0]],
            fill='toself',
            name=row["Tier"],
            line_color=colors[row["Tier"]]
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        margin=dict(t=40, b=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# --- full scored session table ---
st.subheader("Full Session Table")
st.caption("All sessions with their score, tier, and recommended action. Download to share with your marketing team.")

display_cols = ["Intent_Score", "Tier", "Action", "Campaign_Cost"] + \
               [c for c in ["PageValues","ProductRelated","BounceRates","ExitRates",
                             "Month","VisitorType","Weekend"] if c in df.columns]

st.dataframe(
    df[display_cols].sort_values("Intent_Score", ascending=False),
    use_container_width=True
)

st.download_button(
    "Download full results as CSV",
    data=df.to_csv(index=False),
    file_name="campaign_plan.csv",
    mime="text/csv"
)