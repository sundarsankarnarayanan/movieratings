# Coding Conventions

**Analysis Date:** 2026-01-26

## Naming Patterns

**Files:**
- React components use PascalCase: `MovieCard.tsx`, `ReviewTrendChart.tsx`, `TrendBadge.tsx`
- Utility modules use lowercase with hyphens: `db.ts`
- Page routes follow Next.js convention: `page.tsx`, `layout.tsx`, `[id]/page.tsx`

**Functions:**
- Async data-fetching functions use camelCase with descriptive prefixes: `getTrendingMovies()`, `getRecentMovies()`, `getMovie()`, `getReviews()`, `getMovieTrend()`, `getRatingSnapshots()`
- React components (default exports) use PascalCase: `MovieCard`, `ReviewTrendChart`, `TrendBadge`, `RootLayout`
- Helper functions within components use camelCase: `formatDate()`, `mapSnapshots()`

**Variables:**
- camelCase for all variables and constants: `movie`, `reviews`, `trendingMovies`, `chartData`, `imageUrl`
- Underscore prefix for private/internal state: Not observed in codebase
- Constants that are objects/config use camelCase: `geistSans`, `geistMono`, `configs`

**Types:**
- Interfaces use PascalCase: `Movie`, `DailySnapshot`, `ReviewTrendChartProps`, `TrendBadgeProps`
- Generic type parameters use single letters: `CustomTooltip`, generic params implicit in React

**Database/API:**
- SQL column names use snake_case: `tmdb_id`, `poster_url`, `rating_value`, `snapshot_time`, `movie_id`, `reviewer_id`
- Database schema names use snake_case: `movie_platform.movies`, `movie_platform.rating_snapshots`

## Code Style

**Formatting:**
- Indentation: 2 spaces (inferred from package.json and code samples)
- Line length: No strict limit observed; lines extend to ~120 characters
- Quote style: Single quotes for imports and strings: `import { query } from '@/utils/db'`, `alt={movie.title}`
- Except: Double quotes for type imports: `import type { Metadata } from "next"`

**Linting:**
- ESLint v9 with Next.js config (eslint-config-next@16.1.4)
- Rules applied via `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`
- Config: `eslintrc.config.mjs` with ESM modules
- Run: `npm run lint` (no eslint --fix documented)

**TypeScript:**
- Strict mode enabled: `"strict": true` in tsconfig.json
- Target: ES2017
- Module resolution: bundler
- JSX mode: react-jsx

## Import Organization

**Order:**
1. External packages (Next.js, React, third-party): `import { query } from '@/utils/db'`, `import Link from 'next/link'`
2. Icons/UI libraries: `import { TrendingUp, Clock } from 'lucide-react'`, `import { LineChart, Line, ... } from 'recharts'`
3. Internal components: `import ReviewTrendChart from '@/components/ReviewTrendChart'`, `import TrendBadge from '@/components/TrendBadge'`
4. Styles: `import "./globals.css"`
5. Type imports: `import type { Metadata } from "next"` (separate line at top)

**Path Aliases:**
- `@/*` maps to project root: Used as `@/utils/db`, `@/components/ReviewTrendChart`, `@/components/TrendBadge`
- Consistent use across all files

## Error Handling

**Patterns:**
- Try-catch blocks used in data-fetching functions to gracefully handle missing tables: `getRatingSnapshots()`, `getMovieTrend()`, `getReviews()`
- Fallback return values on error: Return empty array `[]` or `null` for failed queries
- No error logging observed; silent failures with default values

Example from `app/movies/[id]/page.tsx`:
```typescript
async function getReviews(title: string) {
    try {
        const result = await query(
            `SELECT r.*, rev.name as reviewer_name, rev.source as reviewer_source
             FROM reviews r
             JOIN reviewers rev ON r.reviewer_id = rev.id
             WHERE r.movie_title = $1`,
            [title]
        );
        return result.rows || [];
    } catch {
        // reviews table may not exist yet
        return [];
    }
}
```

- Conditional rendering for missing data: `{reviews.length === 0 ? ... : ...}`, `{snapshots && snapshots.length > 0 ? ... : ...}`
- Safe property access with optional chaining when inferring types: `movie.regions?.[0]`, `trend?.trend_status`

## Logging

**Framework:** Console output only; no dedicated logging library configured
- No observed console.log, console.error, or console.warn in source files
- Logging appears to be absent for debugging/monitoring

## Comments

**When to Comment:**
- Minimal commenting in codebase
- Comments used for clarification on non-obvious logic or data structure intent

Example from `app/movies/[id]/page.tsx`:
```typescript
// Use daily_review_snapshots for proper time-series data
// Supports both hourly and daily snapshots via snapshot_time
const result = await query(...);
```

**JSDoc/TSDoc:**
- Not used in the codebase
- Type interfaces include inline comments for clarity: `anomalyDates?: string[]`

## Function Design

**Size:** Functions are moderate in size (8-65 lines)
- Data-fetching functions: 5-15 lines (focused queries)
- Component render functions: 20-100+ lines (JSX-heavy)
- No excessive nesting observed

**Parameters:**
- Single object parameter for components: `function MovieCard({ movie }: { movie: Movie })`
- Destructured in function signature
- Database queries use parameterized queries: `query(text: string, params?: any[])`

**Return Values:**
- Async functions return Promise<Array> or Promise<Object|null>
- React components return JSX.Element
- Conditional early returns for error states: `if (!movie) return <div>...</div>`

## Module Design

**Exports:**
- Default exports for page components: `export default function Home() {...}`
- Default exports for React components: `export default function MovieCard(...) {...}`
- Named exports for utilities: `export const query = (...) => pool.query(...)`
- Type exports: `interface Movie { ... }` (not explicitly exported but implicitly available)

**Barrel Files:**
- Not observed in codebase structure

---

*Convention analysis: 2026-01-26*
