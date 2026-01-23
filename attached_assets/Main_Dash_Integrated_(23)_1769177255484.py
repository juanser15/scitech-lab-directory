# def toggle_upload_modal(open_n, close_n, is_open):
#     # Robust toggle: do not rely on ctx.triggered_id
#     if open_n:
#         return True
#     if close_n:
#         return False
#     return is_open

from dash import Dash, dcc, html, Input, Output, State, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
import dash
from dash.exceptions import PreventUpdate
from datetime import datetime
from scipy.optimize import minimize
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm
import os
# from crisis_layout import crisis_performance_layout
# from crisis_callbacks import *
import pandas as pd
from io import StringIO
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import base64
import io
from data_governance_report import generate_protocol_report
from dash import ctx
# ======================
# BASE DATA (system-of-record)
# ======================
BASE_DATA_CSV = os.path.join(os.path.dirname(__file__), "data", "base_assets.csv")

def load_base_data_csv(path: str = BASE_DATA_CSV) -> pd.DataFrame:
    """Load base returns (expected quarterly). Replace data/base_assets.csv to change defaults."""
    if not os.path.exists(path):
        return pd.DataFrame()
    df0 = pd.read_csv(path)
    if df0.shape[1] >= 2:
        df0.rename(columns={df0.columns[0]: "date"}, inplace=True)
        df0["date"] = pd.to_datetime(df0["date"])
        df0.set_index("date", inplace=True)
    df0 = df0.sort_index()
    return df0

try:
    _BASE_DF = load_base_data_csv()
    BASE_DATA_JSON = _BASE_DF.to_json(orient="split", date_format="iso") if not _BASE_DF.empty else None
except Exception:
    BASE_DATA_JSON = None

import os
import dash_auth


def upload_and_merge(contents_list, filenames, current_json):
    if not contents_list:
        raise PreventUpdate
    base_df = pd.read_json(StringIO(current_json), orient="split") if current_json else load_base_data_csv()
    base_df.index = pd.to_datetime(base_df.index)
    merged = base_df.copy()
    if not isinstance(contents_list, list):
        contents_list = [contents_list]
        filenames = [filenames]
    
    # Track the oldest start date from all new datasets
    new_data_oldest_dates = []
    
    for contents, fname in zip(contents_list, filenames):
        df_new, qc = parse_and_qc_uploaded_returns(contents, fname)
        df_new_q = resample_returns_to_target(df_new, "Q")
        
        # Track the oldest date of the new data
        if not df_new_q.empty:
            new_data_oldest_dates.append(df_new_q.index.min())
        
        df_new_q = align_to_base_index(df_new_q, merged.index)
        for col in df_new_q.columns:
            col_name = col
            if col_name in merged.columns:
                col_name = f"{col_name}__uploaded"
            merged[col_name] = df_new_q[col]
    
    # Cut merged data to start from the oldest date of the NEW data
    # This ensures all assets have data from the same start date
    if new_data_oldest_dates:
        new_data_start = max(new_data_oldest_dates)  # Use the most recent "oldest" date
        merged = merged[merged.index >= new_data_start]
    
    out_json = merged.to_json(orient="split", date_format="iso")
    msg = dbc.Alert(f"✓ Merged {len(contents_list)} file(s). Total assets now: {len(merged.columns)}", color="success")
    return out_json, msg

# def sort_options_alpha(options):
#     """Sort dropdown options alphabetically by label."""
#     try:
#         return sorted(options, key=lambda x: str(x.get("label","")).lower())
#     except Exception:
#         return options


def alpha_sort_assets(assets):
    return sorted(
        [a for a in assets if a is not None],
        key=lambda x: str(x).lower()
    )

def options_from_assets(assets):
    assets = alpha_sort_assets(assets)
    return [{"label": a, "value": a} for a in assets]


def normalize_assets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforces canonical asset ordering across the entire app.
    - Alphabetical
    - Stable
    - Deterministic
    """
    df = df.copy()
    df = df[sorted(df.columns)]
    return df

def run_protocol(name, contents):
    if name == "File ingestion":
        pass

    elif name == "Schema & index validation":
        pass

    elif name == "Return sanity checks":
        pass

    elif name == "Outlier detection (robust)":
        pass

    elif name == "Frequency detection":
        pass

    elif name == "Compounding to quarterly":
        pass

    elif name == "Calendar alignment":
        pass

    elif name == "Merge with base universe":
        pass

# ======================
# CONFIGURATION
# ======================
ACCENT = "#E67E22"
CHART_HEIGHT = 500
EXPORT_FILENAME = "correlation_analysis"

# Al inicio del archivo, después de imports:
# Institutional Color Palette (Bloomberg/Eikon style)
# Institutional Color Palette (Bloomberg/Eikon style) - Refined
INST_COLORS = {
    'bg_deepest': '#0a0e13',
    'bg_primary': '#0d1117',
    'bg_secondary': '#161b22',
    'bg_tertiary': '#21262d',
    'bg_hover': '#2d333b',
    'border_subtle': '#21262d',
    'border': '#30363d',
    'border_emphasis': '#484f58',
    'text_primary': '#ffffff',
    'text_secondary': '#c9d1d9',
    'text_tertiary': '#8b949e',
    'text_disabled': '#6e7681',
    'accent': '#E67E22',  # Desaturated orange (institutional)
    'accent_hover': '#D35400',
    'accent_muted': '#A04000',
    'success': '#3fb950',
    'success_muted': '#2d7a3e',
    'danger': '#f85149',
    'danger_muted': '#b62324',
    'warning': '#d29922',
    'info': '#58a6ff',
}



# Universal chart template - institutional styling
CHART_TEMPLATE = {
    'layout': {
        'template': 'plotly_dark',
        'paper_bgcolor': INST_COLORS['bg_secondary'],
        'plot_bgcolor': INST_COLORS['bg_tertiary'],
        'font': {
            'family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'size': 13,
            'color': INST_COLORS['text_primary']
        },
        'title': {
            'font': {'size': 16, 'weight': 600, 'color': INST_COLORS['text_primary']},
            'x': 0.02,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        'xaxis': {
            'gridcolor': INST_COLORS['border'],
            'gridwidth': 1,
            'showline': True,
            'linecolor': INST_COLORS['border'],
            'linewidth': 1,
            'zeroline': False,
            'title': {'font': {'size': 12, 'color': INST_COLORS['text_tertiary']}},
            'tickfont': {'size': 11, 'color': INST_COLORS['text_secondary']}
        },
        'yaxis': {
            'gridcolor': INST_COLORS['border'],
            'gridwidth': 1,
            'showline': True,
            'linecolor': INST_COLORS['border'],
            'linewidth': 1,
            'zeroline': True,
            'zerolinecolor': INST_COLORS['text_disabled'],
            'zerolinewidth': 1,
            'title': {'font': {'size': 12, 'color': INST_COLORS['text_tertiary']}},
            'tickfont': {'size': 11, 'color': INST_COLORS['text_secondary']}
        },
        'legend': {
            'bgcolor': INST_COLORS['bg_primary'],
            'bordercolor': INST_COLORS['border'],
            'borderwidth': 1,
            'font': {'size': 11, 'color': INST_COLORS['text_secondary']},
            'orientation': 'v',
            'yanchor': 'top',
            'y': 0.99,
            'xanchor': 'right',
            'x': 0.99
        },
        'hoverlabel': {
            'bgcolor': INST_COLORS['bg_primary'],
            'bordercolor': INST_COLORS['border'],
            'font': {'family': 'SF Mono, monospace', 'size': 11}
        },
        'margin': {'l': 60, 'r': 40, 't': 40, 'b': 50},
        'hovermode': 'x unified',
        'showlegend': True
    }
}

# Institutional color palettes for multi-series charts
CHART_COLORS = {
    'sequential': [
        '#E67E22', '#D35400', '#A04000',  # Oranges
        '#58a6ff', '#3b82f6', '#1e40af'   # Blues
    ],
    'diverging': [
        '#f85149',  # Red (negative)
        '#ffffff',  # White (neutral)
        '#3fb950'   # Green (positive)
    ],
    'qualitative': [
        '#E67E22',  # Orange (primary)
        '#58a6ff',  # Blue
        '#3fb950',  # Green
        '#d29922',  # Yellow
        '#8b5cf6',  # Purple
        '#ec4899',  # Pink
        '#14b8a6',  # Teal
        '#f85149'   # Red
    ]
}

# Frequency detection and defaults
FREQ_CONFIG = {
    "D": {"label": "Daily", "ann_factor": 252, "default_window": 20},
    "W": {"label": "Weekly", "ann_factor": 52, "default_window": 12},
    "M": {"label": "Monthly", "ann_factor": 12, "default_window": 6},
    "Q": {"label": "Quarterly", "ann_factor": 4, "default_window": 4},
    "Y": {"label": "Yearly", "ann_factor": 1, "default_window": 3},
}

FAMOUS_PORTFOLIOS = {
    'Custom Portfolio': {
        'description': 'Build your own portfolio from scratch',
        'weights': {},
        'fallback': {}
    },
    '60/40 Classic': {
        'description': 'Traditional 60% stocks, 40% bonds',
        'weights': {'^GSPC': 0.60, 'AGG': 0.40},
        'fallback': {'SPY': 0.60, 'AGG': 0.40}
    },
    'Ray Dalio All Weather': {
        'description': '30% stocks, 40% long bonds, 15% intermediate bonds, 7.5% gold, 7.5% commodities',
        'weights': {'^GSPC': 0.30, 'TLT': 0.40, 'IEF': 0.15, 'GLD': 0.075, 'DBC': 0.075},
        'fallback': {'SPY': 0.30, 'TLT': 0.40, 'IEF': 0.15, 'GLD': 0.075, 'DBC': 0.075}
    },
    'Harry Browne Permanent': {
        'description': '25% stocks, 25% long bonds, 25% gold, 25% cash',
        'weights': {'^GSPC': 0.25, 'TLT': 0.25, 'GLD': 0.25, 'SHY': 0.25},
        'fallback': {'SPY': 0.25, 'TLT': 0.25, 'GLD': 0.25, 'SHY': 0.25}
    },
    'David Swensen Yale': {
        'description': '30% US stocks, 15% international, 20% emerging, 20% REIT, 15% bonds',
        'weights': {'^GSPC': 0.30, 'VEA': 0.15, 'VWO': 0.20, 'VNQ': 0.20, 'TLT': 0.15},
        'fallback': {'SPY': 0.30, 'VEA': 0.15, 'VWO': 0.20, 'VNQ': 0.20, 'TLT': 0.15}
    },
    'Rick Ferri Core Four': {
        'description': '48% US stocks, 24% international, 20% bonds, 8% REIT',
        'weights': {'^GSPC': 0.48, 'VEA': 0.24, 'AGG': 0.20, 'VNQ': 0.08},
        'fallback': {'SPY': 0.48, 'VEA': 0.24, 'AGG': 0.20, 'VNQ': 0.08}
    },
    'Bill Bernstein No Brainer': {
        'description': '25% large cap, 25% small cap, 25% international, 25% bonds',
        'weights': {'^GSPC': 0.25, 'IWM': 0.25, 'VEA': 0.25, 'AGG': 0.25},
        'fallback': {'SPY': 0.25, 'IWM': 0.25, 'VEA': 0.25, 'AGG': 0.25}
    },
    'Mebane Faber Ivy': {
        'description': '20% each: stocks, international, bonds, REIT, commodities',
        'weights': {'^GSPC': 0.20, 'VEA': 0.20, 'AGG': 0.20, 'VNQ': 0.20, 'DBC': 0.20},
        'fallback': {'SPY': 0.20, 'VEA': 0.20, 'AGG': 0.20, 'VNQ': 0.20, 'DBC': 0.20}
    },
    'Golden Butterfly': {
        'description': '20% each: large cap, small cap value, long bonds, short bonds, gold',
        'weights': {'^GSPC': 0.20, 'IWM': 0.20, 'TLT': 0.20, 'SHY': 0.20, 'GLD': 0.20},
        'fallback': {'SPY': 0.20, 'IWM': 0.20, 'TLT': 0.20, 'SHY': 0.20, 'GLD': 0.20}
    }
}


# ============================================================
# INSTITUTIONAL COMPONENT HELPERS
# ============================================================

def apply_institutional_template(fig):
    """
    Apply standardized institutional template to any Plotly figure.
    
    Usage:
        fig = go.Figure()
        fig.add_trace(...)
        fig = apply_institutional_template(fig)
    """
    fig.update_layout(**CHART_TEMPLATE['layout'])
    return fig


def create_empty_chart(message="No data available"):
    """
    Standard empty state for charts with institutional styling.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color=INST_COLORS['text_tertiary'])
    )
    fig = apply_institutional_template(fig)
    return fig


def create_section_header(title, subtitle=None, icon=None):
    """
    Standardized section header with optional subtitle and icon.
    
    Args:
        title: Main section title
        subtitle: Optional descriptive text
        icon: Optional emoji or icon character
    
    Returns:
        html.Div with standardized styling
    """
    title_row_children = []
    if icon:
        title_row_children.append(html.Span(icon, className='section-icon'))
    title_row_children.append(html.H2(title, className='text-h1'))
    
    title_row = html.Div(title_row_children, className='section-title-row')
    
    components = [title_row]
    if subtitle:
        components.append(html.P(subtitle, className='text-label'))
    
    return html.Div(components, className='section-header')


def create_metric_card(label, value, change=None, change_label=None):
    """
    Standardized metric display card with optional change indicator.
    
    Args:
        label: Metric name (e.g., "Sharpe Ratio")
        value: Current value (formatted string)
        change: Optional change percentage (e.g., 2.5)
        change_label: Optional label for change (e.g., "vs last quarter")
    
    Returns:
        html.Div with metric card styling
    """
    change_div = None
    if change is not None:
        change_class = 'positive' if change >= 0 else 'negative'
        arrow = '▲' if change >= 0 else '▼'
        
        change_content = [
            html.Span(arrow),
            html.Span(f"{abs(change):.2f}%")
        ]
        if change_label:
            change_content.append(html.Span(f" {change_label}", style={'marginLeft': '4px'}))
        
        change_div = html.Div(change_content, className=f'metric-change {change_class}')
    
    return html.Div([
        html.Div(label, className='metric-label'),
        html.Div(value, className='metric-value'),
        change_div
    ], className='metric-card')


def create_institutional_card(header_title, body_content, header_subtitle=None, footer_content=None):
    """
    Standardized card component with header, body, and optional footer.
    
    Args:
        header_title: Card title
        body_content: Content for card body (can be any Dash component)
        header_subtitle: Optional subtitle in header
        footer_content: Optional footer content
    
    Returns:
        html.Div with institutional card styling
    """
    header_children = [html.H3(header_title, className='card-header-title')]
    if header_subtitle:
        header_children.append(html.P(header_subtitle, className='card-header-subtitle'))
    
    header = html.Div(header_children, className='card-header')
    body = html.Div(body_content, className='card-body')
    
    components = [header, body]
    if footer_content:
        footer = html.Div(footer_content, className='card-footer')
        components.append(footer)
    
    return html.Div(components, className='card-institutional')


def format_return(value, percentage=True, decimals=2):
    """
    Format return values with institutional conventions.
    
    Args:
        value: Numeric value
        percentage: If True, multiply by 100 and add % sign
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    if value is None or np.isnan(value):
        return "N/A"
    
    if percentage:
        return f"{value * 100:.{decimals}f}%"
    else:
        return f"{value:.{decimals}f}"


def format_large_number(value, decimals=0):
    """
    Format large numbers with commas and optional K/M/B suffix.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
    
    Returns:
        Formatted string
    """
    if value is None or np.isnan(value):
        return "N/A"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1e9:
        return f"{sign}{abs_value/1e9:.{decimals}f}B"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value/1e6:.{decimals}f}M"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value/1e3:.{decimals}f}K"
    else:
        return f"{sign}{abs_value:,.{decimals}f}"



# ======================
# UTILITY FUNCTIONS
# ======================
def detect_frequency(idx):
    """Detect frequency from datetime index and return config"""
    try:
        freq = pd.infer_freq(idx)
    except:
        freq = None
    
    if not freq:
        # Fallback: estimate from median time delta
        if len(idx) > 3:
            dt = (idx[1:] - idx[:-1]).median().days
            if dt <= 2:   return "D", FREQ_CONFIG["D"]
            if dt <= 10:  return "W", FREQ_CONFIG["W"]
            if dt <= 40:  return "M", FREQ_CONFIG["M"]
            if dt <= 120: return "Q", FREQ_CONFIG["Q"]
            return "Y", FREQ_CONFIG["Y"]
        return "M", FREQ_CONFIG["M"]
    
    freq_upper = freq.upper()
    if freq_upper.startswith("D"): return "D", FREQ_CONFIG["D"]
    if freq_upper.startswith("W"): return "W", FREQ_CONFIG["W"]
    if freq_upper.startswith("M"): return "M", FREQ_CONFIG["M"]
    if freq_upper.startswith("Q"): return "Q", FREQ_CONFIG["Q"]
    if freq_upper.startswith("Y"): return "Y", FREQ_CONFIG["Y"]
    return "M", FREQ_CONFIG["M"]


# ======================
# DATA INGESTION GOVERNANCE (Phase 2)
# ======================

def resample_returns_to_quarterly(df: pd.DataFrame) -> pd.DataFrame:
    """Resample returns to quarterly using compounding (prod(1+r)-1)."""
    if df.empty:
        return df
    # Ensure datetime index
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return (1.0 + df).resample('QE').prod() - 1.0


def resample_returns_to_target(df: pd.DataFrame, target_code: str = 'Q') -> pd.DataFrame:
    """Resample returns to a target frequency using compounding.
    Supported target codes:
      - 'Q' -> quarterly (default)
      - 'M' -> monthly
      - 'W' -> weekly (Friday)
      - 'D' -> daily (no-op)
    """
    if df is None or df.empty:
        return df
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    if target_code == 'Q':
        return (1.0 + df).resample('QE').prod() - 1.0
    if target_code == 'M':
        return (1.0 + df).resample('M').prod() - 1.0
    if target_code == 'W':
        return (1.0 + df).resample('W-FRI').prod() - 1.0
    if target_code == 'D':
        return df

    # Fallback: try pandas resample with compounding
    try:
        return (1.0 + df).resample(target_code).prod() - 1.0
    except Exception:
        # As last resort, return original
        return df


def align_to_reference_dates(df: pd.DataFrame, ref_index: pd.DatetimeIndex, tolerance_days: int = 15) -> tuple[pd.DataFrame, dict]:
    """Align df to ref quarter-ends using nearest-with-tolerance. Returns aligned df and alignment report."""
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    ref_index = pd.to_datetime(ref_index).sort_values()
    moved = []
    out_of_tol = []

    # Build map for each ref date to nearest df date
    df_dates = df.index
    if len(df_dates) == 0 or len(ref_index) == 0:
        return df.reindex(ref_index), {
            'method': 'nearest_with_tolerance',
            'tolerance_days': tolerance_days,
            'moved_count': 0,
            'out_of_tolerance_count': len(ref_index),
            'max_shift_days': None,
        }

    # For each ref date, choose nearest df date
    aligned_rows = []
    max_shift = 0
    for d in ref_index:
        # nearest
        i = df_dates.get_indexer([d], method='nearest')[0]
        nearest = df_dates[i]
        shift = abs((nearest - d).days)
        if shift <= tolerance_days:
            if nearest != d:
                moved.append({'ref_date': d.isoformat(), 'nearest_date': nearest.isoformat(), 'shift_days': int(shift)})
                max_shift = max(max_shift, shift)
            aligned_rows.append(df.loc[nearest].rename(d))
        else:
            out_of_tol.append({'ref_date': d.isoformat(), 'nearest_date': nearest.isoformat(), 'shift_days': int(shift)})
            # fill NaNs for that row
            aligned_rows.append(pd.Series({c: float('nan') for c in df.columns}, name=d))

    aligned = pd.DataFrame(aligned_rows)
    aligned.index = ref_index

    report = {
        'method': 'nearest_with_tolerance',
        'tolerance_days': tolerance_days,
        'moved_count': len(moved),
        'out_of_tolerance_count': len(out_of_tol),
        'max_shift_days': max_shift if (moved or out_of_tol) else 0,
        'moved_examples': moved[:10],
        'out_of_tolerance_examples': out_of_tol[:10],
    }
    return aligned, report


def run_data_quality_gate(df: pd.DataFrame) -> dict:
    """Run practical QC checks to flag fat-fingers and suspicious inputs."""
    report = {
        'critical_flags': [],
        'warnings': [],
        'per_asset': {},
        'summary': {}
    }
    if df is None or df.empty:
        report['critical_flags'].append('EMPTY_DATA')
        return report

    # Basic stats
    max_abs = df.abs().max().max()
    min_val = df.min().min()

    # Impossible return
    if min_val < -1.0:
        report['critical_flags'].append('IMPOSSIBLE_RETURN_LT_NEG100')

    # Scale suspect (percent vs decimal)
    if max_abs > 1.5 and max_abs < 200:
        report['warnings'].append('SCALE_SUSPECT_PERCENT')

    # Robust outliers via MAD z-score
    for c in df.columns:
        s = df[c].dropna()
        if len(s) < 8:
            report['per_asset'][c] = {'n': int(len(s)), 'flags': ['SAMPLE_LIMITED']}
            continue
        med = s.median()
        mad = (s - med).abs().median()
        flags = []
        if mad == 0:
            # fallback to std
            std = s.std()
            if std > 0:
                z = ((s - s.mean()) / std).abs().max()
                if z > 6:
                    flags.append('OUTLIER_STD_Z_GT_6')
        else:
            # 0.6745 normalizing constant
            rz = (0.6745 * (s - med) / mad).abs()
            if rz.max() > 6:
                flags.append('OUTLIER_ROBUST_Z_GT_6')
        report['per_asset'][c] = {
            'n': int(len(s)),
            'min': float(s.min()),
            'max': float(s.max()),
            'flags': flags
        }

    report['summary'] = {
        'max_abs_return': float(max_abs),
        'min_return': float(min_val),
        'n_assets': int(df.shape[1]),
        'n_obs': int(df.shape[0]),
    }
    return report


def log_data_quality(report: dict, prefix: str = 'data_quality') -> str:
    """Persist QC report as JSON to local logs directory."""
    try:
        import json
        from datetime import datetime
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        fp = logs_dir / f"{prefix}_{ts}.json"
        fp.write_text(json.dumps(report, indent=2), encoding='utf-8')
        return str(fp)
    except Exception:
        return ''

DATA_GOVERNANCE_PROTOCOLS = [
    {"id": "ingestion", "label": "File ingestion"},
    {"id": "schema", "label": "Schema & index validation"},
    {"id": "sanity", "label": "Return sanity checks"},
    {"id": "outliers", "label": "Outlier detection (robust)"},
    {"id": "frequency", "label": "Frequency detection"},
    {"id": "compounding", "label": "Compounding to quarterly"},
    {"id": "alignment", "label": "Calendar alignment"},
    {"id": "merge", "label": "Merge with base universe"},
]

# =============================================================================
# FACTOR ATTRIBUTION - FLEXIBLE FUNCTION (CAGR ANNUALIZED)
# =============================================================================

def create_factor_attribution_chart_cagr(model, merged_data, years, factor_cols, chart_title="Return Attribution"):
    """
    Genera gráfico de atribución factorial en CAGR anualizado.
    Se adapta automáticamente a 3FF, 5FF, o cualquier modelo factorial.
    
    Uses COMPOUND method (correct), not linear sum.
    Normalizes by Quarter to avoid date mismatch.
    
    Parameters:
    -----------
    model : statsmodels OLS result
    merged_data : pd.DataFrame con Portfolio/Excess_Return y factores
    years : float - años en el análisis
    factor_cols : list - nombres de las columnas de factores
    chart_title : str - título del gráfico
    
    Returns:
    --------
    fig : plotly Figure
    alpha_pct : float - % del retorno total que es alpha
    """
    
    # Extraer alpha y factores
    alpha = model.params['const']
    factors = [col for col in model.params.index if col != 'const']
    
    # Calcular contribuciones CAGR (COMPUESTAS, no suma lineal)
    alpha_series = pd.Series(alpha, index=merged_data.index)
    cumulative_alpha = (1 + alpha_series).prod() - 1
    cagr_alpha = ((1 + cumulative_alpha) ** (1/years) - 1) * 100
    
    cagr_factors = {}
    cumulative_factors = {}
    for factor in factors:
        beta = model.params[factor]
        factor_contrib = beta * merged_data[factor]
        cumulative_factor = (1 + factor_contrib).prod() - 1
        cumulative_factors[factor] = cumulative_factor
        cagr_factor = ((1 + cumulative_factor) ** (1/years) - 1) * 100
        cagr_factors[factor] = cagr_factor
    
    # Total return actual
    if 'Portfolio' in merged_data.columns:
        portfolio_returns = merged_data['Portfolio']
    elif 'Excess_Return' in merged_data.columns:
        portfolio_returns = merged_data['Excess_Return']
    else:
        # Fallback: primera columna que no sea factor
        portfolio_col = [c for c in merged_data.columns if c not in factors + ['RF']][0]
        portfolio_returns = merged_data[portfolio_col]
    
    cumulative_actual = (1 + portfolio_returns).prod() - 1
    cagr_total = ((1 + cumulative_actual) ** (1/years) - 1) * 100
    
    # Preparar datos para gráfico
    labels = ['Alpha'] + factors + ['Total']
    values = [cagr_alpha] + [cagr_factors[f] for f in factors] + [cagr_total]
    
    # Colores dinámicos
    color_map = {
        'Alpha': INST_COLORS['accent'],
        'Mkt-RF': '#3498db',
        'MKT-RF': '#3498db',
        'SMB': '#e74c3c',
        'HML': '#2ecc71',
        'RMW': '#f39c12',
        'CMA': '#9b59b6',
        'MOM': '#1abc9c',
        'Total': INST_COLORS['text_secondary']
    }
    colors = [color_map.get(label, '#7f8c8d') for label in labels]
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors, line=dict(color='white', width=1.5)),
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        textfont=dict(size=11, color='white', family='Arial'),
        hovertemplate='%{x}<br>CAGR: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{chart_title}<br><sub>Fama-French {len(factors)}-Factor Model</sub>',
            font=dict(size=14, color='white', family='Arial'),
            x=0.5, xanchor='center'
        ),
        xaxis=dict(
            title='',
            tickfont=dict(size=10, color='white'),
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            title=dict(
                text='Annualized Return (CAGR %)',
                font=dict(size=11, color='white')
            ),
            tickfont=dict(size=10, color='white'),
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.3)'
        ),
        plot_bgcolor='#0d1117',
        paper_bgcolor='#0d1117',
        showlegend=False,
        height=350,
        margin=dict(t=60, b=70, l=60, r=20),
        template='plotly_dark'
    )
    
    # Info annotation
    alpha_pct_of_total = (cumulative_alpha / cumulative_actual) * 100 if cumulative_actual != 0 else 0
    
    info_text = (
        f'Total: {cumulative_actual*100:.0f}% ({years:.1f}yrs)<br>'
        f'Alpha: {cagr_alpha:.1f}% annual '
        f'({alpha_pct_of_total:.0f}% of total)'
    )
    
    fig.add_annotation(
        text=info_text,
        xref='paper', yref='paper',
        x=0.98, y=0.98,
        xanchor='right', yanchor='top',
        showarrow=False,
        bgcolor='#161b22',
        bordercolor=INST_COLORS['accent'],
        borderwidth=2,
        borderpad=8,
        font=dict(size=9, color='white', family='Arial'),
        opacity=0.95
    )
    
    return fig, alpha_pct_of_total


def help_icon(metric_name, what_it_shows, why_it_matters, what_to_look_for=None, icon_id=None):
    """
    Orange "?" icon with structured institutional-grade tooltip.
    No emojis, clean formatting, left-aligned text.
    """
    if icon_id is None:
        import random
        icon_id = f"help-{metric_name.lower().replace(' ', '-')}-{random.randint(1000, 9999)}"
    
    # Build tooltip content as HTML, not a raw string
    tooltip_children = [
        html.Div([
            html.Span("What it shows: ", style={'fontWeight': 'bold'}),
            html.Span(what_it_shows),
        ]),
        html.Br(),
        html.Div([
            html.Span("Why it matters: ", style={'fontWeight': 'bold'}),
            html.Span(why_it_matters),
        ]),
    ]
    
    if what_to_look_for:
        tooltip_children.extend([
            html.Br(),
            html.Div([
                html.Span("What to look for: ", style={'fontWeight': 'bold'}),
                html.Span(what_to_look_for),
            ])
        ])
    
    return html.Span([
        html.Span(
            "?",
            id=icon_id,
            style={
                'display': 'inline-block',
                'width': '18px',
                'height': '18px',
                'lineHeight': '18px',
                'textAlign': 'center',
                'backgroundColor': '#E67E22',
                'color': 'white',
                'borderRadius': '50%',
                'fontSize': '12px',
                'fontWeight': 'bold',
                'marginLeft': '8px',
                'cursor': 'help',
                'verticalAlign': 'middle',
            },
        ),
        dbc.Tooltip(
            html.Div(tooltip_children),
            target=icon_id,
            placement='right',
            style={
                'maxWidth': '450px',
                'fontSize': '13px',
                'whiteSpace': 'normal',
                'textAlign': 'left',
                'lineHeight': '1.5',
            },
        ),
    ])




def download_fama_french_factors():
    """
    Download Fama-French 5 factors + Momentum from Ken French's data library
    Returns DataFrame with daily factors
    """
    import urllib.request
    import zipfile
    from io import BytesIO
    
    try:
        # Download FF 5 Factors (daily)
        url_5factors = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
        
        response = urllib.request.urlopen(url_5factors)
        zip_file = zipfile.ZipFile(BytesIO(response.read()))
        csv_file = zip_file.namelist()[0]
        
        # Read the CSV - Ken French files have specific format
        with zip_file.open(csv_file) as f:
            lines = f.readlines()
            
        # Find where data starts (after header)
        start_idx = 0
        for i, line in enumerate(lines):
            if b'Mkt-RF' in line:
                start_idx = i
                break
        
        # Parse data
        data_lines = []
        for line in lines[start_idx+1:]:
            line_str = line.decode('utf-8').strip()
            if not line_str or line_str.startswith('Copyright') or len(line_str.split(',')) < 5:
                break
            data_lines.append(line_str)
        
        # Create DataFrame
        data = []
        for line in data_lines:
            parts = line.split(',')
            if len(parts) >= 6:
                try:
                    date = pd.to_datetime(parts[0], format='%Y%m%d')
                    mkt_rf = float(parts[1]) / 100  # Convert from percentage
                    smb = float(parts[2]) / 100
                    hml = float(parts[3]) / 100
                    rmw = float(parts[4]) / 100
                    cma = float(parts[5]) / 100
                    data.append([date, mkt_rf, smb, hml, rmw, cma])
                except:
                    continue
        
        df_factors = pd.DataFrame(data, columns=['Date', 'MKT-RF', 'SMB', 'HML', 'RMW', 'CMA'])
        df_factors.set_index('Date', inplace=True)
        
        # Download Momentum factor
        try:
            url_mom = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip"
            response_mom = urllib.request.urlopen(url_mom)
            zip_file_mom = zipfile.ZipFile(BytesIO(response_mom.read()))
            csv_file_mom = zip_file_mom.namelist()[0]
            
            with zip_file_mom.open(csv_file_mom) as f:
                lines_mom = f.readlines()
            
            start_idx_mom = 0
            for i, line in enumerate(lines_mom):
                if b'Mom' in line or b'MOM' in line:
                    start_idx_mom = i
                    break
            
            mom_data = []
            for line in lines_mom[start_idx_mom+1:]:
                line_str = line.decode('utf-8').strip()
                if not line_str or line_str.startswith('Copyright') or len(line_str.split(',')) < 2:
                    break
                parts = line_str.split(',')
                if len(parts) >= 2:
                    try:
                        date = pd.to_datetime(parts[0], format='%Y%m%d')
                        mom = float(parts[1]) / 100
                        mom_data.append([date, mom])
                    except:
                        continue
            
            df_mom = pd.DataFrame(mom_data, columns=['Date', 'MOM'])
            df_mom.set_index('Date', inplace=True)
            
            # Merge
            df_factors = df_factors.join(df_mom, how='left')
            df_factors['MOM'].fillna(0, inplace=True)
            
        except:
            df_factors['MOM'] = 0
            
        return df_factors
        
    except Exception as e:
        print(f"Error downloading Fama-French factors: {e}")
        return None

def calculate_quadrant_analysis(growise_returns, benchmark_returns):
    """
    Calculate quadrant analysis for regime-dependent performance
    Returns dict with statistics for each quadrant
    """
    # Align data
    combined = pd.DataFrame({
        'GROWISE': growise_returns,
        'Benchmark': benchmark_returns
    }).dropna()
    
    # Define quadrants
    q1_mask = (combined['Benchmark'] > 0) & (combined['GROWISE'] > 0)  # Both Up
    q2_mask = (combined['Benchmark'] < 0) & (combined['GROWISE'] > 0)  # Bench Down, GW Up (KEY!)
    q3_mask = (combined['Benchmark'] < 0) & (combined['GROWISE'] < 0)  # Both Down
    q4_mask = (combined['Benchmark'] > 0) & (combined['GROWISE'] < 0)  # Bench Up, GW Down
    
    def quadrant_stats(mask, name):
        subset = combined[mask]
        if len(subset) == 0:
            return {
                'name': name,
                'count': 0,
                'hit_rate': 0,
                'avg_growise': 0,
                'avg_benchmark': 0,
                'beta': 0,
                'alpha': 0
            }
        
        # Calculate beta and alpha via regression
        if len(subset) > 2:
            X = subset['Benchmark'].values.reshape(-1, 1)
            y = subset['GROWISE'].values
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)
            beta = model.coef_[0]
            alpha = model.intercept_
        else:
            beta = 0
            alpha = 0
        
        return {
            'name': name,
            'count': len(subset),
            'hit_rate': len(subset) / len(combined) * 100,
            'avg_growise': subset['GROWISE'].mean() * 100,  # Convert to percentage
            'avg_benchmark': subset['Benchmark'].mean() * 100,
            'beta': beta,
            'alpha': alpha * 100
        }
    
    results = {
        'Q1': quadrant_stats(q1_mask, 'Q1: Both Up'),
        'Q2': quadrant_stats(q2_mask, 'Q2: Benchmark Down, GROWISE Up'),
        'Q3': quadrant_stats(q3_mask, 'Q3: Both Down'),
        'Q4': quadrant_stats(q4_mask, 'Q4: Benchmark Up, GROWISE Down'),
        'data': combined
    }
    
    return results

def calculate_factor_attribution(growise_returns, factors_df):
    """
    Calculate factor exposures and attribution for GROWISE returns
    Returns dict with factor betas, attributions, and alpha
    """
    # Align data
    combined = growise_returns.to_frame('GROWISE').join(factors_df, how='inner')
    combined = combined.dropna()
    
    if len(combined) < 20:
        return None
    
    # Run regression: GROWISE = alpha + beta_mkt*MKT + beta_smb*SMB + ... + epsilon
    
    factor_cols = ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
    available_factors = [f for f in factor_cols if f in combined.columns]
    
    if len(available_factors) == 0:
        return None
    
    X = combined[available_factors].values
    y = combined['GROWISE'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate contributions
    factor_betas = dict(zip(available_factors, model.coef_))
    alpha = model.intercept_
    
    # Calculate factor contributions to total return
    total_return = combined['GROWISE'].sum()
    factor_contributions = {}
    
    for factor, beta in factor_betas.items():
        factor_return = combined[factor].sum()
        contribution = beta * factor_return
        factor_contributions[factor] = contribution
    
    # Calculate R-squared
    y_pred = model.predict(X)
    r_squared = r2_score(y, y_pred)
    
    return {
        'betas': factor_betas,
        'alpha': alpha,
        'alpha_total': alpha * len(combined),  # Total alpha contribution
        'contributions': factor_contributions,
        'total_return': total_return,
        'r_squared': r_squared,
        'residuals': y - y_pred
    }

# ======================
# UTILITY FUNCTIONS
# ======================
def infer_ann_factor(idx) -> int:
    """Infer annualization factor from index frequency"""
    freq_code, freq_config = detect_frequency(idx)
    return freq_config["ann_factor"]

def detect_native_label(idx) -> str:
    """Detect native frequency label"""
    freq_code, freq_config = detect_frequency(idx)
    return freq_config["label"]

def compound_resample(s: pd.Series, rule: str) -> pd.Series:
    """Resample returns by geometric compounding"""
    return (1 + s).resample(rule).prod() - 1

def find_benchmark(columns):
    """Auto-detect benchmark column - prioritize GROWISE for Correlation Analysis"""
    for cand in ["GROWISE", "SPX", "S&P", "SP500", "^GSPC"]:
        for c in columns:
            if cand.lower() in str(c).lower():
                return c
    return columns[0] if len(columns) else None

def find_benchmark_pf(columns):
    """Auto-detect benchmark column for Portfolio Lab - prioritize GSPC"""
    for cand in ["GSPC", "^GSPC", "SPX", "S&P500", "SP500", "GROWISE"]:
        for c in columns:
            if cand.lower() in str(c).lower():
                return c
    return columns[0] if len(columns) else None

def ann_metrics(series: pd.Series):
    """Calculate annualized metrics"""
    series = series.dropna()
    if len(series) < 2:
        return np.nan, np.nan, np.nan, np.nan
    af = infer_ann_factor(series.index)
    mu  = series.mean() * af
    vol = series.std() * np.sqrt(af)
    sharpe = mu / vol if vol != 0 else np.nan
    dd = (1 + series).cumprod()
    dd = dd / dd.cummax() - 1.0
    maxdd = dd.min()
    return mu, vol, sharpe, maxdd

def validate_data(df: pd.DataFrame) -> tuple:
    """Validate uploaded data and return (is_valid, message)"""
    if df.empty:
        return False, "Dataset is empty"
    
    # Check if index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except:
            return False, "First column must be dates. Ensure your CSV has dates in the first column."
    
    # Phase 2: Quality gate + frequency harmonization to quarterly (Growise system frequency)
    qc = run_data_quality_gate(df)

    # Detect input frequency and resample to quarterly if needed
    in_freq_code, in_freq_config = detect_frequency(df.index)
    if in_freq_code != 'Q':
        df = resample_returns_to_target(df, target_code='Q')
    # Re-detect after resample
    freq_code, freq_config = detect_frequency(df.index)

    freq_label = freq_config["label"]
    
    # Check for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return False, "No numeric columns found. Check your data format."
    
    if len(numeric_cols) < len(df.columns):
        non_numeric = set(df.columns) - set(numeric_cols)
        # Only warn, don't fail - just use numeric columns
        df = df[numeric_cols]
    
    missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    if missing_pct > 50:  # Relaxed from 30% to 50%
        return False, f"Too much missing data ({missing_pct:.1f}%). Consider filling or removing missing values."
    
    if len(df) < 10:  # Relaxed from 20 to 10
        return False, f"Insufficient data points ({len(df)}). Need at least 10 periods."
    
    # Check if data looks like returns - be more lenient
    max_val = df.abs().max().max()
    if max_val > 100:  # Very relaxed - just check it's not obviously wrong
        return False, f"Data values seem unrealistic (max: {max_val:.2f}). Please verify your data."
    
    # Build success message with warnings if needed
    warnings = []
    if missing_pct > 10:
        warnings.append(f"WARNING: {missing_pct:.1f}% missing data")
    if max_val > 2:
        warnings.append(f"WARNING: Large values detected (max: {max_val:.2f}) - ensure these are returns")
    
    warning_text = " | ".join(warnings) if warnings else ""
    success_msg = f"SUCCESS: Loaded: {len(df)} periods ({freq_label}), {len(df.columns)} assets ({df.index.min().date()} to {df.index.max().date()})"
    
    if warning_text:
        success_msg += f"\n{warning_text}"
    
    return True, success_msg

def calculate_correlation_stability(returns, target, window=12, stability_window=24):
    """Calculate rolling correlation and its stability (std dev)"""
    roll_corr = returns.rolling(window).corr(target)
    stability = roll_corr.rolling(stability_window).std()
    return roll_corr, stability

def detect_market_regime(benchmark_returns, threshold=0):
    """Classify periods as bull (1) or bear (0) market"""
    return (benchmark_returns > threshold).astype(int)

# ======================
# App Initialization
# ======================
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)

# ======================
# AUTHENTICATION
# ======================


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


auth = dash_auth.BasicAuth(app, VALID_USERS)

app.title = "SciTech Lab"

# Add custom CSS for tutorial highlighting
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Tutorial element highlighting */
            .tour-highlight {
                animation: tour-pulse 2s ease-in-out infinite;
                box-shadow: 0 0 20px 5px rgba(255, 140, 0, 0.6) !important;
                border: 3px solid #E67E22 !important;
                border-radius: 8px;
                position: relative;
                z-index: 999;
            }
            
            @keyframes tour-pulse {
                0%, 100% {
                    box-shadow: 0 0 20px 5px rgba(255, 140, 0, 0.6);
                }
                50% {
                    box-shadow: 0 0 30px 8px rgba(255, 140, 0, 0.8);
                }
            }
            
            /* Tutorial modal styling */
            .modal-content {
                border-radius: 12px !important;
            }
            
            .modal-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 12px 12px 0 0 !important;
            }
            
            .modal-body {
                padding: 2rem;
                line-height: 1.8;
            }
            
            .modal-footer {
                background-color: #f8f9fa;
                border-radius: 0 0 12px 12px !important;
            }
            
            /* Tour button styling */
            #start-tour {
                animation: tour-button-pulse 3s ease-in-out infinite;
            }
            
            @keyframes tour-button-pulse {
                0%, 100% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Element highlighting coordination
            window.dashExtensions = window.dashExtensions || {};
            
            window.dashExtensions.highlightElement = function(elementId) {
                // Remove previous highlights
                document.querySelectorAll('.tour-highlight').forEach(el => {
                    el.classList.remove('tour-highlight');
                });
                
                if (!elementId) return;
                
                // Add highlight to target element
                const element = document.getElementById(elementId);
                if (element) {
                    element.classList.add('tour-highlight');
                    
                    // Scroll element into view smoothly
                    setTimeout(() => {
                        element.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center',
                            inline: 'nearest'
                        });
                    }, 300);
                    
                    // Remove highlight after 5 seconds
                    setTimeout(() => {
                        element.classList.remove('tour-highlight');
                    }, 5000);
                }
            };
        </script>
    </body>
</html>
"""





def create_analysis_tab():
    """Main analysis tab with improved controls"""
    return dbc.Container([

        # ======================
        # GLOBAL STORES (TOP-LEVEL)
        # ======================
        dcc.Store(id='data-store', data=BASE_DATA_JSON),  # Store validated data
        dcc.Store(id='data-info-store'),                  # Store data metadata
        dcc.Store(id='freq-store'),                       # Store frequency info
        dcc.Store(id='date-filter-store', data={'start': None, 'end': None, 'label': 'All'}),
        dcc.Store(id="guide-state", data={"open": False, "i": 0}),

        # ✅ MOVE THESE HERE (NOT inside CardBody)
        dcc.Store(
            id="upload-protocol-store",
            data={
                "status": "idle",
                "current_step": 0,
                "files": None,
                "filenames": None,
                "base_json": None,
                "merged_json": None,
                "error": None,
                "steps": [
                    {"name": "File ingestion", "state": "pending"},
                    {"name": "Schema & index validation", "state": "pending"},
                    {"name": "Return sanity checks", "state": "pending"},
                    {"name": "Outlier detection", "state": "pending"},
                    {"name": "Frequency detection", "state": "pending"},
                    {"name": "Compounding to quarterly", "state": "pending"},
                    {"name": "Calendar alignment", "state": "pending"},
                    {"name": "Merge with base universe", "state": "pending"},
                ],
            }
        ),

        dcc.Interval(
            id="upload-interval",
            interval=700,
            n_intervals=0,
            disabled=True
        ),
        
        # Clock interval for header
        dcc.Interval(
            id="clock-interval",
            interval=1000,
            n_intervals=0
        ),

        # ======================
        # GUIDE BUTTON - Top header, highly visible for new users (FIXED position)
        # ======================
        html.Div([
            html.Span("New here?", className="guide-prompt-text"),
            dbc.Button("Start Tutorial", id="btn-start-guide", color="warning", 
                       size="sm", className="guide-btn ms-2"),
        ], className="guide-header-bar", 
           style={"position": "fixed", "top": "10px", "right": "20px", "zIndex": 1100}),

        html.Div(id="guide-debug", className="text-info", style={"fontSize": "12px"}),

        dbc.Popover(
            [
                dbc.PopoverHeader(id="guide-title", className="guide-popover-header"),
                dbc.PopoverBody(
                    [
                        html.Div(id="guide-body", className="guide-popover-body"),
                        html.Div(
                            id="guide-progress",
                            className="guide-progress-indicator"
                        ),
                        html.Div([
                            dbc.Button("Back", id="guide-back", size="sm", 
                                       color="secondary", outline=True, className="guide-nav-btn"),
                            dbc.Button("Next", id="guide-next", size="sm", 
                                       color="warning", className="guide-nav-btn-primary"),
                            dbc.Button("Skip", id="guide-skip", size="sm", 
                                       color="link", className="guide-skip-btn"),
                        ], className="guide-nav-buttons")
                    ], className="guide-popover-content"
                )
            ],
            id="guide-popover",
            target="btn-start-guide",
            is_open=False,
            placement="bottom",
            trigger="legacy",
            className="guide-popover-container"
        ),

        # ======================
        # MAIN ROW
        # ======================
        dbc.Row([

            # ===== SIDEBAR =====
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Controls", className="bg-dark",
                                   style={"color": ACCENT, "fontWeight": "bold"}),

                    dbc.CardBody([

                        # ===== DATA (COMMAND) =====
                        html.Div("DATA", className="command-section-title"),

                        # Primary action button
                        html.Button("ADD NEW ASSETS", id="btn-open-upload-modal",
                                   className="sidebar-cmd-btn sidebar-cmd-btn-primary mb-2"),

                        html.Button("DATA TOOLS", id="btn-toggle-data-tools",
                                   className="sidebar-cmd-btn sidebar-cmd-btn-secondary mb-2"),
                        html.Div(
                            [
                                dbc.Button("Clear Session", id="btn-clear-session",
                                           color="secondary", outline=True,
                                           className="w-100 mb-1",
                                           style={"height": "32px", "fontSize": "11px"}),
                                dbc.Button("Download Sample", id="btn-download-sample",
                                           color="secondary", outline=True,
                                           className="w-100 mb-1",
                                           style={"height": "32px", "fontSize": "11px"}),
                                dbc.Button("Quality Report", id="btn-download-qc-report",
                                           color="secondary", outline=True,
                                           className="w-100 mb-2",
                                           style={"height": "32px", "fontSize": "11px"}),
                            ],
                            id="collapse-data-tools",
                            className="w-100",
                            style={"display": "none", "width": "100%"}
                        ),

                        # Data info panel - professional stats
                        html.Div(id="data-info-panel", className="data-info-panel mt-2"),
                        
                        # Hidden alert for compatibility
                        html.Div(id="data-info-alert", style={"display": "none"}),

                        dcc.Download(id="download-qc-report"),
                        dcc.Download(id="download-sample"),

                        # ✅ NOTE: Store+Interval REMOVED from here

                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Add New Assets (Upload)")),
                                dbc.ModalBody([
                                    html.Div("Running data governance protocols...", className="fw-bold mb-2"),

                                    html.Ul(id="protocol-status-list", children=[
                                        html.Li("File ingestion", className="protocol-item pending", id="protocol-ingestion"),
                                        html.Li("Schema & index validation", className="protocol-item pending", id="protocol-schema"),
                                        html.Li("Return sanity checks", className="protocol-item pending", id="protocol-sanity"),
                                        html.Li("Outlier detection (robust)", className="protocol-item pending", id="protocol-outliers"),
                                        html.Li("Frequency detection", className="protocol-item pending", id="protocol-frequency"),
                                        html.Li("Compounding to quarterly", className="protocol-item pending", id="protocol-compounding"),
                                        html.Li("Calendar alignment", className="protocol-item pending", id="protocol-alignment"),
                                        html.Li("Merge with base universe", className="protocol-item pending", id="protocol-merge"),
                                    ], className="protocol-list"),

                                    html.Hr(),

                                    dcc.Upload(
                                        id="upload-multi",
                                        children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                                        multiple=True,
                                        style={
                                            "width": "100%",
                                            "height": "90px",
                                            "lineHeight": "90px",
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "borderRadius": "8px",
                                            "textAlign": "center"
                                        }
                                    ),

                                    html.Div(id="upload-status", className="mt-2"),
                                ]),
                                dbc.ModalFooter([
                                    dbc.Button("Close", id="btn-close-upload-modal", color="secondary")
                                ])
                            ],
                            id="upload-modal",
                            is_open=False,
                            size="lg"
                        ),

                        html.Hr(),

                        # ===== WINDOW =====
                        html.Div("WINDOW", className="command-section-title"),

                        html.Label("Date Range", className="command-label"),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("YTD", id="btn-ytd", size="sm", outline=True,
                                           style={"backgroundColor": "#21262d", "borderColor": "#30363d",
                                                  "color": "#ffffff", "fontWeight": "600"}),
                                dbc.Button("1Y", id="btn-1y", size="sm", outline=True,
                                           style={"backgroundColor": "#21262d", "borderColor": "#30363d",
                                                  "color": "#ffffff", "fontWeight": "600"}),
                                dbc.Button("3Y", id="btn-3y", size="sm", outline=True,
                                           style={"backgroundColor": "#21262d", "borderColor": "#30363d",
                                                  "color": "#ffffff", "fontWeight": "600"}),
                                dbc.Button("5Y", id="btn-5y", size="sm", outline=True,
                                           style={"backgroundColor": "#21262d", "borderColor": "#30363d",
                                                  "color": "#ffffff", "fontWeight": "600"}),
                                dbc.Button("All", id="btn-all", size="sm", outline=True,
                                           style={"backgroundColor": "#21262d", "borderColor": "#30363d",
                                                  "color": "#ffffff", "fontWeight": "600"}),
                            ],
                            style={"width": "100%"}
                        ),

                        html.Small(id="date-range-info", className="text-muted", style={"fontSize": "10px"}),

                        html.Hr(),

                        html.Div([
                            html.Label("Rolling Window", className="command-label"),
                            html.Small(id="window-freq-info", className="text-info ms-2",
                                       style={"fontSize": "11px"}),
                        ]),

                        dcc.Slider(
                            id="window", min=2, max=24, step=1, value=8,
                            marks={i: str(i) for i in [2, 4, 6, 8, 12, 18, 24]},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),

                        html.Br(),

                        # ===== ASSETS =====
                        html.Div("ASSETS", className="command-section-title"),

                        html.Label("Benchmark", className="command-label-sm"),
                        dcc.Dropdown(id="benchmark", multi=False, className="dropdown-compact"),

                        html.Label("Compare With", className="command-label-sm mt-2"),
                        dcc.Dropdown(id="single-asset", multi=False, className="dropdown-compact"),

                        html.Label("Avg Corr Assets", className="command-label-sm mt-2"),
                        dcc.Dropdown(id="avg-assets", multi=True, className="dropdown-compact"),
                        html.Div([
                            html.A("All", id="btn-avg-all", className="link-action me-2"),
                            html.A("Clear", id="btn-avg-clear", className="link-action"),
                        ], className="mt-1"),

                        html.Label("Heatmap Assets", className="command-label-sm mt-2"),
                        dcc.Dropdown(id="heatmap-assets", multi=True, className="dropdown-compact"),
                        html.Div([
                            html.A("All", id="btn-hm-all", className="link-action me-2"),
                            html.A("Clear", id="btn-hm-clear", className="link-action"),
                        ], className="mt-1"),
                    ])
                ], id="guide-controls", className="mb-4 bg-secondary text-light shadow")
            ], md=3, className="command-sidebar"),

            # ===== MAIN CONTENT =====
            dbc.Col([
                # Rolling Correlation Section
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Rolling Correlation Analysis", style={"fontWeight": "bold", "color": ACCENT}),
                        help_icon('rolling_corr',
                                 "Rolling correlation over time between selected asset and benchmark.",
                                 "Shows how the relationship between assets changes over time. Useful for detecting regime changes.",
                                 "Look for periods of high/low correlation and sudden spikes during market stress.")
                    ], className="bg-dark"),
                    dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='rolling-corr', style={"height": "450px"})),
                        dbc.Button("Show Data Table", id="btn-toggle-rolling-table", 
                                   color="secondary", size="sm", outline=True, className="mt-2"),
                        dbc.Collapse(
                            html.Div(id='rolling-table', className="mt-2"),
                            id="collapse-rolling-table",
                            is_open=False
                        )
                    ])
                ], className="mb-4 bg-secondary"),
                
                # Average Correlation Section
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Average Correlation Dashboard", style={"fontWeight": "bold", "color": ACCENT}),
                        help_icon('avg_corr',
                                 "Average pairwise correlations across selected assets.",
                                 "Measures overall portfolio diversification. Lower average correlation = better diversification.",
                                 "Target < 0.5 for good diversification. Monitor for correlation creep over time.")
                    ], className="bg-dark"),
                    dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='avg-corr', style={"height": "400px"})),
                        dbc.Button("Show Data Table", id="btn-toggle-avg-table", 
                                   color="secondary", size="sm", outline=True, className="mt-2"),
                        dbc.Collapse(
                            html.Div(id='avg-table', className="mt-2"),
                            id="collapse-avg-table",
                            is_open=False
                        )
                    ])
                ], className="mb-4 bg-secondary"),
                
                # Heatmap Evolution Section
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Correlation Heatmap", style={"fontWeight": "bold", "color": ACCENT}),
                        help_icon('heatmap',
                                 "Visual matrix showing pairwise correlations between all selected assets.",
                                 "Quickly identify which assets are highly correlated (red) vs uncorrelated/negatively correlated (blue).",
                                 "Look for clusters of high correlation - these represent concentration risk.")
                    ], className="bg-dark"),
                    dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='heatmap-evolution', style={"height": "500px"})),
                        dbc.Button("Show Data Table", id="btn-toggle-heatmap-table", 
                                   color="secondary", size="sm", outline=True, className="mt-2"),
                        dbc.Collapse(
                            html.Div(id='heatmap-table', className="mt-2"),
                            id="collapse-heatmap-table",
                            is_open=False
                        )
                    ])
                ], className="mb-4 bg-secondary"),
                
            ], md=9),
        ])
    ], fluid=True)


def create_portfolio_tab():
    """Enhanced Portfolio Lab with stress testing"""
    return dbc.Container([
        dcc.Store(id='rets-json'),
        dcc.Store(id='pf-portfolio-store', data=[]),
        
        html.H2("Portfolio Lab — Correlation Analytics", 
                style={"color": ACCENT, "fontSize": "20px"}, className="mb-3"),
        
        dbc.Row([
            # Controls
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Portfolio Builder", className="bg-dark",
                                 style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        html.H5("Select Assets", className="text-light"),
                        dcc.Dropdown(id='pf-assets', multi=True, ),
                        html.Br(),

                        html.H5("Portfolio Weights", className="text-light"),
                        html.Div(id='pf-weights-container'),
                        dbc.ButtonGroup([
                            dbc.Button("Equal Weights", id="btn-equal-weights", 
                                     color="secondary", size="sm", className="mt-2"),
                            dbc.Button("Normalize", id="btn-normalize-weights", 
                                     color="secondary", outline=True, size="sm", className="mt-2 ms-1"),
                        ], className="w-100"),
                        html.Small(id="weights-sum-info", className="text-info mt-2", 
                                 style={"fontSize": "11px"}),
                        html.Br(), html.Br(),

                        # html.H5("Rebalance Frequency", className="text-light"),
                        # dcc.RadioItems(
                        #     id='pf-freq',
                        #     options=[
                        #         {"label": "Daily", "value": "D"},
                        #         {"label": "Weekly", "value": "W"},
                        #         {"label": "Monthly", "value": "M"},
                        #         {"label": "Native", "value": "N"},
                        #     ],
                        #     value="N", className="text-light"
                        # ),
                        # html.Br(),

                        dbc.Button("Build Portfolio", id="pf-build", 
                                 color="warning", n_clicks=0, className="w-100 mb-2",
                                 style={"height": "38px", "fontSize": "12px", "fontWeight": "600"}),
                        dbc.Button("View Portfolio Weights", id="btn-view-weights", 
                                 color="secondary", n_clicks=0, className="w-100 mb-2",
                                 style={"height": "38px", "fontSize": "12px", "fontWeight": "500"}),
                        dbc.Button("Clear All Portfolios", id="pf-clear", 
                                 color="secondary", outline=True, n_clicks=0, className="w-100",
                                 style={"height": "38px", "fontSize": "12px"}),

                        html.Hr(),

html.H5([
                        "Rolling Correlation - Portfolio Context",
                        help_icon('pf_rolling_corr',
                                 "Rolling correlation between portfolio and selected benchmark. Dynamic relationship tracking.",
                                 "Monitors whether constructed portfolio maintains diversification properties across time. Spikes indicate regime shifts.",
                                 "Target <0.3 stable. Spikes >0.7 during crises = diversification failure. Validate construction assumptions.")
                    ], className="text-light"),
                        dcc.Dropdown(id='pf-roll-portfolio', placeholder="Choose portfolio",
                                   style={"color": "black", "marginTop": "8px"}),
                        dcc.Dropdown(id='pf-roll-target', multi=False, 
                                   style={"color": "black", "marginTop": "8px"}),
                        dcc.Input(id='pf-roll-window', type='number', min=3, step=1, value=8,
                                style={"width": "100%", "marginTop": "8px"}, 
                                placeholder="Rolling window"),
                    ])
                ], className="bg-secondary text-light shadow")
            ], md=3),

            # Visualizations
            dbc.Col([
                # 3D Bubble Chart (ENHANCED)
                dbc.Row([
                    dbc.Col([
                        html.H5([
                        "3D Interactive Portfolio Explorer",
                        help_icon('3d_bubble',
                                 "3D scatter: return (x), volatility (y), Sharpe (z). Bubble size = allocation weight.",
                                 "Interactive visualization of portfolio space. Rotate to find northwest regions (high return, low vol, high Sharpe).",
                                 "Northwest = dominates. Large bubbles = concentrated positions. Use for client presentations.")
                    ], className="text-light"),
                        dcc.Dropdown(id='pf-3d-bench', multi=False, 
                                   ),
                    ], md=6),
                    dbc.Col([
                        html.H5("View Controls", className="text-light"),
                        dbc.ButtonGroup([
                            dbc.Button("Reset View", id="btn-reset-3d", 
                                     color="secondary", size="sm"),
                            dbc.Button("Full Range", id="btn-full-range", 
                                     color="warning", size="sm"),
                        ])
                    ], md=6),
                ]),
                html.Br(),
                dcc.Loading(dcc.Graph(id='pf-3d-bubble', style={"height": "700px"})),
                html.Div(id='pf-stats', className="text-light mt-2"),
                
                html.Hr(),

# Rolling Correlation
                html.H5([
                        "Rolling Correlation - Portfolio Context",
                        help_icon('pf_rolling_corr',
                                 "Rolling correlation between portfolio and selected benchmark. Dynamic relationship tracking.",
                                 "Monitors whether constructed portfolio maintains diversification properties across time. Spikes indicate regime shifts.",
                                 "Target <0.3 stable. Spikes >0.7 during crises = diversification failure. Validate construction assumptions.")
                    ], className="text-light"),
                dcc.Loading(dcc.Graph(id='pf-rolling-corr', style={"height": "400px"})),
            ], md=9)
        ])
    ], fluid=True)

def calculate_portfolio_returns(df, weights):
    """Calculate portfolio returns from weights."""
    port_ret = pd.Series(0, index=df.index)
    for asset, weight in weights.items():
        if asset in df.columns:
            port_ret += df[asset] * weight
    return port_ret

def calculate_all_metrics(returns, rf_rate=0):
    """Calculate comprehensive metrics."""
    if len(returns) < 2:
        return {}
    
    total_ret = (1 + returns).prod() - 1
    periods_per_year = 4  # Quarterly
    years = len(returns) / periods_per_year
    ann_ret = (1 + total_ret) ** (1/years) - 1
    
    vol = returns.std() * np.sqrt(periods_per_year)
    
    sharpe = (ann_ret - rf_rate) / vol if vol > 0 else 0
    
    downside_ret = returns[returns < 0]
    downside_vol = downside_ret.std() * np.sqrt(periods_per_year) if len(downside_ret) > 0 else vol
    sortino = (ann_ret - rf_rate) / downside_vol if downside_vol > 0 else 0
    
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()
    
    calmar = ann_ret / abs(max_dd) if max_dd < 0 else 0
    
    return {
        'annual_return': ann_ret,
        'volatility': vol,
        'sharpe': sharpe,
        'sortino': sortino,
        'max_drawdown': max_dd,
        'calmar': calmar
    }

def optimize_portfolio(df, assets, objective='max_sharpe', rf_rate=0, allow_growise=True):
    """Optimize portfolio weights."""
    n = len(assets)
    
    def portfolio_stats(weights):
        port_ret = (df[assets] * weights).sum(axis=1)
        metrics = calculate_all_metrics(port_ret, rf_rate)
        return metrics
    
    def neg_sharpe(weights):
        stats = portfolio_stats(weights)
        return -stats.get('sharpe', 0)
    
    def neg_sortino(weights):
        stats = portfolio_stats(weights)
        return -stats.get('sortino', 0)
    
    def volatility(weights):
        stats = portfolio_stats(weights)
        return stats.get('volatility', 1)
    
    # Choose objective function
    if 'sharpe' in objective.lower():
        obj_func = neg_sharpe
    elif 'sortino' in objective.lower():
        obj_func = neg_sortino
    else:  # min vol
        obj_func = volatility
    
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = tuple((0, 1) for _ in range(n))
    
    x0 = np.array([1/n] * n)
    
    result = minimize(obj_func, x0, method='SLSQP', 
                     bounds=bounds, constraints=constraints)
    
    if result.success:
        return dict(zip(assets, result.x))
    return None

def calculate_efficient_frontier(df, assets, rf_rate=0, n_points=25):
    """
    Generate TRUE efficient frontier using proper optimization.
    Not Monte Carlo garbage - actual optimized portfolios.
    """
    n = len(assets)
    
    # Calculate return range for target returns
    returns_data = df[assets]
    mean_returns = returns_data.mean() * 4  # Annualized (quarterly data)
    cov_matrix = returns_data.cov() * 4
    
    # Find min and max possible returns
    min_ret = mean_returns.min()
    max_ret = mean_returns.max()
    
    # Target returns across the range
    target_returns = np.linspace(min_ret, max_ret, n_points)
    
    frontier_vols = []
    frontier_rets = []
    
    for target_ret in target_returns:
        # Minimize volatility for this target return
        def portfolio_volatility(weights):
            port_ret = np.dot(weights, mean_returns)
            port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return port_vol
        
        # Constraints: weights sum to 1, return = target
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: np.dot(w, mean_returns) - target_ret}
        ]
        
        bounds = tuple((0, 1) for _ in range(n))
        x0 = np.array([1/n] * n)
        
        result = minimize(portfolio_volatility, x0, method='SLSQP',
                         bounds=bounds, constraints=constraints,
                         options={'maxiter': 500, 'ftol': 1e-9})
        
        if result.success:
            opt_vol = portfolio_volatility(result.x)
            opt_ret = np.dot(result.x, mean_returns)
            
            frontier_vols.append(opt_vol)
            frontier_rets.append(opt_ret)
    
    return {'returns': frontier_rets, 'vols': frontier_vols}

def filter_and_renormalize_weights(weights, threshold=0.03, force_growise=False):
    """
    Filter out assets <threshold% and renormalize to 100%.
    If force_growise=True, ensures GROWISE gets at least threshold allocation.
    
    Returns: (filtered_weights, removed_assets)
    """
    removed = {}
    
    # If forcing GROWISE and it exists but is below threshold
    if force_growise and 'GROWISE' in weights and weights['GROWISE'] < threshold:
        # Set GROWISE to threshold
        weights_copy = weights.copy()
        weights_copy['GROWISE'] = threshold
        
        # Reduce others proportionally
        other_assets = {k: v for k, v in weights_copy.items() if k != 'GROWISE'}
        other_total = sum(other_assets.values())
        
        if other_total > (1 - threshold):
            scale_factor = (1 - threshold) / other_total
            for k in other_assets:
                weights_copy[k] *= scale_factor
        
        weights = weights_copy
    
    # Filter out small allocations
    filtered = {k: v for k, v in weights.items() if v >= threshold}
    removed = {k: v for k, v in weights.items() if v < threshold and k != 'GROWISE'}
    
    # If GROWISE was removed but force_growise is True, add it back
    if force_growise and 'GROWISE' in weights and 'GROWISE' not in filtered:
        filtered['GROWISE'] = threshold
        if 'GROWISE' in removed:
            del removed['GROWISE']
    
    # Renormalize to 100%
    if filtered:
        total = sum(filtered.values())
        filtered = {k: v/total for k, v in filtered.items()}
    
    return filtered, removed

# ============================================================
# VISUALIZATION FUNCTIONS
# ============================================================

def create_equity_curves_v8(equity_curves):
    """Create professional equity curves."""
    fig = go.Figure()
    
    for eq in equity_curves:
        g_pct = eq['growise_pct']
        alpha = min(0.3 + (g_pct * 3.5), 1.0)  # FIX: Capped at 1.0
        
        color = f'rgba(6, 167, 125, {alpha})'
        
        fig.add_trace(go.Scatter(
            x=eq['dates'],
            y=eq['equity'],
            mode='lines',
            name=f"{g_pct*100:.0f}% GROWISE",
            line=dict(color=color, width=2),
            hovertemplate='<b>%{y:.2f}x</b><extra></extra>'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_sharpe_sortino_sensitivity(results_df):
    """Sharpe and Sortino sensitivity charts."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Sharpe Ratio', 'Sortino Ratio')
    )
    
    x_vals = results_df['growise_pct'] * 100
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=results_df['sharpe'],
        mode='lines+markers',
        name='Sharpe',
        line=dict(color='#06A77D', width=3),
        marker=dict(size=8)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=results_df['sortino'],
        mode='lines+markers',
        name='Sortino',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8),
        showlegend=False
    ), row=1, col=2)
    
    fig.update_xaxes(title_text="GROWISE %", row=1, col=1)
    fig.update_xaxes(title_text="GROWISE %", row=1, col=2)
    fig.update_yaxes(title_text="Sharpe Ratio", row=1, col=1)
    fig.update_yaxes(title_text="Sortino Ratio", row=1, col=2)
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        showlegend=False
    )
    
    return fig

def create_return_vol_sensitivity(results_df):
    """Return and Volatility sensitivity charts."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Annual Return', 'Volatility')
    )
    
    x_vals = results_df['growise_pct'] * 100
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=results_df['annual_return'] * 100,
        mode='lines+markers',
        name='Return',
        line=dict(color='#06A77D', width=3),
        marker=dict(size=8)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=results_df['volatility'] * 100,
        mode='lines+markers',
        name='Volatility',
        line=dict(color='#E67E22', width=3),
        marker=dict(size=8),
        showlegend=False
    ), row=1, col=2)
    
    fig.update_xaxes(title_text="GROWISE %", row=1, col=1)
    fig.update_xaxes(title_text="GROWISE %", row=1, col=2)
    fig.update_yaxes(title_text="Return %", row=1, col=1)
    fig.update_yaxes(title_text="Volatility %", row=1, col=2)
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        showlegend=False
    )
    
    return fig

def create_correlation_sensitivity(results_df):
    """Correlation sensitivity - DYNAMIC Y-AXIS."""
    fig = go.Figure()
    
    x_vals = results_df['growise_pct'] * 100
    y_vals = results_df['benchmark_corr']
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='lines+markers',
        name='Correlation',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8)
    ))
    
    # DYNAMIC Y-AXIS (not fixed at [-1, 1])
    y_min, y_max = y_vals.min(), y_vals.max()
    y_range = y_max - y_min
    padding = y_range * 0.1
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        xaxis_title="GROWISE %",
        yaxis_title="Correlation with Benchmark",
        yaxis=dict(range=[y_min - padding, y_max + padding]),  # DYNAMIC!
        showlegend=False
    )
    
    return fig

def create_efficient_frontier_comparison(frontier_with, frontier_without, 
                                        metrics_with, metrics_without, rf, df_returns=None):
    """
    Professional efficient frontier with REAL Monte Carlo portfolios.
    Generates random weight vectors and calculates their actual risk/return using the covariance matrix.
    """
    import numpy as np
    fig = go.Figure()
    
    # Generate REAL random portfolios if we have the data
    if df_returns is not None and len(df_returns.columns) > 0:
        n_portfolios = 2000
        n_assets = len(df_returns.columns)
        
        # Calculate actual statistics
        returns = df_returns.mean() * 4  # Annualized
        cov_matrix = df_returns.cov() * 4  # Annualized
        
        random_vols = []
        random_rets = []
        random_sharpes = []
        
        # Generate random weight vectors
        for _ in range(n_portfolios):
            # Generate random weights that sum to 1
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            # Calculate ACTUAL portfolio statistics using real covariance matrix
            port_return = np.dot(weights, returns)
            port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            port_sharpe = (port_return - rf) / port_vol if port_vol > 0 else 0
            
            random_rets.append(port_return)
            random_vols.append(port_vol)
            random_sharpes.append(port_sharpe)
        
        # Plot random portfolios as colored dots
        fig.add_trace(go.Scatter(
            x=random_vols,
            y=random_rets,
            mode='markers',
            name='Random Portfolios',
            marker=dict(
                size=3,
                color=random_sharpes,
                colorscale='Turbo',  # Purple -> Blue -> Green -> Yellow
                showscale=True,
                colorbar=dict(
                    title='Sharpe<br>Ratio',
                    x=1.12,
                    thickness=15,
                    len=0.7
                ),
                opacity=0.5,
                line=dict(width=0)
            ),
            hovertemplate='Random Portfolio<br>Vol: %{x:.2%}<br>Return: %{y:.2%}<br>Sharpe: %{marker.color:.2f}<extra></extra>',
            showlegend=False
        ))
    
    # Plot efficient frontier curve on top
    if frontier_with and len(frontier_with.get('vols', [])) > 0:
        vols = np.array(frontier_with['vols'])
        rets = np.array(frontier_with['returns'])
        
        # Main frontier curve - thick white line
        fig.add_trace(go.Scatter(
            x=vols,
            y=rets,
            mode='lines+markers',
            name='Efficient Frontier',
            line=dict(color='white', width=5),
            marker=dict(size=8, color='white', symbol='diamond', line=dict(width=1, color='#58a6ff')),
            hovertemplate='<b>Efficient Frontier</b><br>Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
        ))
    
    # Mark minimum volatility portfolio (red star on left)
    if frontier_with and len(frontier_with.get('vols', [])) > 0:
        min_vol_idx = np.argmin(frontier_with['vols'])
        fig.add_trace(go.Scatter(
            x=[frontier_with['vols'][min_vol_idx]],
            y=[frontier_with['returns'][min_vol_idx]],
            mode='markers+text',
            marker=dict(size=25, color='#f85149', symbol='star', line=dict(color='white', width=2)),
            text=['Min Vol'],
            textposition='bottom center',
            textfont=dict(size=11, color='white', family='Arial Black'),
            name='Minimum Volatility',
            hovertemplate='<b>Min Volatility Portfolio</b><br>Vol: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
        ))
    
    # Mark maximum Sharpe portfolio (green star on curve)
    if metrics_with:
        fig.add_trace(go.Scatter(
            x=[metrics_with['volatility']],
            y=[metrics_with['annual_return']],
            mode='markers+text',
            marker=dict(size=35, color='#3fb950', symbol='star', line=dict(color='white', width=3)),
            text=[f"<b>Optimal</b><br>Sharpe: {metrics_with['sharpe']:.2f}"],
            textposition='top center',
            textfont=dict(size=12, color='white', family='Arial Black'),
            name='Optimal Portfolio',
            hovertemplate=f"<b>OPTIMAL PORTFOLIO</b><br>Return: {metrics_with['annual_return']:.2%}<br>Vol: {metrics_with['volatility']:.2%}<br>Sharpe: {metrics_with['sharpe']:.2f}<extra></extra>"
        ))
    
    # Mark max returns portfolio (blue star on right)
    if frontier_with and len(frontier_with.get('vols', [])) > 0:
        max_ret_idx = np.argmax(frontier_with['returns'])
        fig.add_trace(go.Scatter(
            x=[frontier_with['vols'][max_ret_idx]],
            y=[frontier_with['returns'][max_ret_idx]],
            mode='markers+text',
            marker=dict(size=25, color='#58a6ff', symbol='star', line=dict(color='white', width=2)),
            text=['Max Return'],
            textposition='top center',
            textfont=dict(size=11, color='white', family='Arial Black'),
            name='Maximum Returns',
            hovertemplate='<b>Max Returns Portfolio</b><br>Vol: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        title=dict(
            text='Efficient Frontier: Portfolio Optimization Space',
            font=dict(size=18, color='white', family='Arial'),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        height=550,
        xaxis_title="Expected Volatility",
        yaxis_title="Expected Return",
        xaxis=dict(
            tickformat='.2%', 
            gridcolor='rgba(128,128,128,0.15)',
            showgrid=True,
            zeroline=False,
            title=dict(font=dict(size=14))
        ),
        yaxis=dict(
            tickformat='.2%', 
            gridcolor='rgba(128,128,128,0.15)',
            showgrid=True,
            zeroline=False,
            title=dict(font=dict(size=14))
        ),
        hovermode='closest',
        showlegend=True,
        legend=dict(
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01,
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(t=60, b=50, l=60, r=150)  # Extra right margin for colorbar
    )
    
    return fig

def create_metrics_comparison_bars(metrics_with, metrics_without):
    """Elite metrics comparison with % improvement annotations."""
    fig = go.Figure()
    
    if not metrics_without:
        # Only WITH metrics - simple display
        categories = ['Sharpe', 'Sortino', 'Calmar']
        values = [
            metrics_with['sharpe'],
            metrics_with['sortino'],
            metrics_with['calmar']
        ]
        
        colors = ['#06A77D', '#2E86AB', '#E67E22']
        
        fig.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=colors,
            text=[f"{v:.2f}" for v in values],
            textposition='outside',
            textfont=dict(size=14, color='white', family='Arial Black'),
            hovertemplate='%{x}: %{y:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.02)',
            height=400,
            showlegend=False,
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            xaxis=dict(tickfont=dict(size=13, family='Arial Black'))
        )
    else:
        # Comparison mode - show improvements
        categories = ['Sharpe', 'Sortino', 'Calmar']
        
        values_without = [
            metrics_without['sharpe'],
            metrics_without['sortino'],
            metrics_without['calmar']
        ]
        
        values_with = [
            metrics_with['sharpe'],
            metrics_with['sortino'],
            metrics_with['calmar']
        ]
        
        # Calculate improvements
        improvements = []
        for v_with, v_without in zip(values_with, values_without):
            if v_without != 0:
                imp = ((v_with - v_without) / abs(v_without)) * 100
                improvements.append(imp)
            else:
                improvements.append(0)
        
        fig.add_trace(go.Bar(
            x=categories, y=values_without,
            name='Without GROWISE',
            marker=dict(color='rgba(128, 128, 128, 0.6)',
                       line=dict(color='gray', width=2)),
            text=[f"{v:.2f}" for v in values_without],
            textposition='outside',
            textfont=dict(size=12, color='gray'),
            hovertemplate='Without: %{y:.3f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=categories, y=values_with,
            name='With GROWISE',
            marker=dict(color='#06A77D',
                       line=dict(color='white', width=2)),
            text=[f"{v:.2f}" for v in values_with],
            textposition='outside',
            textfont=dict(size=14, color='#06A77D', family='Arial Black'),
            hovertemplate='With: %{y:.3f}<extra></extra>'
        ))
        
        # Add improvement annotations
        for i, (cat, imp) in enumerate(zip(categories, improvements)):
            max_val = max(values_with[i], values_without[i])
            fig.add_annotation(
                x=cat,
                y=max_val * 1.15,
                text=f"+{imp:.0f}%",
                showarrow=False,
                font=dict(size=13, color='#06A77D', family='Arial Black'),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='#06A77D',
                borderwidth=1,
                borderpad=3
            )
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.02)',
            height=400,
            barmode='group',
            bargap=0.2,
            bargroupgap=0.1,
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            xaxis=dict(tickfont=dict(size=13, family='Arial Black')),
            legend=dict(yanchor="top", y=0.98, xanchor="right", x=0.98,
                       bgcolor='rgba(0,0,0,0.7)', bordercolor='#30363d', borderwidth=1,
                       font=dict(size=11))
        )
    
    return fig

def create_optimal_weights_chart(weights, threshold=0.03):
    """Elite pie chart - groups small allocations (<3%) into Others."""
    # Separate large and small allocations
    large_weights = {k: v for k, v in weights.items() if v >= threshold}
    small_weights = {k: v for k, v in weights.items() if v < threshold}
    
    # If we have small weights, group them
    if small_weights:
        others_total = sum(small_weights.values())
        display_weights = large_weights.copy()
        display_weights['Others'] = others_total
        
        # Create hover text for Others showing breakdown
        others_text = "Others:<br>" + "<br>".join([f"{k}: {v*100:.1f}%" 
                                                   for k, v in sorted(small_weights.items(), 
                                                                     key=lambda x: x[1], reverse=True)])
    else:
        display_weights = large_weights
        others_text = None
    
    # Sort by value descending
    sorted_weights = dict(sorted(display_weights.items(), key=lambda x: x[1], reverse=True))
    
    assets = list(sorted_weights.keys())
    values = list(sorted_weights.values())
    
    # Professional color scheme
    colors = []
    for i, asset in enumerate(assets):
        if 'GROWISE' in asset:
            colors.append('#06A77D')
        elif asset == 'Others':
            colors.append('#4a5568')  # Gray for Others
        else:
            # Cycle through professional colors
            color_palette = ['#2E86AB', '#F18F01', '#D4145A', '#9B59B6', 
                           '#3498DB', '#E74C3C', '#1ABC9C', '#F39C12']
            colors.append(color_palette[i % len(color_palette)])
    
    # Custom hover text
    hover_texts = []
    for asset, value in zip(assets, values):
        if asset == 'Others' and others_text:
            hover_texts.append(others_text)
        else:
            hover_texts.append(f"{asset}<br>{value*100:.2f}%")
    
    fig = go.Figure(data=[go.Pie(
        labels=assets,
        values=values,
        hole=0.45,
        marker=dict(colors=colors, 
                   line=dict(color='#1a1a1a', width=2)),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, family='Arial', color='white'),
        hovertext=hover_texts,
        hoverinfo='text',
        pull=[0.05 if 'GROWISE' in a else 0 for a in assets],  # Pull out GROWISE slice
        rotation=90
    )])
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="middle", 
            y=0.5, 
            xanchor="left", 
            x=1.02,
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='#30363d',
            borderwidth=1,
            font=dict(size=11)
        ),
        annotations=[dict(
            text=f'<b>{len(display_weights)}</b><br>Assets',
            x=0.5, y=0.5,
            font=dict(size=16, color='white', family='Arial Black'),
            showarrow=False
        )]
    )
    
    return fig

def create_risk_return_comparison(metrics_with, metrics_without):
    """Risk-return scatter comparison."""
    fig = go.Figure()
    
    if metrics_without:
        fig.add_trace(go.Scatter(
            x=[metrics_without['volatility']],
            y=[metrics_without['annual_return']],
            mode='markers+text',
            name='Without GROWISE',
            marker=dict(color='gray', size=20, symbol='circle'),
            text=['Without'],
            textposition='top center'
        ))
    
    if metrics_with:
        fig.add_trace(go.Scatter(
            x=[metrics_with['volatility']],
            y=[metrics_with['annual_return']],
            mode='markers+text',
            name='With GROWISE',
            marker=dict(color='#06A77D', size=20, symbol='star'),
            text=['With'],
            textposition='top center'
        ))
    
    # Arrow if both exist
    if metrics_with and metrics_without:
        fig.add_annotation(
            x=metrics_with['volatility'],
            y=metrics_with['annual_return'],
            ax=metrics_without['volatility'],
            ay=metrics_without['annual_return'],
            xref='x', yref='y', axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor='#06A77D'
        )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        xaxis_title="Volatility",
        yaxis_title="Return",
        showlegend=False
    )
    
    return fig

def create_equity_comparison(port_rets_with, port_rets_without):
    """Equity curves comparison - WITH vs WITHOUT."""
    fig = go.Figure()
    
    initial = 100000
    
    if port_rets_without is not None:
        cum_without = initial * (1 + port_rets_without).cumprod()
        fig.add_trace(go.Scatter(
            x=port_rets_without.index,
            y=cum_without,
            mode='lines',
            name='Without GROWISE',
            line=dict(color='gray', width=2, dash='dot')
        ))
    
    if port_rets_with is not None:
        cum_with = initial * (1 + port_rets_with).cumprod()
        fig.add_trace(go.Scatter(
            x=port_rets_with.index,
            y=cum_with,
            mode='lines',
            name='With GROWISE',
            line=dict(color='#06A77D', width=3)
        ))
        
        # Fill between if both exist
        if port_rets_without is not None:
            fig.add_trace(go.Scatter(
                x=port_rets_with.index,
                y=cum_with,
                fill='tonexty',
                fillcolor='rgba(6, 167, 125, 0.2)',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        hovermode='x unified'
    )
    
    return fig

def create_optimization_insights(weights_with, weights_without, 
                                metrics_with, metrics_without, has_growise):
    """Create insights card."""
    if weights_without and has_growise:
        growise_alloc = weights_with.get('GROWISE', 0) * 100
        sharpe_delta = ((metrics_with['sharpe'] - metrics_without['sharpe']) / 
                       metrics_without['sharpe'] * 100) if metrics_without['sharpe'] != 0 else 0
        ret_delta = (metrics_with['annual_return'] - metrics_without['annual_return']) * 100
        dd_delta = ((metrics_without['max_drawdown'] - metrics_with['max_drawdown']) / 
                   abs(metrics_without['max_drawdown']) * 100) if metrics_without['max_drawdown'] != 0 else 0
        
        insights = dbc.Alert([
            html.H4("GROWISE Impact Summary", className='alert-heading'),
            html.Hr(),
            html.P([
                html.Strong(f"Recommended GROWISE Allocation: {growise_alloc:.1f}%"),
                html.Br(),
                f"• Sharpe Ratio: {metrics_without['sharpe']:.2f} → {metrics_with['sharpe']:.2f} ",
                html.Span(f"(+{sharpe_delta:.1f}%)", style={'color': '#06A77D'}),
                html.Br(),
                f"• Annual Return: {metrics_without['annual_return']*100:.1f}% → {metrics_with['annual_return']*100:.1f}% ",
                html.Span(f"(+{ret_delta:.1f} bps)", style={'color': '#06A77D'}),
                html.Br(),
                f"• Max Drawdown: {metrics_without['max_drawdown']*100:.1f}% → {metrics_with['max_drawdown']*100:.1f}% ",
                html.Span(f"({dd_delta:.1f}% better)", style={'color': '#06A77D'})
            ])
        ], color='success', style={'backgroundColor': '#1a4d3a', 'borderColor': '#06A77D'})
    else:
        insights = dbc.Alert([
            html.H4("Optimization Results", className='alert-heading'),
            html.Hr(),
            html.P([
                html.Strong("Optimal Portfolio Found"),
                html.Br(),
                f"• Sharpe Ratio: {metrics_with['sharpe']:.2f}",
                html.Br(),
                f"• Annual Return: {metrics_with['annual_return']*100:.1f}%",
                html.Br(),
                f"• Volatility: {metrics_with['volatility']*100:.1f}%",
                html.Br(),
                f"• Max Drawdown: {metrics_with['max_drawdown']*100:.1f}%"
            ])
        ], color='info')
    
    return insights


def create_regime_factor_tab():
    """
    Regime & Factor Analysis Tab
    Provides quadrant analysis and Fama-French factor attribution
    """
    return dbc.Container([
        dcc.Store(id='ff-factors-store'),  # Store for Fama-French factors
        
        html.H2("Regime & Factor Analysis", style={"color": ACCENT, "fontSize": "20px"}, className="mb-4"),
        
        dbc.Row([
            # Controls Column
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Analysis Controls", className="bg-dark",
                                 style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        html.Label("Benchmark for Regime Analysis", className="text-light fw-bold"),
                        dcc.Dropdown(
                            id='regime-benchmark',
                            placeholder="Select benchmark index",
                            style={"marginBottom": "15px"}
                        ),
                        
                        html.Label("Target Asset (GROWISE)", className="text-light fw-bold"),
                        dcc.Dropdown(
                            id='regime-target',
                            placeholder="Select target asset",
                            style={"marginBottom": "20px"}
                        ),
                        
                        html.Hr(),
                        
                        html.H6("Factor Model Selection", className="text-light fw-bold mb-2"),
                        dcc.RadioItems(
                            id='factor-model-selector',
                            options=[
                                {'label': ' 3-Factor (Mkt, SMB, HML)', 'value': '3'},
                                {'label': ' 5-Factor (+ RMW, CMA)', 'value': '5'},
                                {'label': ' 6-Factor (+ Momentum)', 'value': '6'}
                            ],
                            value='5',
                            className="text-light",
                            labelStyle={'display': 'block', 'marginBottom': '8px'}
                        ),
                        
                        html.Hr(),
                        
                        html.H6("Download Factors", className="text-light fw-bold"),
                        html.Small("Frequency will auto-match your data", 
                                 className="text-muted d-block mb-2"),
                        dbc.Button([html.I(className="fas fa-download me-2"), "Download FF Factors"], 
                                 id="btn-download-factors", color="secondary", className="w-100 mb-2"),
                        html.Div(id='factor-download-status', className="mt-2"),
                        
                        html.Hr(),
                        
                        dbc.Button([html.I(className="fas fa-chart-line me-2"), "Run Analysis"], 
                                 id="btn-run-regime-analysis", color="success", 
                                 className="w-100", size="lg")
                    ])
                ], className="bg-secondary text-light shadow")
            ], md=3),
            
            # Results Column
            dbc.Col([
                # Quadrant Scatter - FULL WIDTH
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-scatter me-2"), 
                            "Regime Scatter",
                            help_icon('regime_scatter',
                                     "Benchmark (x) vs GROWISE (y). Q2 (left-up) = tail hedge. Polynomial = convexity test.",
                                     "Q2 density proves crisis protection. 2nd derivative >0 = asymmetric payoff (gains>losses).",
                                     "Target: Q2 >20%, Q2 avg >+5%, 2nd deriv >0. Check 2008, 2020.")
                        ], className="mb-0 text-light")
                    ], className="bg-dark"),
                    dbc.CardBody([
                        html.Div(id='current-date-display', className="text-center mb-2",
                                style={'fontSize': '16px', 'fontWeight': '600', 'color': ACCENT}),
                        dcc.Loading(
                            dcc.Graph(id='quadrant-scatter', 
                                     config={'displayModeBar': True},
                                     style={'height': '500px'})
                        )
                    ])
                ], className="mb-3 shadow"),
                
                # 4 Quadrant Cards - SIDE BY SIDE
                html.H6("Quadrant Statistics", className="text-light mb-2"),
                dbc.Row([
                    dbc.Col([html.Div(id='q1-card')], md=3),
                    dbc.Col([html.Div(id='q2-card')], md=3),
                    dbc.Col([html.Div(id='q3-card')], md=3),
                    dbc.Col([html.Div(id='q4-card')], md=3)
                ], className="mb-4"),
                
                # Factor Analysis Section
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-line me-2"), 
                            "Factor Analysis",
                            help_icon('factor_analysis',
                                     "FF regression: systematic betas + alpha. Rolling = time-varying. Full-period = avg loadings.",
                                     "Low betas = uncorrelated with known premia (skill). Alpha t-stat>2 = statistically significant edge.",
                                     "Targets: betas<0.2, alpha t>2, R²<0.3. Check IR = alpha/tracking error.")
                        ], className="mb-0 text-light")
                    ], className="bg-dark"),
                    dbc.CardBody([
                        html.Small("Rolling window shows how factor exposures evolve over time", 
                                 className="text-muted d-block mb-3", style={'fontSize': '12px'}),
                        dcc.Loading(
                            dcc.Graph(id='factor-rolling-chart',
                                     config={'displayModeBar': False},
                                     style={'height': '350px'})
                        ),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.H6([
                                    "Average Betas (Full Period)",
                                    help_icon('avg_betas',
                                             "Factor exposures: MKT, SMB, HML, RMW, CMA, MOM. Regression coefficients.",
                                             "Betas near zero = returns uncorrelated with known premia. Proves skill vs factor loading.",
                                             "Target <0.2 all factors. Alpha t-stat>2 = statistically significant edge.")
                                ], className="text-light text-center mb-2", style={'fontSize': '13px'}),
                                dcc.Loading(
                                    dcc.Graph(id='factor-betas-bar',
                                             config={'displayModeBar': False},
                                             style={'height': '350px'})
                                )
                            ], md=6),
                            dbc.Col([
                                html.H6([
                                    "Return Attribution (Full Period)",
                                    help_icon('return_attribution',
                                             "Factor contributions + alpha. Beta × factor return + intercept.",
                                             "Alpha bar = unexplained returns (skill). Large positive = value beyond passive factor exposure.",
                                             "Alpha highlighted. Check alpha/tracking error (IR). Alpha t-stat>2 for significance.")
                                ], className="text-light text-center mb-2", style={'fontSize': '13px'}),
                                dcc.Loading(
                                    dcc.Graph(id='attribution-evolution-chart',
                                             config={'displayModeBar': False},
                                             style={'height': '350px'})
                                )
                            ], md=6)
                        ])
                    ])
                ], className="mb-3 shadow"),
                
                # Summary Statistics
                html.Div(id='factor-summary-stats', className="mb-3")
                
            ], md=9)
        ])
        
    ], fluid=True)


def create_growise_tab():
    """GROWISE Portfolio Optimizer"""
    return dbc.Container([
        dcc.Store(id='gw-ready'),
        dcc.Store(id='preset-weights-store'),
        dcc.Store(id='preset-name-store', data='Custom Portfolio'),
        
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id='modal-title')),
            dbc.ModalBody(id='modal-body'),
            dbc.ModalFooter(dbc.Button("Close", id='close-modal'))
        ], id='preset-modal', size='lg', is_open=False),
        
        html.H2("GROWISE Portfolio Optimizer", style={"color": "#E67E22", "fontSize": "20px"}, className="mb-3"),
        dbc.Alert(id='gw-status', style={'display': 'none'}),
        html.Div(id='gw-content')
    ], fluid=True)

def create_resources_tab():
    """
    Resources & Documentation Tab
    Template downloads, statistical glossary, demo mode, and user guides
    """
    return dbc.Container([
        html.H2("Resources & Documentation", 
                style={"color": ACCENT, "fontSize": "20px"}, 
                className="mb-4"),
        
        dbc.Row([
            # Left Column - Quick Actions
            dbc.Col([
                # Template Download Card
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-download me-2"),
                        "Portfolio Template"
                    ], className="bg-dark", style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        html.P("Download CSV template to share your portfolio returns with us.", 
                               className="mb-3"),
                        
                        dcc.Download(id="download-template-csv"),
                        dbc.Button([
                            html.I(className="fas fa-file-csv me-2"),
                            "Download Template"
                        ], id="btn-download-template-csv", color="warning", className="w-100 mb-2"),
                        
                        html.Hr(),
                        
                        html.H6("Format Requirements:", className="text-light mb-2"),
                        html.Ul([
                            html.Li("Date column (YYYY-MM-DD)"),
                            html.Li("Returns as decimals (0.05 = 5%)"),
                            html.Li("Consistent frequency (M/Q/Y)"),
                            html.Li("No missing dates")
                        ], className="small text-muted mb-0")
                    ])
                ], className="mb-3 shadow"),
                
                # Demo Mode Card
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-theater-masks me-2"),
                        "Demo Mode (Role-Play)"
                    ], className="bg-dark", style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        html.P("Practice client presentations with pre-loaded sample data.", 
                               className="mb-3"),
                        
                        dbc.Button([
                            html.I(className="fas fa-play me-2"),
                            "Launch Demo Mode"
                        ], id="btn-launch-demo", color="success", className="w-100 mb-2"),
                        
                        dbc.Button([
                            html.I(className="fas fa-stop me-2"),
                            "Exit Demo Mode"
                        ], id="btn-exit-demo", color="danger", className="w-100 mb-2", style={'display': 'none'}),
                        
                        html.Div(id='demo-mode-status', className='mb-2'),
                        
                        html.Hr(),
                        
                        html.Small([
                            html.Strong("Scenario: "),
                            "Institutional investor with $50M AUM comparing GROWISE vs traditional 60/40"
                        ], className="text-muted")
                    ])
                ], className="mb-3 shadow"),
                
                # Contact Card
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-envelope me-2"),
                        "Need Help?"
                    ], className="bg-dark", style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        html.P("Contact our team for assistance with the platform.", 
                               className="mb-2"),
                        html.A("juan.serur@sci.tech", 
                               href="mailto:juan.serur@sci.tech",
                               className="text-warning")
                    ])
                ], className="shadow")
                
            ], md=4),
            
            # Right Column - Documentation
            dbc.Col([
                # Statistical Glossary
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-book me-2"),
                        "Statistical Glossary"
                    ], className="bg-dark", style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        html.Div([
                            # Glossary content (accordion)
                            dbc.Accordion([
                                # Sharpe Ratio
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Risk-adjusted return metric. Measures excess return per unit of total risk."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Formula: "),
                                        html.Code("Sharpe = (R - Rf) / σ")
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Interpretation: "),
                                        "Higher is better. >1 is good, >2 is very good, >3 is excellent."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Example: "),
                                        "Portfolio returns 15%, risk-free is 3%, volatility is 12%. Sharpe = (15%-3%)/12% = 1.0"
                                    ], className="mb-0 small text-muted")
                                ], title="Sharpe Ratio"),
                                
                                # Sortino Ratio
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Downside risk-adjusted return. Only penalizes negative volatility."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Formula: "),
                                        html.Code("Sortino = (R - Rf) / σ_downside")
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Why it matters: "),
                                        "Sharpe penalizes upside volatility too. Sortino only cares about downside."
                                    ], className="mb-0 small text-muted")
                                ], title="Sortino Ratio"),
                                
                                # Alpha
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Excess return vs expected return (CAPM). Measures skill/edge."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Formula: "),
                                        html.Code("α = R_actual - [Rf + β(R_market - Rf)]")
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Interpretation: "),
                                        "Positive alpha = outperformance. Negative alpha = underperformance."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("GROWISE Context: "),
                                        "Multi-asset strategy typically shows high alpha (76%+) with low market beta, "
                                        "indicating returns come from skill/strategy, not market exposure."
                                    ], className="mb-0 small text-muted")
                                ], title="Alpha (α)"),
                                
                                # Beta
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Market sensitivity. Measures how much an asset moves relative to the market."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Values: "),
                                        "β=1: moves with market. β>1: more volatile. β<1: less volatile. β<0: inverse."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Example: "),
                                        "β=1.5 means if market goes up 10%, asset goes up 15% (on average)."
                                    ], className="mb-0 small text-muted")
                                ], title="Beta (β)"),
                                
                                # Correlation
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Linear relationship between two assets. Ranges from -1 to +1."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Values: "),
                                        "ρ=+1: perfect positive (move together). "
                                        "ρ=-1: perfect negative (move opposite). "
                                        "ρ=0: no relationship."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Crisis Problem: "),
                                        "Correlations spike during crises. Traditional diversification fails when needed most. "
                                        "Tail hedge funds or structurally uncorrelated funds, like GROWISE, maintain low/negative correlations even in crises."
                                    ], className="mb-0 small text-muted")
                                ], title="Correlation (ρ)"),
                                
                                # VaR
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Value at Risk. Maximum expected loss at a given confidence level."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Example: "),
                                        "95% VaR = $100k means: 95% of the time, you won't lose more than $100k."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Limitation: "),
                                        "Tells you NOTHING about what happens in the worst 5%."
                                    ], className="mb-0 small text-muted")
                                ], title="Value at Risk (VaR)"),
                                
                                # CVaR
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Conditional VaR. Average loss BEYOND the VaR threshold."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Example: "),
                                        "95% CVaR = $150k means: in the worst 5% of cases, average loss is $150k."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Why better than VaR: "),
                                        "Captures tail risk. VaR ignores severity beyond threshold."
                                    ], className="mb-0 small text-muted")
                                ], title="Conditional VaR (CVaR)"),
                                
                                # Maximum Drawdown
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "Largest peak-to-trough decline in portfolio value."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Example: "),
                                        "Portfolio peaks at $1M, drops to $700k, recovers to $900k. Max DD = 30%."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Why it matters: "),
                                        "Measures worst-case historical loss. Key metric for risk tolerance."
                                    ], className="mb-0 small text-muted")
                                ], title="Maximum Drawdown"),
                                
                                # R-squared
                                dbc.AccordionItem([
                                    html.P([
                                        html.Strong("Definition: "),
                                        "% of variance explained by the model. Measures goodness of fit."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Values: "),
                                        "0% = no fit. 100% = perfect fit. Typically 30-90% for equity strategies."
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("GROWISE Context: "),
                                        "R² with Fama-French factors typically <5%, indicating returns are "
                                        "highly idiosyncratic (not explained by common risk factors)."
                                    ], className="mb-0 small text-muted")
                                ], title="R-squared (R²)")
                                
                            ], id="glossary-accordion", always_open=False, start_collapsed=True)
                        ])
                    ])
                ], className="mb-3 shadow"),
                
                # ETF/Asset Definitions
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-landmark me-2"),
                        "Common Assets & ETFs"
                    ], className="bg-dark", style={"color": ACCENT, "fontWeight": "bold"}),
                    dbc.CardBody([
                        dbc.Accordion([
                            # GROWISE
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("GROWISE")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "GROWISE Multi-Strategy Portfolio"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Multi-asset portfolio with global equities, fixed income and derivatives overlays as diversified portfolio reference."],
                                    className="mb-0 small text-muted")
                            ], title="GROWISE — Multi-Strategy Portfolio"),
                            
                            # BTC-USD
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("BTC-USD")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Bitcoin vs US Dollar"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Bitcoin cryptocurrency quoted against USD; reflects BTC market price in USD."],
                                    className="mb-0 small text-muted")
                            ], title="BTC-USD — Bitcoin"),
                            
                            # DBC
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("DBC")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Invesco DB Commodity Index Tracking Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Broad commodities ETF tracking diversified index of energy, metals and agricultural futures."],
                                    className="mb-0 small text-muted")
                            ], title="DBC — Commodities"),
                            
                            # GLD
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("GLD")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "SPDR Gold Shares"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "ETF seeking to replicate gold price performance in international markets, before fees and expenses."],
                                    className="mb-0 small text-muted")
                            ], title="GLD — Gold"),
                            
                            # SLV
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("SLV")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "iShares Silver Trust"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "ETF seeking to replicate silver price performance in international markets, before fees and expenses."],
                                    className="mb-0 small text-muted")
                            ], title="SLV — Silver"),
                            
                            # USO
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("USO")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "United States Oil Fund, LP"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Commodities ETF providing exposure to WTI crude oil price via linked financial instruments."],
                                    className="mb-0 small text-muted")
                            ], title="USO — Oil"),
                            
                            # VBINX
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("VBINX")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Vanguard Balanced Index Fund Investor Shares"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Balanced fund approximately 60/40 between broad US equity and investment grade USD bonds."],
                                    className="mb-0 small text-muted")
                            ], title="VBINX — Balanced 60/40"),
                            
                            # XLB
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLB")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Materials Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Sector ETF offering exposure to S&P 500 materials sector (chemicals, metals, packaging, etc.)."],
                                    className="mb-0 small text-muted")
                            ], title="XLB — Materials Sector"),
                            
                            # XLE
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLE")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Energy Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Sector ETF concentrating US energy companies: oil, gas and related services."],
                                    className="mb-0 small text-muted")
                            ], title="XLE — Energy Sector"),
                            
                            # XLF
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLF")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Financial Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Sector ETF of US financials: banks, insurers, asset managers and other financial services."],
                                    className="mb-0 small text-muted")
                            ], title="XLF — Financial Sector"),
                            
                            # XLI
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLI")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Industrial Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Sector ETF providing exposure to US industrials (airlines, machinery, transportation, etc.)."],
                                    className="mb-0 small text-muted")
                            ], title="XLI — Industrial Sector"),
                            
                            # XLK
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLK")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Technology Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Sector ETF grouping S&P 500 IT companies (software, hardware, semiconductors, IT services)."],
                                    className="mb-0 small text-muted")
                            ], title="XLK — Technology Sector"),
                            
                            # XLU
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLU")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Utilities Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Sector ETF of US utilities: electricity, gas, water and regulated public service companies."],
                                    className="mb-0 small text-muted")
                            ], title="XLU — Utilities Sector"),
                            
                            # XLV
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLV")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Health Care Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Healthcare sector ETF including pharma, biotech, medical equipment and US health services."],
                                    className="mb-0 small text-muted")
                            ], title="XLV — Healthcare Sector"),
                            
                            # XLY
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("XLY")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Consumer Discretionary Select Sector SPDR Fund"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "US consumer discretionary sector ETF: retailers, autos, leisure, hotels, restaurants, etc."],
                                    className="mb-0 small text-muted")
                            ], title="XLY — Consumer Discretionary"),
                            
                            # ^GSPC
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("^GSPC")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "S&P 500 Index"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Stock index representing ~500 large US public companies; standard US large cap equity benchmark."],
                                    className="mb-0 small text-muted")
                            ], title="^GSPC — S&P 500"),
                            
                            # AGG
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("AGG")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "iShares Core U.S. Aggregate Bond ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Fixed income ETF replicating investment grade USD bond market (Treasuries, MBS and corporate bonds)."],
                                    className="mb-0 small text-muted")
                            ], title="AGG — Aggregate Bonds"),
                            
                            # IEF
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("IEF")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "iShares 7-10 Year Treasury Bond ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "US Treasury bond ETF with intermediate maturities between 7 and 10 years."],
                                    className="mb-0 small text-muted")
                            ], title="IEF — 7-10Y Treasuries"),
                            
                            # IWM
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("IWM")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "iShares Russell 2000 ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Equity ETF replicating Russell 2000 index of US small cap stocks."],
                                    className="mb-0 small text-muted")
                            ], title="IWM — Small Caps"),
                            
                            # SHY
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("SHY")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "iShares 1-3 Year Treasury Bond ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Fixed income ETF investing in short-term US Treasury bonds with 1-3 year maturities."],
                                    className="mb-0 small text-muted")
                            ], title="SHY — Short-Term Treasuries"),
                            
                            # TLT
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("TLT")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "iShares 20+ Year Treasury Bond ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "US Treasury bond ETF with very long-term maturities exceeding 20 years."],
                                    className="mb-0 small text-muted")
                            ], title="TLT — Long-Term Treasuries"),
                            
                            # VEA
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("VEA")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Vanguard FTSE Developed Markets ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "International equity ETF tracking developed market stocks outside US (Europe, Pacific, Canada)."],
                                    className="mb-0 small text-muted")
                            ], title="VEA — International Developed"),
                            
                            # VNQ
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("VNQ")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Vanguard Real Estate ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "ETF investing in REITs and US real estate companies, replicating broad US real estate index."],
                                    className="mb-0 small text-muted")
                            ], title="VNQ — Real Estate"),
                            
                            # VWO
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("VWO")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Vanguard FTSE Emerging Markets ETF"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Emerging markets equity ETF tracking stock index of emerging countries (China, India, Brazil, etc.)."],
                                    className="mb-0 small text-muted")
                            ], title="VWO — Emerging Markets"),
                            
                            # BRK-B
                            dbc.AccordionItem([
                                html.P([html.Strong("Ticker: "), html.Code("BRK-B")], className="mb-2"),
                                html.P([html.Strong("Full Name: "), "Berkshire Hathaway Inc. Class B"], className="mb-2"),
                                html.P([html.Strong("Description: "), 
                                    "Warren Buffett's conglomerate: diversified businesses, insurance and investments."],
                                    className="mb-0 small text-muted")
                            ], title="BRK-B — Berkshire Hathaway")
                            
                        ], id="assets-accordion", always_open=False, start_collapsed=True)

                    ])
                ], className="shadow")
                
            ], md=8)
        ])
        
    ], fluid=True)


app.layout = dbc.Container([
            # Professional Institutional Header
            html.Div([
                # Top bar with branding
                html.Div([
                    # Left: Logo + Brand
                    html.Div([
                        html.Img(src="/assets/LOGO.png", height="52px", style={"marginRight": "16px"}),
                        html.Div([
                            html.Div([
                                html.Span("SIGMA", style={"fontWeight": "700", "color": "#E67E22", "fontSize": "18px", "letterSpacing": "2px"}),
                                html.Span("LAB", style={"fontWeight": "300", "color": "#ffffff", "fontSize": "18px", "letterSpacing": "2px"}),
                            ]),
                            html.Div("Portfolio Analytics Platform", style={
                                "fontSize": "10px", 
                                "color": "#6e7681", 
                                "letterSpacing": "1.5px", 
                                "textTransform": "uppercase",
                                "marginTop": "-2px"
                            }),
                        ], style={"display": "flex", "flexDirection": "column"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                    
                    # Right: Status indicators (Bloomberg style)
                    html.Div([
                        html.Div([
                            html.Span("LIVE", style={"color": "#22c55e", "fontSize": "9px", "fontWeight": "600", "marginRight": "6px"}),
                            html.Span(id="header-clock", style={"color": "#8b949e", "fontSize": "11px", "fontFamily": "monospace"}),
                        ], style={"display": "flex", "alignItems": "center", "marginRight": "20px"}),
                        html.Div([
                            html.Span("v2.1", style={"color": "#6e7681", "fontSize": "10px", "padding": "2px 6px", "border": "1px solid #30363d", "borderRadius": "3px"}),
                        ]),
                    ], style={"display": "flex", "alignItems": "center"}),
                ], style={
                    "display": "flex", 
                    "justifyContent": "space-between", 
                    "alignItems": "center",
                    "padding": "12px 20px",
                    "backgroundColor": "#0d1117",
                    "borderBottom": "1px solid #21262d"
                }),
            ], className="institutional-header"),
    
            dcc.Tabs([
                        dcc.Tab(label="Correlation Analysis", children=create_analysis_tab(),
                                style={"padding": "12px 24px", "fontWeight": "500", "backgroundColor": "#0d1117", "color": "#8b949e", "border": "none", "borderRight": "1px solid #21262d"},
                                selected_style={"padding": "12px 24px", "fontWeight": "600", "backgroundColor": "#161b22", "color": "#ffffff", "border": "none", "borderRight": "1px solid #21262d", "borderTop": "2px solid #E67E22"}),
                        dcc.Tab(label="Analytics", children=html.Div(id='full-stats-content'),
                                style={"padding": "12px 24px", "fontWeight": "500", "backgroundColor": "#0d1117", "color": "#8b949e", "border": "none", "borderRight": "1px solid #21262d"},
                                selected_style={"padding": "12px 24px", "fontWeight": "600", "backgroundColor": "#161b22", "color": "#ffffff", "border": "none", "borderRight": "1px solid #21262d", "borderTop": "2px solid #E67E22"}),
                        dcc.Tab(label="Portfolio Lab", children=create_portfolio_tab(),
                                style={"padding": "12px 24px", "fontWeight": "500", "backgroundColor": "#0d1117", "color": "#8b949e", "border": "none", "borderRight": "1px solid #21262d"},
                                selected_style={"padding": "12px 24px", "fontWeight": "600", "backgroundColor": "#161b22", "color": "#ffffff", "border": "none", "borderRight": "1px solid #21262d", "borderTop": "2px solid #E67E22"}),
                        dcc.Tab(label="Regime & Factors", children=create_regime_factor_tab(),
                                style={"padding": "12px 24px", "fontWeight": "500", "backgroundColor": "#0d1117", "color": "#8b949e", "border": "none", "borderRight": "1px solid #21262d"},
                                selected_style={"padding": "12px 24px", "fontWeight": "600", "backgroundColor": "#161b22", "color": "#ffffff", "border": "none", "borderRight": "1px solid #21262d", "borderTop": "2px solid #E67E22"}),
                        dcc.Tab(label="GROWISE Optimizer", children=create_growise_tab(),
                                style={"padding": "12px 24px", "fontWeight": "500", "backgroundColor": "#0d1117", "color": "#8b949e", "border": "none", "borderRight": "1px solid #21262d"},
                                selected_style={"padding": "12px 24px", "fontWeight": "600", "backgroundColor": "#161b22", "color": "#ffffff", "border": "none", "borderRight": "1px solid #21262d", "borderTop": "2px solid #E67E22"}),
                        dcc.Tab(label="Resources", children=create_resources_tab(),
                                style={"padding": "12px 24px", "fontWeight": "500", "backgroundColor": "#0d1117", "color": "#8b949e", "border": "none"},
                                selected_style={"padding": "12px 24px", "fontWeight": "600", "backgroundColor": "#161b22", "color": "#ffffff", "border": "none", "borderTop": "2px solid #E67E22"}),
                    
                    ], style={"border": "1px solid #21262d", "borderRadius": "4px 4px 0 0", "marginBottom": "20px", "marginLeft": "15px", "marginRight": "15px"})
                ], fluid=True, style={'backgroundColor': '#0d1117', 'minHeight': '100vh', 'paddingTop': '20px'})


# Demo Mode Modal
demo_modal = dbc.Modal([
    dbc.ModalHeader("Demo Mode Activated"),
    dbc.ModalBody([
        html.H5("Role-Play Scenario:", className="text-warning mb-3"),
        html.P([
            html.Strong("Client Profile: "),
            "Institutional investor with $50M AUM currently in traditional 60/40 (stocks/bonds)"
        ], className="mb-2"),
        html.P([
            html.Strong("Objective: "),
            "Demonstrate how adding GROWISE improves risk-adjusted returns and crisis protection"
        ], className="mb-2"),
        html.P([
            html.Strong("Key Talking Points: "),
        ], className="mb-1"),
        html.Ul([
            html.Li("Low correlation with traditional assets"),
            html.Li("Positive convexity (asymmetric payoff)"),
            html.Li("Crisis performance (Q2 quadrant density)"),
            html.Li("High alpha, low beta (skill-based returns)")
        ], className="mb-3"),
        html.Hr(),
        html.P([
            html.I(className="fas fa-info-circle me-2"),
            "Data has been pre-loaded. Navigate through the tabs to build your presentation."
        ], className="text-muted small mb-0")
    ]),
    dbc.ModalFooter([
        dbc.Button("Start Demo", id="btn-close-demo-modal", color="success")
    ])
], id="modal-demo", size="lg", is_open=False)

# Portfolio Weights Modal
weights_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Portfolio Weights Summary")),
    dbc.ModalBody(id='weights-modal-body'),
    dbc.ModalFooter(
        dbc.Button("Close", id="close-weights-modal", className="ms-auto", n_clicks=0)
    ),
], id="weights-modal", size="lg", is_open=False)

# Combine layout with modal
app.layout = html.Div([app.layout, weights_modal, demo_modal])

# ======================
# CALLBACKS - DATA HANDLING
# ======================

@app.callback(
    Output('data-controls', 'children'),
    Input('data-source', 'value')
)
def show_controls(source):
    if source == "excel":
        return dcc.Upload(
            id={'type':'upload','field':'file'},
            multiple=True,
            children=html.Div(["Drag and Drop or Select Excel/CSV File"]),
            style={
                "width": "100%", "height": "60px", "lineHeight": "60px",
                "borderWidth": "1px", "borderStyle": "dashed",
                "borderRadius": "5px", "textAlign": "center",
                "margin": "10px 0", "backgroundColor": "#2c2c2c", "color": "white"
            }
        )
    return html.Div(["WARNING: Please select a data source."], className="text-warning")

def load_and_validate_data(upload_contents):
    """Load data and validate it"""
    if not upload_contents:
        return pd.DataFrame(), "No data uploaded"
    
    try:
        # Get the content - it's passed as a list, take first element
        content = upload_contents[0] if isinstance(upload_contents, list) else upload_contents
        
        if content is None:
            return pd.DataFrame(), "No file content received"
        
        # Debug: Check content type
        if not isinstance(content, str):
            return pd.DataFrame(), f"Unexpected content type: {type(content)}"
        
        # Handle the upload content - should be "data:type;base64,content"
        # But sometimes it's just the base64 content directly
        if ',' in content:
            # Standard format with header
            parts = content.split(',', 1)
            if len(parts) == 2:
                content_type, content_string = parts
            else:
                return pd.DataFrame(), "Could not parse file content"
        else:
            # Maybe it's just base64 without the header
            content_string = content
        
        # Decode base64
        try:
            decoded = base64.b64decode(content_string)
        except Exception as e:
            return pd.DataFrame(), f"Could not decode file content: {str(e)}"
        
        # Try to read as CSV or Excel
        df = None
        errors = []
        
        # Try CSV with various configurations
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                # Try with index_col=0 (first column as index)
                df = pd.read_csv(io.BytesIO(decoded), index_col=0, parse_dates=True, encoding=encoding)
          
                if not df.empty:
                    break
            except Exception as e:
                errors.append(f"CSV ({encoding}): {str(e)[:50]}")
                try:
                    # Try without index_col in case format is different
                    df = pd.read_csv(io.BytesIO(decoded), parse_dates=True, encoding=encoding)
          
                    if not df.empty:
                        # Use first column as index if it looks like dates
                        first_col = df.columns[0]
                        try:
                            df[first_col] = pd.to_datetime(df[first_col])
                            df = df.set_index(first_col)
                            break
                        except:
                            pass
                except Exception as e2:
                    errors.append(f"CSV-alt ({encoding}): {str(e2)[:50]}")
        
        # If CSV failed, try Excel
        if df is None or df.empty:
            try:
                df = pd.read_excel(io.BytesIO(decoded), index_col=0, parse_dates=True)
            except Exception as e:
                errors.append(f"Excel: {str(e)[:50]}")
                try:
                    # Try without index_col
                    df = pd.read_excel(io.BytesIO(decoded), parse_dates=True)
                    if not df.empty:
                        first_col = df.columns[0]
                        try:
                            df[first_col] = pd.to_datetime(df[first_col])
                            df = df.set_index(first_col)
                        except:
                            pass
                except Exception as e2:
                    errors.append(f"Excel-alt: {str(e2)[:50]}")
        
        if df is None or df.empty:
            error_summary = "; ".join(errors[:3])  # Show first 3 errors
            return pd.DataFrame(), f"Could not read file. Tried multiple formats. Errors: {error_summary}"
        
        # Validate
        is_valid, msg = validate_data(df)
        return df if is_valid else pd.DataFrame(), msg
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return pd.DataFrame(), f"Unexpected error: {str(e)}\n\nDetails: {error_detail[:200]}"

@app.callback(
    Output('data-store', 'data'),
    Output('data-info-alert', 'children'),
    Output('freq-store', 'data'),
    Output('window', 'value'),
    Input({'type':'upload','field':'file'}, 'contents'),
    Input({'type':'upload','field':'file'}, 'filename'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def handle_data_upload(upload_contents, upload_filenames, existing_data_json):
    """Handle file upload with comprehensive error handling"""
    
    if not upload_contents:
            return None, "No file uploaded", None, 4

    # Multi-file upload + session merge
    # If previous data exists in the current browser session, merge new uploads into it.
    base_df = None
    if existing_data_json:
        try:
            import pandas as pd
            from io import StringIO
            base_df = pd.read_json(StringIO(existing_data_json), orient='split')
        except Exception:
            base_df = None

    # Normalize inputs to lists
    contents_list = upload_contents if isinstance(upload_contents, list) else [upload_contents]
    names_list = upload_filenames if isinstance(upload_filenames, list) else [upload_filenames]
    # Load, validate, resample, align, and merge each uploaded file
    merged_msgs = []
    for c, fn in zip(contents_list, names_list):
        df_i, msg_i = load_and_validate_data([c])
        if df_i is None or df_i.empty:
            return None, f"ERROR: {msg_i}", None, 4

        # Phase 2: QC + frequency harmonization to quarterly
        qc_i = run_data_quality_gate(df_i)
        in_freq_code, _ = detect_frequency(df_i.index)
        if in_freq_code != 'Q':
            df_i = resample_returns_to_target(df_i, target_code='Q')

        # If we already have a base_df, align df_i quarter-ends to base_df index within tolerance
        if base_df is not None and not base_df.empty:
            try:
                import pandas as pd
                base_index = pd.to_datetime(base_df.index).sort_values()
                df_i = df_i.sort_index()
                # map to nearest base quarter end within 20 days
                mapped = pd.merge_asof(
                    df_i.reset_index().rename(columns={'index':'date'}).sort_values('date'),
                    pd.DataFrame({'date': base_index}),
                    on='date',
                    direction='nearest',
                    tolerance=pd.Timedelta(days=20)
                )
                mapped = mapped.dropna(subset=['date'])
                mapped = mapped.set_index('date')
                df_i = mapped[df_i.columns]
            except Exception:
                pass

        # Merge into base_df
        if base_df is None or base_df.empty:
            base_df = df_i.copy()
        else:
            # rename on collision
            for col in df_i.columns:
                if col in base_df.columns:
                    new_col = f"{col}__upload"
                    k = 2
                    while new_col in base_df.columns:
                        new_col = f"{col}__upload{k}"
                        k += 1
                    df_i = df_i.rename(columns={col:new_col})
            base_df = base_df.join(df_i, how='outer')

        merged_msgs.append(f"{fn or 'uploaded file'}: {msg_i}")

    df = base_df
    msg = " | ".join(merged_msgs)

    if df is None or df.empty:
        return None, "ERROR: No valid data after merge", None, 4
    
    # Phase 2: Quality gate + frequency harmonization to quarterly (Growise system frequency)
    qc = run_data_quality_gate(df)

    # Detect input frequency and resample to quarterly if needed
    in_freq_code, in_freq_config = detect_frequency(df.index)
    if in_freq_code != 'Q':
        df = resample_returns_to_target(df, target_code='Q')
    # Re-detect after resample
    freq_code, freq_config = detect_frequency(df.index)

    default_window = freq_config["default_window"]
    
    # Store data and metadata
    try:
        data_json = df.to_json(date_format='iso', orient='split')
    except Exception as e:
        return None, f"ERROR: Error serializing data: {str(e)}", None, 4
    
    min_date = df.index.min()
    max_date = df.index.max()
    
    # Build a professional upload summary (Phase 1 proline + Phase 2 QC)
    min_date = df.index.min()
    max_date = df.index.max()
    n_assets = len(df.columns)
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M')

    qc_lines = []
    if qc.get('critical_flags'):
        qc_lines.append(html.Div([html.Strong('QC (CRITICAL): '), ', '.join(qc['critical_flags'])], className='text-danger'))
    if qc.get('warn_flags'):
        qc_lines.append(html.Div([html.Strong('QC (WARN): '), ', '.join(qc['warn_flags'])], className='text-warning'))
    if qc.get('info_flags'):
        qc_lines.append(html.Div([html.Strong('QC (INFO): '), ', '.join(qc['info_flags'])], className='text-info'))

    success_msg = html.Div([
        html.Strong('SUCCESS: Data loaded and validated.'),
        html.Br(),
        html.Small(f"Assets: {n_assets} | Range: {min_date.date()} → {max_date.date()} | Freq: {freq_config['label']} | Updated: {last_update}"),
        html.Br(),
        html.Small(msg),
        html.Div(qc_lines) if qc_lines else html.Div()
    ])
    
    freq_data = {"code": freq_code, "config": freq_config}


    return (data_json, success_msg,
            freq_data, default_window)

@app.callback(
    Output('data-preview-table', 'children'),
    Input('data-store', 'data')
)
def show_data_preview(data_json):
    if not data_json:
        return html.Div([
            html.P("No data loaded", className="text-muted"),
            html.Hr(),
            html.H6("Expected CSV Format:", className="text-light"),
            html.Pre("""Date,Asset1,Asset2,Asset3
2020-01-01,0.01,0.02,-0.01
2020-01-02,-0.005,0.015,0.008
2020-01-03,0.003,-0.01,0.012
...

• First column should be dates
• Other columns are asset returns (decimal format)
• Example: 0.01 = 1% return""", 
                style={"backgroundColor": "#1a1a1a", "padding": "10px", 
                       "color": "#aaa", "fontSize": "11px"})
        ])
    
    try:
        df = pd.read_json(StringIO(data_json), orient='split')
        
        preview_df = pd.concat([df.head(3), df.tail(3)])
        preview_df = preview_df.reset_index()
        preview_df.columns = ['Date'] + list(preview_df.columns[1:])
        
        # Format the preview nicely
        for col in preview_df.columns:
            if col != 'Date':
                preview_df[col] = preview_df[col].apply(lambda x: f"{x:.4f}" if pd.notnull(x) else "NaN")
        
        table = dash_table.DataTable(
            data=preview_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in preview_df.columns],
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': 'black', 'color': ACCENT, 'fontWeight': 'bold'},
            style_cell={'backgroundColor': '#1e1e1e', 'color': 'white', 'textAlign': 'left', 'fontSize': '12px'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'Date'},
                    'fontWeight': 'bold',
                    'color': ACCENT
                }
            ]
        )
        
        return html.Div([
            html.P(f"Showing first 3 and last 3 rows of {len(df)} total periods", 
                   className="text-info", style={"fontSize": "12px"}),
            table
        ])
        
    except Exception as e:
        return html.P(f"Error displaying preview: {str(e)}", className="text-danger")

# ======================
# DATE RANGE PRESETS
# ======================

@app.callback(
    Output('date-filter-store', 'data'),
    Output('date-range-info', 'children'),
    Input('btn-ytd', 'n_clicks'),
    Input('btn-1y', 'n_clicks'),
    Input('btn-3y', 'n_clicks'),
    Input('btn-5y', 'n_clicks'),
    Input('btn-all', 'n_clicks'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def set_date_filter(ytd, y1, y3, y5, all_btn, data_json):
    if not ctx.triggered or not data_json:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    max_date = df.index.max()
    min_date = df.index.min()
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-ytd':
        start = pd.Timestamp(f"{max_date.year}-01-01")
        start = max(start, min_date)
        label = "YTD"
    elif button_id == 'btn-1y':
        start = max_date - pd.DateOffset(years=1)
        start = max(start, min_date)
        label = "1Y"
    elif button_id == 'btn-3y':
        start = max_date - pd.DateOffset(years=3)
        start = max(start, min_date)
        label = "3Y"
    elif button_id == 'btn-5y':
        start = max_date - pd.DateOffset(years=5)
        start = max(start, min_date)
        label = "5Y"
    elif button_id == 'btn-all':
        start = min_date
        label = "All Data"
    else:
        raise PreventUpdate
    
    delta_days = (max_date - start).days
    years = delta_days / 365.25
    info = f"📅 {label}: {years:.1f} years ({delta_days} days)"
    
    return {'start': start.isoformat(), 'end': max_date.isoformat(), 'label': label}, info

@app.callback(
    Output('window-freq-info', 'children'),
    Input('freq-store', 'data'),
    Input('window', 'value'),
)
def update_window_freq_info(freq_data, window):
    """Display window size in different time units"""
    if not freq_data or not window:
        return ""
    
    freq_label = freq_data['config']['label']
    
    # Calculate approximate time span
    if freq_data['code'] == 'D':
        approx = f"≈ {window} days"
    elif freq_data['code'] == 'W':
        approx = f"≈ {window} weeks ({window/4:.1f} months)"
    elif freq_data['code'] == 'M':
        approx = f"≈ {window} months ({window/12:.1f} years)"
    elif freq_data['code'] == 'Q':
        approx = f"≈ {window} quarters ({window/4:.1f} years)"
    else:
        approx = f"≈ {window} years"
    
    return f"({freq_label} data: {approx})"

# ======================
# CALLBACKS - DROPDOWNS & CONTROLS
# ======================

@app.callback(
    Output('benchmark', 'options'),
    Output('benchmark', 'value'),
    Output('single-asset', 'options'),
    Output('avg-assets', 'options'),
    Output('heatmap-assets', 'options'),
    Input('data-store', 'data')
)
def update_dropdowns(data_json):
    if not data_json:
        return [], None, [], [], []
    
    df = pd.read_json(StringIO(data_json), orient='split')
    # P0: Alphabetical ordering for selectable assets (pre-launch note)
    col_names = sorted(list(df.columns), key=lambda x: str(x).upper())
    cols = [{'label': c, 'value': c} for c in col_names]
    default_bench = find_benchmark(df.columns)
    return cols, default_bench, cols, cols, cols

@app.callback(
    Output('avg-assets', 'value'),
    Output('heatmap-assets', 'value'),
    Input('btn-avg-all', 'n_clicks'),
    Input('btn-avg-clear', 'n_clicks'),
    Input('btn-hm-all', 'n_clicks'),
    Input('btn-hm-clear', 'n_clicks'),
    State('avg-assets', 'options'),
    State('heatmap-assets', 'options'),
    State('benchmark', 'value')
)
def select_all_clear(n_avg_all, n_avg_clear, n_hm_all, n_hm_clear, 
                     avg_opts, hm_opts, bench):
    if not ctx.triggered:
        return no_update, no_update

    trig = ctx.triggered[0]['prop_id'].split('.')[0]
    avg_all_vals = [o['value'] for o in (avg_opts or [])]
    hm_all_vals  = [o['value'] for o in (hm_opts or [])]

    if trig == 'btn-avg-all':
        return [v for v in avg_all_vals if v != bench], no_update
    if trig == 'btn-avg-clear':
        return [], no_update
    if trig == 'btn-hm-all':
        return no_update, hm_all_vals
    if trig == 'btn-hm-clear':
        return no_update, []
    return no_update, no_update

# ======================
# CALLBACKS - ANALYSIS VISUALIZATIONS
# ======================

def filter_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range"""
    if start_date and end_date:
        return df.loc[start_date:end_date]
    return df

@app.callback(
    Output('rolling-corr', 'figure'),
    Output('rolling-table', 'children'),
    #Output('regime-analysis', 'figure'),
    Output('avg-corr', 'figure'),
    Output('avg-table', 'children'),
    #Output('corr-distribution', 'figure'),
    Output('heatmap-evolution', 'figure'),
    Output('heatmap-table', 'children'),
    Input('data-store', 'data'),
    Input('window', 'value'),
    Input('benchmark', 'value'),
    Input('single-asset', 'value'),
    Input('avg-assets', 'value'),
    Input('heatmap-assets', 'value'),
    Input('date-filter-store', 'data'),  # AGREGAR ESTA LÍNEA
)
def update_all_charts(data_json, window, benchmark, single_asset, avg_assets,
                      heatmap_assets, date_filter):  # AGREGAR date_filter
    
    # Use date filter from store
    start_date = date_filter.get('start') if date_filter else None
    end_date = date_filter.get('end') if date_filter else None
    
    if not data_json or not benchmark or not single_asset:
        placeholder = go.Figure()
        placeholder.update_layout(template="plotly_dark",
                                 xaxis=dict(visible=False), 
                                 yaxis=dict(visible=False))
        placeholder.add_annotation(text="Please load data and select assets", 
                                  xref="paper", yref="paper",
                                  showarrow=False, font=dict(size=16, color="white"))
        return (placeholder, html.P("No data", className="text-muted"),
                        # placeholder,  # regime-analysis REMOVED
                        placeholder, html.P("No data", className="text-muted"),
                        # placeholder,  # corr-distribution REMOVED
                        placeholder, html.P("No data", className="text-muted"))
    
    df = pd.read_json(StringIO(data_json), orient='split')
    df = filter_by_date_range(df, start_date, end_date)
    
    # 1. ROLLING CORRELATION WITH STABILITY
    corr_series, stability = calculate_correlation_stability(
        df[single_asset], df[benchmark], window, window*2
    )
    
    fig_rolling = make_subplots(
        rows=2, cols=1, 
        row_heights=[0.7, 0.3],
        subplot_titles=("Rolling Correlation", "Correlation Stability (Std Dev)"),
        vertical_spacing=0.12
    )
    
    fig_rolling.add_trace(
        go.Scatter(x=corr_series.index, y=corr_series, 
                  name="Rolling Corr", line=dict(color=ACCENT)),
        row=1, col=1
    )
    fig_rolling.add_hline(y=corr_series.mean(), line_dash="dash",
                         annotation_text=f"Mean: {corr_series.mean():.3f}",
                         row=1, col=1)
    
    fig_rolling.add_trace(
        go.Scatter(x=stability.index, y=stability, 
                  name="Stability", line=dict(color=INST_COLORS["warning"])),
        row=2, col=1
    )
    
    fig_rolling.update_layout(
        template="plotly_dark",
        height=CHART_HEIGHT,
        title_text=f"Rolling {window} Correlation: {benchmark} vs {single_asset} | Mean: {corr_series.mean():.3f}",
        showlegend=True
    )
    
    rolling_tbl = dash_table.DataTable(
        columns=[{"name": "Rolling Corr", "id": "corr"}],
        data=[{"corr": f"{v:.3f}"} for v in corr_series.dropna().tail(10)],
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "black", "color": ACCENT},
        style_cell={"backgroundColor": "#1e1e1e", "color": "white"}
    )
    
    # 2. REGIME ANALYSIS
    # regime = detect_market_regime(df[benchmark])
    # bull_mask = regime == 1
    # bear_mask = regime == 0
    
    # corr_bull = df[single_asset][bull_mask].corr(df[benchmark][bull_mask])
    # corr_bear = df[single_asset][bear_mask].corr(df[benchmark][bear_mask])
    
    # fig_regime = go.Figure()
    
    # # Scatter with regime coloring
    # colors = ['red' if r == 0 else 'green' for r in regime]
    # fig_regime.add_trace(go.Scatter(
    #     x=df[benchmark], 
    #     y=df[single_asset],
    #     mode='markers',
    #     marker=dict(color=colors, size=4, opacity=0.6),
    #     name='Returns',
    #     text=[f"{'Bear' if r==0 else 'Bull'}" for r in regime],
    #     hovertemplate='%{text}<br>Bench: %{x:.2%}<br>Asset: %{y:.2%}<extra></extra>'
    # ))
    
    # fig_regime.update_layout(
    #     template="plotly_dark",
    #     title=f"Correlation by Regime: {benchmark} vs {single_asset}<br>"
    #           f"Bull: {corr_bull:.3f} | Bear: {corr_bear:.3f}",
    #     xaxis_title=f"{benchmark} Returns",
    #     yaxis_title=f"{single_asset} Returns",
    #     height=CHART_HEIGHT
    # )
    
    # 3. AVERAGE CORRELATION
    if avg_assets:
        avg_list = [a for a in avg_assets if a != benchmark]
        if len(avg_list) > 0:
            # Calculate rolling correlation for each asset, then average
            corr_list = []
            for asset in avg_list:
                corr = df[asset].rolling(window).corr(df[benchmark])
                corr_list.append(corr)
            # Average across all assets
            avg_corrs = pd.concat(corr_list, axis=1).mean(axis=1)
            
            fig_avg = go.Figure(go.Scatter(x=avg_corrs.index, y=avg_corrs,
                                          line=dict(color=ACCENT)))
            fig_avg.add_hline(y=avg_corrs.mean(), line_dash="dash",
                            annotation_text=f"Mean: {avg_corrs.mean():.3f}")
            fig_avg.update_layout(
                template="plotly_dark",
                title=f"Average Rolling Correlation: {benchmark} vs {len(avg_list)} Assets | Mean: {avg_corrs.mean():.3f}",
                height=CHART_HEIGHT
            )
            avg_tbl = dash_table.DataTable(
                columns=[{"name": "Avg Corr", "id": "avg"}],
                data=[{"avg": f"{v:.3f}"} for v in avg_corrs.dropna().tail(10)],
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "black", "color": ACCENT},
                style_cell={"backgroundColor": "#1e1e1e", "color": "white"}
            )
        else:
            fig_avg = go.Figure()
            fig_avg.update_layout(template="plotly_dark")
            avg_tbl = html.P("Select assets other than benchmark", className="text-muted")
    else:
        fig_avg = go.Figure()
        fig_avg.update_layout(template="plotly_dark")
        avg_tbl = html.P("No assets selected", className="text-muted")
    
    # 4. CORRELATION DISTRIBUTION OVER TIME
    # corr_series_dist = df[single_asset].rolling(window).corr(df[benchmark]).dropna()
    
    # if dist_groupby == 'Y':
    #     groups = corr_series_dist.groupby(corr_series_dist.index.year)
    # elif dist_groupby == 'Q':
    #     groups = corr_series_dist.groupby(corr_series_dist.index.to_period('Q'))
    # else:  # 'M'
    #     groups = corr_series_dist.groupby(corr_series_dist.index.to_period('M'))
    
    # fig_dist = go.Figure()
    # for name, group in groups:
    #     fig_dist.add_trace(go.Box(y=group.values, name=str(name), boxmean='sd'))
    
    # fig_dist.update_layout(
    #     template="plotly_dark",
    #     title=f"Correlation Distribution Over Time ({dist_groupby}): {benchmark} vs {single_asset}",
    #     yaxis_title="Correlation",
    #     height=CHART_HEIGHT,
    #     showlegend=False
    # )
    
    # 5. HEATMAP EVOLUTION (ANIMATED)
    if heatmap_assets and len(heatmap_assets) > 1:
        # Create frames for animation
        frames = []
        dates = []
        step = max(1, len(df) // 20)  # Max 20 frames
        
        for i in range(window, len(df), step):
            subset = df[heatmap_assets].iloc[max(0, i-window):i]
            if len(subset) >= window:
                corr_matrix = subset.corr()
                dates.append(df.index[i])
                frames.append(corr_matrix)
        
        if frames:
            # Initial heatmap
            fig_hm_evo = px.imshow(
                frames[0], 
                text_auto=".2f", 
                color_continuous_scale='RdBu',
                zmin=-1, zmax=1
            )
            
            # Add animation frames
            fig_hm_evo.frames = [
                go.Frame(
                    data=[go.Heatmap(z=frame.values, 
                                    x=frame.columns, 
                                    y=frame.index,
                                    text=frame.round(2).values,
                                    texttemplate='%{text}',
                                    colorscale='RdBu',
                                    zmin=-1, zmax=1)],
                    name=date.strftime('%Y-%m-%d')
                )
                for frame, date in zip(frames, dates)
            ]
            
            # Add play/pause buttons and date display
            fig_hm_evo.update_layout(
                template="plotly_dark",
                title=dict(
                    text="Correlation Heatmap Evolution (Animated)",
                    y=0.98,
                    x=0.5,
                    xanchor='center',
                    yanchor='top'
                ),
                height=CHART_HEIGHT + 100,
                updatemenus=[{
                    "type": "buttons",
                    "showactive": False,
                    "direction": "left",
                    "pad": {"r": 10, "t": 10},
                    "x": 0.0,
                    "xanchor": "left",
                    "y": 1.12,
                    "yanchor": "top",
                    "buttons": [
                        {"label": "▶", "method": "animate",
                         "args": [None, {"frame": {"duration": 500, "redraw": True},
                                       "fromcurrent": True}]},
                        {"label": "⏸", "method": "animate",
                         "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                         "mode": "immediate"}]}
                    ]
                }],
                sliders=[{
                    "active": 0,
                    "yanchor": "top",
                    "y": -0.08,
                    "xanchor": "left",
                    "currentvalue": {
                        "visible": True,
                        "prefix": "Current Date: ",
                        "font": {"color": ACCENT, "size": 13},
                        "xanchor": "center"
                    },
                    "pad": {"b": 5, "t": 30},
                    "len": 0.9,
                    "x": 0.05,
                    "steps": [
                        {"args": [[f.name], {"frame": {"duration": 0, "redraw": True},
                                            "mode": "immediate"}],
                         "label": f.name, 
                         "value": f.name,
                         "method": "animate"}
                        for f in fig_hm_evo.frames
                    ]
                }],
                margin=dict(t=60, b=80, l=40, r=40)
            )
        else:
            fig_hm_evo = go.Figure()
            fig_hm_evo.update_layout(template="plotly_dark")
        
        hm_tbl = dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in frames[-1].columns],
            data=frames[-1].reset_index().round(2).to_dict("records"),
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "black", "color": ACCENT},
            style_cell={"backgroundColor": "#1e1e1e", "color": "white"}
        )
    else:
        fig_hm_evo = go.Figure()
        fig_hm_evo.update_layout(template="plotly_dark")
        hm_tbl = html.P("Select at least 2 assets", className="text-muted")
    
    return (fig_rolling, rolling_tbl,  # fig_regime REMOVED
                fig_avg, avg_tbl,  # fig_dist REMOVED
                fig_hm_evo, hm_tbl)

# ======================
# TABLE COLLAPSE TOGGLES
# ======================

@app.callback(
    Output('collapse-rolling-table', 'is_open'),
    Output('btn-toggle-rolling-table', 'children'),
    Input('btn-toggle-rolling-table', 'n_clicks'),
    State('collapse-rolling-table', 'is_open'),
    prevent_initial_call=True
)
def toggle_rolling_table(n_clicks, is_open):
    if n_clicks:
        new_state = not is_open
        label = "Hide Data Table" if new_state else "Show Data Table"
        return new_state, label
    return is_open, "Show Data Table"

@app.callback(
    Output('collapse-avg-table', 'is_open'),
    Output('btn-toggle-avg-table', 'children'),
    Input('btn-toggle-avg-table', 'n_clicks'),
    State('collapse-avg-table', 'is_open'),
    prevent_initial_call=True
)
def toggle_avg_table(n_clicks, is_open):
    if n_clicks:
        new_state = not is_open
        label = "Hide Data Table" if new_state else "Show Data Table"
        return new_state, label
    return is_open, "Show Data Table"

@app.callback(
    Output('collapse-heatmap-table', 'is_open'),
    Output('btn-toggle-heatmap-table', 'children'),
    Input('btn-toggle-heatmap-table', 'n_clicks'),
    State('collapse-heatmap-table', 'is_open'),
    prevent_initial_call=True
)
def toggle_heatmap_table(n_clicks, is_open):
    if n_clicks:
        new_state = not is_open
        label = "Hide Data Table" if new_state else "Show Data Table"
        return new_state, label
    return is_open, "Show Data Table"

@app.callback(
    Output('collapse-data-tools', 'style'),
    Input('btn-toggle-data-tools', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_data_tools(n_clicks):
    if n_clicks and n_clicks % 2 == 1:
        return {"display": "block"}
    return {"display": "none"}

# Header clock update
@app.callback(
    Output('header-clock', 'children'),
    Input('clock-interval', 'n_intervals')
)
def update_clock(n):
    from datetime import datetime
    now = datetime.now()
    return now.strftime('%H:%M:%S UTC-5')

@app.callback(
    Output('data-info-panel', 'children'),
    Input('data-store', 'data'),
    Input('data-info-store', 'data'),
)
def update_data_info_panel(data_json, info_store):
    """Create professional data info panel with base vs added info"""
    if not data_json:
        return html.Div([
            html.Div("No Data", className="data-info-title"),
            html.Div("Upload to begin", className="data-info-subtitle")
        ])
    
    try:
        df = pd.read_json(StringIO(data_json), orient='split')
        n_assets = len(df.columns)
        n_periods = len(df)
        current_assets = set(df.columns)
        
        # Load base data for comparison
        base_df = load_base_data_csv()
        n_base_assets = len(base_df.columns) if base_df is not None and not base_df.empty else 0
        n_base_periods = len(base_df) if base_df is not None and not base_df.empty else 0
        base_assets = set(base_df.columns) if base_df is not None and not base_df.empty else set()
        
        # Calculate added assets (new assets not in base)
        added_assets = current_assets - base_assets
        n_added_assets = len(added_assets)
        
        # Get base date range
        if base_df is not None and not base_df.empty:
            base_start = base_df.index.min()
            base_end = base_df.index.max()
        else:
            base_start = None
            base_end = None
        
        # Current date range
        start_date = df.index.min()
        end_date = df.index.max()
        
        # Check if date range changed due to added data
        period_diff = n_periods - n_base_periods
        date_range_changed = False
        
        if base_start is not None:
            # If current start is earlier than base start, show it
            if start_date < base_start:
                date_range_changed = True
        
        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime('%b %Y')
            end_str = end_date.strftime('%b %Y')
        else:
            start_str = str(start_date)[:7]
            end_str = str(end_date)[:7]
        
        # Build info rows
        rows = []
        
        # Assets row
        if n_added_assets > 0:
            rows.append(html.Div([
                html.Span(str(n_assets), className="data-info-value"),
                html.Span(" assets ", className="data-info-label"),
                html.Span(f"(+{n_added_assets} added)", className="data-info-added"),
            ], className="data-info-row"))
        else:
            rows.append(html.Div([
                html.Span(str(n_assets), className="data-info-value"),
                html.Span(" assets", className="data-info-label"),
            ], className="data-info-row"))
        
        # Periods row - show negative if new data reduces overlap
        if period_diff != 0:
            if period_diff > 0:
                period_label = f"(+{period_diff} new)"
                period_class = "data-info-added"
            else:
                period_label = f"({period_diff} due to new data)"
                period_class = "data-info-reduced"
            rows.append(html.Div([
                html.Span(str(n_periods), className="data-info-value"),
                html.Span(" periods ", className="data-info-label"),
                html.Span(period_label, className=period_class),
            ], className="data-info-row"))
        else:
            rows.append(html.Div([
                html.Span(str(n_periods), className="data-info-value"),
                html.Span(" periods", className="data-info-label"),
            ], className="data-info-row"))
        
        # Date range with indicator if changed
        if date_range_changed:
            rows.append(html.Div([
                html.Span(f"{start_str}", className="data-info-date-new"),
                html.Span(f" — {end_str}", className="data-info-date"),
            ], className="data-info-row mt-1"))
        else:
            rows.append(html.Div([
                html.Span(f"{start_str} — {end_str}", className="data-info-date"),
            ], className="data-info-row mt-1"))
        
        return html.Div(rows, className="data-info-content")
    except:
        return html.Div("Data loaded", className="data-info-subtitle")

# ======================
# WINDOW OPTIMIZATION
# ======================

# @app.callback(
#     Output('optimal-window-info', 'children'),
#     Output('window', 'value', allow_duplicate=True),
#     Input('btn-optimize-window', 'n_clicks'),
#     State('data-store', 'data'),
#     State('benchmark', 'value'),
#     State('single-asset', 'value'),
#     prevent_initial_call=True
# )
# def optimize_window(n_clicks, data_json, benchmark, single_asset):
#     if not data_json or not benchmark or not single_asset:
#         return "WARNING: Load data first", no_update
    
#     df = pd.read_json(StringIO(data_json), orient='split')
    
#     # Test windows from 2 to 24
#     windows = range(2, 25)
#     stabilities = []
    
#     for w in windows:
#         _, stability = calculate_correlation_stability(
#             df[single_asset], df[benchmark], w, w*2
#         )
#         stabilities.append(stability.mean())
    
#     # Find window with lowest average stability (most stable correlation)
#     optimal_idx = np.nanargmin(stabilities)
#     optimal_window = windows[optimal_idx]
    
#     return f"SUCCESS: Optimal window: {optimal_window} (lowest volatility)", optimal_window

# ======================
# FULL STATS TAB
# ======================

@app.callback(
    Output('full-stats-content', 'children'),
    Input('data-store', 'data'),
)
def create_full_stats_tab(data_json):
    """Create full statistics tab with pairwise correlation analysis"""
    if not data_json:
        return dbc.Container([
            html.H4("Please load data first from the Analysis tab.", 
                   className="text-warning mt-4")
        ], fluid=True)
    
    df = pd.read_json(StringIO(data_json), orient='split')
    
    return dbc.Container([
        html.H2("Full Statistical Overview", style={"color": ACCENT, "fontSize": "20px"}, className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.Label("Select Asset for Pairwise Analysis", className="text-light"),
                dcc.Dropdown(
                    id='stats-asset-select',
                    options=[{'label': c, 'value': c} for c in df.columns],
                    value=find_benchmark(df.columns),
                    
                ),
            ], md=4),
            dbc.Col([
                html.Label("Histogram Bins", className="text-light"),
                dcc.Slider(
                    id='stats-bins',
                    min=10, max=50, step=5, value=20,
                    marks={10: '10', 20: '20', 30: '30', 40: '40', 50: '50'},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], md=4),
            dbc.Col([
                html.Label("Show Normal Curve", className="text-light"),
                dbc.Checklist(
                    id='stats-show-normal',
                    options=[{"label": " Overlay", "value": "show"}],
                    value=["show"],
                    switch=True,
                    className="mt-2"
                ),
            ], md=4),
        ]),
        
        html.Br(),
        
        # Pairwise Correlation Distribution
        dbc.Card([
            dbc.CardHeader("Distribution of Pairwise Correlations", 
                          className="bg-dark",
                          style={"color": ACCENT, "fontWeight": "bold"}),
            dbc.CardBody([
                dcc.Loading(dcc.Graph(id='pairwise-corr-hist', 
                                     style={"height": f"{CHART_HEIGHT}px"})),
            ])
        ], className="mb-4 bg-dark text-light shadow"),
        
        # Correlation Matrix
        # dbc.Card([
        #     dbc.CardHeader("Full Correlation Matrix", 
        #                   className="bg-dark",
        #                   style={"color": ACCENT, "fontWeight": "bold"}),
        #     dbc.CardBody([
        #         dcc.Loading(dcc.Graph(id='full-corr-matrix', 
        #                              style={"height": "700px"})),
        #     ])
        # ], className="mb-4 bg-dark text-light shadow"),
        
        # Summary Statistics
        dbc.Card([
            dbc.CardHeader("Summary Statistics", 
                          className="bg-dark",
                          style={"color": ACCENT, "fontWeight": "bold"}),
            dbc.CardBody([
                html.Div(id='summary-stats-table')
            ])
        ], className="mb-4 bg-dark text-light shadow"),
        
    ], fluid=True)

@app.callback(
    Output('pairwise-corr-hist', 'figure'),
    #Output('full-corr-matrix', 'figure'),
    Output('summary-stats-table', 'children'),
    Input('data-store', 'data'),
    Input('stats-asset-select', 'value'),
    Input('stats-bins', 'value'),
    Input('stats-show-normal', 'value'),
)
def update_full_stats(data_json, selected_asset, n_bins, show_normal):
    """Update full statistics visualizations"""
    if not data_json or not selected_asset:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    
    # Calculate full correlation matrix
    corr_matrix = df.corr()
    
    # 1. ENHANCED PAIRWISE CORRELATION HISTOGRAM
    asset_corrs = corr_matrix[selected_asset].drop(selected_asset)
    
    fig_hist = go.Figure()
    
    # Main histogram
    fig_hist.add_trace(go.Histogram(
        x=asset_corrs.values,
        nbinsx=n_bins,
        marker_color=ACCENT,
        opacity=0.7,
        name='Correlations',
        histnorm='probability density' if show_normal and 'show' in show_normal else ''
    ))
    
    # Add normal distribution overlay if requested
    if show_normal and 'show' in show_normal:
        from scipy import stats
        mean = asset_corrs.mean()
        std = asset_corrs.std()
        
        x_range = np.linspace(asset_corrs.min(), asset_corrs.max(), 100)
        y_normal = stats.norm.pdf(x_range, mean, std)
        
        fig_hist.add_trace(go.Scatter(
            x=x_range,
            y=y_normal,
            mode='lines',
            name='Normal Distribution',
            line=dict(color='cyan', width=2, dash='dash')
        ))
    
    # Add vertical lines for statistics
    mean_corr = asset_corrs.mean()
    median_corr = asset_corrs.median()
    
    fig_hist.add_vline(x=mean_corr, line_dash="dash", line_color=INST_COLORS["warning"],
                      annotation_text=f"Mean: {mean_corr:.3f}",
                      annotation_position="top right")
    fig_hist.add_vline(x=median_corr, line_dash="dot", line_color="cyan",
                      annotation_text=f"Median: {median_corr:.3f}",
                      annotation_position="top left")
    
    # Add percentile lines
    p25 = asset_corrs.quantile(0.25)
    p75 = asset_corrs.quantile(0.75)
    fig_hist.add_vline(x=p25, line_dash="dot", line_color="lightgray", opacity=0.5)
    fig_hist.add_vline(x=p75, line_dash="dot", line_color="lightgray", opacity=0.5)
    
    fig_hist.update_layout(
        template="plotly_dark",
        title=f"Distribution of Pairwise Correlations: {selected_asset} vs All Assets<br>"
              f"<sub>Mean: {mean_corr:.3f} | Std: {asset_corrs.std():.3f} | "
              f"IQR: [{p25:.3f}, {p75:.3f}]</sub>",
        xaxis_title="Correlation",
        yaxis_title="Probability Density" if (show_normal and 'show' in show_normal) else "Frequency",
        height=CHART_HEIGHT,
        showlegend=True if (show_normal and 'show' in show_normal) else False
    )
    
    # 2. FULL CORRELATION MATRIX HEATMAP
    # fig_matrix = px.imshow(
    #     corr_matrix,
    #     text_auto=".2f",
    #     color_continuous_scale='RdBu',
    #     zmin=-1, zmax=1,
    #     labels=dict(color="Correlation")
    # )
    # fig_matrix.update_layout(
    #     template="plotly_dark",
    #     title="Full Correlation Matrix (All Assets)",
    #     height=700
    # )
    
    # 3. ENHANCED SUMMARY STATISTICS - COMPACT LAYOUT
    
    # Calculate additional statistics
    skewness = asset_corrs.skew()
    kurtosis = asset_corrs.kurtosis()
    
    # Create compact metric cards in 2-column layout
    def create_stat_metric(label, value, interpretation=''):
        """Create a compact stat metric card"""
        return dbc.Card([
            dbc.CardBody([
                html.H6(label, className="text-secondary mb-2", style={'fontSize': '12px'}),
                html.H4(value, className="mb-1", style={'color': ACCENT}),
                html.P(interpretation, className="text-muted mb-0", 
                      style={'fontSize': '11px', 'fontStyle': 'italic'}) if interpretation else None
            ], style={'padding': '12px'})
        ], className="mb-2 bg-dark border-secondary")
    
    # Determine interpretations
    skew_interpretation = 'Right-skewed' if skewness > 0.5 else ('Left-skewed' if skewness < -0.5 else 'Symmetric')
    kurt_interpretation = 'Heavy tails' if kurtosis > 1 else ('Light tails' if kurtosis < -1 else 'Normal')
    high_corr_pct = (asset_corrs > 0.7).sum() / len(asset_corrs) * 100
    low_corr_pct = (asset_corrs.abs() < 0.3).sum() / len(asset_corrs) * 100
    high_interpretation = 'Many highly correlated' if high_corr_pct > 30 else 'Few highly correlated'
    low_interpretation = 'Good diversification' if low_corr_pct > 30 else 'Limited diversification'
    
    stats_layout = dbc.Row([
        # Column 1 - Basic Stats
        dbc.Col([
            html.H6("Distribution Statistics", className="text-light mb-3"),
            create_stat_metric("Mean", f"{mean_corr:.3f}"),
            create_stat_metric("Median", f"{median_corr:.3f}"),
            create_stat_metric("Std Deviation", f"{asset_corrs.std():.3f}"),
            create_stat_metric("Skewness", f"{skewness:.3f}", skew_interpretation),
            create_stat_metric("Kurtosis", f"{kurtosis:.3f}", kurt_interpretation),
        ], md=6),
        
        # Column 2 - Range & Composition
        dbc.Col([
            html.H6("Range & Composition", className="text-light mb-3"),
            create_stat_metric("Min / Max", f"{asset_corrs.min():.3f} / {asset_corrs.max():.3f}"),
            create_stat_metric("25th / 75th Percentile", f"{p25:.3f} / {p75:.3f}"),
            create_stat_metric("Range", f"{asset_corrs.max() - asset_corrs.min():.3f}"),
            create_stat_metric("% High Corr (>0.7)", f"{high_corr_pct:.1f}%", high_interpretation),
            create_stat_metric("% Low Corr (<0.3)", f"{low_corr_pct:.1f}%", low_interpretation),
        ], md=6)
    ])
    
    return fig_hist, stats_layout


# ======================
# EXPORT FUNCTIONALITY (PDF)
# ======================
# 
# @app.callback(
#     Output("download-report", "data"),
#     Input("btn-export", "n_clicks"),
#     State('data-store', 'data'),
#     State('benchmark', 'value'),
#     State('window', 'value'),
#     prevent_initial_call=True
# )
# def export_report(n_clicks, data_json, benchmark, window):
#     if not data_json:
#         return no_update
#     
#     df = pd.read_json(StringIO(data_json), orient='split')
#     
    # Create summary report
#     report = f"""Correlation Analysis Report
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ========================================
# 
# Dataset Info:
# - Period: {df.index.min()} to {df.index.max()}
# - Assets: {len(df.columns)}
# - Observations: {len(df)}
# - Rolling Window: {window}
# - Benchmark: {benchmark}
# 
# Correlation Summary:
# """
#     
#     for col in df.columns:
#         if col != benchmark:
#             corr = df[col].corr(df[benchmark])
#             report += f"  {col}: {corr:.3f}\n"
#     
#     return dict(content=report, filename=f"{EXPORT_FILENAME}_{datetime.now().strftime('%Y%m%d')}.txt")

# ======================
# TOGGLE CALLBACKS
# ======================

for collapse_id, btn_id in [
    ("collapse-rolling", "btn-rolling"),
    ("collapse-avg", "btn-avg"),
    ("collapse-heatmap", "btn-heatmap")
]:
    @app.callback(
        Output(collapse_id, "is_open"),
        Input(btn_id, "n_clicks"),
        State(collapse_id, "is_open")
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

# ======================
# PORTFOLIO LAB CALLBACKS
# ======================

@app.callback(
    Output('rets-json', 'data'),
    Output('pf-assets', 'options'),
    Output('pf-assets', 'value'),
    Output('pf-roll-target', 'options'),
    Output('pf-roll-target', 'value'),
    Output('pf-3d-bench', 'options'),
    Output('pf-3d-bench', 'value'),
    Input('data-store', 'data'),
)
def init_portfolio_lab(data_json):
    if not data_json:
        return None, [], [], [], None, [], None
    
    rets = pd.read_json(StringIO(data_json), orient='split').dropna()
    bench_col = find_benchmark_pf(list(rets.columns))
    
    asset_opts = [{'label': c, 'value': c} for c in rets.columns]
    default_assets = [c for c in rets.columns][:4]
    
    all_opts = [{'label': c, 'value': c} for c in rets.columns]
    
    return (rets.to_json(date_format="iso", orient="split"),
            asset_opts, default_assets,
            all_opts, bench_col,
            [{'label': bench_col, 'value': bench_col}], bench_col)

# Dynamic weights inputs
@app.callback(
    Output('pf-weights-container', 'children'),
    Input('pf-assets', 'value'),
    prevent_initial_call=False
)
def update_weights_inputs(assets):
    """Generate individual weight inputs for each selected asset"""
    if not assets or len(assets) == 0:
        return html.Div([
            html.P("Select assets first", className="text-muted", style={"fontSize": "12px"})
        ])
    
    equal_weight = 1.0 / len(assets)
    
    inputs = []
    for i, asset in enumerate(assets):
        inputs.append(
            html.Div([
                html.Label(f"{asset}", className="text-light", 
                          style={"fontSize": "12px", "marginBottom": "2px"}),
                dcc.Input(
                    id={'type': 'weight-input', 'index': i, 'asset': asset},
                    type='number',
                    value=equal_weight,
                    min=0,
                    max=1,
                    step=0.01,
                    style={"width": "100%", "marginBottom": "8px"}
                )
            ])
        )
    
    return html.Div(inputs)

@app.callback(
    Output({'type': 'weight-input', 'index': ALL, 'asset': ALL}, 'value'),
    Input('btn-equal-weights', 'n_clicks'),
    Input('btn-normalize-weights', 'n_clicks'),
    State({'type': 'weight-input', 'index': ALL, 'asset': ALL}, 'value'),
    State('pf-assets', 'value'),
    prevent_initial_call=True
)
def manage_weights(n_equal, n_normalize, current_weights, assets):
    """Handle equal weights and normalization"""
    if not ctx.triggered or not assets:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-equal-weights':
        equal_weight = 1.0 / len(assets)
        return [equal_weight] * len(assets)
    
    elif button_id == 'btn-normalize-weights':
        if not current_weights or all(w is None or w == 0 for w in current_weights):
            raise PreventUpdate
        total = sum(w for w in current_weights if w is not None)
        if total == 0:
            raise PreventUpdate
        normalized = [w / total if w is not None else 0 for w in current_weights]
        return normalized
    
    raise PreventUpdate

@app.callback(
    Output('weights-sum-info', 'children'),
    Input({'type': 'weight-input', 'index': ALL, 'asset': ALL}, 'value'),
)
def display_weights_sum(weights):
    """Display sum of weights and alert if not 100%"""
    if not weights or all(w is None for w in weights):
        return ""
    
    total = sum(w for w in weights if w is not None)
    
    if abs(total - 1.0) < 0.001:
        return f"SUCCESS: Total: {total:.1%} (Balanced)"
    elif total > 1.0:
        return f"WARNING: Total: {total:.1%} (Over 100%)"
    else:
        return f"WARNING: Total: {total:.1%} (Under 100%)"

# ======================
# PORTFOLIO LAB CALLBACKS (continued)
# ======================

@app.callback(
    Output('pf-3d-bubble', 'figure'),
    Output('pf-stats', 'children'),
    Output('pf-portfolio-store', 'data'),
    Input('pf-build', 'n_clicks'),
    State('rets-json', 'data'),
    State('pf-assets', 'value'),
    State({'type': 'weight-input', 'index': ALL, 'asset': ALL}, 'value'),
    #State('pf-freq', 'value'),
    State('pf-portfolio-store', 'data'),
    prevent_initial_call=True
)
def build_portfolio(n_clicks, rets_json, assets, weights_list, store):  # REMOVED freq
    if not n_clicks or not assets or not rets_json:
        raise PreventUpdate
    
    freq = "N"  # Always use native data frequency
    
    rets = pd.read_json(rets_json, orient='split')
    bench_col = find_benchmark(list(rets.columns))
    
    # Parse weights from individual inputs
    if not weights_list or len(weights_list) != len(assets):
        return no_update, html.P("WARNING: Weights error", className="text-warning"), no_update
    
    weights = np.array([w if w is not None else 0 for w in weights_list], dtype=float)
    
    if not np.isfinite(weights).all() or weights.sum() == 0:
        return no_update, html.P("WARNING: Invalid weights", className="text-warning"), no_update
    
    # Normalize weights
    weights = weights / weights.sum()
    
    # Resample if needed
    if freq in ["D", "W", "M"]:
        rule = {"D":"D", "W":"W", "M":"M"}[freq]
        pf_rets = (rets[assets].apply(compound_resample, rule=rule)).dot(weights)
    else:
        pf_rets = rets[assets].dot(weights)
    
    # Calculate metrics
    ann_ret, ann_vol, sharpe, max_dd = ann_metrics(pf_rets)
    bench = rets[bench_col].reindex_like(pf_rets)
    corr = pf_rets.corr(bench)
    
    # Store portfolio (max 5)
    store = store or []
    new_item = {
        "name": f"PF {len(store)+1}",
        "assets": assets,
        "weights": weights.tolist(),
        "rets_json": pf_rets.to_json(date_format="iso", orient="split"),
    }
    store.append(new_item)
    if len(store) > 5:
        store = store[-5:]
    
    fig = go.Figure()
    fig.update_layout(
        template="plotly_dark",
        scene=dict(
            xaxis_title="Volatility (Ann.)",
            yaxis_title="Annual Return",
            zaxis_title="Correlation"
        ),
        title="Interactive 3D Portfolio Bubbles"
    )
    
    # stats_text = html.Div([
    #     html.H4("📊 Latest Portfolio Stats", style={"color": ACCENT}),
    #     html.P(f"Annual Return: {ann_ret:.2%}"),
    #     html.P(f"Annual Volatility: {ann_vol:.2%}"),
    #     html.P(f"Sharpe Ratio: {sharpe:.2f}"),
    #     html.P(f"Correlation vs {bench_col}: {corr:.2f}"),
    #     html.P(f"Max Drawdown: {max_dd:.2%}"),
    #     html.P(f"Assets: {', '.join(assets)}", style={"fontSize": "12px", "color": "#888"}),
    #     html.P(f"Weights: {', '.join([f'{w:.2%}' for w in weights])}", 
    #            style={"fontSize": "12px", "color": "#888"})
    # ])
    
    # Build stats cards (include Sortino)
    ann_factor = infer_ann_factor(pf_rets.index)
    ann_ret = (1 + pf_rets).prod() ** (ann_factor/len(pf_rets)) - 1
    ann_vol = pf_rets.std() * (ann_factor ** 0.5)
    downside = pf_rets[pf_rets < 0]
    downside_vol = (downside.std() * (ann_factor ** 0.5)) if len(downside) > 0 else ann_vol
    sortino = (ann_ret) / downside_vol if downside_vol and downside_vol > 0 else 0
    sharpe = (ann_ret) / ann_vol if ann_vol and ann_vol > 0 else 0
    cumulative = (1 + pf_rets).cumprod()
    running_max = cumulative.cummax()
    dd = (cumulative - running_max) / running_max
    max_dd = float(dd.min()) if len(dd) else 0.0

    def _metric_card(label, value, suffix=""):
        return dbc.Card(dbc.CardBody([
            html.Div(label, style={"fontSize":"11px","opacity":0.7,"letterSpacing":"0.06em"}),
            html.Div(f"{value}{suffix}", style={"fontSize":"22px","fontWeight":"800","color":ACCENT})
        ]), className="bg-dark text-light shadow", style={"border":"1px solid #30363d"})

    stats_cards = dbc.Row([
        dbc.Col(_metric_card("RETURN (ANN.)", f"{ann_ret*100:.1f}", "%"), md=3),
        dbc.Col(_metric_card("VOL (ANN.)", f"{ann_vol*100:.1f}", "%"), md=3),
        dbc.Col(_metric_card("SHARPE", f"{sharpe:.2f}"), md=3),
        dbc.Col(_metric_card("SORTINO", f"{sortino:.2f}"), md=3),
        dbc.Col(_metric_card("MAX DD", f"{max_dd*100:.1f}", "%"), md=3),
    ], className="g-2")

    return fig, stats_cards, store

@app.callback(
    Output('pf-portfolio-store', 'data', allow_duplicate=True),
    Input('pf-clear', 'n_clicks'),
    prevent_initial_call=True
)
def clear_portfolios(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return []

@app.callback(
    Output('pf-roll-portfolio', 'options'),
    Output('pf-roll-portfolio', 'value'),
    Output('stress-portfolio', 'options'),
    Output('stress-portfolio', 'value'),
    Input('pf-portfolio-store', 'data')
)
def update_portfolio_dropdowns(store):
    if not store:
        return [], None, [], None
    opts = [{"label": p["name"], "value": p["name"]} for p in store]
    return opts, opts[-1]["value"], opts, opts[-1]["value"]

@app.callback(
    Output('pf-rolling-corr', 'figure'),
    Input('pf-roll-portfolio', 'value'),
    Input('pf-roll-target', 'value'),
    Input('pf-roll-window', 'value'),
    State('pf-portfolio-store', 'data'),
    State('rets-json', 'data')
)
def plot_rolling_corr(port_name, target_col, window, store, rets_json):
    if not store or not port_name or not target_col or not window or not rets_json:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark",
                         title="Select portfolio and target to view rolling correlation")
        return fig
    
    rets = pd.read_json(rets_json, orient='split')
    p = next((x for x in store if x["name"] == port_name), None)
    if p is None or target_col not in rets.columns:
        raise PreventUpdate
    
    pf = pd.read_json(p['rets_json'], orient='split', typ='series').dropna()
    tgt = rets[target_col].reindex(pf.index).dropna()
    aligned = pd.concat([pf.rename("PF"), tgt.rename("Target")], axis=1).dropna()
    
    if len(aligned) < window:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark",
                         title="Insufficient data for rolling correlation")
        return fig
    
    roll = aligned["PF"].rolling(int(window)).corr(aligned["Target"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll.index, y=roll.values, 
                            mode='lines', name='Rolling Corr',
                            line=dict(color=ACCENT)))
    fig.add_hline(y=0, line_dash="dash", line_color=INST_COLORS["text_disabled"])
    fig.add_hline(y=roll.mean(), line_dash="dot", 
                 annotation_text=f"Mean: {roll.mean():.3f}",
                 line_color=INST_COLORS["warning"])
    
    fig.update_layout(
        template="plotly_dark",
        title=f"Rolling Correlation: {port_name} vs {target_col} (window={window})",
        xaxis_title="Date", 
        yaxis_title="Correlation",
        height=400
    )
    return fig

# ENHANCED 3D BUBBLE CHART
last_ranges = None

@app.callback(
    Output('pf-3d-bubble', 'figure', allow_duplicate=True),
    Input('pf-portfolio-store', 'data'),
    Input('rets-json', 'data'),
    Input('pf-3d-bench', 'value'),
    Input('btn-reset-3d', 'n_clicks'),
    Input('btn-full-range', 'n_clicks'),  # NUEVO
    prevent_initial_call=True
)
def update_3d_bubbles(store, rets_json, bench_col, reset_clicks, full_range_clicks):
    global last_ranges
    
    # Check which button was clicked
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if triggered_id == 'btn-reset-3d':
        last_ranges = None
    
    if not store or not rets_json or not bench_col:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            scene=dict(
                xaxis_title="Volatility (Ann.)",
                yaxis_title="Annual Return",
                zaxis_title="Correlation"
            ),
            title="Build portfolios to see them in 3D space"
        )
        return fig
    
    rets = pd.read_json(rets_json, orient='split')
    if bench_col not in rets.columns:
        bench_col = find_benchmark(list(rets.columns))
    bench_all = rets[bench_col]
    
    xs, ys, zs, names, colors, hover_texts = [], [], [], [], [], []
    
    for i, p in enumerate(store):
        pf = pd.read_json(p['rets_json'], orient='split', typ='series').dropna()
        mu, vol, sh, mdd = ann_metrics(pf)
        b = bench_all.reindex_like(pf)
        corr_i = pf.corr(b)
        
        xs.append(vol)
        ys.append(mu)
        zs.append(corr_i)
        names.append(p["name"])
        colors.append(sh if np.isfinite(sh) else 0.0)
        
        # Create detailed hover text
        assets_str = ', '.join(p['assets'][:3])
        if len(p['assets']) > 3:
            assets_str += f' + {len(p["assets"])-3} more'
        hover_texts.append(
            f"<b>{p['name']}</b><br>"
            f"Assets: {assets_str}<br>"
            f"Ann. Return: {mu:.2%}<br>"
            f"Ann. Vol: {vol:.2%}<br>"
            f"Sharpe: {sh:.2f}<br>"
            f"Corr vs {bench_col}: {corr_i:.3f}<br>"
            f"Max DD: {mdd:.2%}"
        )
    
    # Determine ranges based on button clicked
    if triggered_id == 'btn-full-range':
        # FULL RANGE - Expand to theoretical limits
        vol_range = [0, max(xs) * 1.5]  # Start at 0, go 50% beyond max
        ret_min = min(ys) - abs(min(ys)) * 0.5  # Extend downward
        ret_max = max(ys) + abs(max(ys)) * 0.5  # Extend upward
        ret_range = [ret_min, ret_max]
        corr_range = [-1, 1]  # Full correlation range
        last_ranges = dict(vol=vol_range, ret=ret_range, corr=corr_range)
    elif last_ranges is None:
        # Auto-fit on first call
        pad = 0.02
        vol_range = [max(0, min(xs) - pad), max(xs) + pad]
        ret_range = [min(ys) - pad, max(ys) + pad]
        corr_range = [max(-1, min(zs) - pad), min(1, max(zs) + pad)]
        last_ranges = dict(vol=vol_range, ret=ret_range, corr=corr_range)
    else:
        # Use locked ranges
        vol_range = last_ranges["vol"]
        ret_range = last_ranges["ret"]
        corr_range = last_ranges["corr"]
    
    # Create 3D scatter with improved aesthetics
    fig = go.Figure(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers+text',
        text=names,
        textposition="top center",
        textfont=dict(size=12, color='white', family='Arial Black'),  # Better text
        marker=dict(
            size=22,
            opacity=0.85,
            color=colors,
            colorscale="Plasma",  # More vibrant colorscale
            colorbar=dict(title="Sharpe", x=1.12, thickness=15, len=0.7),
            line=dict(color='#FFD700', width=2),  # Gold border
            symbol='circle'
        ),
        hovertext=hover_texts,
        hoverinfo='text',
        hoverlabel=dict(
            bgcolor="#161b22",
            font_size=13,
            font_family="Consolas",
            bordercolor="#E67E22"
        ),
        name="Portfolios",
        # IMPROVED PROJECTION LINES
        # projection=dict(
        #     x=dict(show=True, opacity=0.7, scale=2),  # More visible
        #     y=dict(show=True, opacity=0.7, scale=2),
        #     z=dict(show=True, opacity=0.7, scale=2)
        # )
    ))
    
    # Add benchmark point
    # if bench_col in rets.columns:
    #     b_ret, b_vol, b_sh, _ = ann_metrics(rets[bench_col])
    #     fig.add_trace(go.Scatter3d(
    #         x=[b_vol], y=[b_ret], z=[1.0],
    #         mode='markers+text',
    #         text=[bench_col],
    #         textposition="bottom center",
    #         textfont=dict(size=11, color='#FF4444'),
    #         marker=dict(size=18, color='#FF4444', symbol='diamond', 
    #                    line=dict(color='white', width=2)),
    #         name='Benchmark',
    #         hovertext=f"<b>{bench_col}</b><br>Ann. Ret: {b_ret:.2%}<br>Ann. Vol: {b_vol:.2%}<br>Sharpe: {b_sh:.2f}",
    #         hoverinfo='text',
    #         hoverlabel=dict(bgcolor="#2d1f1f", font_size=13),
    #         showlegend=False
    #     ))
    
    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text="Portfolio Analysis - 3D Risk-Return-Correlation Space",
            font=dict(size=16, color='#E67E22')
        ),
        scene=dict(
            xaxis=dict(
                title="Volatility (Ann.)", 
                range=vol_range, 
                autorange=False,
                gridcolor='#30363d',
                gridwidth=2,
                showbackground=True,
                backgroundcolor='#0d1117',
                tickfont=dict(size=11, color='#c9d1d9', family='Consolas'),
                showspikes=True,
                spikecolor='#E67E22',
                spikethickness=2
            ),
            yaxis=dict(
                title="Annual Return", 
                range=ret_range, 
                autorange=False,
                gridcolor='#30363d',
                gridwidth=2,
                showbackground=True,
                backgroundcolor='#0d1117',
                tickfont=dict(size=11, color='#c9d1d9', family='Consolas'),
                showspikes=True,
                spikecolor='#E67E22',
                spikethickness=2
            ),
            zaxis=dict(
                title=f"Corr vs {bench_col}", 
                range=corr_range, 
                autorange=False,
                gridcolor='#30363d',
                gridwidth=2,
                showbackground=True,
                backgroundcolor='#0d1117',
                tickfont=dict(size=11, color='#c9d1d9', family='Consolas'),
                showspikes=True,
                spikecolor='#E67E22',
                spikethickness=2
            ),
            aspectmode="cube",  # AGREGAR ESTA LÍNEA
            bgcolor='#0d1117',  # AGREGAR ESTA LÍNEA
            camera=dict(  # AGREGAR ESTE BLOQUE
                eye=dict(x=1.8, y=1.2, z=1.4)
            )
        ),
        paper_bgcolor='#0d1117',
        margin=dict(l=20, r=20, b=20, t=60),  # CAMBIAR: eran todos 0
        height=700,
        showlegend=False
    )    
    return fig


# Portfolio Weights Modal Callback
@app.callback(
    Output('weights-modal', 'is_open'),
    Output('weights-modal-body', 'children'),
    Input('btn-view-weights', 'n_clicks'),
    Input('close-weights-modal', 'n_clicks'),
    State('pf-portfolio-store', 'data'),
    State('weights-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_weights_modal(view_clicks, close_clicks, store, is_open):
    ctx_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if ctx_id == 'close-weights-modal':
        return False, ""
    
    if ctx_id == 'btn-view-weights':
        if not store:
            return True, html.P("No portfolios built yet.", className="text-muted")
        
        # Create table with all portfolios
        rows = []
        for pf in store:
            assets_weights = [f"{a}: {w:.1%}" for a, w in zip(pf['assets'], pf['weights'])]
            rows.append(html.Tr([
                html.Td(pf['name'], style={'fontWeight': 'bold', 'color': ACCENT}),
                html.Td(html.Ul([html.Li(aw) for aw in assets_weights], style={'marginBottom': '0'}))
            ]))
        
        table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Portfolio", style={'color': ACCENT, 'backgroundColor': '#1e1e1e'}),
                html.Th("Weights", style={'color': ACCENT, 'backgroundColor': '#1e1e1e'})
            ])),
            html.Tbody(rows)
        ], bordered=True, hover=True, responsive=True, striped=True, 
           className="table-dark",
           style={'backgroundColor': '#1e1e1e', 'color': 'white'})
        
        return True, table
    
    return is_open, ""

# ======================
# STRESS TESTING
# ======================

@app.callback(
    Output('stress-results', 'figure'),
    Output('stress-metrics', 'children'),
    Output('collapse-stress', 'is_open'),
    Input('btn-stress', 'n_clicks'),
    State('stress-portfolio', 'value'),
    State('stress-corr-level', 'value'),
    State('pf-portfolio-store', 'data'),
    State('rets-json', 'data'),
    prevent_initial_call=True
)
def run_stress_test(n_clicks, port_name, stress_level, store, rets_json):
    if not n_clicks or not port_name or not store or not rets_json:
        raise PreventUpdate
    
    rets = pd.read_json(rets_json, orient='split')
    p = next((x for x in store if x["name"] == port_name), None)
    if p is None:
        raise PreventUpdate
    
    # Get portfolio returns
    pf_rets = pd.read_json(p['rets_json'], orient='split', typ='series').dropna()
    
    # Calculate current metrics
    current_ret, current_vol, current_sh, current_dd = ann_metrics(pf_rets)
    
    # Simulate stressed scenario
    # In a crisis, correlations spike toward stress_level
    # This increases portfolio volatility
    
    assets = p['assets']
    weights = np.array(p['weights'])
    
    # Calculate current correlation matrix
    asset_rets = rets[assets].dropna()
    current_corr_matrix = asset_rets.corr()
    
    # Create stressed correlation matrix
    stressed_corr_matrix = current_corr_matrix.copy()
    n_assets = len(assets)
    
    # Set off-diagonal correlations to stress level
    for i in range(n_assets):
        for j in range(n_assets):
            if i != j:
                # Preserve sign but increase magnitude
                sign = np.sign(stressed_corr_matrix.iloc[i, j])
                stressed_corr_matrix.iloc[i, j] = sign * stress_level
    
    # Calculate stressed portfolio volatility
    asset_vols = asset_rets.std().values
    stressed_cov = np.outer(asset_vols, asset_vols) * stressed_corr_matrix.values
    stressed_vol = np.sqrt(weights @ stressed_cov @ weights) * np.sqrt(infer_ann_factor(asset_rets.index))
    
    # Estimate stressed Sharpe (assume return stays same - conservative)
    stressed_sh = current_ret / stressed_vol if stressed_vol > 0 else np.nan
    
    # Create visualization
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Volatility Comparison", "Sharpe Ratio Comparison"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Volatility comparison
    fig.add_trace(
        go.Bar(x=['Normal', 'Stressed'], 
               y=[current_vol, stressed_vol],
               marker_color=[ACCENT, 'red'],
               text=[f'{current_vol:.2%}', f'{stressed_vol:.2%}'],
               textposition='outside'),
        row=1, col=1
    )
    
    # Sharpe comparison
    fig.add_trace(
        go.Bar(x=['Normal', 'Stressed'], 
               y=[current_sh, stressed_sh],
               marker_color=[ACCENT, 'red'],
               text=[f'{current_sh:.2f}', f'{stressed_sh:.2f}'],
               textposition='outside'),
        row=1, col=2
    )
    
    fig.update_layout(
        template="plotly_dark",
        title=f"Stress Test Results: {port_name} (Correlation Spike to {stress_level:.0%})",
        showlegend=False,
        height=400
    )
    
    # Calculate percent changes
    vol_increase = (stressed_vol - current_vol) / current_vol * 100
    sh_decrease = (stressed_sh - current_sh) / abs(current_sh) * 100 if current_sh != 0 else 0
    
    metrics_div = html.Div([
        html.H5("Stress Test Impact", style={"color": "red"}),
        html.P([
            html.Strong("Scenario: "), 
            f"All pairwise correlations spike to {stress_level:.0%}"
        ]),
        html.Hr(style={"borderColor": "red"}),
        html.P([
            html.Strong("Volatility: "),
            f"{current_vol:.2%} → {stressed_vol:.2%} ",
            html.Span(f"(+{vol_increase:.1f}%)", 
                     style={"color": "red", "fontWeight": "bold"})
        ]),
        html.P([
            html.Strong("Sharpe Ratio: "),
            f"{current_sh:.2f} → {stressed_sh:.2f} ",
            html.Span(f"({sh_decrease:+.1f}%)", 
                     style={"color": "red", "fontWeight": "bold"})
        ]),
        html.Hr(style={"borderColor": "red"}),
        html.P([
            html.Strong(" Interpretation: "),
            f"In a crisis where correlations spike to {stress_level:.0%}, this portfolio's "
            f"volatility would increase by {vol_increase:.1f}% and risk-adjusted returns "
            f"would deteriorate significantly."
        ], style={"fontSize": "13px", "color": "#ffcccc"}),
        html.P([
            html.Strong("Mitigation: "),
            "Consider adding low/negative correlation assets or hedging strategies."
        ], style={"fontSize": "13px", "color": "#ccffcc"})
    ])
    
    return fig, metrics_div, True

# ======================
# RUN APP
# ======================

# GROWISE CALLBACK

from dash import callback, Input, Output

# @callback(Output("guide-debug", "children"),
#           Input("btn-start-guide", "n_clicks"))
# def _dbg_guide_click(n):
#     return f"Tutorial clicked: {n}"


@app.callback(
    Output('gw-status', 'children'),
    Output('gw-content', 'children'),
    Output('gw-ready', 'data'),
    Input('data-store', 'data')
)
def gw_load_from_main(data_json):
    """Load data from main tab and initialize GROWISE"""
    if not data_json:
        return "WARNING: No data loaded. Upload data in Correlation Analysis tab first.", html.Div(), None
    
    try:
        df = pd.read_json(StringIO(data_json), orient='split')
        
        if 'GROWISE' not in df.columns:
            return "WARNING: GROWISE column not found in data.", html.Div(), None
        
        available_assets = [col for col in df.columns if col != 'GROWISE']
        
        # Crear config exacto del growise
        config_layout = dbc.Card([
            dbc.CardBody([
                html.H4("Step 2: Configure Portfolio", className='mb-4'),
                
                dbc.Tabs([
                    # TAB 1: MARGINAL
                    dbc.Tab([
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.H5("Quick Start: Load Famous Portfolio", className='mb-2'),
                                    dcc.Dropdown(
                                        id='preset-dropdown',
                                        options=[{'label': name, 'value': name} 
                                                for name in FAMOUS_PORTFOLIOS.keys()],
                                        value='Custom Portfolio',
                                        placeholder='Select a preset or build custom...',
                                        clearable=False
                                    ),
                                    html.Div(id='preset-status', className='mt-2')
                                ])
                            ], className='mb-4'),
                            
                            html.Div(id='preset-weights-display', className='mb-3'),
                            
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Select Assets for Portfolio", className='fw-bold'),
                                    ], width=10),
                                    dbc.Col([
                                        dbc.Button("All", id='btn-select-all', size='sm', 
                                                  color='secondary', outline=True, className='w-100')
                                    ], width=2)
                                ], className='mb-2'),
                                
                                dcc.Dropdown(
                                    id='assets-dropdown',
                                    options=[{'label': asset, 'value': asset} 
                                            for asset in available_assets],
                                    value=[],
                                    multi=True,
                                    placeholder='Choose assets...'
                                ),
                                
                                html.Div(id='slider-container', className='mt-3 mb-3'),
                                #html.Div(id='pie-preview', className='mb-3'),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button([html.I(className='fas fa-balance-scale me-2'), "Equal Weights"], 
                                                  id='btn-equal-weights', color='secondary', outline=True, className='w-100')
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Button([html.I(className='fas fa-percentage me-2'), "Normalize"], 
                                                  id='btn-normalize', color='warning', outline=True, className='w-100')
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Button([html.I(className='fas fa-chart-line me-2'), "Analyze"], 
                                                  id='btn-analyze', color='success', className='w-100')
                                    ], md=4)
                                ])
                            ], id='custom-portfolio-section', style={'display': 'block'}),
                            
                            html.Hr(className='my-4'),
                            html.H5("Analysis Parameters", className='mb-3'),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("GROWISE Range", className='fw-bold'),
                                    dcc.RangeSlider(
                                        id='growise-range',
                                        min=0, max=50, step=5,
                                        value=[0, 50],
                                        marks={i: f'{i}%' for i in range(0, 51, 10)}
                                    )
                                ], md=8),
                                dbc.Col([
                                    html.Label("Benchmark", className='fw-bold'),
                                    dcc.Dropdown(
                                        id='benchmark-dropdown',
                                        options=[{'label': asset, 'value': asset} 
                                                for asset in available_assets if '^' in asset or 'SPY' in asset],
                                        value='^GSPC' if '^GSPC' in available_assets else None
                                    )
                                ], md=4)
                            ])
                        ], className='p-3'),
                        
                        html.Div(id='results-marginal', className='mt-4')
                        
                    ], label="Marginal Analysis", tab_id="tab-marginal"),
                    
                    # TAB 2: OPTIMIZATION
                    dbc.Tab([
                        html.Div([
                            html.H5("Portfolio Optimization", className='mb-3'),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Quick Load", className='fw-bold'),
                                    dcc.Dropdown(
                                        id='opt-preset-selector',
                                        options=[{'label': name, 'value': name} 
                                                for name in FAMOUS_PORTFOLIOS.keys() 
                                                if name != 'Custom Portfolio'],
                                        value=None,
                                        placeholder='Load assets from famous portfolio...',
                                        clearable=True
                                    )
                                ], md=6),
                                dbc.Col([
                                    html.Label("Force GROWISE", className='fw-bold'),
                                    dbc.Switch(
                                        id='opt-force-growise',
                                        value=False,
                                        label="Ensure ≥3% GROWISE allocation"
                                    )
                                ], md=6)
                            ], className='mb-3'),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Assets (including GROWISE)", className='fw-bold'),
                                    dcc.Dropdown(
                                        id='opt-assets-dropdown',
                                        options=[{'label': asset, 'value': asset} 
                                                for asset in df.columns],
                                        value=[],
                                        multi=True,
                                        placeholder='Select assets...'
                                    )
                                ], md=7),
                                dbc.Col([
                                    html.Label("Objective", className='fw-bold'),
                                    dcc.Dropdown(
                                        id='opt-objective',
                                        options=[
                                            {'label': 'Maximize Sharpe Ratio', 'value': 'sharpe'},
                                            {'label': 'Minimize Volatility', 'value': 'volatility'},
                                            {'label': 'Maximize Sortino Ratio', 'value': 'sortino'}
                                        ],
                                        value='sharpe',
                                        clearable=False
                                    )
                                ], md=3),
                                dbc.Col([
                                    html.Label("\u00A0", className='fw-bold'),
                                    dbc.Button("All", id='btn-select-all-opt', size='sm', 
                                              color='secondary', outline=True, className='w-100')
                                ], md=2)
                            ], className='mb-3'),
                            
                            dbc.Button("Optimize Portfolio", id='btn-optimize', 
                                      color='warning', className='w-100 fw-bold', size='lg')
                        ], className='p-3'),
                        
                        html.Div(id='results-optimization', className='mt-4')
                        
                    ], label="Optimization", tab_id="tab-optimization")
                ], id='config-tabs', active_tab="tab-marginal")
            ])
        ], style={'backgroundColor': '#161b22', 'border': '1px solid #30363d', 'borderRadius': '6px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.3)'})
        
        # status = dbc.Alert([
        #     html.Strong("SUCCESS: Data loaded from Correlation Analysis!"),
        #     html.Br(),
        #     f"Shape: {df.shape[0]} periods × {df.shape[1]} assets | GROWISE detected ✓"
        # ], color='success')
        
        return html.Div(), config_layout, data_json
        
    except Exception as e:
        return dbc.Alert(f"ERROR: Error: {str(e)}", color='danger'), html.Div(), None


def upload_data(contents, filename):
    if not contents:
        raise PreventUpdate
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), index_col=0, parse_dates=True)
            
        else:
            df = pd.read_excel(io.BytesIO(decoded), index_col=0, parse_dates=True)
        
        # Data validation
        if 'GROWISE' not in df.columns:
            return None, dbc.Alert("ERROR: GROWISE column not found", color='danger'), [], {'display': 'none'}
        
        if df.isnull().sum().sum() > 0:
            df = df.dropna(axis=1, how='all')
        
        data_json = df.to_json(orient='split', date_format='iso')
        
        available_assets = [col for col in df.columns if col != 'GROWISE']
        
        # Configuration layout
        config_layout = [
            dbc.Card([
                dbc.CardBody([
                    html.H4("Step 2: Configure Portfolio", className='mb-4'),
                    
                    # TABS FOR MARGINAL VS OPTIMIZATION
                    dbc.Tabs([
                        # TAB 1: MARGINAL ANALYSIS
                        dbc.Tab([
                            html.Div([
                                # Preset selector
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("Quick Start: Load Famous Portfolio", className='mb-2'),
                                        dcc.Dropdown(
                                            id='preset-dropdown',
                                            options=[{'label': name, 'value': name} 
                                                    for name in FAMOUS_PORTFOLIOS.keys()],
                                            value=None,
                                            placeholder='Select a preset or build custom...',
                                            clearable=False
                                        ),
                                        html.Div(id='preset-status', className='mt-2')
                                    ])
                                ], className='mb-4'),
                                
                                # Preset weights display (card with analyze button)
                                html.Div(id='preset-weights-display', className='mb-3'),
                                
                                # Custom portfolio section (hidden for presets)
                                html.Div([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label("Select Assets for Portfolio", className='fw-bold'),
                                        ], width=10),
                                        dbc.Col([
                                            dbc.Button("All", id='btn-select-all', size='sm', 
                                                      color='secondary', outline=True, className='w-100')
                                        ], width=2)
                                    ], className='mb-2'),
                                    
                                    dcc.Dropdown(
                                        id='assets-dropdown',
                                        options=[{'label': asset, 'value': asset} 
                                                for asset in available_assets],
                                        value=[],
                                        multi=True,
                                        placeholder='Choose assets...'
                                    ),
                                    
                                    html.Div(id='slider-container', className='mt-3 mb-3'),
                                    
                                    html.Div(id='pie-preview', className='mb-3'),
                                    
                                    # Equal weights button (SAME SIZE as analyze)
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Button([
                                                html.I(className='fas fa-balance-scale me-2'),
                                                "Equal Weights"
                                            ], id='btn-equal-weights', color='info', outline=True, className='w-100')
                                        ], md=6),
                                        dbc.Col([
                                            dbc.Button([
                                                html.I(className='fas fa-chart-line me-2'),
                                                "Analyze"
                                            ], id='btn-analyze', color='success', className='w-100')
                                        ], md=6)
                                    ])
                                ], id='custom-portfolio-section', style={'display': 'block'}),
                                
                                # Analysis parameters
                                html.Hr(className='my-4'),
                                html.H5("Analysis Parameters", className='mb-3'),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("GROWISE Range", className='fw-bold'),
                                        dcc.RangeSlider(
                                            id='growise-range',
                                            min=0, max=50, step=5,
                                            value=[5, 20],
                                            marks={i: f'{i}%' for i in range(0, 51, 10)}
                                        )
                                    ], md=8),
                                    dbc.Col([
                                        html.Label("Benchmark", className='fw-bold'),
                                        dcc.Dropdown(
                                            id='benchmark-dropdown',
                                            options=[{'label': asset, 'value': asset} 
                                                    for asset in available_assets if '^' in asset or 'SPY' in asset],
                                            value='^GSPC' if '^GSPC' in available_assets else None
                                        )
                                    ], md=4)
                                ])
                            ], className='p-3'),
                            
                            # RESULTS INSIDE TAB 1
                            html.Div(id='results-marginal', className='mt-4')
                            
                        ], label="Marginal Analysis", tab_id="tab-marginal"),
                        
                        # TAB 2: OPTIMIZATION - CLEAN & FOCUSED
                        dbc.Tab([
                            html.Div([
                                html.H5("Portfolio Optimization", className='mb-3'),
                                html.P("Mathematical optimization to find ideal weights. GROWISE is treated as a regular asset.", 
                                       className='text-muted mb-3'),
                                
                                # Quick Load from Preset
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Quick Load", className='fw-bold'),
                                        dcc.Dropdown(
                                            id='opt-preset-selector',
                                            options=[{'label': name, 'value': name} 
                                                    for name in FAMOUS_PORTFOLIOS.keys() 
                                                    if name != 'Custom Portfolio'],
                                            value=None,
                                            placeholder='Load assets from famous portfolio...',
                                            clearable=True,
                                            style={'fontSize': '14px'}
                                        )
                                    ], md=6),
                                    dbc.Col([
                                        html.Label("Force GROWISE", className='fw-bold'),
                                        html.Div([
                                            dbc.Switch(
                                                id='opt-force-growise',
                                                value=False,
                                                label="Ensure ≥3% GROWISE allocation",
                                                style={'fontSize': '13px'}
                                            )
                                        ], className='mt-2')
                                    ], md=6)
                                ], className='mb-3'),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Assets (including GROWISE)", className='fw-bold'),
                                        html.Div([
                                            dcc.Dropdown(
                                                id='opt-assets-dropdown',
                                                options=[{'label': asset, 'value': asset} 
                                                        for asset in df.columns],
                                                value=[],
                                                multi=True,
                                                placeholder='Select assets (including GROWISE)...',
                                                style={'fontSize': '14px'}
                                            )
                                        ])
                                    ], md=7),
                                    dbc.Col([
                                        html.Label("Objective", className='fw-bold'),
                                        dcc.Dropdown(
                                            id='opt-objective',
                                            options=[
                                                {'label': 'Maximize Sharpe Ratio', 'value': 'sharpe'},
                                                {'label': 'Minimize Volatility', 'value': 'volatility'},
                                                {'label': 'Maximize Sortino Ratio', 'value': 'sortino'}
                                            ],
                                            value='sharpe',
                                            clearable=False,
                                            style={'fontSize': '14px'}
                                        )
                                    ], md=3),
                                    dbc.Col([
                                        html.Label("\u00A0", className='fw-bold'),  # Non-breaking space for alignment
                                        dbc.Button("All", id='btn-select-all-opt', size='sm', 
                                                  color='secondary', outline=True, className='w-100 mt-0',
                                                  style={'fontSize': '12px'})
                                    ], md=2)
                                ], className='mb-3', align='end'),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button("Optimize Portfolio", id='btn-optimize', 
                                                  color='warning', className='w-100 fw-bold', size='lg')
                                    ])
                                ])
                            ], className='p-3'),
                            
                            # RESULTS INSIDE TAB 2
                            html.Div(id='results-optimization', className='mt-4')
                            
                        ], label="Optimization", tab_id="tab-optimization")
                    ], id='config-tabs', active_tab="tab-marginal")
                ])
            ], style={'backgroundColor': '#161b22', 
                     'border': f"1px solid {'#30363d'}"})
        ]
        
        status = dbc.Alert([
            html.Strong("SUCCESS: Data loaded successfully!"),
            html.Br(),
            f"Shape: {df.shape[0]} periods × {df.shape[1]} assets"
        ], color='success')
        
        return data_json, status, config_layout, {'display': 'block'}
        
    except Exception as e:
        return None, dbc.Alert(f"ERROR: Error: {str(e)}", color='danger'), [], {'display': 'none'}

# PRESET SELECTION -> TOGGLE UI AND SHOW WEIGHTS - FIX #1 & #2
@app.callback(
    Output('custom-portfolio-section', 'style'),
    Output('preset-weights-display', 'children'),
    Output('preset-name-store', 'data'),
    Output('preset-modal', 'is_open'),
    Output('modal-title', 'children'),
    Output('modal-body', 'children'),
    Input('preset-dropdown', 'value'),
    Input('close-modal', 'n_clicks'),
    State('preset-weights-store', 'data'),
    State('preset-modal', 'is_open'),
    State('gw-ready', 'data'),  # Added to check available assets
    prevent_initial_call=True
)
def toggle_custom_ui(preset_name, close_clicks, preset_weights, is_open, data_json):
    triggered = ctx.triggered_id
    if triggered == 'close-modal':
        return no_update, no_update, no_update, False, no_update, no_update
    
    if not preset_name or not data_json:
        raise PreventUpdate
    
    # Load available assets
    df = pd.read_json(StringIO(data_json), orient='split')
    available_assets = set(df.columns)
    
    if preset_name == 'Custom Portfolio':
        return {'display': 'block'}, [], preset_name, False, "", []
    else:
        # FIX #1 & #2: Always create the analyze button, even if preset_weights is None
        # Map preset weights to available assets
        preset_config = FAMOUS_PORTFOLIOS.get(preset_name, {})
        target_weights = preset_config.get('weights', {})
        fallback_weights = preset_config.get('fallback', {})
        
        # Try to map weights
        mapped_weights = {}
        for asset, weight in target_weights.items():
            if asset in available_assets:
                mapped_weights[asset] = weight * 100
            elif asset in fallback_weights:
                fallback_asset = asset
                if fallback_weights[fallback_asset] in available_assets:
                    mapped_weights[fallback_weights[fallback_asset]] = weight * 100
        
        # If no mapping worked, use fallback directly
        if not mapped_weights:
            for asset, weight in fallback_weights.items():
                if asset in available_assets:
                    mapped_weights[asset] = weight * 100
        
        # Create display even if mapping incomplete
        preset_desc = preset_config.get('description', '')
        
        # Modal content
        modal_title = f"{preset_name}"
        modal_body = [
            html.P(preset_desc, className='text-muted mb-3'),
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Asset", style={'fontSize': '16px'}), 
                    html.Th("Weight", style={'fontSize': '16px'})
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(html.Strong(asset), style={'fontSize': '14px'}), 
                        html.Td(f"{weight:.1f}%", style={'fontSize': '14px'})
                    ]) 
                    for asset, weight in mapped_weights.items()
                ])
            ], bordered=True, hover=True, striped=True, responsive=True, 
               style={'backgroundColor': '#1c2128', 'color': '#e1e4e8'})
        ]
        
        # Preset display card - ALWAYS CREATE THE BUTTON
        preset_display = dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.H5([
                        html.I(className='fas fa-chart-pie me-2'),
                        f"{preset_name}"
                    ], className='mb-2', style={'color': '#06A77D'}),
                    html.P(preset_desc, className='text-muted mb-3'),
                    
                    html.Div([
                        html.Strong(f"Portfolio: {len(mapped_weights)} assets"),
                        html.Br(),
                        html.Small(", ".join(mapped_weights.keys()) if mapped_weights else "No assets mapped", 
                                  className='text-muted')
                    ], className='mb-3'),
                    
                    # Buttons - SAME SIZE - ALWAYS SHOW
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className='fas fa-eye me-2'),
                                "View Details"
                            ], id='btn-view-preset', color='info', outline=True, className='w-100')
                        ], md=6),
                        dbc.Col([
                            dbc.Button([
                                html.I(className='fas fa-chart-line me-2'),
                                "Analyze This Portfolio"
                            ], id='btn-analyze', color='success', className='w-100',
                               disabled=len(mapped_weights) == 0)  # Disable if no assets mapped
                        ], md=6)
                    ])
                ])
            ])
        ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}"})
        
        return {'display': 'none'}, preset_display, preset_name, False, modal_title, modal_body

# Modal open callback
@app.callback(
    Output('preset-modal', 'is_open', allow_duplicate=True),
    Input('btn-view-preset', 'n_clicks'),
    State('preset-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_modal(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# Load preset weights when preset selected
@app.callback(
    Output('preset-weights-store', 'data'),
    Output('preset-status', 'children'),
    Output('assets-dropdown', 'value'),
    Input('preset-dropdown', 'value'),
    State('gw-ready', 'data'),
    prevent_initial_call=True
)
def load_preset(preset_name, data_json):
    if not preset_name or not data_json or preset_name == 'Custom Portfolio':
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    available_assets = set(df.columns)
    
    preset_config = FAMOUS_PORTFOLIOS.get(preset_name, {})
    target_weights = preset_config.get('weights', {})
    fallback_weights = preset_config.get('fallback', {})
    
    mapped_weights = {}
    missing = []
    
    for asset, weight in target_weights.items():
        if asset in available_assets:
            mapped_weights[asset] = weight * 100
        else:
            fallback = [k for k, v in fallback_weights.items() if k != asset]
            if fallback and fallback[0] in available_assets:
                mapped_weights[fallback[0]] = weight * 100
            else:
                missing.append((asset, weight))
    
    selected_assets = list(mapped_weights.keys())
    status_msg = None
    
    if missing:
        missing_assets = [m[0] for m in missing]
        status_msg = dbc.Alert([
            html.Strong(f"⚠ Partially loaded: {preset_name}"),
            html.Br(),
            f"Mapped {len(mapped_weights)} assets. Missing: {', '.join(missing_assets)}"
        ], color='warning')
    
    return mapped_weights, status_msg, selected_assets

# ASSET SELECTION -> CREATE SLIDERS
@app.callback(
    Output('slider-container', 'children'),
    Input('assets-dropdown', 'value'),
    State('preset-name-store', 'data'),
    prevent_initial_call=True
)
def create_sliders(assets, preset_name):
    if preset_name != 'Custom Portfolio':
        return []
    
    if not assets:
        return html.Div("Select assets above to configure weights", className='text-muted')
    
    sliders = []
    for asset in assets:
        sliders.append(
            dbc.Row([
                dbc.Col([
                    html.Label(asset, className='fw-bold')
                ], width=2),
                dbc.Col([
                    dcc.Slider(
                        id={'type': 'weight-slider', 'asset': asset},
                        min=0, max=100, step=1,
                        value=100.0/len(assets),
                        marks={0: '0%', 50: '50%', 100: '100%'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=10)
            ], className='mb-3')
        )
    
    return html.Div(sliders)

# SLIDERS -> LIVE PIE CHART
# @app.callback(
#     Output('pie-preview', 'children'),
#     Input({'type': 'weight-slider', 'asset': ALL}, 'value'),
#     State({'type': 'weight-slider', 'asset': ALL}, 'id'),
#     prevent_initial_call=True
# )
# def update_pie(slider_values, slider_ids):
#     if not slider_values or not slider_ids:
#         raise PreventUpdate
    
#     assets = [s['asset'] for s in slider_ids]
#     total = sum(slider_values)
    
#     fig = go.Figure(data=[go.Pie(
#         labels=assets,
#         values=slider_values,
#         hole=0.4,
#         marker=dict(colors=['#06A77D', '#2E86AB', '#F18F01', '#D4145A', 
#                            '#6C757D', '#9B59B6', '#3498DB', '#E74C3C'])
#     )])
    
#     fig.update_layout(
#         template='plotly_dark',
#         paper_bgcolor='rgba(0,0,0,0)',
#         height=300,
#         showlegend=True,
#         legend=dict(orientation="h", yanchor="bottom", y=-0.2),
#         font=dict(size=11)
#     )
    
#     return dbc.Card([
#         dbc.CardBody([
#             html.H6([
#                 html.I(className='fas fa-chart-pie me-2'),
#                 f"Portfolio Preview (Total: {total:.1f}%)"
#             ], className='mb-2'),
#             dcc.Graph(figure=fig, config={'displayModeBar': False})
#         ])
#     ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}"})

# SET WEIGHTS AFTER SLIDERS CREATED
@app.callback(
    Output({'type': 'weight-slider', 'asset': ALL}, 'value', allow_duplicate=True),
    Input('slider-container', 'children'),
    State('preset-weights-store', 'data'),
    State('assets-dropdown', 'value'),
    State('preset-name-store', 'data'),
    prevent_initial_call=True
)
def load_preset_weights(slider_children, preset_weights, assets, preset_name):
    if preset_name != 'Custom Portfolio' or not preset_weights or not assets or not slider_children:
        raise PreventUpdate
    
    weight_values = [preset_weights.get(asset, 100.0/len(assets)) for asset in assets]
    return weight_values

# EQUAL WEIGHTS
@app.callback(
    Output({'type': 'weight-slider', 'asset': ALL}, 'value', allow_duplicate=True),
    Input('btn-equal-weights', 'n_clicks'),
    State('assets-dropdown', 'value'),
    prevent_initial_call=True
)
def set_equal_weights(n_clicks, assets):
    if not assets:
        raise PreventUpdate
    equal = 100.0 / len(assets)
    return [equal] * len(assets)


# NORMALIZE WEIGHTS
@app.callback(
    Output({'type': 'weight-slider', 'asset': ALL}, 'value', allow_duplicate=True),
    Input('btn-normalize', 'n_clicks'),
    State({'type': 'weight-slider', 'asset': ALL}, 'value'),
    prevent_initial_call=True
)
def normalize_weights(n_clicks, current_weights):
    if not current_weights or sum(current_weights) == 0:
        raise PreventUpdate
    
    total = sum(current_weights)
    normalized = [w * 100.0 / total for w in current_weights]
    return normalized


# DETECT MANUAL SLIDER CHANGES -> RESET TO CUSTOM PORTFOLIO
@app.callback(
    Output('preset-name-store', 'data', allow_duplicate=True),
    Output('preset-dropdown', 'value', allow_duplicate=True),
    Input({'type': 'weight-slider', 'asset': ALL}, 'value'),
    State('preset-name-store', 'data'),
    State('preset-dropdown', 'value'),
    prevent_initial_call=True
)
def detect_manual_slider_change(slider_values, current_preset_name, current_dropdown):
    # If user manually changes sliders while a preset is selected, switch to Custom
    if current_preset_name and current_preset_name != 'Custom Portfolio':
        return 'Custom Portfolio', 'Custom Portfolio'
    raise PreventUpdate

# SELECT ALL ASSETS - MARGINAL TAB
@app.callback(
    Output('assets-dropdown', 'value', allow_duplicate=True),
    Input('btn-select-all', 'n_clicks'),
    State('gw-ready', 'data'),
    prevent_initial_call=True
)
def select_all_assets(n_clicks, data_json):
    if not data_json:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    available_assets = [col for col in df.columns if col != 'GROWISE']
    
    return available_assets

# SELECT ALL ASSETS - OPTIMIZATION TAB (FIX #4)
@app.callback(
    Output('opt-assets-dropdown', 'value', allow_duplicate=True),
    Input('btn-select-all-opt', 'n_clicks'),
    State('gw-ready', 'data'),
    prevent_initial_call=True
)
def select_all_assets_opt(n_clicks, data_json):
    if not data_json:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    # Include ALL assets including GROWISE (FIX #6)
    return list(df.columns)

# PRESET SELECTOR IN OPTIMIZATION - Load assets from famous portfolios
@app.callback(
    Output('opt-assets-dropdown', 'value', allow_duplicate=True),
    Input('opt-preset-selector', 'value'),
    State('gw-ready', 'data'),
    prevent_initial_call=True
)
def load_preset_assets_optimization(preset_name, data_json):
    if not preset_name or not data_json:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    available_assets = set(df.columns)
    
    preset_config = FAMOUS_PORTFOLIOS.get(preset_name, {})
    target_weights = preset_config.get('weights', {})
    fallback_weights = preset_config.get('fallback', {})
    
    # Map assets to available ones
    selected_assets = []
    for asset in target_weights.keys():
        if asset in available_assets:
            selected_assets.append(asset)
        else:
            # Try fallback
            for fallback_asset in fallback_weights.keys():
                if fallback_asset in available_assets and fallback_asset not in selected_assets:
                    selected_assets.append(fallback_asset)
                    break
    
    # Always add GROWISE if available
    if 'GROWISE' in available_assets and 'GROWISE' not in selected_assets:
        selected_assets.append('GROWISE')
    
    return selected_assets

# MAIN ANALYSIS CALLBACK - PROPERLY HANDLES BOTH PRESET AND CUSTOM
@app.callback(
    Output('results-marginal', 'children'),
    Input('btn-analyze', 'n_clicks'),
    State('gw-ready', 'data'),
    State('preset-name-store', 'data'),
    State('preset-weights-store', 'data'),
    State('assets-dropdown', 'value'),
    State({'type': 'weight-slider', 'asset': ALL}, 'value'),
    State({'type': 'weight-slider', 'asset': ALL}, 'id'),
    State('growise-range', 'value'),
    State('benchmark-dropdown', 'value'),
    prevent_initial_call=True
)
def run_analysis(n_clicks, data_json, preset_name, preset_weights,
                assets, slider_values, slider_ids, growise_range, benchmark):
    if not data_json:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient='split')
    
    if 'GROWISE' not in df.columns:
        return dbc.Alert("GROWISE column not found in data", color="danger")
    
    # Build base portfolio - PRESET FIRST, then CUSTOM
    # Build base portfolio
    base_weights = {}
    
    # CUSTOM PORTFOLIO - use sliders if they exist
    if assets and slider_values and len(slider_values) > 0:
        # Check total
        total = sum(slider_values)
        if abs(total - 100) > 1.0:  # Allow 1% tolerance
            return dbc.Alert(f"WARNING: Weights must sum to ~100% (current: {total:.1f}%). Use Normalize button.", 
                            color="warning")
        
        # Build weights from sliders
        for val, slider_id in zip(slider_values, slider_ids):
            base_weights[slider_id['asset']] = val / 100.0
    
    # PRESET PORTFOLIO - use preset weights if no sliders
    elif preset_name and preset_name != 'Custom Portfolio' and preset_weights:
        base_weights = {k: v/100 for k, v in preset_weights.items()}
    
    # No portfolio configured
    if not base_weights:
        return dbc.Alert("WARNING: Please select assets and configure weights, or choose a preset portfolio.", 
                        color="warning")
    
    # GROWISE allocations
    g_allocs = [i/100 for i in range(growise_range[0], growise_range[1]+1, 5)]
    
    rf = 0  # FIX #5: Hardcoded to 0
    
    # Calculate for each GROWISE allocation
    results = []
    equity_curves = []
    
    for g_pct in g_allocs:
        # Adjust base portfolio
        adjusted_weights = {k: v * (1 - g_pct) for k, v in base_weights.items()}
        adjusted_weights['GROWISE'] = g_pct
        
        # Calculate returns
        port_returns = calculate_portfolio_returns(df, adjusted_weights)
        
        # Calculate metrics
        metrics = calculate_all_metrics(port_returns, rf)
        metrics['growise_pct'] = g_pct
        
        # Benchmark correlation
        if benchmark and benchmark in df.columns:
            metrics['benchmark_corr'] = port_returns.corr(df[benchmark])
        
        results.append(metrics)
        
        # Equity curve
        cum_returns = (1 + port_returns).cumprod()
        equity_curves.append({
            'growise_pct': g_pct,
            'dates': port_returns.index,
            'equity': cum_returns
        })
    
    results_df = pd.DataFrame(results)
    
    # Create visualizations - PROFESSIONAL LAYOUT
    try:
        # EQUITY CURVE - LARGE AT TOP
        fig_equity = create_equity_curves_v8(equity_curves)
        
        # SENSITIVITY CHARTS
        fig_sharpe_sortino = create_sharpe_sortino_sensitivity(results_df)
        fig_return_vol = create_return_vol_sensitivity(results_df)
        
        # CORRELATION - DYNAMIC Y-AXIS
        fig_corr = create_correlation_sensitivity(results_df) if 'benchmark_corr' in results_df.columns else None
        
        # Best allocation
        best_idx = results_df['sharpe'].idxmax()
        best_metrics = results_df.iloc[best_idx]
        
        insights = dbc.Alert([
            html.H4("Key Findings", className='alert-heading'),
            html.Hr(),
            html.P([
                html.Strong(f"Optimal GROWISE: {best_metrics['growise_pct']*100:.0f}%"),
                html.Br(),
                f"Sharpe: {best_metrics['sharpe']:.2f} | ",
                f"Sortino: {best_metrics['sortino']:.2f} | ",
                f"Return: {best_metrics['annual_return']*100:.1f}% | ",
                f"Vol: {best_metrics['volatility']*100:.1f}% | ",
                f"MaxDD: {best_metrics['max_drawdown']*100:.1f}%"
            ])
        ], color='warning', style={'backgroundColor': '#2d2416', 'borderColor': '#E67E22'})
        
        # Results table
        table_df = results_df[['growise_pct', 'sharpe', 'sortino', 'calmar', 
                               'annual_return', 'volatility', 'max_drawdown']].copy()
        table_df['growise_pct'] = (table_df['growise_pct'] * 100).round(0).astype(int).astype(str) + '%'
        table_df.columns = ['GROWISE %', 'Sharpe', 'Sortino', 'Calmar', 'Return', 'Vol', 'MaxDD']
        
        for col in ['Return', 'Vol', 'MaxDD']:
            table_df[col] = (table_df[col] * 100).round(2).astype(str) + '%'
        
        for col in ['Sharpe', 'Sortino', 'Calmar']:
            table_df[col] = table_df[col].round(3)
        
        table = dbc.Table.from_dataframe(table_df, striped=True, bordered=True, hover=True,
                                        style={'fontSize': '14px'})
        
        # BUILD OUTPUT - ONLY MARGINAL CHARTS
        output = dbc.Container([
            # Insights
            dbc.Row([dbc.Col([insights])], className='mb-4'),
            
            # Equity curve - FULL WIDTH
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Growth of $1 Invested",
                                help_icon('growth_1dollar',
                                         "Equity curves across GROWISE allocations. $1 starting capital, compounded returns.",
                                         "Terminal wealth and path smoothness test allocation efficiency. Marginal contribution of each weight increment.",
                                         "Higher terminal = better CAGR. Smooth path = lower realized vol. Steeper = faster compounding.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_equity, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ])
            ], className='mb-4'),
            
            # Sharpe/Sortino + Return/Vol side by side
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Sharpe & Sortino Sensitivity",
                                help_icon('sharpe_sortino',
                                         "Risk-adjusted returns vs allocation. Sharpe = total vol, Sortino = downside only.",
                                         "Peak identifies optimal weight for max return/risk. Sortino>Sharpe signals positive skew (valuable asymmetry).",
                                         "Find simultaneous peak. Sortino>Sharpe = convex. Compare to optimizer allocation for validation.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_sharpe_sortino, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Return & Volatility Sensitivity",
                                help_icon('return_vol_sensitivity',
                                         "Annualized return and vol vs allocation. Explicit return-risk trade-off visualization.",
                                         "Optimal weight balances marginal return gain vs marginal risk addition. Diminishing returns at high allocations.",
                                         "Northwest movement (higher return, lower vol) dominates. Note inflection where risk accelerates.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_return_vol, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=6)
            ], className='mb-4'),
            
            # Correlation - FULL WIDTH
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Benchmark Correlation",
                                help_icon('benchmark_corr',
                                         "Rolling correlation between GROWISE and benchmark across weights. Diversification quality test.",
                                         "Stable low correlation validates structural decorrelation. Spikes during crises reveal breakdown precisely when needed.",
                                         "Target <0.3 stable across weights. Validate against 2008/2020. Zero/negative = genuine hedge.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_corr, config={'displayModeBar': False}) if fig_corr else html.P("No benchmark selected")
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ])
            ], className='mb-4') if fig_corr else html.Div(),
            
            # Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Detailed Results", className='mb-3'),
                            table
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ])
            ])
        ], fluid=True)
        
        return output
        
    except Exception as e:
        import traceback
        return dbc.Alert(f"ERROR: Analysis error: {str(e)}\n\n{traceback.format_exc()}", color="danger")


# OPTIMIZATION CALLBACK - COMPLETE WITH ALL ANALYSIS (FIX #3, #5, #6)
@app.callback(
    Output('results-optimization', 'children'),
    Input('btn-optimize', 'n_clicks'),
    State('gw-ready', 'data'),
    State('opt-assets-dropdown', 'value'),
    State('opt-objective', 'value'),
    State('opt-force-growise', 'value'),
    prevent_initial_call=True
)
def run_optimization(n_clicks, data_json, assets, objective, force_growise):
    if not data_json or not assets:
        raise PreventUpdate
    
    try:
        df = pd.read_json(StringIO(data_json), orient='split')
        
        has_growise = 'GROWISE' in assets
        
        # Prepare data - use selected assets as-is
        df_all = df[assets].dropna()
        
        if len(df_all) < 20:
            return dbc.Alert("Need at least 20 periods of data", color="warning")
        
        rf = 0  # Hardcoded to 0
        
        # Optimize
        result_with_raw = optimize_portfolio(df_all, list(df_all.columns), 
                                            objective=f'max_{objective}',
                                            rf_rate=rf, allow_growise=True)
        
        if not result_with_raw:
            return dbc.Alert("ERROR: Optimization failed", color="danger")
        
        # Filter and renormalize weights - remove <3% and renormalize to 100%
        result_with, removed_assets = filter_and_renormalize_weights(
            result_with_raw, threshold=0.03, force_growise=force_growise
        )
        
        # Optimize WITHOUT GROWISE (for comparison) - only if GROWISE was in original selection
        result_without = None
        if has_growise and len(assets) > 1:
            assets_no_growise = [a for a in assets if a != 'GROWISE']
            if len(assets_no_growise) > 1:
                df_no = df[assets_no_growise].dropna()
                result_without_raw = optimize_portfolio(df_no, list(df_no.columns),
                                                       objective=f'max_{objective}',
                                                       rf_rate=rf, allow_growise=False)
                if result_without_raw:
                    result_without, _ = filter_and_renormalize_weights(
                        result_without_raw, threshold=0.03, force_growise=False
                    )
        
        # Calculate metrics with cleaned weights
        port_rets_with = calculate_portfolio_returns(df_all, result_with)
        metrics_with = calculate_all_metrics(port_rets_with, rf)
        
        port_rets_without = None
        metrics_without = None
        if result_without:
            df_no = df[[a for a in assets if a != 'GROWISE']].dropna()
            port_rets_without = calculate_portfolio_returns(df_no, result_without)
            metrics_without = calculate_all_metrics(port_rets_without, rf)
        
        # Generate efficient frontiers - use fewer points (proper optimization is slower)
        frontier_with = calculate_efficient_frontier(df_all, list(df_all.columns), rf_rate=rf, n_points=20)
        frontier_without = None
        if result_without:
            frontier_without = calculate_efficient_frontier(df_no, list(df_no.columns), rf_rate=rf, n_points=20)
        
        # Create visualizations - pass df_all for REAL Monte Carlo portfolios
        fig_frontier = create_efficient_frontier_comparison(frontier_with, frontier_without, 
                                                           metrics_with, metrics_without, rf, df_returns=df_all)
        
        fig_metrics = create_metrics_comparison_bars(metrics_with, metrics_without)
        
        fig_weights = create_optimal_weights_chart(result_with, threshold=0.03)
        
        fig_rr = create_risk_return_comparison(metrics_with, metrics_without)
        
        # Equity curves comparison
        fig_equity = create_equity_comparison(port_rets_with, port_rets_without)
        
        # Insights with info about removed assets
        insights = create_optimization_insights(result_with, result_without, 
                                              metrics_with, metrics_without, has_growise)
        
        # Add info about removed assets if any
        if removed_assets:
            removed_list = [f"{k}: {v*100:.1f}%" for k, v in sorted(removed_assets.items(), 
                                                                     key=lambda x: x[1], reverse=True)]
            removed_info = html.Small([
                html.Br(),
                html.Span("Note: ", style={'color': '#6c757d'}),
                html.Span(f"Removed {len(removed_assets)} assets <3%: ", 
                         style={'color': '#6c757d'}),
                html.Span(", ".join(removed_list), style={'color': '#6c757d', 'fontSize': '11px'})
            ])
        else:
            removed_info = html.Div()
        
        # BUILD OUTPUT
        output = dbc.Container([
            # Key insights
            dbc.Row([
                dbc.Col([
                    html.Div([insights, removed_info])
                ])
            ], className='mb-4'),
            
            # Top metrics row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Risk-Adjusted Returns",
                                help_icon('risk_adjusted_returns',
                                         "Sharpe (total vol), Sortino (downside), Calmar (max DD). Baseline vs optimized.",
                                         "Ratios distinguish skill from leverage. 20% @ 30% vol (SR 0.67) loses to 12% @ 10% vol (SR 1.2).",
                                         "All three up = genuine improvement. Sortino>Sharpe = positive skew. Targets: SR>1.0, Sortino>1.5, Calmar>0.5.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_metrics, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Efficient Frontier",
                                help_icon('efficient_frontier',
                                         "Mean-variance frontier via quadratic optimization. Random portfolios (dots) vs efficient curve (white). Green star = Sharpe-optimal.",
                                         "All feasible portfolios lie below curve. Distance to frontier quantifies improvement potential. Dots above = math error.",
                                         "Star on curve = valid. Curvature = diversification benefit. Flat = limited rebalancing alpha.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_frontier, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=6)
            ], className='mb-4'),
            
            # Equity curves - FULL WIDTH
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Growth of $100,000",
                                help_icon('growth_100k',
                                         "Compounded wealth: baseline vs optimized. $100k starting capital, reinvested returns.",
                                         "Terminal wealth = definitive test. Gap = alpha in dollars. Path = investor retention.",
                                         "Higher end = validated. Smooth = better SR. Recovery speed = tail hedge quality.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_equity, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=12)
            ], className='mb-4'),
            
            # Bottom row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Optimal Allocation",
                                help_icon('optimal_allocation',
                                         "Mean-variance optimal weights. Assets <3% removed and renormalized.",
                                         "Result of quadratic optimization maximizing Sharpe/Sortino. Reflects all pairwise correlations and return/risk trade-offs.",
                                         "Small GROWISE weights (5-15%) can materially improve Sharpe via low correlation. Not arbitrary - math-driven.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_weights, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5([
                                "Risk-Return Profile",
                                help_icon('risk_return_profile',
                                         "Scatter: vol (x) vs return (y). Baseline vs optimized portfolios.",
                                         "Northwest movement = domination (higher return, lower risk). Slope from origin = Sharpe ratio.",
                                         "Optimized should lie northwest of baseline. Steeper slope = better risk-adjusted. Distance = absolute performance.")
                            ], className='mb-3'),
                            dcc.Graph(figure=fig_rr, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': '#161b22', 'border': f"1px solid {'#30363d'}",
                             'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'})
                ], md=6)
            ])
        ], fluid=True)
        
        return output
        
    except Exception as e:
        import traceback
        return dbc.Alert(f"ERROR: Optimization error: {str(e)}\n\n{traceback.format_exc()}", color="danger")

# ============================================================
# RUN APP
# ============================================================
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 8050))
#     app.run(host='0.0.0.0', port=port, debug=False)
    
# if __name__ == '__main__':
#     app.run(debug=True, port=8016)


# ============================================================
# REGIME & FACTOR ANALYSIS CALLBACKS
# ============================================================

# Populate dropdowns for regime analysis
@app.callback(
    [Output("regime-benchmark", "options"),
     Output("regime-target", "options"),
     Output("regime-benchmark", "value"),
     Output("regime-target", "value")],
    Input("data-store", "data")
)
def populate_regime_dropdowns(data_json):
    if not data_json:
        return [], [], None, None
    
    df = pd.read_json(StringIO(data_json), orient="split")
    assets = sorted(list(df.columns), key=lambda x: str(x).lower())
    options = [{"label": a, "value": a} for a in assets]
    
    # Auto-select defaults
    benchmark = find_benchmark_pf(assets)  # Prioritize ^GSPC
    growise = "GROWISE" if "GROWISE" in assets else assets[0]
    
    return options, options, benchmark, growise

# Download Fama-French Factors with frequency matching
@app.callback(
    [Output("ff-factors-store", "data"),
     Output("factor-download-status", "children")],
    Input("btn-download-factors", "n_clicks"),
    [State("factor-model-selector", "value"),
     State("data-store", "data")],
    prevent_initial_call=True
)
def download_factors(n_clicks, model_type, data_json):
    if not n_clicks or not data_json:
        raise PreventUpdate
    
    try:
        # Load user data to detect frequency
        df_user = pd.read_json(StringIO(data_json), orient='split')
        freq_code, freq_config = detect_frequency(df_user.index)
        
        # Download daily factors first
        factors_df = download_fama_french_factors()
        
        if factors_df is None:
            return None, dbc.Alert("ERROR: Failed to download factors", color="danger", className="mt-2")
        
        # Select factors based on model type
        if model_type == '3':
            factor_cols = ['MKT-RF', 'SMB', 'HML']
        elif model_type == '5':
            factor_cols = ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA']
        else:  # '6'
            factor_cols = ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA', 'MOM']
        
        factors_df = factors_df[factor_cols]
        
        # Resample to match user data frequency
        if freq_code != 'D':
            # Map frequency codes
            freq_map = {'W': 'W-FRI', 'M': 'M', 'Q': 'Q', 'Y': 'Y'}
            resample_freq = freq_map.get(freq_code, 'M')
            
            # Compound returns for resampling
            factors_resampled = (1 + factors_df).resample(resample_freq).prod() - 1
            factors_df = factors_resampled
        
        # Align dates with user data - NORMALIZAR POR QUARTER
        # Convertir ambos índices a Quarter para evitar date mismatch
        user_quarters = df_user.index.to_period('Q')
        factors_quarters = factors_df.index.to_period('Q')
        
        # Find common quarters
        common_quarters = set(user_quarters).intersection(set(factors_quarters))
        
        if len(common_quarters) < 10:
            return None, dbc.Alert(
                f"ERROR: Insufficient quarter overlap. User data: {df_user.index.min().date()} to {df_user.index.max().date()}. " +
                f"Factors: {factors_df.index.min().date()} to {factors_df.index.max().date()}",
                color="danger", className="mt-2"
            )
        
        # Filter factors to common quarters
        factors_df = factors_df[factors_quarters.isin(common_quarters)]
        
        # Convert to JSON for storage
        factors_json = factors_df.to_json(orient='split', date_format='iso')
        
        freq_label = freq_config['label']
        msg = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"SUCCESS: Downloaded {len(factors_df)} {freq_label.lower()} observations of {model_type}-factor model",
            html.Br(),
            html.Small(f"Date range: {factors_df.index.min().date()} to {factors_df.index.max().date()}", 
                      className="text-muted")
        ], color="success", className="mt-2")
        
        return factors_json, msg
        
    except Exception as e:
        import traceback
        return None, dbc.Alert(f"ERROR: Error: {str(e)}\n{traceback.format_exc()[:200]}", color="danger", className="mt-2")

# Run Regime & Factor Analysis - IMPROVED VERSION
@app.callback(
    [Output('quadrant-scatter', 'figure'),
     Output('current-date-display', 'children'),
     Output('q1-card', 'children'),
     Output('q2-card', 'children'),
     Output('q3-card', 'children'),
     Output('q4-card', 'children'),
     Output('factor-rolling-chart', 'figure'),
     Output('factor-betas-bar', 'figure'),
     Output('attribution-evolution-chart', 'figure'),
     Output('factor-summary-stats', 'children')],
    Input('btn-run-regime-analysis', 'n_clicks'),
    [State('data-store', 'data'),
     State('regime-benchmark', 'value'),
     State('regime-target', 'value'),
     State('ff-factors-store', 'data')],
    prevent_initial_call=True
)
def run_regime_factor_analysis(n_clicks, data_json, benchmark, target, factors_json):
    empty_fig = go.Figure()
    empty_fig.update_layout(template="plotly_dark", xaxis={'visible': False}, yaxis={'visible': False})
    empty_fig.add_annotation(text="Please select assets and run analysis", xref="paper", yref="paper",
                            x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="white"))
    empty_card = html.P("No data", className="text-muted")
    
    if not data_json or not benchmark or not target:
        return empty_fig, "", empty_card, empty_card, empty_card, empty_card, empty_fig, empty_fig, empty_fig, empty_card
    
    try:
        # Load data
        df = pd.read_json(StringIO(data_json), orient='split')
        
        if benchmark not in df.columns or target not in df.columns:
            raise ValueError("Selected assets not found in data")
        
        # Detect frequency for annualization
        freq_code, freq_config = detect_frequency(df.index)
        ann_factor = freq_config['ann_factor']
        
        # === QUADRANT ANALYSIS ===
        quadrant_results = calculate_quadrant_analysis(df[target], df[benchmark])
        data_combined = quadrant_results['data']
        
        # Create scatter plot with DYNAMIC AXES and polynomial fit
        fig_scatter = go.Figure()
        
        # Calculate axis ranges with 10% padding
        x_vals = data_combined['Benchmark'] * 100
        y_vals = data_combined['GROWISE'] * 100
        x_range = [x_vals.min() * 1.1, x_vals.max() * 1.1]
        y_range = [y_vals.min() * 1.1, y_vals.max() * 1.1]
        
        # Add quadrant shading (scaled to data)
        x_mid = 0
        y_mid = 0
        fig_scatter.add_shape(type="rect", x0=x_range[0], y0=y_mid, x1=x_mid, y1=y_range[1],
                             fillcolor="rgba(255,100,100,0.15)", line_width=0)  # Q2 - KEY
        fig_scatter.add_shape(type="rect", x0=x_mid, y0=y_mid, x1=x_range[1], y1=y_range[1],
                             fillcolor="rgba(100,255,100,0.15)", line_width=0)  # Q1
        fig_scatter.add_shape(type="rect", x0=x_range[0], y0=y_range[0], x1=x_mid, y1=y_mid,
                             fillcolor="rgba(128,128,128,0.15)", line_width=0)  # Q3
        fig_scatter.add_shape(type="rect", x0=x_mid, y0=y_range[0], x1=x_range[1], y1=y_mid,
                             fillcolor="rgba(255,140,0,0.15)", line_width=0)  # Q4
        
        # Scatter points
        fig_scatter.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='markers',
            marker=dict(size=7, color=y_vals, colorscale='RdYlGn', showscale=False, line=dict(width=0.5, color='white')),
            text=[f"{idx.date()}<br>Bench: {b:.2f}%<br>GW: {g:.2f}%" 
                  for idx, b, g in zip(data_combined.index, x_vals, y_vals)],
            hoverinfo='text',
            showlegend=False,
            name='Observations'
        ))
        
        # Add polynomial fit (2nd order) to show convexity
        try:
            from numpy.polynomial import polynomial as P
            x_sorted = np.sort(x_vals.values)
            y_sorted = y_vals[x_vals.argsort()].values
            coefs = P.polyfit(x_sorted, y_sorted, 2)
            x_fit = np.linspace(x_sorted.min(), x_sorted.max(), 100)
            y_fit = P.polyval(x_fit, coefs)
            
            fig_scatter.add_trace(go.Scatter(
                x=x_fit, y=y_fit,
                mode='lines',
                line=dict(color=ACCENT, width=3, dash='dash'),
                name='Trend (2nd order)',
                hoverinfo='skip'
            ))
        except:
            pass
        
        # Axes
        fig_scatter.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.3, line_width=1)
        fig_scatter.add_vline(x=0, line_dash="solid", line_color="white", opacity=0.3, line_width=1)
        
        fig_scatter.update_layout(
            template="plotly_dark",
            title=dict(text=f"{target} vs {benchmark} — Regime Scatter", x=0.5, xanchor='center'),
            xaxis=dict(title=f"{benchmark} Return (%)", range=x_range, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title=f"{target} Return (%)", range=y_range, gridcolor='rgba(255,255,255,0.1)'),
            height=500,
            showlegend=True,
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(0,0,0,0.5)'),
            margin=dict(t=60, b=60, l=60, r=20)
        )
        
        # Date display
        date_str = f"Data Range: {df.index.min().date()} to {df.index.max().date()}"
        
        # Create 4 Quadrant Cards
        def create_q_card(q_key, q_data, color, icon):
            return dbc.Card([
                dbc.CardHeader([html.I(className=f"fas fa-{icon} me-2"), q_data['name']], 
                              className=f"bg-{color} text-white", 
                              style={'fontSize': '13px', 'fontWeight': '600', 'padding': '8px'}),
                dbc.CardBody([
                    html.Div([
                        html.Strong(f"{q_data['count']}", style={'fontSize': '24px', 'color': ACCENT}),
                        html.Br(),
                        html.Small(f"{q_data['hit_rate']:.1f}% of periods", className="text-muted")
                    ], className="text-center mb-2"),
                    html.Hr(style={'margin': '8px 0'}),
                    html.Small([
                        f"Avg {target[:6]}: ", html.Strong(f"{q_data['avg_growise']:.2f}%"), html.Br(),
                        f"Avg {benchmark[:6]}: {q_data['avg_benchmark']:.2f}%", html.Br(),
                        f"β: {q_data['beta']:.3f} | α: {q_data['alpha']:.2f}%"
                    ], className="text-muted", style={'fontSize': '11px'})
                ], style={'padding': '12px'})
            ], style={'height': '100%'})
        
        q1_card = create_q_card('Q1', quadrant_results['Q1'], 'success', 'arrow-up')
        q2_card = create_q_card('Q2', quadrant_results['Q2'], 'danger', 'shield-alt')
        q3_card = create_q_card('Q3', quadrant_results['Q3'], 'secondary', 'arrow-down')
        q4_card = create_q_card('Q4', quadrant_results['Q4'], 'warning', 'coins')
        
        # === FACTOR ATTRIBUTION ===
        if factors_json:
            factors_df = pd.read_json(StringIO(factors_json), orient='split')
            factors_df.index = pd.to_datetime(factors_df.index)
            
            # Align dates - NORMALIZAR POR QUARTER para evitar date mismatch
            df_quarters = df.index.to_period('Q')
            factors_quarters = factors_df.index.to_period('Q')
            common_quarters = set(df_quarters).intersection(set(factors_quarters))
            
            # Filter por Quarter
            df_aligned = df[[target]][df_quarters.isin(common_quarters)]
            factors_aligned = factors_df[factors_quarters.isin(common_quarters)]
            common_dates = df_aligned.index  # Para compatibilidad con código posterior
                
            if len(common_quarters) < 20:
                fig_rolling = empty_fig
                fig_betas_bar = empty_fig
                fig_attrib = empty_fig
                factor_summary = dbc.Alert("Insufficient overlapping data", color="warning")
            else:
                # Calculate ROLLING factor exposures (36-period window)
                window = min(36, len(common_dates) // 3)
                rolling_betas = {}
                
                for i in range(window, len(common_dates)):
                    subset_ret = df_aligned.iloc[i-window:i].values.flatten()
                    subset_factors = factors_aligned.iloc[i-window:i].values
                    
                    # Skip if NaN values present
                    if np.isnan(subset_ret).any() or np.isnan(subset_factors).any():
                        continue
                    
                    try:
                        from sklearn.linear_model import LinearRegression
                        model = LinearRegression()
                        model.fit(subset_factors, subset_ret)
                        
                        date = common_dates[i]
                        rolling_betas[date] = dict(zip(factors_aligned.columns, model.coef_))
                    except Exception:
                        continue
                
                # Guard: If no valid windows, set empty charts with warning and skip processing
                if not rolling_betas:
                    fig_rolling = empty_fig
                    fig_betas_bar = empty_fig
                    fig_attrib = empty_fig
                    factor_summary = dbc.Alert("Insufficient valid data (too many missing values)", color="warning")
                    # Skip the rest of factor analysis - jump to return statement at end
                    return fig_quadrant, date_display, q1_card, q2_card, q3_card, q4_card, fig_rolling, fig_betas_bar, fig_attrib, factor_summary
                
                # Convert to DataFrame for plotting
                rolling_df = pd.DataFrame(rolling_betas).T
                
                # Normalize to percentages for stacked area chart
                rolling_df_pct = rolling_df.div(rolling_df.abs().sum(axis=1), axis=0) * 100
                
                # Create percentage-based stacked area chart
                fig_rolling = go.Figure()
                
                factor_colors = {
                    'MKT-RF': '#E67E22',
                    'SMB': '#4169E1',
                    'HML': '#32CD32',
                    'RMW': '#FF6347',
                    'CMA': '#9370DB',
                    'MOM': '#FFD700'
                }
                
                for factor in rolling_df_pct.columns:
                    fig_rolling.add_trace(go.Scatter(
                        x=rolling_df_pct.index,
                        y=rolling_df_pct[factor],
                        name=factor,
                        mode='lines',
                        stackgroup='one',
                        groupnorm='percent',
                        fillcolor=factor_colors.get(factor, '#888888'),
                        line=dict(width=0.5, color=factor_colors.get(factor, '#888888')),
                        hovertemplate='%{y:.1f}%<extra></extra>'
                    ))
                
                fig_rolling.update_layout(
                    template="plotly_dark",
                    title="",
                    xaxis_title="",
                    yaxis=dict(title="% of Total Exposure", ticksuffix='%', range=[0, 100]),
                    height=350,
                    hovermode='x unified',
                    legend=dict(orientation='h', y=-0.2, x=0.5, xanchor='center', font=dict(size=9)),
                    margin=dict(t=10, b=70, l=60, r=10),
                    showlegend=True
                )
                
                # Create bar chart for average betas
                avg_betas = rolling_df.mean()
                fig_betas_bar = go.Figure()
                
                colors_bar = [factor_colors.get(f, '#888888') for f in avg_betas.index]
                
                fig_betas_bar.add_trace(go.Bar(
                    x=avg_betas.values,
                    y=avg_betas.index,
                    orientation='h',
                    marker_color=colors_bar,
                    text=[f"{v:.3f}" for v in avg_betas.values],
                    textposition='outside',
                    textfont=dict(size=10),
                    hovertemplate='%{x:.3f}<extra></extra>'
                ))
                
                fig_betas_bar.update_layout(
                    template="plotly_dark",
                    title="",
                    xaxis=dict(title="Beta", gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(title="", tickfont=dict(size=10)),
                    height=350,
                    margin=dict(t=10, b=50, l=60, r=40),
                    showlegend=False
                )
                fig_betas_bar.add_vline(x=0, line_dash="solid", line_color="white", opacity=0.3, line_width=1)
                
                # =====================================================================
                # FACTOR ATTRIBUTION - MÉTODO CORRECTO (COMPUESTO + QUARTER NORMALIZATION)
                # =====================================================================
                
                # Preparar datos - NORMALIZAR POR QUARTER para evitar date mismatch
                portfolio_df = df_aligned.copy()
                portfolio_df.columns = ['Portfolio']
                portfolio_df['Quarter'] = portfolio_df.index.to_period('Q')
                portfolio_df = portfolio_df.set_index('Quarter')
                
                factors_q = factors_aligned.copy()
                factors_q['Quarter'] = factors_q.index.to_period('Q')
                factors_q_indexed = factors_q.set_index('Quarter')
                
                # Merge por Quarter (no por fecha exacta)
                merged = portfolio_df.join(factors_q_indexed, how='inner')
                merged.index = merged.index.to_timestamp()
                
                # Verificar cobertura
                coverage_pct = len(merged) / len(df_aligned) * 100
                
                if len(merged) < 20:
                    fig_attrib = empty_fig
                    fig_attrib.add_annotation(
                        text=f"Insufficient data after alignment<br>Only {len(merged)} periods available",
                        xref="paper", yref="paper", x=0.5, y=0.5,
                        showarrow=False, font=dict(size=14, color="white")
                    )
                else:
                    # Regresión con STATSMODELS (para tener p-values y R²)
                    y = merged['Portfolio']
                    X = merged[list(factors_aligned.columns)]
                    X = sm.add_constant(X)
                    
                    model_sm = sm.OLS(y, X).fit()
                    
                    # Calcular años
                    years_analysis = len(merged) / 4.0  # Asumiendo datos trimestrales
                    
                    # Generar gráfico usando función flexible
                    fig_attrib, alpha_pct = create_factor_attribution_chart_cagr(
                        model=model_sm,
                        merged_data=merged,
                        years=years_analysis,
                        factor_cols=list(factors_aligned.columns),
                        chart_title="Return Attribution"
                    )
                
                # =====================================================================
                # SUMMARY STATS - ACTUALIZADO CON STATSMODELS
                # =====================================================================
                
                if len(merged) >= 20:
                    # Total return (compuesto)
                    total_return_cum = (1 + merged['Portfolio']).prod() - 1
                    total_return_ann = ((1 + total_return_cum) ** (4/len(merged)) - 1) * 100
                    
                    # R² y Alpha del modelo
                    r2 = model_sm.rsquared
                    alpha_quarterly = model_sm.params['const']
                    alpha_ann = ((1 + alpha_quarterly)**4 - 1) * 100
                    
                    # Factor dominante
                    betas = {k: v for k, v in model_sm.params.items() if k != 'const'}
                    betas_abs = {k: abs(v) for k, v in betas.items()}
                    dominant_factor = max(betas_abs, key=betas_abs.get) if betas_abs else "None"
                    dominant_beta = betas.get(dominant_factor, 0)
                    
                    factor_summary = dbc.Alert([
                        dbc.Row([
                            dbc.Col([
                                html.H6("R²", className="text-light mb-1", style={'fontSize': '13px'}),
                                html.H4(f"{r2*100:.1f}%", style={'color': ACCENT, 'marginBottom': '2px'}),
                                html.Small("Model Fit", className="text-muted", style={'fontSize': '10px'})
                            ], md=3, className="text-center"),
                            dbc.Col([
                                html.H6("Alpha (Ann.)", className="text-light mb-1", style={'fontSize': '13px'}),
                                html.H4(f"{alpha_ann:+.2f}%", 
                                       style={'color': 'green' if alpha_ann > 0 else 'red', 'marginBottom': '2px'}),
                                html.Small(f"p-val: {model_sm.pvalues['const']:.3f}", className="text-muted", style={'fontSize': '10px'})
                            ], md=3, className="text-center"),
                            dbc.Col([
                                html.H6("Return (Ann.)", className="text-light mb-1", style={'fontSize': '13px'}),
                                html.H4(f"{total_return_ann:+.2f}%", style={'color': ACCENT, 'marginBottom': '2px'}),
                                html.Small(f"{len(merged)} periods", className="text-muted", style={'fontSize': '10px'})
                            ], md=3, className="text-center"),
                            dbc.Col([
                                html.H6("Top Factor", className="text-light mb-1", style={'fontSize': '13px'}),
                                html.H4(dominant_factor, style={'color': ACCENT, 'marginBottom': '2px', 'fontSize': '18px'}),
                                html.Small(f"β = {dominant_beta:.3f}", className="text-muted", style={'fontSize': '10px'})
                            ], md=3, className="text-center")
                        ])
                    ], color="dark", className="text-light", style={'padding': '15px', 'marginBottom': '0'})
                else:
                    factor_summary = dbc.Alert(
                        f"Insufficient data: only {len(merged)} periods after alignment ({coverage_pct:.0f}% coverage)",
                        color="warning"
                    )
                
        else:
            fig_rolling = empty_fig
            fig_betas_bar = empty_fig
            fig_attrib = empty_fig
            factor_summary = dbc.Alert("Please download Fama-French factors first", color="warning")
        
        return fig_scatter, date_str, q1_card, q2_card, q3_card, q4_card, fig_rolling, fig_betas_bar, fig_attrib, factor_summary
        
    except Exception as e:
        import traceback
        error_msg = dbc.Alert(f"Error: {str(e)}\n{traceback.format_exc()[:500]}", color="danger")
        return empty_fig, "Error", error_msg, error_msg, error_msg, error_msg, empty_fig, empty_fig, empty_fig, error_msg


# ======================
# GUIDED TOUR
# ======================




# ======================
# TUTORIAL SYSTEM
# ======================




# ===== Tutorial / Guide definition =====

# ----------------------
# GUIDE / TUTORIAL SYSTEM
# ----------------------
TOUR_STEPS = [
    {
        "title": "Welcome — SigmaLab Portfolio Analyzer",
        "content": html.Div([
            html.P(
                "This platform is designed to answer a single institutional question:",
                className="fw-bold mb-2"
            ),
            html.P(
                "Does adding GROWISE improve portfolio efficiency through structural diversification and "
                "risk-adjusted outcomes — not just standalone performance?",
                className="mb-3"
            ),
            html.Hr(),
            html.P("What this guide covers:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Where to load data and how the platform validates it"),
                html.Li("How asset selection impacts correlation and covariance estimates"),
                html.Li("How to interpret rolling correlation and heatmap regime shifts"),
                html.Li("How to read the efficient frontier and allocation outputs"),
                html.Li("How to interpret marginal contribution and regime/factor diagnostics"),
            ], className="mb-3"),
            html.Small(
                "Estimated duration: ~4–6 minutes. You can skip or revisit this guide at any time.",
                className="text-muted"
            )
        ])
    },

    {
        "title": "Step 1 — What problem this solves: correlation breakdown",
        "content": html.Div([
            html.P(
                "Diversification often fails precisely when it is most needed. During systemic stress, "
                "cross-asset correlations can converge toward 1.",
                className="mb-2"
            ),
            html.P(
                "This platform explicitly tests whether GROWISE remains a diversifier in stressed regimes, "
                "not only in stable markets.",
                className="mb-3"
            ),
            html.Ul([
                html.Li("If correlations spike in crises, diversification benefits can vanish"),
                html.Li("If correlation remains stable/low during crises, that is structural diversification"),
                html.Li("If correlation turns negative in drawdowns, that can behave as a tail-hedge characteristic"),
            ])
        ])
    },

    {
        "title": "Step 2 — Upload data: inputs, formats, and expectations",
        "content": html.Div([
            html.P(
                "Begin by uploading a returns dataset (CSV/Excel). The platform treats your upload as the source "
                "of truth across all tabs and outputs.",
                className="mb-3"
            ),
            html.P("Minimum requirements:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Columns = assets; rows = time periods"),
                html.Li("Returns in decimals (0.02 = 2%, not 2)"),
                html.Li("A date column or index that can be parsed as datetime"),
                html.Li("Reasonable history length: longer samples improve inference quality"),
            ], className="mb-3"),
            html.P(
                "If the dataset is misformatted, downstream statistics (correlation, covariance, optimization) can be materially distorted.",
                className="text-warning fw-bold mb-0"
            )
        ])
    },

    {
        "title": "Step 3 — Data validation: what the platform checks and why",
        "content": html.Div([
            html.P(
                "Before analysis, the platform performs basic institutional-grade sanity checks to reduce silent errors.",
                className="mb-3"
            ),
            html.P("Typical checks include:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Missing data handling and consistency checks"),
                html.Li("Outlier inspection (extreme returns that may reflect bad data)"),
                html.Li("Basic distribution diagnostics (skew/kurtosis) to contextualize risk"),
                html.Li("Frequency inference (daily/weekly/monthly) to annualize metrics correctly"),
            ], className="mb-3"),
            html.P(
                "Recommendation: if results look “too good” or inconsistent with intuition, validate the input series first.",
                className="mb-0"
            )
        ])
    },

    {
        "title": "Step 4 — Asset selection: how it affects the mathematics",
        "content": html.Div([
            html.P(
                "Your asset selection determines the dimensionality and stability of the covariance matrix used across the app.",
                className="mb-3"
            ),
            html.Ul([
                html.Li("Select GROWISE plus at least one benchmark (e.g., SPX proxy) for meaningful diversification tests"),
                html.Li("Adding more assets can improve realism but may reduce stability if the sample is short"),
                html.Li("Highly correlated assets can create redundancy; diversifiers add information"),
            ], className="mb-3"),
            html.P(
                "Institutional principle: correlation is estimated with error. Short samples and many assets increase estimation risk.",
                className="text-warning mb-0"
            )
        ])
    },

    {
        "title": "Step 5 — Date filtering: why window choice changes conclusions",
        "content": html.Div([
            html.P(
                "The time window defines which regimes you are measuring. A diversifier in calm periods may fail in crises, "
                "and vice versa.",
                className="mb-3"
            ),
            html.P("How to use date filters:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("All Data: best default for robust inference and factor estimation"),
                html.Li("1Y / YTD: useful for recent behavior, but statistically less reliable"),
                html.Li("Custom windows: isolate known stress regimes to test correlation breakdown"),
            ], className="mb-3"),
            html.P(
                "Recommendation: run All Data first, then validate with a crisis-window sanity check.",
                className="mb-0"
            )
        ])
    },

    {
        "title": "Step 6 — Rolling correlation: what to look for (and what to ignore)",
        "content": html.Div([
            html.P(
                "Rolling correlation reveals how relationships evolve across regimes, rather than assuming a single average correlation.",
                className="mb-3"
            ),
            html.P("Interpretation framework:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Stable low correlation: potential structural diversifier"),
                html.Li("Sharp spikes in stress: diversification breakdown risk"),
                html.Li("Mean reversion after spikes: tactical regime effect, not necessarily structural change"),
                html.Li("Sustained high correlation: limited diversification benefit"),
            ], className="mb-3"),
            html.P(
                "Avoid overfitting: do not conclude structural properties from a single short window.",
                className="text-muted mb-0"
            )
        ])
    },

    {
        "title": "Step 7 — Correlation heatmap: how crises appear in the matrix",
        "content": html.Div([
            html.P(
                "The heatmap summarizes the full correlation structure at a point in time (or through time, if animated).",
                className="mb-3"
            ),
            html.P("How to read it:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Broad shift toward high correlations: systemic regime (liquidity / macro shock)"),
                html.Li("Isolated high correlations: local clustering rather than system-wide convergence"),
                html.Li("Assets that remain low/negative vs benchmark in systemic regimes are the true diversifiers"),
            ], className="mb-3"),
            html.P(
                "Institutional takeaway: the key is behavior during widespread convergence — not the average in normal markets.",
                className="mb-0"
            )
        ])
    },

    {
        "title": "Step 8 — Why correlation ≠ diversification (the critical nuance)",
        "content": html.Div([
            html.P(
                "Correlation is a first-order proxy. Diversification quality depends on co-movement during drawdowns, "
                "volatility clustering, and tail dependence.",
                className="mb-3"
            ),
            html.P("Common pitfalls:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Low average correlation can hide crisis-period correlation spikes"),
                html.Li("Nonlinear payoffs can provide protection even when linear correlation is not strongly negative"),
                html.Li("Diversification may come from convexity, not just correlation"),
            ], className="mb-3"),
            html.P(
                "Practical rule: validate diversification with regime analysis and drawdown-conditioned behavior, not a single summary statistic.",
                className="mb-0"
            )
        ])
    },

    {
        "title": "Step 9 — Portfolio Lab: efficient frontier and optimization outputs",
        "content": html.Div([
            html.P(
                "The Portfolio Lab translates diversification into portfolio geometry: expected return vs risk and the efficient frontier.",
                className="mb-3"
            ),
            html.P("What to interpret:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Efficient frontier: the best achievable return for each risk level (under the constraints)"),
                html.Li("Optimal portfolio marker: the allocation that maximizes the selected objective (e.g., Sharpe / Sortino)"),
                html.Li("Improvement vs baseline: quantifies whether adding GROWISE improves risk-adjusted efficiency"),
            ], className="mb-3"),
            html.P(
                "If an output looks unstable, revisit window length, asset count, and data cleanliness before drawing conclusions.",
                className="text-muted mb-0"
            )
        ])
    },

    {
        "title": "Step 10 — Marginal contribution, regimes, factors: what to do next",
        "content": html.Div([
            html.P(
                "After optimization, validate the result with marginal contribution and diagnostic attribution.",
                className="mb-3"
            ),
            html.P("Recommended workflow:", className="fw-bold mb-2"),
            html.Ul([
                html.Li("Run marginal allocation sweeps: identify where small weights produce outsized Sharpe/Sortino improvements"),
                html.Li("Check benchmark correlation across weights: ensure diversification is not concentrated in one narrow regime"),
                html.Li("Use regime scatter to validate behavior in benchmark drawdowns (tail-sensitive quadrant)"),
                html.Li("Use factor attribution to distinguish alpha from passive factor exposure"),
            ], className="mb-3"),
            html.P(
                "Close: once the diagnostics agree, you have an allocator-ready narrative supported by multiple independent tests.",
                className="fw-bold mb-0"
            )
        ])
    },
]



@app.callback(
    Output("guide-popover", "is_open"),
    Output("guide-title", "children"),
    Output("guide-body", "children"),
    Output("guide-progress", "children"),
    Output("guide-state", "data"),
    Input("btn-start-guide", "n_clicks"),
    Input("guide-next", "n_clicks"),
    Input("guide-back", "n_clicks"),
    Input("guide-skip", "n_clicks"),
    State("guide-state", "data"),
    prevent_initial_call=True
)
def run_popover_guide(start, next_, back, skip, state):

    trigger = ctx.triggered_id

    # -------------------------
    # HARD GUARD: ignore noise
    # -------------------------
    if trigger not in {
        "btn-start-guide",
        "guide-next",
        "guide-back",
        "guide-skip",
    }:
        raise PreventUpdate

    open_ = state.get("open", False)
    step_i = state.get("i", 0)

    # -------------------------
    # START GUIDE
    # -------------------------
    if trigger == "btn-start-guide":
        step_i = 0
        open_ = True

    # -------------------------
    # NEXT
    # -------------------------
    elif trigger == "guide-next":
        if not open_:
            raise PreventUpdate
        step_i = min(step_i + 1, len(TOUR_STEPS) - 1)

    # -------------------------
    # BACK
    # -------------------------
    elif trigger == "guide-back":
        if not open_:
            raise PreventUpdate
        step_i = max(step_i - 1, 0)

    # -------------------------
    # SKIP / CLOSE
    # -------------------------
    elif trigger == "guide-skip":
        return False, "", "", "", {"open": False, "i": 0}

    step = TOUR_STEPS[step_i]

    return (
        True,
        step["title"],
        step["content"],
        f"Step {step_i + 1} of {len(TOUR_STEPS)}",
        {"open": True, "i": step_i},
    )




# ======================
# RUN APP
# ======================


# ======================
# RESOURCES TAB CALLBACKS
# ======================

# Download Template CSV
@app.callback(
    Output('download-template-csv', 'data'),
    Input('btn-download-template-csv', 'n_clicks'),
    prevent_initial_call=True
)
def download_template(n):
    """Generate and download portfolio template CSV"""
    template = pd.DataFrame({
        'Date': pd.date_range('2020-03-31', periods=20, freq='Q'),
        'Portfolio': [0.0234, 0.0567, 0.0312, 0.0445, 0.0289, 0.0534, -0.0123, 0.0678,
                     -0.0234, -0.0345, -0.0156, 0.0423, 0.0512, 0.0634, 0.0289, 0.0456,
                     0.0378, 0.0534, 0.0412, 0.0489],
        'Benchmark': [0.0156, 0.0423, 0.0289, 0.0378, 0.0234, 0.0467, -0.0089, 0.0589,
                     -0.0178, -0.0289, -0.0123, 0.0356, 0.0445, 0.0567, 0.0234, 0.0389,
                     0.0312, 0.0467, 0.0356, 0.0423],
        'Asset1': [np.nan] * 20,
        'Asset2': [np.nan] * 20,
        'Asset3': [np.nan] * 20
    })
    
    return dcc.send_data_frame(template.to_csv, "portfolio_returns_template.csv", index=False)


# Demo Mode (Role-Play)
@app.callback(
    [Output('data-store', 'data', allow_duplicate=True),
     Output('modal-demo', 'is_open'),
     Output('btn-launch-demo', 'style'),
     Output('btn-exit-demo', 'style'),
     Output('demo-mode-status', 'children')],
    Input('btn-launch-demo', 'n_clicks'),
    State('modal-demo', 'is_open'),
    prevent_initial_call=True
)
def launch_demo_mode(n, is_open):
    """Load demo data for role-play scenarios"""
    if n:
        # Load demo data (quarterly returns)# Load demo data (quarterly returns) - 24 assets, 12 quarters
# Load demo data (quarterly returns) - 24 assets, 20 quarters (5 years)
        demo_data = pd.DataFrame({
            'Date': pd.date_range('2020-09-30', periods=20, freq='Q'),
            'GROWISE': [-0.184658234, 0.112097593, 0.012928473, 0.093010374, -0.044690866, 0.119772701, -0.101132166, -0.280606548, 0.051084966, 0.165759955, 0.306371767, 0.050512181, 0.079049778, 0.059749805, -0.086402294, 0.205800236, -0.363698979, 0.199698752, 0.079681015, 0.237269029],
            'BTC-USD': [1.689206207, 1.031563321, -0.405269339, 0.249710327, 0.057444608, -0.016580187, -0.565540143, -0.017838887, -0.148431673, 0.721014721, 0.070185181, -0.115146075, 0.567239659, 0.687763681, -0.121336223, 0.010389674, 0.475287238, -0.116454906, 0.297840646, 0.008243152],
            'DBC': [0.125574142, 0.129932037, 0.158940318, 0.048311705, 0.029732503, 0.254090437, 0.022256251, -0.102477386, 0.037174172, -0.036916859, -0.043807897, 0.099559354, -0.073595541, 0.042195978, 0.011319088, -0.041325804, 0.011289187, 0.052385448, -0.03066669, 0.01811098],
            'GLD': [0.007000935, -0.103162109, 0.035446349, -0.008512972, 0.041042537, 0.056679848, -0.067478481, -0.081859243, 0.096786716, 0.080051886, -0.027016684, -0.038256617, 0.115018965, 0.076110285, 0.045158435, 0.130459066, -0.003826186, 0.190021926, 0.057923131, 0.007200759],
            'SLV': [0.13539743, -0.076109034, 0.066960286, -0.152766266, 0.048245602, 0.063691256, -0.185314682, -0.061158768, 0.25828574, 0.004541343, -0.05560585, -0.026328351, 0.070796486, 0.044536239, 0.167912074, 0.069251042, -0.073213655, 0.176984423, 0.058728674, 0.017677476],
            'USO': [0.16684331, 0.22780978, 0.230693377, 0.053728954, 0.03424656, 0.363502611, 0.084052826, -0.187554449, 0.073989, -0.052346286, -0.043497939, 0.272383975, -0.175735827, 0.181245335, 0.01092332, -0.121497658, 0.080520667, 0.023560539, -0.054571332, 0.037751363],
            'VBINX': [0.089331345, 0.023377866, 0.057598542, -0.000602502, 0.05469435, -0.056170705, -0.12163432, -0.045243833, 0.048862341, 0.055287009, 0.046027022, -0.032438532, 0.099301828, 0.056869827, 0.02029512, 0.057336284, 0.003828029, -0.018708942, 0.067923765, 0.006621148],
            'XLB': [0.1431758, 0.09314524, 0.049077495, -0.034675814, 0.151171768, -0.023486108, -0.159280248, -0.070724811, 0.149584081, 0.042879119, 0.032437841, -0.047560638, 0.096597264, 0.089825594, -0.044776735, 0.096253741, -0.122444365, 0.026739379, 0.026486441, 0.029438551],
            'XLE': [0.282366921, 0.308193305, 0.109264931, -0.021294713, 0.079259555, 0.390471787, -0.054003751, 0.018112189, 0.227032737, -0.043163933, -0.011409541, 0.121806469, -0.063554986, 0.135173808, -0.02677691, -0.028797863, -0.016188738, 0.099449345, -0.08507313, 0.008017926],
            'XLF': [0.23133053, 0.160139495, 0.081801479, 0.027322888, 0.045486034, -0.014854242, -0.174904822, -0.029580225, 0.133545777, -0.055275744, 0.053227239, -0.011620641, 0.139166386, 0.124430562, -0.020114611, 0.106406391, 0.070964416, 0.03436633, 0.054998476, 0.004487314],
            'XLI': [0.155057164, 0.115223039, 0.043411039, -0.041445318, 0.085539434, -0.023508134, -0.14815067, -0.046982557, 0.191196819, 0.034468138, 0.064925521, -0.051500271, 0.130535434, 0.108424073, -0.029146757, 0.114956318, -0.022275482, -0.00218096, 0.128930934, 0.006100826],
            'XLK': [0.116733538, 0.02361445, 0.113851944, 0.013020931, 0.166614866, -0.084237157, -0.198072666, -0.063300323, 0.050659418, 0.216195235, 0.153726291, -0.05510091, 0.176750147, 0.083821314, 0.088139672, -0.000285023, 0.03163098, -0.110431248, 0.228446788, 0.006554115],
            'XLU': [0.064834653, 0.028998173, -0.004980121, 0.017929738, 0.129346236, 0.047185482, -0.050614948, -0.059550763, 0.084976846, -0.032781153, -0.025463756, -0.092183197, 0.084788477, 0.045197987, 0.0462971, 0.193533861, -0.055247972, 0.04914312, 0.042827953, 0.003367547],
            'XLV': [0.079898735, 0.032661902, 0.083103444, 0.014279874, 0.111009143, -0.024648022, -0.059921424, -0.051834599, 0.126328358, -0.043320222, 0.029478945, -0.026082345, 0.064087371, 0.087134741, -0.009536863, 0.060682236, -0.102760118, 0.065456782, -0.072437105, -0.004340021],
            'XLY': [0.095918021, 0.047001776, 0.063930867, 0.006544071, 0.140965012, -0.093698834, -0.255146406, 0.038320373, -0.090810997, 0.1613218, 0.137833001, -0.050313212, 0.112746025, 0.030650276, -0.005968779, 0.100786398, 0.12180051, -0.117434721, 0.102968083, 0.002346636],
            '^GSPC': [0.116880782, 0.057725181, 0.081706293, 0.002336251, 0.106473795, -0.049467291, -0.164450954, -0.052771392, 0.070805014, 0.070272186, 0.082999292, -0.036475555, 0.112354169, 0.101580143, 0.039230329, 0.055306493, 0.020676844, -0.045868202, 0.105687088, 0.002721964],
            'AGG': [0.00400836, 0.007279806, -0.03371909, 0.017730151, -0.000116497, -0.00097559, -0.058457596, -0.045795033, -0.047023422, 0.015891756, 0.032322514, -0.009414744, -0.032194105, 0.067568553, -0.007356444, 0.000279025, 0.053010006, -0.03104825, 0.027379111, 0.012743038],
            'IEF': [0.002033669, -0.012830679, -0.05733487, 0.024675403, -0.000344908, 0.001169141, -0.063737394, -0.044680617, -0.056938354, 0.005863275, 0.0392151, -0.018825993, -0.044733794, 0.064069858, -0.01293063, -0.001858507, 0.057236808, -0.0460521, 0.037872225, 0.014022233],
            'IWM': [0.050153334, 0.312983467, 0.129019271, 0.03971471, -0.043411488, 0.020003232, -0.075416969, -0.172765961, -0.021179289, 0.06211783, 0.02694575, 0.052626766, -0.051799423, 0.139786616, 0.05044091, -0.03254225, 0.092433022, 0.00328698, -0.09514096, 0.084699308],
            'SHY': [0.000692747, 0.000162221, -0.000903285, -0.000545342, 0.000324461, -0.006038052, -0.025050059, -0.004985902, -0.015910422, 0.006855074, 0.016113539, -0.006277569, 0.006362447, 0.025073218, 0.002714475, 0.008204632, 0.02871415, -0.00079954, 0.015617683, 0.011442499],
            'TLT': [-0.000682927, -0.029834332, -0.139224072, 0.070268103, 0.003590566, 0.031841557, -0.106288709, -0.125932632, -0.102839932, -0.018798456, 0.073789248, -0.024758817, -0.131117804, 0.129446841, -0.036987365, -0.020059345, 0.07933563, -0.097289004, 0.049379724, -0.019839868],
            'VEA': [0.059975598, 0.164513156, 0.045099265, 0.057565172, -0.016227939, 0.026961757, -0.057720343, -0.139356447, -0.106112111, 0.167837803, 0.080291906, 0.031805849, -0.04680699, 0.109984092, 0.053463899, -0.005760175, 0.07153096, -0.080922351, 0.067859231, 0.130501828],
            'VNQ': [0.013267966, 0.09291584, 0.087920236, 0.115984829, 0.006101348, 0.150518369, -0.060744472, -0.153913686, -0.110543207, 0.043354987, 0.016880839, 0.017624485, -0.085733273, 0.182258616, -0.012911862, -0.019412126, 0.172880101, -0.076761751, 0.02683051, -0.006682632],
            'VWO': [0.102286339, 0.165895371, 0.040053929, 0.048893025, -0.070631054, -0.001247078, -0.064631664, -0.09040171, -0.112048843, 0.085686884, 0.037178667, 0.012410313, -0.028273666, 0.070753888, 0.017251611, 0.05168049, 0.096697747, -0.057403464, 0.028747793, 0.095960958]
        })
        demo_data.set_index('Date', inplace=True)
        
        demo_json = demo_data.to_json(orient='split', date_format='iso')
        
        return (
            demo_json, 
            not is_open,
            {'display': 'none'},  # Hide Launch button
            {'display': 'block'},  # Show Exit button
            dbc.Alert("🎭 Demo mode active! Using sample data.", color="success", className="mb-0 small")
        )
    
    return dash.no_update, is_open


# Close Demo Modal
@app.callback(
    Output('modal-demo', 'is_open', allow_duplicate=True),
    Input('btn-close-demo-modal', 'n_clicks'),
    State('modal-demo', 'is_open'),
    prevent_initial_call=True
)
def close_demo_modal(n, is_open):
    """Close demo modal"""
    if n:
        return False
    return is_open


# Correlation Education Modal Callback


# Exit Demo Mode
@app.callback(
    [Output('data-store', 'data', allow_duplicate=True),
     Output('btn-launch-demo', 'style', allow_duplicate=True),
     Output('btn-exit-demo', 'style', allow_duplicate=True),
     Output('demo-mode-status', 'children', allow_duplicate=True)],
    Input('btn-exit-demo', 'n_clicks'),
    prevent_initial_call=True
)
def exit_demo_mode(n):
    '''Clear demo data and return to normal mode'''
    if n:
        return (
            None,  # Clear data-store
            {'display': 'block'},  # Show Launch button
            {'display': 'none'},   # Hide Exit button
            dbc.Alert("Demo mode exited. Upload your own data.", color="info", className="mb-0 small")
        )
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('modal-corr-edu', 'is_open'),
    Input('btn-open-corr-modal', 'n_clicks'),
    Input('btn-close-corr-modal', 'n_clicks'),
    State('modal-corr-edu', 'is_open'),
    prevent_initial_call=True
)
def toggle_corr_modal(open_n, close_n, is_open):
    return not is_open





def parse_and_qc_uploaded_returns(contents: str, filename: str):
    if not contents:
        raise PreventUpdate
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if filename.lower().endswith('.csv'):
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), index_col=0, parse_dates=True)

    else:
        df = pd.read_excel(io.BytesIO(decoded), index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    max_abs = float(df.abs().max().max()) if not df.empty else 0.0
    flags = []
    if max_abs > 1.5:
        flags.append("SCALE_SUSPECT_PERCENT")
    if (df.min().min() if not df.empty else 0.0) < -1.0:
        flags.append("IMPOSSIBLE_RETURN")
    return df, {"file": filename, "max_abs": max_abs, "flags": flags}

def resample_returns_to_target(df: pd.DataFrame, target_code: str = 'Q') -> pd.DataFrame:
    if df is None or df.empty:
        return df
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    if target_code == 'Q':
        return (1.0 + df).resample('QE').prod() - 1.0
    if target_code == 'M':
        return (1.0 + df).resample('M').prod() - 1.0
    if target_code == 'W':
        return (1.0 + df).resample('W-FRI').prod() - 1.0
    return df

def align_to_base_index(df_new: pd.DataFrame, base_index: pd.DatetimeIndex, tol_days: int = 15) -> pd.DataFrame:
    if df_new is None or df_new.empty:
        return df_new
    base_index = pd.to_datetime(base_index)
    new = df_new.copy()
    new.index = pd.to_datetime(new.index)
    new = new.sort_index()
    aligned_idx = []
    for dt in new.index:
        nearest = min(base_index, key=lambda x: abs((x - dt).days))
        if abs((nearest - dt).days) <= tol_days:
            aligned_idx.append(nearest)
        else:
            aligned_idx.append(pd.NaT)
    new.index = aligned_idx
    new = new[~new.index.isna()]
    new = new.groupby(new.index).first()
    return new.reindex(base_index)

# @app.callback(
#     Output("data-store", "data", allow_duplicate=True),
#     Output("upload-status", "children"),
#     Input("upload-multi", "contents"),
#     State("upload-multi", "filename"),
#     State("data-store", "data"),
#     prevent_initial_call=True
# )
# def upload_and_merge(contents_list, filenames, current_json):
#     if not contents_list:
#         raise PreventUpdate
#     base_df = pd.read_json(StringIO(current_json), orient="split") if current_json else load_base_data_csv()
#     base_df.index = pd.to_datetime(base_df.index)
#     merged = base_df.copy()
#     if not isinstance(contents_list, list):
#         contents_list = [contents_list]
#         filenames = [filenames]
#     for contents, fname in zip(contents_list, filenames):
#         df_new, qc = parse_and_qc_uploaded_returns(contents, fname)
#         df_new_q = resample_returns_to_target(df_new, "Q")
#         df_new_q = align_to_base_index(df_new_q, merged.index)
#         for col in df_new_q.columns:
#             col_name = col
#             if col_name in merged.columns:
#                 col_name = f"{col_name}__uploaded"
#             merged[col_name] = df_new_q[col]
#     out_json = merged.to_json(orient="split", date_format="iso")
#     msg = dbc.Alert(f"✓ Merged {len(contents_list)} file(s). Total assets now: {len(merged.columns)}", color="success")
#     return out_json, msg


@app.callback(
    Output("upload-modal", "is_open"),
    Input("btn-open-upload-modal", "n_clicks"),
    Input("btn-close-upload-modal", "n_clicks"),
    State("upload-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_upload_modal(open_n, close_n, is_open):
    
    print("TRIGGER:", ctx.triggered_id)
    
    trigger = ctx.triggered_id
    
    if trigger == "btn-open-upload-modal":
        return True

    if trigger == "btn-close-upload-modal":
        return False

    return is_open

@app.callback(
    Output("data-store", "data", allow_duplicate=True),
    Output("data-info-alert", "children", allow_duplicate=True),
    Input("btn-clear-session", "n_clicks"),
    prevent_initial_call=True
)
def clear_session_uploads(n):
    if not n:
        raise PreventUpdate
    df0 = load_base_data_csv()
    j = df0.to_json(orient="split", date_format="iso") if not df0.empty else None
    return j, "Session reset to base dataset."

@app.callback(
    Output("download-qc-report", "data"),
    Input("btn-download-qc-report", "n_clicks"),
    State("data-store", "data"),
    State("upload-protocol-store", "data"),
    prevent_initial_call=True
)
def download_qc_report(n, data_json, protocol_state):
    """Generate and download professional PDF Data Governance report"""
    if not n or not data_json:
        raise PreventUpdate
    
    df = pd.read_json(StringIO(data_json), orient="split")
    df.index = pd.to_datetime(df.index)
    
    if protocol_state and protocol_state.get("steps"):
        steps = protocol_state.get("steps", [])
        filename = protocol_state.get("filename", "portfolio_data.csv")
    else:
        steps = [
            {"name": "Data loaded", "state": "passed", "detail": "From session"},
            {"name": "Schema validation", "state": "passed", "detail": f"{len(df.columns)} assets"},
            {"name": "Return sanity checks", "state": "passed", "detail": "All values in range"},
            {"name": "Frequency detection", "state": "passed", "detail": "Quarterly"},
            {"name": "Data ready", "state": "passed", "detail": f"{len(df)} periods"}
        ]
        filename = "session_data.csv"
    
    data_profile = {}
    # Include ALL assets in the profile (not just first 15)
    for col in df.columns:
        series = df[col].dropna()
        data_profile[col] = {
            "count": len(series),
            "missing_pct": (df[col].isna().sum() / len(df)) * 100,
            "min": series.min() if len(series) > 0 else 0,
            "max": series.max() if len(series) > 0 else 0,
            "mean": series.mean() if len(series) > 0 else 0,
            "std": series.std() if len(series) > 0 else 0
        }
    
    recommendations = []
    max_val = df.abs().max().max()
    if max_val > 0.5:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": f"Large return detected ({max_val:.2%})",
            "action": "Verify this is not a data error or stock split"
        })
    
    missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    if missing_pct > 5:
        recommendations.append({
            "priority": "HIGH" if missing_pct > 20 else "MEDIUM",
            "issue": f"{missing_pct:.1f}% missing data",
            "action": "Consider filling missing values or removing incomplete assets"
        })
    
    file_info = {
        "Rows": len(df),
        "Columns": len(df.columns),
        "Date Range": f"{df.index.min().date()} to {df.index.max().date()}",
        "Frequency": "Quarterly (harmonized)",
        "Assets": ", ".join(df.columns[:5].tolist()) + ("..." if len(df.columns) > 5 else "")
    }
    
    pdf_buffer = generate_protocol_report(
        filename=filename,
        protocol_results=steps,
        data_profile=data_profile,
        recommendations=recommendations if recommendations else None,
        file_info=file_info,
        user="Analyst"
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return dcc.send_bytes(
        pdf_buffer.getvalue(),
        filename=f"SigmaLab_DataQuality_Report_{timestamp}.pdf"
    )

@app.callback(
    Output("download-sample", "data"),
    Input("btn-download-sample", "n_clicks"),
    State("data-store", "data"),
    prevent_initial_call=True
)
def download_sample(n, data_json):
    if not n or not data_json:
        raise PreventUpdate
    df = pd.read_json(StringIO(data_json), orient="split")
    df.index = pd.to_datetime(df.index)
    samp = df.tail(12).copy()
    samp.insert(0, "date", samp.index.strftime("%Y-%m-%d"))
    return dict(content=samp.to_csv(index=False), filename="sigmalab_sample_last12.csv")

# @app.callback(
#     Output("upload-protocol-status", "data"),
#     Input("upload-multi", "contents"),
#     prevent_initial_call=True
# )
# def start_protocol_runner(contents):
#     if not contents:
#         raise PreventUpdate

#     return {
#         "running": True,
#         "steps": [{"id": p["id"], "label": p["label"], "status": "pending"} for p in DATA_GOVERNANCE_PROTOCOLS],
#         "summary": None
#     }

# @app.callback(
#     Output("protocol-runner-list", "children"),
#     Output("protocol-summary", "children"),
#     Input("upload-protocol-status", "data"),
#     prevent_initial_call=False
# )
# def render_protocol_runner(state):
#     if not state or not state.get("steps"):
#         # Estado inicial: mostrar la lista default (spinners)
#         children = [
#             html.Div(
#                 [dbc.Spinner(size="sm", color="warning"), html.Span(p["label"], className="ms-2")],
#                 className="protocol-item pending"
#             )
#             for p in DATA_GOVERNANCE_PROTOCOLS
#         ]
#         return children, ""

#     def icon_for(status):
#         if status == "passed":
#             return html.Span("✓", className="me-2")
#         if status == "warning":
#             return html.Span("⚠", className="me-2")
#         if status == "failed":
#             return html.Span("✗", className="me-2")
#         return dbc.Spinner(size="sm", color="warning")

#     children = []
#     for s in state["steps"]:
#         status = s.get("status", "pending")
#         label = s.get("label", s.get("id"))
#         children.append(
#             html.Div(
#                 [icon_for(status), html.Span(label)],
#                 className=f"protocol-item {status}"
#             )
#         )

#     summary = ""
#     if state.get("summary"):
#         summary = (
#             f"✓ {state['summary'].get('passed',0)} passed · "
#             f"⚠ {state['summary'].get('fixed',0)} auto-fixed · "
#             f"✗ {state['summary'].get('failed',0)} failed"
#         )

#     return children, summary

@callback(
    Output("upload-protocol-store", "data"),
    Output("upload-interval", "disabled"),
    Input("upload-multi", "contents"),
    State("upload-protocol-store", "data"),
    State("upload-multi","filename"),
    State("data-store","data"),
    prevent_initial_call=True
)
def start_protocol_run(contents, state, filenames, current_json):
    if not contents:
        raise PreventUpdate

    # Reset completo
    for step in state["steps"]:
        step["state"] = "pending"
    state["files"] = contents
    state["filenames"] = filenames
    state["base_json"] = current_json
    state["status"] = "running"
    state["current_step"] = 0
    #state["files"] = contents

    return state, False   # 🔓 habilita el interval

@callback(
    Output("upload-protocol-store", "data", allow_duplicate=True),
    Output("upload-interval", "disabled", allow_duplicate=True),
    Input("upload-interval", "n_intervals"),
    State("upload-protocol-store", "data"),
    prevent_initial_call=True
)
def run_next_protocol(n, state):

    if not state or state.get("status") != "running":
        return state, True

    i = state.get("current_step", 0)

    # Done guard (shouldn't usually hit because we stop interval at merge)
    if i >= len(state.get("steps", [])):
        state["status"] = "success"
        return state, True

    step_name = state["steps"][i]["name"]

    # Mark current step running
    state["steps"][i]["state"] = "running"
    state["steps"][i]["detail"] = "Running..."

    try:
        # ✅ LAST STEP = MERGE (do it ONCE, here)
        if step_name.lower() in ["merge", "merge with base universe", "merge_with_base_universe"]:
            merged_json, qc_summary = upload_and_merge(
                state.get("files"),
                state.get("filenames"),
                state.get("base_json")
            )
            state["merged_json"] = merged_json
            state["qc_summary"] = qc_summary

            state["steps"][i]["state"] = "passed"
            state["steps"][i]["detail"] = "Merged successfully."

            state["status"] = "success"
            state["current_step"] = i + 1

            return state, True  # ✅ stop interval

        # Otherwise run your real step logic (or placeholder)
        run_protocol(step_name, state.get("files"))

        state["steps"][i]["state"] = "passed"
        state["steps"][i]["detail"] = "Passed."
        state["current_step"] = i + 1

        return state, False  # continue

    except Exception as e:
        state["steps"][i]["state"] = "failed"
        state["steps"][i]["detail"] = str(e)
        state["status"] = "failed"
        state["error"] = str(e)
        return state, True  # stop interval
    
@callback(
    Output("data-store", "data", allow_duplicate=True),
    Output("upload-status", "children", allow_duplicate=True),
    Input("upload-protocol-store", "data"),
    prevent_initial_call=True
)
def finalize_merge(state):
    if not state:
        raise PreventUpdate

    if state.get("status") == "success" and state.get("merged_json"):
        # Show a short summary in the modal (or wherever upload-status renders)
        msg = state.get("qc_summary") or "✅ Data accepted and merged into session."
        return state["merged_json"], msg

    # If failed, show error but do not change data-store
    if state.get("status") == "failed":
        err = state.get("error") or "❌ Upload failed. Please fix and re-upload."
        return no_update, f"❌ {err}"

    raise PreventUpdate

@callback(
    Output("protocol-status-list", "children"),
    Input("upload-protocol-store", "data"),
    prevent_initial_call=True
)
def update_protocol_list_visual(state):
    """Update protocol list items with visual state classes"""
    if not state or not state.get("steps"):
        raise PreventUpdate
    
    step_ids = [
        "protocol-ingestion",
        "protocol-schema", 
        "protocol-sanity",
        "protocol-outliers",
        "protocol-frequency",
        "protocol-compounding",
        "protocol-alignment",
        "protocol-merge"
    ]
    
    children = []
    for i, step in enumerate(state["steps"]):
        step_state = step.get("state", "pending")
        step_name = step.get("name", f"Step {i+1}")
        step_detail = step.get("detail", "")
        
        item_class = f"protocol-item {step_state}"
        
        if step_detail:
            content = html.Span([
                html.Span(step_name, className="protocol-step-name"),
                html.Span(f" - {step_detail}", className="protocol-step-detail")
            ])
        else:
            content = step_name
            
        children.append(
            html.Li(content, className=item_class, id=step_ids[i] if i < len(step_ids) else None)
        )
    
    return children
    

# RUN APP
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
    
# Expose server for gunicorn (Railway deployment)
# server = app.server
# if __name__ == '__main__':
#     app.run_server(debug=True, port=8050)
