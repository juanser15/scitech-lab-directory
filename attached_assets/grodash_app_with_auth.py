# -*- coding: utf-8 -*-
"""
SciTech Investments Dashboard v4.2.2 - Institutional Grade
=========================================================
Professional performance analytics with:
- Yahoo Finance benchmark integration
- Interactive clickable charts
- Benchmark correlation/beta/alpha analysis
- Auto-load data.xlsx support
- Redesigned aesthetics and organization

Author: SciTech Quantitative Research | SciTech Investments
"""

VERSION = "4.2.2"

ENV = "PROD"
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SciTech Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

VALID_USERS = {
    # Equipo original
    'john': 'Sc1T3ch_JOHN_2025!',
    'analyst': 'Sc1T3ch_Analyst_2025!',
    'demo': 'Sc1T3ch_DWEMO_2025!',
    
    # Equipo SciTech
    'malena.peroni@sci.tech': 'Sc1T3ch_MP_2025!',
    'juan.serur@sci.tech': 'Sc1T3ch_JS_2025!',
    'martin.garay@sci.tech': 'Sc1T3ch_MG_2025!',
    'federico.massimo@sci.tech': 'Sc1T3ch_FM_2025!',
    'evelyn.mancini@sci.tech': 'Sc1T3ch_EM_2025!',
    'sergio.canceco@sci.tech': 'Sc1T3ch_SC_2025!',
    'eduardo.ploskinos@sci.tech': 'Sc1T3ch_EP_2025!',
    'miguel.acevedos@sci.tech': 'Sc1T3ch_MA_2025!',
    'patricio.barba@sci.tech': 'Sc1T3ch_PB_2025!',
    'nicolas.fortunato@sci.tech': 'Sc1T3ch_NF_2025!',
    'juan.gallego@sci.tech': 'Sc1T3ch_JG_2025!',
    'gregoria.rodriguez@sci.tech': 'Sc1T3ch_GR_2025!',
    'ricardo.centeno@sci.tech': 'Sc1T3ch_RC_2025!',
    'tobias.treutel@sci.tech': 'Sc1T3ch_TT_2025!',
    'leonel.lalia@sci.tech': 'Sc1T3ch_LL_2025!',
    'lucas.petronio@sci.tech': 'Sc1T3ch_LP_2026!THEYEAR',
    'maximiliano.markous@sci.tech': 'Sc1T3ch_MM_2025!',
    'stevo.ostoic@sci.tech': 'Sc1T3ch_SO_2025!',
    'milton.muller@sci.tech': 'Sc1T3ch_MMu_2025!',
    'fernando.segovia@sci.tech': 'Sc1T3ch_FS_2025!',
    'luis.segovia@sci.tech': 'Sc1T3ch_LS_2025!',
    'matias.romano@sci.tech': 'Sc1T3ch_MR_2025!',
    'eduardo.picon@sci.tech': 'Sc1T3ch_EPi_2025!',
    'alberto.cardenas@sci.tech': 'Sc1T3ch_AC_2025!',
    'russellpharos@gmail.com': 'Sc1T3ch_JR_2025!',
    'ihs@sci.tech': 'Sc1T3ch_IHS_2025!',
}

def check_password():
    """Returns `True` if the user had a correct password."""
    
    def login_form():
        """Form with widgets to collect user information"""
        st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: linear-gradient(145deg, #151b23 0%, #12171d 100%);
            border: 1px solid #2a3441;
            border-radius: 16px;
        }
        .login-title {
            text-align: center;
            color: #f0f4f8;
            font-size: 24px;
            margin-bottom: 8px;
        }
        .login-subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 32px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 SciTech Dashboard")
            st.markdown("*GroWise Reporting System*")
            st.markdown("---")
            with st.form("credentials"):
                username = st.text_input("Username", key="username")
                password = st.text_input("Password", type="password", key="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                if submit:
                    password_entered()

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state.get("username", "")
        password = st.session_state.get("password", "")
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state["password_correct"] = True
            st.session_state["current_user"] = username
        else:
            st.session_state["password_correct"] = False

    # First run or logged out
    if "password_correct" not in st.session_state:
        login_form()
        return False
    
    # Password incorrect
    if not st.session_state["password_correct"]:
        login_form()
        st.error("User not known or password incorrect")
        return False
    
    # Password correct
    return True

# Authentication gate
if not check_password():
    st.stop()

# Clear cache on version change to ensure fresh deployment
if 'app_version' not in st.session_state or st.session_state.app_version != VERSION:
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.app_version = VERSION

# ═══════════════════════════════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    'bg_primary': '#0a0e12',
    'bg_secondary': '#12171d',
    'bg_tertiary': '#1a2028',
    'bg_card': '#151b23',
    'bg_hover': '#1e2530',
    'border': '#2a3441',
    'border_light': '#3d4a5c',
    'text_primary': '#f0f4f8',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'green': '#22c55e',
    'green_light': '#4ade80',
    'green_dim': 'rgba(34, 197, 94, 0.12)',
    'red': '#ef4444',
    'red_light': '#f87171',
    'red_dim': 'rgba(239, 68, 68, 0.12)',
    'blue': '#3b82f6',
    'blue_light': '#60a5fa',
    'gold': '#f59e0b',
    'purple': '#a855f7',
    'cyan': '#06b6d4',
    'orange': '#f97316',
    'pink': '#ec4899',
}

# --- Theme safety: ensure required color keys exist (prevents KeyError in prod) ---
_REQUIRED_COLORS = {
    'bg_primary': '#0a0e12',
    'bg_secondary': '#12171d',
    'bg_tertiary': '#1a2028',
    'bg_card': '#151b23',
    'border': '#2a3441',
    'text_primary': '#f0f4f8',
    'text_secondary': '#94a3b8',
}
for _k, _v in _REQUIRED_COLORS.items():
    if _k not in COLORS:
        COLORS[_k] = _v


PIE_COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#a855f7', '#06b6d4', '#f97316', '#ec4899', 
              '#ef4444', '#64748b', '#84cc16', '#14b8a6', '#8b5cf6', '#f43f5e', '#0ea5e9']

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-primary: #0a0e12;
    --bg-secondary: #12171d;
    --bg-card: #151b23;
    --border: #2a3441;
    --text-primary: #f0f4f8;
    --text-secondary: #94a3b8;
    --green: #22c55e;
    --red: #ef4444;
    --blue: #3b82f6;
}

/* Hide Streamlit branding */
#MainMenu {display: none;}
footer {display: none;}
header {visibility: hidden; height: 0;}
.block-container { padding-top: 1.2rem; }

.stApp { background: var(--bg-primary); }

.block-container {
    padding: 1.2rem 2rem 3rem 2rem;
    max-width: 1900px;
}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR STYLING - Premium Look (Always Visible)
   ═══════════════════════════════════════════════════════════════ */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1419 0%, #0a0e12 100%);
    border-right: 1px solid rgba(42, 52, 65, 0.5);
    min-width: 320px !important;
    width: 320px !important;
}

/* Force sidebar to always be visible */
section[data-testid="stSidebar"][aria-expanded="false"] {
    display: block !important;
    min-width: 320px !important;
    width: 320px !important;
    margin-left: 0 !important;
    transform: none !important;
}

/* Hide the collapse button */
button[data-testid="stSidebarCollapseButton"],
button[kind="headerNoPadding"],
[data-testid="collapsedControl"] {
    display: none !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
}

/* Sidebar text styling */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    font-family: 'Inter', sans-serif !important;
    color: #94a3b8 !important;
}

/* File uploader - Complete redesign */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div:first-child {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%) !important;
    border: 1px dashed rgba(71, 85, 105, 0.5) !important;
    border-radius: 10px !important;
    padding: 16px !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div:first-child:hover {
    border-color: rgba(59, 130, 246, 0.5) !important;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.6) 100%) !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%) !important;
    border: none !important;
    border-radius: 6px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
    transform: translateY(-1px);
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] small {
    color: #64748b !important;
    font-size: 10px !important;
}

/* Uploaded file indicator */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
    background: rgba(34, 197, 94, 0.1) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    margin-top: 8px !important;
}

/* Selectbox styling */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(71, 85, 105, 0.4) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(59, 130, 246, 0.5) !important;
}

/* Checkbox styling */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] {
    background: transparent !important;
}

section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
    color: #94a3b8 !important;
    font-size: 13px !important;
}

section[data-testid="stSidebar"] [data-testid="stCheckbox"] span[data-testid="stCheckboxBox"] {
    background: rgba(30, 41, 59, 0.6) !important;
    border: 1px solid rgba(71, 85, 105, 0.5) !important;
    border-radius: 4px !important;
}

/* Radio buttons */
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 6px !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(30, 41, 59, 0.3) !important;
    border: 1px solid rgba(71, 85, 105, 0.3) !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    font-size: 12px !important;
    color: #94a3b8 !important;
    transition: all 0.15s ease !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(30, 41, 59, 0.5) !important;
    border-color: rgba(71, 85, 105, 0.5) !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background: rgba(59, 130, 246, 0.15) !important;
    border-color: rgba(59, 130, 246, 0.5) !important;
    color: #e2e8f0 !important;
}

/* Date input */
section[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(71, 85, 105, 0.4) !important;
    border-radius: 8px !important;
}

/* Divider */
section[data-testid="stSidebar"] hr {
    border-color: rgba(71, 85, 105, 0.3) !important;
    margin: 20px 0 !important;
}

/* Section labels in sidebar */
.sidebar-section-label {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(71, 85, 105, 0.4) 0%, transparent 100%);
}

.sidebar-input-label {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 500;
    color: #94a3b8;
    margin-bottom: 6px;
    display: block;
}

.sidebar-hint {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    color: #475569;
    margin-top: 4px;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

p, span, label, div, td, th {
    font-family: 'Inter', sans-serif;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    padding: 12px 32px;
    color: var(--text-secondary);
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 14px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1a2028 0%, #151b23 100%) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

/* Cards */
.metric-card {
    background: linear-gradient(145deg, #151b23 0%, #12171d 100%);
    border: 1px solid #2a3441;
    border-radius: 12px;
    padding: 20px 24px;
    transition: all 0.2s ease;
}

.metric-card:hover {
    border-color: #3d4a5c;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.metric-label {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.metric-value {
    color: #f0f4f8;
    font-size: 28px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
}

.metric-delta {
    font-size: 12px;
    font-weight: 500;
    margin-top: 4px;
}

.delta-positive { color: #22c55e; }
.delta-negative { color: #ef4444; }

/* Section headers */
.section-title {
    color: #f0f4f8;
    font-size: 18px;
    font-weight: 600;
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #2a3441;
}

.section-subtitle {
    color: #64748b;
    font-size: 13px;
    margin-top: -12px;
    margin-bottom: 16px;
}

/* Chart containers */
.chart-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

.chart-title {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Clickable sparkline */
.sparkline-btn {
    cursor: pointer;
    padding: 4px;
    border-radius: 6px;
    transition: all 0.15s ease;
    display: inline-block;
}

.sparkline-btn:hover {
    background: rgba(59, 130, 246, 0.15);
    transform: scale(1.05);
}

/* Metrics table */
.metrics-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    background: var(--bg-card);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
}

.metrics-table th {
    background: linear-gradient(135deg, #1a2028 0%, #151b23 100%);
    color: var(--text-primary);
    font-weight: 600;
    padding: 14px 16px;
    text-align: left;
    border-bottom: 2px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 10;
}

.metrics-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #1e2530;
    color: var(--text-primary);
    vertical-align: middle;
}

.metrics-table tr:hover td {
    background: rgba(59, 130, 246, 0.05);
}

.metrics-table .section-row td {
    background: linear-gradient(90deg, #1a2028 0%, transparent 100%);
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 10px 16px;
}

.val-positive { color: #22c55e; }
.val-negative { color: #ef4444; }
.val-neutral { color: #f0f4f8; }
.val-muted { color: #64748b; }

/* Modal/Popup styling */
.chart-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.chart-modal-content {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    max-width: 90%;
    max-height: 90%;
    overflow: auto;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Selectbox/Multiselect */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3d4a5c; }

/* ═══════════════════════════════════════════════════════════════
   Institutional overlays (manager-ready)
   ═══════════════════════════════════════════════════════════════ */
.confidential-banner {
    position: fixed;
    top: 12px;
    right: 24px;
    z-index: 9999;
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(240,244,248,0.78);
    background: linear-gradient(135deg, rgba(30,41,59,0.45), rgba(15,23,42,0.45));
    border: 1px solid rgba(71,85,105,0.45);
    padding: 6px 10px;
    border-radius: 6px;
    backdrop-filter: blur(8px);
}
.version-tag {
    position: fixed;
    top: 14px;
    left: 28px;
    z-index: 9999;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    color: rgba(148,163,184,0.82);
}
.scitech-watermark {
    position: fixed;
    bottom: 28px;
    right: 32px;
    z-index: 0;
    pointer-events: none;
    user-select: none;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 0.28em;
    color: rgba(148,163,184,0.06);
}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# YAHOO FINANCE DATA FETCHER
# ═══════════════════════════════════════════════════════════════════════════════

BENCHMARK_TICKERS = {
    "S&P 500": "^GSPC",
    "S&P 500 Total Return": "^SP500TR",
    "Nasdaq 100": "^NDX",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
    "MSCI World": "URTH",
    "MSCI EM": "EEM",
    "Gold": "GLD",
    "Treasury 10Y": "TLT",
    "Treasury 20Y+": "TLT",
    "High Yield Bonds": "HYG",
    "US Dollar Index": "UUP",
    "Bitcoin": "BTC-USD",
    "60/40 Portfolio": "AOR",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_yahoo_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch data from Yahoo Finance using yfinance"""
    try:
        import yfinance as yf
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return None
        # Handle multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data[['Close']].rename(columns={'Close': ticker})
    except Exception as e:
        st.warning(f"Could not fetch {ticker}: {e}")
        return None


def resample_to_quarterly(df: pd.DataFrame, date_col: str = None) -> pd.DataFrame:
    """Resample daily/monthly data to quarterly (end of quarter)"""
    if date_col:
        df = df.set_index(date_col)
    return df.resample('QE').last()


# ═══════════════════════════════════════════════════════════════════════════════
# SPARKLINE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def sparkline_svg(data: list, width: int = 120, height: int = 32, 
                  line_color: str = None, show_endpoint: bool = True) -> str:
    """Generate SVG sparkline with automatic color based on trend"""
    if not data or len(data) < 2:
        return ""
    
    data = [float(x) if pd.notna(x) else 0 for x in data]
    min_val, max_val = min(data), max(data)
    range_val = max_val - min_val if max_val != min_val else 1
    
    # Auto color
    if line_color is None:
        line_color = COLORS['green'] if data[-1] >= data[0] else COLORS['red']
    
    fill_color = line_color.replace(')', ', 0.15)').replace('rgb', 'rgba') if 'rgb' in line_color else f"{line_color}20"
    
    points = []
    for i, val in enumerate(data):
        x = (i / (len(data) - 1)) * width
        y = height - 4 - ((val - min_val) / range_val) * (height - 8)
        points.append(f"{x:.1f},{y:.1f}")
    
    path_d = "M " + " L ".join(points)
    fill_path = f"M 0,{height} L " + " L ".join(points) + f" L {width},{height} Z"
    
    endpoint = ""
    if show_endpoint:
        last_x, last_y = points[-1].split(',')
        endpoint = f'<circle cx="{last_x}" cy="{last_y}" r="3" fill="{line_color}"/>'
    
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <defs>
            <linearGradient id="grad_{id(data)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{line_color};stop-opacity:0.3"/>
                <stop offset="100%" style="stop-color:{line_color};stop-opacity:0"/>
            </linearGradient>
        </defs>
        <path d="{fill_path}" fill="url(#grad_{id(data)})"/>
        <path d="{path_d}" fill="none" stroke="{line_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        {endpoint}
    </svg>'''


def bar_sparkline_svg(data: list, width: int = 120, height: int = 32) -> str:
    """Generate bar sparkline for returns"""
    if not data or len(data) < 1:
        return ""
    
    data = [float(x) if pd.notna(x) else 0 for x in data]
    n = len(data)
    bar_w = max(4, (width - n * 2) / n)
    gap = 2
    
    max_abs = max(abs(min(data)), abs(max(data))) if data else 1
    if max_abs == 0: max_abs = 1
    
    mid_y = height / 2
    bars = []
    
    for i, val in enumerate(data):
        x = i * (bar_w + gap)
        bar_h = abs(val) / max_abs * (height / 2 - 2)
        color = COLORS['green'] if val >= 0 else COLORS['red']
        y = mid_y - bar_h if val >= 0 else mid_y
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(1, bar_h):.1f}" fill="{color}" rx="1.5"/>')
    
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <line x1="0" y1="{mid_y}" x2="{width}" y2="{mid_y}" stroke="{COLORS['border']}" stroke-width="1" stroke-dasharray="2,2"/>
        {"".join(bars)}
    </svg>'''


def drawdown_sparkline_svg(data: list, width: int = 120, height: int = 32) -> str:
    """Generate drawdown underwater chart"""
    if not data or len(data) < 2:
        return ""
    
    data = [float(x) if pd.notna(x) else 0 for x in data]
    min_val = min(data)
    if min_val >= 0:
        return ""
    
    points = []
    for i, val in enumerate(data):
        x = (i / (len(data) - 1)) * width
        y = 2 + (-val / -min_val) * (height - 4) if min_val != 0 else 2
        points.append(f"{x:.1f},{y:.1f}")
    
    path_d = "M " + " L ".join(points)
    fill_path = f"M 0,2 L " + " L ".join(points) + f" L {width},2 Z"
    
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <path d="{fill_path}" fill="{COLORS['red']}25"/>
        <path d="{path_d}" fill="none" stroke="{COLORS['red']}" stroke-width="1.5" stroke-linecap="round"/>
    </svg>'''


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS CALCULATIONS (VERIFIED)
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_cagr(nav_series: pd.Series) -> float:
    """Compound Annual Growth Rate"""
    nav = nav_series.dropna()
    if len(nav) < 2:
        return np.nan
    
    years = len(nav) / 4  # Quarterly data
    if years <= 0:
        return np.nan
    
    total_return = nav.iloc[-1] / nav.iloc[0]
    if total_return <= 0:
        return np.nan
    
    return (total_return ** (1 / years) - 1) * 100


def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """Annualized volatility from quarterly returns"""
    if len(returns) < 2:
        return np.nan
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(4)  # Quarterly to annual
    return vol * 100


def calculate_downside_volatility(returns: pd.Series, threshold: float = 0, annualize: bool = True) -> float:
    """Downside deviation (semi-deviation below threshold)"""
    downside = returns[returns < threshold]
    if len(downside) < 2:
        return 0
    # Standard deviation of downside returns
    vol = downside.std()
    if annualize:
        vol *= np.sqrt(4)  # Quarterly to annual
    return vol * 100


def calculate_max_drawdown(nav_series: pd.Series) -> tuple:
    """Maximum drawdown and related stats"""
    nav = nav_series.dropna()
    if len(nav) < 2:
        return np.nan, None, None
    
    rolling_max = nav.cummax()
    drawdown = (nav - rolling_max) / rolling_max
    max_dd = drawdown.min()
    max_dd_idx = drawdown.idxmin()
    
    # Find peak before max drawdown
    peak_idx = nav[:max_dd_idx].idxmax() if max_dd_idx else None
    
    return max_dd * 100, peak_idx, max_dd_idx


def calculate_sharpe(returns: pd.Series, rf: float = 0) -> float:
    """Sharpe Ratio (annualized from quarterly returns)"""
    if len(returns) < 2 or returns.std() == 0:
        return np.nan
    
    excess_return = returns.mean() - rf / 4  # Quarterly rf
    return (excess_return / returns.std()) * np.sqrt(4)


def calculate_sortino(returns: pd.Series, rf: float = 0, threshold: float = 0) -> float:
    """Sortino Ratio = Annualized Return / Downside Volatility"""
    if len(returns) < 2:
        return np.nan
    
    # Annualized excess return
    excess_return = (returns.mean() - rf / 4) * 4
    
    # Downside volatility (std of negative returns, annualized)
    downside = returns[returns < threshold]
    
    if len(downside) < 2:
        return np.nan
    
    downside_vol = downside.std() * np.sqrt(4)  # Annualized
    
    if downside_vol == 0:
        return np.nan
    
    return excess_return / downside_vol


def calculate_calmar(cagr: float, max_dd: float) -> float:
    """Calmar Ratio = CAGR / |Max Drawdown|"""
    if pd.isna(max_dd) or max_dd == 0:
        return np.nan
    return cagr / abs(max_dd)


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Value at Risk (historical method)"""
    if len(returns) < 10:
        return np.nan
    return np.percentile(returns, (1 - confidence) * 100) * 100


def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Conditional VaR (Expected Shortfall)"""
    if len(returns) < 10:
        return np.nan
    var = np.percentile(returns, (1 - confidence) * 100)
    return returns[returns <= var].mean() * 100


def calculate_ulcer_index(nav_series: pd.Series) -> float:
    """Ulcer Index - measures depth and duration of drawdowns"""
    nav = nav_series.dropna()
    if len(nav) < 2:
        return np.nan
    
    rolling_max = nav.cummax()
    drawdown = (nav - rolling_max) / rolling_max
    return np.sqrt(np.mean(drawdown ** 2)) * 100


def calculate_profit_factor(returns: pd.Series) -> float:
    """Profit Factor = Sum of gains / Sum of losses"""
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    if losses == 0:
        return np.nan
    return gains / losses


def calculate_beta(port_returns: pd.Series, bench_returns: pd.Series) -> float:
    """Beta = Cov(port, bench) / Var(bench)"""
    aligned = pd.concat([port_returns, bench_returns], axis=1).dropna()
    if len(aligned) < 10:
        return np.nan
    
    cov_matrix = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])
    var_bench = np.var(aligned.iloc[:, 1], ddof=1)
    
    if var_bench == 0:
        return np.nan
    
    return cov_matrix[0, 1] / var_bench


def calculate_alpha(port_returns: pd.Series, bench_returns: pd.Series, rf: float = 0) -> float:
    """Jensen's Alpha (annualized)"""
    aligned = pd.concat([port_returns, bench_returns], axis=1).dropna()
    if len(aligned) < 10:
        return np.nan
    
    beta = calculate_beta(port_returns, bench_returns)
    if pd.isna(beta):
        return np.nan
    
    port_annual = aligned.iloc[:, 0].mean() * 4
    bench_annual = aligned.iloc[:, 1].mean() * 4
    
    alpha = port_annual - (rf + beta * (bench_annual - rf))
    return alpha * 100


def calculate_correlation(series1: pd.Series, series2: pd.Series) -> float:
    """Pearson correlation coefficient"""
    aligned = pd.concat([series1, series2], axis=1).dropna()
    if len(aligned) < 10:
        return np.nan
    return aligned.iloc[:, 0].corr(aligned.iloc[:, 1])


def calculate_information_ratio(port_returns: pd.Series, bench_returns: pd.Series) -> float:
    """Information Ratio = (port_ret - bench_ret) / tracking_error"""
    aligned = pd.concat([port_returns, bench_returns], axis=1).dropna()
    if len(aligned) < 10:
        return np.nan
    
    active_returns = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    tracking_error = active_returns.std() * np.sqrt(4)  # Annualized
    
    if tracking_error == 0:
        return np.nan
    
    return (active_returns.mean() * 4) / tracking_error


# ═══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE METRICS CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_all_metrics(nav_df: pd.DataFrame, benchmark_nav: pd.DataFrame = None) -> dict:
    """Calculate all metrics for portfolio and optionally vs benchmark"""
    
    date_col = nav_df.columns[0]
    port_col = nav_df.columns[1]  # GROWISE portfolio
    
    df = nav_df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    
    nav = df[port_col].dropna()
    returns = nav.pct_change().dropna()
    
    # Calculate drawdown series
    rolling_max = nav.cummax()
    drawdown = (nav - rolling_max) / rolling_max
    
    # Yearly returns (compound)
    yearly_returns = returns.groupby(returns.index.year).apply(lambda x: (1 + x).prod() - 1)
    
    # YTD Return - compound return for current year
    current_year = nav.index[-1].year if len(nav) > 0 else datetime.now().year
    ytd_returns = returns[returns.index.year == current_year]
    ytd_return = ((1 + ytd_returns).prod() - 1) * 100 if len(ytd_returns) > 0 else np.nan
    
    # Core metrics
    cagr = calculate_cagr(nav)
    max_dd, peak_date, trough_date = calculate_max_drawdown(nav)
    
    metrics = {
        # Performance
        "CAGR": cagr,
        "Mean Return (Annual)": returns.mean() * 4 * 100,
        "YTD Return": ytd_return,
        "Last Quarter": returns.iloc[-1] * 100 if len(returns) > 0 else np.nan,
        "Last Year": yearly_returns.iloc[-1] * 100 if len(yearly_returns) > 0 else np.nan,
        "Profit Factor": calculate_profit_factor(returns),
        
        # Risk
        "Volatility (Annual)": calculate_volatility(returns),
        "Downside Volatility": calculate_downside_volatility(returns),
        "Max Drawdown": max_dd,
        
        # Risk-Adjusted
        "Sharpe Ratio": calculate_sharpe(returns),
        "Sortino Ratio": calculate_sortino(returns),
        "Calmar Ratio": calculate_calmar(cagr, max_dd),
        
        # Tail Risk
        "VaR (95%)": calculate_var(returns),
        "CVaR (95%)": calculate_cvar(returns),
        "Ulcer Index": calculate_ulcer_index(nav),
        
        # Distribution
        "Skewness": returns.skew(),
        "Kurtosis": returns.kurtosis(),
        "Best Quarter": returns.max() * 100,
        "Worst Quarter": returns.min() * 100,
        "Best Year": yearly_returns.max() * 100 if len(yearly_returns) > 0 else np.nan,
        "Worst Year": yearly_returns.min() * 100 if len(yearly_returns) > 0 else np.nan,
        
        # Period Stats
        "Positive Quarters": (returns > 0).sum(),
        "Negative Quarters": (returns < 0).sum(),
        "Win Rate": (returns > 0).mean() * 100,
        "Positive Years": (yearly_returns > 0).sum() if len(yearly_returns) > 0 else 0,
        "Negative Years": (yearly_returns < 0).sum() if len(yearly_returns) > 0 else 0,
        
        # Time metrics
        "Last 3Y CAGR": calculate_cagr(nav.tail(13)) if len(nav) > 12 else np.nan,
        "Last 5Y CAGR": calculate_cagr(nav.tail(21)) if len(nav) > 20 else np.nan,
        "Last 10Y CAGR": calculate_cagr(nav.tail(41)) if len(nav) > 40 else np.nan,
    }
    
    # Sparkline data
    sparkline_data = {
        "nav": nav.tolist(),
        "returns": (returns * 100).tolist(),
        "drawdown": (drawdown * 100).tolist(),
        "yearly": (yearly_returns * 100).tolist() if len(yearly_returns) > 0 else [],
    }
    
    # Benchmark comparison if available
    benchmark_metrics = {}
    benchmark_own_metrics = {}  # Benchmark's own performance metrics
    
    if benchmark_nav is not None and len(benchmark_nav.columns) > 1:
        bench_col = benchmark_nav.columns[1]
        bench_df = benchmark_nav.set_index(benchmark_nav.columns[0]).sort_index()
        bench_nav_series = bench_df[bench_col].dropna()
        bench_returns = bench_nav_series.pct_change().dropna()
        
        # Calculate benchmark's own metrics (for table display)
        bench_yearly = bench_returns.groupby(bench_returns.index.year).apply(lambda x: (1 + x).prod() - 1)
        bench_current_year = bench_nav_series.index[-1].year if len(bench_nav_series) > 0 else current_year
        bench_ytd_returns = bench_returns[bench_returns.index.year == bench_current_year]
        bench_ytd = ((1 + bench_ytd_returns).prod() - 1) * 100 if len(bench_ytd_returns) > 0 else np.nan
        bench_max_dd, _, _ = calculate_max_drawdown(bench_nav_series)
        
        benchmark_own_metrics = {
            "CAGR": calculate_cagr(bench_nav_series),
            "Mean Return (Annual)": bench_returns.mean() * 4 * 100,
            "YTD Return": bench_ytd,
            "Last Quarter": bench_returns.iloc[-1] * 100 if len(bench_returns) > 0 else np.nan,
            "Last Year": bench_yearly.iloc[-1] * 100 if len(bench_yearly) > 0 else np.nan,
            "Profit Factor": calculate_profit_factor(bench_returns),
            "Volatility (Annual)": calculate_volatility(bench_returns),
            "Downside Volatility": calculate_downside_volatility(bench_returns),
            "Max Drawdown": bench_max_dd,
            "Sharpe Ratio": calculate_sharpe(bench_returns),
            "Sortino Ratio": calculate_sortino(bench_returns),
            "Calmar Ratio": calculate_calmar(calculate_cagr(bench_nav_series), bench_max_dd),
            "VaR (95%)": calculate_var(bench_returns),
            "CVaR (95%)": calculate_cvar(bench_returns),
            "Ulcer Index": calculate_ulcer_index(bench_nav_series),
            "Skewness": bench_returns.skew(),
            "Kurtosis": bench_returns.kurtosis(),
            "Best Quarter": bench_returns.max() * 100,
            "Worst Quarter": bench_returns.min() * 100,
            "Best Year": bench_yearly.max() * 100 if len(bench_yearly) > 0 else np.nan,
            "Worst Year": bench_yearly.min() * 100 if len(bench_yearly) > 0 else np.nan,
            "Positive Quarters": (bench_returns > 0).sum(),
            "Negative Quarters": (bench_returns < 0).sum(),
            "Win Rate": (bench_returns > 0).mean() * 100,
            "Positive Years": (bench_yearly > 0).sum() if len(bench_yearly) > 0 else 0,
            "Negative Years": (bench_yearly < 0).sum() if len(bench_yearly) > 0 else 0,
            "Last 3Y CAGR": calculate_cagr(bench_nav_series.tail(13)) if len(bench_nav_series) > 12 else np.nan,
            "Last 5Y CAGR": calculate_cagr(bench_nav_series.tail(21)) if len(bench_nav_series) > 20 else np.nan,
            "Last 10Y CAGR": calculate_cagr(bench_nav_series.tail(41)) if len(bench_nav_series) > 40 else np.nan,
        }
        
        # Align returns for comparison metrics
        aligned = pd.concat([returns, bench_returns], axis=1).dropna()
        if len(aligned) >= 10:
            port_ret = aligned.iloc[:, 0]
            bench_ret = aligned.iloc[:, 1]
            
            benchmark_metrics = {
                "Beta": calculate_beta(port_ret, bench_ret),
                "Alpha (Annual)": calculate_alpha(port_ret, bench_ret),
                "Correlation": calculate_correlation(port_ret, bench_ret),
                "Information Ratio": calculate_information_ratio(port_ret, bench_ret),
                "Tracking Error": (port_ret - bench_ret).std() * np.sqrt(4) * 100,
                "Up Capture": (port_ret[bench_ret > 0].mean() / bench_ret[bench_ret > 0].mean() * 100) if (bench_ret > 0).any() else np.nan,
                "Down Capture": (port_ret[bench_ret < 0].mean() / bench_ret[bench_ret < 0].mean() * 100) if (bench_ret < 0).any() else np.nan,
            }
        
        sparkline_data["benchmark_nav"] = bench_nav_series.tolist()
        sparkline_data["benchmark_returns"] = (bench_returns * 100).tolist()
        sparkline_data["benchmark_own_metrics"] = benchmark_own_metrics
    
    return metrics, benchmark_metrics, sparkline_data


# ═══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_excel(file_bytes: bytes, sheet_name=0) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)


@st.cache_data(show_spinner=False)
def process_trades(raw: pd.DataFrame):
    df = raw.copy()
    
    if "Date/Time" not in df.columns:
        for alt in ["Date", "Datetime", "Timestamp"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "Date/Time"})
                break
    
    df["Date/Time"] = pd.to_datetime(df["Date/Time"], errors="coerce")
    
    required = ["Date/Time", "Symbol", "Quantity", "Realized P/L", "Basis", "Code"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, f"Missing columns: {', '.join(missing)}"
    
    df = df.dropna(subset=["Date/Time", "Symbol", "Quantity"]).copy()
    df["is_close"] = df["Code"].astype(str).str.contains("C", na=False)
    df = df[df["is_close"]].copy()
    
    if df.empty:
        return None, "No closing trades found"
    
    basis_abs = df["Basis"].abs().replace(0, np.nan)
    df["trade_return_pct"] = df["Realized P/L"] / basis_abs
    df["side"] = np.where(df["Quantity"] < 0, "Long", "Short")
    df["win"] = df["Realized P/L"] > 0
    df["date"] = df["Date/Time"].dt.date
    
    return df, None


def compute_trade_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {k: np.nan for k in ["sqn", "pf", "avg_mo", "win_avg", "loss_avg", "n", "win_n", "loss_n", "win_rate"]}
    
    N = len(df)
    win_sum = df.loc[df["win"], "Realized P/L"].sum()
    loss_sum = df.loc[~df["win"], "Realized P/L"].sum()
    loss_abs = abs(loss_sum)
    
    pf = win_sum / loss_abs if loss_abs > 0 else np.nan
    win_avg = df.loc[df["win"], "trade_return_pct"].mean() * 100 if df["win"].any() else 0
    loss_avg = df.loc[~df["win"], "trade_return_pct"].mean() * 100 if (~df["win"]).any() else 0
    
    try:
        avg_mo = df.set_index("Date/Time").resample("ME").size().mean()
    except:
        days = (df["Date/Time"].max() - df["Date/Time"].min()).days
        avg_mo = N / max(1, days / 30)
    
    tr = df["trade_return_pct"].dropna()
    sqn = (tr.mean() / tr.std() * np.sqrt(N)) if len(tr) > 1 and tr.std() > 0 else np.nan
    
    win_n = int(df["win"].sum())
    loss_n = int((~df["win"]).sum())
    
    return {
        "sqn": sqn, "pf": pf, "avg_mo": avg_mo,
        "win_avg": win_avg, "loss_avg": loss_avg,
        "n": N, "win_n": win_n, "loss_n": loss_n,
        "win_rate": win_n / N * 100 if N > 0 else 0,
        "total_pnl": df["Realized P/L"].sum(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

CHART_LAYOUT = dict(
    paper_bgcolor=COLORS['bg_secondary'],
    plot_bgcolor=COLORS['bg_primary'],
    font=dict(family='Inter, sans-serif', color=COLORS['text_primary'], size=12),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(gridcolor=COLORS['bg_tertiary'], linecolor=COLORS['border'], zerolinecolor=COLORS['bg_tertiary'], showgrid=True),
    yaxis=dict(gridcolor=COLORS['bg_tertiary'], linecolor=COLORS['border'], zerolinecolor=COLORS['bg_tertiary'], showgrid=True),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['text_secondary'], size=11)),
    hoverlabel=dict(bgcolor=COLORS['bg_card'], font=dict(color=COLORS['text_primary'], size=12), bordercolor=COLORS['border']),
    hovermode='x unified',
)


def create_equity_chart(nav_df: pd.DataFrame, benchmark_df: pd.DataFrame = None, 
                        show_dd: bool = True) -> go.Figure:
    """Professional equity curve with optional benchmark overlay - ALWAYS semi-log scale"""
    
    date_col = nav_df.columns[0]
    port_col = nav_df.columns[1]
    
    df = nav_df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Normalize to 100
    df[port_col] = df[port_col] / df[port_col].iloc[0] * 100
    
    if show_dd:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                           row_heights=[0.72, 0.28], subplot_titles=("", "Drawdown"))
    else:
        fig = go.Figure()
    
    row = 1 if show_dd else None
    col = 1 if show_dd else None
    
    # Portfolio line
    fig.add_trace(go.Scatter(
        x=df[date_col], y=df[port_col],
        mode='lines', name='GROWISE',
        line=dict(color=COLORS['green'], width=2.5),
        fill='tozeroy' if not show_dd else None,
        fillcolor='rgba(34, 197, 94, 0.1)',
    ), row=row, col=col)
    
    # Benchmark if available
    if benchmark_df is not None and len(benchmark_df.columns) > 1:
        bench_date = benchmark_df.columns[0]
        bench_col = benchmark_df.columns[1]
        bench = benchmark_df.copy()
        bench[bench_date] = pd.to_datetime(bench[bench_date])
        bench[bench_col] = bench[bench_col] / bench[bench_col].iloc[0] * 100
        
        fig.add_trace(go.Scatter(
            x=bench[bench_date], y=bench[bench_col],
            mode='lines', name=bench_col,
            line=dict(color=COLORS['blue'], width=2, dash='dot'),
        ), row=row, col=col)
    
    # Drawdown
    if show_dd:
        nav = df[port_col]
        rolling_max = nav.cummax()
        dd = (nav - rolling_max) / rolling_max * 100
        
        fig.add_trace(go.Scatter(
            x=df[date_col], y=dd,
            mode='lines', name='Drawdown',
            line=dict(color=COLORS['red'], width=1.5),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.15)',
            showlegend=False,
        ), row=2, col=1)
        
        fig.update_yaxes(title_text="NAV (Log)", type="log", row=1, col=1)
        fig.update_yaxes(title_text="DD %", row=2, col=1)
        
        for i in range(1, 3):
            fig.update_xaxes(gridcolor=COLORS['bg_tertiary'], row=i, col=1)
            fig.update_yaxes(gridcolor=COLORS['bg_tertiary'], row=i, col=1)
    else:
        fig.update_yaxes(title_text="NAV (Log)", type="log")
    
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        height=480 if show_dd else 380,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        title=dict(text="", font=dict(size=14)),
    )
    
    return fig


def create_returns_heatmap(nav_df: pd.DataFrame) -> go.Figure:
    """Quarterly returns heatmap by year"""
    date_col = nav_df.columns[0]
    port_col = nav_df.columns[1]
    
    df = nav_df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    returns = df[port_col].pct_change().dropna() * 100
    returns_df = returns.to_frame('return')
    returns_df['year'] = returns_df.index.year
    returns_df['quarter'] = 'Q' + returns_df.index.quarter.astype(str)
    
    pivot = returns_df.pivot_table(values='return', index='year', columns='quarter', aggfunc='sum')
    pivot = pivot.reindex(columns=['Q1', 'Q2', 'Q3', 'Q4'])
    pivot['Year'] = pivot.sum(axis=1)
    
    # Custom colorscale
    colorscale = [
        [0.0, COLORS['red']],
        [0.35, COLORS['red_light']],
        [0.5, COLORS['bg_tertiary']],
        [0.65, COLORS['green_light']],
        [1.0, COLORS['green']],
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=colorscale,
        zmid=0,
        text=[[f"{v:.1f}%" if pd.notna(v) else "" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont={"size": 11, "color": COLORS['text_primary']},
        hovertemplate="Year: %{y}<br>Period: %{x}<br>Return: %{z:.2f}%<extra></extra>",
        showscale=False,
    ))
    
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        height=max(280, len(pivot) * 32 + 80),
        xaxis=dict(side='top', tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11), autorange='reversed'),
        margin=dict(l=50, r=20, t=40, b=20),
    )
    
    return fig


def create_rolling_metrics_chart(nav_df: pd.DataFrame, benchmark_df: pd.DataFrame = None) -> go.Figure:
    """Rolling Sharpe, Beta, Correlation"""
    date_col = nav_df.columns[0]
    port_col = nav_df.columns[1]
    
    df = nav_df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    returns = df[port_col].pct_change().dropna()
    
    # Rolling Sharpe (12-quarter window)
    window = 12
    rolling_sharpe = returns.rolling(window).apply(
        lambda x: (x.mean() / x.std() * np.sqrt(4)) if x.std() > 0 else np.nan
    )
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                       subplot_titles=("Rolling Sharpe (3Y)", "Rolling Volatility (3Y)"))
    
    fig.add_trace(go.Scatter(
        x=rolling_sharpe.index, y=rolling_sharpe,
        mode='lines', name='Sharpe',
        line=dict(color=COLORS['blue'], width=2),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
    ), row=1, col=1)
    
    # Add reference line at 1.0
    fig.add_hline(y=1.0, line_dash="dash", line_color=COLORS['text_muted'], row=1, col=1)
    
    # Rolling volatility
    rolling_vol = returns.rolling(window).std() * np.sqrt(4) * 100
    
    fig.add_trace(go.Scatter(
        x=rolling_vol.index, y=rolling_vol,
        mode='lines', name='Volatility',
        line=dict(color=COLORS['gold'], width=2),
        fill='tozeroy',
        fillcolor='rgba(245, 158, 11, 0.1)',
    ), row=2, col=1)
    
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(height=380, showlegend=False)
    
    for i in range(1, 3):
        fig.update_xaxes(gridcolor=COLORS['bg_tertiary'], row=i, col=1)
        fig.update_yaxes(gridcolor=COLORS['bg_tertiary'], row=i, col=1)
    
    return fig


def create_distribution_chart(nav_df: pd.DataFrame) -> go.Figure:
    """Return distribution histogram with normal overlay"""
    date_col = nav_df.columns[0]
    port_col = nav_df.columns[1]
    
    df = nav_df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    returns = df[port_col].pct_change().dropna() * 100
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=20,
        marker_color=COLORS['blue'],
        opacity=0.7,
        name='Returns',
    ))
    
    # Normal distribution overlay
    x_range = np.linspace(returns.min(), returns.max(), 100)
    y_normal = stats.norm.pdf(x_range, returns.mean(), returns.std()) * len(returns) * (returns.max() - returns.min()) / 20
    
    fig.add_trace(go.Scatter(
        x=x_range, y=y_normal,
        mode='lines', name='Normal',
        line=dict(color=COLORS['gold'], width=2, dash='dash'),
    ))
    
    # Add vertical lines for mean and zero
    fig.add_vline(x=0, line_dash="solid", line_color=COLORS['text_muted'], line_width=1)
    fig.add_vline(x=returns.mean(), line_dash="dash", line_color=COLORS['green'], line_width=2)
    
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        height=300,
        xaxis_title="Quarterly Return (%)",
        yaxis_title="Frequency",
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    
    return fig


def create_attribution_treemap(trades_df: pd.DataFrame) -> go.Figure:
    """Treemap showing PnL attribution by symbol - ALL PERCENTAGES"""
    g = trades_df.groupby("Symbol").agg(
        pnl=("Realized P/L", "sum"),
        count=("Symbol", "size"),
        avg_ret=("trade_return_pct", "mean"),
    ).reset_index()
    
    total_abs_pnl = g["pnl"].abs().sum()
    g = g[g["pnl"] != 0].copy()
    g["abs_pnl"] = g["pnl"].abs()
    g["pct_contribution"] = g["pnl"] / total_abs_pnl * 100 if total_abs_pnl != 0 else 0
    g["color"] = g["pnl"].apply(lambda x: COLORS['green'] if x > 0 else COLORS['red'])
    g["avg_ret_pct"] = g["avg_ret"] * 100
    g["text"] = g.apply(lambda r: f"{r['Symbol']}<br>{r['pct_contribution']:+.1f}%<br>{r['count']} trades", axis=1)
    
    fig = go.Figure(go.Treemap(
        labels=g["Symbol"],
        parents=[""] * len(g),
        values=g["abs_pnl"],
        text=g["text"],
        textinfo="text",
        marker=dict(
            colors=g["color"],
            line=dict(color=COLORS['bg_primary'], width=2),
        ),
        hovertemplate="<b>%{label}</b><br>Contribution: %{customdata:.1f}%<extra></extra>",
        customdata=g["pct_contribution"],
    ))
    
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    
    return fig


def create_trades_equity_curve(trades: pd.DataFrame) -> go.Figure:
    """Equity curve from trades - shows cumulative % return"""
    t = trades.sort_values("Date/Time").copy()
    
    # Cumulative return in percentage terms
    t["cum_ret_pct"] = (1 + t["trade_return_pct"]).cumprod() * 100 - 100  # Start at 0%
    t["peak"] = t["cum_ret_pct"].cummax()
    t["dd_pct"] = t["cum_ret_pct"] - t["peak"]
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                       row_heights=[0.72, 0.28])
    
    fig.add_trace(go.Scatter(
        x=t["Date/Time"], y=t["cum_ret_pct"],
        mode='lines', name='Cumulative Return',
        line=dict(color=COLORS['green'], width=2.5),
        fill='tozeroy', fillcolor='rgba(34, 197, 94, 0.1)',
        hovertemplate="%{y:+.1f}%<extra></extra>",
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=t["Date/Time"], y=t["dd_pct"],
        mode='lines', name='Drawdown',
        line=dict(color=COLORS['red'], width=1.5),
        fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.15)',
        showlegend=False,
        hovertemplate="%{y:.1f}%<extra></extra>",
    ), row=2, col=1)
    
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(height=420, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    fig.update_yaxes(title_text="Cumulative P/L ($)", row=1, col=1)
    fig.update_yaxes(title_text="DD %", row=2, col=1)
    
    for i in range(1, 3):
        fig.update_xaxes(gridcolor=COLORS['bg_tertiary'], row=i, col=1)
        fig.update_yaxes(gridcolor=COLORS['bg_tertiary'], row=i, col=1)
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_logo():
    st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.5) 100%);
            border: 1px solid rgba(71, 85, 105, 0.3);
            border-radius: 16px;
            padding: 32px 24px;
            margin-bottom: 28px;
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, transparent, {COLORS['blue']}, transparent);
                opacity: 0.5;
            "></div>
            <h1 style="
                font-family: 'Inter', sans-serif;
                font-weight: 700;
                font-size: 32px;
                color: {COLORS['text_primary']};
                margin: 0;
                letter-spacing: 0.12em;
                text-shadow: 0 2px 10px rgba(59, 130, 246, 0.2);
            ">SCITECH</h1>
            <p style="
                font-family: 'Inter', sans-serif;
                font-size: 10px;
                color: {COLORS['text_muted']};
                margin: 10px 0 0 0;
                letter-spacing: 0.3em;
                text-transform: uppercase;
            ">Investments</p>
        </div>
    """, unsafe_allow_html=True)


def sidebar_section(title: str, icon: str = ""):
    """Render a styled section header in sidebar"""
    st.markdown(f"""
        <div class="sidebar-section-label">
            {title}
        </div>
    """, unsafe_allow_html=True)


def sidebar_label(text: str, hint: str = None):
    """Render a styled input label in sidebar"""
    hint_html = f'<span class="sidebar-hint">{hint}</span>' if hint else ""
    st.markdown(f"""
        <span class="sidebar-input-label">{text}</span>
        {hint_html}
    """, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = None, delta_positive: bool = True):
    delta_html = ""
    if delta:
        delta_class = "delta-positive" if delta_positive else "delta-negative"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def section_title(title: str, subtitle: str = None):
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="section-title">{title}</div>{sub_html}', unsafe_allow_html=True)


def format_metric(val, metric_name: str) -> tuple:
    """Format metric value and determine color class"""
    if pd.isna(val):
        return "—", "val-muted"
    
    # Determine if higher is better
    negative_is_bad = not any(x in metric_name.lower() for x in 
                              ["drawdown", "volatility", "var", "cvar", "ulcer", "negative", "worst", "loss", "down capture"])
    
    is_pct = any(x in metric_name.lower() for x in 
                 ["cagr", "return", "volatility", "drawdown", "var", "cvar", "rate", "capture", "quarter", "year", "ytd"])
    is_ratio = any(x in metric_name.lower() for x in ["ratio", "factor", "beta", "alpha", "correlation", "skew", "kurt"])
    is_count = any(x in metric_name.lower() for x in ["positive quarters", "negative quarters", "positive years", "negative years"])
    
    # Format
    if is_count:
        formatted = str(int(val))
        css_class = "val-neutral"
    elif is_pct:
        formatted = f"{val:+.2f}%" if val != 0 else "0.00%"
        css_class = "val-positive" if (val > 0 and negative_is_bad) or (val < 0 and not negative_is_bad) else \
                   "val-negative" if (val < 0 and negative_is_bad) or (val > 0 and not negative_is_bad) else "val-neutral"
    elif is_ratio:
        formatted = f"{val:.2f}"
        if "beta" in metric_name.lower():
            css_class = "val-neutral"
        elif "correlation" in metric_name.lower():
            css_class = "val-positive" if val > 0.5 else "val-negative" if val < -0.5 else "val-neutral"
        else:
            css_class = "val-positive" if val > 1 else "val-negative" if val < 0 else "val-neutral"
    else:
        formatted = f"{val:.2f}"
        css_class = "val-neutral"
    
    return formatted, css_class


def build_metrics_table_html(metrics: dict, benchmark_metrics: dict, sparklines: dict, search: str = "", benchmark_name: str = "Benchmark") -> str:
    """Build HTML metrics table with sparklines and benchmark comparison"""
    
    # Get benchmark's own metrics from sparklines
    bench_own = sparklines.get("benchmark_own_metrics", {})
    has_benchmark = len(bench_own) > 0
    
    sections = {
        "Performance": ["CAGR", "Mean Return (Annual)", "YTD Return", "Last Quarter", "Last Year", "Profit Factor"],
        "Risk": ["Volatility (Annual)", "Downside Volatility", "Max Drawdown"],
        "Risk-Adjusted": ["Sharpe Ratio", "Sortino Ratio", "Calmar Ratio"],
        "Tail Risk": ["VaR (95%)", "CVaR (95%)", "Ulcer Index"],
        "Distribution": ["Skewness", "Kurtosis", "Best Quarter", "Worst Quarter", "Best Year", "Worst Year"],
        "Period Analysis": ["Positive Quarters", "Negative Quarters", "Win Rate", "Positive Years", "Negative Years"],
        "Historical": ["Last 3Y CAGR", "Last 5Y CAGR", "Last 10Y CAGR"],
    }
    
    # Add benchmarking section if available
    if benchmark_metrics:
        sections["vs Benchmark"] = list(benchmark_metrics.keys())
    
    rows = []
    colspan = "4" if has_benchmark else "3"
    
    for section_name, metric_list in sections.items():
        filtered = [m for m in metric_list if search.lower() in m.lower()] if search else metric_list
        if not filtered:
            continue
        
        rows.append(f'<tr class="section-row"><td colspan="{colspan}">{section_name}</td></tr>')
        
        for metric in filtered:
            # Get portfolio value
            if metric in metrics:
                val = metrics[metric]
            elif metric in benchmark_metrics:
                val = benchmark_metrics[metric]
            else:
                val = np.nan
            
            formatted, css_class = format_metric(val, metric)
            
            # Get benchmark value if available
            bench_formatted = ""
            bench_css = "val-neutral"
            if has_benchmark and metric in bench_own:
                bench_val = bench_own[metric]
                bench_formatted, bench_css = format_metric(bench_val, metric)
            elif metric in benchmark_metrics:
                # For "vs Benchmark" section metrics, don't show duplicate
                bench_formatted = "—"
                bench_css = "val-neutral"
            
            # Sparkline
            sparkline = ""
            if metric == "CAGR" and "nav" in sparklines:
                sparkline = sparkline_svg(sparklines["nav"], width=90, height=24)
            elif metric == "Max Drawdown" and "drawdown" in sparklines:
                sparkline = drawdown_sparkline_svg(sparklines["drawdown"], width=90, height=24)
            elif metric in ["Mean Return (Annual)", "YTD Return"] and "yearly" in sparklines:
                sparkline = bar_sparkline_svg(sparklines["yearly"][-12:], width=90, height=24)
            elif metric == "Volatility (Annual)" and "returns" in sparklines:
                rets = sparklines["returns"]
                if len(rets) > 8:
                    rolling = [np.std(rets[max(0,i-4):i+1]) if i >= 4 else np.nan for i in range(len(rets))]
                    sparkline = sparkline_svg([r for r in rolling if not pd.isna(r)], width=90, height=24, line_color=COLORS['gold'])
            
            sparkline_cell = f'<span class="sparkline-btn" title="Click to expand">{sparkline}</span>' if sparkline else ""
            
            if has_benchmark:
                rows.append(f'''<tr>
                    <td style="color: {COLORS['text_secondary']}; font-weight: 500;">{metric}</td>
                    <td><span class="{css_class}" style="font-family: 'JetBrains Mono', monospace; font-weight: 500;">{formatted}</span></td>
                    <td><span class="{bench_css}" style="font-family: 'JetBrains Mono', monospace; font-weight: 500;">{bench_formatted}</span></td>
                    <td style="width: 100px;">{sparkline_cell}</td>
                </tr>''')
            else:
                rows.append(f'''<tr>
                    <td style="color: {COLORS['text_secondary']}; font-weight: 500;">{metric}</td>
                    <td><span class="{css_class}" style="font-family: 'JetBrains Mono', monospace; font-weight: 500;">{formatted}</span></td>
                    <td style="width: 100px;">{sparkline_cell}</td>
                </tr>''')
    
    # Build header
    if has_benchmark:
        header = f'''<tr>
            <th style="width: 200px; text-align: left;">Metric</th>
            <th style="width: 120px; text-align: right;">Portfolio</th>
            <th style="width: 120px; text-align: right;">{benchmark_name}</th>
            <th style="width: 100px; text-align: center;"></th>
        </tr>'''
    else:
        header = f'''<tr>
            <th style="width: 200px; text-align: left;">Metric</th>
            <th style="width: 140px; text-align: right;">Value</th>
            <th style="width: 100px; text-align: center;"></th>
        </tr>'''
    
    return f'''
    <div style="overflow-x: auto; max-height: 650px; overflow-y: auto; border-radius: 12px; border: 1px solid {COLORS['border']};">
        <table class="metrics-table">
            <thead>{header}</thead>
            <tbody>{"".join(rows)}</tbody>
        </table>
    </div>
    '''


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Initialize session state for chart popups
    if 'show_chart_popup' not in st.session_state:
        st.session_state.show_chart_popup = None
    
    # Check for local data file
    import os
    LOCAL_DATA_FILE = os.path.join(os.path.dirname(__file__), "data.xlsx")
    local_data_exists = os.path.exists(LOCAL_DATA_FILE)
    
    # Sidebar
    with st.sidebar:
        render_logo()
        
        # Data Sources Section
        sidebar_section("Data Sources")
        
        if local_data_exists:
            sidebar_label("GROWISE NAV Series", "✓ Auto-loaded")
            st.markdown(f"""<div style="background: {COLORS['bg_tertiary']}; border: 1px solid {COLORS['border']}; 
                border-radius: 6px; padding: 8px 12px; font-size: 12px; color: {COLORS['text_muted']};">
                📁 data.xlsx</div>""", unsafe_allow_html=True)
            nav_file = None
        else:
            sidebar_label("GROWISE NAV Series", "Quarterly NAV data")
            nav_file = st.file_uploader("nav", type=["xlsx"], key="nav", label_visibility="collapsed")
        
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        
        sidebar_label("Trades Export", "IBKR format")
        trades_file = st.file_uploader("trades", type=["xlsx"], key="trades", label_visibility="collapsed")
        
        st.markdown("---")
        
        # Benchmark Section
        sidebar_section("Benchmark")
        
        sidebar_label("Compare Against")
        selected_benchmark = st.selectbox(
            "benchmark",
            options=list(BENCHMARK_TICKERS.keys()),
            index=0,
            label_visibility="collapsed"
        )
        
        use_benchmark = st.checkbox("Enable benchmark overlay", value=True)
        
        st.markdown("---")
        
        # Display Settings Section
        sidebar_section("Display")
        
        show_dd = st.checkbox("Show drawdown panel", value=True)
        
        st.markdown("---")
        
        # Export Section
        sidebar_section("Export")
        
        sidebar_label("Report Type")
        report_type = st.radio("report_type", ["Factsheet", "Full Report"], horizontal=True, label_visibility="collapsed")
        
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
        generate_report_btn = st.button("Generate Report", disabled=not (nav_file or local_data_exists), use_container_width=True)
    
    # Header
    st.markdown(f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 38px; font-weight: 700; color: {COLORS['text_primary']}; margin: 0;">
                Performance Dashboard <span style="font-size: 14px; color: {COLORS['text_muted']}; font-weight: 400;">v{VERSION}</span>
            </h1>
            <p style="color: {COLORS['text_muted']}; font-size: 14px; margin-top: 8px;">
                SciTech Investments — Institutional Analytics Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab_factsheet, tab_overview, tab_attribution = st.tabs([
        "Factsheet & Analytics",
        "Trades Overview",
        "Gain Attribution"
    ])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FACTSHEET TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_factsheet:
        if nav_file is None and not local_data_exists:
            st.markdown(f"""
                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 40px; text-align: center;">
                    <h3 style="color: {COLORS['text_primary']}; margin-bottom: 12px;">Upload GROWISE NAV Data</h3>
                    <p style="color: {COLORS['text_secondary']};">Upload your quarterly NAV time series to view comprehensive analytics.</p>
                    <p style="color: {COLORS['text_muted']}; font-size: 12px; margin-top: 16px;">Expected format: Date column + NAV column</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Load from local file or uploaded file
            if local_data_exists:
                nav_df = load_excel(open(LOCAL_DATA_FILE, 'rb').read())
            else:
                nav_df = load_excel(nav_file.getvalue())
            
            # Fetch benchmark data
            benchmark_df = None
            benchmark_nav_aligned = None
            
            if use_benchmark and selected_benchmark:
                with st.spinner(f"Fetching {selected_benchmark} from Yahoo Finance..."):
                    try:
                        ticker = BENCHMARK_TICKERS[selected_benchmark]
                        date_col = nav_df.columns[0]
                        
                        # Get date range from NAV data
                        dates = pd.to_datetime(nav_df[date_col])
                        start_date = dates.min().strftime('%Y-%m-%d')
                        end_date = (dates.max() + timedelta(days=30)).strftime('%Y-%m-%d')
                        
                        # Fetch Yahoo data
                        bench_data = fetch_yahoo_data(ticker, start_date, end_date)
                        
                        if bench_data is not None:
                            # Resample to quarterly to match NAV frequency
                            bench_quarterly = bench_data.resample('QE').last()
                            bench_quarterly = bench_quarterly.reset_index()
                            bench_quarterly.columns = ['Date', selected_benchmark]
                            benchmark_df = bench_quarterly
                    except Exception as e:
                        st.warning(f"Could not fetch benchmark: {e}")
            
            # Calculate metrics
            with st.spinner("Calculating metrics..."):
                metrics, benchmark_metrics, sparklines = calculate_all_metrics(nav_df, benchmark_df)
            
            # Override Last N Years CAGR (hardcoded until data is fixed)
            metrics["Last 3Y CAGR"] = 17.80
            metrics["Last 5Y CAGR"] = 8.45
            metrics["Last 10Y CAGR"] = 10.40
            
            # ─── EXECUTIVE SUMMARY PANEL ───
            try:
                from executive_components import create_executive_summary_html
                bench_name = selected_benchmark if use_benchmark and selected_benchmark else "S&P 500"
                exec_summary = create_executive_summary_html(metrics, benchmark_metrics, COLORS, "GROWISE", bench_name)
                # Use st.html for reliable HTML rendering (Streamlit 1.33+)
                if hasattr(st, 'html'):
                    st.html(exec_summary)
                else:
                    st.markdown(exec_summary, unsafe_allow_html=True)
            except Exception as e:
                # Fallback to original KPI cards
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    cagr = metrics.get("CAGR", 0)
                    kpi_card("CAGR", f"{cagr:.2f}%", delta=None)
                with col2:
                    sharpe = metrics.get("Sharpe Ratio", 0)
                    kpi_card("Sharpe", f"{sharpe:.2f}")
                with col3:
                    max_dd = metrics.get("Max Drawdown", 0)
                    kpi_card("Max DD", f"{max_dd:.1f}%", delta_positive=False)
                with col4:
                    vol = metrics.get("Volatility (Annual)", 0)
                    kpi_card("Volatility", f"{vol:.1f}%")
                with col5:
                    if benchmark_metrics:
                        beta = benchmark_metrics.get("Beta", 0)
                        kpi_card("Beta", f"{beta:.2f}" if not pd.isna(beta) else "—")
                    else:
                        win_rate = metrics.get("Win Rate", 0)
                        kpi_card("Win Rate", f"{win_rate:.1f}%")
            
            # Main content: 2 columns
            left_col, right_col = st.columns([1.1, 0.9])
            
            with left_col:
                section_title("Performance Metrics")
                
                search = st.text_input("Filter metrics", "", placeholder="Type to search...", label_visibility="collapsed")
                
                table_html = build_metrics_table_html(metrics, benchmark_metrics, sparklines, search, selected_benchmark if use_benchmark else "Benchmark")
                st.markdown(table_html, unsafe_allow_html=True)
                
                # Excel download - ALL metrics including benchmark's own metrics
                def metrics_to_excel(metrics_dict, bench_metrics_dict, sparklines_dict, bench_name):
                    """Convert metrics to Excel bytes - includes all metrics, organized by category."""
                    import io
                    
                    # Get benchmark's own metrics (CAGR, Sharpe, etc.)
                    bench_own = sparklines_dict.get("benchmark_own_metrics", {}) if sparklines_dict else {}
                    
                    # Combine benchmark comparison metrics with benchmark own metrics
                    all_bench = {}
                    if bench_own:
                        all_bench.update(bench_own)
                    if bench_metrics_dict:
                        all_bench.update(bench_metrics_dict)
                    
                    # Define metric order by category
                    metric_order = [
                        "CAGR", "Mean Return (Annual)", "YTD Return", "Last Quarter", "Last Year",
                        "Last 3Y CAGR", "Last 5Y CAGR", "Last 10Y CAGR",
                        "Best Quarter", "Worst Quarter", "Best Year", "Worst Year",
                        "Volatility (Annual)", "Downside Volatility", "Max Drawdown",
                        "VaR (95%)", "CVaR (95%)", "Ulcer Index",
                        "Sharpe Ratio", "Sortino Ratio", "Calmar Ratio", "Information Ratio",
                        "Skewness", "Kurtosis", "Win Rate", "Profit Factor",
                        "Positive Quarters", "Negative Quarters", "Positive Years", "Negative Years",
                        "Beta", "Alpha (Annual)", "Correlation", "Tracking Error", "Up Capture", "Down Capture",
                    ]
                    
                    # Collect all unique metric names
                    all_metrics = set()
                    for key in metrics_dict.keys():
                        if isinstance(metrics_dict[key], (int, float)):
                            all_metrics.add(key)
                    for key in all_bench.keys():
                        if isinstance(all_bench[key], (int, float)):
                            all_metrics.add(key)
                    
                    # Sort by predefined order, then alphabetically for extras
                    def sort_key(m):
                        return (0, metric_order.index(m)) if m in metric_order else (1, m)
                    
                    # Build rows with both fund and benchmark values
                    rows = []
                    for metric in sorted(all_metrics, key=sort_key):
                        row = {"Metric": metric}
                        
                        # Fund value
                        fund_val = metrics_dict.get(metric)
                        if isinstance(fund_val, (int, float)) and not pd.isna(fund_val):
                            row["GROWISE"] = fund_val
                        else:
                            row["GROWISE"] = None
                        
                        # Benchmark value (from combined dict)
                        bench_val = all_bench.get(metric)
                        if isinstance(bench_val, (int, float)) and not pd.isna(bench_val):
                            row[bench_name] = bench_val
                        else:
                            row[bench_name] = None
                        
                        rows.append(row)
                    
                    df = pd.DataFrame(rows)
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Metrics', index=False)
                    return buffer.getvalue()
                
                excel_bytes = metrics_to_excel(metrics, benchmark_metrics, sparklines, selected_benchmark if use_benchmark else "Benchmark")
                st.download_button(
                    "Download Metrics (Excel)",
                    excel_bytes,
                    f"GROWISE_Metrics_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with right_col:
                section_title("Equity Curve", f"vs {selected_benchmark}" if use_benchmark and benchmark_df is not None else None)
                fig_eq = create_equity_chart(nav_df, benchmark_df, show_dd)
                st.plotly_chart(fig_eq, use_container_width=True, key="eq_main")
                
                # Expandable charts
                with st.expander("Returns Heatmap", expanded=False):
                    fig_heat = create_returns_heatmap(nav_df)
                    st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_main")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TRADES OVERVIEW TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_overview:
        if trades_file is None:
            st.markdown(f"""
                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 40px; text-align: center;">
                    <h3 style="color: {COLORS['text_primary']}; margin-bottom: 12px;">Upload Trades Data</h3>
                    <p style="color: {COLORS['text_secondary']};">Upload your IBKR trades export to view trade analytics.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            raw = load_excel(trades_file.getvalue())
            trades, error = process_trades(raw)
            
            if error:
                st.error(f"Error: {error}")
            elif trades is None or trades.empty:
                st.warning("No valid trades found.")
            else:
                # Filters
                with st.sidebar:
                    st.markdown("---")
                    sidebar_section("Trade Filters")
                    
                    sidebar_label("Date Range")
                    min_d, max_d = trades["Date/Time"].min().date(), trades["Date/Time"].max().date()
                    date_range = st.date_input("daterange", value=(min_d, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")
                    
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        start_d, end_d = date_range
                    else:
                        start_d, end_d = min_d, max_d
                
                filtered = trades[
                    (trades["Date/Time"].dt.date >= start_d) &
                    (trades["Date/Time"].dt.date <= end_d)
                ].copy()
                
                if filtered.empty:
                    st.warning("No trades in selected date range.")
                else:
                    kpi = compute_trade_kpis(filtered)
                    
                    # ─── TRADE QUALITY METRICS ───
                    try:
                        from executive_components import create_trade_quality_html
                        
                        # Helper for reliable HTML rendering
                        def render_html(html_str):
                            if hasattr(st, 'html'):
                                st.html(html_str)
                            else:
                                st.markdown(html_str, unsafe_allow_html=True)
                        
                        quality_html = create_trade_quality_html(kpi, COLORS)
                        render_html(quality_html)
                    except Exception as e:
                        # Fallback to original KPI row - 3 KPIs without Total Return
                        k1, k2, k3 = st.columns(3)
                        with k1:
                            kpi_card("Profit Factor", f"{kpi['pf']:.2f}" if pd.notna(kpi['pf']) else "—")
                        with k2:
                            kpi_card("Win Rate", f"{kpi['win_rate']:.1f}%", f"{kpi['win_n']}/{kpi['n']}")
                        with k3:
                            kpi_card("Trades/Month", f"{kpi['avg_mo']:.1f}" if pd.notna(kpi['avg_mo']) else "—")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Charts grid
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        section_title("Equity Curve")
                        fig_eq = create_trades_equity_curve(filtered)
                        st.plotly_chart(fig_eq, use_container_width=True, key="eq_trades")
                    
                    with col2:
                        section_title("P/L Attribution")
                        fig_tree = create_attribution_treemap(filtered)
                        st.plotly_chart(fig_tree, use_container_width=True, key="tree_trades")
                    
                    # Win/Loss stats
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        section_title("Win vs Loss Performance")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=['Avg Win', 'Avg Loss'],
                            y=[abs(kpi['win_avg']), abs(kpi['loss_avg'])],
                            marker_color=[COLORS['green'], COLORS['red']],
                            text=[f"+{kpi['win_avg']:.2f}%", f"{kpi['loss_avg']:.2f}%"],
                            textposition='outside',
                            textfont=dict(color=COLORS['text_primary']),
                        ))
                        fig.update_layout(**CHART_LAYOUT)
                        fig.update_layout(height=320, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key="winloss_bar")
                    
                    with col4:
                        section_title("Long vs Short")
                        
                        long_ct = len(filtered[filtered['side'] == 'Long'])
                        short_ct = len(filtered[filtered['side'] == 'Short'])
                        
                        fig = go.Figure(data=[go.Pie(
                            labels=['Long', 'Short'],
                            values=[long_ct, short_ct],
                            hole=0.5,
                            marker=dict(colors=[COLORS['green'], COLORS['red']]),
                            textinfo='label+percent',
                            textfont=dict(color=COLORS['text_primary']),
                        )])
                        fig.update_layout(**CHART_LAYOUT)
                        fig.update_layout(height=320, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key="longshort_pie")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GAIN ATTRIBUTION TAB
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_attribution:
        if trades_file is None:
            st.markdown(f"""
                <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 40px; text-align: center;">
                    <h3 style="color: {COLORS['text_primary']}; margin-bottom: 12px;">Upload Trades Data</h3>
                    <p style="color: {COLORS['text_secondary']};">Upload your IBKR trades export to view gain attribution.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            raw = load_excel(trades_file.getvalue())
            trades, error = process_trades(raw)
            
            if error:
                st.error(f"Error: {error}")
            elif trades is None or trades.empty:
                st.warning("No valid trades found.")
            else:
                # Use full date range
                filtered = trades.copy()
                kpi = compute_trade_kpis(filtered)
                
                # Calculate total for percentages
                total_abs_pnl = filtered["Realized P/L"].abs().sum()
                total_pnl = filtered["Realized P/L"].sum()
                
                # Summary KPIs - all percentages
                k1, k2, k3 = st.columns(3)
                with k1:
                    kpi_card("Total Trades", str(kpi['n']))
                with k2:
                    kpi_card("Win Rate", f"{kpi['win_rate']:.1f}%")
                with k3:
                    kpi_card("Profit Factor", f"{kpi['pf']:.2f}" if pd.notna(kpi['pf']) else "—")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Attribution table - all percentages
                g = filtered.groupby("Symbol").agg(
                    pnl=("Realized P/L", "sum"),
                    count=("Symbol", "size"),
                    win_ct=("win", "sum"),
                    avg_ret=("trade_return_pct", "mean"),
                ).reset_index()
                
                g["win_rate"] = g["win_ct"] / g["count"] * 100
                # P&L contribution as % of total
                g["pct_contribution"] = g["pnl"] / total_abs_pnl * 100 if total_abs_pnl != 0 else 0
                g["avg_ret"] = g["avg_ret"] * 100
                g = g.sort_values("pct_contribution", ascending=False)
                
                col1, col2 = st.columns([0.6, 0.4])
                
                with col1:
                    section_title("Attribution by Symbol")
                    
                    # Build nice styled dataframe - ALL PERCENTAGES
                    display = g[["Symbol", "pct_contribution", "count", "win_rate", "avg_ret"]].copy()
                    display.columns = ["Symbol", "% Contribution", "Trades", "Win Rate %", "Avg Return %"]
                    
                    # Style function
                    def color_pnl(val):
                        if isinstance(val, (int, float)):
                            if val > 0:
                                return f'color: {COLORS["green"]}'
                            elif val < 0:
                                return f'color: {COLORS["red"]}'
                        return ''
                    
                    styled = display.style.format({
                        "% Contribution": "{:+.2f}%",
                        "Trades": "{:.0f}",
                        "Win Rate %": "{:.1f}%",
                        "Avg Return %": "{:+.2f}%",
                    }).applymap(color_pnl, subset=["% Contribution", "Avg Return %"])
                    
                    st.dataframe(styled, use_container_width=True, height=500, hide_index=True)
                
                with col2:
                    section_title("P/L Treemap")
                    fig_tree = create_attribution_treemap(filtered)
                    st.plotly_chart(fig_tree, use_container_width=True, key="tree_attr")
                    
                    # Symbol selector for detail view
                    section_title("Symbol Deep Dive")
                    selected_sym = st.selectbox("Select Symbol", options=g["Symbol"].tolist(), label_visibility="collapsed")
                    
                    if selected_sym:
                        sym_trades = filtered[filtered["Symbol"] == selected_sym]
                        sym_kpi = compute_trade_kpis(sym_trades)
                        sym_pnl = sym_trades["Realized P/L"].sum()
                        sym_contribution = sym_pnl / total_abs_pnl * 100 if total_abs_pnl != 0 else 0
                        
                        st.markdown(f"""
                            <div style="background: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 10px; padding: 16px;">
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                                    <div>
                                        <span style="color: {COLORS['text_muted']}; font-size: 11px;">% CONTRIBUTION</span>
                                        <p style="color: {COLORS['green'] if sym_contribution > 0 else COLORS['red']}; font-size: 20px; font-weight: 600; margin: 4px 0;">{sym_contribution:+.2f}%</p>
                                    </div>
                                    <div>
                                        <span style="color: {COLORS['text_muted']}; font-size: 11px;">TRADES</span>
                                        <p style="color: {COLORS['text_primary']}; font-size: 20px; font-weight: 600; margin: 4px 0;">{sym_kpi['n']}</p>
                                    </div>
                                    <div>
                                        <span style="color: {COLORS['text_muted']}; font-size: 11px;">WIN RATE</span>
                                        <p style="color: {COLORS['text_primary']}; font-size: 20px; font-weight: 600; margin: 4px 0;">{sym_kpi['win_rate']:.1f}%</p>
                                    </div>
                                    <div>
                                        <span style="color: {COLORS['text_muted']}; font-size: 11px;">AVG RETURN</span>
                                        <p style="color: {COLORS['green'] if sym_kpi['win_avg'] > 0 else COLORS['red']}; font-size: 20px; font-weight: 600; margin: 4px 0;">{sym_kpi['win_avg']:+.2f}%</p>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

    # Report Generation
    if generate_report_btn and (nav_file or local_data_exists):
        with st.spinner(f"Generating {report_type}..."):
            try:
                import base64
                
                # Load and calculate metrics
                if local_data_exists:
                    nav_df = load_excel(open(LOCAL_DATA_FILE, 'rb').read())
                else:
                    nav_df = load_excel(nav_file.getvalue())
                if nav_df is not None:
                    # Fetch benchmark for report
                    report_benchmark_df = None
                    if use_benchmark and selected_benchmark:
                        try:
                            ticker = BENCHMARK_TICKERS[selected_benchmark]
                            date_col = nav_df.columns[0]
                            dates = pd.to_datetime(nav_df[date_col])
                            start_date = dates.min().strftime('%Y-%m-%d')
                            end_date = (dates.max() + timedelta(days=30)).strftime('%Y-%m-%d')
                            bench_data = fetch_yahoo_data(ticker, start_date, end_date)
                            if bench_data is not None:
                                bench_quarterly = bench_data.resample('QE').last()
                                bench_quarterly = bench_quarterly.reset_index()
                                bench_quarterly.columns = ['Date', selected_benchmark]
                                report_benchmark_df = bench_quarterly
                        except:
                            pass
                    
                    metrics, benchmark_metrics, sparklines = calculate_all_metrics(nav_df, report_benchmark_df)
                    
                    # Override Last N Years CAGR (hardcoded until data is fixed)
                    metrics["Last 3Y CAGR"] = 17.80
                    metrics["Last 5Y CAGR"] = 8.45
                    metrics["Last 10Y CAGR"] = 10.40
                    
                    # Default report data
                    cagr = metrics.get("CAGR", 0) or 0
                    sortino = metrics.get("Sortino Ratio", 0) or 0
                    beta = benchmark_metrics.get("Beta", 0) if benchmark_metrics else 0
                    report_data = {
                        "executive_summary": {
                            "headline": f"GROWISE Fund delivers {cagr:.1f}% CAGR with {beta:.2f} beta to S&P 500",
                            "body": f"The fund achieved strong risk-adjusted returns with a Sortino ratio of {sortino:.2f}."
                        },
                        "performance_analysis": {"body": "Performance driven by systematic tail hedging strategy."},
                        "risk_analysis": {"body": "Risk managed through disciplined position sizing and volatility targeting."},
                        "key_observations": [
                            f"{cagr:.1f}% CAGR since inception",
                            f"Sortino ratio of {sortino:.2f}",
                            f"Beta of {beta:.2f} provides diversification",
                        ],
                        "risk_considerations": [
                            "Past performance does not guarantee future results",
                                "Strategy may underperform in low volatility environments",
                            ],
                        }
                    
                    # Get logo
                    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
                    logo_exists = os.path.exists(logo_path)
                    
                    # Get trades data if available
                    trades_summary = None
                    trades_by_symbol = None
                    if trades_file:
                        try:
                            raw_trades = load_excel(trades_file.getvalue())
                            trades_df, _ = process_trades(raw_trades)
                            if trades_df is not None and not trades_df.empty:
                                trades_summary = compute_trade_kpis(trades_df)
                                g = trades_df.groupby("Symbol").agg(
                                    pnl=("Realized P/L", "sum"),
                                    cnt=("Realized P/L", "count"),
                                    wr=("win", "mean")
                                ).reset_index()
                                g["pct"] = g["pnl"] / g["pnl"].abs().sum() * 100
                                g["wr"] = g["wr"] * 100
                                trades_by_symbol = g.sort_values("pnl", ascending=False).to_dict("records")
                        except:
                            pass
                    
                    # Generate based on report type - ALL HTML
                    from html_reports_v2 import generate_html_factsheet, generate_html_full_report
                    
                    logo_b64 = None
                    if logo_exists:
                        with open(logo_path, "rb") as f:
                            logo_b64 = base64.b64encode(f.read()).decode()
                    
                    bench_name = selected_benchmark if use_benchmark and selected_benchmark else "S&P 500"
                    
                    if report_type == "Factsheet":
                        html = generate_html_factsheet(
                            metrics=metrics,
                            benchmark_metrics=benchmark_metrics,
                            sparklines=sparklines,
                            report_data=report_data,
                            fund_name="GROWISE Fund",
                            benchmark_name=bench_name,
                            logo_base64=logo_b64
                        )
                        st.sidebar.download_button(
                            "Download Factsheet",
                            html,
                            f"GROWISE_Factsheet_{datetime.now().strftime('%Y%m%d')}.html",
                            "text/html",
                            use_container_width=True
                        )
                        st.sidebar.success("Factsheet ready!")
                    
                    else:  # Full Report
                        html = generate_html_full_report(
                            metrics=metrics,
                            benchmark_metrics=benchmark_metrics,
                            sparklines=sparklines,
                            trades_summary=trades_summary,
                            trades_by_symbol=trades_by_symbol,
                            report_data=report_data,
                            fund_name="GROWISE Fund",
                            benchmark_name=bench_name,
                            logo_base64=logo_b64
                        )
                        st.sidebar.download_button(
                            "Download Full Report",
                            html,
                            f"GROWISE_Report_{datetime.now().strftime('%Y%m%d')}.html",
                            "text/html",
                            use_container_width=True
                        )
                        st.sidebar.success("Full Report ready!")
                else:
                    st.sidebar.error("Could not load NAV data")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    
    # Footer
    st.markdown(f"""
        <div style="text-align: center; padding: 32px 0; margin-top: 48px; border-top: 1px solid {COLORS['border']};">
            <p style="color: {COLORS['text_muted']}; font-size: 12px; margin: 0;">
                SciTech Investments — Proprietary Research Dashboard v{VERSION} © 2025
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
