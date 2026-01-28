# SciTech Lab

## Overview

SciTech Lab is a portal application for investment and quantitative analysis tools. It serves as a landing page that showcases and links to various financial analysis applications including SigmaLab (correlation matrices, regime detection, asset clustering), GroWise (portfolio performance, benchmark analysis), and other planned investment tools. The application fetches real-time market data (S&P 500, VIX) from Yahoo Finance to display current market conditions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite with hot module replacement
- **Routing**: Wouter (lightweight React router)
- **State Management**: TanStack React Query for server state
- **Styling**: Tailwind CSS with shadcn/ui component library
- **Animations**: Framer Motion for UI animations
- **UI Components**: Radix UI primitives with custom styling via class-variance-authority

### Backend Architecture
- **Runtime**: Node.js with Express 5
- **Language**: TypeScript compiled with tsx
- **API Structure**: RESTful endpoints under `/api/*` prefix
- **Development**: Vite dev server integration with HMR proxy

### Data Layer
- **ORM**: Drizzle ORM with PostgreSQL dialect
- **Schema Location**: `shared/schema.ts` (shared between frontend and backend)
- **Validation**: Zod schemas generated from Drizzle schemas via drizzle-zod
- **Migrations**: Drizzle Kit with `db:push` command

### Project Structure
```
├── client/           # React frontend application
│   └── src/
│       ├── components/ui/  # shadcn/ui components
│       ├── pages/          # Page components
│       ├── hooks/          # Custom React hooks
│       └── lib/            # Utilities and query client
├── server/           # Express backend
│   ├── index.ts      # Entry point
│   ├── routes.ts     # API route definitions
│   ├── storage.ts    # Data storage abstraction
│   └── vite.ts       # Vite dev server integration
├── shared/           # Shared types and schemas
│   └── schema.ts     # Drizzle database schema
└── script/           # Build scripts
```

### Build System
- Development: `npm run dev` runs tsx with Vite middleware
- Production: Custom build script bundles server with esbuild, client with Vite
- Output: `dist/` directory with `index.cjs` (server) and `public/` (client assets)

## External Dependencies

### Database
- **PostgreSQL**: Primary database via `DATABASE_URL` environment variable
- **Session Store**: connect-pg-simple for Express sessions

### Financial Data APIs
- **Yahoo Finance**: yahoo-finance2 package for real-time market quotes (S&P 500, VIX)
- Cached with 60-second TTL to reduce API calls

### Key NPM Packages
- **UI**: Full shadcn/ui component set with Radix primitives
- **Charts**: Recharts for data visualization
- **Forms**: React Hook Form with Zod resolver
- **HTTP Client**: Fetch API with custom wrapper in queryClient.ts