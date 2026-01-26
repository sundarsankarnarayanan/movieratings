-- Safe Schema Migration: Prevents data loss on movie updates
-- Run this after schema_v2.sql and schema_trend_analysis.sql

SET search_path TO movie_platform;

-- 1. Add stable tmdb_id reference to snapshot tables
-- This allows data to be preserved even if movie records are deleted/recreated
ALTER TABLE rating_snapshots ADD COLUMN IF NOT EXISTS tmdb_id INTEGER;
ALTER TABLE daily_review_snapshots ADD COLUMN IF NOT EXISTS tmdb_id INTEGER;

-- Create indexes for tmdb_id lookups
CREATE INDEX IF NOT EXISTS idx_rating_snapshots_tmdb ON rating_snapshots(tmdb_id);
CREATE INDEX IF NOT EXISTS idx_daily_snapshots_tmdb ON daily_review_snapshots(tmdb_id);

-- 2. Change CASCADE to SET NULL to prevent data loss
-- When a movie is deleted, snapshots are preserved with NULL movie_id but valid tmdb_id
ALTER TABLE rating_snapshots
    DROP CONSTRAINT IF EXISTS rating_snapshots_movie_id_fkey;
ALTER TABLE rating_snapshots
    ADD CONSTRAINT rating_snapshots_movie_id_fkey
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE SET NULL;

ALTER TABLE daily_review_snapshots
    DROP CONSTRAINT IF EXISTS daily_review_snapshots_movie_id_fkey;
ALTER TABLE daily_review_snapshots
    ADD CONSTRAINT daily_review_snapshots_movie_id_fkey
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE SET NULL;

-- 3. Add soft delete support to movies table
ALTER TABLE movies ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE movies ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- 4. Create audit log table for tracking all data changes
CREATE TABLE IF NOT EXISTS data_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
    record_id TEXT,
    tmdb_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT DEFAULT 'system',
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table ON data_audit_log(table_name, changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_tmdb ON data_audit_log(tmdb_id);

-- 5. Function to restore orphaned snapshots when movie is re-added
CREATE OR REPLACE FUNCTION restore_orphaned_snapshots(p_tmdb_id INTEGER, p_movie_id UUID)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
BEGIN
    -- Restore rating_snapshots
    UPDATE rating_snapshots
    SET movie_id = p_movie_id
    WHERE tmdb_id = p_tmdb_id AND movie_id IS NULL;
    GET DIAGNOSTICS updated_count = ROW_COUNT;

    -- Restore daily_review_snapshots
    UPDATE daily_review_snapshots
    SET movie_id = p_movie_id
    WHERE tmdb_id = p_tmdb_id AND movie_id IS NULL;

    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- 6. View to find orphaned snapshots (snapshots without active movie)
CREATE OR REPLACE VIEW orphaned_snapshots AS
SELECT
    'rating_snapshots' as table_name,
    tmdb_id,
    COUNT(*) as snapshot_count,
    MIN(snapshot_time) as earliest,
    MAX(snapshot_time) as latest
FROM rating_snapshots
WHERE movie_id IS NULL AND tmdb_id IS NOT NULL
GROUP BY tmdb_id
UNION ALL
SELECT
    'daily_review_snapshots' as table_name,
    tmdb_id,
    COUNT(*) as snapshot_count,
    MIN(snapshot_time) as earliest,
    MAX(snapshot_time) as latest
FROM daily_review_snapshots
WHERE movie_id IS NULL AND tmdb_id IS NOT NULL
GROUP BY tmdb_id;

COMMENT ON TABLE data_audit_log IS 'Tracks all data modifications for debugging and recovery';
COMMENT ON FUNCTION restore_orphaned_snapshots IS 'Restores historical data when a movie is re-added to the database';
COMMENT ON VIEW orphaned_snapshots IS 'Shows historical data that has lost its movie reference';
