# Codebase Concerns

**Analysis Date:** 2026-01-26

## Tech Debt

**No API Layer - Direct Database Queries in Components:**
- Issue: Frontend components execute raw SQL queries directly. Database schema details leak into presentation layer, making refactoring dangerous and coupling UI to DB structure.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx`, `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx`
- Impact: Cannot change database structure without updating frontend. SQL injection risk if parameterization breaks. Harder to test components. Schema changes require coordinated updates across multiple files.
- Fix approach: Create API route handlers in `app/api/` that expose REST endpoints for data queries. Move all database logic to centralized API layer. Components call `/api/trending-movies` instead of `query()`.

**Missing Caching Strategy:**
- Issue: Both home page (`/`) and detail pages execute fresh queries on every render with `revalidate = 0`. No caching means every page load hits the database, causing unnecessary load.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (line 5), `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (line 6)
- Impact: Database scalability bottleneck. Real-time data not needed for trending movies (24h changes are granular enough). Performance degrades with user growth.
- Fix approach: Use Next.js `revalidate: 3600` (1 hour) for `/` since trends don't change minute-to-minute. Use `revalidate: 1800` for movie detail pages. Add ISR (Incremental Static Regeneration) to rebuild high-traffic pages periodically without cache busting.

**Loose Type Safety with `any` Parameters:**
- Issue: `params?: any[]` in query function and `payload: any` in CustomTooltip allow any values. Runtime errors possible when unexpected data structures passed.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/utils/db.ts` (line 15), `/Users/sundar/Projects/MovieRatings/web-app/components/ReviewTrendChart.tsx` (line 57)
- Impact: Silent failures when data format changes. Tooltip crashes if payload shape unexpected. No IDE hints for query parameter structure.
- Fix approach: Define TypeScript interfaces for each query's parameter structure. Use strict typing: `query<T>(text: string, params: QueryParams): Promise<QueryResult<T>>`. Type the CustomTooltip payload explicitly based on chartData structure.

**Unhandled Error Cases in Data Fetching:**
- Issue: Multiple query functions silently catch errors and return empty arrays/null, masking database failures or connection issues.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (lines 14-26, 30-39, 41-64)
- Impact: Users see blank sections without knowing if data failed to load or genuinely doesn't exist. No monitoring of database errors. Hard to debug issues in production.
- Fix approach: Differentiate between "data not found" (empty array) and "query failed" (throw error or return error object). Use try/catch with specific error logging. Show user-friendly error messages when queries fail. Add observability hooks.

**No Input Validation on Query Parameters:**
- Issue: Movie ID from URL params passed directly to queries without validation. `id: string` accepted as-is in database queries.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (line 66-67)
- Impact: Invalid IDs cause unexpected query behavior. No validation that `id` is a valid integer before passing to database. Could crash if non-numeric value causes type mismatch.
- Fix approach: Validate and sanitize all URL parameters. Parse `id` to number: `const movieId = parseInt(id, 10)`. Throw error or redirect if invalid. Use Zod or similar for schema validation.

**Hardcoded Polling Intervals and Thresholds:**
- Issue: Snapshot analysis uses hardcoded 24-hour windows, 7-day windows, 5σ threshold for anomalies without configuration.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (lines 17, 23)
- Impact: Cannot tune trend sensitivity without code changes. No A/B testing capability. Harder to backtest analysis against different timeframes.
- Fix approach: Move thresholds to environment variables or database configuration table. Allow querying trends with variable time windows. Document why specific intervals were chosen.

## Security Considerations

**Database Credentials in Environment Variables Without Encryption:**
- Risk: DB_PASSWORD stored in plaintext in `.env` and `.env.local` files. Git history contains credentials in recent commits. If `.env.local` accidentally committed, credentials exposed publicly.
- Files: `/Users/sundar/Projects/MovieRatings/.env`, `/Users/sundar/Projects/MovieRatings/web-app/.env.local`
- Current mitigation: Files listed in `.gitignore`, but no rotation policy for compromised credentials.
- Recommendations: Implement credential rotation mechanism. Use PostgreSQL IAM authentication instead of passwords where possible. Audit git history for exposed secrets: `git log -p | grep -i password`. Consider using a secrets manager (AWS Secrets Manager, HashiCorp Vault) in production. Regenerate all exposed credentials immediately.

**SQL Parameterization Correct but Vulnerable to Query Logic Flaws:**
- Risk: While using parameterized queries (`$1`, `$2`), complex queries have multiple joins that could expose unintended data. No row-level security on database queries.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (lines 9, 15-21, 45-59)
- Current mitigation: Parameterized queries prevent SQL injection.
- Recommendations: Implement database views with restricted column selections. Add row-level security policies if multi-tenant features added. Audit which columns are actually needed by each query and return only those.

**External Image URLs (TMDB) Not Validated:**
- Risk: `movie.poster_url` and `movie.backdrop_url` rendered directly in `<img src>` without validation. TMDB image URLs could be exploited if TMDB CDN compromised or URL field poisoned.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (lines 82-86), `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (lines 84-89, 98-101)
- Current mitigation: TMDB is trusted source.
- Recommendations: Validate image URLs start with `https://image.tmdb.org`. Implement Content Security Policy (CSP) header to restrict image sources. Consider proxying images through your own endpoint with caching.

## Performance Bottlenecks

**N+1 Query Pattern in Movie Detail Page:**
- Problem: Movie detail page executes 4 separate database queries sequentially (getMovie, getReviews, getMovieTrend, getRatingSnapshots).
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (lines 68-76)
- Cause: Each async function fetches independently rather than batching. If database latency is 100ms per query, page load is 400ms minimum just for queries.
- Improvement path: Batch queries using Promise.all(), combine related queries using JOINs where possible, or use a data loader pattern to deduplicate identical requests.

**Inefficient Trending Query with Subquery and DISTINCT:**
- Problem: `getTrendingMovies` uses subquery for `rating_24h_ago` which forces database to scan rating_snapshots table multiple times.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (lines 8-27)
- Cause: DISTINCT ON + subquery are computationally expensive. Query processes 7 days of data just to compare 24h changes.
- Improvement path: Use window functions `LAG()` instead of subquery. Precompute trending scores in materialized view. Cache trending results for 1 hour instead of recalculating on each page load.

**No Database Indexes on Common Query Columns:**
- Problem: Queries filter by `movie_id`, `snapshot_time`, `source`, `rating_type` but no confirmation indexes exist.
- Files: All query functions
- Cause: Database may do full table scans instead of index seeks, especially as dataset grows.
- Improvement path: Ensure indexes on: `rating_snapshots(movie_id)`, `rating_snapshots(snapshot_time)`, `rating_snapshots(source)`. Monitor query execution plans. Add composite indexes for common filter combinations.

## Fragile Areas

**Web Scraping Dependency (Not visible in web-app, but in agents):**
- Files: `/Users/sundar/Projects/MovieRatings/agents/` (Python scraping scripts)
- Why fragile: HTML selectors break when TMDB, RT, IMDb update site structure. No monitoring of scraper failures. If scraper fails, no fresh data for analysis.
- Safe modification: Add try/catch with logging around each HTML parse. Return null/empty instead of crashing. Log when selectors fail to find expected elements. Add versioning to scraper code with rollback capability.
- Test coverage: No tests for scraper logic. Scraper failures only discovered when data doesn't appear.

**Trend Analysis Logic with Hardcoded Thresholds:**
- Files: Trend analyzer (not in web-app, but affects data quality): unknown location based on GSD_JOURNEY.md reference
- Why fragile: Classification logic for trending_up/trending_down/sleeper_hit uses magic numbers. If movie popularity distribution changes (e.g., more extreme spikes), thresholds become wrong.
- Safe modification: Document why each threshold was chosen. Add configuration flags for thresholds. Run analysis with multiple threshold sets and compare results before deploying changes.
- Test coverage: Unknown if trend classifications are tested against known scenarios.

**Chart Component Assumes Data Shape:**
- Files: `/Users/sundar/Projects/MovieRatings/web-app/components/ReviewTrendChart.tsx`
- Why fragile: Component assumes `snapshots` array with specific structure. If schema changes (e.g., snapshot_time → timestamp), component crashes silently.
- Safe modification: Add runtime validation that snapshots conform to DailySnapshot interface. Add defensive checks for missing fields with fallbacks. Test with incomplete/malformed data.
- Test coverage: No unit tests for component. Cannot verify behavior with edge cases (empty array, single data point, null values in fields).

**Metadata Object Assumptions in Detail Page:**
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (lines 83-132)
- Why fragile: Code assumes `movie` object has properties like `poster_url`, `backdrop_url`, `regions`, `overview` that may be null/undefined. Conditional checks exist but not consistently.
- Safe modification: Create Movie type interface enforcing required vs optional fields. Use nullish coalescing (`??`) and optional chaining consistently. Add type guards before rendering.
- Test coverage: No tests for different movie data scenarios (missing poster, no regions, partial data).

## Test Coverage Gaps

**No Tests for Database Query Functions:**
- What's not tested: `getTrendingMovies()`, `getRecentMovies()`, `getMovie()`, `getReviews()`, all database interactions
- Files: `/Users/sundar/Projects/MovieRatings/web-app/utils/db.ts`, `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx`, `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx`
- Risk: Query bugs only discovered in production. Schema changes cause silent failures. No regression detection.
- Priority: High - database queries are critical path to application functionality

**No Tests for React Components:**
- What's not tested: ReviewTrendChart rendering, TrendBadge rendering, MovieCard usage, error states
- Files: `/Users/sundar/Projects/MovieRatings/web-app/components/ReviewTrendChart.tsx`, `/Users/sundar/Projects/MovieRatings/web-app/components/TrendBadge.tsx`, `/Users/sundar/Projects/MovieRatings/web-app/components/MovieCard.tsx`
- Risk: UI breaks silently when data changes. Props validation not verified. Visual regressions undetected.
- Priority: Medium - affects user experience but current site is low-traffic

**No End-to-End Tests:**
- What's not tested: Full page load workflow (request data → render → display). User interactions with trends page, movie details page.
- Files: All web-app pages and components
- Risk: Integration issues between components not caught. Broken links, missing data sections, layout shifts.
- Priority: Medium - would catch real-world failures

**No Tests for Error Paths:**
- What's not tested: Database connection failures, missing movies (404 scenario), query timeouts, malformed snapshots
- Files: All data fetching functions
- Risk: Error handling code never executed in testing. Users see unexpected errors. No observability of what went wrong.
- Priority: High - production reliability depends on error handling

## Missing Critical Features / Known Limitations

**No Real-Time Updates Without Page Reload:**
- Problem: Trending data refreshes only on page reload. Users don't see live trend changes.
- Blocks: Real-time dashboard use case. Cannot build real-time alert system.

**No Error Boundary for Component Failures:**
- Problem: If any component crashes, entire page fails. No graceful degradation.
- Blocks: Reliability. Cannot serve partial content if one query fails.

**No Infinite Scroll or Pagination:**
- Problem: Home page loads all trending movies at once (limited to 20, but no pagination).
- Blocks: Scalability. UI becomes slow with hundreds of movies.

**No Search or Filtering:**
- Problem: Users cannot filter movies by genre, source, date range.
- Blocks: Discoverability. Hard to find specific movies in large dataset.

**No User Preferences or Watchlist:**
- Problem: Each user sees same data. Cannot save favorites.
- Blocks: Personalization features. Reduced engagement.

**Incomplete Schema Handling in Frontend:**
- Problem: Detail page tries to render `movie.regions` as array but schema may return different format.
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/movies/[id]/page.tsx` (line 107)
- Blocks: Consistent display of region information across all movies.

---

*Concerns audit: 2026-01-26*
