import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_auth

# ======================
# AUTH (igual a SigmaLab por ahora)
# ======================
VALID_USERS = {
    "john": "growise2025",
    "analyst": "scitech123",
    "demo": "demo2025",
    "juan.serur@sci.tech": "Sc1T3ch_JS_2025!",
    "martin.garay@sci.tech": "Sc1T3ch_MG_2025!",
    "federico.massimo@sci.tech": "Sc1T3ch_FM_2025!",
    "ihs@sci.tech": "Sc1T3ch_IHS_2025!",
    "leonel.lalia@sci.tech": "Sc1T3ch_LL_2025!",
    "maximiliano.markous@sci.tech": "Sc1T3ch_MM_2025!",
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
    suppress_callback_exceptions=True,
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
# CSS (Institutional polishing)
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

/* overlay behind content for readability */
.frame:before{
  content:"";
  position:absolute; inset:0;
  z-index: 0;
  background:
    radial-gradient(1200px 700px at 18% 14%, rgba(0,0,0,0.10), transparent 60%),
    linear-gradient(180deg, rgba(0,0,0,0.08), rgba(0,0,0,0.46));
  pointer-events:none;
}

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
  font-weight: 660;
  font-size: 26px;
  color: rgba(233,238,247,0.92);
  line-height: 1;
  user-select:none;
}
.logo small {
  display:block;
  font-size: 10px;
  letter-spacing: 0.32em;
  opacity: .78;
  margin-top: 6px;
}

/* ticker */
.ticker {
  width: 900px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(0,0,0,0.20);
}

/* content */
.content {
  height: calc(100vh - 128px);
  display:flex;
  justify-content:center;
  align-items:center;
}

/* one column, portal width */
.cards {
  width: min(1020px, 94vw);
  display:grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin: 0 auto;
}

/* link wrapper - keeps hover consistent */
.sc-link { display:block; }

/* institutional row card */
.sc-card {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 14px 22px;
  border-radius: 14px;
  border: 1px solid rgba(233,238,247,0.14);
  background: linear-gradient(180deg, rgba(14,22,38,0.74), rgba(14,22,38,0.40));
  box-shadow: 0 18px 52px rgba(0,0,0,0.34);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  cursor:pointer;
  transition: transform 140ms ease-out, border-color 140ms ease-out, box-shadow 140ms ease-out, background 140ms ease-out;
}

/* subtle hover (no retail bounce) */
.sc-card:hover {
  transform: translateY(-0.5px);
  border-color: rgba(120,210,200,0.30);
  box-shadow: 0 22px 60px rgba(0,0,0,0.40);
  background: linear-gradient(180deg, rgba(16,26,44,0.78), rgba(16,26,44,0.44));
}

.left {
  display:flex;
  align-items:center;
  gap: 14px;
  min-width: 0;
}

/* icon */
.icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(0,0,0,0.22);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 20px;
  color: rgba(233,238,247,0.90);
  flex: 0 0 auto;
}

/* text block */
.textblock {
  display:flex;
  flex-direction:column;
  align-items:flex-start;
  justify-content:center;
  text-align:left;
  min-width: 0;
}

.title {
  font-size: 20px;
  font-weight: 670;
  color: rgba(233,238,247,0.93);
  line-height: 1.12;
  letter-spacing: -0.01em;
}

.sub {
  margin-top: 3px;
  font-size: 12.5px;
  color: rgba(233,238,247,0.62);
  letter-spacing: 0.01em;
  line-height: 1.1;
}

/* right arrow */
.arrow {
  font-size: 24px;
  opacity: .45;
  line-height: 1;
  display:flex;
  align-items:center;
  justify-content:center;
  width: 30px;
  flex: 0 0 auto;
}

/* footer */
.footer {
  height: 64px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size: 12px;
  opacity: .72;
  user-select:none;
}

/* links */
a, a:hover, a:visited { color: inherit; text-decoration: none; }

/* mobile polish */
@media (max-width: 980px) {
  .ticker { width: 100%; }
  .frame { padding: 16px 14px; }
  .cards { width: min(980px, 96vw); gap: 12px; }
  .title { font-size: 19px; }
  .sub { font-size: 12px; }
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
    # IMPORTANT: target="_blank" -> abre en nueva pestaña
    return dcc.Link(
        href=url,
        target="_blank",
        className="sc-link",
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
                    # Icono sugerido para Client360: "bi-person-badge" o "bi-people" o "bi-journal-text"
                    card("Client360", "Client coverage • CRM • activity", "bi-person-badge", TARGETS["Client360"]),
                ],
            ),
        ),

        html.Div(
            className="footer",
            children=[
                html.Div("SciTech Lab"),
                html.Div("Docs / Runbooks • Changelog • System Status"),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
