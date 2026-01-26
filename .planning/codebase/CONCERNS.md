# Codebase Concerns

**Analysis Date:** 2026-01-26

## Tech Debt

**Secrets in Environment Configuration:**
- Issue: `.env` file contains hardcoded service role key (NEXT_PUBLIC_SUPABASE_ANON_KEY) that appears to be a demo/test key
- Files: `/Users/sundar/Projects/MovieRatings/.env`
- Impact: Exposes authentication tokens in repository. Public keys can be intercepted; service role should never be exposed to client code.
- Fix approach: Remove all hardcoded keys from `.env`, use environment-specific secrets management. Make `.env` a template (`.env.example`) with placeholders. Use secret management service (AWS Secrets Manager, Vault, etc.) for production deployments.

**Web Scraping Brittleness:**
- Issue: Rotten Tomatoes scraper uses hardcoded CSS selectors (`tr[data-qa="critic-review-row"]`, `span.icon--fresh/rotten`) which are fragile to DOM changes
- Files: `/Users/sundar/Projects/MovieRatings/scrapers/rotten_tomatoes.py` (lines 16, 45, 72)
- Impact: Any website redesign breaks scraper. Current code has fallbacks but they're heuristic-based and unreliable (lines 48-68).
- Fix approach: Switch to official TMDB data where possible. For other sources, implement selector versioning and automated testing. Add monitoring to detect when selectors break (unexpected null results).

**Inconsistent Error Handling:**
- Issue: Database connections return None on failure but code doesn't always check. Web routes have no error boundary or try-catch blocks.
- Files: `/Users/sundar/Projects/MovieRatings/database.py` (lines 21-23, 26, 42, 51, 68, 82, 89, 95, 112), `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (no error handling), `/Users/sundar/Projects/MovieRatings/web-app/app/movie/[id]/page.tsx` (basic null check only, line 75)
- Impact: Database connection failure silently fails, returns empty arrays treated as "no data". Network errors in page generation cause unhandled crashes.
- Fix approach: Implement consistent error handling: return Result<T, Error> types. Add error boundaries in Next.js pages. Log all database failures. Provide user-facing error messages.

**Missing Input Validation:**
- Issue: Python database methods accept user parameters without validation (e.g., `upsert_movie`, `insert_review`)
- Files: `/Users/sundar/Projects/MovieRatings/database.py` (lines 25-65, 41-48, 50-65)
- Impact: Could accept malformed data (null values in required fields, SQL injection if raw queries were used)
- Fix approach: Add Pydantic models or dataclasses to validate inputs before database operations. Add schema constraints in PostgreSQL (NOT NULL, CHECK constraints).

**Weak API Key Management:**
- Issue: TMDB and OpenAI API keys loaded from environment but no validation that they exist or are valid
- Files: `/Users/sundar/Projects/MovieRatings/llm_client.py` (line 9), `/Users/sundar/Projects/MovieRatings/tmdb_client.py` (line 9)
- Impact: Silent failures - APIs return errors that are logged but execution continues with empty results
- Fix approach: Validate API keys on service initialization. Fail fast with clear error messages. Implement API key rotation detection.

---

## Known Bugs

**Database Connection Not Closed:**
- Symptoms: PostgreSQL connections may leak, exceeding max connections over time
- Files: `/Users/sundar/Projects/MovieRatings/database.py` (lines 10-23, 88-92)
- Trigger: Multiple requests through the application; Pool in `web-app/utils/db.ts` does not show explicit close handlers
- Workaround: Restart database service to reset connections
- Fix: Implement connection pool management with proper cleanup. Use context managers or connection pool lifecycle management.

**Review Date Parsing Inconsistency:**
- Symptoms: Reviews with NULL review_date stored in database but UI doesn't handle missing dates well
- Files: `/Users/sundar/Projects/MovieRatings/scrapers/rotten_tomatoes.py` (line 66), `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (lines 138-140)
- Trigger: Critics without review dates in Rotten Tomatoes profiles
- Fix: Standardize date handling - use Unix timestamps or require valid dates. Add data validation at insert.

**Chart Data Type Mismatch:**
- Symptoms: `CustomTooltip` in ReviewTrendChart uses `any` type, could fail with unexpected data structure
- Files: `/Users/sundar/Projects/MovieRatings/web-app/components/ReviewTrendChart.tsx` (line 44)
- Trigger: Malformed snapshot data from database
- Fix: Implement strict TypeScript types for snapshot payloads. Use zod or similar for runtime validation.

---

## Security Considerations

**Web Scraping Without Rate Limiting:**
- Risk: Scraper makes unlimited requests to external websites, could trigger IP blocks or legal issues
- Files: `/Users/sundar/Projects/MovieRatings/scrapers/base.py` (lines 20-26), `/Users/sundar/Projects/MovieRatings/scrapers/rotten_tomatoes.py` (lines 9, 39)
- Current mitigation: User-Agent header present but no backoff, retry logic, or request throttling
- Recommendations: Add `time.sleep()` between requests, implement exponential backoff, respect robots.txt, consider using API partnerships instead

**SQL Injection (Low Risk but Preventable):**
- Risk: While current code uses parameterized queries (good), dynamic query building in `list_movies` (line 97-108) could be exploited
- Files: `/Users/sundar/Projects/MovieRatings/database.py` (lines 94-109)
- Current mitigation: Uses `%s` parameter placeholders with `psycopg2.extras`
- Recommendations: Migrate to ORM (SQLAlchemy) to eliminate manual SQL. Add SQL query linting to CI/CD.

**CORS/CSRF Not Enforced:**
- Risk: Web app makes database queries from browser; no CORS headers or CSRF tokens visible
- Files: `/Users/sundar/Projects/MovieRatings/web-app/utils/db.ts` (direct database access)
- Current mitigation: Database is local (127.0.0.1) in development
- Recommendations: Implement API middleware layer (Next.js API routes) instead of direct database access from client. Add CORS validation. Implement CSRF tokens if forms are added.

**Credentials in Version Control:**
- Risk: `.env` file committed with test credentials
- Files: `/Users/sundar/Projects/MovieRatings/.env`
- Current mitigation: Only demo/test keys, not production credentials
- Recommendations: Add `.env` to `.gitignore` immediately. Audit git history for any real credentials. Use `.env.example` with placeholders.

---

## Performance Bottlenecks

**Unoptimized Movie List Queries:**
- Problem: `list_movies` in database.py returns ALL matching records; no pagination
- Files: `/Users/sundar/Projects/MovieRatings/database.py` (lines 94-109)
- Cause: No LIMIT or OFFSET in query; could return thousands of rows
- Improvement path: Add pagination parameters (limit, offset). Index on region, language, title for faster filtering.

**Large Chart Re-renders:**
- Problem: `ReviewTrendChart` re-renders all data on every prop change; no memoization
- Files: `/Users/sundar/Projects/MovieRatings/web-app/components/ReviewTrendChart.tsx` (line 21)
- Cause: No `React.memo()` wrapper; `formatChartData` runs on every render
- Improvement path: Wrap component with `React.memo()`, memoize `formatChartData` with `useMemo()`, lazy load chart library

**Full Page Revalidation:**
- Problem: Both `page.tsx` files set `revalidate = 0` (no caching)
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (line 5), `/Users/sundar/Projects/MovieRatings/web-app/app/movie/[id]/page.tsx` (line 6)
- Cause: Database queries run on every page load (getTrendingMovies, getRatingHistory, etc.)
- Impact: With 100 concurrent users, 100 database queries hit simultaneously
- Improvement path: Implement ISR (Incremental Static Regeneration) with `revalidate = 60`. Use Redis caching layer for hot queries. Implement database query timeouts.

**No Connection Pooling Limits:**
- Problem: `web-app/utils/db.ts` creates pool but doesn't show max connection configuration
- Files: `/Users/sundar/Projects/MovieRatings/web-app/utils/db.ts` (lines 3-9)
- Cause: Default pool size may be too small (default: 10). No connection timeout configured.
- Improvement path: Set `max: 20`, `idleTimeoutMillis: 30000`, `connectionTimeoutMillis: 2000`

**Materialized View Not Refreshing:**
- Problem: `movie_trends` materialized view requires manual refresh via `refresh_movie_trends()` function
- Files: `/Users/sundar/Projects/MovieRatings/schema_v2.sql` (lines 92-117)
- Cause: No automatic refresh trigger; view becomes stale between manual refreshes
- Improvement path: Create trigger on `rating_snapshots` INSERT/UPDATE to auto-refresh, or use regular view instead

---

## Fragile Areas

**Rotten Tomatoes Scraper:**
- Files: `/Users/sundar/Projects/MovieRatings/scrapers/rotten_tomatoes.py`
- Why fragile: Depends on 3 hardcoded CSS selectors that break on any DOM update. Fallback logic uses heuristics (detecting "fresh"/"rotten" in parent HTML) which is unreliable.
- Safe modification: Add automated tests that scrape a snapshot page and verify selectors still work. Monitor selector failures and alert. Consider migrating to TMDB API only.
- Test coverage: No test file exists for scrapers. Zero test coverage.

**LLM Summary Generation:**
- Files: `/Users/sundar/Projects/MovieRatings/llm_client.py` (lines 16-59)
- Why fragile: Parses unstructured text responses using string matching ("POSITIVES:" and "NEGATIVES:" literals). If OpenAI changes response format or API fails, returns generic fallback strings that obscure the error.
- Safe modification: Implement structured output with JSON parsing. Add retry logic with exponential backoff. Log all LLM requests/responses for debugging.
- Test coverage: Zero. No tests for prompt variations or error cases.

**Database Query in Server Component:**
- Files: `/Users/sundar/Projects/MovieRatings/web-app/app/page.tsx` (lines 7-42), `/Users/sundar/Projects/MovieRatings/web-app/app/movie/[id]/page.tsx` (lines 8-56)
- Why fragile: Direct database queries in async server components with no error handling. Column names must match exactly (if schema changes, queries silently fail and return undefined).
- Safe modification: Create data layer functions with schema validation. Add tests that verify returned types. Implement error boundaries.
- Test coverage: Zero. No test files for page components.

---

## Scaling Limits

**Database Connection Pool:**
- Current capacity: Default pool size (likely 10) across all Next.js routes
- Limit: With 100 concurrent users, connections will be exhausted, subsequent requests queue indefinitely
- Scaling path: Increase pool size to 30-50, add read-only replicas for SELECT queries, implement query caching

**Single Database Instance:**
- Current capacity: Single PostgreSQL instance (localhost:54322)
- Limit: No replication, no failover. Single point of failure.
- Scaling path: Set up primary-replica with streaming replication, implement failover with Patroni or similar

**Materialized View Refresh:**
- Current capacity: Manual refresh only, one view (movie_trends)
- Limit: View becomes stale between refreshes; with many movies, REFRESH takes seconds (blocking writes)
- Scaling path: Use CONCURRENT refresh option (requires UNIQUE index), or switch to regular view with indexed base tables

**Web Scraping Concurrency:**
- Current capacity: Sequential scraping (no parallelization visible in agents)
- Limit: `movie_release_agent.py` iterates regions sequentially; scraping 1 region takes ~30s, total 6+ minutes for 12 regions
- Scaling path: Use thread pool or async/await, implement circuit breakers for rate-limited endpoints

**Large Dataset Pagination:**
- Current capacity: No pagination in any query
- Limit: Queries return all matching rows; first load of "all movies" could be 10,000+ records
- Scaling path: Implement cursor-based pagination, cache hot datasets in Redis, use lazy loading in UI

---

## Dependencies at Risk

**Deprecated Web Scraping Approach:**
- Risk: Web scraping is fragile and legally risky. Websites update layouts without notice.
- Impact: Entire review data pipeline breaks when Rotten Tomatoes/Metacritic redesigns
- Migration plan: Migrate to official TMDB API entirely (already used for movie metadata). Partner with Rotten Tomatoes for official data access. Use aggregator APIs (Omdb, etc.) if available.

**BeautifulSoup/Requests Stack:**
- Risk: BeautifulSoup is synchronous, blocking. No async support. Requests library doesn't have built-in retry logic.
- Impact: Scraper can't handle timeouts gracefully; gets stuck on slow pages
- Migration plan: Switch to `httpx` with async/await, implement `httpx.AsyncClient` with timeout and retry config. Use `Playwright` for JavaScript-heavy sites if needed.

**Hardcoded Chart Library (Recharts):**
- Risk: Recharts is large (bundle impact) and not responsive to some data shapes
- Impact: If charting needs change significantly, requires rewrite
- Migration plan: Consider lightweight alternative like `Chart.js` or `D3.js` for complex needs. Evaluate business requirements first.

---

## Missing Critical Features

**No Data Validation Framework:**
- Problem: No schema validation on API inputs or database responses
- Blocks: Can't safely add new fields to database without risking silent failures
- Priority: High - Should implement before scaling beyond demo

**No Error Logging/Monitoring:**
- Problem: All errors print to console/stdout with no centralized logging
- Blocks: Can't debug production issues or detect patterns
- Priority: High - Critical for production deployment

**No Rate Limiting on Scrape Jobs:**
- Problem: Scrapers make unlimited requests to websites
- Blocks: Can't scale beyond demo without getting IP-blocked
- Priority: High - Required before adding more sources

**No Database Backups:**
- Problem: Single database instance with no backup mechanism visible
- Blocks: Data loss from any failure is permanent
- Priority: Critical - Must implement immediately

**No Automated Tests:**
- Problem: Zero test files in entire codebase
- Blocks: Can't safely refactor or deploy changes
- Priority: High - Should start with integration tests for critical paths

---

## Test Coverage Gaps

**No Unit Tests:**
- What's not tested: Database methods (`upsert_movie`, `get_movie_reviews`, etc.), LLM client, TMDB client, scraper logic
- Files: `/Users/sundar/Projects/MovieRatings/database.py`, `/Users/sundar/Projects/MovieRatings/llm_client.py`, `/Users/sundar/Projects/MovieRatings/tmdb_client.py`, `/Users/sundar/Projects/MovieRatings/scrapers/rotten_tomatoes.py`
- Risk: Silent failures in critical data operations. No way to catch regressions.
- Priority: High

**No Integration Tests:**
- What's not tested: End-to-end flows (scrape → database → UI), TMDB API + database, LLM summarization pipeline
- Files: All agent files (`movie_release_agent.py`, `summarization_agent.py`), page components
- Risk: Data corruption or loss during complex operations. No verification that UI displays correct data.
- Priority: High

**No E2E Tests:**
- What's not tested: Full user journeys (view homepage, navigate to movie detail, see chart data)
- Files: Web app (`app/page.tsx`, `app/movie/[id]/page.tsx`)
- Risk: UI regressions ship to production. Chart rendering bugs only caught by manual testing.
- Priority: Medium - Lower priority than unit/integration tests

**No Performance Tests:**
- What's not tested: Query performance under load, page load times, connection pool exhaustion
- Risk: Scaling issues discovered in production, not development
- Priority: Medium - Important once traffic scales

---

*Concerns audit: 2026-01-26*
