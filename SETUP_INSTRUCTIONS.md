# Setup Instructions - Movie Data Display Fix

## Issues Resolved

1. **All movies showing same poster image** - Fixed
2. **No timeseries of ratings displayed** - Fixed
3. **No rating performance categorization** - Fixed

## What Was Fixed

### 1. Poster Image Bug
**Problem:** All movies had the same placeholder image from Rotten Tomatoes.

**Solution:** Enhanced `agents/web_scraping_tracker.py` to use TMDB API for fetching unique poster images per movie.

### 2. Routing Bug
**Problem:** Home page linked to old movie detail page that used wrong database schema.

**Solution:**
- Updated `web-app/app/page.tsx` to link to `/movies/{id}` instead of `/movie/{id}`
- Deleted old `web-app/app/movie/[id]/page.tsx` that queried wrong schema

### 3. Data Display
**Problem:** Timeseries and categorization features existed but weren't visible.

**Solution:** Correct page (`web-app/app/movies/[id]/page.tsx`) now displayed, showing:
- ReviewTrendChart for timeseries ratings
- TrendBadge for performance categorization
- Rating history table
- Current ratings from multiple sources

## Required Configuration

### TMDB API Key (REQUIRED for unique poster images)

1. **Get a free API key:**
   - Go to https://www.themoviedb.org/
   - Create an account (free)
   - Go to Settings → API
   - Request an API key (free tier is sufficient)

2. **Configure the key:**
   - Open `.env` file in project root
   - Replace `TMDB_API_KEY=your_tmdb_api_key` with your actual key
   - Example: `TMDB_API_KEY=abc123def456...`

3. **Verify configuration:**
   ```bash
   grep TMDB_API_KEY .env
   # Should show: TMDB_API_KEY=abc123def456... (your actual key)
   ```

## How to Apply Changes

### Step 1: Re-populate Database with Correct Images

```bash
# Run the data population script
./populate_db.sh
```

This will:
- Scrape movies from Rotten Tomatoes
- Fetch unique poster/backdrop images from TMDB API
- Store proper poster_url and backdrop_url in database
- Initialize rating snapshots

### Step 2: Start the Platform

```bash
# Start web app and rating monitor
./start_platform.sh
```

This will:
- Populate database if needed
- Analyze trends (calculate movie_trends data)
- Start web dashboard on http://localhost:3000
- Start real-time rating monitor

## Verification

### Check if Images are Fixed

```bash
# Check distinct poster URLs in database
python3 -c "
from database import Database
db = Database()
with db.conn.cursor() as cur:
    cur.execute('SELECT COUNT(DISTINCT poster_url) FROM movies;')
    distinct_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM movies;')
    total_count = cur.fetchone()[0]
    print(f'Distinct posters: {distinct_count}/{total_count}')
    print('✅ Fixed!' if distinct_count > 1 else '❌ Still broken - check TMDB_API_KEY')
"
```

Expected output: `Distinct posters: 20/20` (or similar - numbers should match)

### Check Web App

1. Visit http://localhost:3000
2. Click on any movie from "Biggest Movers" or "Latest Releases"
3. You should see:
   - ✅ Unique poster image for that movie
   - ✅ "Rating History" section with timeseries chart
   - ✅ Trend badge (e.g., "Rising ↑", "Stable →", "Declining ↓")
   - ✅ Current ratings from RT, IMDb, Metacritic

## Troubleshooting

### Still seeing same image for all movies?

**Check 1:** TMDB API key is configured
```bash
grep TMDB_API_KEY .env
# Should NOT show "your_tmdb_api_key"
```

**Check 2:** Re-run population script
```bash
./populate_db.sh
```

**Check 3:** Verify TMDB API is working
```bash
python3 -c "
import os
from dotenv import load_dotenv
import requests
load_dotenv()
api_key = os.environ.get('TMDB_API_KEY')
response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query=Nosferatu')
print('✅ TMDB API working!' if response.status_code == 200 else f'❌ Error: {response.status_code}')
"
```

### Not seeing timeseries/trends?

**Check 1:** Verify rating data exists
```bash
python3 -c "
from database import Database
db = Database()
with db.conn.cursor() as cur:
    cur.execute('SELECT COUNT(*) FROM rating_snapshots;')
    print(f'Rating snapshots: {cur.fetchone()[0]}')
    cur.execute('SELECT COUNT(*) FROM movie_trends;')
    print(f'Movie trends: {cur.fetchone()[0]}')
"
```

**Check 2:** Run trend analyzer
```bash
PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages python3 agents/trend_analyzer.py
```

**Check 3:** Check you're on correct page
- URL should be `/movies/{id}` not `/movie/{id}`
- Old `/movie/` route has been removed

## Summary

**Before Fix:**
- ❌ All movies showed identical placeholder image
- ❌ No rating timeseries visible
- ❌ No performance categorization

**After Fix + Configuration:**
- ✅ Each movie has unique poster from TMDB
- ✅ Rating timeseries charts displayed
- ✅ Performance trends (Rising/Stable/Declining) visible
- ✅ Multiple data sources (RT, IMDb, Metacritic)

**Required Action:**
1. Add TMDB_API_KEY to .env
2. Run ./populate_db.sh
3. Verify at http://localhost:3000
