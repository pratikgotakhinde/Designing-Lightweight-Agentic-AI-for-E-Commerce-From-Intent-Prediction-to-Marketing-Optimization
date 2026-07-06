import os, json
import streamlit as st

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")

st.set_page_config(page_title="About", layout="centered")

try:
    with open(os.path.join(MODEL_DIR, "thresholds.json")) as f:
        t = json.load(f)
    HIGH_T = t["HIGH_THRESHOLD"]
    MED_T  = t["MEDIUM_THRESHOLD"]
except Exception:
    HIGH_T = 0.60
    MED_T  = 0.40

st.title("How it works")
st.divider()

st.markdown("""
This tool looks at how a visitor behaves during a single browsing session 
and estimates how likely they are to make a purchase.

Rather than showing the same discount to everyone, it scores each session 
and picks a different response depending on where that person sits on the 
intent scale. High-intent visitors get a gentle urgency message. Mid-range 
visitors get a small discount to push them over the line. Low-intent 
visitors get queued for a retargeting ad later — no point spending money on 
a discount for someone who isn't ready to buy.
""")

st.divider()

# --- the three tiers ---
st.subheader("The three intent tiers")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"###  HIGH")
    st.markdown(f"""
    **Score ≥ {HIGH_T}**

    Visitor is already browsing product pages with strong engagement.
    Conversion is likely — just show something that creates a sense of urgency.

    **Action:** Urgency Banner  
    **Message:** _"Only a few left — grab yours before it's gone."_  
    **Cost:** €0.00 / session
    """)

with c2:
    st.markdown(f"###  MEDIUM")
    st.markdown(f"""
    **Score {MED_T} – {HIGH_T}**

    Visitor is interested but not quite there. 
    A small push — like a limited-time discount — usually tips them over.

    **Action:** 10% Discount Coupon  
    **Message:** _"Here's 10% off — just for this session."_  
    **Cost:** €5.00 / session
    """)

with c3:
    st.markdown(f"### LOW")
    st.markdown(f"""
    **Score < {MED_T}**

    Visitor is browsing casually with low engagement.
    Not worth a discount right now — re-engage them later via a cheaper ad.

    **Action:** Retargeting Ad  
    **Message:** _"Come back soon — your cart is waiting."_  
    **Cost:** €0.50 / session
    """)

st.divider()

# --- what drives the score ---
st.subheader("What the model looks at")

st.markdown("""
The model was trained on session-level data from 12,330 real e-commerce visits.
The five features that matter most:

| Feature | Why it matters |
|---------|---------------|
| **Page Values** | Pages with higher historical revenue value signal buying intent |
| **Exit Rate** | High exit rate means the visitor is about to leave without buying |
| **Bounce Rate** | Visitors who bounce quickly rarely convert |
| **Month** | May, March and November tend to have more buyers |
| **Visitor Type** | Returning visitors buy more often than first-time visitors |

On the session scorer page, the top 3 features driving each individual 
prediction are shown — so you can see exactly why someone got a HIGH or LOW score.
""")

st.divider()

# --- cost comparison ---
st.subheader("Why not just give everyone a discount?")

st.markdown("""
Most shops either give everyone a discount or give no one one.
Both are wasteful in different ways.

The table below shows what happens when you test this on 2,466 sessions:
""")

st.dataframe({
    "Approach":          ["Give everyone a discount", "Agent (targeted)"],
    "Total Cost":        ["€12,330",                  "~€3,200"],
    "Buyers Reached":    ["100%",                     "97%+"],
    "Money Wasted":      ["€9,000+ on non-buyers",    "Minimal"],
}, use_container_width=True)

st.success("Same conversion result. 74% cheaper.")

st.divider()

# --- model details ---
st.subheader("Model")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Algorithm",       "XGBoost")
col2.metric("Test AUC",        "0.9242")
col3.metric("F1 Score",        "0.6667")
col4.metric("CV AUC (5-fold)", "0.9290 ± 0.0040")

st.markdown("""
Five models were compared — Logistic Regression, Random Forest, XGBoost, 
LightGBM, and MLP. XGBoost gave the best AUC and was stable across 
cross-validation folds, so it was picked for the final pipeline.

The cross-validation spread of ±0.0040 means the model generalises well 
and isn't just memorising the training data.
""")

st.divider()

# --- how to use the app ---
st.subheader("Pages in this app")

st.markdown("""
| Page | What to do there |
|------|-----------------|
| **Session Scorer** (home) | Enter a single visitor's session data manually and get an instant score + action |
| **Campaign Analysis** | Upload a CSV of sessions — get tier breakdown, charts, traffic analysis, seasonal patterns, and a downloadable campaign plan |
| **Batch Scoring** | Upload a CSV and download a scored version with tier + action for every row |
| **About** | This page |

For the Campaign Analysis page, download the sample CSV first to see the 
expected column format, then replace the sample rows with your own session data.
""")

st.divider()
st.caption("Built on UCI Online Shoppers Purchase Intention dataset · XGBoost · SHAP explainability · Streamlit")