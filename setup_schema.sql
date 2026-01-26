-- Create a new schema for the platform
CREATE SCHEMA IF NOT EXISTS movie_platform;

-- Set search path to the new schema
SET search_path TO movie_platform;

-- Create reviewers table
CREATE TABLE IF NOT EXISTS reviewers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    region TEXT,
    language TEXT,
    source TEXT,
    external_url TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create movies table
CREATE TABLE IF NOT EXISTS movies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tmdb_id INTEGER UNIQUE,
    title TEXT NOT NULL,
    original_title TEXT,
    release_date DATE NOT NULL,
    region TEXT,
    language TEXT,
    overview TEXT,
    vote_average FLOAT,
    vote_count INTEGER,
    popularity FLOAT,
    poster_path TEXT,
    backdrop_path TEXT,
    genre_ids INTEGER[],
    adult BOOLEAN,
    video BOOLEAN,
    ai_summary_positive TEXT,
    ai_summary_negative TEXT,
    trending_score FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reviewer_id UUID REFERENCES reviewers(id) ON DELETE CASCADE,
    movie_title TEXT NOT NULL,
    rating TEXT,
    content TEXT,
    review_date DATE,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create movie_regions table for granular release tracking
CREATE TABLE IF NOT EXISTS movie_regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    movie_id UUID REFERENCES movies(id) ON DELETE CASCADE,
    region_code TEXT NOT NULL,
    release_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(movie_id, region_code)
);

-- Add indexes for search and performance
CREATE INDEX IF NOT EXISTS idx_reviewers_region_lang ON reviewers (region, language);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer_id ON reviews (reviewer_id);
CREATE INDEX IF NOT EXISTS idx_movies_release_date_region ON movies (release_date, region, language);
CREATE INDEX IF NOT EXISTS idx_movie_regions_date ON movie_regions (release_date);
