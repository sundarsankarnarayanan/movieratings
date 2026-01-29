import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from langdetect import detect, LangDetectException

load_dotenv()

class ReviewScraper:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "127.0.0.1"),
            port=os.environ.get("DB_PORT", "54322"),
            database=os.environ.get("DB_NAME", "postgres"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres")
        )
        self.conn.autocommit = True
        
        with self.conn.cursor() as cur:
            cur.execute("SET search_path TO movie_platform;")

    def get_movies_to_scrape(self, limit=20):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT id, title, release_date 
                FROM movies 
                WHERE release_date >= NOW() - INTERVAL '1 year'
                ORDER BY release_date DESC
                LIMIT %s;
            """
            cur.execute(query, (limit,))
            return cur.fetchall()

    def scrape_with_playwright(self, movies):
        total_stored = 0
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            for movie in movies:
                print(f"\nProcessing {movie['title']}...")
                try:
                    # 1. Search for Movie URL on RT
                    search_query = movie['title'].replace(' ', '%20')
                    page.goto(f"https://www.rottentomatoes.com/search?search={search_query}")
                    
                    # Wait for results
                    try:
                        movie_link = page.wait_for_selector('search-page-result[type="movie"] a', timeout=5000)
                        if not movie_link:
                             # fallback
                             movie_link = page.wait_for_selector('a[href*="/m/"]', timeout=3000)
                    except:
                        print("    ⚠️ Could not find movie in search results")
                        continue

                    if not movie_link:
                        continue

                    href = movie_link.get_attribute('href')
                    if not href:
                        continue
                        
                    full_url = href if href.startswith('http') else f"https://www.rottentomatoes.com{href}"
                    print(f"    Found URL: {full_url}")

                    # 2. Scrape (Mocking User Reviews via Critic Page or Audience Page)
                    # Let's try Audience reviews
                    reviews_url = f"{full_url}/reviews?type=user"
                    page.goto(reviews_url)
                    
                    # Wait for review cards (using custom tag logic or class)
                    # RT uses 'review-card' often now, or just look for text containers
                    try:
                        page.wait_for_selector('[class*="review-text"], [data-qa="review-text"]', timeout=5000)
                    except:
                        print("    ⚠️ No reviews loaded (timeout)")
                        pass

                    # Extract Reviews
                    reviews_data = page.evaluate("""() => {
                        const reviews = [];
                        // Select all review containers
                        const cards = document.querySelectorAll('review-card, .audience-review-row, .review-row');
                        
                        cards.forEach(card => {
                            const author = card.querySelector('[data-qa="review-critic-link"], .display-name, .audience-reviews__name')?.innerText.trim() || "Anonymous";
                            const content = card.querySelector('[data-qa="review-quote"], .review-text, .audience-reviews__review')?.innerText.trim();
                            const dateStr = card.querySelector('[data-qa="review-date"], .review-date, .audience-reviews__duration')?.innerText.trim();
                            
                            // Rating
                            let rating = "Neutral";
                            if (card.querySelector('[class*="icon-fresh"]')) rating = "Fresh";
                            if (card.querySelector('[class*="icon-rotten"]')) rating = "Rotten";
                            const stars = card.querySelectorAll('.star-display .star-full').length;
                            if (stars > 0) rating = stars + "/5";

                            if (content) {
                                reviews.push({
                                    source: "RottenTomatoes (Audience)",
                                    author,
                                    content,
                                    date_str: dateStr,
                                    rating,
                                    language: 'en' // Default
                                });
                            }
                        });
                        return reviews;
                    }""")
                    
                    print(f"    Found {len(reviews_data)} reviews")
                    
                    # Store
                    stored_count = self.store_reviews(movie['id'], reviews_data)
                    print(f"    ✅ Stored {stored_count} new reviews")
                    total_stored += stored_count

                except Exception as e:
                    print(f"    ❌ Error scraping {movie['title']}: {e}")

            browser.close()
        return total_stored



    def store_reviews(self, movie_id, reviews):
        count = 0
        with self.conn.cursor() as cur:
            for review in reviews:
                # Parse date logic here or in SQL
                r_date = datetime.now().date()
                if review['date_str']:
                    try:
                        # Try parsing various formats
                        for fmt in ['%b %d, %Y', '%B %d, %Y', '%m/%d/%y']:
                             try:
                                 r_date = datetime.strptime(review['date_str'], fmt).date()
                                 break
                             except: pass
                    except: pass


                # Language Detection
                lang = review['language']
                if review['content']:
                    try:
                        lang = detect(review['content'])
                    except LangDetectException:
                        pass

                try:
                    cur.execute("""
                        INSERT INTO reviews (
                            movie_id, source, author_name, rating, content, 
                            language, review_date, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (source, movie_id, author_name, review_date) 
                        DO NOTHING
                        RETURNING id;
                    """, (
                        movie_id, 
                        review['source'], 
                        review['author'], 
                        review['rating'], 
                        review['content'],
                        lang, 
                        r_date
                    ))
                    if cur.fetchone():
                        count += 1
                except Exception:
                    continue
        return count

    def run(self):
        print("🕷️ Starting Playwright Review Scraper...")
        movies = self.get_movies_to_scrape()
        self.scrape_with_playwright(movies)
        self.conn.close()

if __name__ == "__main__":
    scraper = ReviewScraper()
    scraper.run()
