import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Grid3X3, 
  TrendingUp, 
  Globe2, 
  UserSquare2,
  ArrowUpRight,
  Shield,
  Clock,
  Activity,
  Sparkles,
  Zap,
  BarChart3,
  GraduationCap,
  BookOpen,
  ChevronRight
} from "lucide-react";
import bgImage from "../assets/generated_images/glowing_network_constellation_dark.png";

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
    accentColor: "from-amber-400/25 to-amber-400/5",
  },
  {
    id: "growise",
    title: "GroWise",
    subtitle: "Portfolio performance · Benchmark analysis · Factor attribution",
    icon: TrendingUp,
    url: "https://growise.sci-techlab.com",
    status: "LIVE",
    enabled: true,
    accentColor: "from-amber-400/25 to-amber-400/5",
  },
  {
    id: "atlas",
    title: "Atlas",
    subtitle: "Market intelligence · Quantitative research · Macro context",
    icon: Globe2,
    url: "https://atlas.sci-techlab.com",
    status: "SOON",
    enabled: false,
    accentColor: "from-slate-400/20 to-slate-400/5",
  },
  {
    id: "client360",
    title: "Client360",
    subtitle: "Coverage management · Activity tracking · Reporting suite",
    icon: UserSquare2,
    url: "https://script.google.com/a/macros/sci.tech/s/AKfycby_6WGTvIZ7MNqJOLF32s-uucxGdwRQj7zmP-FPahZ7gsZYZLQxQPWpIBuWvd_htFOs/exec",
    status: "LIVE",
    enabled: true,
    accentColor: "from-amber-400/25 to-amber-400/5",
  },
];

function StatusIndicator({ status }: { status: AppCard["status"] }) {
  const config = {
    LIVE: {
      icon: Shield,
      label: "LIVE",
      dotColor: "bg-amber-400",
      textColor: "text-amber-300/90",
      borderColor: "border-amber-400/30",
    },
    BETA: {
      icon: Activity,
      label: "BETA",
      dotColor: "bg-blue-400",
      textColor: "text-blue-300/90",
      borderColor: "border-blue-400/30",
    },
    SOON: {
      icon: Clock,
      label: "SOON",
      dotColor: "bg-slate-400/60",
      textColor: "text-slate-400/70",
      borderColor: "border-slate-500/20",
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
        p-3.5 sm:p-4 rounded-xl
        border border-amber-200/10
        bg-gradient-to-br from-slate-800/80 to-slate-900/60
        backdrop-blur-2xl shadow-lg
        ${app.enabled ? "cursor-pointer hover:border-amber-400/30 hover:shadow-amber-900/20 hover:shadow-xl" : "opacity-50 cursor-default"}
        transition-all duration-300 ease-out
      `}
      data-testid={`card-app-${app.id}`}
    >
      {/* Subtle accent gradient on hover */}
      <div className={`absolute inset-0 bg-gradient-to-r ${app.accentColor} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      
      {/* Top border glow on hover */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-400/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative flex items-center gap-5 min-w-0">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center bg-amber-400/5 border border-amber-400/10 group-hover:border-amber-400/30 group-hover:bg-amber-400/10 transition-all duration-300"
          data-testid={`icon-${app.id}`}
        >
          <Icon className="w-4 h-4 text-amber-200/80 group-hover:text-amber-200 transition-colors duration-300" strokeWidth={1.5} />
        </div>
        <div className="flex flex-col min-w-0">
          <span
            className="text-base sm:text-lg font-semibold text-amber-50 tracking-tight leading-tight"
            data-testid={`text-title-${app.id}`}
          >
            {app.title}
          </span>
          <span
            className="mt-1 text-[12px] text-slate-300/80 font-light tracking-wide"
            data-testid={`text-subtitle-${app.id}`}
          >
            {app.subtitle}
          </span>
        </div>
      </div>

      <div className="relative flex items-center gap-4 flex-shrink-0">
        <StatusIndicator status={app.status} />
        <div className="w-7 h-7 rounded-md flex items-center justify-center bg-amber-400/5 border border-amber-400/10 group-hover:border-amber-400/30 group-hover:bg-amber-400/15 transition-all duration-300">
          <ArrowUpRight className="w-3.5 h-3.5 text-amber-200/50 group-hover:text-amber-200 transition-colors duration-300" strokeWidth={2} />
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
      className="hidden lg:flex items-center gap-1 px-2 py-2 rounded-xl border border-amber-200/10 bg-slate-800/50 backdrop-blur-xl"
      data-testid="widget-world-clocks"
    >
      {MARKETS.map((market, idx) => {
        const isOpen = getMarketStatus(market);
        return (
          <div key={market.city} className="flex items-center">
            <div className="flex flex-col items-center px-4 py-1 min-w-[72px]">
              <div className="flex items-center gap-1.5 mb-1">
                <span className={`w-1.5 h-1.5 rounded-full ${isOpen ? 'bg-amber-400' : 'bg-slate-500/50'}`} />
                <span className="text-[10px] font-medium tracking-wider text-slate-400 uppercase">
                  {market.city}
                </span>
              </div>
              <span className="text-base font-mono text-amber-50/90 tracking-wider">
                {formatTime(market.timezone)}
              </span>
            </div>
            {idx < MARKETS.length - 1 && (
              <div className="w-px h-8 bg-amber-200/10" />
            )}
          </div>
        );
      })}
    </motion.div>
  );
}

function LiveIndicator() {
  return (
    <div className="lg:hidden flex items-center gap-2 px-3 py-1.5 rounded-md border border-amber-400/20 bg-slate-800/50">
      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
      <span className="text-[10px] font-medium tracking-[0.1em] text-amber-200/70 uppercase">Live</span>
    </div>
  );
}

function GreetingBanner() {
  const [greeting, setGreeting] = useState("");
  const [quote, setQuote] = useState({ text: "", author: "" });

  const quotes = [
    { text: "The only way to win is to work and work and work and hope to have a few insights.", author: "Jim Simons" },
    { text: "In a world where luck plays a large role, focus on the process rather than the outcome.", author: "Ed Thorp" },
    { text: "The essence of mathematics is not to make simple things complicated, but to make complicated things simple.", author: "Stan Gudder" },
    { text: "Beware of geeks bearing formulas.", author: "Warren Buffett (on quants)" },
    { text: "Markets look a lot less efficient from the banks of the Hudson than from the banks of the Charles.", author: "Fischer Black" },
    { text: "The normal distribution is a theoretical fiction.", author: "Benoît Mandelbrot" },
    { text: "If you torture the data long enough, it will confess to anything.", author: "Ronald Coase" },
    { text: "In theory, theory and practice are the same. In practice, they are not.", author: "Albert Einstein" },
    { text: "Nature uses only the longest threads to weave her patterns.", author: "Richard Feynman" },
    { text: "The stock market is a device for transferring money from the impatient to the patient.", author: "Emanuel Derman" },
  ];

  useEffect(() => {
    const hour = new Date().toLocaleString("en-US", { 
      timeZone: "America/New_York", 
      hour: "numeric", 
      hour12: false 
    });
    const h = parseInt(hour);
    
    if (h >= 5 && h < 12) setGreeting("Good morning");
    else if (h >= 12 && h < 17) setGreeting("Good afternoon");
    else if (h >= 17 && h < 21) setGreeting("Good evening");
    else setGreeting("Good night");

    setQuote(quotes[Math.floor(Math.random() * quotes.length)]);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="mb-8 p-4 rounded-xl border border-amber-400/10 bg-gradient-to-r from-amber-400/5 via-transparent to-blue-400/5"
      data-testid="greeting-banner"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium text-amber-200/90 mb-2 block">{greeting}</span>
          <p className="text-sm text-slate-300/80 italic leading-relaxed">
            "{quote.text}"
          </p>
          <p className="mt-1 text-xs text-slate-400/60">
            — {quote.author}
          </p>
        </div>
        <QuickStats />
      </div>
    </motion.div>
  );
}

function QuickStats() {
  const [stats, setStats] = useState({ spx: 0, vix: 0, spxChange: 0, loading: true });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/market-data");
        if (response.ok) {
          const data = await response.json();
          setStats({
            spx: data.spx,
            vix: data.vix,
            spxChange: data.spxChange,
            loading: false
          });
        }
      } catch (error) {
        console.error("Failed to fetch market data:", error);
        setStats(prev => ({ ...prev, loading: false }));
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (stats.loading) {
    return (
      <div className="hidden sm:flex items-center gap-4 px-4 py-2 rounded-lg border border-slate-700/50 bg-slate-800/30">
        <span className="text-xs text-slate-500">Loading...</span>
      </div>
    );
  }

  return (
    <div className="hidden sm:flex items-center gap-4 px-4 py-2 rounded-lg border border-slate-700/50 bg-slate-800/30">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-3.5 h-3.5 text-slate-400" />
        <div className="flex flex-col">
          <span className="text-[9px] text-slate-500 uppercase tracking-wide">S&P 500</span>
          <div className="flex items-center gap-1">
            <span className={`text-sm font-mono ${stats.spxChange >= 0 ? "text-emerald-400" : "text-red-400"}`}>
              {stats.spx.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className={`text-[10px] ${stats.spxChange >= 0 ? "text-emerald-400" : "text-red-400"}`}>
              {stats.spxChange >= 0 ? "+" : ""}{stats.spxChange.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>
      <div className="w-px h-6 bg-slate-700/50" />
      <div className="flex items-center gap-2">
        <Zap className="w-3.5 h-3.5 text-slate-400" />
        <div className="flex flex-col">
          <span className="text-[9px] text-slate-500 uppercase tracking-wide">VIX</span>
          <span className="text-sm font-mono text-amber-300">
            {stats.vix.toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <div
      className="relative min-h-screen w-full overflow-x-hidden"
      style={{
        background: `linear-gradient(135deg, #0c1220 0%, #141e30 50%, #0f172a 100%)`,
      }}
    >
      {/* Background image with blend */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-40"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          mixBlendMode: "screen",
        }}
      />

      {/* Golden accent glow top */}
      <div 
        className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at center top, rgba(251,191,36,0.08) 0%, transparent 60%)",
        }}
      />

      {/* Blue accent glow bottom */}
      <div 
        className="fixed bottom-0 right-0 w-[600px] h-[400px] pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at bottom right, rgba(59,130,246,0.06) 0%, transparent 60%)",
        }}
      />

      <div className="relative z-10 flex flex-col min-h-screen max-w-[1200px] mx-auto px-6 sm:px-8 lg:px-12">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-between py-6 sm:py-8 border-b border-amber-200/10"
          data-testid="header-main"
        >
          <div className="flex items-center gap-6" data-testid="brand-logo">
            <div className="flex flex-col">
              <span className="text-xl sm:text-2xl font-semibold tracking-[0.2em] text-amber-50 leading-none">
                SCITECH
              </span>
              <span className="text-[9px] sm:text-[10px] tracking-[0.4em] text-amber-200/60 mt-1.5 font-medium">
                INVESTMENTS
              </span>
            </div>
            {/* OPTION 2: University link in header */}
            <a 
              href="#university" 
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-md border border-amber-400/20 bg-amber-400/5 hover:bg-amber-400/10 hover:border-amber-400/40 transition-all duration-300"
              data-testid="link-university-header"
            >
              <GraduationCap className="w-3.5 h-3.5 text-amber-300/80" />
              <span className="text-[10px] tracking-[0.15em] text-amber-200/80 font-medium uppercase">University</span>
            </a>
          </div>

          <div className="flex items-center gap-4">
            <WorldClocks />
            <LiveIndicator />
          </div>
        </motion.header>

        {/* Content */}
        <main className="flex-1 flex flex-col justify-center py-12 sm:py-16">
          <GreetingBanner />

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="mb-6"
          >
            <h1 className="text-[11px] sm:text-xs tracking-[0.25em] text-amber-200/70 font-medium uppercase mb-2">
              Application Suite
            </h1>
            <div className="w-16 h-px bg-gradient-to-r from-amber-400/60 to-transparent" />
          </motion.div>

          <div className="space-y-2.5">
            {APPS.map((app, index) => (
              <AppCardComponent key={app.id} app={app} index={index} />
            ))}
          </div>

          {/* OPTION 3: University section below apps */}
          <motion.div
            id="university"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-12 pt-8 border-t border-amber-200/10"
          >
            <div className="flex items-center gap-3 mb-4">
              <GraduationCap className="w-5 h-5 text-amber-400/80" />
              <h2 className="text-[11px] sm:text-xs tracking-[0.25em] text-amber-200/70 font-medium uppercase">
                SciTech University
              </h2>
            </div>
            
            <a
              href="#"
              className="group block p-5 rounded-xl border border-amber-400/15 bg-gradient-to-br from-amber-400/5 via-slate-800/50 to-blue-400/5 hover:border-amber-400/30 hover:shadow-lg hover:shadow-amber-900/10 transition-all duration-300"
              data-testid="card-university"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-amber-400/20 to-amber-600/10 border border-amber-400/20">
                    <BookOpen className="w-5 h-5 text-amber-300" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-amber-50 tracking-tight">Campus</h3>
                    <p className="text-[12px] text-slate-300/70 mt-0.5">Courses, certifications & learning resources</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-amber-200/50 group-hover:text-amber-200 transition-colors">
                  <span className="hidden sm:inline text-[11px] tracking-wide uppercase">Explore</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </a>
          </motion.div>
        </main>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="flex flex-wrap justify-between items-center py-6 sm:py-8 border-t border-amber-200/10 gap-4"
          data-testid="footer-main"
        >
          <div className="flex items-center gap-6">
            <span className="text-[11px] tracking-[0.1em] text-slate-400 font-light uppercase">
              SciTech Lab
            </span>
            <span className="text-[10px] text-amber-200/40">v2.0</span>
          </div>
          <div className="flex items-center gap-6 text-[11px] text-slate-400 font-light">
            <span className="hover:text-amber-200/80 transition-colors cursor-pointer">Documentation</span>
            <span className="text-slate-600">·</span>
            <span className="hover:text-amber-200/80 transition-colors cursor-pointer">Changelog</span>
            <span className="text-slate-600">·</span>
            <span className="hover:text-amber-200/80 transition-colors cursor-pointer">Status</span>
          </div>
        </motion.footer>
      </div>
    </div>
  );
}
