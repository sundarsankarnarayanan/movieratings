# GSD: From Idea to Working System

## The Ask
"I want to track movie reviews in real-time and detect bot manipulation."

## What We Built
A multi-source review tracking system with trend analysis and bot detection.

---

## Evolution

### Phase 1: Basic Setup
**Goal**: Get movie data into a database

**What we did**:
- Created Postgres schema
- Built RT scraper for new releases
- Stored movies in DB

**Result**: 20 movies in database

---

### Phase 2: Multi-Source Ratings
**Goal**: Track ratings from multiple platforms

**What we did**:
- Added rating monitor agent
- Scraped RT, IMDb, Metacritic
- Stored time-series snapshots

**Result**: Real-time rating tracking from 3 sources

---

### Phase 3: Trend Analysis
**Goal**: Detect manipulation and trending patterns

**What we did**:
- Created daily snapshot table
- Built trend analyzer with classification logic
- Added anomaly detection (bot spikes)

**Result**: Automatic classification (🔥 trending up, 💎 sleeper hit, ⚠️ suspicious)

---

### Phase 4: Visualization
**Goal**: Show trends to users

**What we did**:
- Built Next.js dashboard
- Created interactive trend charts
- Added trend badges

**Result**: Visual dashboard at localhost:3000

---

## Key Decisions

### Why web scraping instead of APIs?
- No API keys needed
- More data sources available
- Free

### Why Postgres instead of MongoDB?
- Time-series queries are easier with SQL
- Materialized views for performance
- JSONB for flexibility when needed

### Why daily snapshots instead of every scrape?
- Reduces storage (1 row/day vs 24 rows/day)
- Easier trend analysis
- Still captures manipulation patterns

---

## What Works

✅ Scrapes 3 sources (RT, IMDb, Metacritic)  
✅ Detects rating changes  
✅ Tracks review velocity  
✅ Classifies trends automatically  
✅ Flags suspicious spikes  
✅ Shows interactive charts  

---

## What Needs Work

⚠️ Review count scraping (RT doesn't always expose counts)  
⚠️ Scraper selectors break when sites update  
⚠️ No API layer (direct DB queries in components)  
⚠️ No caching (every page load hits DB)  
⚠️ No tests  

---

## Lessons Learned

1. **Start simple**: Got basic scraping working before adding complexity
2. **Iterate fast**: Built MVP, then added features based on what was missing
3. **Scraping is fragile**: Sites change HTML frequently, need monitoring
4. **Time-series is powerful**: Daily snapshots enable rich trend analysis
5. **Visual feedback matters**: Charts make trends immediately obvious

---

## Next Steps (If You Want)

### Short-term
1. Fix review count scraping
2. Add error monitoring
3. Create API layer

### Long-term
1. Add more sources (Letterboxd, etc.)
2. ML-based bot detection
3. Email alerts for suspicious activity
4. Public deployment

---

## Time Investment

- **Planning**: 30 min
- **Database schema**: 1 hour
- **Scrapers**: 3 hours (RT, IMDb, Metacritic)
- **Trend analysis**: 2 hours
- **UI components**: 2 hours
- **Testing/debugging**: 2 hours

**Total**: ~10 hours from zero to working system

---

## The Stack

**Backend**: Python + Postgres  
**Scraping**: BeautifulSoup + Requests  
**Frontend**: Next.js + React + Recharts  
**Deployment**: Local (for now)

---

## Files Created (In Order)

1. `schema_v2.sql` - Database foundation
2. `agents/web_scraping_tracker.py` - Movie discovery
3. `agents/reviewer_discovery.py` - Critic tracking
4. `agents/rating_monitor.py` - Multi-source scraping
5. `schema_trend_analysis.sql` - Trend tables
6. `agents/trend_analyzer.py` - Classification logic
7. `web-app/components/ReviewTrendChart.tsx` - Visualization
8. `web-app/components/TrendBadge.tsx` - Status indicators
9. `Makefile` - Automation
10. `README.md` - This doc

---

## Commands Used Most

```bash
make populate          # Get fresh data
make analyze-trends    # Run analysis
make web              # Start dashboard
```

---

## Metrics

- **Movies tracked**: 40+
- **Reviewers**: 50+
- **Rating snapshots**: 100+/day
- **Sources**: 3 (RT, IMDb, Metacritic)
- **Trend classifications**: 4 types
- **Bot detection**: 5σ threshold

---

## Bottom Line

From "I want to track reviews" to a working multi-source trend analysis system in ~10 hours.

**The GSD approach**: Build the simplest thing that works, then iterate based on real needs.
