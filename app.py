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
    selected_company = st.selectbox("🎯 Target Company:", ["All Market Overview"] + list(companies))
    st.markdown("---")
    st.caption("Data refreshes automatically every 60s.")

# 4. Main Dashboard Header
if selected_company == "All Market Overview":
    st.header("🌐 Market Overview")
    filtered_df = df
else:
    st.header(f"📊 {selected_company} Analytics")
    filtered_df = df[df[company_col] == selected_company]

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# 5. Top Level KPI Scorecards
try:
    if selected_company != "All Market Overview":
        col1, col2, col3, col4 = st.columns(4)
        
        current_disc = filtered_df[current_col].iloc[0]
        avg_disc = filtered_df[avg_col].iloc[0]
        
        # Calculate Delta to show if the spread is better than average
        if isinstance(current_disc, str): current_disc = float(current_disc.replace('%', '').strip())
        if isinstance(avg_disc, str): avg_disc = float(avg_disc.replace('%', '').strip())
        delta_val = round(current_disc - avg_disc, 2)
        
        col1.metric("Current Discount", f"{current_disc}%", f"{delta_val}% vs Avg", delta_color="normal")
        col2.metric("5-Year Average", f"{avg_disc}%")
        col3.metric("Stock Price", f"₹{filtered_df[stock_price_col].iloc[0]}")
        col4.metric("Holding Co. Price", f"₹{filtered_df[hold_co_col].iloc[0]}")
    else:
        # Show average metrics across the board
        col1, col2, col3 = st.columns(3)
        col1.metric("Tracked Pairs", f"{len(filtered_df)}")
        col2.metric("Market Status", "Active", "Live Connection")
        col3.metric("Strategy", "Holding Company Arbitrage")

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # 6. Tabbed Interface for clean UX
    tab1, tab2 = st.tabs(["📈 Visual Analytics", "🧮 Execution Matrix"])

    with tab1:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### Discount Spread Analysis")
            # Melt data for grouped bar chart
            melted_df = filtered_df.melt(
                id_vars=[company_col], 
                value_vars=[current_col, avg_col], 
                var_name='Metric', 
                value_name='Percentage'
            )
            
            # Clean numeric values for charting
            melted_df['Percentage'] = melted_df['Percentage'].astype(str).str.replace('%', '').astype(float)
            
            fig1 = px.bar(
                melted_df, x=company_col, y='Percentage', color='Metric', barmode='group',
                color_discrete_sequence=['#1f77b4', '#aec7e8'] # Professional blue tones
            )
            fig1.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend_title_text='',
                xaxis_title="",
                yaxis_title="Discount (%)",
                hovermode="x unified",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.markdown("#### Execution Sizing (Shares to Buy)")
            fig2 = px.bar(
                filtered_df, x=company_col, y=shares_needed_col, 
                color=company_col, text=shares_needed_col,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig2.update_traces(textposition='outside')
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis_title="",
                yaxis_title="Volume",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("#### Live Trade Execution Data")
        # Format the dataframe so it looks like a professional table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                stock_price_col: st.column_config.NumberColumn("Stock Price", format="₹%.2f"),
                hold_co_col: st.column_config.NumberColumn("Hold Co Price", format="₹%.2f"),
                current_col: st.column_config.TextColumn("Current Discount"),
                avg_col: st.column_config.TextColumn("5Yr Avg"),
                shares_needed_col: st.column_config.NumberColumn("Shares to Buy", help="Amount per lot")
            }
        )

except KeyError as e:
    st.error(f"🚨 Column Error: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
