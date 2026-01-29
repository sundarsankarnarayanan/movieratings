# Codebase Concerns

**Analysis Date:** 2025-01-27

## Tech Debt

**Schema Inconsistency Between Python Backend and Web App:**
- Issue: The Python backend `database.py` uses column names like `poster_path`, `backdrop_path`, while the schema_v2.sql defines `poster_url`, `backdrop_url`. The web app queries expect the `_url` suffix.
- Files: `database.py` (lines 54-55), `web-app/app/page.tsx` (line 11), `web-app/app/movies/[id]/page.tsx`
- Impact: Data inserted by Python agents may not have the URL columns the web app expects, causing missing posters/backdrops.
- Fix approach: Align column names across all layers. Either update `database.py` to construct full URLs and use `_url` columns, or update schema and web app to use raw paths.

**Multiple Schema Files Without Clear Migration Path:**
- Issue: Three separate schema files exist (`setup_schema.sql`, `schema_v2.sql`, `schema_trend_analysis.sql`) plus a migration file, with no clear execution order or migration system.
- Files: `setup_schema.sql`, `schema_v2.sql`, `schema_trend_analysis.sql`, `schema_safe_migration.sql`
- Impact: Database state may differ across environments. Risk of data loss when running schema files that contain `DROP SCHEMA CASCADE`.
- Fix approach: Consolidate into a single current-state schema plus numbered migration files. Consider adopting a migration tool like Alembic (Python) or implement version tracking.

**Duplicate Database Connection Code:**
- Issue: Database connection logic is duplicated across multiple agent files with slight variations.
- Files: `database.py`, `agents/trend_analyzer.py` (line 21), `agents/reviewer_discovery.py` (line 22), `agents/rating_monitor.py` (line 23), `agents/release_tracker.py` (line 24), `agents/web_scraping_tracker.py` (line 24), `apply_sql.py` (line 11)
- Impact: Changes to connection handling must be made in multiple places. Inconsistent error handling across files.
- Fix approach: Create a shared database utility module that all agents import.

**Hardcoded Default Credentials in Python:**
- Issue: Default credentials `postgres/postgres` are hardcoded as fallbacks in connection code.
- Files: `database.py` (lines 14-16), `apply_sql.py` (lines 14-15)
- Impact: Production deployments could accidentally use default credentials if environment variables are missing.
- Fix approach: Fail fast with clear error messages when required environment variables are missing instead of using defaults.

**Unused Supabase Dependencies:**
- Issue: `@supabase/supabase-js` is installed in the web app but the app uses direct PostgreSQL connections via `pg` instead.
- Files: `web-app/package.json` (line 12), `web-app/utils/db.ts`
- Impact: Unnecessary dependency bloat. Confusion about intended database access pattern.
- Fix approach: Remove `@supabase/supabase-js` if direct PostgreSQL is the chosen approach, or migrate to use Supabase client.

**Layout Metadata Not Updated:**
- Issue: The app layout still has default Next.js boilerplate metadata.
- Files: `web-app/app/layout.tsx` (lines 15-18)
- Impact: Poor SEO and browser tab displays "Create Next App" instead of app name.
- Fix approach: Update title to "Movie Ratings Tracker" and add proper description.

## Known Bugs

**Empty `.env.example` Has Duplicate Lines:**
- Symptoms: The example env file has duplicate SUPABASE entries.
- Files: `.env.example` (lines 1-4)
- Trigger: Opening the file shows duplication.
- Workaround: None needed for functionality but confusing for setup.

**Schema Mismatch in Movie Detail Page:**
- Symptoms: Movie detail page may fail to find movies because it queries without schema prefix in some cases.
- Files: `web-app/app/movies/[id]/page.tsx` (line 9 uses `movies` without prefix, line 32 uses `movie_trends`)
- Trigger: The `db.ts` sets search_path on connect, but connection pooling may not guarantee consistent state.
- Workaround: The schema prefix is set on pool connect event.

## Security Considerations

**Exposed Credentials in .env File:**
- Risk: The `.env` file contains an actual Supabase anon key that appears to be a demo/local key.
- Files: `.env` (line 16)
- Current mitigation: This appears to be a local development key based on the `supabase-demo` issuer in the JWT.
- Recommendations: Add `.env` to `.gitignore` (currently listed), ensure no production keys are committed. The key visible has `exp: 2084460382` (year 2066) which is a demo key pattern.

**No Input Validation on Query Parameters:**
- Risk: Movie ID parameter passed directly to SQL query could be vulnerable if not properly sanitized.
- Files: `web-app/app/movies/[id]/page.tsx` (line 9), `database.py` (multiple methods)
- Current mitigation: Parameterized queries are used (`$1`, `%s` placeholders), which prevents SQL injection.
- Recommendations: Current implementation is safe due to parameterized queries. Consider adding TypeScript type validation on the route parameter.

**No Rate Limiting on Web App:**
- Risk: No apparent rate limiting on database queries from the web frontend.
- Files: `web-app/app/page.tsx`, `web-app/app/movies/[id]/page.tsx`
- Current mitigation: None observed.
- Recommendations: Add rate limiting middleware or use Supabase's built-in rate limiting if migrating to Supabase client.

**Scraper User-Agent Spoofing:**
- Risk: Using a Chrome User-Agent string to scrape websites may violate terms of service.
- Files: `scrapers/base.py` (lines 21-23)
- Current mitigation: None.
- Recommendations: Review terms of service for scraped sites. Consider using official APIs where available.

## Performance Bottlenecks

**N+1 Query Pattern on Home Page:**
- Problem: The trending movies query uses a correlated subquery for each row to get 24h-ago rating.
- Files: `web-app/app/page.tsx` (lines 13-20)
- Cause: The subquery `SELECT rating_value FROM ... WHERE rs2.movie_id = m.id` executes per row.
- Improvement path: Use window functions or a self-join to fetch historical ratings in a single pass.

**No Caching Configured:**
- Problem: Every page load hits the database with `revalidate = 0` forcing SSR.
- Files: `web-app/app/page.tsx` (line 5), `web-app/app/movies/[id]/page.tsx` (line 6)
- Cause: Explicit setting to disable caching for real-time data.
- Improvement path: Consider Incremental Static Regeneration (ISR) with short revalidation periods (e.g., 60 seconds) for trending data. Movie detail pages could have longer cache times.

**Database Pool Configuration Missing:**
- Problem: PostgreSQL pool uses default configuration without explicit connection limits.
- Files: `web-app/utils/db.ts` (lines 3-9)
- Cause: Pool constructor called with only connection parameters.
- Improvement path: Add pool configuration: `max` connections, `idleTimeoutMillis`, `connectionTimeoutMillis`.

## Fragile Areas

**Web Scraper Selectors:**
- Files: `scrapers/rotten_tomatoes.py` (lines 16, 45-50, 71-74)
- Why fragile: CSS selectors like `tr[data-qa="critic-review-row"]` and `a[href*="/critic/"]` will break when Rotten Tomatoes updates their HTML structure.
- Safe modification: Add multiple fallback selectors. The current code does have some fallback logic (lines 48-68) but it's still HTML-dependent.
- Test coverage: `test_scraper.py` exists but uses mocked HTML, won't catch real site changes.

**Movie Title Matching for Reviews:**
- Files: `database.py` (lines 111-127), `web-app/app/movies/[id]/page.tsx` (lines 13-27)
- Why fragile: Reviews are linked to movies by title string matching rather than foreign key.
- Safe modification: Add `tmdb_id` foreign key to reviews table for reliable linking.
- Test coverage: No tests for edge cases like title variations, special characters, or duplicate titles.

## Scaling Limits

**Database Connection Pooling:**
- Current capacity: Default `pg` pool settings (likely 10 connections).
- Limit: Will exhaust connections under moderate concurrent load.
- Scaling path: Configure explicit pool limits and consider PgBouncer for production.

**Scraper Rate Limits:**
- Current capacity: `rate_limit_per_minute: 10` defined in schema but not enforced in code.
- Limit: Could get IP blocked by scraped sites.
- Scaling path: Implement the rate limiting defined in `review_sources` table. Consider using a queue system for scrape jobs.

## Dependencies at Risk

**Next.js 16.x:**
- Risk: Using very recent Next.js version (16.1.4) which may have undiscovered bugs.
- Impact: Potential breaking changes or instability.
- Migration plan: Monitor for patches. Consider using LTS version for production.

**React 19.x:**
- Risk: React 19 is recent; some ecosystem packages may not be fully compatible.
- Impact: Third-party component libraries may have issues.
- Migration plan: Recharts 3.7.0 is being used which should support React 19.

## Missing Critical Features

**Error Boundary/Error UI:**
- Problem: No error boundary components in the React tree.
- Blocks: Users see cryptic errors when components fail instead of graceful degradation.

**Loading States:**
- Problem: No loading skeletons or suspense boundaries in the UI.
- Blocks: Users see blank pages during data fetching.

**Authentication/Authorization:**
- Problem: No user authentication system.
- Blocks: Cannot personalize experience, track user preferences, or restrict access.

**Health Check Endpoint:**
- Problem: No health check endpoint for monitoring.
- Blocks: Cannot use standard container orchestration health checks.

## Test Coverage Gaps

**No Tests for Web App:**
- What's not tested: All React components and Next.js pages have zero test coverage.
- Files: `web-app/components/MovieCard.tsx`, `web-app/components/ReviewTrendChart.tsx`, `web-app/components/TrendBadge.tsx`, `web-app/app/page.tsx`, `web-app/app/movies/[id]/page.tsx`
- Risk: UI regressions will go unnoticed. Component props type issues won't be caught.
- Priority: High - these are user-facing components.

**No Integration Tests:**
- What's not tested: End-to-end flow from scraping to display.
- Files: All agent files in `agents/` directory
- Risk: Individual unit tests pass but system doesn't work together.
- Priority: Medium - manual testing catches most issues currently.

**No Database Tests:**
- What's not tested: Schema migrations, constraint behavior, materialized view refresh.
- Files: All `.sql` files
- Risk: Schema changes may break in unexpected ways.
- Priority: Medium.

**TypeScript `any` Usage:**
- What's not tested: Type safety is bypassed with `any` types.
- Files: `web-app/app/movies/[id]/page.tsx` (lines 196, 218), `web-app/utils/db.ts` (line 15), `web-app/components/ReviewTrendChart.tsx` (line 57)
- Risk: Runtime type errors that TypeScript should catch.
- Priority: Medium - define proper interfaces for database results and component props.

---

*Concerns audit: 2025-01-27*
