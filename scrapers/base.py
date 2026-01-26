from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    def __init__(self, region, language):
        self.region = region
        self.language = language

    @abstractmethod
    def get_top_reviewers(self, limit=10):
        """Fetches the top reviewers for the source."""
        pass

    @abstractmethod
    def get_latest_reviews(self, reviewer_url):
        """Fetches the latest reviews for a specific reviewer."""
        pass

    def _get_soup(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
