# Architecture

**Analysis Date:** 2026-01-26

## Pattern Overview

**Overall:** Multi-tier event-driven system with time-series data collection

**Key Characteristics:**
- Separation between backend agents (Python-based data collection) and frontend presentation (Next.js React)
- Time-series snapshot model for tracking rating changes over time
- Periodic agent-driven data collection and analysis pipeline
- Real-time UI queries against PostgreSQL with server-side rendering

## Layers

**Presentation Layer:**
- Purpose: Display movie trends, ratings, and review history to users
- Location: `web-app/app/`, `web-app/components/`
- Contains: Next.js page components, React UI components, client-side charts
- Depends on: Database queries (via `@/utils/db`)
- Used by: Web browser clients accessing `/` (home), `/movie/[id]` (detail), `/movies/[id]` (alt detail)

**Data Access Layer:**
- Purpose: Execute SQL queries against PostgreSQL database
- Location: `web-app/utils/db.ts`, `database.py`
- Contains: Connection pooling, query execution, transaction management
- Depends on: PostgreSQL connection strings and credentials
- Used by: Page components in presentation layer, agents in collection layer

**Collection & Monitoring Layer:**
- Purpose: Periodically collect rating data and analyze trends
- Location: `agents/` (Python agents)
- Contains: `rating_monitor.py`, `trend_analyzer.py`, `release_tracker.py`, `reviewer_discovery.py`
- Depends on: PostgreSQL database, web scraping (requests/BeautifulSoup), external TMDB API
- Used by: Orchestration scripts that invoke agents periodically

**Scraping Layer:**
- Purpose: Extract data from external review platforms
- Location: `scrapers/` (Python scrapers with base class)
- Contains: Site-specific parsers for Rotten Tomatoes, abstractable to other platforms
- Depends on: HTTP requests, HTML parsing libraries
- Used by: Collection layer agents

**Schema & Storage:**
- Purpose: Persist all system state and historical data
- Location: Database schema defined in `setup_schema.sql` and `schema_v2.sql`
- Contains: Movies, reviewers, rating_snapshots (time-series), daily_review_snapshots, review_sources, scrape_logs, materialized views
- Depends on: PostgreSQL 13+
- Used by: All layers read/write through this

## Data Flow

**Movie Rating Collection Flow:**

1. Periodic trigger (cron job or manual invocation) launches `agents/rating_monitor.py`
2. `RatingMonitor.get_active_movies()` queries database for movies released in last N days
3. For each movie, `RatingMonitor.scrape_rt_rating()` makes HTTP request to Rotten Tomatoes
4. BeautifulSoup parses HTML response, extracts critic/audience scores
5. `RatingMonitor.insert_snapshot()` writes `rating_snapshots` record with timestamp, source, rating_value, review_count
6. `TrendAnalyzer` periodically aggregates snapshots into `daily_review_snapshots` table
7. Web UI queries latest snapshots and displays trending movies on `/` homepage

**Movie Detail Page Flow:**

1. User visits `/movie/[id]` where `[id]` is TMDB ID
2. Server-side `getMovie()` executes parameterized query against `movies` table
3. Server-side `getRatingHistory()` fetches all `rating_snapshots` for that movie
4. `formatChartData()` groups snapshots by timestamp and source/rating_type
5. Server-side `getDailySnapshots()` retrieves aggregated `daily_review_snapshots`
6. React component `ReviewTrendChart` renders line chart with two Y-axes (reviews, score)
7. `latestRatings` object computed from snapshots, displayed as cards

**State Management:**

- State is persisted in PostgreSQL database, not in-memory
- No client-side state management framework (Redux/Zustand)
- Each page request queries fresh data (revalidate = 0 on all pages)
- `TrendBadge` component receives computed status from backend (e.g., 'trending_up', 'sleeper_hit')

## Key Abstractions

**RatingSnapshot:**
- Purpose: Record a single measurement of a movie's rating at a point in time
- Examples: `rating_snapshots` table in schema
- Pattern: Time-series pattern - immutable records append-only, indexed by (movie_id, source, rating_type, snapshot_time)
- Fields: movie_id, source ('RottenTomatoes', 'Metacritic', 'IMDb'), rating_type ('tomatometer', 'audience'), rating_value, review_count, snapshot_time, metadata (JSONB)

**Movie:**
- Purpose: Core entity representing a film with metadata
- Examples: `movies` table in schema, `Movie` type used in page queries
- Pattern: Entity pattern with UUID primary key, TMDB ID as external identifier
- Contains: title, release_date, genres, overview, poster_url, backdrop_url, ai_summary fields

**DailyReviewSnapshot:**
- Purpose: Pre-aggregated daily metrics for trend analysis
- Examples: `daily_review_snapshots` table in schema_v2.sql
- Pattern: Materialized aggregation pattern - computed nightly from `rating_snapshots`, supports fast trend queries
- Fields: movie_id, snapshot_date, total_reviews, new_reviews_today, critic_score, audience_score, review_velocity, score_change

**MovieTrend:**
- Purpose: Computed trend classification and anomaly detection
- Examples: `movie_trends` materialized view, `TrendBadge` component
- Pattern: Derived data pattern - computed from historical snapshots, cached in `movie_trends` view
- Statuses: 'trending_up', 'trending_down', 'sleeper_hit', 'stable'

## Entry Points

**Web Application Entry:**
- Location: `web-app/app/layout.tsx`
- Triggers: HTTP request to Next.js server
- Responsibilities: Root layout, font loading, metadata

**Homepage:**
- Location: `web-app/app/page.tsx`
- Triggers: GET `/`
- Responsibilities: Execute `getTrendingMovies()` and `getRecentMovies()` queries, render trending movies grid (24h movers) and latest releases grid

**Movie Detail Page (Primary):**
- Location: `web-app/app/movie/[id]/page.tsx`
- Triggers: GET `/movie/[id]` where id = TMDB ID
- Responsibilities: Fetch movie metadata, rating history, daily snapshots, compute latest ratings by source, render hero section with poster/backdrop, display current ratings cards, render trend chart, show rating history table

**Movie Detail Page (Secondary):**
- Location: `web-app/app/movies/[id]/page.tsx`
- Triggers: GET `/movies/[id]`
- Responsibilities: Similar to primary but fetches reviews from separate table, displays AI summaries, shows regional reviews

**Rating Monitor Agent:**
- Location: `agents/rating_monitor.py` > `RatingMonitor.run()`
- Triggers: Scheduled execution (cron/orchestration script)
- Responsibilities: Poll active movies, scrape current ratings from Rotten Tomatoes, insert snapshots

**Trend Analyzer Agent:**
- Location: `agents/trend_analyzer.py` > `TrendAnalyzer.run()`
- Triggers: Scheduled execution (cron/orchestration script)
- Responsibilities: Aggregate daily snapshots, detect anomalies, classify trends (trending_up/down), compute growth rates

## Error Handling

**Strategy:** Fail-safe with logging

**Patterns:**
- Database connection failures: Graceful degradation, return empty results or "not found" page
- Scraper errors: Log to `scrape_logs` table with status/error_message, continue with next movie
- Missing movie data: 404-like response ("Movie not found" message on detail pages)
- Timeout handling: BeautifulSoup parsing wraps requests in try/except, retries with backoff

## Cross-Cutting Concerns

**Logging:**
- Backend agents log to `scrape_logs` table with source_name, status ('success'/'error'), error_message
- Web UI has no explicit logging; errors render as empty UI sections (e.g., "No trend data available yet")

**Validation:**
- Database schema enforces NOT NULL constraints, UNIQUE constraints on external IDs (tmdb_id, profile_url)
- Frontend TypeScript interfaces (e.g., `DailySnapshot`, `TrendBadgeProps`) provide compile-time type safety

**Authentication:**
- Not implemented - no user authentication, all endpoints are public read-only
- Database credentials passed via environment variables (DB_HOST, DB_USER, DB_PASSWORD)

---

*Architecture analysis: 2026-01-26*
