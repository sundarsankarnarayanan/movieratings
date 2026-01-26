-- Real-Time Movie Review Trend Platform Schema
-- Drop existing schema and recreate
DROP SCHEMA IF EXISTS movie_platform CASCADE;
CREATE SCHEMA movie_platform;
SET search_path TO movie_platform;

-- 1. Movies Table (Core metadata)
CREATE TABLE movies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tmdb_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    original_title TEXT,
    release_date DATE NOT NULL,
    genres TEXT[],
    regions TEXT[],
    poster_url TEXT,
    backdrop_url TEXT,
    overview TEXT,
    runtime INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_movies_release_date ON movies(release_date DESC);
CREATE INDEX idx_movies_tmdb_id ON movies(tmdb_id);

-- 2. Reviewers Table (Regional critic tracking)
CREATE TABLE reviewers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    platform TEXT NOT NULL, -- 'RottenTomatoes', 'Metacritic', 'IMDb', etc.
    region TEXT NOT NULL,
    profile_url TEXT UNIQUE NOT NULL,
    influence_score FLOAT DEFAULT 0,
    last_scraped_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reviewers_platform_region ON reviewers(platform, region);
CREATE INDEX idx_reviewers_profile_url ON reviewers(profile_url);

-- 3. Rating Snapshots (Time-Series Core)
CREATE TABLE rating_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    movie_id UUID REFERENCES movies(id) ON DELETE CASCADE,
    source TEXT NOT NULL, -- 'RottenTomatoes', 'Metacritic', 'IMDb', 'Letterboxd'
    rating_type TEXT NOT NULL, -- 'critic', 'audience', 'tomatometer', 'metascore'
    rating_value FLOAT NOT NULL,
    review_count INTEGER DEFAULT 0,
    snapshot_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB, -- Store additional context (e.g., fresh/rotten counts)
    UNIQUE(movie_id, source, rating_type, snapshot_time)
);

-- Critical indexes for time-series queries
CREATE INDEX idx_snapshots_time ON rating_snapshots(snapshot_time DESC);
CREATE INDEX idx_snapshots_movie_time ON rating_snapshots(movie_id, snapshot_time DESC);
CREATE INDEX idx_snapshots_source ON rating_snapshots(source, snapshot_time DESC);

-- 4. Review Sources (Platform configuration)
CREATE TABLE review_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL, -- 'RottenTomatoes', 'Metacritic', 'IMDb'
    base_url TEXT NOT NULL,
    scrape_interval_minutes INTEGER DEFAULT 60,
    last_scraped_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    rate_limit_per_minute INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Scrape Logs (Monitor agent health)
CREATE TABLE scrape_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name TEXT NOT NULL,
    movie_id UUID REFERENCES movies(id) ON DELETE CASCADE,
    status TEXT NOT NULL, -- 'success', 'error', 'rate_limited'
    error_message TEXT,
    snapshots_created INTEGER DEFAULT 0,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scrape_logs_time ON scrape_logs(scraped_at DESC);

-- Insert default review sources
INSERT INTO review_sources (name, base_url, scrape_interval_minutes, rate_limit_per_minute) VALUES
('RottenTomatoes', 'https://www.rottentomatoes.com', 60, 10),
('Metacritic', 'https://www.metacritic.com', 120, 5),
('IMDb', 'https://www.imdb.com', 180, 5);

-- Materialized view for trend calculation
CREATE MATERIALIZED VIEW movie_trends AS
SELECT 
    m.id as movie_id,
    m.title,
    m.release_date,
    rs.source,
    rs.rating_type,
    FIRST_VALUE(rs.rating_value) OVER w as current_rating,
    FIRST_VALUE(rs.rating_value) OVER w - LAG(rs.rating_value, 24) OVER w as rating_change_24h,
    COUNT(*) OVER w as total_snapshots
FROM movies m
JOIN rating_snapshots rs ON m.id = rs.movie_id
WHERE rs.snapshot_time > NOW() - INTERVAL '30 days'
WINDOW w AS (PARTITION BY m.id, rs.source, rs.rating_type ORDER BY rs.snapshot_time DESC)
ORDER BY m.release_date DESC;

CREATE UNIQUE INDEX idx_movie_trends ON movie_trends(movie_id, source, rating_type);

-- Function to refresh trends (call periodically)
CREATE OR REPLACE FUNCTION refresh_movie_trends()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY movie_trends;
END;
$$ LANGUAGE plpgsql;
