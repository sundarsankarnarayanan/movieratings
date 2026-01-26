from scrapers.rotten_tomatoes import RottenTomatoesScraper
import json

def verify_scrapers():
    print("=== Scraper Verification Tool ===")
    
    # 1. Test Rotten Tomatoes
    print("\n[1/2] Testing Rotten Tomatoes Scraper...")
    rt = RottenTomatoesScraper()
    
    print("  - Fetching top critics...")
    critics = rt.get_top_reviewers(limit=3)
    
    if not critics:
        print("  ❌ UNABLE TO FIND CRITICS. Check URL/Selectors.")
        return
        
    print(f"  ✅ Found {len(critics)} critics.")
    for c in critics:
        print(f"    - {c['name']} ({c['external_url']})")
        
    # 2. Test Review Fetching for the first critic
    target_critic = critics[0]
    print(f"\n[2/2] Testing Review Fetching for {target_critic['name']}...")
    reviews = rt.get_latest_reviews(target_critic['external_url'])
    
    if not reviews:
        print("  ❌ UNABLE TO FIND REVIEWS. Check Profile URL/Selectors.")
        print(f"     URL tested: {target_critic['external_url']}")
    else:
        print(f"  ✅ Found {len(reviews)} reviews.")
        for r in reviews[:2]:
            print(f"    - [{r['rating']}] {r['movie_title']}: {r['content'][:50]}...")

if __name__ == "__main__":
    verify_scrapers()
