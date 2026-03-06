import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="Arbitrage Dashboard", layout="wide")
st.title("📈 Live Arbitrage Opportunity Dashboard")

# 2. Fetch Data from Google Sheets
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1I48HWtmhga7AAJbFDIhjblHDzNGHZ5ASJtGtVZMTioE/export?format=csv&gid=0"
    df = pd.read_csv(sheet_url)
    # Clean up any accidental spaces at the beginning or end of column names
    df.columns = df.columns.str.strip() 
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Connection Failed. Please check your Google Sheet link. Error: {e}")
    st.stop()

# 3. Sidebar Debugger & Filter
st.sidebar.header("Controls")
companies = df.iloc[:, 0].dropna().unique() 
selected_company = st.sidebar.selectbox("Filter by Company:", ["All Companies"] + list(companies))

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Debugging: Actual Column Names")
st.sidebar.write("If the dashboard crashes, make sure the names below exactly match the variables in the code:")
st.sidebar.write(df.columns.tolist())

# 4. Filter Logic
if selected_company != "All Companies":
    filtered_df = df[df.iloc[:, 0] == selected_company]
else:
    filtered_df = df

# 5. Dashboard Visualizations
st.markdown("### Quick Metrics")

try:
    # --- COLUMN NAME VARIABLES ---
    # If the app crashes, check the sidebar for your exact column names and update these:
    company_
