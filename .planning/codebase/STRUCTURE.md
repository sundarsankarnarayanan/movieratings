# Codebase Structure

**Analysis Date:** 2026-01-27

## Directory Layout

```
MovieRatings/
├── agents/                    # Python data collection agents
├── scrapers/                  # Web scraping utilities
├── web-app/                   # Next.js frontend application
│   ├── app/                   # App Router pages
│   │   ├── movies/[id]/       # Dynamic movie detail route
│   │   ├── page.tsx           # Homepage
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   ├── utils/                 # Utility modules
│   └── public/                # Static assets
├── .planning/                 # Project planning documents
│   └── codebase/              # Codebase analysis docs
├── *.py                       # Root-level Python scripts
├── *.sql                      # Database schema files
└── *.sh                       # Shell scripts
```

## Directory Purposes

**`agents/`**
- Purpose: Data collection and analysis agents
- Contains: Python classes that run as standalone scripts
- Key files:
  - `release_tracker.py`: Fetches new movie releases from TMDB
  - `rating_monitor.py`: Scrapes ratings from RT, IMDb, Metacritic
  - `trend_analyzer.py`: Classifies movie trends from snapshots
  - `reviewer_discovery.py`: Builds critic database
  - `web_scraping_tracker.py`: Additional scraping utilities

**`scrapers/`**
- Purpose: Reusable web scraping classes
- Contains: Abstract base scraper and platform implementations
- Key files:
  - `base.py`: `BaseScraper` abstract class with `_get_soup()` helper
  - `rotten_tomatoes.py`: RT-specific scraping logic

**`web-app/`**
- Purpose: Next.js 16 frontend application
- Contains: App Router pages, React components, utilities
- Key files:
  - `app/page.tsx`: Homepage with trending movies grid
  - `app/movies/[id]/page.tsx`: Movie detail page with charts
  - `app/layout.tsx`: Root layout with fonts and metadata
  - `components/MovieCard.tsx`: Reusable movie card component
  - `components/ReviewTrendChart.tsx`: Recharts line chart (client component)
  - `components/TrendBadge.tsx`: Status indicator badge
  - `utils/db.ts`: PostgreSQL connection pool

**Root Python Scripts:**
- Purpose: Standalone utilities and legacy entry points
- Key files:
  - `database.py`: Database class for Python agent data access
  - `tmdb_client.py`: TMDB API client class
  - `main.py`: Legacy scraper entry point
  - `summarization_agent.py`: AI summary generation (uses LLM)
  - `llm_client.py`: LLM API wrapper

**SQL Schema Files:**
- Purpose: Database schema definitions
- Key files:
  - `schema_v2.sql`: Core schema with movies, reviewers, rating_snapshots
  - `schema_trend_analysis.sql`: Adds daily_review_snapshots, movie_trends
  - `schema_safe_migration.sql`: Migration utilities
  - `setup_schema.sql`: Initial setup script

**Shell Scripts:**
- Purpose: Automation and startup
- Key files:
  - `start_platform.sh`: Master startup script
  - `populate_db.sh`: Initial data population
  - `run_pipeline.sh`: Pipeline execution

## Key File Locations

**Entry Points:**
- `/Users/sundar/Projects/MovieRatings/start_platform.sh`: Platform startup
- `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx`: Web app homepage
- `/Users/sundar/Projects/MovieRatings/agents/rating_monitor.py`: Continuous monitoring

**Configuration:**
- `/Users/sundar/Projects/MovieRatings/.env`: Environment variables (Python)
- `/Users/sundar/Projects/MovieRatings/web-app/.env.local`: Web app environment
- `/Users/sundar/Projects/MovieRatings/web-app/package.json`: Node dependencies
- `/Users/sundar/Projects/MovieRatings/requirements.txt`: Python dependencies

**Core Logic:**
- `/Users/sundar/Projects/MovieRatings/database.py`: Python DB operations
- `/Users/sundar/Projects/MovieRatings/web-app/utils/db.ts`: TypeScript DB client
- `/Users/sundar/Projects/MovieRatings/agents/trend_analyzer.py`: Trend classification

**Testing:**
- `/Users/sundar/Projects/MovieRatings/test_scraper.py`: Scraper tests
- `/Users/sundar/Projects/MovieRatings/test_mcp_server.py`: MCP server tests
- `/Users/sundar/Projects/MovieRatings/test_movie_agent.py`: Agent tests

## Naming Conventions

**Files:**
- Python: `snake_case.py` (e.g., `rating_monitor.py`, `release_tracker.py`)
- TypeScript/React: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- SQL: `snake_case.sql` (e.g., `schema_v2.sql`)
- Shell: `snake_case.sh`

**Directories:**
- Lowercase with hyphens for web-app dirs (e.g., `web-app`)
- Lowercase for Python packages (e.g., `agents`, `scrapers`)

## Where to Add New Code

**New Agent:**
- Implementation: `/Users/sundar/Projects/MovieRatings/agents/`
- Follow pattern: Class with `__init__` (DB connection), methods, `run()` entry point
- Add `if __name__ == "__main__"` block for standalone execution

**New Web Page:**
- Implementation: `/Users/sundar/Projects/MovieRatings/web-app/app/`
- Use folder-based routing (e.g., `app/rankings/page.tsx` for `/rankings`)
- Server Component by default, add `'use client'` only if needed

**New React Component:**
- Implementation: `/Users/sundar/Projects/MovieRatings/web-app/components/`
- Use PascalCase filename matching component name
- Server Component unless interactivity required

**New Scraper:**
- Implementation: `/Users/sundar/Projects/MovieRatings/scrapers/`
- Extend `BaseScraper` from `base.py`
- Implement `get_top_reviewers()` and `get_latest_reviews()`

**New Database Table:**
- Schema: Add to `/Users/sundar/Projects/MovieRatings/schema_v2.sql` or create migration file
- Python access: Add methods to `database.py`
- TypeScript access: Write raw SQL in page components or add to `utils/db.ts`

**Utilities:**
- Python shared helpers: Add to root level or create `utils/` directory
- TypeScript shared helpers: `/Users/sundar/Projects/MovieRatings/web-app/utils/`

## Special Directories

**`.planning/`**
- Purpose: Project planning and analysis documents
- Generated: No (manually created)
- Committed: Yes

**`web-app/.next/`**
- Purpose: Next.js build output
- Generated: Yes (by `npm run build` or `npm run dev`)
- Committed: No (in .gitignore)

**`web-app/node_modules/`**
- Purpose: Node.js dependencies
- Generated: Yes (by `npm install`)
- Committed: No (in .gitignore)

**`web-app/public/`**
- Purpose: Static assets served at root URL
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-01-27*
