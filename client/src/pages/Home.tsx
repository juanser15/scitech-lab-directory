import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Grid3X3, 
  TrendingUp, 
  Globe2, 
  UserSquare2,
  ArrowUpRight,
  Shield,
  Clock,
  Activity
} from "lucide-react";
import bgImage from "@assets/generated_images/glowing_network_constellation_dark.png";

interface AppCard {
  id: string;
  title: string;
  subtitle: string;
  icon: typeof Grid3X3;
  url: string;
  status: "LIVE" | "BETA" | "SOON";
  enabled: boolean;
  accentColor: string;
}

const APPS: AppCard[] = [
  {
    id: "sigmalab",
    title: "SigmaLab",
    subtitle: "Correlation matrices · Regime detection · Asset clustering",
    icon: Grid3X3,
    url: "https://sigma.sci-techlab.com",
    status: "LIVE",
    enabled: true,
    accentColor: "from-emerald-500/20 to-emerald-500/5",
  },
  {
    id: "growise",
    title: "GroWise",
    subtitle: "Portfolio performance · Benchmark analysis · Factor attribution",
    icon: TrendingUp,
    url: "https://growise.sci-techlab.com",
    status: "LIVE",
    enabled: true,
    accentColor: "from-blue-500/20 to-blue-500/5",
  },
  {
    id: "atlas",
    title: "Atlas",
    subtitle: "Market intelligence · Quantitative research · Macro context",
    icon: Globe2,
    url: "https://atlas.sci-techlab.com",
    status: "SOON",
    enabled: false,
    accentColor: "from-amber-500/20 to-amber-500/5",
  },
  {
    id: "client360",
    title: "Client360",
    subtitle: "Coverage management · Activity tracking · Reporting suite",
    icon: UserSquare2,
    url: "https://script.google.com/a/macros/sci.tech/s/AKfycby_6WGTvIZ7MNqJOLF32s-uucxGdwRQj7zmP-FPahZ7gsZYZLQxQPWpIBuWvd_htFOs/exec",
    status: "LIVE",
    enabled: true,
    accentColor: "from-violet-500/20 to-violet-500/5",
  },
];

function StatusIndicator({ status }: { status: AppCard["status"] }) {
  const config = {
    LIVE: {
      icon: Shield,
      label: "LIVE",
      dotColor: "bg-emerald-400",
      textColor: "text-emerald-400/90",
      borderColor: "border-emerald-500/20",
    },
    BETA: {
      icon: Activity,
      label: "BETA",
      dotColor: "bg-blue-400",
      textColor: "text-blue-400/90",
      borderColor: "border-blue-500/20",
    },
    SOON: {
      icon: Clock,
      label: "SOON",
      dotColor: "bg-amber-400/60",
      textColor: "text-amber-400/70",
      borderColor: "border-amber-500/15",
    },
  };

  const { label, dotColor, textColor, borderColor } = config[status];

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-[10px] font-semibold tracking-[0.15em] uppercase border ${borderColor} bg-white/[0.02] backdrop-blur-sm ${textColor}`}
      data-testid={`indicator-status-${status.toLowerCase()}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor} ${status === 'LIVE' ? 'animate-pulse' : ''}`} />
      <span>{label}</span>
    </div>
  );
}

function AppCardComponent({ app, index }: { app: AppCard; index: number }) {
  const Icon = app.icon;

  const cardContent = (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay: index * 0.1,
        ease: [0.25, 0.46, 0.45, 0.94]
      }}
      whileHover={app.enabled ? { 
        y: -4,
        transition: { duration: 0.2 }
      } : {}}
      className={`
        group relative overflow-hidden
        flex items-center justify-between 
        p-5 sm:p-6 rounded-xl
        border border-white/[0.06]
        bg-gradient-to-br from-white/[0.04] to-white/[0.01]
        backdrop-blur-2xl
        ${app.enabled ? "cursor-pointer" : "opacity-50 cursor-default"}
        transition-all duration-300 ease-out
      `}
      data-testid={`card-app-${app.id}`}
    >
      {/* Subtle accent gradient on hover */}
      <div className={`absolute inset-0 bg-gradient-to-r ${app.accentColor} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      
      {/* Top border glow on hover */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative flex items-center gap-5 min-w-0">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center bg-white/[0.03] border border-white/[0.06] group-hover:border-white/[0.12] group-hover:bg-white/[0.06] transition-all duration-300"
          data-testid={`icon-${app.id}`}
        >
          <Icon className="w-5 h-5 text-white/80 group-hover:text-white transition-colors duration-300" strokeWidth={1.5} />
        </div>
        <div className="flex flex-col min-w-0">
          <span
            className="text-lg sm:text-xl font-semibold text-white tracking-tight leading-tight"
            data-testid={`text-title-${app.id}`}
          >
            {app.title}
          </span>
          <span
            className="mt-1.5 text-[13px] text-white/60 font-light tracking-wide"
            data-testid={`text-subtitle-${app.id}`}
          >
            {app.subtitle}
          </span>
        </div>
      </div>

      <div className="relative flex items-center gap-4 flex-shrink-0">
        <StatusIndicator status={app.status} />
        <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-white/[0.03] border border-white/[0.06] group-hover:border-white/[0.15] group-hover:bg-white/[0.08] transition-all duration-300">
          <ArrowUpRight className="w-4 h-4 text-white/40 group-hover:text-white/80 transition-colors duration-300" strokeWidth={2} />
        </div>
      </div>
    </motion.div>
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

interface MarketClock {
  city: string;
  timezone: string;
  market: string;
  openHour: number;
  closeHour: number;
}

const MARKETS: MarketClock[] = [
  { city: "NYC", timezone: "America/New_York", market: "NYSE", openHour: 9.5, closeHour: 16 },
  { city: "LDN", timezone: "Europe/London", market: "LSE", openHour: 8, closeHour: 16.5 },
  { city: "TYO", timezone: "Asia/Tokyo", market: "TSE", openHour: 9, closeHour: 15 },
  { city: "HKG", timezone: "Asia/Hong_Kong", market: "HKEX", openHour: 9.5, closeHour: 16 },
  { city: "SYD", timezone: "Australia/Sydney", market: "ASX", openHour: 10, closeHour: 16 },
];

function WorldClocks() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getMarketStatus = (market: MarketClock) => {
    const now = new Date();
    const hour = parseInt(now.toLocaleString("en-US", { timeZone: market.timezone, hour: "2-digit", hour12: false }));
    const minute = parseInt(now.toLocaleString("en-US", { timeZone: market.timezone, minute: "2-digit" }));
    const day = now.toLocaleString("en-US", { timeZone: market.timezone, weekday: "short" });
    
    if (day === "Sat" || day === "Sun") return false;
    const totalHours = hour + minute / 60;
    return totalHours >= market.openHour && totalHours < market.closeHour;
  };

  const formatTime = (timezone: string) => {
    return time.toLocaleTimeString("en-US", {
      timeZone: timezone,
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.3 }}
      className="hidden lg:flex items-center gap-1 px-2 py-2 rounded-xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-xl"
      data-testid="widget-world-clocks"
    >
      {MARKETS.map((market, idx) => {
        const isOpen = getMarketStatus(market);
        return (
          <div key={market.city} className="flex items-center">
            <div className="flex flex-col items-center px-4 py-1 min-w-[72px]">
              <div className="flex items-center gap-1.5 mb-1">
                <span className={`w-1.5 h-1.5 rounded-full ${isOpen ? 'bg-emerald-400' : 'bg-white/20'}`} />
                <span className="text-[10px] font-medium tracking-wider text-white/50 uppercase">
                  {market.city}
                </span>
              </div>
              <span className="text-base font-mono text-white/90 tracking-wider">
                {formatTime(market.timezone)}
              </span>
            </div>
            {idx < MARKETS.length - 1 && (
              <div className="w-px h-8 bg-white/[0.06]" />
            )}
          </div>
        );
      })}
    </motion.div>
  );
}

function LiveIndicator() {
  return (
    <div className="sm:hidden flex items-center gap-2 px-3 py-1.5 rounded-md border border-white/[0.06] bg-white/[0.02]">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
      <span className="text-[10px] font-medium tracking-[0.1em] text-white/50 uppercase">Live</span>
    </div>
  );
}

export default function Home() {
  return (
    <div
      className="relative min-h-screen w-full overflow-x-hidden"
      style={{
        background: `linear-gradient(180deg, rgba(3,6,12,0.5) 0%, rgba(3,6,12,0.4) 100%), url(${bgImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Noise texture overlay */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-[0.02]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Subtle vignette - reduced intensity */}
      <div 
        className="fixed inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.15) 100%)",
        }}
      />

      {/* Accent glow */}
      <div 
        className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] pointer-events-none opacity-30"
        style={{
          background: "radial-gradient(ellipse at center top, rgba(16,185,129,0.08) 0%, transparent 70%)",
        }}
      />

      <div className="relative z-10 flex flex-col min-h-screen max-w-[1200px] mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-between py-6 sm:py-8 border-b border-white/[0.04]"
          data-testid="header-main"
        >
          <div className="flex items-center gap-6" data-testid="brand-logo">
            <div className="flex flex-col">
              <span className="text-xl sm:text-2xl font-semibold tracking-[0.2em] text-white leading-none">
                SCITECH
              </span>
              <span className="text-[9px] sm:text-[10px] tracking-[0.4em] text-white/60 mt-1.5 font-light">
                INVESTMENTS
              </span>
            </div>
                      </div>

          <div className="flex items-center gap-4">
            <WorldClocks />
            <LiveIndicator />
          </div>
        </motion.header>

        {/* Content */}
        <main className="flex-1 flex flex-col justify-center py-12 sm:py-16">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="mb-10"
          >
            <h1 className="text-[11px] sm:text-xs tracking-[0.25em] text-white/50 font-light uppercase mb-2">
              Application Suite
            </h1>
            <div className="w-12 h-px bg-gradient-to-r from-emerald-500/50 to-transparent" />
          </motion.div>

          <div className="space-y-3">
            {APPS.map((app, index) => (
              <AppCardComponent key={app.id} app={app} index={index} />
            ))}
          </div>
        </main>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="flex flex-wrap justify-between items-center py-6 sm:py-8 border-t border-white/[0.04] gap-4"
          data-testid="footer-main"
        >
          <div className="flex items-center gap-6">
            <span className="text-[11px] tracking-[0.1em] text-white/50 font-light uppercase">
              SciTech Lab
            </span>
            <span className="text-[10px] text-white/35">v2.0</span>
          </div>
          <div className="flex items-center gap-6 text-[11px] text-white/40 font-light">
            <span className="hover:text-white/70 transition-colors cursor-pointer">Documentation</span>
            <span className="text-white/20">·</span>
            <span className="hover:text-white/70 transition-colors cursor-pointer">Changelog</span>
            <span className="text-white/20">·</span>
            <span className="hover:text-white/70 transition-colors cursor-pointer">Status</span>
          </div>
        </motion.footer>
      </div>
    </div>
  );
}
