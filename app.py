import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_auth

# ======================
# AUTH (igual a SigmaLab por ahora)
# ======================
VALID_USERS = {
    'john': 'growise2025',
    'analyst': 'scitech123',
    'demo': 'demo2025',
    'juan.serur@sci.tech': 'Sc1T3ch_JS_2025!',
    'martin.garay@sci.tech': 'Sc1T3ch_MG_2025!',
    'federico.massimo@sci.tech': 'Sc1T3ch_FM_2025!',
    'ihs@sci.tech': 'Sc1T3ch_IHS_2025!',
    'leonel.lalia@sci.tech': 'Sc1T3ch_LL_2025!',
    'maximiliano.markous@sci.tech': 'Sc1T3ch_MM_2025!'
}

external_stylesheets = [
    dbc.themes.SLATE,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_folder="assets",
    assets_url_path="/assets",
)
server = app.server
auth = dash_auth.BasicAuth(app, VALID_USERS)
app.title = "SciTech Lab"

# ======================
# TARGETS (STAGING)
# ======================
TARGETS = {
    "SigmaLab": "https://www.sci-techlab.com",
    "GroWise": "https://GROWISE-XXXX.up.railway.app",
    "Atlas": "https://ATLAS-XXXX.up.railway.app",
}

# ======================
# CSS (1 columna + cards más bajas + mejor contraste)
# ======================
THEME_CSS = """
html, body {
  height: 100%;
  margin: 0;
  background: #070A10 url("/assets/bg_scitech_map.png") no-repeat center center fixed;
  background-size: cover;
  overflow: hidden;
  color: #E9EEF7;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}

#_dash-app-content { height: 100vh; }

.frame {
  position: relative;
  height: 100vh;
  padding: 18px 24px;
}

/* overlay atrás del contenido (para legibilidad sin “lavar” la UI) */
.frame:before{
  content:"";
  position:absolute; inset:0;
  z-index: 0;
  background:
    radial-gradient(1200px 700px at 20% 18%, rgba(0,0,0,0.10), transparent 60%),
    linear-gradient(180deg, rgba(0,0,0,0.08), rgba(0,0,0,0.40));
  pointer-events:none;
}

/* contenido encima del overlay */
.topbar, .content, .footer {
  position: relative;
  z-index: 1;
}

/* top bar */
.topbar {
  height: 64px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 16px;
}

.logo {
  letter-spacing: 0.14em;
  font-weight: 650;
  font-size: 26px;
  color: rgba(233,238,247,0.92);
  line-height: 1;
}
.logo small {
  display:block;
  font-size: 10px;
  letter-spacing: 0.32em;
  opacity: .75;
  margin-top: 6px;
}

/* ticker (widget real) */
.ticker {
  width: 900px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(0,0,0,0.22);
}

/* content */
.content {
  height: calc(100vh - 128px);
  display:flex;
  justify-content:center;
  align-items:center;
}

/* 1 columna ALWAYS + ancho “portal” */
.cards {
  width: min(860px, 94vw);
  display:grid;
  grid-template-columns: 1fr;
  gap: 18px;
  margin: 0 auto;
}

/* card (más baja/compacta) */
.card {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 14px 22px;  /* ↓ menos alta */
  border-radius: 12px; /* más tight */
  border: 1px solid rgba(233,238,247,0.18);
  background: linear-gradient(180deg, rgba(18,28,46,0.72), rgba(18,28,46,0.34));
  box-shadow: 0 18px 48px rgba(0,0,0,0.35);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  cursor:pointer;
  transition: all 140ms ease-out;
}

.card:hover {
  transform: translateY(-2px);
  border-color: rgba(82,224,208,0.35);
  box-shadow: 0 24px 60px rgba(0,0,0,0.42);
}

.left {
  display:flex;
  align-items:center;
  gap: 14px;
}

.icon {
  width: 40px;         /* ↓ */
  height: 40px;        /* ↓ */
  border-radius: 12px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(0,0,0,0.22);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 20px;     /* ↓ */
  color: rgba(233,238,247,0.90);
}

.title {
  font-size: 20px;     /* ↓ */
  font-weight: 650;
  color: rgba(233,238,247,0.92);
  line-height: 1.15;
}

.sub {
  margin-top: 2px;     /* ↓ */
  font-size: 11px;     /* ↓ */
  opacity: .70;
}

.arrow {
  font-size: 22px;     /* ↓ */
  opacity: .55;
  margin-left: 16px;
}

/* footer */
.footer {
  height: 64px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size: 12px;
  opacity: .70;
}

/* links sin underline */
a, a:hover, a:visited { color: inherit; text-decoration: none; }

@media (max-width: 980px) {
  .ticker { width: 100%; }
}
"""

app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
  {{%metas%}}
  <title>SciTech Lab</title>
  {{%css%}}
  <style>{THEME_CSS}</style>
</head>
<body>
  {{%app_entry%}}
  <footer>
    {{%config%}}
    {{%scripts%}}
    {{%renderer%}}
  </footer>
</body>
</html>
"""

# ======================
# TradingView ticker (real prices)
# ======================
TV_TICKER = html.Iframe(
    srcDoc="""
<!DOCTYPE html><html><body style="margin:0;background:transparent;">
<script src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js">
{
  "symbols": [
    {"proName": "SP:SPX", "title": "SPX"},
    {"proName": "NASDAQ:NDX", "title": "NDX"},
    {"proName": "TVC:DXY", "title": "DXY"},
    {"proName": "CBOE:VIX", "title": "VIX"}
  ],
  "colorTheme": "dark",
  "isTransparent": true,
  "displayMode": "adaptive",
  "locale": "en"
}
</script>
</body></html>
""",
    className="ticker",
)

def card(title, subtitle, icon, url):
    return dcc.Link(
        href=url,
        target="_blank",
        children=html.Div(
            className="card",
            children=[
                html.Div(
                    className="left",
                    children=[
                        html.Div(html.I(className=f"bi {icon}"), className="icon"),
                        html.Div(
                            children=[
                                html.Div(title, className="title"),
                                html.Div(subtitle, className="sub"),
                            ]
                        ),
                    ],
                ),
                html.Div("›", className="arrow"),
            ],
        ),
    )

# ======================
# LAYOUT
# ======================
app.layout = html.Div(
    className="frame",
    children=[
        html.Div(
            className="topbar",
            children=[
                html.Div(["SCITECH", html.Small("INVESTMENTS")], className="logo"),
                TV_TICKER,
            ],
        ),

        html.Div(
            className="content",
            children=html.Div(
                className="cards",
                children=[
                    card("SigmaLab", "Correlation • regimes • clustering", "bi-grid-3x3-gap", TARGETS["SigmaLab"]),
                    card("GroWise Dashboard", "Performance • benchmarks • attribution", "bi-graph-up-arrow", TARGETS["GroWise"]),
                    card("SciTech Atlas", "Market + quant context • curated research", "bi-globe2", TARGETS["Atlas"]),
                ],
            ),
        ),

        html.Div(
            className="footer",
            children=[
                html.Div("SciTech Lab"),
                html.Div("Docs / Runbooks   •   Changelog   •   System Status"),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
