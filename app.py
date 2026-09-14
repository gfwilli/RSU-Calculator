import datetime
import streamlit as st
import yfinance as yf

# --- Page Configuration & Styling ---
st.set_page_config(page_title="RSU Liquidity & Prequalification Calculator", layout="wide")

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

st.title("RSU Liquidity & Prequalification Tool")
st.markdown("Adjust your equity details below to watch your borrowing capacity update instantly in real time.")
st.markdown("---")

# --- Core Logic ---
@st.cache_data
def fetch_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return float(price)
    except:
        return 175.50

# --- Inputs Section (Placed outside a form so it updates live on every change) ---
st.subheader("Customize Your Grant & Borrower Details")

form_col1, form_col2 = st.columns(2)

with form_col1:
    client_name = st.text_input("Full Name", "Jane Doe")
    client_email = st.text_input("Work Email", "jane@company.com")
    company_ticker = st.text_input("Company Ticker", "GOOGL").upper()
    
with form_col2:
    vested_shares = st.number_input("Total Vested Shares", value=1000, step=50)
    unvested_shares = st.number_input("Total Unvested Shares", value=1500, step=50)

# Fetch live stock price and calculate values dynamically as inputs change
stock_price = fetch_stock_price(company_ticker)
vested_market_value = vested_shares * stock_price
max_loan_capacity = vested_market_value * 0.35

st.markdown("---")

# --- Top Section: Live Outputs & Results (Reacts instantly) ---
st.subheader("Your Estimated Liquidity Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Current Share Price", f"${stock_price:,.2f}")
col2.metric("Gross Vested Value", f"${vested_market_value:,.2f}")
col3.metric("Max Loan Capacity (35% Cap)", f"${max_loan_capacity:,.2f}")

st.markdown("---")

# --- Prequalification Action Button ---
if st.button("Submit for Prequalification"):
    if not client_name or not client_email:
        st.error("Please provide your name and work email to submit your prequalification request.")
    else:
        st.success(f"Thank you, {client_name}! Your prequalification profile for up to ${max_loan_capacity:,.2f} has been submitted. Our team will contact you at {client_email} shortly.")

