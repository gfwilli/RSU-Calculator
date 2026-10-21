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
    st.session_state.vested_shares = 250
if "unvested_shares" not in st.session_state:
    st.session_state.unvested_shares =
