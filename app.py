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
# TARGETS
# ======================
TARGETS = {
    "SigmaLab": "https://www.sci-techlab.com",
    "GroWise": "https://GROWISE-XXXX.up.railway.app",
    "Atlas": "https://ATLAS-XXXX.up.railway.app",
    "Client360": "https://script.google.com/a/macros/sci.tech/s/AKfycby_6WGTvIZ7MNqJOLF32s-uucxGdwRQj7zmP-FPahZ7gsZYZLQxQPWpIBuWvd_htFOs/exec",
}

# ======================
# CSS (UI POLISHING)
# ======================
THEME_CSS = """
html, body {
  height: 100%;
  margin: 0;
  background: #070A10 url("/assets/bg_scitech_map.png") no-repeat center center fixed;
  background-size: cover;
  overflow: hidden;
  color: #E9EEF7;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
}

#_dash-app-content { height: 100vh; }

.frame {
  position: relative;
  height: 100vh;
  padding: 18px 24px;
}

/* legibilidad sin “lavar” el background */
.frame:before{
  content:"";
  position:absolute; inset:0;
  z-index: 0;
  background:
    radial-gradient(1200px 700px at 20% 18%, rgba(0,0,0,0.12), transparent 60%),
    radial-gradient(900px 520px at 78% 38%, rgba(0,0,0,0.18), transparent 55%),
    linear-gradient(180deg, rgba(0,0,0,0.10), rgba(0,0,0,0.55));
  pointer-events:none;
}

.topbar, .content, .footer { position: relative; z-index: 1; }

/* Top bar */
.topbar {
  height: 64px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 16px;
}

.logo {
  letter-spacing: 0.14em;
  font-weight: 700;
  font-size: 26px;
  color: rgba(233,238,247,0.95);
  line-height: 1;
  text-transform: uppercase;
}
.logo small {
  display:block;
  font-size: 10px;
  letter-spacing: 0.32em;
  opacity: .78;
  margin-top: 6px;
}

/* Ticker (desktop) */
.ticker {
  width: 900px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.25);
}

/* Content */
.content {
  height: calc(100vh - 128px);
  display:flex;
  justify-content:center;
  align-items:center;
}

/* Cards layout: one column always */
.cards {
  width: min(980px, 94vw);
  display:grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin: 0 auto;
}

/* Card */
.sc-card {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 16px 22px;
  border-radius: 14px;
  border: 1px solid rgba(233,238,247,0.16);
  background: linear-gradient(180deg, rgba(16,26,44,0.70), rgba(16,26,44,0.30));
  box-shadow: 0 18px 46px rgba(0,0,0,0.38);
  backdrop-filter: blur(11px);
  -webkit-backdrop-filter: blur(11px);
  cursor:pointer;
  transition: transform 140ms ease-out, border-color 140ms ease-out, box-shadow 140ms ease-out, background 140ms ease-out;
}

.sc-card:hover {
  transform: translateY(-2px);
  border-color: rgba(82,224,208,0.32);
  box-shadow: 0 26px 64px rgba(0,0,0,0.45);
  background: linear-gradient(180deg, rgba(18,30,50,0.78), rgba(18,30,50,0.34));
}

.left {
  display:flex;
  align-items:center;
  gap: 14px;
  min-width: 0;
}

.icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(0,0,0,0.20);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 21px;
  color: rgba(233,238,247,0.92);
  flex: 0 0 auto;
}

.textblock {
  display:flex;
  flex-direction:column;
  align-items:flex-start; /* left aligned */
  justify-content:center;
  text-align:left;
  min-width: 0;
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: rgba(233,238,247,0.95);
  line-height: 1.12;
  letter-spacing: -0.01em;
}

.sub {
  margin-top: 4px;
  font-size: 13px;
  opacity: .78;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 72vw; /* ayuda mobile */
}

.arrow {
  font-size: 28px;
  opacity: .55;
  line-height: 1;
  display:flex;
  align-items:center;
  justify-content:center;
  width: 34px;
  flex: 0 0 auto;
}

/* Footer */
.footer {
  height: 64px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size: 12px;
  opacity: .75;
}

a, a:hover, a:visited { color: inherit; text-decoration: none; }

/* Mobile polish */
@media (max-width: 820px) {
  .frame { padding: 14px 14px; }
  .ticker { display: none; } /* evita glitch/espacio raro mobile */
  .topbar { height: 56px; }
  .logo { font-size: 22px; letter-spacing: 0.12em; }
  .sc-card { padding: 14px 16px; border-radius: 14px; }
  .title { font-size: 20px; }
  .sub { font-size: 12px; max-width: 64vw; }
  .icon { width: 44px; height: 44px; border-radius: 14px; }
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
            className="sc-card",
            children=[
                html.Div(
                    className="left",
                    children=[
                        html.Div(html.I(className=f"bi {icon}"), className="icon"),
                        html.Div(
                            className="textblock",
                            children=[
                                html.Div(title, className="title"),
                                html.Div(subtitle, className="sub"),
                            ],
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
                    card("Client360", "Client coverage • CRM • activity", "bi-person-badge", TARGETS["Client360"]),
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
    app.run_server(debug=True)
