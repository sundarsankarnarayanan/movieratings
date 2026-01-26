# Movie Review Trend Tracker - GSD Documentation

## What This Does
Tracks movie reviews from RT, IMDb, and Metacritic in real-time. Detects bot manipulation. Shows trending patterns.

## Quick Start (5 minutes)

### 1. Setup Database
```bash
# Start your Postgres (port 54322)
make setup-db
```

### 2. Configure
```bash
# Copy and edit .env
cp .env.example .env
# Set: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
```

### 3. Run
```bash
make start
# Opens dashboard at http://localhost:3000
```

Done. That's it.

---

## Commands You'll Actually Use

```bash
make populate          # Get initial data (20 movies, 50 critics, ratings)
make analyze-trends    # Run trend analysis
make monitor          # Start continuous monitoring (every 60 min)
make web              # Just the dashboard
make clean            # Kill stuck processes
```

---

## How It Works

### Data Flow
```
1. Web Scraper → Grabs movies from RT
2. Rating Monitor → Scrapes RT/IMDb/Metacritic every hour
3. Trend Analyzer → Detects patterns (trending up/down, sleeper hits, bots)
4. Dashboard → Shows everything
```

### What Gets Tracked
- **Daily**: Review counts, scores, velocity
- **Sources**: Rotten Tomatoes, IMDb, Metacritic
- **Metrics**: Growth rate, score momentum, anomalies

---

## Files That Matter

### Agents (Python)
```
agents/web_scraping_tracker.py   # Finds new movies
agents/reviewer_discovery.py     # Finds top critics
agents/rating_monitor.py         # Scrapes ratings (3 sources)
agents/trend_analyzer.py         # Classifies trends
```

### Database
```
schema_v2.sql                    # Main schema
schema_trend_analysis.sql        # Trend tables
```

### Web App
```
web-app/app/page.tsx             # Dashboard
web-app/app/movie/[id]/page.tsx  # Movie details
web-app/components/ReviewTrendChart.tsx  # Trend chart
web-app/components/TrendBadge.tsx        # Status badges
```

---

## Trend Detection Logic

### 🔥 Trending Up
- Positive slope in review velocity
- Consistent growth over 7 days

### 📉 Trending Down
- Negative slope
- Declining interest

### 💎 Sleeper Hit
- Slow start: <20 reviews/day
- Then spikes: 3x+ increase
- Score improves: +5%

### ⚠️ Bot Detection
- Spike >5 standard deviations
- Flags suspicious activity

---

## Troubleshooting

### No data showing?
```bash
# Run populate again
make populate
```

### Dashboard won't start?
```bash
make clean
make web
```

### Scraping errors?
- RT/IMDb/Metacritic change their HTML frequently
- Check selectors in `rating_monitor.py`
- Update CSS selectors as needed

### Database connection failed?
```bash
# Check your .env file
cat .env | grep DB_
# Verify Postgres is running on the right port
lsof -i :54322
```

---

## Customization

### Change scraping interval
```bash
# Edit Makefile or run directly
python3 agents/rating_monitor.py --continuous 30  # Every 30 min
```

### Add more sources
Edit `agents/rating_monitor.py`:
1. Add `scrape_SOURCE_rating()` method
2. Call it in `monitor_movie()`
3. Store with `store_snapshot()`

### Tune bot detection
Edit `agents/trend_analyzer.py`:
```python
# Line ~130: Change threshold
if new_reviews > mean + (5 * stdev):  # Change 5 to 3 for more sensitive
```

---

## Database Schema (Key Tables)

### movies
Core movie data (title, release date, poster, etc.)

### rating_snapshots
Every rating change ever recorded (time-series)

### daily_review_snapshots
Daily aggregates (review counts, velocity, score changes)

### movie_trends
Current trend classification (trending_up, sleeper_hit, etc.)

---

## API Endpoints (Future)

Not implemented yet. Currently uses direct Postgres queries.

To add:
1. Create `web-app/app/api/` routes
2. Move queries from page components to API
3. Add caching

---

## Deployment

### Local (Current)
```bash
make start
```

### Production (TODO)
1. Deploy Postgres to cloud (Supabase, Railway, etc.)
2. Update `.env` with production DB credentials
3. Deploy Next.js to Vercel
4. Run agents on cron (GitHub Actions, Railway, etc.)

---

## Performance

### Current Limits
- Scrapes ~40 movies in ~2 minutes
- Rate limited: 1 req/sec per source
- Dashboard loads in <1s

### Scaling
- Add Redis caching for dashboard
- Use materialized views (already created, need refresh)
- Parallelize scraping with multiprocessing

---

## Contributing

1. Don't break existing scrapers
2. Add tests if you add features
3. Update this doc

---

## License
Do whatever you want with it.

---

## Support
Check the code. It's commented.
