# Codebase Structure

**Analysis Date:** 2026-01-26

## Directory Layout

```
MovieRatings/
├── web-app/                    # Next.js frontend application
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page (trending + recent)
│   │   ├── movies/[id]/       # Dynamic movie detail page
│   │   ├── globals.css        # Global Tailwind styles
│   │   └── favicon.ico
│   ├── components/            # Reusable React components
│   │   ├── MovieCard.tsx      # Movie card with rating display
│   │   ├── ReviewTrendChart.tsx # Line chart for rating trends
│   │   └── TrendBadge.tsx     # Status badge (trending/sleeper/stable)
│   ├── utils/                 # Utility functions
│   │   └── db.ts             # PostgreSQL pool and query wrapper
│   ├── public/                # Static assets (SVG icons)
│   ├── .next/                 # Build output (generated)
│   ├── package.json           # npm dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── next.config.ts         # Next.js configuration
│   ├── eslint.config.mjs      # ESLint rules
│   └── postcss.config.mjs     # PostCSS/Tailwind config
│
├── agents/                     # Python data collection agents
│   ├── release_tracker.py     # Monitor TMDB for new movie releases
│   ├── rating_monitor.py      # Fetch current ratings from platforms
│   ├── trend_analyzer.py      # Compute movie trend metrics
│   ├── reviewer_discovery.py  # Find reviewers from sources
│   └── web_scraping_tracker.py # Track scraping activity
│
├── scrapers/                   # Web scraping modules
│   ├── rotten_tomatoes.py     # Rotten Tomatoes scraper
│   ├── base.py               # Base scraper class
│   └── __init__.py
│
├── Python root modules:
│   ├── main.py               # Pipeline orchestration entry point
│   ├── mcp_server.py         # MCP server for Claude integration
│   ├── movie_release_agent.py # Agent for release discovery
│   ├── database.py           # PostgreSQL connection and queries
│   ├── llm_client.py         # LLM service client
│   ├── summarization_agent.py # AI-powered movie summarization
│   ├── tmdb_client.py        # TMDB API wrapper
│   ├── apply_sql.py          # SQL migration utility
│   └── [test files]          # Testing utilities
│
├── .planning/                 # GSD planning documents
│   └── codebase/
│       ├── ARCHITECTURE.md    # This architecture analysis
│       └── STRUCTURE.md       # This structure guide
│
├── Database:
│   └── movies.db             # SQLite (dev only, replaced by PostgreSQL in prod)
│
└── Configuration:
    ├── .env                   # Environment variables (git ignored)
    ├── .env.example          # Environment template
    ├── schema_safe_migration.sql # Database schema
    ├── requirements.txt       # Python dependencies
    ├── Makefile              # Common commands
    └── SETUP_INSTRUCTIONS.md # Setup guide
```

## Directory Purposes

**`web-app/app/`:**
- Purpose: Next.js pages and routes using App Router
- Contains: Page components (async RSC), layout, global styles
- Key files: `layout.tsx` (root), `page.tsx` (home), `movies/[id]/page.tsx` (detail)

**`web-app/components/`:**
- Purpose: Reusable React UI components
- Contains: Movie cards, charts, badges
- Key files: `MovieCard.tsx`, `ReviewTrendChart.tsx`, `TrendBadge.tsx`

**`web-app/utils/`:**
- Purpose: Shared utility functions and helpers
- Contains: Database access wrapper
- Key files: `db.ts` (PostgreSQL Pool)

**`agents/`:**
- Purpose: Autonomous Python agents for data collection and analysis
- Contains: Separate agent modules for specific responsibilities
- Key files: `release_tracker.py`, `rating_monitor.py`, `trend_analyzer.py`

**`scrapers/`:**
- Purpose: Web scraping implementations for external review platforms
- Contains: Base scraper class and platform-specific implementations
- Key files: `base.py` (abstract), `rotten_tomatoes.py` (concrete)

## Key File Locations

**Entry Points:**
- `web-app/app/layout.tsx`: Root layout for Next.js application
- `web-app/app/page.tsx`: Homepage showing trending and recent movies
- `web-app/app/movies/[id]/page.tsx`: Movie detail page with full analytics
- `main.py`: Backend pipeline orchestration
- `mcp_server.py`: MCP integration server

**Configuration:**
- `web-app/package.json`: Frontend dependencies and scripts
- `web-app/tsconfig.json`: TypeScript compiler options with path aliases (`@/*` → root)
- `web-app/next.config.ts`: Next.js build configuration
- `.env`: Environment variables (DB credentials, API keys)
- `requirements.txt`: Python dependencies
- `schema_safe_migration.sql`: PostgreSQL schema definition

**Core Logic:**
- `web-app/utils/db.ts`: Database connection and query execution
- `web-app/app/page.tsx`: Data fetching for home page (trending/recent movies)
- `web-app/app/movies/[id]/page.tsx`: Data fetching for movie detail
- `database.py`: Python database abstraction layer
- `llm_client.py`: LLM API integration (Claude)
- `agents/*.py`: Data collection and analysis workflows

**Testing:**
- `test_mcp_server.py`: MCP server tests
- `test_scraper.py`: Scraper functionality tests
- `test_movie_agent.py`: Movie agent tests
- `verify_scrapers.py`: Scraper verification

## Naming Conventions

**Files:**
- Page components: `[name]/page.tsx` (Next.js convention)
- UI Components: PascalCase (e.g., `MovieCard.tsx`, `ReviewTrendChart.tsx`)
- Python modules: snake_case (e.g., `release_tracker.py`, `rating_monitor.py`)
- Utilities: Descriptive names in lowercase (e.g., `db.ts`)
- Tests: `test_*.py` prefix (e.g., `test_scraper.py`)

**Directories:**
- Pages: Lowercase, kebab-case for multi-word (`movies`, `[id]`)
- Components: PascalCase plural (e.g., `components/`)
- Agents: Plural for collection (`agents/`)
- Utils: Lowercase plural (`utils/`)

**TypeScript/React:**
- Component names: PascalCase (e.g., `MovieCard`, `ReviewTrendChart`)
- Interfaces: PascalCase with `Props` suffix (e.g., `MovieCardProps`, `TrendBadgeProps`)
- Type names: PascalCase (e.g., `DailySnapshot`, `Movie`)

## Where to Add New Code

**New Feature (UI):**
- Primary code: `web-app/app/[feature]/page.tsx` (create new route)
- Components: `web-app/components/[ComponentName].tsx`
- Tests: `web-app/__tests__/[feature].test.tsx` (if added)
- Follow: Use async RSC for data fetching, Tailwind for styling, TypeScript for types

**New Component:**
- Implementation: `web-app/components/[ComponentName].tsx`
- Props: Define TypeScript interface with `Props` suffix
- Styling: Use Tailwind classes only (no CSS modules)
- Example: Export as default, use PascalCase filename

**New Data Collection Agent:**
- Implementation: `agents/[agent_name].py`
- Pattern: Import from `database.py` for queries, `llm_client.py` for LLM
- Entry: Call from `main.py` orchestration or schedule as cron job
- Example: `agents/new_feature_agent.py` → import in `main.py` → execute in pipeline

**Utilities/Helpers:**
- Backend: `database.py` for DB, create helper functions there
- Frontend: `web-app/utils/[util_name].ts` for reusable functions
- Pattern: Export as named exports, document with JSDoc/comments

**Database Queries:**
- Direct SQL in page components where fetching (e.g., `app/page.tsx`)
- Abstract frequently-used queries into `database.py` functions
- Use parameterized queries to prevent SQL injection: `$1`, `$2` placeholders
- Wrap in try-catch for graceful error handling

## Special Directories

**`web-app/.next/`:**
- Purpose: Next.js build output and generated files
- Generated: Yes (via `npm run build`)
- Committed: No (in `.gitignore`)

**`web-app/node_modules/`:**
- Purpose: npm installed dependencies
- Generated: Yes (via `npm install`)
- Committed: No (in `.gitignore`)

**`.planning/codebase/`:**
- Purpose: GSD analysis documents for codebase guidance
- Contains: ARCHITECTURE.md, STRUCTURE.md, and other analysis docs
- Committed: Yes
- Usage: Referenced by `/gsd:plan-phase` and `/gsd:execute-phase` commands

---

*Structure analysis: 2026-01-26*
