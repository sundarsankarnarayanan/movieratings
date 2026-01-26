"""
Agent 1: Daily Release Tracker
Fetches all new movie releases globally from TMDb API
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

class ReleaseTracker:
    def __init__(self):
        self.tmdb_api_key = os.environ.get("TMDB_API_KEY")
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        
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
    
    def fetch_releases(self, date, regions=None):
        """Fetch movies released on a specific date across regions"""
        if regions is None:
            regions = ['US', 'GB', 'FR', 'IN', 'ES', 'DE', 'JP', 'KR', 'CN', 'BR', 'MX', 'IT', 
                      'CA', 'AU', 'RU', 'IT', 'NL', 'SE', 'NO', 'DK']
        
        all_movies = {}
        
        for region in regions:
            url = f"{self.tmdb_base_url}/discover/movie"
            params = {
                'api_key': self.tmdb_api_key,
                'region': region,
                'primary_release_date.gte': date,
                'primary_release_date.lte': date,
                'sort_by': 'popularity.desc'
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for movie in data.get('results', []):
                    tmdb_id = movie['id']
                    
                    # Aggregate regions for the same movie
                    if tmdb_id not in all_movies:
                        all_movies[tmdb_id] = {
                            'movie': movie,
                            'regions': set()
                        }
                    all_movies[tmdb_id]['regions'].add(region)
                    
            except Exception as e:
                print(f"Error fetching {region}: {e}")
                continue
        
        return all_movies
    
    def enrich_movie_metadata(self, tmdb_id):
        """Fetch detailed metadata for a movie"""
        url = f"{self.tmdb_base_url}/movie/{tmdb_id}"
        params = {'api_key': self.tmdb_api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error enriching movie {tmdb_id}: {e}")
            return None
    
    def store_movie(self, movie_data, regions):
        """Store movie in database"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get detailed metadata
            details = self.enrich_movie_metadata(movie_data['id'])
            if not details:
                return None
            
            genres = [g['name'] for g in details.get('genres', [])]
            
            query = """
                INSERT INTO movies (
                    tmdb_id, title, original_title, release_date, 
                    genres, regions, poster_url, backdrop_url, overview, runtime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tmdb_id) DO UPDATE SET
                    regions = EXCLUDED.regions,
                    updated_at = NOW()
                RETURNING *;
            """
            
            poster_url = f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get('poster_path') else None
            backdrop_url = f"https://image.tmdb.org/t/p/original{details['backdrop_path']}" if details.get('backdrop_path') else None
            
            cur.execute(query, (
                details['id'],
                details['title'],
                details.get('original_title'),
                details.get('release_date'),
                genres,
                list(regions),
                poster_url,
                backdrop_url,
                details.get('overview'),
                details.get('runtime')
            ))
            
            return cur.fetchone()
    
    def initialize_snapshots(self, movie_id):
        """Create initial rating snapshots for a new movie"""
        with self.conn.cursor() as cur:
            # Initialize with placeholder values (will be updated by rating monitor)
            sources = ['RottenTomatoes', 'Metacritic', 'IMDb']
            
            for source in sources:
                query = """
                    INSERT INTO rating_snapshots (
                        movie_id, source, rating_type, rating_value, review_count
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (movie_id, source, rating_type, snapshot_time) DO NOTHING;
                """
                
                # Initialize with 0 values - rating monitor will update
                cur.execute(query, (movie_id, source, 'critic', 0.0, 0))
    
    def run(self, date=None):
        """Main execution"""
        if date is None:
            # Default to yesterday
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🎬 Fetching releases for {date}...")
        movies = self.fetch_releases(date)
        
        print(f"Found {len(movies)} unique movies across all regions")
        
        stored_count = 0
        for tmdb_id, data in movies.items():
            try:
                stored_movie = self.store_movie(data['movie'], data['regions'])
                if stored_movie:
                    self.initialize_snapshots(stored_movie['id'])
                    stored_count += 1
                    print(f"  ✅ {stored_movie['title']} ({', '.join(data['regions'])})")
            except Exception as e:
                print(f"  ❌ Error storing movie {tmdb_id}: {e}")
        
        print(f"\n✅ Stored {stored_count} movies")
        
        self.conn.close()

if __name__ == "__main__":
    tracker = ReleaseTracker()
    tracker.run()
