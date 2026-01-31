# Quick Reference - Movie Review Tracker

## One-Liners

```bash
# Create venv and install deps
make install

# Start everything
make start

# Just get data
make populate

# Just analyze
make analyze-trends

# Just dashboard
make web

# Kill stuck stuff
make clean
```

---

## File Structure

```
MovieRatings/
├── agents/                    # Python scrapers
│   ├── web_scraping_tracker.py   # Find movies
│   ├── reviewer_discovery.py     # Find critics
│   ├── rating_monitor.py         # Scrape ratings (RT/IMDb/MC)
│   └── trend_analyzer.py         # Classify trends
├── web-app/                   # Next.js dashboard
│   ├── app/
│   │   ├── page.tsx              # Homepage
│   │   └── movie/[id]/page.tsx   # Movie detail
│   └── components/
│       ├── ReviewTrendChart.tsx  # Trend chart
│       └── TrendBadge.tsx        # Status badge
├── schema_v2.sql              # Main DB schema
├── schema_trend_analysis.sql  # Trend tables
├── Makefile                   # Commands
├── .env                       # Config (DB credentials)
└── README.md                  # Main docs
```

---

## Database Tables

| Table | What It Does |
|-------|-------------|
| `movies` | Movie metadata |
| `reviewers` | Critic info |
| `rating_snapshots` | Every rating change (time-series) |
| `daily_review_snapshots` | Daily aggregates |
| `movie_trends` | Current trend classification |
| `review_sources` | Source config (RT, IMDb, etc.) |
| `scrape_logs` | Error tracking |

---

## Trend Types

| Icon | Status | Meaning |
|------|--------|---------|
| 🔥 | `trending_up` | Growing interest |
| 📉 | `trending_down` | Declining interest |
| 💎 | `sleeper_hit` | Slow start → spike |
| ➡️ | `stable` | No major changes |
| ⚠️ | `suspicious` | Possible bot activity |

---

## Environment Variables

```bash
DB_HOST=127.0.0.1
DB_PORT=54322
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## Common Issues

| Problem | Fix |
|---------|-----|
| Port 3000 busy | `make clean` |
| No data | `make populate` |
| DB connection failed | Check `.env` and Postgres |
| Scraping errors | Sites changed HTML, update selectors |

---

## Scraper Selectors (Update These When Sites Change)

### Rotten Tomatoes
```python
# Rating: 'rt-text[slot="criticsScore"]'
# Review count: '[data-qa="tomatometer-review-count"]'
```

### IMDb
```python
# Rating: '[data-testid="hero-rating-bar__aggregate-rating__score"] span'
```

### Metacritic
```python
# Metascore: '.c-siteReviewScore_background-critic_medium span'
# User score: '.c-siteReviewScore_background-user span'
```

---

## Performance

- Scrape 40 movies: ~2 min
- Analyze trends: ~5 sec
- Dashboard load: <1 sec

---

## Monitoring Schedule

```bash
# Recommended cron
0 * * * * make populate        # Every hour
0 */6 * * * make analyze-trends # Every 6 hours
```

---

## Tech Stack

- **Language**: Python 3.9+, TypeScript
- **Database**: PostgreSQL
- **Web**: Next.js 16, React, Recharts
- **Scraping**: BeautifulSoup4, Requests

---

## Ports

- `3000/3001`: Web dashboard
- `54322`: PostgreSQL

---

## Logs

Check terminal output. No log files (yet).

---

## Backup

```bash
# Backup database
pg_dump -h 127.0.0.1 -p 54322 -U postgres postgres > backup.sql

# Restore
psql -h 127.0.0.1 -p 54322 -U postgres postgres < backup.sql
```
