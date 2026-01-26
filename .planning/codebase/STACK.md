# Technology Stack

**Analysis Date:** 2026-01-26

## Languages

**Primary:**
- TypeScript 5 - All application code and configuration
- TSX/JSX - React component files in `app/` and `components/`

**Secondary:**
- JavaScript - PostCSS and ESLint configuration files

## Runtime

**Environment:**
- Node.js (version unspecified in project, uses ESM modules)

**Package Manager:**
- npm
- Lockfile: `package-lock.json` present

## Frameworks

**Core:**
- Next.js 16.1.4 - Full-stack React framework with App Router
  - Entry point: `app/layout.tsx`
  - Pages: `app/page.tsx` (home), `app/movies/[id]/page.tsx` (detail)

**UI & Styling:**
- React 19.2.3 - Component library
- React DOM 19.2.3 - DOM rendering
- Tailwind CSS 4 - Utility-first CSS framework
  - Config: PostCSS via `postcss.config.mjs`

**Data Visualization:**
- Recharts 3.7.0 - Charting library for React
  - Used in `components/ReviewTrendChart.tsx` for line charts

**Icons & Utilities:**
- Lucide React 0.562.0 - Icon library (used in components for TrendingUp, Star, Clock, Globe, etc.)
- date-fns 4.1.0 - Date formatting and manipulation

## Database & ORM

**Database Driver:**
- pg (node-postgres) 8.17.2 - PostgreSQL client
  - TypeScript definitions: `@types/pg` 8.16.0

**Connection:**
- Custom pool wrapper in `utils/db.ts`
- Uses `Pool` from `pg` with environment-based configuration
- Auto-sets schema to `movie_platform` on connection

**No ORM detected** - Raw SQL queries used throughout application

## Testing & Linting

**Linting:**
- ESLint 9 - JavaScript/TypeScript linter
  - Config: `eslint.config.mjs` (flat config format)
  - Extends: `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`
  - Ignores: `.next/`, `out/`, `build/`, `next-env.d.ts`

**Testing Framework:** Not detected in dependencies or configuration

## Build & Development

**Build Tools:**
- Next.js built-in bundler and TypeScript compiler
- Tailwind CSS with PostCSS compilation

**Development Server:**
- Next.js dev server (`npm run dev`)

**Build Commands:**
```bash
npm run dev       # Start development server
npm run build     # Build for production
npm start         # Start production server
npm run lint      # Run ESLint
```

## Configuration

**TypeScript:**
- Config file: `tsconfig.json`
- Target: ES2017
- Strict mode enabled
- Module resolution: bundler
- Path alias: `@/*` maps to project root
- JSX: react-jsx

**Next.js:**
- Config file: `next.config.ts` (minimal/empty configuration)
- Revalidation: Dynamic routes set to `revalidate = 0` (no ISR caching)

**Environment:**
- Development config: `.env.local`
- Example provided: `.env.local.example`
- Required variables: Database connection (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
- Client-side variables would use `NEXT_PUBLIC_` prefix (Supabase SDK imported but not actively used in current code)

## Platform Requirements

**Development:**
- Node.js runtime
- PostgreSQL database (local or remote)
- Port 54322 default (dev config in `.env.local`)

**Production:**
- Node.js runtime
- PostgreSQL database
- Standard Next.js deployment target (Vercel recommended, but any Node.js host works)

## Dependency Summary

**Direct Production Dependencies:**
- `@supabase/supabase-js` 2.91.0 - Supabase SDK (imported but not actively used in current code)
- `date-fns` 4.1.0 - Date utilities
- `lucide-react` 0.562.0 - Icon components
- `next` 16.1.4 - Web framework
- `pg` 8.17.2 - PostgreSQL driver
- `react` 19.2.3 - UI library
- `react-dom` 19.2.3 - DOM rendering
- `recharts` 3.7.0 - Charting library

**Total dependencies:** 8 production, 6 dev

---

*Stack analysis: 2026-01-26*
