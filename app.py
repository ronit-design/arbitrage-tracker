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
    avg_col = '5-year average discount'
    stock_price_col = 'Stock Price'
    hold_co_col = 'Holding Company Price'
    shares_needed_col = 'No of Hold Co share to be bought'

    col1, col2, col3 = st.columns(3)

    if selected_company != "All Companies":
        col1.metric("Current Discount", f"{filtered_df[current_col].iloc[0]}")
        col2.metric("Stock Price", f"₹{filtered_df[stock_price_col].iloc[0]}")
        col3.metric("Holding Co. Price", f"₹{filtered_df[hold_co_col].iloc[0]}")
    else:
        st.info("Select a specific company from the sidebar to see isolated metrics.")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Current vs 5-Year Avg Discount")
        
        # THE FIX: "Melting" the data so the chart never gets confused by lengths
        melted_df = filtered_df.melt(
            id_vars=[company_col], 
            value_vars=[current_col, avg_col], 
            var_name='Discount Type', 
            value_name='Discount (%)'
        )
        
        fig1 = px.bar(
            melted_df, 
            x=company_col, 
            y='Discount (%)', 
            color='Discount Type',
            barmode='group'
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.subheader("Trade Execution: Shares Needed")
        fig2 = px.bar(
            filtered_df, 
            x=company_col, 
            y=shares_needed_col, 
            color=company_col,
            labels={shares_needed_col: 'Shares to Buy'}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Live Execution Matrix")
    st.dataframe(filtered_df, use_container_width=True)

except KeyError as e:
    st.error(f"🚨 **Column Name Mismatch!** Python cannot find the column: {e}.")
