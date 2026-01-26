import unittest
from unittest.mock import patch, MagicMock
from tmdb_client import TMDBClient

class TestTMDBClient(unittest.TestCase):
    def setUp(self):
        self.client = TMDBClient()

    @patch('requests.get')
    def test_get_movies_by_date(self, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "title": "Mock Movie 1", "release_date": "2024-01-21"},
                {"id": 2, "title": "Mock Movie 2", "release_date": "2024-01-21"}
            ]
        }
        mock_get.return_value = mock_response
        
        movies = self.client.get_movies_by_date("2024-01-21", r_region="US", r_language="en")
        self.assertEqual(len(movies), 2)
        self.assertEqual(movies[0]['title'], "Mock Movie 1")

if __name__ == '__main__':
    unittest.main()
