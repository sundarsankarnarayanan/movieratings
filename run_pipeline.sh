#!/bin/bash

# Global Movie Intelligence Pipeline
# Runs agents to fetch data, analyze it, and update the platform.

echo "Starting Pipeline..."

# 1. Fetch Global Releases
echo "[1/3] Fetching global movie releases..."
python3 movie_release_agent.py

# 2. Fetch Reviews (Assuming main.py fetches for new movies)
# Note: main.py needs to be intelligent to fetch relevant critics. 
# For now, we run it to ensure our critic database is up to date, 
# although efficiently it should be targeted.
echo "[2/3] Fetching reviews from top critics..."
python3 main.py

# 3. Generate AI Summaries
echo "[3/3] Generating AI summaries and insights..."
python3 summarization_agent.py

echo "Pipeline Complete. Web Dashboard Updated."
