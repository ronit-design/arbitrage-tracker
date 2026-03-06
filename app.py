import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Arbitrage Dashboard", layout="wide")
st.title("📈 Live Arbitrage Opportunity Dashboard")
st.markdown("Real-time tracking of holding company discounts. Data refreshes every 60 seconds.")

# 2. Connect to Google Sheets
@st.cache_data(ttl=60) # Caches the data for 60 seconds to keep it "live" without crashing
def load_data():
    # This is the direct CSV export link for your specific Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1I48HWtmhga7AAJbFDIhjblHDzNGHZ5ASJtGtVZMTioE/export?format=csv&gid=0"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip() # Cleans up any accidental spaces in your column names
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Connection Failed. Please ensure your Google Sheet sharing settings are set to 'Anyone with the link can view'. Error details: {e}")
    st.stop()

# 3. Interactive Filter
st.sidebar.header("Controls")
companies = df.iloc[:, 0].dropna().unique() # Assumes Company Name is the first column
selected_company = st.sidebar.selectbox("Filter by Company:", ["All Companies"] + list(companies))

if selected_company != "All Companies":
    filtered_df = df[df.iloc[:, 0] == selected_company]
else:
    filtered_df = df

# 4. Top-Level KPIs (Scorecards)
st.markdown("### Quick Metrics")
col1, col2, col3 = st.columns(3)

if selected_company != "All Companies":
    current_discount = filtered_df['Current Discount Value'].iloc[0]
    avg_discount = filtered_df['5-year average discount'].iloc[0]
    
    col1.metric("Current Discount", f"{current_discount}", delta=f"vs 5-yr Avg")
    col2.metric("Stock Price", f"₹{filtered_df['Stock Price'].iloc[0]}")
    col3.metric("Holding Co. Price", f"₹{filtered_df['Holding Company Price'].iloc[0]}")
else:
    st.info("Select a specific company from the sidebar to see isolated metrics.")

st.markdown("---")

# 5. Visualizations
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Current vs 5-Year Avg Discount")
    # Assuming columns are exactly named this in your sheet
    fig1 = px.bar(filtered_df, x=filtered_df.columns[0], y=['Current Discount Value', '5-year average discount'], 
                  barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    st.subheader("Trade Execution: Shares Needed")
    fig2 = px.bar(filtered_df, x=filtered_df.columns[0], y='No of Hold Co share to be bought',
                  color=filtered_df.columns[0])
    st.plotly_chart(fig2, use_container_width=True)

# 6. Raw Data Matrix
st.subheader("Live Execution Matrix")
st.dataframe(filtered_df, use_container_width=True)
