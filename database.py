import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "127.0.0.1"),
                port=os.environ.get("DB_PORT", "5432"),
                database=os.environ.get("DB_NAME", "postgres"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", "postgres")
            )
            self.conn.autocommit = True
            with self.conn.cursor() as cur:
                cur.execute("SET search_path TO movie_platform;")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def upsert_reviewer(self, reviewer_data):
        if not self.conn: return None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                INSERT INTO reviewers (name, region, language, source, external_url)
                VALUES (%(name)s, %(region)s, %(language)s, %(source)s, %(external_url)s)
                ON CONFLICT (external_url) DO UPDATE SET
                    name = EXCLUDED.name,
                    region = EXCLUDED.region,
                    language = EXCLUDED.language,
                    source = EXCLUDED.source
                RETURNING *;
            """
            cur.execute(query, reviewer_data)
            return cur.fetchone()

    def insert_review(self, review_data):
        if not self.conn: return
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO reviews (reviewer_id, movie_title, rating, content, review_date, source_url)
                VALUES (%(reviewer_id)s, %(movie_title)s, %(rating)s, %(content)s, %(review_date)s, %(source_url)s);
            """
            cur.execute(query, review_data)

    def upsert_movie(self, movie_data):
        if not self.conn: return None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                INSERT INTO movies (tmdb_id, title, original_title, release_date, region, language, overview, vote_average, vote_count, popularity, poster_path, backdrop_path, genre_ids, adult, video, trending_score)
                VALUES (%(tmdb_id)s, %(title)s, %(original_title)s, %(release_date)s, %(region)s, %(language)s, %(overview)s, %(vote_average)s, %(vote_count)s, %(popularity)s, %(poster_path)s, %(backdrop_path)s, %(genre_ids)s, %(adult)s, %(video)s, %(trending_score)s)
                ON CONFLICT (tmdb_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    vote_average = EXCLUDED.vote_average,
                    vote_count = EXCLUDED.vote_count,
                    popularity = EXCLUDED.popularity,
                    trending_score = EXCLUDED.trending_score
                RETURNING *;
            """
            cur.execute(query, movie_data)
            return cur.fetchone()

    def upsert_movie_region(self, region_data):
        if not self.conn: return None
        # Handle the UNIQUE(movie_id, region_code) constraint
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                INSERT INTO movie_regions (movie_id, region_code, release_date)
                VALUES (%(movie_id)s, %(region_code)s, %(release_date)s)
                ON CONFLICT (movie_id, region_code) DO UPDATE SET
                    release_date = EXCLUDED.release_date
                RETURNING *;
            """
            cur.execute(query, region_data)
            return cur.fetchone()

    def get_movies_for_summarization(self, limit=10):
        if not self.conn: return []
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM movies WHERE ai_summary_positive IS NULL ORDER BY popularity DESC LIMIT %s;"
            cur.execute(query, (limit,))
            return cur.fetchall()

    def update_movie_summary(self, tmdb_id, positive_summary, negative_summary):
        if not self.conn: return
        with self.conn.cursor() as cur:
            query = "UPDATE movies SET ai_summary_positive = %s, ai_summary_negative = %s WHERE tmdb_id = %s;"
            cur.execute(query, (positive_summary, negative_summary, tmdb_id))

    def list_movies(self, region=None, language=None, title_query=None):
        if not self.conn: return []
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = "SELECT * FROM movies WHERE 1=1"
            params = []
            if region:
                query += " AND region = %s"
                params.append(region)
            if language:
                query += " AND language = %s"
                params.append(language)
            if title_query:
                query += " AND title ILIKE %s"
                params.append(f"%{title_query}%")
            cur.execute(query, params)
            return cur.fetchall()

    def get_movie_reviews(self, tmdb_id):
        if not self.conn: return []
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First get movie title
            cur.execute("SELECT title FROM movies WHERE tmdb_id = %s;", (tmdb_id,))
            movie = cur.fetchone()
            if not movie: return []
            title = movie['title']

            # Join with reviewers to get name
            query = """
                SELECT r.*, rev.name as reviewer_name 
                FROM reviews r
                JOIN reviewers rev ON r.reviewer_id = rev.id
                WHERE r.movie_title = %s;
            """
            cur.execute(query, (title,))
            results = cur.fetchall()
            # Format to match previous Realtime API structure roughly
            for r in results:
                r['reviewers'] = {'name': r['reviewer_name']}
            return results

    def get_movie_stats(self, movie_title):
        if not self.conn: return {"count": 0, "fresh_score": 0}
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT rating FROM reviews WHERE movie_title = %s;", (movie_title,))
            rows = cur.fetchall()
            if not rows: return {"count": 0, "fresh_score": 0}
            
            count = len(rows)
            fresh_count = sum(1 for r in rows if r['rating'] == 'Fresh')
            score = (fresh_count / count) * 100 if count > 0 else 0
            return {"count": count, "fresh_score": score}

    def get_reviewer_by_url(self, external_url):
        if not self.conn: return None
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM reviewers WHERE external_url = %s;", (external_url,))
            return cur.fetchone()
