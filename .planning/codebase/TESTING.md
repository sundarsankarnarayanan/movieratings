# Testing Patterns

**Analysis Date:** 2026-01-27

## Test Framework

### Python (Primary Testing)

**Runner:**
- `unittest` (Python standard library)
- No external test runner configured (no pytest, no pytest.ini)

**Assertion Library:**
- `unittest` assertions (e.g., `self.assertEqual`, `self.assertIn`)

**Mocking:**
- `unittest.mock` (standard library)
- `patch` decorator for dependency injection
- `MagicMock` for complex mock objects

**Run Commands:**
```bash
# Run a specific test file
python -m unittest test_scraper.py
python -m unittest test_mcp_server.py
python -m unittest test_movie_agent.py

# Run all tests (discover pattern)
python -m unittest discover -p "test_*.py"
```

### TypeScript/React (web-app)

**Status:** No test framework configured

**What's Missing:**
- No Jest, Vitest, or Playwright configuration
- No test files exist in `web-app/`
- No test scripts in `web-app/package.json`

## Test File Organization

### Python

**Location:**
- Root directory alongside source files
- Pattern: `test_*.py` files at same level as module being tested

**Naming:**
- Files: `test_{module_name}.py`
- Classes: `Test{ClassName}` (e.g., `TestRottenTomatoesScraper`)
- Methods: `test_{action_being_tested}` (e.g., `test_get_top_reviewers`)

**Structure:**
```
/Users/sundar/Projects/MovieRatings/
├── scrapers/
│   ├── base.py
│   └── rotten_tomatoes.py
├── test_scraper.py          # Tests for scrapers
├── mcp_server.py
├── test_mcp_server.py       # Tests for MCP server
├── tmdb_client.py
├── test_movie_agent.py      # Tests for TMDB client
```

### TypeScript/React

**Recommended (not implemented):**
- Co-located tests: `ComponentName.test.tsx`
- Or dedicated `__tests__/` directory

## Test Structure

### Python Test Pattern

**Suite Organization:**
```python
import unittest
from unittest.mock import patch, MagicMock
from scrapers.rotten_tomatoes import RottenTomatoesScraper

class TestRottenTomatoesScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = RottenTomatoesScraper()

    @patch('scrapers.base.BaseScraper._get_soup')
    def test_get_top_reviewers(self, mock_get_soup):
        # Arrange: Set up mock
        mock_get_soup.return_value = MagicMock()
        mock_get_soup.return_value.select.return_value = [
            MagicMock(text='John Doe', attrs={'href': '/critics/john-doe'})
        ]

        # Act: Call the method
        reviewers = self.scraper.get_top_reviewers(limit=2)

        # Assert: Verify results
        self.assertEqual(len(reviewers), 2)
        self.assertEqual(reviewers[0]['name'], 'John Doe')

if __name__ == '__main__':
    unittest.main()
```

**Patterns:**
- `setUp()` for test instance initialization
- `@patch` decorator for mocking external dependencies
- Arrange-Act-Assert pattern (implicit, not commented)

### MCP Server Test Pattern

```python
class TestMCPServer(unittest.TestCase):
    @patch('mcp_server.db')
    def test_list_movies(self, mock_db):
        # Arrange: Mock database response
        mock_db.list_movies.return_value = [
            {"title": "Inception", "release_date": "2010-07-16", "tmdb_id": 27205}
        ]

        # Act: Call the function
        result = list_movies(title="Inception")

        # Assert: Verify string output contains expected data
        self.assertIn("Inception", result)
        self.assertIn("27205", result)
```

### TMDB Client Test Pattern

```python
class TestTMDBClient(unittest.TestCase):
    def setUp(self):
        self.client = TMDBClient()

    @patch('requests.get')
    def test_get_movies_by_date(self, mock_get):
        # Arrange: Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "title": "Mock Movie 1", "release_date": "2024-01-21"}
            ]
        }
        mock_get.return_value = mock_response

        # Act
        movies = self.client.get_movies_by_date("2024-01-21", r_region="US")

        # Assert
        self.assertEqual(len(movies), 2)
        self.assertEqual(movies[0]['title'], "Mock Movie 1")
```

## Mocking

### Framework
- `unittest.mock` (standard library)

### Common Patterns

**Patching Module Dependencies:**
```python
@patch('mcp_server.db')
def test_function(self, mock_db):
    mock_db.list_movies.return_value = [...]
```

**Patching HTTP Requests:**
```python
@patch('requests.get')
def test_api_call(self, mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {...}
    mock_get.return_value = mock_response
```

**Patching BeautifulSoup HTML Parsing:**
```python
@patch('scrapers.base.BaseScraper._get_soup')
def test_scraping(self, mock_get_soup):
    mock_get_soup.return_value = MagicMock()
    mock_get_soup.return_value.select.return_value = [
        MagicMock(text='Element Text', attrs={'href': '/path'})
    ]
```

### What to Mock:
- External HTTP requests (`requests.get`)
- Database connections (`mcp_server.db`)
- HTML parsing results (`_get_soup`)

### What NOT to Mock:
- Business logic within the class being tested
- Data transformation functions
- Simple utility functions

## Fixtures and Factories

### Test Data Patterns

**Inline Mock Data:**
```python
mock_db.list_movies.return_value = [
    {"title": "Inception", "release_date": "2010-07-16", "tmdb_id": 27205}
]
```

**Mock HTML (Inline):**
```python
mock_html = """
<table>
    <tr><td><a href="/critics/john-doe">John Doe</a></td></tr>
</table>
"""
```

### No Dedicated Fixtures
- No `conftest.py` or fixture files
- Test data defined inline within each test method
- No factory libraries (e.g., factory_boy)

## Coverage

### Requirements
- None enforced
- No coverage configuration

### Recommended Setup (Not Implemented):
```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run -m unittest discover -p "test_*.py"
coverage report
coverage html
```

## Test Types

### Unit Tests (Implemented)

**Scope:**
- Individual functions and methods
- Class methods with mocked dependencies

**Files:**
- `test_scraper.py`: Tests `RottenTomatoesScraper` class
- `test_mcp_server.py`: Tests MCP server functions
- `test_movie_agent.py`: Tests `TMDBClient` class

### Integration Tests (Not Implemented)

**What's Missing:**
- No tests that verify database operations
- No tests for API endpoints
- No tests for scraper + database workflow

### E2E Tests (Not Implemented)

**Framework:** Not configured

**What's Missing:**
- No Playwright or Cypress for web-app
- No end-to-end workflow tests

## Common Patterns

### Async Testing

**Not Required:**
- Python tests use synchronous unittest
- No async/await patterns in test code

### Error Testing

**Pattern (Not Heavily Used):**
```python
# Current tests don't test error cases explicitly
# Recommended pattern:
def test_api_error_handling(self):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = self.client.get_movies_by_date("invalid")
    self.assertEqual(result, [])
```

### String Assertion Pattern

```python
# MCP server returns formatted strings, not structured data
result = list_movies(title="Inception")
self.assertIn("Inception", result)
self.assertIn("27205", result)
```

## Test Coverage Gaps

### Critical Untested Areas

**Database Operations (`database.py`):**
- No tests for `Database` class methods
- `upsert_reviewer`, `upsert_movie`, `insert_review` untested
- Risk: SQL queries could have bugs undetected

**Agents (`agents/*.py`):**
- `TrendAnalyzer` not tested
- `release_tracker.py`, `rating_monitor.py` not tested
- Complex algorithm logic (trend detection, anomaly detection) untested

**Web Application (`web-app/`):**
- Zero test coverage
- Data fetching functions untested
- React components untested
- Chart rendering untested

**Scrapers (Partial):**
- `BaseScraper._get_soup` not directly tested
- Error handling paths not tested

## Adding Tests to This Codebase

### For New Python Code

1. Create `test_{module_name}.py` in root directory
2. Use unittest framework with mocking:
```python
import unittest
from unittest.mock import patch, MagicMock
from your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        self.instance = YourClass()

    @patch('your_module.external_dependency')
    def test_method_name(self, mock_dep):
        # Arrange
        mock_dep.return_value = expected_data

        # Act
        result = self.instance.method_name()

        # Assert
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
```

### For Web Application (Recommended Setup)

**Install Vitest (recommended for Next.js):**
```bash
cd web-app
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

**Create `vitest.config.ts`:**
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
  },
})
```

**Example Component Test:**
```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import TrendBadge from '@/components/TrendBadge'

describe('TrendBadge', () => {
  it('renders trending up status', () => {
    render(<TrendBadge status="trending_up" />)
    expect(screen.getByText('Trending Up')).toBeInTheDocument()
  })
})
```

---

*Testing analysis: 2026-01-27*
