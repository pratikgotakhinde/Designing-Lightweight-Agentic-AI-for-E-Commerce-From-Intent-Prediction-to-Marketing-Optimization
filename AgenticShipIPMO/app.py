import streamlit as st
from agent import AgenticOrchestrator
from model_utils import build_feature_row, MONTHS, VISITOR_TYPES

st.set_page_config(page_title="ShopIQ", page_icon="🛒", layout="centered")


@st.cache_resource
def load_agent():
    return AgenticOrchestrator()


agent = load_agent()

st.title("ShopIQ — Visitor Intelligence")
st.caption("Predict purchase intent and recommend the right action for each session.")
st.divider()

# --- session inputs ---
st.subheader("Session Details")

col1, col2 = st.columns(2)
with col1:
    page_values = st.number_input("Page Values", min_value=0.0, value=0.0, step=1.0)
    product_pages = st.number_input("Product Pages Visited", min_value=0, value=2, step=1)
    product_dur = st.number_input("Product Duration (sec)", min_value=0.0, value=120.0, step=10.0)
    bounce_rate = st.number_input(
        "Bounce Rate (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.02,
        step=0.01,
        format="%.3f",
    )
    exit_rate = st.number_input(
        "Exit Rate (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.04,
        step=0.01,
        format="%.3f",
    )

with col2:
    admin_pages = st.number_input("Admin Pages Visited", min_value=0, value=0, step=1)
    admin_dur = st.number_input("Admin Duration (sec)", min_value=0.0, value=0.0, step=10.0)
    info_pages = st.number_input("Info Pages Visited", min_value=0, value=0, step=1)
    info_dur = st.number_input("Info Duration (sec)", min_value=0.0, value=0.0, step=10.0)
    special_day = st.slider("Special Day Proximity", 0.0, 1.0, 0.0, step=0.2)

col3, col4, col5 = st.columns(3)
with col3:
    month = st.selectbox("Month", MONTHS)
with col4:
    visitor_type = st.selectbox("Visitor Type", VISITOR_TYPES)
with col5:
    weekend = st.checkbox("Weekend session?")

col6, col7, col8 = st.columns(3)
with col6:
    os_type = st.number_input("OS", min_value=1, max_value=8, value=2)
with col7:
    browser = st.number_input("Browser", min_value=1, max_value=13, value=2)
with col8:
    region = st.number_input("Region", min_value=1, max_value=9, value=1)

traffic_type = st.number_input("Traffic Type", min_value=1, max_value=20, value=2)

st.divider()

# --- run the agent pipeline ---
if st.button("Analyse Session", use_container_width=True):
    inputs = {
        "PageValues": page_values,
        "ProductRelated": product_pages,
        "ProductRelated_Duration": product_dur,
        "BounceRates": bounce_rate,
        "ExitRates": exit_rate,
        "Administrative": admin_pages,
        "Administrative_Duration": admin_dur,
        "Informational": info_pages,
        "Informational_Duration": info_dur,
        "SpecialDay": special_day,
        "Month": month,
        "VisitorType": visitor_type,
        "Weekend": int(weekend),
        "OperatingSystems": os_type,
        "Browser": browser,
        "Region": region,
        "TrafficType": traffic_type,
    }

    features_df = build_feature_row(inputs)
    result = agent.run(features_df)

    score = result.get("score", 0.0)
    tier = result.get("tier", "LOW")
    action = result.get("action", {})
    top3 = result.get("top_features", [])

    st.divider()
    st.subheader("Results")

    tier_colors = {
        "HIGH": "🟢",
        "MEDIUM": "🟡",
        "LOW": "🔴",
    }

    st.metric(label="Purchase Probability", value=f"{score:.1%}")
    st.markdown(f"**Intent Tier:** {tier_colors.get(tier, '')} {tier}")

    st.info(
        f"**Recommended Action:** {action.get('action', 'N/A')} \n"
        f"**Message to show:** _{action.get('message', 'N/A')}_ \n"
        f"**Campaign cost:** €{action.get('cost', 0.0):.2f} / session"
    )

    st.subheader("Why this score?")
    for feat, val in top3:
        direction = "pushed score up" if val > 0 else "pushed score down"
        st.markdown(f"- **{feat}** → SHAP {val:+.4f} ({direction})")

    with st.expander("Raw feature input"):
        st.dataframe(features_df.T.rename(columns={0: "value"}))
