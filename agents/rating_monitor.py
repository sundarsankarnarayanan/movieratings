"""
Agent 3: Real-Time Rating Monitor
Continuously scrapes rating updates and stores time-series snapshots
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

load_dotenv()

class RatingMonitor:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD")
        )
        self.conn.autocommit = True
        
        with self.conn.cursor() as cur:
            cur.execute("SET search_path TO movie_platform;")
    
    def get_active_movies(self, days=30):
        """Get movies released in the last N days"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT * FROM movies 
                WHERE release_date > NOW() - INTERVAL '%s days'
                ORDER BY release_date DESC;
            """
            cur.execute(query, (days,))
            return cur.fetchall()
    
    def scrape_rt_rating(self, movie_title):
        """Scrape Rotten Tomatoes rating for a movie"""
        import json

        # Search for movie
        search_url = f"https://www.rottentomatoes.com/search?search={movie_title.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find first movie result in the movie results section
            movie_section = soup.select_one('search-page-result[type="movie"]')
            if not movie_section:
                # Fallback to general search media row
                movie_link = soup.select_one('search-page-media-row a[slot="title"], a[data-qa="search-result-title"]')
            else:
                movie_link = movie_section.select_one('search-page-media-row a[slot="title"]')

            if not movie_link:
                # Last resort fallback
                movie_link = soup.select_one('a[href*="/m/"]')

            if not movie_link:
                return None

            movie_url = movie_link['href']
            if not movie_url.startswith('http'):
                movie_url = f"https://www.rottentomatoes.com{movie_url}"

            # Get movie page
            movie_response = requests.get(movie_url, headers=headers, timeout=10)
            movie_response.raise_for_status()
            movie_soup = BeautifulSoup(movie_response.text, 'html.parser')

            ratings = {}
            review_counts = {}

            # PRIMARY METHOD: Extract from JSON-LD schema data (most reliable)
            for script in movie_soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'Movie':
                        agg = data.get('aggregateRating', {})
                        if agg.get('ratingValue'):
                            ratings['tomatometer'] = float(agg['ratingValue'])
                        if agg.get('reviewCount'):
                            review_counts['critic_reviews'] = int(agg['reviewCount'])
                        break
                except Exception:
                    pass

            # FALLBACK: CSS selectors for audience score (not in JSON-LD)
            if 'tomatometer' not in ratings:
                tomatometer = movie_soup.select_one('rt-text[slot="criticsScore"], [data-qa="tomatometer"]')
                if tomatometer:
                    score_text = tomatometer.text.strip().replace('%', '')
                    try:
                        ratings['tomatometer'] = float(score_text)
                    except Exception as e:
                        print(f"      Failed to parse tomatometer '{score_text}': {e}")

            audience_score = movie_soup.select_one('rt-text[slot="audienceScore"], [data-qa="audience-score"]')
            if audience_score:
                score_text = audience_score.text.strip().replace('%', '')
                try:
                    ratings['audience'] = float(score_text)
                except Exception as e:
                    print(f"      Failed to parse audience score '{score_text}': {e}")

            # Additional review counts from page scraping
            page_review_counts = self.scrape_review_counts(movie_soup)
            if page_review_counts:
                review_counts.update(page_review_counts)

            if review_counts:
                ratings['review_counts'] = review_counts

            return ratings

        except Exception as e:
            print(f"Error scraping RT for {movie_title}: {e}")
            return None
    
    def scrape_review_counts(self, soup):
        """Extract review counts from movie page"""
        try:
            counts = {}
            
            # Try to find critic review count
            critic_count_elem = soup.select_one('[data-qa="tomatometer-review-count"], .scoreboard__info--reviews')
            if critic_count_elem:
                text = critic_count_elem.text.strip()
                # Extract number from text like "150 Reviews"
                import re
                match = re.search(r'(\d+)', text)
                if match:
                    counts['critic_reviews'] = int(match.group(1))
            
            # Try to find audience review count  
            audience_count_elem = soup.select_one('[data-qa="audience-rating-count"]')
            if audience_count_elem:
                text = audience_count_elem.text.strip()
                match = re.search(r'([\d,]+)', text)
                if match:
                    counts['audience_reviews'] = int(match.group(1).replace(',', ''))
            
            return counts if counts else None
        except Exception as e:
            print(f"      Failed to extract review counts: {e}")
            return None
    
    def scrape_imdb_rating(self, movie_title):
        """Scrape IMDb rating for a movie"""
        try:
            # Search IMDb
            search_url = f"https://www.imdb.com/find?q={movie_title.replace(' ', '+')}&s=tt&ttype=ft"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find first movie result
            result = soup.select_one('a[href*="/title/tt"]')
            if not result:
                return None
            
            movie_url = f"https://www.imdb.com{result['href'].split('?')[0]}"
            
            # Get movie page
            movie_response = requests.get(movie_url, headers=headers, timeout=10)
            movie_response.raise_for_status()
            movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
            
            # Extract rating
            rating_elem = movie_soup.select_one('[data-testid="hero-rating-bar__aggregate-rating__score"] span')
            if rating_elem:
                score_text = rating_elem.text.strip()
                try:
                    # IMDb uses 0-10 scale, convert to percentage
                    score = float(score_text) * 10
                    return {'imdb_score': score}
                except:
                    pass
            
            return None
        except Exception as e:
            print(f"      Error scraping IMDb: {e}")
            return None
    
    def scrape_metacritic_rating(self, movie_title):
        """Scrape Metacritic rating for a movie"""
        try:
            # Search Metacritic
            search_url = f"https://www.metacritic.com/search/{movie_title.replace(' ', '-')}/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find movie result
            movie_link = soup.select_one('a[href*="/movie/"]')
            if not movie_link:
                return None
            
            movie_url = f"https://www.metacritic.com{movie_link['href']}"
            
            # Get movie page
            movie_response = requests.get(movie_url, headers=headers, timeout=10)
            movie_response.raise_for_status()
            movie_soup = BeautifulSoup(movie_response.text, 'html.parser')
            
            ratings = {}
            
            # Metascore (critic score)
            metascore = movie_soup.select_one('.c-siteReviewScore_background-critic_medium span, .metascore_w')
            if metascore:
                try:
                    ratings['metascore'] = float(metascore.text.strip())
                except:
                    pass
            
            # User score
            user_score = movie_soup.select_one('.c-siteReviewScore_background-user span')
            if user_score:
                try:
                    # User score is 0-10, convert to percentage
                    ratings['user_score'] = float(user_score.text.strip()) * 10
                except:
                    pass
            
            return ratings if ratings else None
        except Exception as e:
            print(f"      Error scraping Metacritic: {e}")
            return None
    
    def get_last_snapshot(self, movie_id, source, rating_type):
        """Get the most recent snapshot for comparison"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT * FROM rating_snapshots
                WHERE movie_id = %s AND source = %s AND rating_type = %s
                ORDER BY snapshot_time DESC
                LIMIT 1;
            """
            cur.execute(query, (movie_id, source, rating_type))
            return cur.fetchone()
    
    def store_snapshot(self, movie_id, source, rating_type, rating_value, review_count=0):
        """Store a new rating snapshot"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:

            query = """
                INSERT INTO rating_snapshots (
                    movie_id, source, rating_type, rating_value, review_count, snapshot_time
                ) VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (movie_id, source, rating_type, snapshot_time) DO NOTHING
                RETURNING *;
            """

            cur.execute(query, (movie_id, source, rating_type, rating_value, review_count))
            self.conn.commit()
            return cur.fetchone()
    
    def store_daily_snapshot(self, movie_id, source, ratings, review_counts, interval='daily'):
        """Store review snapshot for trend analysis.

        Args:
            movie_id: UUID of the movie
            source: Rating source (e.g., 'RottenTomatoes')
            ratings: Dict with 'tomatometer' and/or 'audience' scores
            review_counts: Dict with 'critic_reviews' and/or 'audience_reviews'
            interval: 'hourly' or 'daily' - determines snapshot granularity
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            from datetime import datetime

            # Determine snapshot time based on interval
            if interval == 'hourly':
                time_trunc = "DATE_TRUNC('hour', NOW())"
                prev_interval = "1 hour"
            else:
                time_trunc = "DATE_TRUNC('day', NOW())"
                prev_interval = "1 day"

            # Check previous snapshot
            prev_query = f"""
                SELECT total_reviews, critic_score 
                FROM daily_review_snapshots 
                WHERE movie_id = %s AND source = %s 
                AND snapshot_time = {time_trunc} - INTERVAL '{prev_interval}'
                LIMIT 1;
            """
            cur.execute(prev_query, (movie_id, source))
            previous = cur.fetchone()

            # Calculate metrics
            total_reviews = review_counts.get('critic_reviews', 0) + review_counts.get('audience_reviews', 0)
            new_reviews = 0
            score_change = 0.0

            if previous:
                new_reviews = total_reviews - (previous['total_reviews'] or 0)
                if previous['critic_score'] and ratings.get('tomatometer'):
                    score_change = ratings['tomatometer'] - previous['critic_score']

            # Calculate velocity (reviews per day since release)
            days_query = "SELECT EXTRACT(DAY FROM NOW() - release_date)::INTEGER as days FROM movies WHERE id = %s;"
            cur.execute(days_query, (movie_id,))
            days_result = cur.fetchone()
            days_since_release = max(days_result['days'] if days_result else 1, 1)
            review_velocity = total_reviews / days_since_release

            # Store snapshot with timestamp
            query = f"""
                INSERT INTO daily_review_snapshots (
                    movie_id, source, snapshot_date, snapshot_time,
                    total_reviews, new_reviews_today,
                    critic_score, audience_score, score_change
                ) VALUES (%s, %s, CURRENT_DATE, {time_trunc}, %s, %s, %s, %s, %s)
                ON CONFLICT (movie_id, source, snapshot_time) DO UPDATE SET
                    total_reviews = EXCLUDED.total_reviews,
                    new_reviews_today = EXCLUDED.new_reviews_today,
                    critic_score = EXCLUDED.critic_score,
                    audience_score = EXCLUDED.audience_score
                RETURNING *;
            """
            
            cur.execute(query, (
                movie_id, source,
                total_reviews, new_reviews,
                ratings.get('tomatometer'), ratings.get('audience'), score_change
            ))

            return cur.fetchone()
    
    def log_scrape(self, source_name, movie_id, status, error_message=None, snapshots_created=0):
        """Log scraping activity"""
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO scrape_logs (
                    source_name, movie_id, status, error_message, snapshots_created
                ) VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(query, (source_name, movie_id, status, error_message, snapshots_created))
    
    def monitor_movie(self, movie, interval='daily'):
        """Monitor a single movie for rating changes from all sources.

        Args:
            movie: Movie dict with 'id', 'title', etc.
            interval: 'hourly' or 'daily' - snapshot granularity
        """
        print(f"  Monitoring: {movie['title']}")
        
        snapshots_created = 0
        
        # 1. Scrape Rotten Tomatoes
        rt_ratings = self.scrape_rt_rating(movie['title'])
        if rt_ratings:
            review_counts = rt_ratings.pop('review_counts', {})
            
            # Store regular snapshots
            for rating_type, rating_value in rt_ratings.items():
                last_snapshot = self.get_last_snapshot(movie['id'], 'RottenTomatoes', rating_type)
                
                if not last_snapshot or last_snapshot['rating_value'] != rating_value:
                    snapshot = self.store_snapshot(
                        movie['id'], 
                        'RottenTomatoes', 
                        rating_type, 
                        rating_value
                    )
                    if snapshot:
                        snapshots_created += 1
                        change = ""
                        if last_snapshot:
                            diff = rating_value - last_snapshot['rating_value']
                            change = f" ({diff:+.1f})"
                        print(f"    ✅ RT {rating_type}: {rating_value}{change}")
            
            # Store time-series snapshot
            if review_counts:
                try:
                    daily_snapshot = self.store_daily_snapshot(
                        movie['id'],
                        'RottenTomatoes',
                        rt_ratings,
                        review_counts,
                        interval=interval
                    )
                    if daily_snapshot:
                        label = "Hourly" if interval == 'hourly' else "Daily"
                        print(f"    📊 {label} snapshot: {daily_snapshot['total_reviews']} reviews (+{daily_snapshot['new_reviews_today']} new)")
                except Exception as e:
                    print(f"    ⚠️ Failed to store daily snapshot: {e}")
            
            self.log_scrape('RottenTomatoes', movie['id'], 'success', snapshots_created=snapshots_created)
        else:
            self.log_scrape('RottenTomatoes', movie['id'], 'error', error_message='No ratings found')
        
        # 2. Scrape IMDb
        time.sleep(1)  # Rate limiting
        imdb_ratings = self.scrape_imdb_rating(movie['title'])
        if imdb_ratings:
            for rating_type, rating_value in imdb_ratings.items():
                last_snapshot = self.get_last_snapshot(movie['id'], 'IMDb', rating_type)
                
                if not last_snapshot or last_snapshot['rating_value'] != rating_value:
                    snapshot = self.store_snapshot(
                        movie['id'],
                        'IMDb',
                        rating_type,
                        rating_value
                    )
                    if snapshot:
                        snapshots_created += 1
                        print(f"    ✅ IMDb {rating_type}: {rating_value}")
            
            self.log_scrape('IMDb', movie['id'], 'success', snapshots_created=snapshots_created)
        
        # 3. Scrape Metacritic
        time.sleep(1)  # Rate limiting
        mc_ratings = self.scrape_metacritic_rating(movie['title'])
        if mc_ratings:
            for rating_type, rating_value in mc_ratings.items():
                last_snapshot = self.get_last_snapshot(movie['id'], 'Metacritic', rating_type)
                
                if not last_snapshot or last_snapshot['rating_value'] != rating_value:
                    snapshot = self.store_snapshot(
                        movie['id'],
                        'Metacritic',
                        rating_type,
                        rating_value
                    )
                    if snapshot:
                        snapshots_created += 1
                        print(f"    ✅ Metacritic {rating_type}: {rating_value}")
            
            self.log_scrape('Metacritic', movie['id'], 'success', snapshots_created=snapshots_created)
    
    def run_once(self, interval='daily'):
        """Run one monitoring cycle.

        Args:
            interval: 'hourly' or 'daily' - snapshot granularity
        """
        print(f"🔄 Starting rating monitor cycle at {datetime.now()} (interval: {interval})")

        movies = self.get_active_movies(days=30)
        print(f"Found {len(movies)} active movies")

        for movie in movies:
            try:
                self.monitor_movie(movie, interval=interval)
                time.sleep(2)  # Rate limiting between movies
            except Exception as e:
                print(f"  ❌ Error monitoring {movie['title']}: {e}")
                self.log_scrape('RottenTomatoes', movie['id'], 'error', error_message=str(e))

        print(f"✅ Cycle complete\n")

    def run_continuous(self, interval_minutes=60, snapshot_interval='daily'):
        """Run continuous monitoring loop.

        Args:
            interval_minutes: Minutes between monitoring cycles
            snapshot_interval: 'hourly' or 'daily' - snapshot granularity
        """
        print(f"🚀 Starting continuous rating monitor (cycle: {interval_minutes} min, snapshots: {snapshot_interval})")

        while True:
            try:
                self.run_once(interval=snapshot_interval)
                print(f"⏳ Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\n👋 Shutting down rating monitor")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry

    def get_movies_by_age(self, min_days, max_days):
        """Get movies released within a specific age range (days)"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT * FROM movies 
                WHERE release_date <= NOW() - INTERVAL '%s days'
                AND release_date > NOW() - INTERVAL '%s days'
                ORDER BY release_date DESC;
            """
            cur.execute(query, (min_days, max_days))
            return cur.fetchall()

    def run_adaptive(self):
        """Run continuous monitoring with adaptive scheduling based on movie 'freshness'"""
        print("🚀 Starting ADAPTIVE rating monitor")
        print("   - 🔥 Hot (< 7 days): Every 30 mins")
        print("   - 🎬 Active (7-30 days): Every 4 hours")
        print("   - 📚 Archive (> 30 days): Every 24 hours")

        cycle_count = 0
        interval_minutes = 30 # Base heartbeat

        while True:
            try:
                print(f"\n🔄 Cycle {cycle_count} starting at {datetime.now().strftime('%H:%M')}")
                
                # 1. ALWAYS scrape Hot movies (0-7 days old)
                hot_movies = self.get_movies_by_age(0, 7)
                print(f"   🔥 Processing {len(hot_movies)} HOT movies...")
                for movie in hot_movies:
                    self.monitor_movie(movie, interval='hourly')
                
                
                # 2. Active Cycles (7-30 days) - Check every 4 hours (interval=8)
                if cycle_count % 8 == 0:
                    print("  Checking Active Movies...")
                    active_movies = self.get_movies_by_age(7, 30)
                    for movie in active_movies:
                        self.monitor_movie(movie, interval='daily')
                        
                # 3. Archive Cycles (30-90 days) - Check every 24 hours (interval=48)
                if cycle_count % 48 == 0:
                    print("  Checking Archive Movies...")
                    archive_movies = self.get_movies_by_age(30, 90)
                    for movie in archive_movies:
                        self.monitor_movie(movie, interval='daily')

                cycle_count += 1
                print(f"⏳ Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                print("\n👋 Shutting down rating monitor")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Movie Rating Monitor')
    parser.add_argument('--adaptive', action='store_true', help='Run with adaptive scheduling')
    parser.add_argument('--continuous', action='store_true', help='Run continuously (legacy mode)')
    parser.add_argument('--interval', type=int, default=60, help='Minutes between cycles (default: 60)')
    parser.add_argument('--snapshots', choices=['hourly', 'daily'], default='daily',
                        help='Snapshot granularity: hourly or daily (default: daily)')
    args = parser.parse_args()

    monitor = RatingMonitor()

    if args.adaptive:
        monitor.run_adaptive()
    elif args.continuous:
        monitor.run_continuous(interval_minutes=args.interval, snapshot_interval=args.snapshots)
    else:
        # Default run once
        monitor.run_once(interval=args.snapshots)
