import requests
from bs4 import BeautifulSoup
from typing import List, Dict

class GoogleReviewScraper:
    """
    Scrapes Google search results for movie ratings and review snippets.
    """
    def fetch_reviews(self, movie_title: str) -> List[Dict]:
        query = f"{movie_title} reviews"
        url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        reviews = []
        # Google review snippets (fragile, may need selector updates)
        for div in soup.select('div.jcQ2Ge'):  # Example selector
            snippet = div.get_text(strip=True)
            if snippet:
                reviews.append({
                    "content": snippet,
                    "source": "Google",
                    "author_name": None,
                    "rating": None,
                    "review_date": None
                })
        return reviews
