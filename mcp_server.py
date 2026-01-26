from mcp.server.fastmcp import FastMCP
from database import Database
import json

# Initialize FastMCP server
mcp = FastMCP("MovieRatings")
db = Database()

@mcp.tool()
def list_movies(region: str = None, language: str = None, title: str = None) -> str:
    """
    List movies stored in the database with optional filters.
    
    Args:
        region: ISO 3166-1 region code (e.g., 'US', 'FR')
        language: ISO 639-1 language code (e.g., 'en', 'fr')
        title: Partial title to search for
    """
    movies = db.list_movies(region=region, language=language, title_query=title)
    if not movies:
        return "No movies found matching the criteria."
    
    output = []
    for m in movies:
        output.append(f"- {m['title']} ({m['release_date']}) [ID: {m['tmdb_id']}]")
    
    return "\n".join(output)

@mcp.tool()
def get_movie_reviews(tmdb_id: int) -> str:
    """
    Get all reviews and ratings for a specific movie by its TMDB ID.
    
    Args:
        tmdb_id: The TMDB ID of the movie
    """
    reviews = db.get_movie_reviews(tmdb_id)
    if not reviews:
        return f"No reviews found for movie with ID {tmdb_id}."
    
    output = []
    for r in reviews:
        reviewer_name = r.get('reviewers', {}).get('name', 'Unknown')
        output.append(f"Reviewer: {reviewer_name}\nRating: {r['rating']}\nContent: {r['content']}\n---")
    
    return "\n".join(output)

@mcp.tool()
def get_movie_insights(title: str) -> str:
    """
    Get statistical insights for a movie based on stored reviews.
    
    Args:
        title: The exact title of the movie
    """
    stats = db.get_movie_stats(title)
    if stats['count'] == 0:
        return f"No statistical data found for '{title}'."
    
    return f"Insights for '{title}':\n- Total Reviews: {stats['count']}\n- Rotten Tomatoes Proxy Score: {stats['fresh_score']:.1f}% Fresh"

if __name__ == "__main__":
    mcp.run()
