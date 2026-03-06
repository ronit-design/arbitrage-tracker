import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Setup & Pro CSS Styling
st.set_page_config(page_title="Arbitrage Terminal", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Global spacing and font tweaks */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 98%; font-family: 'Inter', sans-serif;}
    
    /* Sleek Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #0f172a;
    }
    
    /* Hide Streamlit UI elements for a standalone app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Headers */
    h1, h2, h3 { color: #0f172a; font-weight: 700 !important; }
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
    with st.spinner('Synchronizing with live market data...'):
        df = load_data()
except Exception as e:
    st.error(f"Connection Failed: {e}")
    st.stop()

# --- EXACT COLUMN DEFINITIONS ---
company_col = 'Stock'
current_col = 'Current Discount Value'
avg_col = '5 year average'  
max_col = 'Maximum Discount'
min_col = 'Minimum Discount'
stock_price_col = 'Price'
hold_co_col = 'Holding Company Price'
shares_needed_col = 'Shares of Holding Company to be Bought per Lot'

# Helper function to safely convert percentage strings to numbers for charting
def clean_pct(val):
    try:
        return float(str(val).replace('%', '').replace(',', '').strip())
    except:
        return 0.0

# 3. Sidebar Controls
with st.sidebar:
    st.title("🏦 Arbitrage Desk")
    st.markdown("Live Discount Spread Tracker")
    st.markdown("---")
    companies = df[company_col].dropna().unique() 
    selected_company = st.selectbox("🎯 Target Pair:", ["Overview"] + list(companies))
    st.markdown("---")
    st.caption("🟢 Status: Connected (Refreshes 60s)")

# 4. Main Dashboard View
if selected_company == "Overview":
    st.header("🌐 Market Overview")
    st.info("👈 Select a specific company pair from the sidebar to view deep analytics and historical spread ranges.")
    
    # Overview Table
    st.markdown("#### Live Arbitrage Matrix")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            stock_price_col: st.column_config.NumberColumn("Stock Price", format="₹%.2f"),
            hold_co_col: st.column_config.NumberColumn("Hold Co Price", format="₹%.2f"),
            shares_needed_col: st.column_config.NumberColumn("Shares to Buy")
        }
    )
    
else:
    # Filter data for selected company
    filtered_df = df[df[company_col] == selected_company]
    st.header(f"📊 {selected_company} Analytics")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Extract metrics and clean them for math/display
    try:
        c_val_raw = filtered_df[current_col].iloc[0]
        a_val_raw = filtered_df[avg_col].iloc[0]
        max_val_raw = filtered_df[max_col].iloc[0]
        min_val_raw = filtered_df[min_col].iloc[0]
        
        c_val = clean_pct(c_val_raw)
        a_val = clean_pct(a_val_raw)
        max_val = clean_pct(max_val_raw)
        min_val = clean_pct(min_val_raw)
        
        delta_val = round(c_val - a_val, 2)
        delta_str = f"{delta_val}% vs 5Yr Avg"
        
        # 5. Prominent KPI Scorecards (Focused entirely on the spread)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Discount", f"{c_val}%", delta_str, delta_color="normal")
        col2.metric("5-Year Mean", f"{a_val}%")
        col3.metric("Maximum Discount", f"{max_val}%")
        col4.metric("Minimum Discount", f"{min_val}%")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 6. Advanced Bullet Chart Visualization
        st.markdown("#### Spread Range Indicator")
        st.markdown("Visualizing where the current discount sits historically. The black marker is the 5-Year Mean.")
        
        fig_bullet = go.Figure(go.Indicator(
            mode = "number+gauge+delta",
            value = c_val,
            number = {'suffix': "%", 'font': {'size': 40, 'color': '#0f172a'}},
            delta = {'reference': a_val, 'position': "top", 'suffix': "%"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'shape': "bullet",
                'axis': {'range': [min_val - 5, max_val + 5]},
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': a_val
                },
                'steps': [
                    {'range': [min_val, a_val], 'color': "#e2e8f0"},
                    {'range': [a_val, max_val], 'color': "#cbd5e1"}
                ],
                'bar': {'color': "#3b82f6", 'thickness': 0.4} # Blue fill for current value
            }
        ))
        
        fig_bullet.update_layout(
            height=250, 
            margin=dict(l=20, r=30, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bullet, use_container_width=True)
        
        st.markdown("---")
        
        # 7. Execution Data Split
        col_exec1, col_exec2 = st.columns(2)
        with col_exec1:
            st.markdown("#### Price Data")
            st.write(f"**Stock Price:** ₹{filtered_df[stock_price_col].iloc[0]}")
            st.write(f"**Holding Company Price:** ₹{filtered_df[hold_co_col].iloc[0]}")
            
        with col_exec2:
            st.markdown("#### Execution Sizing")
            shares = filtered_df[shares_needed_col].iloc[0]
            st.info(f"Shares to be bought per lot: **{shares}**")

    except Exception as e:
        st.error(f"Error calculating metrics for this company. Make sure the sheet data isn't blank. Details: {e}")
