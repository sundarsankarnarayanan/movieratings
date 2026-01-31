import sys
from datetime import datetime, timedelta
from tmdb_client import TMDBClient
from database import Database

def movie_release_agent():
    tmdb = TMDBClient()
    db = Database()
    
    # Calculate yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"Fetching global releases for date: {yesterday}")
    
    # Top 12 Movie Markets
    regions = [
        {'code': 'US', 'lang': 'en'}, # United States
        {'code': 'GB', 'lang': 'en'}, # United Kingdom
        {'code': 'FR', 'lang': 'fr'}, # France
        {'code': 'IN', 'lang': 'hi'}, # India
        {'code': 'ES', 'lang': 'es'}, # Spain
        {'code': 'DE', 'lang': 'de'}, # Germany
        {'code': 'JP', 'lang': 'ja'}, # Japan
        {'code': 'KR', 'lang': 'ko'}, # South Korea
        {'code': 'CN', 'lang': 'zh'}, # China
        {'code': 'BR', 'lang': 'pt'}, # Brazil
        {'code': 'MX', 'lang': 'es'}, # Mexico
        {'code': 'IT', 'lang': 'it'}  # Italy
    ]
    
    total_new_movies = 0
    
    for r in regions:
        print(f"Processing Region: {r['code']} ({r['lang']})...")
        movies = tmdb.get_movies_by_date(yesterday, r_region=r['code'], r_language=r['lang'])
        
        count = 0
        for m in movies:
            # 1. Upsert Movie (Base Data)
            # Default scoring for trending = popularity
            trending_score = m.get("popularity", 0)
            
            # Generate slug
            import re
            slug = re.sub(r'[^a-z0-9]+', '_', m.get("title", "").lower()).strip('_')
            release_year = m.get("release_date", "0000")[:4]
            slug = f"{slug}-{release_year}"
            
            movie_data = {
                "slug": slug,
                "title": m.get("title"),
                "original_title": m.get("original_title"),
                "release_date": m.get("release_date"), # Global/Primary release date
                "regions": [r['code']], 
                "original_language": r['lang'],
                "overview": m.get("overview"),
                "poster_url": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else None,
                "backdrop_url": f"https://image.tmdb.org/t/p/original{m.get('backdrop_path')}" if m.get('backdrop_path') else None,
                "runtime": m.get("runtime")
            }
            stored_movie = db.upsert_movie(movie_data)
            
            if stored_movie:
                # 2. Upsert Region Specific Entry
                region_data = {
                    "movie_id": stored_movie['id'],
                    "region_code": r['code'],
                    "release_date": m.get("release_date") or yesterday
                }
                db.upsert_movie_region(region_data)
                count += 1
                
        print(f"  - Upserted {count} movies for {r['code']}.")
        total_new_movies += count

    print(f"Global fetch complete. Processed {total_new_movies} region-entries.")

if __name__ == "__main__":
    movie_release_agent()
