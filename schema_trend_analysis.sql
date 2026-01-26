-- Review Trend Analysis Schema Migration
-- Adds daily review tracking and trend classification

SET search_path TO movie_platform;

-- Drop existing materialized view if it exists
DROP MATERIALIZED VIEW IF EXISTS trending_movies CASCADE;

-- 1. Daily Review Snapshots (Time-Series Data)
CREATE TABLE IF NOT EXISTS daily_review_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    movie_id UUID REFERENCES movies(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    
    -- Review metrics
    total_reviews INTEGER DEFAULT 0,
    new_reviews_today INTEGER DEFAULT 0,
    
    -- Rating metrics
    critic_score FLOAT,
    audience_score FLOAT,
    
    -- Velocity metrics (calculated)
    review_velocity FLOAT, -- reviews per day since release
    score_change FLOAT, -- rating change from previous day
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(movie_id, source, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_daily_snapshots_date ON daily_review_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_snapshots_movie ON daily_review_snapshots(movie_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_snapshots_movie_source ON daily_review_snapshots(movie_id, source, snapshot_date DESC);

-- 2. Movie Trends (Calculated Classifications)
CREATE TABLE IF NOT EXISTS movie_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    movie_id UUID REFERENCES movies(id) ON DELETE CASCADE UNIQUE,
    
    -- Trend classification
    trend_status TEXT, -- 'trending_up', 'trending_down', 'stable', 'sleeper_hit'
    trend_confidence FLOAT, -- 0-1 confidence score
    
    -- Metrics (7-day window)
    avg_daily_reviews FLOAT,
    review_growth_rate FLOAT, -- percentage change
    score_momentum FLOAT, -- direction of rating change
    
    -- Anomaly detection
    has_suspicious_activity BOOLEAN DEFAULT false,
    spike_detected BOOLEAN DEFAULT false,
    spike_date DATE,
    spike_magnitude FLOAT, -- how many standard deviations
    
    last_calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_movie_trends_status ON movie_trends(trend_status);
CREATE INDEX IF NOT EXISTS idx_movie_trends_suspicious ON movie_trends(has_suspicious_activity) WHERE has_suspicious_activity = true;

-- 3. Helper function to get days since release
CREATE OR REPLACE FUNCTION days_since_release(movie_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT EXTRACT(DAY FROM NOW() - release_date)::INTEGER
        FROM movies
        WHERE id = movie_id
    );
END;
$$ LANGUAGE plpgsql;

-- 4. Materialized view for quick trend lookups
CREATE MATERIALIZED VIEW trending_movies AS
SELECT 
    m.id,
    m.title,
    m.poster_url,
    m.release_date,
    mt.trend_status,
    mt.trend_confidence,
    mt.avg_daily_reviews,
    mt.review_growth_rate,
    mt.score_momentum,
    mt.has_suspicious_activity,
    mt.spike_detected
FROM movies m
JOIN movie_trends mt ON m.id = mt.movie_id
WHERE m.release_date > NOW() - INTERVAL '30 days'
ORDER BY 
    CASE mt.trend_status
        WHEN 'sleeper_hit' THEN 1
        WHEN 'trending_up' THEN 2
        WHEN 'stable' THEN 3
        WHEN 'trending_down' THEN 4
    END,
    mt.review_growth_rate DESC;

CREATE UNIQUE INDEX idx_trending_movies ON trending_movies(id);

-- Function to refresh trending view
CREATE OR REPLACE FUNCTION refresh_trending_movies()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY trending_movies;
END;
$$ LANGUAGE plpgsql;
