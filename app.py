import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_auth

# ======================
# AUTH (same as SigmaLab)
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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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
# GLOBAL CSS
# ======================
THEME_CSS = """
html, body {
  height: 100%;
  margin: 0;
  background: url("/assets/bg_scitech_map.png") no-repeat center center fixed;
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

.frame:before{
  content:"";
  position:absolute; inset:0;
  background:
    radial-gradient(1200px 700px at 20% 20%, rgba(0,0,0,0.25), transparent 60%),
    linear-gradient(180deg, rgba(0,0,0,0.15), rgba(0,0,0,0.55));
  pointer-events:none;
}

/* top bar */
.topbar {
  height: 64px;
  display:flex;
  align-items:center;
  justify-content:space-between;
}

.logo {
  letter-spacing: 0.14em;
  font-weight: 650;
  font-size: 26px;
}
.logo small {
  display:block;
  font-size: 10px;
  letter-spacing: 0.32em;
  opacity: .7;
  margin-top: 4px;
}

.ticker {
  width: 900px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.18);
}

/* content */
.content {
  height: calc(100vh - 128px);
  display:flex;
  justify-content:center;
  align-items:center;
}

.cards {
  width: min(700px, 94vw);      /* más “portal” y menos ancho */
  display: grid;
  grid-template-columns: 1fr;   /* 1 columna ALWAYS */
  gap: 18px;
  margin: 0 auto;
}

.card {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 20px 22px;
  border-radius: 14px;
  border: 1px solid rgba(233,238,247,0.18);
  background: linear-gradient(180deg, rgba(18,28,46,0.60), rgba(18,28,46,0.28));
  backdrop-filter: blur(10px);
  cursor:pointer;
  transition: all 140ms ease-out;
}
.card:hover {
  transform: translateY(-2px);
  border-color: rgba(82,224,208,0.35);
}

.left {
  display:flex;
  align-items:center;
  gap: 14px;
}

.icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(0,0,0,0.20);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 22px;
}

.title {
  font-size: 22px;
  font-weight: 650;
}
.sub {
  margin-top: 4px;
  font-size: 12px;
  opacity: .7;
}

.arrow {
  font-size: 28px;
  opacity: .5;
}

/* footer */
.footer {
  height: 64px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size: 12px;
  opacity: .6;
}

@media (max-width: 980px) {
  .cards { grid-template-columns: 1fr; }
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
# TradingView Ticker (REAL)
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
    className="ticker"
)

def card(title, subtitle, icon, url):
    return dcc.Link(
        href=url,
        target="_blank",
        children=html.Div(
            className="card",
            children=[
                html.Div(className="left", children=[
                    html.Div(html.I(className=f"bi {icon}"), className="icon"),
                    html.Div([
                        html.Div(title, className="title"),
                        html.Div(subtitle, className="sub"),
                    ])
                ]),
                html.Div("›", className="arrow")
            ]
        )
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
                    card("SigmaLab",
                         "Correlation • regimes • clustering",
                         "bi-grid-3x3-gap",
                         TARGETS["SigmaLab"]),
                    card("GroWise Dashboard",
                         "Performance • benchmarks • attribution",
                         "bi-graph-up-arrow",
                         TARGETS["GroWise"]),
                    card("SciTech Atlas",
                         "Market + quant context • curated research",
                         "bi-globe2",
                         TARGETS["Atlas"]),
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

