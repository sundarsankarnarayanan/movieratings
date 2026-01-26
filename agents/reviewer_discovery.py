"""
Agent 2: Reviewer Discovery
Builds and maintains database of top reviewers per region
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time

load_dotenv()

class ReviewerDiscovery:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD")
        )
        self.conn.autocommit = True
        
        with self.conn.cursor() as cur:
            cur.execute("SET search_path TO movie_platform;")
    
    def scrape_rotten_tomatoes_critics(self):
        """Scrape top critics from Rotten Tomatoes"""
        url = "https://editorial.rottentomatoes.com/otg-article/top-critics-list/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            critic_links = soup.select('a[href*="/critic/"]')
            reviewers = []
            
            for link in critic_links[:50]:  # Top 50 critics
                name = link.text.strip()
                profile_url = link['href']
                
                if not profile_url.startswith('http'):
                    profile_url = f"https://www.rottentomatoes.com{profile_url}"
                
                if name and "/critic/" in profile_url:
                    reviewers.append({
                        'name': name,
                        'platform': 'RottenTomatoes',
                        'region': 'US',  # Default, can be enhanced
                        'profile_url': profile_url,
                        'influence_score': 0.8  # Top critics get high score
                    })
            
            return reviewers
        except Exception as e:
            print(f"Error scraping RT critics: {e}")
            return []
    
    def store_reviewer(self, reviewer_data):
        """Store or update reviewer in database"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                INSERT INTO reviewers (
                    name, platform, region, profile_url, influence_score, last_scraped_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (profile_url) DO UPDATE SET
                    influence_score = EXCLUDED.influence_score,
                    last_scraped_at = NOW(),
                    is_active = true
                RETURNING *;
            """
            
            cur.execute(query, (
                reviewer_data['name'],
                reviewer_data['platform'],
                reviewer_data['region'],
                reviewer_data['profile_url'],
                reviewer_data['influence_score']
            ))
            
            return cur.fetchone()
    
    def run(self):
        """Main execution"""
        print("🔍 Discovering top reviewers...")
        
        # Scrape Rotten Tomatoes
        rt_critics = self.scrape_rotten_tomatoes_critics()
        print(f"Found {len(rt_critics)} RT critics")
        
        stored_count = 0
        for critic in rt_critics:
            try:
                result = self.store_reviewer(critic)
                if result:
                    stored_count += 1
                    print(f"  ✅ {result['name']} ({result['platform']})")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"  ❌ Error storing {critic['name']}: {e}")
        
        print(f"\n✅ Stored {stored_count} reviewers")
        self.conn.close()

if __name__ == "__main__":
    discovery = ReviewerDiscovery()
    discovery.run()
