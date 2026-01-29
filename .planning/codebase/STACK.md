# Technology Stack

**Analysis Date:** 2026-01-27

## Languages

**Primary:**
- TypeScript 5.x - Next.js web application (`web-app/`)
- Python 3.9+ - Backend agents, scrapers, and data pipeline (root directory)

**Secondary:**
- SQL (PostgreSQL) - Database schema and stored procedures (`schema_*.sql`)
- Bash - Orchestration scripts (`start_platform.sh`, `populate_db.sh`)

## Runtime

**Frontend Environment:**
- Node.js (version not pinned, inferred from Next.js 16)
- npm (package manager)
- Lockfile: `web-app/package-lock.json` present

**Backend Environment:**
- Python 3.9+ (referenced in `start_platform.sh`)
- pip (package manager)
- No lockfile (only `requirements.txt`)

## Frameworks

**Web Framework:**
- Next.js 16.1.4 - React-based SSR/SSG framework
  - App Router pattern (uses `app/` directory)
  - Server Components for data fetching
  - `revalidate = 0` for real-time data

**UI Framework:**
- React 19.2.3 - UI library
- React DOM 19.2.3 - React DOM renderer
- Tailwind CSS 4.x - Utility-first CSS framework
  - PostCSS integration via `@tailwindcss/postcss`

**Python Framework:**
- No web framework (Python is used for agents/scripts only)
- MCP (Model Context Protocol) via `mcp[cli]` for AI tool server

**Testing:**
- None detected in web-app
- None detected in Python code

**Build/Dev:**
- ESLint 9.x with Next.js config - Linting
- TypeScript 5.x - Type checking
- PostCSS - CSS processing

## Key Dependencies

**Frontend Critical:**
- `@supabase/supabase-js` ^2.91.0 - Database client (via Supabase)
- `pg` ^8.17.2 - Direct PostgreSQL client
- `recharts` ^3.7.0 - Charting library for trend visualization
- `lucide-react` ^0.562.0 - Icon library
- `date-fns` ^4.1.0 - Date formatting utilities

**Backend Critical:**
- `psycopg2-binary` - PostgreSQL adapter for Python
- `beautifulsoup4` - HTML parsing for web scraping
- `requests` - HTTP client for API/scraping
- `openai` - OpenAI API for AI summarization
- `supabase` - Supabase Python client
- `python-dotenv` - Environment variable management
- `mcp[cli]` - Model Context Protocol server

## Configuration

**Environment Variables (Backend - `.env.example`):**
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_service_role_key
TMDB_API_KEY=your_tmdb_api_key
OPENAI_API_KEY=your_openai_api_key
```

**Environment Variables (Frontend - `web-app/.env.local.example`):**
```
NEXT_PUBLIC_SUPABASE_URL=your_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

**Database Connection (used by both):**
```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
```

**TypeScript Configuration (`web-app/tsconfig.json`):**
- Target: ES2017
- Module: ESNext with bundler resolution
- Strict mode enabled
- Path alias: `@/*` maps to `./*`

**Build Configuration:**
- `web-app/next.config.ts` - Default Next.js config (no custom options)
- `web-app/postcss.config.mjs` - Tailwind CSS via PostCSS
- `web-app/eslint.config.mjs` - Next.js ESLint rules

## Platform Requirements

**Development:**
- Node.js (compatible with Next.js 16)
- Python 3.9+
- PostgreSQL 14+ (for gen_random_uuid and advanced features)
- macOS/Linux (shell scripts use bash)

**Production:**
- PostgreSQL database (Supabase hosted)
- Node.js hosting for Next.js app
- Python runtime for background agents

**Database:**
- PostgreSQL with `movie_platform` schema
- Uses UUIDs, JSONB, arrays, materialized views
- Custom functions and triggers

## Scripts

**npm scripts (`web-app/package.json`):**
```bash
npm run dev     # Start Next.js dev server
npm run build   # Production build
npm run start   # Start production server
npm run lint    # Run ESLint
```

**Shell scripts (root):**
- `start_platform.sh` - Master startup script
- `populate_db.sh` - Database population
- `run_pipeline.sh` - Data pipeline runner

**Python entry points:**
- `main.py` - Scraper entry point
- `movie_release_agent.py` - TMDB movie fetcher
- `summarization_agent.py` - AI summarization
- `mcp_server.py` - MCP tool server
- `agents/rating_monitor.py` - Real-time rating monitor
- `agents/trend_analyzer.py` - Trend analysis
- `agents/release_tracker.py` - Release tracking
- `agents/reviewer_discovery.py` - Reviewer discovery
- `agents/web_scraping_tracker.py` - Web scraping tracker

---

*Stack analysis: 2026-01-27*
