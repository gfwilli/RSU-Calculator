import datetime
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="RSU Lending & Equity Calculator", layout="wide")

st.title("RSU Equity & Lending Assessment Tool")
st.markdown("Evaluate vested values, post-tax liquidity, and single-stock borrowing capacity.")

# --- Sidebar Inputs ---
st.sidebar.header("Borrower & Grant Inputs")
client_name = st.sidebar.text_input("Borrower Name", "Jane Doe")
base_salary = st.sidebar.number_input("Base Salary ($)", value=200000, step=10000)
state_tax_rate = st.sidebar.number_input("State Tax Rate (e.g., 0.093 for CA)", value=0.093, step=0.005)
company_ticker = st.sidebar.text_input("Company Ticker", "GOOGL").upper()

stock_tier = st.sidebar.selectbox("Stock Risk Tier", ["Mega-Cap", "Standard", "Volatile"])
is_insider = st.sidebar.checkbox("Corporate Insider / Executive", value=True)

st.sidebar.subheader("RSU Tranche Details")
vested_shares = st.sidebar.number_input("Total Vested Shares", value=800, step=50)
unvested_shares = st.sidebar.number_input("Total Unvested Shares", value=1200, step=50)
next_vest_date = st.sidebar.date_input("Next Vest Date", datetime.date(2026, 10, 1))

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
    if tier == "Mega-Cap": return 0.50
    elif tier == "Standard": return 0.40
    return 0.20

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

# --- Main Dashboard Display ---
col1, col2, col3 = st.columns(3)
col1.metric("Current Share Price", f"${stock_price:,.2f}")
col2.metric("Gross Vested Value", f"${vested_market_value:,.2f}")
col3.metric("Est. Post-Tax Vested Value", f"${net_vest_value:,.2f}")

st.markdown("---")

col4, col5 = st.columns(2)
with col4:
    st.subheader("Lending & Risk Assessment")
    st.write(f"**Max Loan Capacity (SBL at {int(ltv_ratio*100)}% LTV):** ${potential_loan:,.2f}")
    st.write(f"**Estimated True Marginal Tax Rate:** {true_tax_rate*100:.1f}%")
    st.write(f"**Blackout Status:** {check_blackout(is_insider)}")

with col5:
    st.subheader("Pipeline Summary")
    st.write(f"**Unvested Pipeline Value:** ${unvested_market_value:,.2f}")
    st.write(f"**Next Vest Date:** {next_vest_date.strftime('%B %d, %Y')}")
    st.write(f"**Unvested Shares Count:** {unvested_shares:,} shares")
