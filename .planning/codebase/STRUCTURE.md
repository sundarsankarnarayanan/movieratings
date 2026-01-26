# Codebase Structure

**Analysis Date:** 2026-01-26

## Directory Layout

```
MovieRatings/
├── web-app/                    # Next.js frontend application
│   ├── app/                    # Next.js app router pages
│   │   ├── page.tsx            # Homepage (/route)
│   │   ├── layout.tsx          # Root layout
│   │   ├── movie/
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Movie detail page (/movie/[tmdb_id])
│   │   ├── movies/
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Alt movie detail page (/movies/[tmdb_id])
│   │   ├── globals.css         # Global Tailwind styles
│   │   └── favicon.ico
│   ├── components/             # React components
│   │   ├── ReviewTrendChart.tsx     # Chart for daily review trends
│   │   ├── MovieCard.tsx            # Movie card component
│   │   └── TrendBadge.tsx           # Status badge (trending_up/down/sleeper_hit)
│   ├── utils/                  # Shared utilities
│   │   └── db.ts               # PostgreSQL connection pool and query function
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── next.config.ts          # Next.js config
│   ├── eslint.config.mjs       # ESLint config
│   └── postcss.config.mjs      # PostCSS/Tailwind config
│
├── agents/                     # Python data collection agents
│   ├── rating_monitor.py       # Agent 3: Scrapes current ratings
│   ├── trend_analyzer.py       # Agent 4: Analyzes trends, detects anomalies
│   ├── release_tracker.py      # Agent 1: Discovers new movie releases
│   ├── reviewer_discovery.py   # Agent 2: Finds top reviewers by region
│   └── web_scraping_tracker.py # Web scraping telemetry
│
├── scrapers/                   # Scraper implementations
│   ├── base.py                 # BaseScraper abstract class
│   └── rotten_tomatoes.py      # RottenTomatoes-specific scraper
│
├── .planning/                  # GSD planning documents
│   └── codebase/               # Codebase analysis (this directory)
│       ├── ARCHITECTURE.md
│       ├── STRUCTURE.md
│       ├── STACK.md
│       └── INTEGRATIONS.md
│
├── setup_schema.sql            # Initial database schema (v1)
├── schema_v2.sql               # Current database schema (v2) with time-series tables
├── schema_trend_analysis.sql   # Trend analysis schema additions
├── database.py                 # Python Database class for legacy operations
├── main.py                     # Entry point for reviewer scraping pipeline
├── llm_client.py               # LLM client wrapper (Claude API)
├── tmdb_client.py              # TMDB API client
├── mcp_server.py               # MCP (Model Context Protocol) server
├── apply_sql.py                # Utility to apply SQL migrations
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (local)
├── .env.example                # Example env template
├── Makefile                    # Build/dev commands
├── run_pipeline.sh             # Script to run collection pipeline
├── populate_db.sh              # Script to populate initial data
├── start_platform.sh           # Script to start web and agents
├── README.md                   # Project readme
├── PROJECT.md                  # Project scope/goals
├── REQUIREMENTS.md             # Requirements specification
├── ROADMAP.md                  # Development roadmap
├── STATE.md                    # Current project state
├── GSD_JOURNEY.md              # GSD execution history
└── QUICK_REF.md                # Quick reference guide

```

## Directory Purposes

**web-app/:**
- Purpose: Next.js React application serving the web UI
- Contains: Page routes, React components, utilities, configuration
- Key files: `app/page.tsx`, `app/movie/[id]/page.tsx`, `components/ReviewTrendChart.tsx`, `utils/db.ts`

**web-app/app/:**
- Purpose: Next.js App Router - defines all HTTP routes
- Contains: Page components (.tsx files), layout components, global CSS
- Key files: `page.tsx` (homepage), `layout.tsx` (root), `movie/[id]/page.tsx` (movie detail)

**web-app/components/:**
- Purpose: Reusable React UI components
- Contains: Presentational components rendered by pages
- Key files: `ReviewTrendChart.tsx` (recharts visualization), `TrendBadge.tsx` (status indicator)

**web-app/utils/:**
- Purpose: Shared helper functions and clients
- Contains: Database connection, utility functions
- Key files: `db.ts` (PostgreSQL client)

**agents/:**
- Purpose: Python agents for data collection and analysis
- Contains: Scheduled tasks that run independently
- Key files: `rating_monitor.py` (scrapes ratings), `trend_analyzer.py` (computes trends)

**scrapers/:**
- Purpose: Web scraping implementations
- Contains: Site-specific parsers
- Key files: `base.py` (abstract base class), `rotten_tomatoes.py` (RT implementation)

**.planning/codebase/:**
- Purpose: GSD-generated codebase documentation
- Contains: Architecture, structure, conventions, testing, concerns, stack, integrations
- Key files: `ARCHITECTURE.md`, `STRUCTURE.md`, `STACK.md`, `INTEGRATIONS.md`

## Key File Locations

**Entry Points:**

- `web-app/app/layout.tsx`: Root HTML layout, font loading, metadata
- `web-app/app/page.tsx`: Homepage with trending/recent movies
- `web-app/app/movie/[id]/page.tsx`: Movie detail with trends and history
- `main.py`: Python pipeline entry point for reviewer scraping

**Configuration:**

- `web-app/package.json`: Node dependencies (Next.js, React, Supabase, Recharts)
- `web-app/tsconfig.json`: TypeScript compiler config (path alias: `@/*`)
- `web-app/next.config.ts`: Next.js configuration
- `requirements.txt`: Python dependencies (psycopg2, requests, BeautifulSoup4, python-dotenv)
- `.env`: Environment variables (DB_HOST, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME)

**Core Logic:**

- `web-app/utils/db.ts`: PostgreSQL connection pool, `query()` function
- `database.py`: Python Database class with upsert/query methods
- `agents/rating_monitor.py`: Scrapes ratings, inserts snapshots
- `agents/trend_analyzer.py`: Aggregates daily snapshots, detects anomalies
- `scrapers/base.py`: Abstract scraper with `_get_soup()` helper
- `scrapers/rotten_tomatoes.py`: RT-specific scraper implementation

**Testing:**

- `test_mcp_server.py`: Tests for MCP server
- `test_scraper.py`: Tests for scrapers
- `test_movie_agent.py`: Tests for agents
- `verify_scrapers.py`: Verification script for scraper functionality

**Database Schema:**

- `setup_schema.sql`: Initial schema (v1) with reviewers, movies, reviews, movie_regions tables
- `schema_v2.sql`: Current schema (v2) with rating_snapshots (time-series), daily_review_snapshots, materialized views
- `schema_trend_analysis.sql`: Trend analysis tables and functions

## Naming Conventions

**Files:**

- Page components: `page.tsx` (App Router convention)
- Server components: No prefix, async by default
- Client components: `'use client'` directive at top
- Utility files: Lowercase with underscores (`db.ts`, `review_trend_chart.tsx`)
- SQL files: `schema_*.sql`, `setup_*.sql`
- Python scripts: `snake_case` (e.g., `rating_monitor.py`, `trend_analyzer.py`)

**Directories:**

- Features: Named after what they contain (`components/`, `agents/`, `scrapers/`)
- Dynamic routes: Bracket notation `[param]` (Next.js convention)
- Python packages: Lowercase, can contain `__init__.py`

## Where to Add New Code

**New Feature (End-to-End):**

- Frontend page: `web-app/app/[feature]/page.tsx` or `web-app/app/[feature]/[id]/page.tsx`
- Component: `web-app/components/[FeatureName].tsx` (PascalCase for components)
- Utility: `web-app/utils/[featureName].ts` (camelCase)
- Query logic: Add functions to page file, call `query()` from `@/utils/db`
- Style: Use Tailwind CSS in component className (no separate CSS files required)

**New Collection Agent:**

- File location: `agents/[feature_name].py`
- Pattern: Create class extending common patterns from `rating_monitor.py` (init DB connection, set search_path, implement run() method)
- Database integration: Use psycopg2 with RealDictCursor, write results to appropriate table
- Logging: Write status to `scrape_logs` table

**New Scraper:**

- File location: `scrapers/[platform_name].py` (lowercase platform)
- Pattern: Create class extending `BaseScraper` abstract class
- Methods: Implement `get_top_reviewers()` and `get_latest_reviews()` methods
- Helper: Use `self._get_soup(url)` to fetch and parse HTML

**Utilities/Helpers:**

- Shared utilities: `web-app/utils/[name].ts` (TypeScript for frontend, Python files at root or in `agents/`)
- Database helpers: Add methods to `database.py` class (Python) or create utility functions in `web-app/utils/db.ts`

## Special Directories

**web-app/.next/:**
- Purpose: Build artifacts and generated types
- Generated: Yes (created by Next.js build)
- Committed: No (in .gitignore)

**web-app/node_modules/:**
- Purpose: Installed Node dependencies
- Generated: Yes (created by npm install)
- Committed: No (in .gitignore)

**web-app/public/:**
- Purpose: Static files served by Next.js (favicons, images, etc.)
- Generated: No
- Committed: Yes

**.planning/codebase/:**
- Purpose: GSD-generated documentation
- Generated: Yes (created by /gsd:map-codebase)
- Committed: Yes (part of repo)

---

*Structure analysis: 2026-01-26*
