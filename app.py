import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Arbitrage Terminal",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="expanded"
)

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1I48HWtmhga7AAJbFDIhjblHDzNGHZ5ASJtGtVZMTioE"
    "/export?format=csv&gid=0"
)

COL_COMPANY = "Stock"
COL_CURRENT = "Current Discount Value"
COL_AVG     = "5 year average"
COL_MAX     = "Maximum Discount"
COL_MIN     = "Minimum Discount"
COL_PRICE   = "Price"
COL_HOLDCO  = "Holding Company Price"
COL_SHARES  = "Shares of Holding Company to be Bought per Lot"
COL_MEDIAN  = "Median"
COL_MODE    = "Mode"

TRIGGERS = {
    "TVS Motors":             {"entry": 61.0,  "exit": 46.0,  "color": "#2563EB"},
    "Bajaj Finance":          {"entry": 1.3,   "exit": -20.0, "color": "#7C3AED"},
    "Cholamandalam Finance":  {"entry": 47.0,  "exit": 22.0,  "color": "#059669"},
    "SRF":                    {"entry": 78.0,  "exit": 68.0,  "color": "#D97706"},
    "KSP Pumps":              {"entry": 71.0,  "exit": 61.0,  "color": "#DC2626"},
}

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
BG       = "#F0F2F5"
SURFACE  = "#FFFFFF"
BORDER   = "#DDE1E7"
TEXT_PRI = "#0D1117"
TEXT_SEC = "#5A6478"
TEXT_MUT = "#8B93A4"
SIDEBAR  = "#0D1117"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ─ Reset ─ */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}}

/* ─ Page background ─ */
.stApp {{ background-color: {BG}; }}
.block-container {{
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 100% !important;
}}

/* ─ Hide Streamlit chrome ─ */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ─ Sidebar ─ */
section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR} !important;
    border-right: 1px solid #1E2433 !important;
}}
section[data-testid="stSidebar"] .stSelectbox > label {{
    color: {TEXT_MUT} !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}}
section[data-testid="stSidebar"] [data-testid="stSelectboxVirtualDropdown"] {{
    background: #1A2235 !important;
    border-color: #2D3748 !important;
}}

/* ─ Metric cards ─ */
div[data-testid="metric-container"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
}}
div[data-testid="metric-container"] > label {{
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.9px !important;
    color: {TEXT_MUT} !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] > div {{
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: {TEXT_PRI} !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: -1px !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-size: 0.72rem !important;
    font-weight: 600 !important;
}}

/* ─ Dataframe ─ */
div[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}}

/* ─ Divider ─ */
hr {{
    border: none !important;
    border-top: 1px solid {BORDER} !important;
    margin: 1.5rem 0 !important;
}}

/* ─ Spinner ─ */
.stSpinner > div {{ border-top-color: #2563EB !important; }}

/* ── Custom Components ── */
.page-header {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 1.75rem;
    padding-bottom: 1.25rem;
    border-bottom: 2px solid {BORDER};
}}
.page-header-left h1 {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {TEXT_PRI};
    letter-spacing: -0.5px;
    margin: 0 0 3px 0;
    line-height: 1;
}}
.page-header-left p {{
    font-size: 0.78rem;
    color: {TEXT_MUT};
    margin: 0;
    font-weight: 500;
}}
.page-header-right {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.live-pill {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #065F46;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.live-pill-dot {{
    width: 7px; height: 7px;
    background: #10B981;
    border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}}
@keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.2; }} }}

.section-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    color: {TEXT_MUT};
    margin-bottom: 0.75rem;
    display: block;
}}

.card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}

.signal-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}
.sig-strong {{ background:#EFF6FF; color:#1D4ED8; border:1.5px solid #BFDBFE; }}
.sig-buy    {{ background:#F0FDF4; color:#15803D; border:1.5px solid #BBF7D0; }}
.sig-wait   {{ background:#FFFBEB; color:#92400E; border:1.5px solid #FDE68A; }}
.sig-exit   {{ background:#FFF1F2; color:#BE123C; border:1.5px solid #FECDD3; }}

.kv-table {{ width:100%; border-collapse:collapse; }}
.kv-table tr {{ border-bottom: 1px solid #F1F4F8; }}
.kv-table tr:last-child {{ border-bottom: none; }}
.kv-table td {{ padding: 9px 4px; font-size: 0.83rem; line-height: 1.4; }}
.kv-table td:first-child {{ color: {TEXT_SEC}; font-weight: 500; width:55%; }}
.kv-table td:last-child  {{ color: {TEXT_PRI}; font-weight: 700; text-align:right;
                            font-family:'JetBrains Mono',monospace; font-size:0.81rem; }}

.overview-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 18px 20px;
    border-top: 3px solid var(--accent);
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    height: 100%;
}}
.overview-card .oc-name {{
    font-size: 0.7rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.8px; color:{TEXT_MUT}; margin-bottom:6px;
}}
.overview-card .oc-value {{
    font-size: 1.55rem; font-weight:800; letter-spacing:-0.5px;
    font-family:'JetBrains Mono',monospace;
    color: var(--accent); margin-bottom:3px;
}}
.overview-card .oc-delta {{
    font-size: 0.72rem; color:{TEXT_MUT}; font-weight:500; margin-bottom:12px;
}}

.trigger-box {{
    border-radius: 6px;
    padding: 14px 16px;
    border: 1px solid var(--b-color);
    background: var(--bg-color);
}}
.trigger-box .tb-label {{
    font-size:0.65rem; font-weight:700; text-transform:uppercase;
    letter-spacing:1px; color:var(--text-color); margin-bottom:6px;
}}
.trigger-box .tb-value {{
    font-size:1.35rem; font-weight:800; color:var(--text-color);
    font-family:'JetBrains Mono',monospace;
}}
.trigger-box .tb-sub {{
    font-size:0.7rem; color:var(--text-color); opacity:0.75; margin-top:4px;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def clean_pct(val):
    """
    Converts a value to a percentage float.
    Handles strings like "67%", "1.4%", "-34%", or plain numbers.
    Values are assumed to already be in percentage form (e.g. 67, not 0.67).
    """
    try:
        return float(str(val).replace('%', '').replace(',', '').strip())
    except Exception:
        return None

def fmt(val, decimals=2):
    if val is None:
        return "—"
    return f"{val:.{decimals}f}%"

def fmt_price(val):
    try:
        return f"₹{float(str(val).replace(',','')):,.2f}"
    except Exception:
        return str(val)

def get_trigger(company):
    """Case-insensitive, whitespace-tolerant lookup into TRIGGERS."""
    key = company.strip().lower()
    for k, v in TRIGGERS.items():
        if k.strip().lower() == key:
            return v
    return None

def get_signal(current, company):
    t = get_trigger(company)
    if not t or current is None:
        return "wait"
    if current >= t["entry"] + 6:
        return "strong"
    if current >= t["entry"]:
        return "buy"
    if current <= t["exit"]:
        return "exit"
    return "wait"

def signal_badge(sig, include_icon=True):
    MAP = {
        "strong": ("sig-strong", "STRONG BUY",  "↑↑"),
        "buy":    ("sig-buy",    "BUY SIGNAL",  "↑"),
        "wait":   ("sig-wait",   "WAIT",         "—"),
        "exit":   ("sig-exit",   "EXIT",         "↓"),
    }
    cls, label, icon = MAP.get(sig, MAP["wait"])
    prefix = f"{icon} " if include_icon else ""
    return f'<span class="signal-pill {cls}">{prefix}{label}</span>'

def signal_label(sig):
    return {"strong":"Strong Buy","buy":"Buy","wait":"Wait","exit":"Exit"}.get(sig,"Wait")

# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def load_data():
    d = pd.read_csv(SHEET_URL)
    d.columns = d.columns.str.strip()
    return d

try:
    with st.spinner("Connecting to live data..."):
        df = load_data()
except Exception as e:
    st.error(f"Connection failed — {e}")
    st.stop()

companies = df[COL_COMPANY].dropna().unique().tolist()

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 16px 0 16px">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:1.5px;color:#4B5563;margin-bottom:4px">
            ARBITRAGE
        </div>
        <div style="font-size:1.1rem;font-weight:800;color:#F9FAFB;
                    letter-spacing:-0.3px;margin-bottom:2px">
            Terminal
        </div>
        <div style="font-size:0.72rem;color:#6B7280;margin-bottom:24px;
                    padding-bottom:20px;border-bottom:1px solid #1E2433">
            Discount Spread Monitor
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected = st.selectbox(
        "VIEW",
        ["Overview"] + companies,
        key="nav"
    )

    st.markdown("""
    <div style="height:1px;background:#1E2433;margin:16px 0"></div>
    <div style="padding:0 4px">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:1.2px;color:#4B5563;margin-bottom:12px">
            Signal Key
        </div>
    </div>
    """, unsafe_allow_html=True)

    for sig in ["strong","buy","wait","exit"]:
        st.markdown(
            f'<div style="margin-bottom:7px;padding:0 4px">{signal_badge(sig)}</div>',
            unsafe_allow_html=True
        )

    st.markdown(f"""
    <div style="position:absolute;bottom:24px;left:0;right:0;padding:0 16px">
        <div style="height:1px;background:#1E2433;margin-bottom:16px"></div>
        <div style="font-size:0.68rem;color:#4B5563;font-weight:500">
            Auto-refresh · 60s
        </div>
        <div style="font-size:0.72rem;color:#374151;font-weight:600;
                    margin-top:3px;font-family:'JetBrains Mono',monospace">
            {datetime.now().strftime("%H:%M:%S")}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHART THEME — explicit white, no transparency
# ══════════════════════════════════════════════════════════════════════════════
CHART_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="Inter, sans-serif", color=TEXT_SEC),
    margin=dict(l=16, r=16, t=32, b=16),
    xaxis=dict(
        gridcolor="#EAECF0",
        linecolor=BORDER,
        tickcolor=BORDER,
        tickfont=dict(size=11, color=TEXT_SEC),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#EAECF0",
        linecolor=BORDER,
        tickcolor=BORDER,
        tickfont=dict(size=11, color=TEXT_SEC),
        zeroline=True,
        zerolinecolor="#CBD5E1",
        zerolinewidth=1.5,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font=dict(size=11, color=TEXT_SEC),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
#  OVERVIEW PAGE
# ══════════════════════════════════════════════════════════════════════════════
if selected == "Overview":
    now_str = datetime.now().strftime("%d %b %Y  ·  %H:%M")

    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-left">
            <h1>Market Overview</h1>
            <p>Holding company discount arbitrage tracker</p>
        </div>
        <div class="page-header-right">
            <span style="font-size:0.78rem;color:{TEXT_MUT};font-family:'JetBrains Mono',monospace">
                {now_str}
            </span>
            <span class="live-pill">
                <span class="live-pill-dot"></span>Live
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Signal cards ──────────────────────────────────────────────────────────
    cols = st.columns(len(companies), gap="medium")
    for i, company in enumerate(companies):
        row = df[df[COL_COMPANY] == company]
        if row.empty:
            continue
        c_val  = clean_pct(row[COL_CURRENT].iloc[0])
        t      = get_trigger(company) or {}
        color  = t.get("color", "#2563EB")
        sig    = get_signal(c_val, company)
        badge  = signal_badge(sig)
        entry  = t.get("entry")
        delta  = round(c_val - entry, 2) if c_val is not None and entry is not None else None
        delta_str = f"{delta:+.2f}% vs entry trigger" if delta is not None else ""

        with cols[i]:
            st.markdown(f"""
            <div class="overview-card" style="--accent:{color}">
                <div class="oc-name">{company}</div>
                <div class="oc-value">{fmt(c_val)}</div>
                <div class="oc-delta">{delta_str}</div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Comparison chart ─────────────────────────────────────────────────────
    st.markdown('<span class="section-label">Discount Statistics by Company</span>',
                unsafe_allow_html=True)

    # Collect data per company
    ch_names, ch_current, ch_avg, ch_min, ch_max = [], [], [], [], []
    for company in companies:
        row = df[df[COL_COMPANY] == company]
        if row.empty:
            continue
        c  = clean_pct(row[COL_CURRENT].iloc[0])
        a  = clean_pct(row[COL_AVG].iloc[0])
        mn = clean_pct(row[COL_MIN].iloc[0])
        mx = clean_pct(row[COL_MAX].iloc[0])
        if c is None or a is None:
            continue
        ch_names.append(company)
        ch_current.append(round(c,  2))
        ch_avg.append(round(a,  2))
        ch_min.append(round(mn, 2) if mn is not None else None)
        ch_max.append(round(mx, 2) if mx is not None else None)

    # Metric definitions: label, values, color, hover template
    METRICS = [
        ("Current Discount", ch_current, "#2563EB"),
        ("5yr Average",      ch_avg,     "#64748B"),
        ("Minimum Discount", ch_min,     "#10B981"),
        ("Maximum Discount", ch_max,     "#EF4444"),
    ]

    fig_bar = go.Figure()

    for metric_name, values, bar_color in METRICS:
        # Build per-bar hover text with bold company name
        hover_texts = []
        for i, v in enumerate(values):
            company_label = ch_names[i] if i < len(ch_names) else ""
            val_str = f"{v:.2f}%" if v is not None else "—"
            hover_texts.append(
                f"<b style='font-family:Inter,sans-serif;font-size:13px;"
                f"color:#0D1117'>{company_label}</b><br>"
                f"<span style='font-family:Inter,sans-serif;color:#5A6478;"
                f"font-size:11px'>{metric_name}</span><br>"
                f"<span style='font-family:JetBrains Mono,monospace;"
                f"font-size:14px;font-weight:700;color:{bar_color}'>{val_str}</span>"
            )

        safe_values = [v if v is not None else 0 for v in values]

        fig_bar.add_trace(go.Bar(
            name=metric_name,
            x=ch_names,
            y=safe_values,
            marker=dict(
                color=bar_color,
                line=dict(width=0),
                opacity=0.88,
            ),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hover_texts,
            cliponaxis=False,
        ))

    fig_bar.update_layout(**{
        **CHART_LAYOUT,
        "height": 440,
        "barmode": "group",
        "bargap": 0.22,
        "bargroupgap": 0.06,
        "hoverlabel": dict(
            bgcolor=SURFACE,
            bordercolor=BORDER,
            font=dict(family="Inter, sans-serif", size=12, color=TEXT_PRI),
        ),
        "legend": dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color=TEXT_SEC, family="Inter, sans-serif"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        "yaxis": {
            **CHART_LAYOUT["yaxis"],
            "ticksuffix": "%",
            "gridcolor": "#EAECF0",
            "title": dict(
                text="Discount (%)",
                font=dict(size=11, color=TEXT_MUT, family="Inter, sans-serif"),
            ),
        },
        "xaxis": {
            **CHART_LAYOUT["xaxis"],
            "tickfont": dict(
                size=12,
                color=TEXT_PRI,
                family="Inter, sans-serif",
            ),
        },
        "margin": dict(l=16, r=16, t=52, b=16),
    })

    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ── Data matrix ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">Live Arbitrage Matrix</span>',
                unsafe_allow_html=True)

    matrix_rows = []
    for company in companies:
        row = df[df[COL_COMPANY] == company]
        if row.empty: continue
        c   = clean_pct(row[COL_CURRENT].iloc[0])
        a   = clean_pct(row[COL_AVG].iloc[0])
        mx  = clean_pct(row[COL_MAX].iloc[0])
        mn  = clean_pct(row[COL_MIN].iloc[0])
        med = clean_pct(row[COL_MEDIAN].iloc[0]) if COL_MEDIAN in df.columns else None
        t   = get_trigger(company) or {}
        sig = get_signal(c, company)
        gap_to_entry = round(c - t.get("entry", 0), 2) if c else None
        matrix_rows.append({
            "Company":         company,
            "Signal":          signal_label(sig),
            "Current":         fmt(c),
            "5yr Average":     fmt(a),
            "Median":          fmt(med),
            "Maximum":         fmt(mx),
            "Minimum":         fmt(mn),
            "vs Entry":        f"{gap_to_entry:+.2f}%" if gap_to_entry is not None else "—",
        })

    st.dataframe(
        pd.DataFrame(matrix_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company":     st.column_config.TextColumn("Company",     width="medium"),
            "Signal":      st.column_config.TextColumn("Signal",      width="small"),
            "Current":     st.column_config.TextColumn("Current",     width="small"),
            "5yr Average": st.column_config.TextColumn("5yr Average", width="small"),
            "Median":      st.column_config.TextColumn("Median",      width="small"),
            "Maximum":     st.column_config.TextColumn("Maximum",     width="small"),
            "Minimum":     st.column_config.TextColumn("Minimum",     width="small"),
            "vs Entry":    st.column_config.TextColumn("vs Entry",    width="small"),
        }
    )


# ══════════════════════════════════════════════════════════════════════════════
#  INDIVIDUAL COMPANY VIEW
# ══════════════════════════════════════════════════════════════════════════════
else:
    company = selected
    row     = df[df[COL_COMPANY] == company]
    t       = get_trigger(company) or {}
    color   = t.get("color", "#2563EB")

    if row.empty:
        st.error("No data found for this company.")
        st.stop()

    c_val   = clean_pct(row[COL_CURRENT].iloc[0])
    a_val   = clean_pct(row[COL_AVG].iloc[0])
    max_val = clean_pct(row[COL_MAX].iloc[0])
    min_val = clean_pct(row[COL_MIN].iloc[0])
    med_val = clean_pct(row[COL_MEDIAN].iloc[0]) if COL_MEDIAN in df.columns else None
    mode_val= clean_pct(row[COL_MODE].iloc[0])   if COL_MODE   in df.columns else None
    entry_v = t.get("entry")
    exit_v  = t.get("exit")

    sig         = get_signal(c_val, company)
    badge       = signal_badge(sig)
    delta_avg   = round(c_val - a_val, 2)   if c_val and a_val   else None
    delta_entry = round(c_val - entry_v, 2) if c_val and entry_v else None

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-left">
            <h1>{company}</h1>
            <p>Holding company discount analysis &nbsp;·&nbsp;
               Updated {datetime.now().strftime("%H:%M:%S")}</p>
        </div>
        <div class="page-header-right">
            {badge}
            <span class="live-pill">
                <span class="live-pill-dot"></span>Live
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    delta_str = f"{delta_avg:+.2f}% vs 5yr avg" if delta_avg is not None else None

    k1.metric("Current Discount",  fmt(c_val),   delta_str,
              delta_color="off" if delta_avg is None
                          else ("normal" if c_val >= (a_val or 0) else "inverse"))
    k2.metric("5yr Average",       fmt(a_val))
    k3.metric("Median",            fmt(med_val))
    k4.metric("Mode",              fmt(mode_val))
    k5.metric("Maximum",           fmt(max_val))
    k6.metric("Minimum",           fmt(min_val))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main body: chart + right panel ───────────────────────────────────────
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:

        # ── Range position chart ─────────────────────────────────────────────
        st.markdown('<span class="section-label">Discount Range Position</span>',
                    unsafe_allow_html=True)

        if all(v is not None for v in [c_val, min_val, max_val, a_val, entry_v, exit_v]):
            pad   = (max_val - min_val) * 0.08
            x_min = min_val - pad
            x_max = max_val + pad

            fig_range = go.Figure()

            # Zone fills
            for zone_min, zone_max, zone_col, label in [
                (x_min,   exit_v,   "rgba(16,185,129,0.08)",  "Exit Zone"),
                (exit_v,  entry_v,  "rgba(245,158,11,0.08)",  "Wait Zone"),
                (entry_v, x_max,    "rgba(220,38,38,0.08)",   "Buy Zone"),
            ]:
                fig_range.add_shape(
                    type="rect", x0=zone_min, x1=zone_max, y0=0.2, y1=0.8,
                    fillcolor=zone_col, line_width=0, layer="below"
                )
                fig_range.add_annotation(
                    x=(zone_min + zone_max) / 2, y=0.88,
                    text=label, showarrow=False,
                    font=dict(size=9.5, color=TEXT_MUT, family="Inter"),
                    xref="x", yref="y"
                )

            # Zone boundary lines
            for xv, lbl, lclr in [
                (exit_v,  f"Exit<br>{fmt(exit_v)}",   "#D97706"),
                (entry_v, f"Entry<br>{fmt(entry_v)}", "#059669"),
                (a_val,   f"Avg<br>{fmt(a_val)}",     TEXT_SEC),
            ]:
                fig_range.add_shape(
                    type="line", x0=xv, x1=xv, y0=0.2, y1=0.8,
                    line=dict(color=lclr, width=1.5, dash="dot")
                )
                fig_range.add_annotation(
                    x=xv, y=0.12, text=lbl, showarrow=False,
                    font=dict(size=9, color=lclr, family="JetBrains Mono"),
                    xref="x", yref="y", align="center"
                )

            # Track line
            fig_range.add_shape(
                type="line", x0=x_min, x1=x_max, y0=0.5, y1=0.5,
                line=dict(color=BORDER, width=2), layer="below"
            )

            # Current marker
            fig_range.add_trace(go.Scatter(
                x=[c_val], y=[0.5],
                mode="markers+text",
                marker=dict(size=18, color=color,
                            line=dict(width=3, color=SURFACE)),
                text=[fmt(c_val)],
                textposition="top center",
                textfont=dict(size=11, color=color,
                              family="JetBrains Mono"),
                hovertemplate=f"Current: {fmt(c_val)}<extra></extra>",
                showlegend=False,
            ))

            # Axis min/max labels
            for xv, lbl in [(min_val, fmt(min_val)), (max_val, fmt(max_val))]:
                fig_range.add_annotation(
                    x=xv, y=0.88, text=f"<b>{lbl}</b>", showarrow=False,
                    font=dict(size=9.5, color=TEXT_MUT, family="JetBrains Mono"),
                    xref="x", yref="y"
                )

            fig_range.update_layout(
                paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
                height=200,
                margin=dict(l=16, r=16, t=16, b=16),
                xaxis=dict(
                    range=[x_min, x_max],
                    showgrid=False, zeroline=False,
                    showticklabels=False, showline=False,
                ),
                yaxis=dict(
                    range=[0, 1],
                    showgrid=False, zeroline=False,
                    showticklabels=False, showline=False,
                ),
            )
            st.plotly_chart(fig_range, use_container_width=True,
                            config={"displayModeBar": False})

        # ── Entry / Exit trigger boxes ────────────────────────────────────────
        tc1, tc2 = st.columns(2, gap="medium")
        needs = round(entry_v - c_val, 2) if c_val and entry_v else None
        above = round(c_val - exit_v, 2)  if c_val and exit_v  else None

        with tc1:
            st.markdown(f"""
            <div class="trigger-box" style="
                --bg-color:#F0FDF4; --b-color:#A7F3D0; --text-color:#065F46;">
                <div class="tb-label">Entry Trigger</div>
                <div class="tb-value">{fmt(entry_v)}</div>
                <div class="tb-sub">
                    {f'{needs:+.2f}% needed to trigger' if needs else '—'}
                </div>
            </div>""", unsafe_allow_html=True)

        with tc2:
            st.markdown(f"""
            <div class="trigger-box" style="
                --bg-color:#FFFBEB; --b-color:#FDE68A; --text-color:#92400E;">
                <div class="tb-label">Exit Trigger</div>
                <div class="tb-value">{fmt(exit_v)}</div>
                <div class="tb-sub">
                    {f'{above:.2f}% above exit level' if above else '—'}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Right panel ────────────────────────────────────────────────────────
    with right_col:

        st.markdown('<span class="section-label">Execution Data</span>',
                    unsafe_allow_html=True)

        price_val  = row[COL_PRICE].iloc[0]  if COL_PRICE  in row.columns else None
        holdco_val = row[COL_HOLDCO].iloc[0] if COL_HOLDCO in row.columns else None
        shares_val = row[COL_SHARES].iloc[0] if COL_SHARES in row.columns else "—"

        exec_rows = [
            ("Underlying Stock",     fmt_price(price_val)),
            ("Holding Co Price",     fmt_price(holdco_val)),
            ("Shares / Lot",         str(shares_val)),
            ("Current vs Entry",
             f'<span style="color:{"#059669" if delta_entry and delta_entry >= 0 else "#DC2626"};'
             f'font-family:\'JetBrains Mono\',monospace">'
             f'{f"{delta_entry:+.2f}%" if delta_entry is not None else "—"}</span>'),
            ("Signal",               signal_badge(sig, include_icon=False)),
        ]

        rows_html = "".join(
            f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in exec_rows
        )
        st.markdown(
            f'<div class="card"><table class="kv-table">{rows_html}</table></div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Stats panel
        st.markdown('<span class="section-label">Statistics</span>',
                    unsafe_allow_html=True)

        stat_rows = [
            ("Current Discount", fmt(c_val),   color),
            ("5yr Average",      fmt(a_val),   TEXT_SEC),
            ("Median",           fmt(med_val), TEXT_SEC),
            ("Mode",             fmt(mode_val),TEXT_SEC),
            ("Maximum",          fmt(max_val), "#DC2626"),
            ("Minimum",          fmt(min_val), "#059669"),
            ("Entry Trigger",    fmt(entry_v), "#059669"),
            ("Exit Trigger",     fmt(exit_v),  "#D97706"),
        ]
        stat_html = "".join(
            f'<tr><td>{k}</td>'
            f'<td style="color:{c};font-family:\'JetBrains Mono\',monospace">{v}</td></tr>'
            for k, v, c in stat_rows
        )
        st.markdown(
            f'<div class="card"><table class="kv-table">{stat_html}</table></div>',
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  HISTORICAL TIME SERIES
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">Historical Discount — Time Series</span>',
                unsafe_allow_html=True)

    import io

    # Per-company session-state key so uploaded file persists across rerenders
    safe_name = company.replace(' ', '_').replace('/', '_')
    hist_key  = f"hist_data_{safe_name}"

    uploaded = st.file_uploader(
        "Upload historical data (.xlsx)",
        type=["xlsx"],
        key=f"upload_{safe_name}",
        help="Excel file with dates in column A and discount values in column N (stored as decimals, e.g. 0.656 = 65.6%)"
    )

    if uploaded is not None:
        st.session_state[hist_key] = uploaded.read()

    if hist_key in st.session_state and st.session_state[hist_key]:
        hist_bytes = st.session_state[hist_key]

        try:
            xdf = pd.read_excel(io.BytesIO(hist_bytes), header=None)

            # Dates in column 0, discount in column 13 (decimal → %)
            dates     = pd.to_datetime(xdf.iloc[:, 0],  errors='coerce')
            discounts = pd.to_numeric( xdf.iloc[:, 13], errors='coerce') * 100

            hist_df = (
                pd.DataFrame({"date": dates, "discount": discounts})
                .dropna()
                .sort_values("date")
                .reset_index(drop=True)
            )

            if not hist_df.empty:

                # Pre-compute fill colour from the company accent hex
                r_ = int(color[1:3], 16)
                g_ = int(color[3:5], 16)
                b_ = int(color[5:7], 16)
                fill_rgba = f"rgba({r_},{g_},{b_},0.10)"

                hist_mean     = hist_df["discount"].mean()
                hist_max_val  = hist_df["discount"].max()
                hist_min_val  = hist_df["discount"].min()
                hist_max_date = hist_df.loc[hist_df["discount"].idxmax(), "date"]
                hist_min_date = hist_df.loc[hist_df["discount"].idxmin(), "date"]
                hist_med      = hist_df["discount"].median()
                hist_cur      = hist_df["discount"].iloc[-1]

                # ── Build figure ─────────────────────────────────────────────
                fig_ts = go.Figure()

                # Buy zone shading (entry trigger and above)
                if entry_v is not None:
                    y_top = max(hist_max_val * 1.05, entry_v + 5)
                    fig_ts.add_hrect(
                        y0=entry_v, y1=y_top,
                        fillcolor="rgba(37,99,235,0.05)",
                        line_width=0,
                    )

                # Entry trigger line
                if entry_v is not None:
                    fig_ts.add_hline(
                        y=entry_v,
                        line=dict(color="#059669", width=1.5, dash="dash"),
                        annotation_text=f"Entry  {fmt(entry_v)}",
                        annotation_position="top right",
                        annotation_font=dict(
                            size=10, color="#059669",
                            family="JetBrains Mono, monospace"
                        ),
                    )

                # Exit trigger line
                if exit_v is not None:
                    fig_ts.add_hline(
                        y=exit_v,
                        line=dict(color="#D97706", width=1.5, dash="dash"),
                        annotation_text=f"Exit  {fmt(exit_v)}",
                        annotation_position="bottom right",
                        annotation_font=dict(
                            size=10, color="#D97706",
                            family="JetBrains Mono, monospace"
                        ),
                    )

                # Mean line
                fig_ts.add_hline(
                    y=hist_mean,
                    line=dict(color=TEXT_MUT, width=1, dash="dot"),
                    annotation_text=f"Mean  {fmt(hist_mean)}",
                    annotation_position="top left",
                    annotation_font=dict(
                        size=10, color=TEXT_MUT,
                        family="JetBrains Mono, monospace"
                    ),
                )

                # Main discount line with area fill
                fig_ts.add_trace(go.Scatter(
                    x=hist_df["date"],
                    y=hist_df["discount"],
                    mode="lines",
                    name="Discount",
                    line=dict(color=color, width=2),
                    fill="tozeroy",
                    fillcolor=fill_rgba,
                    hovertemplate=(
                        "<b>%{x|%d %b %Y}</b><br>"
                        "Discount: <b>%{y:.2f}%</b>"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                ))

                fig_ts.update_layout(**{
                    **CHART_LAYOUT,
                    "height": 380,
                    "margin": dict(l=16, r=90, t=32, b=16),
                    "hovermode": "x unified",
                    "hoverlabel": dict(
                        bgcolor=SURFACE,
                        bordercolor=BORDER,
                        font=dict(
                            family="Inter, sans-serif",
                            size=12, color=TEXT_PRI
                        ),
                    ),
                    "yaxis": {
                        **CHART_LAYOUT["yaxis"],
                        "ticksuffix": "%",
                        "title": dict(
                            text="Discount (%)",
                            font=dict(
                                size=11, color=TEXT_MUT,
                                family="Inter, sans-serif"
                            ),
                        ),
                    },
                    "xaxis": {
                        **CHART_LAYOUT["xaxis"],
                        "tickformat": "%b '%y",
                        "nticks": 14,
                    },
                })

                st.plotly_chart(
                    fig_ts,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

                # ── Historical stats row ──────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    '<span class="section-label">Historical Statistics</span>',
                    unsafe_allow_html=True
                )

                hs1, hs2, hs3, hs4, hs5 = st.columns(5, gap="small")
                hs1.metric(
                    "Latest (Historical)",
                    fmt(hist_cur),
                )
                hs2.metric(
                    "Maximum",
                    fmt(hist_max_val),
                    hist_max_date.strftime("%d %b %Y"),
                    delta_color="off",
                )
                hs3.metric(
                    "Minimum",
                    fmt(hist_min_val),
                    hist_min_date.strftime("%d %b %Y"),
                    delta_color="off",
                )
                hs4.metric("Mean",   fmt(hist_mean))
                hs5.metric("Median", fmt(hist_med))

            else:
                st.warning("No valid date/discount data found in the uploaded file. "
                           "Check that dates are in column A and discounts in column N.")

        except Exception as e:
            st.error(f"Could not parse Excel file — {e}")
