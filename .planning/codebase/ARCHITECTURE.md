# Architecture

**Analysis Date:** 2026-01-27

## Pattern Overview

**Overall:** Multi-tier data pipeline with web dashboard

**Key Characteristics:**
- Python-based data ingestion agents operating independently
- PostgreSQL database with dedicated `movie_platform` schema
- Next.js 16 frontend with Server Components for data fetching
- Agent-based architecture: each agent has a single responsibility
- Time-series data design for rating trend analysis

## Layers

**Data Ingestion Layer (Python Agents):**
- Purpose: Collect movie data from external sources
- Location: `/Users/sundar/Projects/MovieRatings/agents/`
- Contains: Independent Python scripts that fetch and store data
- Depends on: External APIs (TMDB), web scraping (RT, IMDb, Metacritic), PostgreSQL
- Used by: Database (writes data for frontend consumption)

**Data Access Layer (Python):**
- Purpose: Database abstraction for Python agents
- Location: `/Users/sundar/Projects/MovieRatings/database.py`
- Contains: `Database` class with CRUD operations
- Depends on: psycopg2, PostgreSQL
- Used by: All Python agents and scripts

**Presentation Layer (Next.js):**
- Purpose: Web dashboard for viewing movie trends
- Location: `/Users/sundar/Projects/MovieRatings/web-app/`
- Contains: React Server Components, pages, UI components
- Depends on: PostgreSQL (via pg client), Recharts for visualization
- Used by: End users via browser

**Scraping Layer:**
- Purpose: Web scraping utilities for review platforms
- Location: `/Users/sundar/Projects/MovieRatings/scrapers/`
- Contains: Base scraper class and platform-specific implementations
- Depends on: requests, BeautifulSoup
- Used by: Agents that need to scrape web content

## Data Flow

**Movie Discovery Flow:**
1. `agents/release_tracker.py` fetches new releases from TMDB API
2. Enriches with detailed metadata via TMDB movie endpoint
3. Stores in `movies` table with regions array
4. Initializes empty `rating_snapshots` for each source

**Rating Collection Flow:**
1. `agents/rating_monitor.py` gets active movies (last 30 days)
2. Scrapes RT, IMDb, Metacritic for each movie
3. Compares with last snapshot, stores if changed
4. Creates `daily_review_snapshots` for trend analysis
5. Logs scraping activity to `scrape_logs`

**Trend Analysis Flow:**
1. `agents/trend_analyzer.py` reads `daily_review_snapshots`
2. Calculates slope, detects sleeper hits, identifies anomalies
3. Classifies trend as: `trending_up`, `trending_down`, `sleeper_hit`, `stable`
4. Stores classification in `movie_trends` table

**Frontend Data Flow:**
1. Server Component (`app/page.tsx`) calls `query()` from `utils/db.ts`
2. Raw SQL queries against PostgreSQL with `movie_platform` schema
3. Data transformed and rendered via React Server Components
4. Charts use client component (`ReviewTrendChart.tsx`) with Recharts

**State Management:**
- No client-side state management library
- Server Components fetch fresh data on each request
- `revalidate = 0` disables caching for real-time data

## Key Abstractions

**Agent Pattern:**
- Purpose: Encapsulate data collection responsibility
- Examples: `agents/release_tracker.py`, `agents/rating_monitor.py`, `agents/trend_analyzer.py`
- Pattern: Class with `__init__` for DB connection, domain methods, `run()` or `run_once()` entry point

**BaseScraper:**
- Purpose: Common web scraping functionality
- Examples: `scrapers/base.py`, `scrapers/rotten_tomatoes.py`
- Pattern: Abstract base class with `_get_soup()` helper, concrete implementations override `get_top_reviewers()` and `get_latest_reviews()`

**Database Client:**
- Purpose: PostgreSQL connection management
- Examples: `database.py` (Python), `utils/db.ts` (TypeScript)
- Pattern: Connection pool with automatic `search_path` to `movie_platform` schema

## Entry Points

**Python Agents:**
- Location: `agents/*.py` (each has `if __name__ == "__main__"`)
- Triggers: Manual execution or `start_platform.sh`
- Responsibilities: Data collection and analysis

**Web Application:**
- Location: `web-app/app/page.tsx`
- Triggers: HTTP requests to `/`
- Responsibilities: Render homepage with trending movies, recent releases

**Movie Detail Page:**
- Location: `web-app/app/movies/[id]/page.tsx`
- Triggers: HTTP requests to `/movies/:tmdb_id`
- Responsibilities: Render single movie with reviews, trends, charts

**Platform Startup:**
- Location: `/Users/sundar/Projects/MovieRatings/start_platform.sh`
- Triggers: Manual execution
- Responsibilities: Run data population, start web app, start continuous rating monitor

## Error Handling

**Strategy:** Fail silently with logging, continue processing

**Patterns:**
- Python agents wrap operations in try/except, log errors, continue to next item
- Frontend uses try/catch in data fetching functions, returns empty arrays on failure
- Database operations check for null connection before executing
- Scraping failures logged to `scrape_logs` table with error message

## Cross-Cutting Concerns

**Logging:** Console output via `print()` statements with emoji indicators (no structured logging)

**Validation:** Minimal - relies on database constraints and type checking

**Authentication:** None - no user authentication layer

**Rate Limiting:** Manual `time.sleep()` calls between requests in scraping agents

**Configuration:** Environment variables loaded via `dotenv`, required vars:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `TMDB_API_KEY`

---

*Architecture analysis: 2026-01-27*
