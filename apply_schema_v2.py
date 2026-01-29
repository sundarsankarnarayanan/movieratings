import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def apply_schema_v2():
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
            # Read schema_v2.sql
            with open("schema_v2.sql", "r") as f:
                sql = f.read()
                print("Executing schema_v2.sql...")
                cur.execute(sql)
                print("Schema v2 applied successfully.")
                
    except Exception as e:
        print(f"Error applying schema: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    apply_schema_v2()
