import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import YahooFinance from "yahoo-finance2";

const yf = new YahooFinance();

let cachedMarketData: { spx: number; vix: number; spxChange: number; timestamp: number } | null = null;
const CACHE_DURATION = 60000; // 1 minute cache

async function fetchMarketData() {
  const now = Date.now();
  
  if (cachedMarketData && (now - cachedMarketData.timestamp) < CACHE_DURATION) {
    return cachedMarketData;
  }

  try {
    const [spxQuote, vixQuote] = await Promise.all([
      yf.quote("^GSPC"),
      yf.quote("^VIX")
    ]);

    cachedMarketData = {
      spx: spxQuote.regularMarketPrice || 0,
      vix: vixQuote.regularMarketPrice || 0,
      spxChange: spxQuote.regularMarketChangePercent || 0,
      timestamp: now
    };

    return cachedMarketData;
  } catch (error) {
    console.error("Error fetching market data:", error);
    return cachedMarketData || { spx: 0, vix: 0, spxChange: 0, timestamp: now };
  }
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  app.get("/api/market-data", async (req, res) => {
    try {
      const data = await fetchMarketData();
      res.json(data);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch market data" });
    }
  });

  return httpServer;
}
