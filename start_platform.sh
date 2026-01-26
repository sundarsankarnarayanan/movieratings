#!/bin/bash

# Master Start Script for Movie Intelligence Platform

echo "🚀 Starting Movie Intelligence Platform..."

# 1. Kill any existing processes on common ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# 2. Run initial data population if needed
echo "📊 Running initial data population..."
./populate_db.sh

# 3. Analyze trends
echo "📈 Analyzing movie trends..."
PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages python3 agents/trend_analyzer.py

# 4. Start the Web App in the background
echo "🌐 Starting Web Dashboard..."
cd web-app
npm run dev &
WEB_PID=$!
cd ..

# 5. Start the Rating Monitor in the background (continuous mode)
echo "⏱️ Starting Real-Time Rating Monitor (multi-source)..."
PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages python3 agents/rating_monitor.py --continuous 60 &
MONITOR_PID=$!

echo ""
echo "✅ Application started successfully!"
echo "👉 Dashboard: http://localhost:3000 (or 3001 if 3000 is busy)"
echo "📡 Rating Monitor is tracking changes from RT, IMDb, and Metacritic every 60 minutes."
echo ""
echo "Press Ctrl+C to stop everything."

# Wait for Ctrl+C
trap "kill $WEB_PID $MONITOR_PID; exit" INT
wait
