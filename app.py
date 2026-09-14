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
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'client_name' not in st.session_state: st.session_state.client_name = "Jane Doe"
if 'client_email' not in st.session_state: st.session_state.client_email = "jane@company.com"
if 'company_ticker' not in st.session_state: st.session_state.company_ticker = "GOOGL"
if 'vested_shares' not in st.session_state: st.session_state.vested_shares = 500
if 'unvested_shares' not in st.session_state: st.session_state.unvested_shares = 500
if 'submitted' not in st.session_state: st.session_state.submitted = False

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
max_loan_capacity = total_equity_value * 0.35

def send_notification_email(name, email, ticker, vested, unvested, max_loan):
    """Sends email notification to RSUnits upon submission."""
    # Configure your SMTP credentials or email provider API here
    # Example using standard library smtplib:
    msg = EmailMessage()
    msg.set_content(
        f"New Prequalification Submission:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Ticker: {ticker}\n"
        f"Vested Shares: {vested}\n"
        f"Unvested Shares: {unvested}\n"
        f"Max Loan Capacity: ${max_loan:,.2f}"
    )
    msg['Subject'] = f"New RSU Prequalification Lead: {name}"
    msg['From'] = "app@yourdomain.com"
    msg['To'] = "RSUnits@yourdomain.com"
    
    try:
        # Replace with your SMTP server details
        # server = smtplib.SMTP('smtp.yourserver.com', 587)
        # server.starttls()
        # server.login('user', 'password')
        # server.send_message(msg)
        # server.quit()
        pass
    except Exception as e:
        print(f"Email failed to send: {e}")

# --- Render Success Page View or Calculator View ---
if st.session_state.submitted:
    st.markdown('<h1 style="font-family: \'Urbanist\', sans-serif; font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 1rem;">Submission <span style="color: var(--accent-green);">Successful</span></h1>', unsafe_allow_html=True)
    st.markdown("---")
    st.success(f"Thank you, {st.session_state.client_name}! Your prequalification profile for up to **${max_loan_capacity:,.2f}** has been successfully submitted to RSUnits.")
    st.markdown(f"Our underwriting team will review your details and contact you shortly at **{st.session_state.client_email}**.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Calculate Another Estimate"):
        st.session_state.submitted = False
        st.rerun()

else:
    # --- Top Title ---
    st.markdown('<h1 style="font-family: \'Urbanist\', sans-serif; font-size: 2.5rem; font-weight: 800; color: #ffffff; margin-bottom: 1rem;">Prequalification <span style="color: var(--accent-green);">Estimator</span></h1>', unsafe_allow_html=True)

    # --- Liquidity Summary Section ---
    st.subheader("Your Liquidity Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Share Price", f"${stock_price:,.2f}")
    col2.metric("Total Equity Value (Vested + Unvested)", f"${total_equity_value:,.2f}")
    col3.metric("Max Loan Capacity (35% Cap)", f"${max_loan_capacity:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Inputs Section ---
    st.subheader("Your Details")

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        st.session_state.client_name = st.text_input("Full Name", st.session_state.client_name)
        st.session_state.client_email = st.text_input("Work Email", st.session_state.client_email)
        st.session_state.company_ticker = st.text_input("Company Ticker", st.session_state.company_ticker).upper()
        
    with form_col2:
        vested_str = st.text_input("Total Vested Shares", value=str(int(st.session_state.vested_shares)))
        try:
            st.session_state.vested_shares = float(vested_str) if vested_str else 0.0
        except ValueError:
            st.session_state.vested_shares = 0.0

        unvested_str = st.text_input("Total Unvested Shares", value=str(int(st.session_state.unvested_shares)))
        try:
            st.session_state.unvested_shares = float(unvested_str) if unvested_str else 0.0
        except ValueError:
            st.session_state.unvested_shares = 0.0

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Prequalification Action Button ---
    if st.button("Submit for Prequalification"):
        if not st.session_state.client_name or not st.session_state.client_email:
            st.error("Please provide your name and work email to submit your prequalification request.")
        else:
            send_notification_email(
                st.session_state.client_name,
                st.session_state.client_email,
                st.session_state.company_ticker,
                st.session_state.vested_shares,
                st.session_state.unvested_shares,
                max_loan_capacity
            )
            st.session_state.submitted = True
            st.rerun()
