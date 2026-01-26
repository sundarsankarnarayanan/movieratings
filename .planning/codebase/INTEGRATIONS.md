# External Integrations

**Analysis Date:** 2026-01-26

## APIs & External Services

**Movie Data:**
- The Movie Database (TMDB)
  - What it's used for: Fetches movie metadata, details, images, and discovery
  - SDK/Client: `tmdb_client.py` at `/Users/sundar/Projects/MovieRatings/tmdb_client.py`
  - Auth: Environment variable `TMDB_API_KEY`
  - Endpoints: `/discover/movie`, `/movie/{id}` via https://api.themoviedb.org/3

**Web Scraping:**
- Rotten Tomatoes
  - What it's used for: Scrapes critic reviews, ratings, and reviewer information
  - Library: BeautifulSoup4 + Requests
  - Implementation: `scrapers/rotten_tomatoes.py` at `/Users/sundar/Projects/MovieRatings/scrapers/rotten_tomatoes.py`
  - No API key required; HTTP scraping from https://www.rottentomatoes.com

**Large Language Model:**
- OpenAI API
  - What it's used for: Generates AI summaries of movie reviews (positive/negative aspects)
  - SDK/Client: `openai` Python package, client instantiated in `llm_client.py`
  - Auth: Environment variable `OPENAI_API_KEY`
  - Model: gpt-3.5-turbo
  - Implementation: `/Users/sundar/Projects/MovieRatings/llm_client.py`
  - Function: `summarize_reviews()` processes review text and returns structured summaries

## Data Storage

**Databases:**
- PostgreSQL 12+
  - Purpose: Primary data store for movies, reviews, reviewers, and rating snapshots
  - Connection: Direct psycopg2 connection via environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
  - Schema: `movie_platform` namespace
  - ORM/Client:
    - Python backend: `psycopg2` with `RealDictCursor`
    - Node.js frontend: `pg` driver with parameterized queries
  - Key tables: `movies`, `reviews`, `reviewers`, `rating_snapshots`, `movie_regions`
  - Connection pooling: `Pool` from `pg` package in `/Users/sundar/Projects/MovieRatings/web-app/utils/db.ts`

**Supabase (Optional/Legacy):**
- Supabase PostgreSQL backend
  - Connection: `@supabase/supabase-js` client
  - Auth: `SUPABASE_URL`, `SUPABASE_KEY`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - Status: Environment configured but may be legacy; direct PostgreSQL connection is primary

**File Storage:**
- External image URLs only
  - TMDB image CDN: `https://image.tmdb.org/t/p/original/` and `https://image.tmdb.org/t/p/w500/`
  - Poster/backdrop paths stored in database, fetched from TMDB CDN at runtime

**Caching:**
- None detected in current configuration

## Authentication & Identity

**Auth Provider:**
- Custom/Supabase
  - Implementation: `@supabase/supabase-js` configured in `.env.local`
  - Approach: Supabase JWT tokens (NEXT_PUBLIC_SUPABASE_ANON_KEY for client-side operations)
  - Status: Configured but not actively used in analyzed pages; primarily for potential user management

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Console-based logging in Python backend files (`database.py`, `llm_client.py`, `tmdb_client.py`)
- No structured logging or external logging service configured

## CI/CD & Deployment

**Hosting:**
- Not explicitly configured; inferred as Vercel for Next.js, but could be self-hosted

**CI Pipeline:**
- None detected in codebase

## Environment Configuration

**Required env vars:**

Backend (root `.env`):
- `SUPABASE_URL` - Supabase API endpoint (e.g., http://127.0.0.1:54321)
- `SUPABASE_KEY` - Supabase service role key
- `DB_HOST` - PostgreSQL host (default: 127.0.0.1)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name (default: postgres)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: postgres)
- `TMDB_API_KEY` - The Movie Database API key
- `OPENAI_API_KEY` - OpenAI API key for LLM summarization

Frontend (web-app/.env.local):
- `NEXT_PUBLIC_SUPABASE_URL` - Public Supabase URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Public Supabase anonymous key
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL connection (if frontend queries directly)

**Secrets location:**
- `.env` file (not committed, example at `.env.example`)
- `.env.local` file in web-app (not committed, example at `web-app/.env.local.example`)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Data Flow Summary

1. **Movie Discovery**: TMDB API → Python backend (`tmdb_client.py`) → PostgreSQL (`movies` table)
2. **Review Collection**: Rotten Tomatoes scraper → Python backend (`scrapers/rotten_tomatoes.py`) → PostgreSQL (`reviews`, `reviewers` tables)
3. **AI Summarization**: Review data → OpenAI LLM (`llm_client.py`) → PostgreSQL (`ai_summary_positive`, `ai_summary_negative` columns)
4. **Rating Snapshots**: External rating data → PostgreSQL (`rating_snapshots` table for trend tracking)
5. **Frontend Display**: Next.js app → PostgreSQL (via `pg` driver) → React components render movie/review data

---

*Integration audit: 2026-01-26*
