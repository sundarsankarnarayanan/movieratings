from .base import BaseScraper
import re

class RottenTomatoesScraper(BaseScraper):
    def __init__(self, region='US', language='EN'):
        super().__init__(region, language)
        self.base_url = "https://www.rottentomatoes.com"

    def get_top_reviewers(self, limit=10):
        """Fetches critics from the editorial top critics list."""
        url = "https://editorial.rottentomatoes.com/otg-article/top-critics-list/"
        soup = self._get_soup(url)
        
        reviewers = []
        # Find critic links - The editorial page uses direct links to critic profiles
        critic_items = soup.select('a[href*="/critic/"]')
        
        seen_urls = set()
        for item in critic_items:
            if len(reviewers) >= limit:
                break
                
            name = item.text.strip()
            url_path = item['href']
            full_url = url_path if url_path.startswith('http') else self.base_url + url_path
            
            if full_url not in seen_urls and name and "/critic/" in full_url:
                reviewers.append({
                    "name": name,
                    "region": self.region,
                    "language": self.language,
                    "source": "Rotten Tomatoes",
                    "external_url": full_url
                })
                seen_urls.add(full_url)
        
        return reviewers

    def get_latest_reviews(self, reviewer_url):
        """Fetches reviews from a critic's profile page."""
        soup = self._get_soup(reviewer_url)
        reviews = []
        
        # Try primary selector
        review_rows = soup.select('tr[data-qa="critic-review-row"]')
        
        # Fallback: Find anything that looks like a movie link and has a rating nearby
        if not review_rows:
            # Look for links to movies
            movie_links = soup.select('a[href*="/m/"]')
            for link in movie_links[:10]:
                # Try to find a rating icon or text in the parent containers
                parent = link.find_parent(['tr', 'div', 'li'])
                if parent:
                    rating_elem = parent.select_one('span.icon--fresh, span.icon--rotten, [class*="fresh"], [class*="rotten"]')
                    content_elem = parent.select_one('[class*="excerpt"], [class*="quote"], [class*="review"]')
                    
                    rating = "Fresh"
                    if rating_elem and "rotten" in str(rating_elem).lower():
                        rating = "Rotten"
                        
                    reviews.append({
                        "movie_title": link.text.strip(),
                        "rating": rating,
                        "content": content_elem.text.strip() if content_elem else "No excerpt available.",
                        "review_date": None,
                        "source_url": self.base_url + link['href'] if not link['href'].startswith('http') else link['href']
                    })
        else:
            for row in review_rows[:5]: 
                title_elem = row.select_one('a[data-qa="movie-link"]')
                rating_elem = row.select_one('span.icon--fresh, span.icon--rotten')
                content_elem = row.select_one('td.review-excerpt') 
                date_elem = row.select_one('td.review-date')
                
                if title_elem:
                    rating = "Fresh" if "fresh" in str(rating_elem) else "Rotten"
                    reviews.append({
                        "movie_title": title_elem.text.strip(),
                        "rating": rating,
                        "content": content_elem.text.strip() if content_elem else "",
                        "review_date": date_elem.text.strip() if date_elem else None,
                        "source_url": self.base_url + title_elem['href'] if not title_elem['href'].startswith('http') else title_elem['href']
                    })
        
        return reviews
