# Coding Conventions

**Analysis Date:** 2026-01-27

## Overview

This is a polyglot codebase with two main parts:
- **TypeScript/React**: Next.js web application in `web-app/`
- **Python**: Backend scrapers, agents, and database operations in the root directory

## Naming Patterns

### TypeScript/React (web-app/)

**Files:**
- React components: PascalCase (e.g., `MovieCard.tsx`, `TrendBadge.tsx`, `ReviewTrendChart.tsx`)
- Page routes: `page.tsx` following Next.js App Router conventions
- Layout files: `layout.tsx`
- Utility modules: camelCase (e.g., `db.ts`)

**Functions:**
- React components: PascalCase (e.g., `MovieCard`, `TrendBadge`)
- Data fetching functions: camelCase with verb prefix (e.g., `getMovie`, `getReviews`, `getTrendingMovies`)
- Event handlers: camelCase with `handle` prefix or descriptive action

**Variables:**
- camelCase for all variables (e.g., `trendingMovies`, `chartData`, `reviewVelocity`)
- Constants: camelCase (not SCREAMING_CASE)

**Interfaces/Types:**
- PascalCase with descriptive suffix (e.g., `TrendBadgeProps`, `DailySnapshot`, `ReviewTrendChartProps`)
- Props interfaces end with `Props`

### Python (root/)

**Files:**
- Snake_case for modules (e.g., `rotten_tomatoes.py`, `trend_analyzer.py`, `movie_release_agent.py`)
- Test files prefixed with `test_` (e.g., `test_scraper.py`, `test_mcp_server.py`)

**Classes:**
- PascalCase (e.g., `Database`, `TMDBClient`, `RottenTomatoesScraper`, `TrendAnalyzer`, `BaseScraper`)

**Functions/Methods:**
- snake_case (e.g., `get_top_reviewers`, `upsert_movie`, `calculate_trend_slope`)
- Private methods: underscore prefix (e.g., `_get_soup`)

**Variables:**
- snake_case (e.g., `review_counts`, `trend_status`, `avg_daily_reviews`)

**Constants:**
- SCREAMING_SNAKE_CASE (though few explicit constants exist)

## Code Style

### TypeScript/React

**Formatting:**
- Implicit via Next.js defaults (no explicit Prettier config found)
- 4-space indentation observed in components
- Single quotes for imports
- Double quotes for JSX attributes

**Linting:**
- ESLint with Next.js config (`eslint.config.mjs`)
- Uses `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`
- Run with: `npm run lint` (from `web-app/` directory)

**TypeScript:**
- Strict mode enabled (`"strict": true` in `tsconfig.json`)
- ES2017 target
- Module resolution: bundler
- Path alias: `@/*` maps to `./*`

### Python

**Formatting:**
- No explicit formatter configured (no `.flake8`, `.black.toml`, `pyproject.toml`)
- 4-space indentation observed
- Line length varies (some lines exceed 120 chars)

**Linting:**
- No explicit linting configuration found

## Import Organization

### TypeScript/React

**Order observed:**
1. External packages (React, Next.js, third-party)
2. Internal components/utils (using `@/` alias)

**Example from `web-app/app/movies/[id]/page.tsx`:**
```typescript
import { query } from '@/utils/db';
import { Star, Calendar, Globe, Sparkles, TrendingUp } from 'lucide-react';
import ReviewTrendChart from '@/components/ReviewTrendChart';
import TrendBadge from '@/components/TrendBadge';
```

**Path Aliases:**
- Use `@/` for all internal imports (e.g., `@/utils/db`, `@/components/TrendBadge`)
- Avoid relative paths for components and utilities

### Python

**Order observed:**
1. Standard library imports
2. Third-party packages
3. Local module imports

**Example from `agents/trend_analyzer.py`:**
```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, timedelta
import statistics
```

## Error Handling

### TypeScript/React

**Patterns:**
- Try-catch with silent fallback for optional data:
```typescript
async function getReviews(title: string) {
    try {
        const result = await query(...);
        return result.rows || [];
    } catch {
        // reviews table may not exist yet
        return [];
    }
}
```
- Empty catch block with comment explaining the expected error case
- Return empty arrays `[]` or `null` on failure

### Python

**Patterns:**
- Guard clauses checking for `None` connections:
```python
def upsert_movie(self, movie_data):
    if not self.conn: return None
    # ... rest of method
```
- Print statements for error reporting (not logging framework):
```python
except Exception as e:
    print(f"Error connecting to database: {e}")
```

## Logging

**TypeScript/React:**
- No explicit logging framework
- Console not used in production code

**Python:**
- `print()` statements with emoji prefixes for CLI output:
```python
print("Fetching top reviewers for US/EN (Rotten Tomatoes)...")
print(f"    {status_icon} Status: {trend_data['trend_status']}")
print(f"    Spike detected on {trend_data['spike_date']} ({trend_data['spike_magnitude']:.1f})")
```
- Status icons used: fire, chart_increasing, gem, arrow_right, warning, checkmark, x-mark

## Comments

### When to Comment:
- Document table structure assumptions
- Explain business logic (e.g., sleeper hit detection algorithm)
- Note TODOs for missing features
- Explain fallback behavior

### Docstrings (Python):
- Module-level docstrings with triple quotes:
```python
"""
Agent 4: Trend Analyzer
Analyzes daily review snapshots and classifies movie trends
"""
```
- Method docstrings for public APIs:
```python
def get_movies_by_date(self, date, r_region=None, r_language=None):
    """
    Fetches movies released on a specific date.
    TMDb Discover API parameters:
    primary_release_date.gte: start date
    ...
    """
```

### JSDoc/TSDoc (TypeScript):
- Not heavily used
- Interfaces serve as documentation

## Function Design

### TypeScript/React

**Size:**
- Data fetching functions: 5-20 lines
- React components: 20-150 lines

**Parameters:**
- Props destructured inline or via interface
- Optional parameters use `?` or default values

**Return Values:**
- Data functions return arrays or objects
- Components return JSX

### Python

**Size:**
- Methods typically 10-40 lines
- Complex algorithms documented inline

**Parameters:**
- Default values common (e.g., `limit=10`, `days=30`)
- Named parameters for clarity

**Return Values:**
- Return dictionaries for structured data
- Return `None` or empty list on failure

## Module Design

### TypeScript/React

**Exports:**
- Default exports for React components
- Named exports for utilities:
```typescript
export const query = (text: string, params?: any[]) => pool.query(text, params);
```

**Barrel Files:**
- Not used; direct imports preferred

### Python

**Exports:**
- Classes are the primary export unit
- `__init__.py` files for package structure (e.g., `scrapers/__init__.py`)

**Pattern:**
- Main entry point via `if __name__ == "__main__":` block

## React Component Patterns

**Server Components (default):**
- Async data fetching in page components
- `export const revalidate = 0;` for dynamic data

**Client Components:**
- Marked with `'use client';` directive
- Used for interactive charts/visualizations

**Props Pattern:**
```typescript
interface TrendBadgeProps {
    status: 'trending_up' | 'trending_down' | 'sleeper_hit' | 'stable';
    confidence?: number;
    showLabel?: boolean;
}

export default function TrendBadge({ status, confidence = 0, showLabel = true }: TrendBadgeProps) {
```

## Styling Conventions

**Framework:** Tailwind CSS v4

**Patterns:**
- Inline Tailwind classes on elements
- CSS variables for theme colors (defined in `globals.css`)
- Gradient backgrounds common: `bg-gradient-to-br from-gray-900 via-black to-gray-900`
- Responsive prefixes: `md:`, `lg:`
- Hover states: `hover:scale-[1.02]`, `group-hover:opacity-80`

**Color Scheme:**
- Dark mode primary (gray-900, black backgrounds)
- Accent colors: indigo, purple, pink, green, yellow
- Status colors: green (positive), red (negative), yellow (warning)

## Database Interaction Patterns

### TypeScript (web-app)

**Location:** `web-app/utils/db.ts`

**Pattern:**
- Direct SQL queries with parameterized inputs
- Pool connection with `pg` library
- Schema set on connect: `SET search_path TO movie_platform`

```typescript
export const query = (text: string, params?: any[]) => pool.query(text, params);

// Usage in components:
const result = await query('SELECT * FROM movies WHERE tmdb_id = $1 LIMIT 1', [id]);
```

### Python (root)

**Location:** `database.py`

**Pattern:**
- Class-based database wrapper
- `psycopg2` with `RealDictCursor` for dict-style results
- Upsert methods with `ON CONFLICT DO UPDATE`

```python
def upsert_movie(self, movie_data):
    if not self.conn: return None
    with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            INSERT INTO movies (tmdb_id, title, ...)
            ON CONFLICT (tmdb_id) DO UPDATE SET ...
            RETURNING *;
        """
        cur.execute(query, movie_data)
        return cur.fetchone()
```

## Environment Variables

**Pattern:**
- Load with `dotenv` in Python: `load_dotenv()`
- Access via `process.env` in TypeScript, `os.environ.get()` in Python

**Required Variables:**
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `TMDB_API_KEY` (for movie data)

---

*Convention analysis: 2026-01-27*
