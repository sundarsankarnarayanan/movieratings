# External Integrations

**Analysis Date:** 2026-01-27

## APIs & External Services

**TMDB (The Movie Database):**
- Purpose: Movie metadata, release dates, posters, ratings
- Client: `tmdb_client.py` (custom REST client)
- Base URL: `https://api.themoviedb.org/3`
- Endpoints used:
  - `/discover/movie` - Movies by release date
  - `/movie/{id}` - Movie details
- Auth: API key via `TMDB_API_KEY` env var
- Rate limiting: Not explicitly handled

**OpenAI:**
- Purpose: AI-powered review summarization
- Client: `openai` Python SDK (`llm_client.py`)
- Model: `gpt-3.5-turbo`
- Auth: API key via `OPENAI_API_KEY` env var
- Features used: Chat completions for review analysis
- Output: Positive/negative summary generation

**Supabase:**
- Purpose: Hosted PostgreSQL database
- Clients:
  - `@supabase/supabase-js` (frontend)
  - `supabase` Python package (backend, though primarily using direct pg)
- Auth:
  - Frontend: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - Backend: `SUPABASE_URL`, `SUPABASE_KEY` (service role)

## Web Scraping Sources

**Rotten Tomatoes:**
- Purpose: Critic reviews, Tomatometer scores, audience scores
- Scraper: `scrapers/rotten_tomatoes.py`, `agents/rating_monitor.py`
- Base URLs:
  - `https://www.rottentomatoes.com` - Movie pages
  - `https://editorial.rottentomatoes.com` - Top critics list
- Data extracted:
  - Tomatometer (critic score)
  - Audience score
  - Review counts
  - Individual critic reviews
- Technique: BeautifulSoup HTML parsing + JSON-LD extraction
- Rate limiting: Manual sleep intervals (1 second between requests)

**IMDb:**
- Purpose: Ratings and vote counts
- Scraper: `agents/rating_monitor.py`
- Base URL: `https://www.imdb.com`
- Data extracted: IMDb rating, vote count
- Status: Configured in `review_sources` table, implementation present

**Metacritic:**
- Purpose: Metascore ratings
- Scraper: `agents/rating_monitor.py`
- Base URL: `https://www.metacritic.com`
- Status: Configured in `review_sources` table, implementation present

## Data Storage

**Primary Database:**
- Type: PostgreSQL (hosted on Supabase)
- Schema: `movie_platform`
- Connection (Python): `psycopg2` via environment variables
- Connection (Next.js): `pg` Pool via environment variables
- Key tables:
  - `movies` - Core movie metadata
  - `reviewers` - Critic profiles
  - `reviews` - Individual reviews
  - `rating_snapshots` - Time-series rating data
  - `daily_review_snapshots` - Daily aggregated snapshots
  - `movie_trends` - Materialized view for trends
  - `data_audit_log` - Change tracking

**Environment Variables for Database:**
```
DB_HOST=127.0.0.1 (default)
DB_PORT=5432 (default)
DB_NAME=postgres (default)
DB_USER=postgres (default)
DB_PASSWORD=postgres (default)
```

**Local Development:**
- SQLite fallback: `movies.db` exists but appears unused
- PostgreSQL required for full functionality

**File Storage:**
- Local filesystem only
- No cloud storage integration

**Caching:**
- PostgreSQL materialized views for trend calculations
- Next.js `revalidate = 0` disables caching (real-time data)

## Authentication & Identity

**Auth Provider:**
- Supabase Auth (configured but usage unclear)
- Frontend uses anon key (public access)
- Backend uses service role key (full access)
- No user authentication implemented in current code

## Monitoring & Observability

**Error Tracking:**
- None (console logging only)

**Logging:**
- Python: `print()` statements
- Database: `scrape_logs` table tracks scraper health
  - Status: success, error, rate_limited
  - Error messages captured
  - Snapshot counts tracked

**Metrics:**
- No external metrics service
- Database stores scrape timestamps and counts

## CI/CD & Deployment

**Hosting:**
- Not configured (local development only)
- Web app suitable for Vercel deployment
- Python agents require persistent hosting

**CI Pipeline:**
- None configured
- No GitHub Actions or similar

**Docker:**
- None configured

## Environment Configuration

**Required Environment Variables:**

Backend (`.env`):
```
# Database (PostgreSQL/Supabase)
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

# Or Supabase connection
SUPABASE_URL=
SUPABASE_KEY=

# External APIs
TMDB_API_KEY=
OPENAI_API_KEY=
```

Frontend (`web-app/.env.local`):
```
# Database direct connection
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=

# Supabase (optional, for client-side)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

**Secrets Location:**
- `.env` files (not committed)
- `.env.example` and `.env.local.example` provide templates

## Webhooks & Callbacks

**Incoming:**
- None configured

**Outgoing:**
- None configured

## MCP (Model Context Protocol)

**Server:**
- Implementation: `mcp_server.py`
- Framework: `FastMCP` from `mcp.server.fastmcp`
- Tools exposed:
  - `list_movies(region, language, title)` - Search movies
  - `get_movie_reviews(tmdb_id)` - Get reviews for movie
  - `get_movie_insights(title)` - Get statistical insights
- Purpose: AI assistant integration for movie data queries

## Data Flow Summary

```
1. TMDB API → movie_release_agent.py → movies table
2. Rotten Tomatoes scrape → rating_monitor.py → rating_snapshots table
3. rating_snapshots → trend_analyzer.py → movie_trends view
4. reviews + OpenAI → summarization_agent.py → movies.ai_summary_* columns
5. PostgreSQL → Next.js (pg client) → Web UI
6. PostgreSQL → MCP server → AI assistants
```

## Integration Health Checks

**Implemented:**
- `scrape_logs` table tracks scraper status
- `test_scraper.py` - Scraper validation
- `test_mcp_server.py` - MCP server tests
- `verify_scrapers.py` - Scraper verification
- `debug_rt.py` - Rotten Tomatoes debugging

**Not Implemented:**
- API health checks
- Database connection pooling monitoring
- Rate limit tracking dashboard

---

*Integration audit: 2026-01-27*
