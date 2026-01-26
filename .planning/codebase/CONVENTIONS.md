# Coding Conventions

**Analysis Date:** 2026-01-26

## Naming Patterns

**Files:**
- TypeScript/React components: PascalCase (e.g., `MovieCard.tsx`, `ReviewTrendChart.tsx`, `TrendBadge.tsx`)
- Utility files: camelCase (e.g., `db.ts`)
- Page components: bracket notation for dynamic routes (e.g., `[id]/page.tsx`)
- Python modules: snake_case (e.g., `base.py`, `rotten_tomatoes.py`, `movie_release_agent.py`, `database.py`)

**Functions:**
- TypeScript: camelCase (e.g., `getTrendingMovies()`, `getRecentMovies()`, `getMovie()`)
- Python: snake_case (e.g., `get_top_reviewers()`, `get_latest_reviews()`, `upsert_movie()`)
- Server functions in Next.js: async functions with descriptive names (e.g., `getTrendingMovies`, `getRecentMovies`, `getMovie`, `getReviews`)

**Variables:**
- TypeScript: camelCase (e.g., `trendingMovies`, `recentMovies`, `movie`, `reviews`, `reviewers`)
- Python: snake_case (e.g., `movie_data`, `region_data`, `reviewer_data`, `total_new_movies`)
- Component props: camelCase object notation (e.g., `{ movie }`, `{ snapshots, anomalyDates }`)

**Types and Interfaces:**
- PascalCase (e.g., `Movie`, `DailySnapshot`, `ReviewTrendChartProps`)
- Inline interfaces for component props (e.g., `Movie` interface defined within `MovieCard.tsx`)
- Props interfaces explicitly named with `Props` suffix (e.g., `ReviewTrendChartProps`)

## Code Style

**Formatting:**
- No explicit prettier or formatter configured - relies on ESLint configuration
- Use 4-space indentation in Python files
- Use 2-space indentation in TypeScript/JavaScript files (implied by Next.js defaults)
- Semicolons required at end of statements in TypeScript

**Linting:**
- ESLint configuration: `eslint.config.mjs` using flat config format (ESLint 9+)
- Extends: `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`
- Ignores: `.next/`, `out/`, `build/`, `next-env.d.ts`
- No custom prettier config - follows Next.js defaults

## Import Organization

**Order:**
1. External dependencies (`next/*`, `react/*`, third-party packages like `lucide-react`, `recharts`, `date-fns`)
2. Internal utilities and database functions (e.g., `from '@/utils/db'`)
3. Type imports (e.g., `import type { Metadata } from "next"`)

**Path Aliases:**
- `@/*` maps to root of web-app directory (e.g., `@/utils/db`, `@/components/MovieCard`)
- Defined in `tsconfig.json`: `"paths": { "@/*": ["./*"] }`

**Patterns Observed:**
```typescript
// Correct ordering pattern from codebase:
import { query } from '@/utils/db';
import Link from 'next/link';
import { TrendingUp, Clock } from 'lucide-react';
```

```typescript
// Client component pattern:
'use client';

import { LineChart, ... } from 'recharts';
import { format } from 'date-fns';
```

## Error Handling

**Patterns:**
- Minimal explicit error handling in frontend code - relies on database query failures to propagate
- Python backend uses try-except blocks for database connections (see `database.py` lines 10-23)
- Fallback UI patterns: Conditional rendering for missing data (e.g., `if (!movie)` returns "Movie not found" div)
- Database null checks: `if not self.conn: return None` pattern (see `database.py` lines 26, 42, 51, etc.)
- No throw statements or explicit error boundaries observed in React components

**Example Pattern:**
```typescript
// From /app/movies/[id]/page.tsx
if (!movie) {
    return <div className="text-white text-center py-24">Movie not found</div>;
}
```

```python
# From database.py
if not self.conn: return None
```

## Logging

**Framework:** `console` (JavaScript) and `print()` (Python)

**Patterns:**
- Python uses print statements for informational logging (see `movie_release_agent.py`, `main.py`)
- No structured logging library detected
- Log messages prefixed with context (e.g., `"Processing Region: {r['code']}..."`)
- Frontend has minimal logging - no console.log statements observed in components

**Example:**
```python
print(f"Fetching top reviewers for US/EN (Rotten Tomatoes)...")
print(f"Found {len(top_reviewers)} reviewers.")
print(f"  - Upserted {count} movies for {r['code']}.")
```

## Comments

**When to Comment:**
- Minimal comments in codebase - code is self-documenting
- Comments used for clarification on non-obvious logic (e.g., scraper fallback patterns)
- Commented code blocks rare - not observed in examined files

**JSDoc/TSDoc:**
- Not used in codebase
- Docstring usage minimal in Python (abstract methods have basic docstrings in `base.py`)

**Example from Python:**
```python
def get_top_reviewers(self, limit=10):
    """Fetches the top reviewers for the source."""
    pass
```

## Function Design

**Size:**
- Generally compact functions (10-40 lines typical)
- Async server functions in Next.js: 6-30 lines
- Python class methods: 10-50 lines with inline SQL queries

**Parameters:**
- TypeScript: Prefer named parameter objects over positional params (e.g., `{ movie }` in component props)
- Python: Mix of positional and keyword arguments, kwargs dictionaries used for data (e.g., `reviewer_data`, `movie_data`)
- Default values used sparingly (e.g., `limit=10` in scrapers)

**Return Values:**
- TypeScript: Return JSX directly from page/component functions, return data rows from queries
- Python: Return dictionaries, lists of dictionaries, or None on failure
- Consistent null/None handling: return empty lists `[]` or `None` rather than throwing errors

**Example:**
```typescript
// Async function returning processed data
async function getTrendingMovies() {
  const result = await query(`...`);
  return result.rows.map(row => ({
    ...row,
    rating_change: row.rating_24h_ago ? row.current_rating - row.rating_24h_ago : 0
  }));
}
```

```python
# Method returning dictionary or None
def upsert_reviewer(self, reviewer_data):
    if not self.conn: return None
    with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, reviewer_data)
        return cur.fetchone()
```

## Module Design

**Exports:**
- TypeScript: Use `export default` for single component exports (e.g., `export default function MovieCard(...)`)
- Page components: Use `export default` for page routes
- Named exports rare - prefer default exports for components

**Barrel Files:**
- Not used in codebase - no index files aggregating exports
- Direct imports from component files (e.g., `import MovieCard from './MovieCard'`)

**Organization:**
- Utilities in `utils/` directory contain helper functions (e.g., `db.ts` exports query function)
- Components in `components/` contain reusable React components
- App routes in `app/` with Next.js file-based routing

## TypeScript Configuration

**Strict Mode:** Enabled (`"strict": true` in `tsconfig.json`)

**Key Compiler Options:**
- `target`: ES2017
- `lib`: DOM, ESNext
- `jsx`: react-jsx
- `moduleResolution`: bundler
- `incremental`: true (for faster rebuilds)
- `isolatedModules`: true
- `noEmit`: true (TypeScript compiles to JS via Next.js)

## Database Code Patterns

**SQL Queries:**
- Inline SQL strings in JavaScript/TypeScript async functions
- Parameterized queries in Python using `%s` placeholders (e.g., `WHERE tmdb_id = $1` in JS, `WHERE tmdb_id = %s` in Python)
- Query results processed immediately after execution
- Connection pooling: pg library in Node.js, psycopg2 in Python

**Example:**
```typescript
// From /app/page.tsx
const result = await query(`
    SELECT DISTINCT ON (m.id)
      m.id, m.tmdb_id, m.title, m.release_date, m.poster_url,
      rs.rating_value as current_rating,
      ...
    FROM movie_platform.movies m
    WHERE rs.snapshot_time > NOW() - INTERVAL '7 days'
    LIMIT 20
`);
```

---

*Convention analysis: 2026-01-26*
