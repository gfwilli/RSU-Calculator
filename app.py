import datetime
import streamlit as st
import yfinance as yf

# --- Page Configuration & Styling ---
st.set_page_config(page_title="RSU Lending & Equity Calculator", layout="wide")

# Custom CSS matching the website's dark theme & #a3e635 accent color
st.markdown("""
    <style>
        :root {
            --bg-color: #0b0b0b;
            --card-bg: #141414;
            --border-color: #262626;
            --text-primary: #ffffff;
            --text-secondary: #a3a3a3;
            --accent-green: #a3e635;
            --accent-green-hover: #bef264;
        }
        
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
        }
        
        h1, h2, h3 {
            color: var(--text-primary);
        }
        
        /* Custom styling for metrics / cards */
        div[data-testid="stMetric"] {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 15px;
            border-radius: 12px;
        }
        div[data-testid="stMetric"] label {
            color: var(--text-secondary) !important;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: var(--accent-green) !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("RSU Equity & Lending Assessment Tool")
st.markdown("Evaluate vested values, post-tax liquidity, and single-stock borrowing capacity.")
st.markdown("---")

# --- Top Inputs Section ---
st.subheader("Borrower & Grant Inputs")

with st.expander("Modify Calculator Inputs", expanded=True):
    top_col1, top_col2, top_col3 = st.columns(3)
    
    with top_col1:
        client_name = st.text_input("Borrower Name", "Jane Doe")
        base_salary = st.number_input("Base Salary ($)", value=200000, step=10000)
        state_tax_rate = st.number_input("State Tax Rate (e.g., 0.093 for CA)", value=0.093, step=0.005)
        
    with top_col2:
        company_ticker = st.text_input("Company Ticker", "GOOGL").upper()
        stock_tier = st.selectbox("Stock Risk Tier", ["Mega-Cap", "Standard", "Volatile"])
        is_insider = st.checkbox("Corporate Insider / Executive", value=True)
        
    with top_col3:
        vested_shares = st.number_input("Total Vested Shares", value=800, step=50)
        unvested_shares = st.number_input("Total Unvested Shares", value=1200, step=50)
        next_vest_date = st.date_input("Next Vest Date", datetime.date(2026, 10, 1))

st.markdown("---")

# --- Core Logic ---
@st.cache_data
def fetch_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return float(price)
    except:
        return 175.50  # Fallback price

stock_price = fetch_stock_price(company_ticker)

def estimate_marginal_tax_rate(total_income, state_rate):
    if total_income > 626350: federal_rate = 0.37
    elif total_income > 250525: federal_rate = 0.35
    elif total_income > 191950: federal_rate = 0.32
    elif total_income > 100525: federal_rate = 0.24
    else: federal_rate = 0.22
    return federal_rate + state_rate + 0.0145

def calculate_ltv(tier):
    # Base LTV tiers logic, capped at a maximum of 35% (0.35) per requirements
    if tier == "Mega-Cap": raw_ltv = 0.50
    elif tier == "Standard": raw_ltv = 0.40
    else: raw_ltv = 0.20
    
    return min(raw_ltv, 0.35)

def check_blackout(insider):
    if not insider: return "N/A - Non-Insider (Clear to trade)"
    today = datetime.date.today()
    if today.month in [3, 6, 9, 12] and today.day >= 15:
        return "RESTRICTED: Currently in corporate earnings blackout window."
    return "CLEAR: Outside current blackout window."

# Calculations
vested_market_value = vested_shares * stock_price
unvested_market_value = unvested_shares * stock_price
estimated_vest_income = (unvested_shares / 4) * stock_price
true_tax_rate = estimate_marginal_tax_rate(base_salary + estimated_vest_income, state_tax_rate)
net_vest_value = vested_market_value * (1 - true_tax_rate)

ltv_ratio = calculate_ltv(stock_tier)
potential_loan = vested_market_value * ltv_ratio

# --- Outputs Displayed Below Inputs ---
st.subheader("Assessment Results & Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Current Share Price", f"${stock_price:,.2f}")
col2.metric("Gross Vested Value", f"${vested_market_value:,.2f}")
col3.metric("Est. Post-Tax Vested Value", f"${net_vest_value:,.2f}")

st.markdown("")

col4, col5 = st.columns(2)
with col4:
    st.markdown("### Lending & Risk Assessment")
    st.write(f"**Max Loan Capacity (SBL at {int(ltv_ratio*100)}% Max Capped LTV):** ${potential_loan:,.2f}")
    st.write(f"**Estimated True Marginal Tax Rate:** {true_tax_rate*100:.1f}%")
    st.write(f"**Blackout Status:** {check_blackout(is_insider)}")

with col5:
    st.markdown("### Pipeline Summary")
    st.write(f"**Unvested Pipeline Value:** ${unvested_market_value:,.2f}")
    st.write(f"**Next Vest Date:** {next_vest_date.strftime('%B %d, %Y')}")
    st.write(f"**Unvested Shares Count:** {unvested_shares:,} shares")
