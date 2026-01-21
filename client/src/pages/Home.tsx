import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { 
  Grid3X3, 
  TrendingUp, 
  Globe2, 
  UserSquare2,
  ChevronRight,
  Lock,
  Clock,
  Zap
} from "lucide-react";
import bgImage from "@assets/bg_scitech_map.png";

interface AppCard {
  id: string;
  title: string;
  subtitle: string;
  icon: typeof Grid3X3;
  url: string;
  status: "PROD" | "BETA" | "COMING SOON";
  enabled: boolean;
}

const APPS: AppCard[] = [
  {
    id: "sigmalab",
    title: "SigmaLab",
    subtitle: "Correlation · regimes · clustering",
    icon: Grid3X3,
    url: "https://sigma.sci-techlab.com",
    status: "PROD",
    enabled: true,
  },
  {
    id: "growise",
    title: "GroWise Dashboard",
    subtitle: "Performance · benchmarks · attribution",
    icon: TrendingUp,
    url: "https://growise.sci-techlab.com",
    status: "PROD",
    enabled: true,
  },
  {
    id: "atlas",
    title: "SciTech Atlas",
    subtitle: "Market + quant context · curated research",
    icon: Globe2,
    url: "https://atlas.sci-techlab.com",
    status: "COMING SOON",
    enabled: false,
  },
  {
    id: "client360",
    title: "Client360",
    subtitle: "Client coverage · activity · reporting",
    icon: UserSquare2,
    url: "https://script.google.com/a/macros/sci.tech/s/AKfycby_6WGTvIZ7MNqJOLF32s-uucxGdwRQj7zmP-FPahZ7gsZYZLQxQPWpIBuWvd_htFOs/exec",
    status: "PROD",
    enabled: true,
  },
];

function StatusBadge({ status }: { status: AppCard["status"] }) {
  const config = {
    PROD: {
      icon: Lock,
      className: "border-green-500/30 bg-green-500/10 text-green-300/90",
    },
    BETA: {
      icon: Zap,
      className: "border-blue-500/30 bg-blue-500/10 text-blue-300/90",
    },
    "COMING SOON": {
      icon: Clock,
      className: "border-amber-500/30 bg-amber-500/10 text-amber-300/90",
    },
  };

  const { icon: Icon, className } = config[status];

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wide border ${className}`}
      data-testid={`badge-status-${status.toLowerCase().replace(" ", "-")}`}
    >
      <Icon className="w-3 h-3" />
      <span>{status}</span>
    </div>
  );
}

function AppCardComponent({ app }: { app: AppCard }) {
  const Icon = app.icon;

  const cardContent = (
    <div
      className={`
        flex items-center justify-between p-4 sm:p-5 rounded-2xl
        border border-white/10
        bg-gradient-to-b from-[rgba(17,27,45,0.72)] to-[rgba(17,27,45,0.34)]
        shadow-xl backdrop-blur-xl
        transition-all duration-150 ease-out
        ${app.enabled ? "cursor-pointer hover:translate-y-[-2px] hover:border-primary/30 hover:shadow-2xl" : "opacity-60 cursor-default"}
      `}
      data-testid={`card-app-${app.id}`}
    >
      <div className="flex items-center gap-4 min-w-0">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center bg-black/20 border border-white/10 flex-shrink-0"
          data-testid={`icon-${app.id}`}
        >
          <Icon className="w-5 h-5 text-foreground/90" />
        </div>
        <div className="flex flex-col min-w-0">
          <span
            className="text-lg sm:text-xl font-bold text-foreground/95 leading-tight"
            data-testid={`text-title-${app.id}`}
          >
            {app.title}
          </span>
          <span
            className="mt-1 text-xs text-foreground/60 truncate"
            data-testid={`text-subtitle-${app.id}`}
          >
            {app.subtitle}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 flex-shrink-0">
        <StatusBadge status={app.status} />
        <ChevronRight className="w-6 h-6 text-foreground/50" />
      </div>
    </div>
  );

  if (app.enabled && app.url) {
    return (
      <a
        href={app.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block no-underline"
        data-testid={`link-app-${app.id}`}
      >
        {cardContent}
      </a>
    );
  }

  return cardContent;
}

function TradingViewTicker() {
  return (
    <div
      className="hidden lg:block w-[900px] h-14 rounded-xl overflow-hidden border border-white/10 bg-black/20 shadow-lg"
      data-testid="widget-ticker"
    >
      <iframe
        srcDoc={`
          <!DOCTYPE html>
          <html>
          <body style="margin:0;background:transparent;">
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
          </body>
          </html>
        `}
        className="w-full h-full border-0"
        title="TradingView Ticker"
      />
    </div>
  );
}

function MarketsPill() {
  return (
    <a
      href="https://www.tradingview.com/markets/indices/"
      target="_blank"
      rel="noopener noreferrer"
      className="lg:hidden inline-flex items-center gap-2 px-3 py-2 rounded-full border border-white/10 bg-black/20 text-foreground/80 font-semibold text-xs tracking-wide no-underline"
      data-testid="link-markets"
    >
      <TrendingUp className="w-3.5 h-3.5" />
      <span>Markets</span>
    </a>
  );
}

export default function Home() {
  return (
    <div
      className="relative min-h-screen w-full overflow-x-hidden"
      style={{
        background: `#070A10 url(${bgImage}) no-repeat center center fixed`,
        backgroundSize: "cover",
      }}
    >
      {/* Overlay gradient */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(1200px 700px at 20% 18%, rgba(0,0,0,0.10), transparent 60%),
            radial-gradient(900px 520px at 80% 25%, rgba(0,0,0,0.08), transparent 55%),
            linear-gradient(180deg, rgba(0,0,0,0.10), rgba(0,0,0,0.42))
          `,
        }}
      />

      <div className="relative z-10 flex flex-col min-h-screen px-4 sm:px-6 py-4 sm:py-5">
        {/* Header */}
        <header
          className="flex flex-wrap items-center justify-between gap-4 h-auto sm:h-16"
          data-testid="header-main"
        >
          <div className="flex items-end gap-3" data-testid="brand-logo">
            <div className="flex flex-col">
              <span className="text-2xl font-extrabold tracking-[0.16em] text-foreground/92 leading-none">
                SCITECH
              </span>
              <span className="text-[10px] tracking-[0.34em] text-foreground/65 mt-1">
                INVESTMENTS
              </span>
            </div>
          </div>

          <TradingViewTicker />
          <MarketsPill />
        </header>

        {/* Content */}
        <main className="flex-1 flex items-center justify-center py-6 sm:py-0">
          <div className="w-full max-w-[1040px] space-y-3.5">
            {APPS.map((app) => (
              <AppCardComponent key={app.id} app={app} />
            ))}
          </div>
        </main>

        {/* Footer */}
        <footer
          className="flex flex-wrap justify-between items-center h-16 text-xs text-foreground/60 gap-4"
          data-testid="footer-main"
        >
          <span>SciTech Lab</span>
          <span className="text-foreground/50">Docs / Runbooks · Changelog · System Status</span>
        </footer>
      </div>
    </div>
  );
}
