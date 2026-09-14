import datetime
import streamlit as st
import yfinance as yf

# --- Page Configuration & Styling ---
st.set_page_config(page_title="RSU Prequalification Tool", layout="wide")

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
            --accent-green: #bae655;
            --accent-green-hover: #cbf06f;
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
        
        div[data-testid="stMetric"] {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 20px;
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
        
        .stButton>button {
            background-color: var(--accent-green);
            color: #000000;
            font-weight: 700;
            border-radius: 8px;
            border: none;
            padding: 0.6rem 1.2rem;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: var(--accent-green-hover);
        }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'client_name' not in st.session_state: st.session_state.client_name = "Jane Doe"
if 'client_email' not in st.session_state: st.session_state.client_email = "jane@company.com"
if 'company_ticker' not in st.session_state: st.session_state.company_ticker = "GOOGL"
if 'vested_shares' not in st.session_state: st.session_state.vested_shares = 1000
if 'unvested_shares' not in st.session_state: st.session_state.unvested_shares = 1500

# --- Core Logic ---
@st.cache_data
def fetch_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return float(price)
    except:
        return 175.50

current_ticker = st.session_state.company_ticker.upper()
stock_price = fetch_stock_price(current_ticker)

vested_market_value = st.session_state.vested_shares * stock_price
unvested_market_value = st.session_state.unvested_shares * stock_price
total_equity_value = vested_market_value + unvested_market_value

# 35% underwriting cap applied across both vested and unvested value
max_loan_capacity = total_equity_value * 0.35

# --- Top Title ---
st.markdown('<h1 style="font-family: \'Urbanist\', sans-serif; font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 1rem;">Prequalification <span style="color: var(--accent-green);">Tool</span></h1>', unsafe_allow_html=True)

# --- Liquidity Summary Section (Immediately Below Title) ---
st.subheader("Your Estimated Liquidity Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Current Share Price", f"${stock_price:,.2f}")
col2.metric("Total Equity Value (Vested + Unvested)", f"${total_equity_value:,.2f}")
col3.metric("Max Loan Capacity (35% Cap)", f"${max_loan_capacity:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# --- Inputs Section ("Your Details") ---
st.subheader("Your Details")

form_col1, form_col2 = st.columns(2)

with form_col1:
    st.session_state.client_name = st.text_input("Full Name", st.session_state.client_name)
    st.session_state.client_email = st.text_input("Work Email", st.session_state.client_email)
    st.session_state.company_ticker = st.text_input("Company Ticker", st.session_state.company_ticker).upper()
    
with form_col2:
    st.session_state.vested_shares = st.number_input("Total Vested Shares", value=int(st.session_state.vested_shares), step=50)
    st.session_state.unvested_shares = st.number_input("Total Unvested Shares", value=int(st.session_state.unvested_shares), step=50)

st.markdown("<br>", unsafe_allow_html=True)

# --- Prequalification Action Button ---
if st.button("Submit for Prequalification"):
    if not st.session_state.client_name or not st.session_state.client_email:
        st.error("Please provide your name and work email to submit your prequalification request.")
    else:
        st.success(f"Thank you, {st.session_state.client_name}! Your prequalification profile for up to ${max_loan_capacity:,.2f} has been submitted. Our team will contact you at {st.session_state.client_email} shortly.")
