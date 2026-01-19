import os
import streamlit as st
import pandas as pd
import plotly.express as px

from model_utils import run_model_pipeline
from chat_engine import respond_to_query

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="UIDAI Aadhaar Analytics Platform",
    page_icon="🆔",
    layout="wide"
)

# -------------------- API KEY CHECK --------------------
if not os.getenv("GEMINI_API_KEY"):
    st.error("Gemini API key not configured. Please set GEMINI_API_KEY.")
    st.stop()

# -------------------- STYLES --------------------
st.markdown("""
<style>
.insight-card {
    background-color: #161b22;
    border-radius: 14px;
    padding: 22px;
    border: 1px solid #30363d;
    margin-bottom: 20px;
}
.insight-title {
    font-size: 20px;
    font-weight: 600;
    color: #58a6ff;
    margin-bottom: 12px;
}
.insight-label {
    font-weight: 600;
    color: #c9d1d9;
    margin-top: 10px;
}
.insight-text {
    color: #adbac7;
    font-size: 15px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("🗂 Control Panel")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Predictive Model", "Insight Chat"]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Aadhaar Dataset (CSV)",
    type=["csv"]
)

# -------------------- DATA LOAD --------------------
df = None
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Dataset loaded successfully")

# -------------------- INSIGHT CARD --------------------
def render_insight_card(text):
    sections = {"Finding": "", "Impact": "", "Recommendation": ""}
    current = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        for key in sections:
            if line.startswith(key):
                current = key
                sections[key] = line.replace(f"{key}:", "").strip()
                break
        else:
            if current:
                sections[current] += " " + line

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">Actionable Insight</div>

        <div class="insight-label">Finding</div>
        <div class="insight-text">{sections["Finding"]}</div>

        <div class="insight-label">Impact</div>
        <div class="insight-text">{sections["Impact"]}</div>

        <div class="insight-label">Recommendation</div>
        <div class="insight-text">{sections["Recommendation"]}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ===================== DASHBOARD =====================
# =====================================================
if page == "Dashboard":

    st.title("📊 Aadhaar Activity Dashboard")

    if df is None:
        st.info("Upload dataset to view dashboard.")
    else:
        selected_states = st.multiselect(
            "Select State(s)",
            sorted(df["state"].unique())
        )

        filtered_df = df if not selected_states else df[df["state"].isin(selected_states)]

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(
                filtered_df.groupby("state")["total_activity"].sum().reset_index(),
                x="state",
                y="total_activity",
                title="Total Aadhaar Activity by State"
            )
            st.plotly_chart(fig1, width="stretch")

        with col2:
            demo_df = pd.DataFrame({
                "Age Group": ["0–5", "5–17", "18+"],
                "Total Activity": [
                    filtered_df["age_0_5"].sum(),
                    filtered_df["age_5_17"].sum(),
                    filtered_df["age_18_greater"].sum()
                ]
            })
            fig2 = px.bar(
                demo_df,
                x="Age Group",
                y="Total Activity",
                title="Activity by Demographic Group"
            )
            st.plotly_chart(fig2, width="stretch")

# =====================================================
# ================= PREDICTIVE MODEL ==================
# =====================================================
elif page == "Predictive Model":

    st.title("🔮 Predictive Model Evaluation")

    if df is None:
        st.info("Upload dataset to run model.")
    else:
        if st.button("Run Prediction Model"):
            r2, mae = run_model_pipeline(df)
            st.session_state.model_metrics = (r2, mae)

            st.metric("R² Score", f"{r2:.3f}")
            st.metric("MAE", f"{mae:.0f}")

# =====================================================
# ==================== INSIGHT CHAT ===================
# =====================================================
elif page == "Insight Chat":

    st.title("💬 Insight Chat")

    if df is None:
        st.info("Upload dataset to enable chat.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_query = st.text_input(
            "Ask a policy or analytics question",
            placeholder="e.g. Which demographic group contributes most to updates?"
        )

        if st.button("Ask"):
            if user_query.strip():
                response = respond_to_query(
                    user_query,
                    df,
                    st.session_state.get("model_metrics")
                )
                st.session_state.chat_history.append(response)

        for msg in reversed(st.session_state.chat_history):
            render_insight_card(msg)
