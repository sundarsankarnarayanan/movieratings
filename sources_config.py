# Movie Rating Sources Config
# Used by scrapers to identify and configure each source

sources = [
    {
        "name": "RottenTomatoes",
        "base_url": "https://www.rottentomatoes.com/",
        "type": "critic",
        "scrape_interval_minutes": 60
    },
    {
        "name": "Metacritic",
        "base_url": "https://www.metacritic.com/",
        "type": "critic",
        "scrape_interval_minutes": 60
    },
    {
        "name": "IMDb",
        "base_url": "https://www.imdb.com/",
        "type": "audience",
        "scrape_interval_minutes": 60
    },
    {
        "name": "Google",
        "base_url": "https://www.google.com/search?q={movie}+reviews",
        "type": "audience",
        "scrape_interval_minutes": 120
    },
    {
        "name": "YouTube",
        "base_url": "https://www.youtube.com/results?search_query={movie}+review",
        "type": "video",
        "scrape_interval_minutes": 120
    }
]
