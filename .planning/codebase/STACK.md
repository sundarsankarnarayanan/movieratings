# Technology Stack

**Analysis Date:** 2026-01-26

## Languages

**Primary:**
- TypeScript 5.x - Frontend and Next.js application code
- JavaScript/JSX - React components and utility functions
- Python 3 - Backend scripts for data collection, scraping, and LLM integration

**Secondary:**
- SQL - Database schema and queries (PostgreSQL)
- Shell - Automation scripts for setup and deployment

## Runtime

**Environment:**
- Node.js 18+ (inferred from Next.js 16.1.4)
- Python 3.8+ (for backend services)

**Package Manager:**
- npm (Node.js packages)
- pip (Python packages)
- Lockfile: `web-app/package-lock.json` (present for Node), `requirements.txt` for Python

## Frameworks

**Core Web:**
- Next.js 16.1.4 - Full-stack React framework with SSR
- React 19.2.3 - UI library

**Testing:**
- Not detected in current dependencies

**Build/Dev:**
- TypeScript 5.x - Type checking
- ESLint 9.x - Code linting with Next.js config
- Tailwind CSS 4.x - Utility-first CSS styling
- PostCSS 4.x - CSS processing pipeline

**Backend/Data:**
- psycopg2-binary - Python PostgreSQL adapter
- BeautifulSoup4 - Web scraping library
- Requests - HTTP client for API calls

## Key Dependencies

**Critical:**
- `@supabase/supabase-js` 2.91.0 - Supabase client (for auth/database operations via client)
- `pg` 8.17.2 - PostgreSQL driver for Node.js backend queries
- `recharts` 3.7.0 - React charting library for visualization
- `lucide-react` 0.562.0 - React icon library
- `date-fns` 4.1.0 - Date manipulation utilities

**Backend Integration:**
- `openai` - OpenAI API client for LLM summarization
- `python-dotenv` - Environment variable management
- `mcp[cli]` - Model Context Protocol for agent communication

## Configuration

**Environment:**
- `.env` - Root environment file for backend (database, API keys)
- `.env.local` - Web-app frontend environment overrides
- `.env.example` - Example configuration template
- Environment variables required:
  - Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
  - External APIs: `TMDB_API_KEY`, `OPENAI_API_KEY`
  - Supabase: `SUPABASE_URL`, `SUPABASE_KEY`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Build:**
- `web-app/tsconfig.json` - TypeScript compilation settings (ES2017 target, strict mode enabled)
- `web-app/next.config.ts` - Next.js configuration (currently minimal)
- `web-app/eslint.config.mjs` - ESLint with Next.js and TypeScript rules
- `web-app/postcss.config.mjs` - PostCSS with Tailwind CSS plugin

**Path Aliases:**
- `@/*` → `./*` (root of web-app directory for imports)

## Platform Requirements

**Development:**
- Node.js 18+
- npm or yarn
- Python 3.8+
- PostgreSQL 12+ (local or via Supabase)
- Environment variables configured in `.env` and `.env.local`

**Production:**
- Deployment target: Vercel (inferred from Next.js setup) or self-hosted Node.js server
- Database: PostgreSQL instance (local or Supabase)
- Python backend: Requires separate runtime or serverless function support

---

*Stack analysis: 2026-01-26*
