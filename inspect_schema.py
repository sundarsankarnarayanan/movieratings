import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST", "127.0.0.1"),
    port=os.environ.get("DB_PORT", "54322"),
    database=os.environ.get("DB_NAME", "postgres"),
    user=os.environ.get("DB_USER", "postgres"),
    password=os.environ.get("DB_PASSWORD", "postgres")
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute("SET search_path TO movie_platform;")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'movie_platform' 
        AND table_name = 'daily_review_snapshots';
    """)
    columns = cur.fetchall()
    print("Columns in daily_review_snapshots:")
    for col in columns:
        print(f" - {col[0]} ({col[1]})")
conn.close()
