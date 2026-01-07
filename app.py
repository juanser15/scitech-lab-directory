import dash
from dash import html, dcc
import dash_auth
import dash_bootstrap_components as dbc
import urllib.request
import socket

# ======================
# AUTH
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
    "pamela.ghisla@sci.tech": "Sc1T3ch_PG_2025!",
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
# TARGETS (PROD)
# ======================
TARGETS = {
    "SigmaLab": "https://sigma.sci-techlab.com",
    "GroWise":  "https://growise.sci-techlab.com",
    "Atlas":    "https://atlas.sci-techlab.com",
    "Client360": "https://script.google.com/a/macros/sci.tech/s/AKfycby_6WGTvIZ7MNqJOLF32s-uucxGdwRQj7zmP-FPahZ7gsZYZLQxQPWpIBuWvd_htFOs/exec",
}

# ======================
# Health check (optional): if Atlas not reachable, show Coming Soon
# ======================
def url_is_reachable(url: str, timeout_sec: float = 2.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout_sec)
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "SciTechDirectory/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return 200 <= resp.status < 500  # accept 3xx/4xx as "reachable" (DNS + server responds)
    except Exception:
        return False

ATLAS_ENABLED = url_is_reachable(TARGETS["Atlas"], timeout_sec=2.0)

# ======================
# CSS
# ======================
THEME_CSS = r"""
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

.frame:before{
  content:"";
  position:absolute; inset:0;
  z-index: 0;
  background:
    radial-gradient(1200px 700px at 20% 18%, rgba(0,0,0,0.10), transparent 60%),
    radial-gradient(900px 520px at 80% 25%, rgba(0,0,0,0.08), transparent 55%),
    linear-gradient(180deg, rgba(0,0,0,0.10), rgba(0,0,0,0.42));
  pointer-events:none;
}

.topbar, .content, .footer { position: relative; z-index: 1; }

.topbar{
  height: 64px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 16px;
}

.brand {
  display:flex;
  align-items:flex-end;
  gap: 12px;
  min-width: 280px;
}

.logo {
  letter-spacing: 0.16em;
  font-weight: 720;
  font-size: 26px;
  color: rgba(233,238,247,0.92);
  line-height: 1;
}
.logo small {
  display:block;
  font-size: 10px;
  letter-spacing: 0.34em;
  opacity: .75;
  margin-top: 6px;
}

.envpill{
  margin-bottom: 2px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: .08em;
  font-weight: 700;
  color: rgba(233,238,247,0.85);
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(0,0,0,0.22);
}

.ticker {
  width: 900px;
  height: 56px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(0,0,0,0.20);
  box-shadow: 0 12px 30px rgba(0,0,0,0.25);
}

.markets-pill{
  display:none;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(0,0,0,0.22);
  color: rgba(233,238,247,0.82);
  font-weight: 650;
  font-size: 12px;
  letter-spacing: .02em;
}

.content {
  height: calc(100vh - 128px);
  display:flex;
  justify-content:center;
  align-items:center;
}

.cards {
  width: min(1040px, 94vw);
  display:grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin: 0 auto;
}

.sc-card {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 16px 22px;
  border-radius: 16px;
  border: 1px solid rgba(233,238,247,0.14);
  background: linear-gradient(180deg, rgba(17,27,45,0.72), rgba(17,27,45,0.34));
  box-shadow:
    0 18px 46px rgba(0,0,0,0.34),
    inset 0 1px 0 rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  cursor:pointer;
  transition: transform 140ms ease-out, box-shadow 140ms ease-out, border-color 140ms ease-out;
}
.sc-card:hover {
  transform: translateY(-2px);
  border-color: rgba(82,224,208,0.30);
  box-shadow:
    0 24px 64px rgba(0,0,0,0.44),
    inset 0 1px 0 rgba(255,255,255,0.06);
}
.sc-card.disabled {
  opacity: .62;
  cursor: default;
}
.sc-card.disabled:hover { transform:none; }

.left {
  display:flex;
  align-items:center;
  gap: 14px;
  min-width: 0;
}

.icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(0,0,0,0.22);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 20px;
  color: rgba(233,238,247,0.90);
  flex: 0 0 auto;
}

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
  font-weight: 720;
  color: rgba(233,238,247,0.93);
  line-height: 1.15;
}
.sub {
  margin-top: 4px;
  font-size: 12px;
  opacity: .70;
}

.right {
  display:flex;
  align-items:center;
  gap: 12px;
  flex: 0 0 auto;
}

.badge {
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: .08em;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(0,0,0,0.18);
  color: rgba(233,238,247,0.78);
}
.badge.prod { border-color: rgba(34,197,94,0.28); background: rgba(34,197,94,0.10); }
.badge.soon { border-color: rgba(245,158,11,0.28); background: rgba(245,158,11,0.10); }

.badge.beta {
  border-color: rgba(59, 130, 246, 0.28);
  background: rgba(59, 130, 246, 0.10);
  color: rgba(191, 219, 254, 0.95);
}

.arrow {
  font-size: 26px;
  opacity: .55;
  line-height: 1;
  width: 28px;
  display:flex;
  align-items:center;
  justify-content:center;
}

.footer {
  height: 64px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-size: 12px;
  opacity: .70;
}

a, a:hover, a:visited { color: inherit; text-decoration: none; }

@media (max-width: 980px) {
  .ticker { width: 100%; }
}

@media (max-width: 760px) {
  html, body { overflow: auto; }
  .frame { padding: 14px 14px; }
  .topbar{ height: auto; align-items:flex-start; gap: 10px; }
  .brand { min-width: 0; }
  .ticker { display:none; }
  .markets-pill{ display:inline-flex; }
  .content { height: auto; padding: 18px 0 8px 0; align-items:flex-start; }
  .cards { width: min(980px, 96vw); gap: 12px; }
  .sc-card { padding: 14px 16px; border-radius: 16px; }
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
# TradingView ticker
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

MARKETS_PILL = dcc.Link(
    href="https://www.tradingview.com/markets/indices/",
    target="_blank",
    children=html.Div([html.I(className="bi bi-graph-up"), html.Span(" Markets")], className="markets-pill"),
)

def badge(label: str, kind: str = "prod"):
    icon = {"prod": "bi-lock-fill", "soon": "bi-hourglass-split"}.get(kind, "bi-dot")
    return html.Div([html.I(className=f"bi {icon}"), html.Span(label)], className=f"badge {kind}")

def card(title, subtitle, icon, url=None, status="PROD", status_kind="prod", enabled=True):
    right = html.Div(
        className="right",
        children=[
            badge(status, status_kind),
            html.Div("›", className="arrow"),
        ],
    )

    body = html.Div(
        className=("sc-card" + ("" if enabled else " disabled")),
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
            right,
        ],
    )

    if enabled and url:
        return dcc.Link(href=url, target="_blank", children=body)
    return body

# ======================
# LAYOUT
# ======================
app.layout = html.Div(
    className="frame",
    children=[
        html.Div(
            className="topbar",
            children=[
                html.Div(
                    className="brand",
                    children=[
                        html.Div(["SCITECH", html.Small("INVESTMENTS")], className="logo"),                    ],
                ),
                TV_TICKER,
                MARKETS_PILL,
            ],
        ),

        html.Div(
            className="content",
            children=html.Div(
                className="cards",
                children=[
                    card(
                        "SigmaLab",
                        "Correlation · regimes · clustering",
                        "bi-grid-3x3-gap",
                        TARGETS["SigmaLab"],
                        status="PROD",
                        status_kind="prod",
                        enabled=True,
                    ),
                    card(
                        "GroWise Dashboard",
                        "Performance · benchmarks · attribution",
                        "bi-graph-up-arrow",
                        TARGETS["GroWise"],
                        status="PROD",
                        status_kind="prod",
                        enabled=True,
                    ),
                    card(
                        "SciTech Atlas",
                        "Market + quant context · curated research",
                        "bi-globe2",
                        TARGETS["Atlas"],
                        status=("PROD" if ATLAS_ENABLED else "COMING SOON"),
                        status_kind=("prod" if ATLAS_ENABLED else "soon"),
                        enabled=ATLAS_ENABLED,  # auto
                    ),
                    card(
                        "Client360",
                        "Client coverage · activity · reporting",
                        "bi-person-vcard",
                        TARGETS["Client360"],
                        status="PROD",
                        status_kind="prod",
                        enabled=True,
                    ),
                ],
            ),
        ),

        html.Div(
            className="footer",
            children=[
                html.Div("SciTech Lab"),
                html.Div("Docs / Runbooks · Changelog · System Status"),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
