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
            
            # Extract ratings (expanded selectors for modern RT)
            tomatometer = movie_soup.select_one('rt-text[slot="criticsScore"], [data-qa="tomatometer"]')
            audience_score = movie_soup.select_one('rt-text[slot="audienceScore"], [data-qa="audience-score"]')
            
            ratings = {}
            
            if tomatometer:
                score_text = tomatometer.text.strip().replace('%', '')
                try:
                    ratings['tomatometer'] = float(score_text)
                except Exception as e:
                    print(f"      Failed to parse tomatometer '{score_text}': {e}")
            
            if audience_score:
                score_text = audience_score.text.strip().replace('%', '')
                try:
                    ratings['audience'] = float(score_text)
                except Exception as e:
                    print(f"      Failed to parse audience score '{score_text}': {e}")
            
            # Also try to extract review counts
            review_counts = self.scrape_review_counts(movie_soup)
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
                    movie_id, source, rating_type, rating_value, review_count
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (movie_id, source, rating_type, snapshot_time) DO NOTHING
                RETURNING *;
            """
            
            cur.execute(query, (movie_id, source, rating_type, rating_value, review_count))
            return cur.fetchone()
    
    def store_daily_snapshot(self, movie_id, source, ratings, review_counts):
        """Store daily review snapshot for trend analysis"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            from datetime import date
            
            # Get yesterday's snapshot for comparison
            yesterday_query = """
                SELECT * FROM daily_review_snapshots
                WHERE movie_id = %s AND source = %s
                AND snapshot_date = CURRENT_DATE - INTERVAL '1 day'
                LIMIT 1;
            """
            cur.execute(yesterday_query, (movie_id, source))
            yesterday = cur.fetchone()
            
            # Calculate metrics
            total_reviews = review_counts.get('critic_reviews', 0) + review_counts.get('audience_reviews', 0)
            new_reviews_today = 0
            score_change = 0.0
            
            if yesterday:
                new_reviews_today = total_reviews - (yesterday['total_reviews'] or 0)
                if yesterday['critic_score'] and ratings.get('tomatometer'):
                    score_change = ratings['tomatometer'] - yesterday['critic_score']
            
            # Calculate velocity (reviews per day since release)
            days_query = "SELECT EXTRACT(DAY FROM NOW() - release_date)::INTEGER as days FROM movies WHERE id = %s;"
            cur.execute(days_query, (movie_id,))
            days_result = cur.fetchone()
            days_since_release = max(days_result['days'] if days_result else 1, 1)
            review_velocity = total_reviews / days_since_release
            
            # Store snapshot
            insert_query = """
                INSERT INTO daily_review_snapshots (
                    movie_id, source, snapshot_date,
                    total_reviews, new_reviews_today,
                    critic_score, audience_score,
                    review_velocity, score_change
                ) VALUES (%s, %s, CURRENT_DATE, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (movie_id, source, snapshot_date) 
                DO UPDATE SET
                    total_reviews = EXCLUDED.total_reviews,
                    new_reviews_today = EXCLUDED.new_reviews_today,
                    critic_score = EXCLUDED.critic_score,
                    audience_score = EXCLUDED.audience_score,
                    review_velocity = EXCLUDED.review_velocity,
                    score_change = EXCLUDED.score_change
                RETURNING *;
            """
            
            cur.execute(insert_query, (
                movie_id, source, total_reviews, new_reviews_today,
                ratings.get('tomatometer'), ratings.get('audience'),
                review_velocity, score_change
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
    
    def monitor_movie(self, movie):
        """Monitor a single movie for rating changes from all sources"""
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
            
            # Store daily snapshot
            if review_counts:
                try:
                    daily_snapshot = self.store_daily_snapshot(
                        movie['id'],
                        'RottenTomatoes',
                        rt_ratings,
                        review_counts
                    )
                    if daily_snapshot:
                        print(f"    📊 Daily snapshot: {daily_snapshot['total_reviews']} reviews (+{daily_snapshot['new_reviews_today']} today)")
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
    
    def run_once(self):
        """Run one monitoring cycle"""
        print(f"🔄 Starting rating monitor cycle at {datetime.now()}")
        
        movies = self.get_active_movies(days=30)
        print(f"Found {len(movies)} active movies")
        
        for movie in movies:
            try:
                self.monitor_movie(movie)
                time.sleep(2)  # Rate limiting between movies
            except Exception as e:
                print(f"  ❌ Error monitoring {movie['title']}: {e}")
                self.log_scrape('RottenTomatoes', movie['id'], 'error', error_message=str(e))
        
        print(f"✅ Cycle complete\n")
    
    def run_continuous(self, interval_minutes=60):
        """Run continuous monitoring loop"""
        print(f"🚀 Starting continuous rating monitor (interval: {interval_minutes} min)")
        
        while True:
            try:
                self.run_once()
                print(f"⏳ Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\n👋 Shutting down rating monitor")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry

if __name__ == "__main__":
    import sys
    
    monitor = RatingMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor.run_continuous(interval_minutes=interval)
    else:
        monitor.run_once()
