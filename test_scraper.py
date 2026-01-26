import unittest
from unittest.mock import patch, MagicMock
from scrapers.rotten_tomatoes import RottenTomatoesScraper

class TestRottenTomatoesScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = RottenTomatoesScraper()

    @patch('scrapers.base.BaseScraper._get_soup')
    def test_get_top_reviewers(self, mock_get_soup):
        # Mock HTML response
        mock_html = """
        <table>
            <tr><td><a href="/critics/john-doe">John Doe</a></td></tr>
            <tr><td><a href="/critics/jane-smith">Jane Smith</a></td></tr>
        </table>
        """
        mock_get_soup.return_value = MagicMock()
        mock_get_soup.return_value.select.return_value = [
            MagicMock(text='John Doe', attrs={'href': '/critics/john-doe'}),
            MagicMock(text='Jane Smith', attrs={'href': '/critics/jane-smith'})
        ]
        
        reviewers = self.scraper.get_top_reviewers(limit=2)
        self.assertEqual(len(reviewers), 2)
        self.assertEqual(reviewers[0]['name'], 'John Doe')
        self.assertEqual(reviewers[0]['external_url'], 'https://www.rottentomatoes.com/critics/john-doe')

    @patch('scrapers.base.BaseScraper._get_soup')
    def test_get_latest_reviews(self, mock_get_soup):
        mock_row = MagicMock()
        mock_title = MagicMock(text='Inception')
        mock_title.attrs = {'href': '/m/inception'}
        mock_row.select_one.side_effect = lambda qa: {
            'a[data-qa="movie-link"]': mock_title,
            'span.icon--fresh, span.icon--rotten': MagicMock(),
            'td.review-excerpt': MagicMock(text='Great movie!'),
            'td.review-date': MagicMock(text='Jan 1, 2024')
        }.get(qa)
        
        mock_get_soup.return_value.select.return_value = [mock_row]
        
        reviews = self.scraper.get_latest_reviews('https://www.rottentomatoes.com/critics/john-doe')
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['movie_title'], 'Inception')

if __name__ == '__main__':
    unittest.main()
