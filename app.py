import datetime
import smtplib
from email.message import EmailMessage
import streamlit as st
import yfinance as yf

# --- Page Configuration & Styling ---
st.set_page_config(page_title="Prequalification Estimator", layout="wide")
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
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .viewerBadge_link__1S137 {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "full_name" not in st.session_state:
    st.session_state.full_name = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "company_ticker" not in st.session_state:
    st.session_state.company_ticker = "GOOGL"
if "vested_shares" not in st.session_state:
    st.session_state.vested_shares = 500
if "unvested_shares" not in st.session_state:
    st.session_state.unvested_shares = 500

# Title with lime green accent
st.markdown("<h1>Prequalification <span style='color: var(--accent-green);'>Estimator</span></h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Fetch Stock Price ---
try:
    ticker_symbol = st.session_state.company_ticker
    stock = yf.Ticker(ticker_symbol)
    stock_price = stock.history(period="1d")['Close'].iloc[-1]
except Exception:
    stock_price = 340.76  # Fallback price

vested_market_value = st.session_state.vested_shares * stock_price
unvested_market_value = st.session_state.unvested_shares * stock_price
total_equity_value = vested_market_value + unvested_market_value

# 35% underwriting cap applied across both vested and unvested value
max_loan_capacity = total_equity_value * 0.35

# --- Summary Metrics Display ---
col1, col2, col3 = st.columns(3)
col1.metric("Current Share Price", f"${stock_price:,.2f}")
col2.metric("Total Equity Value (Vested + Unvested)", f"${total_equity_value:,.2f}")
col3.metric("Max Loan Capacity (35% Cap)", f"${max_loan_capacity:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

def send_notification_email(name, email, ticker, vested, unvested, max_loan):
    """Sends email notification to RSUnits upon submission."""
    msg = EmailMessage()
    msg.set_content(
        f"New Prequalification Submission:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Ticker: {ticker}\n"
        f"Vested Shares: {vested}\n"
        f"Unvested Shares: {unvested}\n"
        f"Max Loan Capacity: ${max_loan:,.2f}\n"
    )
    msg['Subject'] = f"New Prequalification Lead: {name} ({ticker})"
    msg['From'] = "system@rsunits.com"
    msg['To'] = "RSUnits@yourdomain.com"
    try:
        pass
    except Exception as e:
        print(f"Email failed to send: {e}")

# --- Inputs Section ("Your Details") ---
st.subheader("Your Details")

# Row 1: Full Name and Company Ticker side-by-side
form_col1, form_col2 = st.columns(2)
with form_col1:
    st.text_input("Full Name", key="full_name", placeholder="e.g. Sarah Jenkins")
with form_col2:
    st.text_input("Company Ticker", key="company_ticker", placeholder="e.g. GOOGL")

# Row 2: Personal Email Address spanning full width
st.text_input(
    "Personal Email Address", 
    key="email", 
    placeholder="sarah.j@gmail.com",
    help="Use your personal email for complete privacy."
)

st.markdown("<br>", unsafe_allow_html=True)

# Row 3: Total Vested and Unvested Shares side-by-side
share_col1, share_col2 = st.columns(2)
with share_col1:
    st.number_input("Total Vested Shares", min_value=0, key="vested_shares")
with share_col2:
    st.number_input("Total Unvested Shares", min_value=0, key="unvested_shares")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Submit for Prequalification"):
    if not st.session_state.full_name or not st.session_state.email:
        st.error("Please fill in your name and email address.")
    else:
        # Uppercase ticker just before sending/processing
        st.session_state.company_ticker = st.session_state.company_ticker.upper()
        send_notification_email(
            st.session_state.full_name,
            st.session_state.email,
            st.session_state.company_ticker,
            st.session_state.vested_shares,
            st.session_state.unvested_shares,
            max_loan_capacity
        )
        st.success("Prequalification estimate calculated successfully!")
        st.session_state.submitted = True
        st.rerun()
