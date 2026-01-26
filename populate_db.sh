#!/bin/bash
# Quick Start Script - Populate Database with Web Scraping

echo "🎬 Starting Movie Database Population..."
echo ""

# Step 1: Scrape movies from web
echo "Step 1/3: Scraping movie releases..."
PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages python3 agents/web_scraping_tracker.py

echo ""
echo "Step 2/3: Discovering top reviewers..."
PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages python3 agents/reviewer_discovery.py

echo ""
echo "Step 3/3: Fetching current ratings..."
PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages python3 agents/rating_monitor.py

echo ""
echo "✅ Database populated! Check your dashboard at http://localhost:3002"
