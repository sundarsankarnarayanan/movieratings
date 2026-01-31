#!/bin/bash
# Quick Start Script - Populate Database with Web Scraping

echo "🎬 Starting Movie Database Population..."
echo ""
# Prevent an externally-set PYTHONPATH from overriding the project's virtualenv packages
if [ -n "$PYTHONPATH" ]; then
  echo "⚠️  PYTHONPATH is set — unsetting it to avoid importing incompatible system packages"
  unset PYTHONPATH
fi


# Step 1: Scrape movies from web
echo "Step 1/3: Scraping movie releases..."
if [ -x ".venv/bin/python" ]; then
  .venv/bin/python agents/web_scraping_tracker.py
else
  python3 agents/web_scraping_tracker.py
fi

echo ""
echo "Step 2/3: Discovering top reviewers..."
if [ -x ".venv/bin/python" ]; then
  .venv/bin/python agents/reviewer_discovery.py
else
  python3 agents/reviewer_discovery.py
fi

echo ""
echo "Step 3/3: Fetching current ratings..."
if [ -x ".venv/bin/python" ]; then
  .venv/bin/python agents/rating_monitor.py
else
  python3 agents/rating_monitor.py
fi

echo ""
echo "✅ Database populated! Check your dashboard at http://localhost:3002"
