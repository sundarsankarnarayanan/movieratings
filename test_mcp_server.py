import unittest
from unittest.mock import patch, MagicMock
from mcp_server import list_movies, get_movie_reviews, get_movie_insights

class TestMCPServer(unittest.TestCase):
    @patch('mcp_server.db')
    def test_list_movies(self, mock_db):
        mock_db.list_movies.return_value = [
            {"title": "Inception", "release_date": "2010-07-16", "slug": "inception"}
        ]
        
        result = list_movies(title="Inception")
        self.assertIn("Inception", result)
        self.assertIn("inception", result)

    @patch('mcp_server.db')
    def test_get_movie_reviews(self, mock_db):
        mock_db.get_movie_reviews.return_value = [
            {"rating": "Fresh", "content": "Masterpiece!", "reviewers": {"name": "Critic A"}}
        ]
        
        result = get_movie_reviews("inception")
        self.assertIn("Critic A", result)
        self.assertIn("Fresh", result)
        self.assertIn("Masterpiece", result)

    @patch('mcp_server.db')
    def test_get_movie_insights(self, mock_db):
        mock_db.get_movie_stats.return_value = {"count": 10, "fresh_score": 90.0}
        
        result = get_movie_insights("Inception")
        self.assertIn("10", result)
        self.assertIn("90.0%", result)

if __name__ == '__main__':
    unittest.main()
