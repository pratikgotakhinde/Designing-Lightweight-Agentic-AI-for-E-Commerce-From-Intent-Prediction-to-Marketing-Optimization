import os, json, pickle
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # pages/ -> AgenticShipIPMO/
MODEL_DIR = os.path.join(BASE_DIR, "model")

def _path(f): return os.path.join(MODEL_DIR, f)

st.set_page_config(page_title="Batch Scoring", layout="wide")

@st.cache_resource
def load_model_and_config():
    try:
        with open(_path("xgb_model.pkl"), "rb") as f:
            model = pickle.load(f)
        with open(_path("feature_cols.json")) as f:
            feature_cols = json.load(f)
        with open(_path("thresholds.json")) as f:
            t = json.load(f)
        return model, feature_cols, t["HIGH_THRESHOLD"], t["MEDIUM_THRESHOLD"], None
    except Exception as e:
        return None, None, 0.60, 0.40, str(e)

model, feature_cols, HIGH_T, MED_T, load_error = load_model_and_config()

st.title("Batch Scoring")
st.caption("Upload a CSV of sessions — get a score and recommended action for every row.")

if load_error:
    st.error(f"Could not load model files: {load_error}")
    st.info("Make sure xgb_model.pkl, feature_cols.json and thresholds.json are inside the model/ folder.")
    st.stop()

st.divider()

# --- sample csv ---
sample = pd.DataFrame({
    "PageValues":              [45.2,  0.0,   120.5, 8.3,  0.0],
    "ProductRelated":          [5,     1,     12,    3,    0],
    "ProductRelated_Duration": [300,   45,    900,   180,  10],
    "BounceRates":             [0.01,  0.20,  0.005, 0.05, 0.35],
    "ExitRates":               [0.03,  0.25,  0.02,  0.08, 0.40],
    "Administrative":          [0,     2,     1,     0,    1],
    "Administrative_Duration": [0,     120,   60,    0,    30],
    "Informational":           [0,     0,     1,     0,    0],
    "Informational_Duration":  [0,     0,     30,    0,    0],
    "SpecialDay":              [0.0,   0.0,   0.4,   0.0,  0.0],
    "Month":                   ["May", "Feb", "Nov", "Mar","Aug"],
    "VisitorType":             ["Returning_Visitor","New_Visitor",
                                "Returning_Visitor","New_Visitor","New_Visitor"],
    "Weekend":                 [False, True,  False, False, True],
    "OperatingSystems":        [2,     1,     3,     2,    1],
    "Browser":                 [2,     1,     2,     2,    1],
    "Region":                  [1,     3,     2,     1,    4],
    "TrafficType":             [2,     1,     4,     2,    3],
})

st.download_button(
    "Download sample CSV",
    data=sample.to_csv(index=False),
    file_name="sample_sessions.csv",
    mime="text/csv"
)

st.divider()

# --- upload ---
uploaded = st.file_uploader("Upload your sessions CSV", type=["csv"])

if not uploaded:
    st.info("Upload a CSV file above. Download the sample first if you need the column format.")
    st.stop()

df_raw = pd.read_csv(uploaded)
st.success(f"Loaded {len(df_raw)} sessions.")

NUMERIC = [
    'Administrative', 'Administrative_Duration',
    'Informational',  'Informational_Duration',
    'ProductRelated', 'ProductRelated_Duration',
    'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay',
    'OperatingSystems', 'Browser', 'Region', 'TrafficType'
]

def encode_row(row):
    r = {col: 0 for col in feature_cols}
    for col in NUMERIC:
        if col in df_raw.columns:
            r[col] = row.get(col, 0)
    r['Weekend'] = 1 if str(row.get('Weekend', 'False')).lower() in ['true','1','yes'] else 0
    month_col = f"Month_{row.get('Month', '')}"
    if month_col in r:
        r[month_col] = 1
    vtype_col = f"VisitorType_{row.get('VisitorType', 'New_Visitor')}"
    if vtype_col in r:
        r[vtype_col] = 1
    return r

def assign_tier(prob):
    if prob >= HIGH_T:
        return "HIGH"
    elif prob >= MED_T:
        return "MEDIUM"
    return "LOW"

ACTION_MAP = {
    "HIGH":   "Urgency Banner",
    "MEDIUM": "10% Discount",
    "LOW":    "Retargeting Ad"
}
COST_MAP = {
    "HIGH": 0.00, "MEDIUM": 5.00, "LOW": 0.50
}

if st.button("Score All Sessions", type="primary", use_container_width=True):

    with st.spinner("Scoring sessions..."):
        try:
            rows = [encode_row(row) for _, row in df_raw.iterrows()]
            X = pd.DataFrame(rows)[feature_cols]
            probs = model.predict_proba(X)[:, 1]

            df_out = df_raw.copy()
            df_out["Intent_Score"]  = np.round(probs, 4)
            df_out["Tier"]          = [assign_tier(p) for p in probs]
            df_out["Action"]        = df_out["Tier"].map(ACTION_MAP)
            df_out["Campaign_Cost"] = df_out["Tier"].map(COST_MAP)

        except Exception as e:
            st.error(f"Scoring failed: {e}")
            st.stop()

    st.divider()
    st.subheader("Results")

    # summary metrics
    total      = len(df_out)
    high       = (df_out["Tier"] == "HIGH").sum()
    medium     = (df_out["Tier"] == "MEDIUM").sum()
    low        = (df_out["Tier"] == "LOW").sum()
    total_cost = df_out["Campaign_Cost"].sum()
    baseline   = total * 5.0
    saved      = baseline - total_cost

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total",         total)
    c2.metric("HIGH",          f"{high} ({high/total:.0%})")
    c3.metric("MEDIUM",        f"{medium} ({medium/total:.0%})")
    c4.metric("LOW",           f"{low} ({low/total:.0%})")
    c5.metric("Campaign Cost", f"€{total_cost:,.2f}")
    c6.metric("Saved",         f"€{saved:,.0f}")

    st.divider()

    # scored table — show key columns first
    display_cols = ["Intent_Score", "Tier", "Action", "Campaign_Cost"] + \
                   [c for c in ["PageValues","ProductRelated","BounceRates",
                                "ExitRates","Month","VisitorType","Weekend"]
                    if c in df_out.columns]

    st.dataframe(
        df_out[display_cols].sort_values("Intent_Score", ascending=False),
        use_container_width=True
    )

    st.download_button(
        "Download scored CSV",
        data=df_out.to_csv(index=False),
        file_name="scored_sessions.csv",
        mime="text/csv"
    )