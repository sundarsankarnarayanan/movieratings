import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def verify():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=os.environ.get("DB_PORT", "54322"),
        database=os.environ.get("DB_NAME", "postgres"),
        user="postgres",
        password="postgres"
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SET search_path TO movie_platform;")
        
        # Check Movies
        cur.execute("SELECT count(*) as c FROM movies;")
        print(f"Movies: {cur.fetchone()['c']}")
        
        # Check Movies with Language
        cur.execute("SELECT original_language, count(*) as c FROM movies GROUP BY original_language;")
        print(f"Languages: {cur.fetchall()}")

        # Check Snapshots
        cur.execute("SELECT count(*) as c FROM rating_snapshots;")
        print(f"Snapshots: {cur.fetchone()['c']}")
        
        # Check Daily Snapshots
        cur.execute("SELECT count(*) as c FROM daily_review_snapshots;")
        print(f"Daily Snapshots: {cur.fetchone()['c']}")
        
        # Check Reviews
        cur.execute("SELECT count(*) as c FROM reviews;")
        print(f"Reviews: {cur.fetchone()['c']}")

    conn.close()

if __name__ == "__main__":
    verify()
