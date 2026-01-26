# PROJECT: Real-Time Movie Review Trend Platform

## Vision
A high-performance, real-time intelligence platform that tracks movie reviews across multiple global sources (Rotten Tomatoes, IMDb, Metacritic) to identify authentic trends and detect bot manipulation.

## Core Problem
Movie reviews are often manipulated by bots or review-bombing campaigns shortly after release. Users need a way to see the *trend* and *velocity* of reviews, rather than just a static snapshot, to determine if a movie is worth watching.

## Target Audience
- Movie enthusiasts looking for authentic audience reception.
- Data analysts tracking entertainment trends.
- Industry professionals monitoring film performance.

## Technology Stack
- **Backend**: Python 3.9+ (Multiprocessing for scraping)
- **Database**: PostgreSQL (Time-series data, Snapshot architecture)
- **Frontend**: Next.js 16 (App Router), React, Tailwind CSS, Recharts
- **Scraping**: BeautifulSoup4, Requests (Custom selectors for RT, IMDb, Metacritic)
- **Infrastructure**: Local dev via Makefile-driven automation

## Success Metrics
- **Data Freshness**: Hourly updates from all primary sources.
- **Accuracy**: Detection of review spikes (>5σ magnitude).
- **Performance**: Dashboard interactive under 1s.
- **Reliability**: Resilient scraper selectors with automatic fallbacks.
