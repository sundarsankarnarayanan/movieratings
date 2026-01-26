import sys
from scrapers.rotten_tomatoes import RottenTomatoesScraper
from database import Database

def main():
    db = Database()
    
    # Example for US/EN using Rotten Tomatoes
    print("Fetching top reviewers for US/EN (Rotten Tomatoes)...")
    rt_scraper = RottenTomatoesScraper(region='US', language='EN')
    
    top_reviewers = rt_scraper.get_top_reviewers(limit=10)
    print(f"Found {len(top_reviewers)} reviewers.")
    
    for r_data in top_reviewers:
        print(f"Processing reviewer: {r_data['name']}")
        reviewer = db.upsert_reviewer(r_data)
        
        if reviewer:
            print(f"Fetching reviews for {r_data['name']}...")
            reviews = rt_scraper.get_latest_reviews(r_data['external_url'])
            for rev in reviews:
                rev['reviewer_id'] = reviewer['id']
                db.insert_review(rev)
            print(f"Stored {len(reviews)} reviews.")

if __name__ == "__main__":
    main()
