import datetime
import streamlit as st
import yfinance as yf

# --- Page Configuration & Styling ---
st.set_page_config(page_title="RSU Lending & Equity Calculator", layout="wide")

# Custom CSS matching the website's dark theme, fonts, and #a3e635 accent color
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Urbanist:wght@600;700;800&display=swap" rel="stylesheet">
    
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
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Urbanist', sans-serif;
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
            font-family: 'Inter', sans-serif;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            color: var(--accent-green) !important;
            font-family: 'Urbanist', sans-serif;
        }
        
        /* Expander and input styling consistency */
        .streamlit-expanderHeader {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            border-radius: 8px;
            font-family: 'Urbanist', sans-serif;
        }
        
        div.stExpander {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("RSU Equity & Lending Assessment Tool")
st.markdown("Evaluate vested values, post-tax liquidity, and single-stock borrowing capacity.")
st.markdown("---")

# --- Core Logic Functions ---
@st.cache_data
def fetch_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return float(price)
    except:
        return 175.50  # Fallback price

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

# --- Outputs Displayed First (Top Section) ---
# We fetch ticker early from a default or dynamic state to compute outputs, 
# but let's grab it from session state or inputs below if initialized.
# To handle top-to-bottom layout cleanly with bottom inputs, we define standard defaults or use a form state, 
# or place outputs up top and inputs down below using Streamlit columns/widgets. 
# Note: Streamlit executes top-to-bottom, so to have inputs at the bottom control top outputs, 
# we can collect inputs using widgets placed at the bottom, or use session state. 
# Alternatively, putting inputs below means we can initialize default session states or handle them seamlessly.

# Initialize Session State for Inputs if not already present
if 'client_name' not in st.session_state: st.session_state.client_name = "Jane Doe"
if 'base_salary' not in st.session_state: st.session_state.base_salary = 200000
if 'state_tax_rate' not in st.session_state: st.session_state.state_tax_rate = 0.093
if 'company_ticker' not in st.session_state: st.session_state.company_ticker = "GOOGL"
if 'stock_tier' not in st.session_state: st.session_state.stock_tier = "Mega-Cap"
if 'is_insider' not in st.session_state: st.session_state.is_insider = True
if 'vested_shares' not in st.session_state: st.session_state.vested_shares = 800
if 'unvested_shares' not in st.session_state: st.session_state.unvested_shares = 1200
if 'next_vest_date' not in st.session_state: st.session_state.next_vest_date = datetime.date(2026, 10, 1)

stock_price = fetch_stock_price(st.session_state.company_ticker)

# Calculations based on current session state values
vested_market_value = st.session_state.vested_shares * stock_price
unvested_market_value = st.session_state.unvested_shares * stock_price
estimated_vest_income = (st.session_state.unvested_shares / 4) * stock_price
true_tax_rate = estimate_marginal_tax_rate(st.session_state.base_salary + estimated_vest_income, st.session_state.state_tax_rate)
net_vest_value = vested_market_value * (1 - true_tax_rate)

ltv_ratio = calculate_ltv(st.session_state.stock_tier)
potential_loan = vested_market_value * ltv_ratio

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
    st.write(f"**Blackout Status:** {check_blackout(st.session_state.is_insider)}")

with col5:
    st.markdown("### Pipeline Summary")
    st.write(f"**Unvested Pipeline Value:** ${unvested_market_value:,.2f}")
    st.write(f"**Next Vest Date:** {st.session_state.next_vest_date.strftime('%B %d, %Y')}")
    st.write(f"**Unvested Shares Count:** {st.session_state.unvested_shares:,} shares")

st.markdown("---")

# --- Inputs Section Moved to the Bottom ---
st.subheader("Borrower & Grant Inputs")

with st.container():
    bot_col1, bot_col2, bot_col3 = st.columns(3)
    
    with bot_col1:
        st.session_state.client_name = st.text_input("Borrower Name", st.session_state.client_name)
        st.session_state.base_salary = st.number_input("Base Salary ($)", value=st.session_state.base_salary, step=10000)
        st.session_state.state_tax_rate = st.number_input("State Tax Rate (e.g., 0.093 for CA)", value=st.session_state.state_tax_rate, step=0.005)
        
    with bot_col2:
        st.session_state.company_ticker = st.text_input("Company Ticker", st.session_state.company_ticker).upper()
        st.session_state.stock_tier = st.selectbox("Stock Risk Tier", ["Mega-Cap", "Standard", "Volatile"], index=["Mega-Cap", "Standard", "Volatile"].index(st.session_state.stock_tier))
        st.session_state.is_insider = st.checkbox("Corporate Insider / Executive", value=st.session_state.is_insider)
        
    with bot_col3:
        st.session_state.vested_shares = st.number_input("Total Vested Shares", value=st.session_state.vested_shares, step=50)
        st.session_state.unvested_shares = st.number_input("Total Unvested Shares", value=st.session_state.unvested_shares, step=50)
        st.session_state.next_vest_date = st.date_input("Next Vest Date", st.session_state.next_vest_date)
