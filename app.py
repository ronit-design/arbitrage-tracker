import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Arbitrage Terminal",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ENTRY / EXIT TRIGGERS (from investment memos) ────────────────────────────
TRIGGERS = {
    "TVS Holdings":           {"entry": 61.0,  "exit": 46.0,  "color": "#3b82f6"},
    "Bajaj Finserv":          {"entry": 1.3,   "exit": -20.0, "color": "#8b5cf6"},
    "Chola Holdings":         {"entry": 47.0,  "exit": 22.0,  "color": "#10b981"},
    "Kama Holdings":          {"entry": 78.0,  "exit": 68.0,  "color": "#f59e0b"},
    "Industrial Prudential":  {"entry": 71.0,  "exit": 61.0,  "color": "#ef4444"},
}

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 98%;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ── Metric Cards ── */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e8edf3;
    border-radius: 10px;
    padding: 18px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
div[data-testid="metric-container"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #64748b !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}

/* ── Signal badges ── */
.badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-buy      { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.badge-strong   { background: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; }
.badge-wait     { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-exit     { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }

/* ── Overview cards ── */
.holding-card {
    background: #ffffff;
    border: 1px solid #e8edf3;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    border-left: 4px solid #3b82f6;
    cursor: pointer;
}
.holding-card h4 {
    margin: 0 0 4px 0;
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
}
.holding-card .sub {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 14px;
}
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
.stat-cell label {
    display: block;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 3px;
}
.stat-cell span {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
}

/* ── Section headers ── */
.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #94a3b8;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f1f5f9;
}

/* ── Range bar ── */
.range-wrap {
    background: #f8fafc;
    border: 1px solid #e8edf3;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 6px;
}
.range-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 8px;
}

/* ── Execution box ── */
.exec-box {
    background: #f8fafc;
    border: 1px solid #e8edf3;
    border-radius: 10px;
    padding: 18px 20px;
}
.exec-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.85rem;
}
.exec-row:last-child { border-bottom: none; }
.exec-row .elabel { color: #64748b; font-weight: 500; }
.exec-row .evalue { font-weight: 700; color: #0f172a; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
}
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; font-size: 0.75rem !important; }

/* ── Dataframe ── */
.dataframe { font-size: 0.83rem; }

/* ── Divider ── */
hr { border-color: #f1f5f9 !important; margin: 1.2rem 0 !important; }

/* ── Page title ── */
.page-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
}
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def clean_pct(val):
    try:
        return float(str(val).replace('%', '').replace(',', '').strip())
    except:
        return None

def get_signal(current, company):
    t = TRIGGERS.get(company)
    if t is None or current is None:
        return "wait"
    if current >= t["entry"] + 6:
        return "strong"
    if current >= t["entry"]:
        return "buy"
    if current <= t["exit"]:
        return "exit"
    return "wait"

def signal_html(sig):
    map_ = {
        "strong": ('<span class="badge badge-strong">⚡ Strong Buy</span>', "Strong Buy Signal"),
        "buy":    ('<span class="badge badge-buy">✅ Buy Signal</span>', "Buy Signal"),
        "wait":   ('<span class="badge badge-wait">⏳ Wait</span>', "Wait"),
        "exit":   ('<span class="badge badge-exit">🔴 Exit</span>', "Exit Signal"),
    }
    return map_.get(sig, map_["wait"])

def fmt_pct(val):
    if val is None:
        return "—"
    return f"{val:+.2f}%" if val < 0 else f"{val:.2f}%"

def range_progress(current, min_val, max_val):
    """Returns 0–100 position of current within [min, max]"""
    if max_val == min_val:
        return 50
    return max(0, min(100, (current - min_val) / (max_val - min_val) * 100))


# ─── DATA ─────────────────────────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1I48HWtmhga7AAJbFDIhjblHDzNGHZ5ASJtGtVZMTioE/export?format=csv&gid=0"

COL_COMPANY  = 'Stock'
COL_CURRENT  = 'Current Discount Value'
COL_AVG      = '5 year average'
COL_MAX      = 'Maximum Discount'
COL_MIN      = 'Minimum Discount'
COL_PRICE    = 'Price'
COL_HOLDCO   = 'Holding Company Price'
COL_SHARES   = 'Shares of Holding Company to be Bought per Lot'
COL_MEDIAN   = 'Median'   # add this column to your sheet, or we calculate below
COL_MODE     = 'Mode'     # add this column to your sheet, or we calculate below

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    with st.spinner(''):
        df = load_data()
except Exception as e:
    st.error(f"⚠ Could not connect to Google Sheet: {e}")
    st.stop()


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏦 Arbitrage Terminal")
    st.markdown('<div style="font-size:0.78rem;color:#64748b;margin-bottom:16px">Discount Spread Tracker</div>', unsafe_allow_html=True)
    st.markdown("---")
    companies = df[COL_COMPANY].dropna().unique().tolist()
    selected = st.selectbox("Select Pair", ["📊 Overview"] + companies, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f'<div style="font-size:0.72rem;color:#475569"><span class="live-dot"></span>Live · Refreshes every 60s</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.72rem;color:#475569;margin-top:6px">Last sync: {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    st.markdown("---")
    # Mini legend
    st.markdown('<div style="font-size:0.7rem;color:#475569;font-weight:600;margin-bottom:8px">SIGNAL KEY</div>', unsafe_allow_html=True)
    for label, cls in [("⚡ Strong Buy", "badge-strong"), ("✅ Buy Signal", "badge-buy"), ("⏳ Wait", "badge-wait"), ("🔴 Exit", "badge-exit")]:
        st.markdown(f'<span class="badge {cls}" style="margin-bottom:4px;display:inline-block">{label}</span>', unsafe_allow_html=True)


# ─── OVERVIEW ─────────────────────────────────────────────────────────────────
if selected == "📊 Overview":
    now_str = datetime.now().strftime("%A, %d %B %Y · %H:%M")
    st.markdown(f'<div class="page-title">Market Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle"><span class="live-dot"></span>Live data · {now_str}</div>', unsafe_allow_html=True)

    # ── Summary signal row ──
    cols = st.columns(len(companies))
    for i, company in enumerate(companies):
        row = df[df[COL_COMPANY] == company]
        if row.empty:
            continue
        c_val  = clean_pct(row[COL_CURRENT].iloc[0])
        t      = TRIGGERS.get(company, {})
        color  = t.get("color", "#3b82f6")
        sig    = get_signal(c_val, company)
        badge, badge_text = signal_html(sig)
        delta  = (c_val - t["entry"]) if c_val is not None and "entry" in t else None
        delta_str = f"{delta:+.1f}% vs entry" if delta is not None else ""

        with cols[i]:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e8edf3;border-radius:12px;
                        padding:16px 18px;border-top:4px solid {color};
                        box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.8px;color:#94a3b8;margin-bottom:6px">
                    {company}
                </div>
                <div style="font-size:1.6rem;font-weight:800;color:{color};margin-bottom:4px">
                    {fmt_pct(c_val)}
                </div>
                <div style="font-size:0.72rem;color:#94a3b8;margin-bottom:10px">{delta_str}</div>
                {badge}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Full data table ──
    st.markdown('<div class="section-header">Live Arbitrage Matrix</div>', unsafe_allow_html=True)

    # Build a clean display df
    display_rows = []
    for company in companies:
        row = df[df[COL_COMPANY] == company]
        if row.empty:
            continue
        c_val   = clean_pct(row[COL_CURRENT].iloc[0])
        a_val   = clean_pct(row[COL_AVG].iloc[0])
        max_val = clean_pct(row[COL_MAX].iloc[0])
        min_val = clean_pct(row[COL_MIN].iloc[0])
        sig     = get_signal(c_val, company)
        _, badge_text = signal_html(sig)
        display_rows.append({
            "Company":          company,
            "Signal":           badge_text,
            "Current Discount": f"{c_val:.2f}%" if c_val is not None else "—",
            "5yr Average":      f"{a_val:.2f}%" if a_val is not None else "—",
            "Max":              f"{max_val:.2f}%" if max_val is not None else "—",
            "Min":              f"{min_val:.2f}%" if min_val is not None else "—",
            "vs Entry":         f"{(c_val - TRIGGERS.get(company, {}).get('entry', 0)):+.1f}%" if c_val else "—",
        })

    st.dataframe(
        pd.DataFrame(display_rows),
        use_container_width=True,
        hide_index=True,
    )

    # ── Comparative bar chart ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Current Discount vs 5yr Average</div>', unsafe_allow_html=True)

    chart_companies, chart_current, chart_avg, chart_entry, chart_colors = [], [], [], [], []
    for company in companies:
        row = df[df[COL_COMPANY] == company]
        if row.empty: continue
        c = clean_pct(row[COL_CURRENT].iloc[0])
        a = clean_pct(row[COL_AVG].iloc[0])
        t = TRIGGERS.get(company, {})
        if c is not None and a is not None:
            chart_companies.append(company)
            chart_current.append(c)
            chart_avg.append(a)
            chart_entry.append(t.get("entry"))
            chart_colors.append(t.get("color", "#3b82f6"))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Current Discount",
        x=chart_companies,
        y=chart_current,
        marker_color=chart_colors,
        marker_line_width=0,
        text=[f"{v:.1f}%" for v in chart_current],
        textposition="outside",
        textfont=dict(size=12, color="#0f172a"),
    ))
    fig.add_trace(go.Scatter(
        name="5yr Average",
        x=chart_companies,
        y=chart_avg,
        mode="markers",
        marker=dict(symbol="line-ew", size=20, color="#64748b", line=dict(width=3, color="#64748b")),
    ))
    fig.add_trace(go.Scatter(
        name="Entry Trigger",
        x=chart_companies,
        y=chart_entry,
        mode="markers",
        marker=dict(symbol="line-ew", size=20, color="#22c55e", line=dict(width=3, color="#22c55e")),
    ))
    fig.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, color="#64748b")),
        yaxis=dict(ticksuffix="%", gridcolor="#f1f5f9", tickfont=dict(color="#94a3b8", size=10)),
        xaxis=dict(tickfont=dict(color="#64748b", size=11)),
        bargap=0.35,
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── INDIVIDUAL COMPANY VIEW ───────────────────────────────────────────────────
else:
    company  = selected
    row      = df[df[COL_COMPANY] == company]
    t        = TRIGGERS.get(company, {})
    color    = t.get("color", "#3b82f6")

    if row.empty:
        st.error("No data found for this company.")
        st.stop()

    c_val   = clean_pct(row[COL_CURRENT].iloc[0])
    a_val   = clean_pct(row[COL_AVG].iloc[0])
    max_val = clean_pct(row[COL_MAX].iloc[0])
    min_val = clean_pct(row[COL_MIN].iloc[0])

    # Try to get median/mode from sheet, else show "—"
    median_val = clean_pct(row[COL_MEDIAN].iloc[0]) if COL_MEDIAN in row.columns else None
    mode_val   = clean_pct(row[COL_MODE].iloc[0])   if COL_MODE   in row.columns else None

    sig          = get_signal(c_val, company)
    badge, badge_text = signal_html(sig)
    delta        = round(c_val - a_val, 2) if c_val is not None and a_val is not None else None
    entry_delta  = round(c_val - t.get("entry", 0), 2) if c_val is not None else None

    # Page header
    now_str = datetime.now().strftime("%H:%M:%S")
    st.markdown(f'<div class="page-title">{company}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle"><span class="live-dot"></span>Live · Last updated {now_str} &nbsp;·&nbsp; {badge}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI Row ──
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    delta_str = f"{delta:+.2f}% vs 5yr avg" if delta is not None else None

    col1.metric("Current Discount", fmt_pct(c_val), delta_str,
                delta_color="off" if delta is None else ("normal" if c_val >= (a_val or 0) else "inverse"))
    col2.metric("5yr Average", fmt_pct(a_val))
    col3.metric("Median", fmt_pct(median_val))
    col4.metric("Mode", fmt_pct(mode_val))
    col5.metric("Maximum", fmt_pct(max_val))
    col6.metric("Minimum", fmt_pct(min_val))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two column layout ──
    left, right = st.columns([3, 2], gap="large")

    with left:
        # Gauge chart
        st.markdown('<div class="section-header">Discount Range Visualiser</div>', unsafe_allow_html=True)

        if c_val is not None and min_val is not None and max_val is not None:
            fig_gauge = go.Figure(go.Indicator(
                mode="number+gauge+delta",
                value=c_val,
                number={"suffix": "%", "font": {"size": 44, "color": "#0f172a", "family": "Inter"}},
                delta={"reference": a_val, "position": "top", "suffix": "%",
                       "font": {"size": 14}, "valueformat": "+.2f"},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "shape": "bullet",
                    "axis": {
                        "range": [min_val - 3, max_val + 3],
                        "ticksuffix": "%",
                        "tickfont": {"size": 10, "color": "#94a3b8"},
                        "tickcolor": "#e2e8f0",
                    },
                    "threshold": {
                        "line": {"color": "#1e293b", "width": 4},
                        "thickness": 0.8,
                        "value": a_val,
                    },
                    "steps": [
                        {"range": [min_val - 3, t.get("exit", min_val)],  "color": "#dcfce7"},
                        {"range": [t.get("exit", min_val), t.get("entry", a_val)], "color": "#fef9c3"},
                        {"range": [t.get("entry", a_val), max_val + 3], "color": "#fee2e2"},
                    ],
                    "bar": {"color": color, "thickness": 0.35},
                }
            ))
            fig_gauge.add_annotation(
                x=0.02, y=0.05, xref="paper", yref="paper",
                text="← Exit Zone", showarrow=False,
                font=dict(size=9, color="#15803d"),
            )
            fig_gauge.add_annotation(
                x=0.98, y=0.05, xref="paper", yref="paper",
                text="Buy Zone →", showarrow=False,
                font=dict(size=9, color="#b91c1c"),
            )
            fig_gauge.update_layout(
                height=220,
                margin=dict(l=20, r=30, t=50, b=30),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Entry/exit trigger info
        c1, c2 = st.columns(2)
        entry_v = t.get("entry")
        exit_v  = t.get("exit")
        with c1:
            needs = round(entry_v - c_val, 2) if c_val is not None and entry_v is not None else None
            st.markdown(f"""
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 16px;">
                <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;
                            color:#15803d;margin-bottom:6px">Entry Trigger</div>
                <div style="font-size:1.4rem;font-weight:800;color:#15803d">{fmt_pct(entry_v)}</div>
                <div style="font-size:0.73rem;color:#16a34a;margin-top:4px">
                    {f'{needs:+.2f}% needed' if needs is not None else '—'}
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            gap = round(c_val - exit_v, 2) if c_val is not None and exit_v is not None else None
            st.markdown(f"""
            <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:14px 16px;">
                <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;
                            color:#c2410c;margin-bottom:6px">Exit Trigger</div>
                <div style="font-size:1.4rem;font-weight:800;color:#c2410c">{fmt_pct(exit_v)}</div>
                <div style="font-size:0.73rem;color:#ea580c;margin-top:4px">
                    {f'{gap:.2f}% above exit' if gap is not None else '—'}
                </div>
            </div>""", unsafe_allow_html=True)

    with right:
        # Execution data
        st.markdown('<div class="section-header">Execution Data</div>', unsafe_allow_html=True)

        price_val  = row[COL_PRICE].iloc[0]  if COL_PRICE  in row.columns else "—"
        holdco_val = row[COL_HOLDCO].iloc[0] if COL_HOLDCO in row.columns else "—"
        shares_val = row[COL_SHARES].iloc[0] if COL_SHARES in row.columns else "—"

        try: price_str  = f"₹{float(str(price_val).replace(',','')):,.2f}"
        except: price_str = str(price_val)
        try: holdco_str = f"₹{float(str(holdco_val).replace(',','')):,.2f}"
        except: holdco_str = str(holdco_val)

        st.markdown(f"""
        <div class="exec-box">
            <div class="exec-row">
                <span class="elabel">Underlying Stock Price</span>
                <span class="evalue">{price_str}</span>
            </div>
            <div class="exec-row">
                <span class="elabel">Holding Co Price</span>
                <span class="evalue">{holdco_str}</span>
            </div>
            <div class="exec-row">
                <span class="elabel">Shares to Buy / Lot</span>
                <span class="evalue">{shares_val}</span>
            </div>
            <div class="exec-row">
                <span class="elabel">Current vs Entry</span>
                <span class="evalue" style="color:{'#15803d' if entry_delta is not None and entry_delta >= 0 else '#b91c1c'}">
                    {f'{entry_delta:+.2f}%' if entry_delta is not None else '—'}
                </span>
            </div>
            <div class="exec-row">
                <span class="elabel">Signal</span>
                <span class="evalue">{badge_text}</span>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # All stats summary
        st.markdown('<div class="section-header">Statistics Summary</div>', unsafe_allow_html=True)
        stats = [
            ("Current",  fmt_pct(c_val),    color),
            ("5yr Avg",  fmt_pct(a_val),    "#64748b"),
            ("Median",   fmt_pct(median_val),"#64748b"),
            ("Mode",     fmt_pct(mode_val),  "#64748b"),
            ("Maximum",  fmt_pct(max_val),   "#ef4444"),
            ("Minimum",  fmt_pct(min_val),   "#22c55e"),
        ]
        rows_html = "".join([
            f"""<div class="exec-row">
                <span class="elabel">{label}</span>
                <span class="evalue" style="color:{clr}">{val}</span>
            </div>"""
            for label, val, clr in stats
        ])
        st.markdown(f'<div class="exec-box">{rows_html}</div>', unsafe_allow_html=True)
