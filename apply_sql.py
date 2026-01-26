import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def setup_db():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "127.0.0.1"),
            port=os.environ.get("DB_PORT", "54322"),
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres")
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            with open("setup_schema.sql", "r") as f:
                sql = f.read()
                print("Executing setup_schema.sql...")
                cur.execute(sql)
                print("Schema and tables created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_db()
