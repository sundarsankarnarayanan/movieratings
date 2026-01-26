# STATE: Movie Review Trend Platform

## Current Phase: Phase 3 & 4 (Analysis & Dashboard Integration)

## Core Specs
- [x] S1: Database Schema Version 2.1 (Trend Analysis Support)
- [x] S2: Python Scraping Core (Agents 1, 2, 3, 4)
- [x] S3: Next.js Dashboard Foundation

## Implementation Details
### Database
- `movies`: Correct metadata populated.
- `rating_snapshots`: 200+ historical entries stored.
- `daily_review_snapshots`: Table created, awaiting high-fidelity review count data.
- `movie_trends`: Table created and verified.

### Agents
- `web_scraping_tracker.py`: Verified (Fixed poster selector issue).
- `reviewer_discovery.py`: Verified.
- `rating_monitor.py`: Scrapes RT, IMDb, Metacritic. Daily snapshot logic implemented.
- `trend_analyzer.py`: Classification logic complete (Sleeper/Trending/Bot).

### Frontend
- Movie Detail Page: Integrated `ReviewTrendChart` and `TrendBadge`.
- Homepage: Shows movers/recent releases.

## Blockers / Next Steps
- **B1**: Review count scraping for RT is intermittent. Investigating JSON-LD or API-like endpoints for more reliable counts.
- **N1**: Run full trend analysis cycle (`make analyze-trends`).
- **N2**: Add "Trending" and "Sleeper Hit" sections to the main dashboard.
- **N3**: Fix data quality for movies currently showing 90% (Run full re-scrape).
