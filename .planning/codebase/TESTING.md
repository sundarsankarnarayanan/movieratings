# Testing Patterns

**Analysis Date:** 2026-01-26

## Test Framework

**Runner:**
- Python: `unittest` (built-in standard library)
- TypeScript/React: No test framework configured (not detected)

**Assertion Library:**
- Python: unittest assertions (e.g., `self.assertEqual()`, `self.assertTrue()`)

**Run Commands:**
```bash
python -m unittest test_scraper.py              # Run specific test file
python -m unittest discover                     # Run all tests
# Note: No test script in package.json for TypeScript
```

## Test File Organization

**Location:**
- Python tests: Co-located with root project directory (not in subdirectories)
- Pattern: Test files named with `test_` prefix (e.g., `test_scraper.py`, `test_mcp_server.py`, `test_movie_agent.py`)
- Files present: `/Users/sundar/Projects/MovieRatings/test_scraper.py`, `test_mcp_server.py`, `test_movie_agent.py`

**Naming:**
- `test_[module_name].py` pattern
- Test methods prefixed with `test_` (e.g., `test_get_top_reviewers`, `test_get_latest_reviews`)

**Structure:**
```
ProjectRoot/
├── test_scraper.py          # Tests for scrapers
├── test_mcp_server.py       # Tests for MCP server
├── test_movie_agent.py      # Tests for movie agent
├── scrapers/
│   ├── __init__.py
│   ├── base.py             # Abstract base class
│   └── rotten_tomatoes.py  # Implementation
└── database.py             # Database connection class
```

## Test Structure

**Suite Organization:**
```python
# From test_scraper.py
import unittest
from unittest.mock import patch, MagicMock
from scrapers.rotten_tomatoes import RottenTomatoesScraper

class TestRottenTomatoesScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = RottenTomatoesScraper()

    @patch('scrapers.base.BaseScraper._get_soup')
    def test_get_top_reviewers(self, mock_get_soup):
        # Test implementation
        pass

    @patch('scrapers.base.BaseScraper._get_soup')
    def test_get_latest_reviews(self, mock_get_soup):
        # Test implementation
        pass

if __name__ == '__main__':
    unittest.main()
```

**Patterns:**
- Setup: `setUp(self)` method runs before each test (initializes scraper instance)
- No teardown methods observed
- Assertion pattern: `self.assertEqual(actual, expected)`
- Test naming: descriptive names starting with `test_`

## Mocking

**Framework:** `unittest.mock` (built-in Python mocking)

**Patterns:**
```python
# From test_scraper.py - decorator-based mocking
@patch('scrapers.base.BaseScraper._get_soup')
def test_get_top_reviewers(self, mock_get_soup):
    mock_html = """..."""
    mock_get_soup.return_value = MagicMock()
    mock_get_soup.return_value.select.return_value = [
        MagicMock(text='John Doe', attrs={'href': '/critics/john-doe'}),
        MagicMock(text='Jane Smith', attrs={'href': '/critics/jane-smith'})
    ]

    reviewers = self.scraper.get_top_reviewers(limit=2)
    self.assertEqual(len(reviewers), 2)
    self.assertEqual(reviewers[0]['name'], 'John Doe')
```

```python
# Mock object configuration with side_effect
mock_row.select_one.side_effect = lambda qa: {
    'a[data-qa="movie-link"]': mock_title,
    'span.icon--fresh, span.icon--rotten': MagicMock(),
    'td.review-excerpt': MagicMock(text='Great movie!'),
    'td.review-date': MagicMock(text='Jan 1, 2024')
}.get(qa)
```

**What to Mock:**
- External HTTP requests (use `@patch('scrapers.base.BaseScraper._get_soup')`)
- HTML parsing results (BeautifulSoup returns)
- Database connections (would use mock for database.py methods)

**What NOT to Mock:**
- Core business logic (scraper filtering, data mapping)
- Assertion conditions
- Test fixture setup

## Fixtures and Factories

**Test Data:**
```python
# From test_scraper.py - inline mock HTML
mock_html = """
<table>
    <tr><td><a href="/critics/john-doe">John Doe</a></td></tr>
    <tr><td><a href="/critics/jane-smith">Jane Smith</a></td></tr>
</table>
"""
```

**Location:**
- Test data defined inline within test methods
- No separate fixtures directory
- No factory classes for generating test data

## Coverage

**Requirements:** None enforced (no coverage tool configured)

**View Coverage:**
```bash
# No coverage reporting configured
# Would need pytest-cov or coverage.py installed
```

## Test Types

**Unit Tests:**
- Scope: Individual scraper methods and data extraction logic
- Approach: Mock external dependencies (HTTP requests), assert returned data structure
- Example: `test_get_top_reviewers()` mocks `_get_soup()`, verifies list of reviewers returned with correct fields
- Location: `test_scraper.py`

**Integration Tests:**
- Scope: Limited - only found in `test_movie_agent.py`, `test_mcp_server.py`
- Not examined in detail - likely test interactions between multiple components

**E2E Tests:**
- Framework: Not used
- No end-to-end test suite detected

## Common Patterns

**Async Testing:**
```python
# Async patterns not used in Python tests
# TypeScript/React has no test configuration
# Next.js async server functions tested implicitly through page rendering
```

**Error Testing:**
```python
# Error handling not explicitly tested in observed test files
# Pattern would follow unittest exception assertions:
# with self.assertRaises(SomeError):
#     function_that_raises_error()
```

**Database Testing:**
```python
# From database.py - Connection initialization with error handling
# Tests would typically mock the psycopg2.connect() method
# Example pattern (not in codebase):
# @patch('psycopg2.connect')
# def test_database_connection(self, mock_connect):
#     mock_connect.return_value = MagicMock()
#     db = Database()
#     self.assertIsNotNone(db.conn)
```

## Test Coverage Gaps

**Untested Areas:**
- All React components (`MovieCard.tsx`, `ReviewTrendChart.tsx`, `TrendBadge.tsx`) - no test framework configured
- All Next.js page components (no Jest/Vitest setup)
- Database class methods (`upsert_reviewer()`, `insert_review()`, `upsert_movie()`, etc.) - no unit tests found
- End-to-end workflows - no E2E framework

**Priority for Testing:**
1. Database operations (medium priority - critical path) - Currently untested
2. React components (medium priority - UI correctness) - Currently untested
3. Scraper edge cases (low priority - external dependencies) - Partially tested

## Testing Best Practices Used

**Strengths:**
- Test isolation: Each test method is independent with setUp
- Mocking external dependencies (HTTP requests)
- Descriptive test names
- Organized test classes by feature

**Gaps:**
- No test runner in TypeScript/React (next steps: add Jest or Vitest)
- No CI/CD test automation detected
- No coverage reporting configured
- Limited assertions per test
- No integration test patterns for database layer

---

*Testing analysis: 2026-01-26*
