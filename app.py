import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="RSUnits | Prequalification Estimator",
    page_icon="⚡",
    layout="centered"
)

# Custom Styling & UI Chrome Removal
st.markdown(
    """
    <style>
    /* Hide the Streamlit footer, menu, and GitHub badge */
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* Overall Theme Tweaks */
    .main {
        background-color: #0b0b0b;
        color: #ffffff;
    }
    .metric-card {
        background-color: #141414;
        border: 1px solid #262626;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_init := True,
    unsafe_allow_html=True
)

# Retrieve Query Parameters passed from the landing page
query_params = st.query_params
default_name = query_params.get("name", "")
default_email = query_params.get("email", "")
default_ticker = query_params.get("ticker", "GOOGL")

# App Header
st.title("Prequalification Estimator")
st.write("Review your estimated liquidity advance capacity based on upcoming RSU vest schedules.")

# Mock Financial Metrics Display
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Current Share Price", value="$340.28")
with col2:
    st.metric(label="Total Equity Value", value="$170,140.00")
with col3:
    st.metric(label="Max Loan Capacity", value="$59,549.00")

st.markdown("---")

# User Details & Inputs Section
st.subheader("Your Details")

col_a, col_b = st.columns(2)
with col_a:
    full_name = st.text_input("Full Name", value=default_name)
with col_b:
    company_ticker = st.text_input("Company Ticker", value=default_ticker)

email = st.text_input("Personal Email Address", value=default_email)

col_c, col_d = st.columns(2)
with col_c:
    vested_shares = st.number_input("Total Vested Shares", value=250, step=10)
with col_d:
    unvested_shares = st.number_input("Total Unvested Shares", value=250, step=10)

# Calculate advance eligibility action
if st.button("Calculate Final Terms", type="primary"):
    if not full_name or not email:
        st.warning("Please provide both your name and email to proceed.")
    else:
        st.success(f"Prequalification profile successfully generated for {full_name} ({company_ticker}). Our underwriting team will review your parameters shortly.")
