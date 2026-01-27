# SciTech Lab

## Overview

SciTech Lab is a portal application for investment analytics and quantitative finance tools. It serves as a centralized directory that links to specialized financial applications including:

- **SigmaLab**: Correlation matrices, regime detection, and asset clustering
- **GroWise**: Portfolio performance, benchmark analysis, and factor attribution
- **Atlas**: Risk engine with VaR calculations and stress testing
- **Client360**: Client management integration via Google Apps Script

The application displays real-time market data (S&P 500, VIX) fetched from Yahoo Finance and provides a notification system for updates across the SciTech ecosystem.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight client-side routing)
- **Styling**: Tailwind CSS with custom dark theme configuration
- **UI Components**: shadcn/ui component library (New York style variant)
- **State Management**: TanStack React Query for server state
- **Animations**: Framer Motion for UI transitions
- **Build Tool**: Vite with React plugin

The frontend follows a component-based architecture with:
- Pages in `client/src/pages/`
- Reusable UI components in `client/src/components/ui/`
- Custom hooks in `client/src/hooks/`
- Utility functions in `client/src/lib/`

### Backend Architecture

- **Framework**: Express.js 5 on Node.js
- **Language**: TypeScript with ESM modules
- **Build**: esbuild for production bundling with selective dependency bundling
- **Development**: tsx for TypeScript execution with Vite middleware for HMR

The server architecture uses:
- `server/index.ts`: Express app initialization and middleware setup
- `server/routes.ts`: API route definitions
- `server/storage.ts`: In-memory data storage abstraction
- `server/static.ts`: Static file serving for production
- `server/vite.ts`: Vite development server integration

### Data Storage

- **Database**: PostgreSQL with Drizzle ORM
- **Schema**: Defined in `shared/schema.ts` using Drizzle's PostgreSQL dialect
- **Migrations**: Generated to `./migrations` directory via `drizzle-kit push`
- **Current Implementation**: MemStorage class provides in-memory storage for users and notifications (database integration ready but uses memory fallback)

### API Structure

REST API endpoints under `/api/`:
- `GET /api/market-data`: Returns cached S&P 500 and VIX data from Yahoo Finance (1-minute cache)
- `GET /api/notifications`: Returns system notifications

## External Dependencies

### Third-Party Services

- **Yahoo Finance** (via yahoo-finance2): Real-time market data for S&P 500 (^GSPC) and VIX (^VIX)
- **External SciTech Applications**:
  - SigmaLab: `https://sigma.sci-techlab.com`
  - GroWise: `https://growise.sci-techlab.com`
  - Atlas: `https://atlas.sci-techlab.com`
  - Client360: Google Apps Script endpoint

### Database

- PostgreSQL database (connection via `DATABASE_URL` environment variable)
- Drizzle ORM for type-safe database operations
- drizzle-zod for schema validation

### Key NPM Packages

- **UI**: @radix-ui primitives, class-variance-authority, clsx, tailwind-merge
- **Data Fetching**: @tanstack/react-query
- **Charts**: recharts
- **Forms**: react-hook-form with @hookform/resolvers, zod validation
- **Date Handling**: date-fns
- **Session Management**: express-session, connect-pg-simple

### Replit Integrations

- @replit/vite-plugin-runtime-error-modal: Error overlay in development
- @replit/vite-plugin-cartographer: Development tooling
- @replit/vite-plugin-dev-banner: Development environment indicator