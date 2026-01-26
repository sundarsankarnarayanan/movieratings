# ROADMAP: Movie Review Trend Platform

## Phase 1: Foundation & Data Discovery (COMPLETED)
- [x] R1: Initialize Postgres schema and movie tracking.
- [x] R2: Build Rotten Tomatoes movie release scraper.
- [x] R3: Implement reviewer discovery agent.

## Phase 2: Multi-Source Intelligence (COMPLETED)
- [x] R1: Expand scraper to support IMDb and Metacritic.
- [x] R2: Implement time-series snapshot storage for all sources.
- [x] R3: Build robust selector fallbacks for modern web components.

## Phase 3: Trend Analysis & Anomaly Detection (IN PROGRESS)
- [x] R1: Create `daily_review_snapshots` table for day-over-day analysis.
- [x] R2: Build `trend_analyzer.py` agent with classification logic.
- [x] R3: Implement bot detection heuristics (standard deviation spikes).
- [/] R4: Refine review count scraping for accurate velocity metrics.

## Phase 4: Intelligence Dashboard (IN PROGRESS)
- [x] R1: Initialize Next.js dashboard with Recharts.
- [x] R2: Build interactive `ReviewTrendChart` visualization.
- [/] R3: Integrate trend badges and anomaly warnings into movie detail pages.

## Phase 5: Production Hardening (TODO)
- [ ] R1: Add API layer for performance and security.
- [ ] R2: Implement Redis caching for high-traffic trend data.
- [ ] R3: Build notification system for suspicious trend spikes.
- [ ] R4: Multi-region scraping load balancing.
