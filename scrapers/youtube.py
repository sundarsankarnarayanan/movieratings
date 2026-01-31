import requests
from bs4 import BeautifulSoup
from typing import List, Dict

class YouTubeReviewScraper:
    """
    Scrapes YouTube search results for movie review video metadata.
    """
    def fetch_reviews(self, movie_title: str) -> List[Dict]:
        query = f"{movie_title} review"
        url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        reviews = []
        # YouTube video titles (fragile, may need selector updates)
        for a in soup.select('a#video-title'):
            title = a.get('title')
            video_url = f"https://www.youtube.com{a.get('href')}"
            if title:
                reviews.append({
                    "content": title,
                    "source": "YouTube",
                    "author_name": None,
                    "rating": None,
                    "review_date": None,
                    "video_url": video_url
                })
        return reviews
