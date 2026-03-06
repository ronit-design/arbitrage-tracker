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
    company_col = df.columns[0]
    current_col = 'Current Discount Value'
    avg_col = '5 year average'  # <--- UPDATED HERE
    stock_price_col = 'Stock Price'
    hold_co_col = 'Holding Company Price'
    
    # NOTE: If the SECOND chart throws an error next, check your debugger 
    # and update this specific line to match your sheet exactly:
    shares_needed_col = 'No of Hold Co share to be bought'

    col1, col2, col3 = st.columns(3)

    if selected_company != "All Companies":
        col1.metric("Current Discount", f"{filtered_df[current_col].iloc[0]}")
        col2.metric("Stock Price", f"₹{filtered_df[stock_price_col].iloc[0]}")
        col3.metric("Holding Co. Price", f"₹{filtered_df[hold_co_col].iloc[0]}")
    else:
        st.info("Select a specific company from the sidebar to see isolated metrics.")

    st.markdown("---")

    col_chart1, col_chart2 =
