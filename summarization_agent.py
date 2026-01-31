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
        slug = movie['slug']
        title = movie['title']
        
        print(f"Processing '{title}' (Slug: {slug})...")
        
        # Fetch reviews for this movie
        reviews = db.get_movie_reviews(slug)
        
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
        
        db.update_movie_summary(slug, pos, neg)
        print(f"  - Summary updated for '{title}'.")
        
        # Respect rate limits if needed
        time.sleep(1)

if __name__ == "__main__":
    summarization_agent()
