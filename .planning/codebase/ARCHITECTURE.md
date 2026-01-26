# Architecture

**Analysis Date:** 2026-01-26

## Pattern Overview

**Overall:** Full-stack monorepo with separated concerns - Next.js frontend for real-time visualization, PostgreSQL backend with Python agents for data collection and analysis.

**Key Characteristics:**
- Server-side rendering with async data fetching (Next.js App Router)
- Multi-agent Python backend for autonomous data collection and trend analysis
- Time-series data storage with snapshot-based tracking
- Real-time rating and review monitoring from external sources

## Layers

**Presentation Layer (Next.js):**
- Purpose: User-facing web application for movie trend visualization and analytics
- Location: `/web-app/app/`, `/web-app/components/`
- Contains: Page components (RSC), UI components (client/server), Tailwind styling
- Depends on: PostgreSQL database via `utils/db.ts`, external image CDNs (TMDB)
- Used by: End users via browser

**Server Utilities Layer:**
- Purpose: Database connection pooling and query abstraction
- Location: `/web-app/utils/db.ts`
- Contains: PostgreSQL Pool configuration, query execution wrapper
- Depends on: `pg` npm package, environment variables
- Used by: All page components needing data

**Agent/Backend Layer (Python):**
- Purpose: Autonomous data collection, analysis, and database population
- Location: `/agents/`, root-level `.py` files
- Contains: Agent orchestration, scraping, trend analysis, LLM-based summarization
- Depends on: PostgreSQL, external APIs (TMDB, review platforms), LLM services
- Used by: Scheduled jobs, manual pipeline execution

**Data Storage Layer:**
- Purpose: Persistent storage of movies, ratings, reviews, trends
- Schema: `movie_platform` PostgreSQL schema with tables: movies, rating_snapshots, reviews, reviewers, movie_trends, daily_review_snapshots
- Accessed by: Next.js pages and Python agents via direct SQL queries

## Data Flow

**Movie Discovery & Initial Population:**

1. Release Tracker Agent (`/agents/release_tracker.py`) monitors TMDB API for new movie releases
2. Fetches movie metadata (title, poster, backdrop, ratings, overview) and stores in `movies` table
3. Web app queries `movies` table and renders Latest Releases section

**Rating Monitoring Pipeline:**

1. Rating Monitor Agent (`/agents/rating_monitor.py`) runs periodically
2. Queries external review platforms (Rotten Tomatoes, TMDB, etc.)
3. Creates `rating_snapshots` entries with timestamp, rating value, source
4. Web app renders Biggest Movers section by calculating `rating_change = current_rating - rating_24h_ago`

**Trend Analysis Pipeline:**

1. Trend Analyzer Agent (`/agents/trend_analyzer.py`) processes historical snapshots
2. Computes `movie_trends` table with: trend_status, trend_confidence, review_growth_rate, spike_date, etc.
3. Web app displays TrendBadge component with trend status and confidence on movie detail page

**Daily Review Snapshots:**

1. Rating data aggregated into daily summaries stored in `daily_review_snapshots`
2. Contains: snapshot_date, total_reviews, critic_score, audience_score, review_velocity, score_change
3. Web app displays ReviewTrendChart using this time-series data

**State Management:**

- No client-side state management (all data fetched server-side)
- Database serves as single source of truth
- Web app with `revalidate = 0` (no caching) ensures real-time data

## Key Abstractions

**Query Abstraction:**
- Purpose: Centralize database access with parameterized queries
- Examples: `utils/db.ts`
- Pattern: Direct SQL execution via pg Pool, scoped to `movie_platform` schema

**Component Hierarchy:**
- Purpose: Reusable UI elements for consistency
- Examples: `components/MovieCard.tsx`, `components/TrendBadge.tsx`, `components/ReviewTrendChart.tsx`
- Pattern: Typed React components with Tailwind CSS, mix of client and server components

**Agent Pattern:**
- Purpose: Autonomous, scheduled data collection and analysis
- Examples: `agents/rating_monitor.py`, `agents/trend_analyzer.py`, `agents/release_tracker.py`
- Pattern: Standalone Python scripts with LLM integration via `llm_client.py`, database access via `database.py`

## Entry Points

**Web Application Root:**
- Location: `/web-app/app/layout.tsx`
- Triggers: Browser request to web-app domain
- Responsibilities: Root layout, metadata, global font configuration

**Home Page:**
- Location: `/web-app/app/page.tsx`
- Triggers: GET /
- Responsibilities: Fetch trending movies and recent releases, render hero + two grid sections

**Movie Detail Page:**
- Location: `/web-app/app/movies/[id]/page.tsx`
- Triggers: GET /movies/[tmdb_id]
- Responsibilities: Fetch movie metadata, reviews, trend data, snapshots; render detail view with charts

**Data Pipeline Entrypoints:**
- `main.py`: Manual orchestration of agent execution
- `mcp_server.py`: MCP server for Claude integration
- `run_pipeline.sh`: Shell script to execute full data collection pipeline

## Error Handling

**Strategy:** Graceful degradation with try-catch blocks at critical points

**Patterns:**
- Database query failures in page components return empty arrays or placeholder UI (e.g., "No reviews collected yet" in movie detail)
- Agent errors logged but don't halt pipeline (e.g., `getReviews()` catches exception and returns `[]`)
- Failed external API calls handled by agent with fallback behavior
- Try-catch in `getRatingSnapshots()`, `getMovieTrend()`, `getReviews()` gracefully handle missing database tables

## Cross-Cutting Concerns

**Logging:**
- Python: Console output in agents, database.py log queries
- Next.js: Server-side console logs via Next.js CLI

**Validation:**
- Database constraints via PostgreSQL schema
- Component props typed via TypeScript interfaces
- Environment variables required at startup (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

**Authentication:**
- No user authentication system; single-tenant application
- Database access secured via environment variables
- External APIs (TMDB, Supabase) accessed via API keys in environment

---

*Architecture analysis: 2026-01-26*
