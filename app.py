import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Setup & CSS Styling
st.set_page_config(page_title="Arbitrage Terminal", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# Injecting Custom CSS for a highly professional look
st.markdown("""
    <style>
    /* Clean up padding */
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 95%; }
    
    /* Elegant Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. Fetch Data from Google Sheets
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1I48HWtmhga7AAJbFDIhjblHDzNGHZ5ASJtGtVZMTioE/export?format=csv&gid=0"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip() 
    return df

try:
    with st.spinner('Connecting to live market data...'):
        df = load_data()
except Exception as e:
    st.error(f"Connection Failed: {e}")
    st.stop()

# --- COLUMN DEFINITIONS ---
company_col = 'Stock'
current_col = 'Current Discount Value'
avg_col = '5 year average'  
stock_price_col = 'Price'
hold_co_col = 'Holding Company Price'
shares_needed_col = 'Shares of Holding Company to be Bought per Lot'
ratio_col = 'Ratio'

# 3. Sidebar Controls
with st.sidebar:
    st.title("🏦 Arbitrage Terminal")
    st.markdown("Real-time holding company tracking.")
    st.markdown("---")
    companies = df[company_col].dropna().unique() 
    selected_company = st.selectbox("🎯 Target Company:", ["All Market
