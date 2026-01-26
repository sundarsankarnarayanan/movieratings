# External Integrations

**Analysis Date:** 2026-01-26

## APIs & External Services

**TMDB (The Movie Database):**
- Service: Movie metadata and image CDN
- What it's used for: Movie data (posters, backdrops, vote_average, vote_count)
- Image URLs: `https://image.tmdb.org/t/p/w500/` prefix used in `components/MovieCard.tsx`
- SDK/Client: Referenced in database schema but not directly called from frontend
- Data accessed: Movie IDs, titles, release dates, poster URLs, backdrop URLs, vote data

---

## Data Storage

**Databases:**

**PostgreSQL (Primary):**
- Connection type: Direct via `pg` driver
- Connection string: Environment-based (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
- Default dev config: `127.0.0.1:54322` (localhost Supabase Postgres)
- Client: `pg` (node-postgres) v8.17.2
- Schema: `movie_platform` (auto-set on connection in `utils/db.ts`)

**Schema/Tables referenced in code:**
- `movies` - Movie metadata (id, tmdb_id, title, release_date, poster_url, backdrop_url, vote_average, vote_count, language, popularity, overview, regions, ai_summary_positive, ai_summary_negative)
- `rating_snapshots` - Time-series rating data (movie_id, rating_value, source, snapshot_time, rating_type='tomatometer')
- `daily_review_snapshots` - Aggregated daily review data (movie_id, snapshot_time, snapshot_date, total_reviews, critic_score, audience_score, new_reviews_today, review_velocity, score_change)
- `movie_trends` - Trend analysis (movie_id, trend_status, trend_confidence, spike_date, review_growth_rate, avg_daily_reviews)
- `reviews` - Review content (movie_title, review_date)
- `reviewers` - Review source metadata (name, source)

**File Storage:** Not detected - images served from TMDB CDN

**Caching:** None detected

---

## Authentication & Identity

**Auth Provider:** Not detected in current active code

**SDK Imported But Unused:**
- `@supabase/supabase-js` v2.91.0 - Installed but not imported or used in any application code
- Environment variables defined: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Status: Prepared but not implemented

---

## Monitoring & Observability

**Error Tracking:** None detected

**Logs:**
- Console-based logging only (no explicit logging framework imported)
- Error handling: Try-catch blocks with silent failures in `app/movies/[id]/page.tsx` for tables that may not exist

---

## CI/CD & Deployment

**Hosting:** Not configured in project

**CI Pipeline:** None detected

**Deployment:** Not configured - uses default Next.js configuration

---

## Environment Configuration

**Required env vars (development):**
- `DB_HOST` - PostgreSQL hostname (default: 127.0.0.1)
- `DB_PORT` - PostgreSQL port (default: 54322)
- `DB_NAME` - Database name (default: postgres)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: postgres)

**Optional env vars (prepared but unused):**
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase public key

**Secrets location:**
- Development: `.env.local` (git-ignored)
- Example template: `.env.local.example`

---

## Webhooks & Callbacks

**Incoming:** None detected

**Outgoing:** None detected

---

## Data Flow

**Request Path:**
1. Client requests page via Next.js router
2. Server-side component calls database via `utils/db.ts` query function
3. PostgreSQL returns row data
4. Component formats and renders data with Recharts (client-side) or Lucide icons
5. Images loaded from TMDB CDN

**Database Queries:**
- Home page: Trending movies (last 7 days rating changes) + Recent releases
- Movie detail: Movie metadata, reviews, trends, rating snapshots (time-series)
- All queries use parameterized queries via `pg` driver (SQL injection protected)

---

## Deployment Considerations

**Environment Setup Required:**
- PostgreSQL database with `movie_platform` schema and required tables
- Environment variables must be set for database connectivity
- TMDB API data must be populated in database (no direct TMDB API calls from frontend)

**Known Gaps:**
- Supabase SDK installed but not integrated
- No authentication/authorization system in place
- No API routes exposed (all data accessed via direct database connection from server components)

---

*Integration audit: 2026-01-26*
