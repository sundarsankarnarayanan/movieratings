"""
Alternative Release Tracker - Web Scraping Based
Scrapes movie releases from Rotten Tomatoes instead of TMDb API
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import re

load_dotenv()

class WebScrapingReleaseTracker:
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

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # TMDB API for poster images
        self.tmdb_api_key = os.environ.get("TMDB_API_KEY")
        self.tmdb_base_url = "https://api.themoviedb.org/3"
    
    def scrape_rt_new_releases(self):
        """Scrape new releases from Rotten Tomatoes"""
        movies = []

        # Try opening this week page
        url = "https://www.rottentomatoes.com/browse/movies_in_theaters/"

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find movie tiles using the correct selector for browse page
            # Use search-page-media-row or tile elements, not generic /m/ links
            movie_elements = soup.select('a[data-qa="discovery-media-list-item-title"], tile-dynamic a[href*="/m/"]')

            seen_titles = set()
            for element in movie_elements[:30]:  # Get first 30 movies
                movie_url = element.get('href', '')

                if not movie_url:
                    continue

                if not movie_url.startswith('http'):
                    movie_url = f"https://www.rottentomatoes.com{movie_url}"

                # Extract title
                title = element.text.strip() if element.text else ""

                if not title:
                    # Fallback to image alt
                    img = element.select_one('rt-img, img')
                    title = img.get('alt', '').strip() if img else ""

                # Cleanup title
                title = re.sub(r'^\s*\d+%\s*', '', title).strip()
                title = re.sub(r'\s+(Opened|Opens|Re-released).*$', '', title, flags=re.DOTALL | re.IGNORECASE).strip()
                title = re.sub(r'\s+poster\s+image\s*$', '', title, flags=re.IGNORECASE).strip()
                title = ' '.join(title.split())

                if not title:
                    # Extract from URL
                    title = movie_url.split('/m/')[-1].replace('_', ' ').title()

                # Skip duplicates by title
                if title and len(title) > 2 and title not in seen_titles:
                    seen_titles.add(title)
                    movies.append({
                        'title': title,
                        'url': movie_url,
                        'source': 'RottenTomatoes'
                    })

            print(f"Found {len(movies)} unique movies from RT")
            return movies

        except Exception as e:
            print(f"Error scraping RT: {e}")
            return []
    
    def get_tmdb_poster(self, movie_title, release_year=None):
        """Get poster URL from TMDB API"""
        if not self.tmdb_api_key:
            return None

        try:
            # Search for movie on TMDB
            search_url = f"{self.tmdb_base_url}/search/movie"
            params = {
                "api_key": self.tmdb_api_key,
                "query": movie_title
            }
            if release_year:
                params["year"] = release_year

            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            results = response.json().get("results", [])

            if results:
                # Get first result's poster
                poster_path = results[0].get("poster_path")
                backdrop_path = results[0].get("backdrop_path")

                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else None

                return {
                    'poster_url': poster_url,
                    'backdrop_url': backdrop_url,
                    'tmdb_id': results[0].get("id")
                }
        except Exception as e:
            print(f"    Error fetching TMDB poster: {e}")

        return None

    def scrape_movie_details(self, movie_url, movie_title):
        """Scrape detailed info from a movie page"""
        import json

        try:
            response = requests.get(movie_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            details = {}

            # Try to find release date
            release_elem = soup.find(string=re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d{4}'))
            if release_elem:
                details['release_date'] = release_elem.strip()

            # POSTER EXTRACTION - Multiple methods for reliability
            poster_url = None

            # Method 1: JSON-LD schema (most reliable, unique per movie)
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'Movie' and data.get('image'):
                        poster_url = data['image']
                        print(f"    ✅ Got poster from JSON-LD")
                        break
                except:
                    pass

            # Method 2: og:image meta tag
            if not poster_url:
                og_image = soup.select_one('meta[property="og:image"]')
                if og_image and og_image.get('content'):
                    poster_url = og_image['content']
                    print(f"    ✅ Got poster from og:image")

            # Method 3: Fallback to rt-img with movie title in alt
            if not poster_url:
                # Look for poster image matching movie title
                for img in soup.select('rt-img'):
                    alt = img.get('alt', '').lower()
                    if 'poster' in alt and movie_title.lower().split()[0] in alt:
                        src = img.get('src') or img.get('srcset', '').split(',')[0].split(' ')[0]
                        if src and 'flixster' in src:
                            poster_url = src
                            print(f"    ✅ Got poster from rt-img")
                            break

            if poster_url:
                details['poster_url'] = poster_url
            else:
                print(f"    ⚠️ No poster found")

            # Try to find genre
            genre_elems = soup.select('[data-qa="movie-info-item-value"]')
            if genre_elems:
                details['genres'] = [g.text.strip() for g in genre_elems[:3]]

            # Try to find overview/synopsis
            overview = soup.select_one('[data-qa="movie-info-synopsis"], .movie_synopsis')
            if overview:
                details['overview'] = overview.text.strip()

            return details

        except Exception as e:
            print(f"  Error scraping details: {e}")
            return {}
    
    def parse_release_date(self, date_str):
        """Parse various date formats"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try common formats
            for fmt in ['%b %d, %Y', '%B %d, %Y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                except:
                    continue
        except:
            pass
        
        # Default to today
        return datetime.now().strftime('%Y-%m-%d')
    
    def store_movie(self, movie_data):
        """Store movie in database"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Use TMDB ID if available, otherwise generate from hash
            tmdb_id = movie_data.get('tmdb_id') or (abs(hash(movie_data['title'])) % 1000000)

            query = """
                INSERT INTO movies (
                    tmdb_id, title, release_date, genres, regions,
                    poster_url, backdrop_url, overview
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tmdb_id) DO UPDATE SET
                    poster_url = EXCLUDED.poster_url,
                    backdrop_url = EXCLUDED.backdrop_url,
                    updated_at = NOW()
                RETURNING *;
            """

            cur.execute(query, (
                tmdb_id,
                movie_data['title'],
                movie_data.get('release_date', datetime.now().strftime('%Y-%m-%d')),
                movie_data.get('genres', []),
                movie_data.get('regions', ['US']),
                movie_data.get('poster_url'),
                movie_data.get('backdrop_url'),
                movie_data.get('overview')
            ))

            return cur.fetchone()
    
    def initialize_snapshots(self, movie_id):
        """Create initial rating snapshots"""
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO rating_snapshots (
                    movie_id, source, rating_type, rating_value, review_count
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (movie_id, source, rating_type, snapshot_time) DO NOTHING;
            """
            
            # Initialize with 0 - rating monitor will update
            cur.execute(query, (movie_id, 'RottenTomatoes', 'tomatometer', 0.0, 0))
    
    def run(self):
        """Main execution"""
        print("🎬 Scraping movie releases from web sources...")
        
        # Scrape from Rotten Tomatoes
        movies = self.scrape_rt_new_releases()
        
        if not movies:
            print("❌ No movies found. Trying alternative approach...")
            # Add some sample movies for demo
            movies = [
                {'title': 'Nosferatu', 'url': 'https://www.rottentomatoes.com/m/nosferatu_2024', 'source': 'RT'},
                {'title': 'Wicked', 'url': 'https://www.rottentomatoes.com/m/wicked_2024', 'source': 'RT'},
                {'title': 'Mufasa: The Lion King', 'url': 'https://www.rottentomatoes.com/m/mufasa_the_lion_king', 'source': 'RT'},
                {'title': 'Sonic the Hedgehog 3', 'url': 'https://www.rottentomatoes.com/m/sonic_the_hedgehog_3', 'source': 'RT'},
                {'title': 'A Complete Unknown', 'url': 'https://www.rottentomatoes.com/m/a_complete_unknown', 'source': 'RT'},
            ]
        
        stored_count = 0
        for movie in movies[:20]:  # Limit to 20 to avoid rate limiting
            try:
                print(f"\nProcessing: {movie['title']}")

                # Scrape details (now includes TMDB lookup)
                details = self.scrape_movie_details(movie['url'], movie['title'])
                time.sleep(1)  # Rate limiting

                # Merge data
                movie_data = {
                    'title': movie['title'],
                    'tmdb_id': details.get('tmdb_id'),
                    'release_date': self.parse_release_date(details.get('release_date')),
                    'genres': details.get('genres', []),
                    'regions': ['US'],
                    'poster_url': details.get('poster_url'),
                    'backdrop_url': details.get('backdrop_url'),
                    'overview': details.get('overview', f"Movie: {movie['title']}")
                }

                if movie_data['poster_url']:
                    print(f"  ✅ Found poster: {movie_data['poster_url'][:50]}...")
                else:
                    print(f"  ⚠️ No poster found for {movie['title']}")

                # Store
                stored_movie = self.store_movie(movie_data)
                if stored_movie:
                    self.initialize_snapshots(stored_movie['id'])
                    stored_count += 1
                    print(f"  ✅ Stored: {stored_movie['title']}")

            except Exception as e:
                print(f"  ❌ Error processing {movie['title']}: {e}")
        
        print(f"\n✅ Successfully stored {stored_count} movies")
        self.conn.close()

if __name__ == "__main__":
    tracker = WebScrapingReleaseTracker()
    tracker.run()
