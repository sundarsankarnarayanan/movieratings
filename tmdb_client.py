import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self):
        self.api_key = os.environ.get("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"

    def get_movies_by_date(self, date, r_region=None, r_language=None):
        """
        Fetches movies released on a specific date.
        TMDb Discover API parameters:
        primary_release_date.gte: start date
        primary_release_date.lte: end date
        region: ISO 3166-1 code
        with_original_language: ISO 639-1 code
        """
        if not self.api_key:
            print("Warning: TMDB_API_KEY not found.")
            return []

        endpoint = f"{self.base_url}/discover/movie"
        params = {
            "api_key": self.api_key,
            "primary_release_date.gte": date,
            "primary_release_date.lte": date,
            "sort_by": "popularity.desc"
        }
        
        if r_region:
            params["region"] = r_region
        if r_language:
            params["with_original_language"] = r_language

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            print(f"Error fetching movies: {response.status_code} - {response.text}")
            return []

    def get_movie_details(self, movie_id):
        endpoint = f"{self.base_url}/movie/{movie_id}"
        params = {"api_key": self.api_key}
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        return None
