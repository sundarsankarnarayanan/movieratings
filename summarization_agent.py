from database import Database
from llm_client import LLMClient
import time

def summarization_agent():
    db = Database()
    llm = LLMClient()
    
    print("Fetching movies pending summarization...")
    # Get top 10 popular movies without summaries
    movies_to_process = db.get_movies_for_summarization(limit=10)
    
    if not movies_to_process:
        print("No pending movies found.")
        return

    print(f"Found {len(movies_to_process)} movies to summarize.")
    
    for movie in movies_to_process:
        tmdb_id = movie['tmdb_id']
        title = movie['title']
        
        print(f"Processing '{title}' (ID: {tmdb_id})...")
        
        # Fetch reviews for this movie
        # Note: Using get_movie_reviews logic which relies on title matching for now
        # Ideally, we should fetch by ID if our scraping linked them correctly.
        # Given the current scraper structure, we'll try to fetch by ID first if supported,
        # but our database.get_movie_reviews uses ID to find title then looks up reviews.
        # So we can use that.
        reviews = db.get_movie_reviews(tmdb_id)
        
        if not reviews:
            print(f"  - No reviews found for '{title}'. Skipping.")
            continue
            
        # Combine review content
        reviews_text = "\n".join([f"- {r['content']}" for r in reviews[:20]]) # Limit to 20 reviews context
        
        if not reviews_text:
            print("  - Empty review content.")
            continue
            
        print(f"  - Generating summary from {len(reviews)} reviews...")
        pos, neg = llm.summarize_reviews(title, reviews_text)
        
        db.update_movie_summary(tmdb_id, pos, neg)
        print(f"  - Summary updated for '{title}'.")
        
        # Respect rate limits if needed
        time.sleep(1)

if __name__ == "__main__":
    summarization_agent()
