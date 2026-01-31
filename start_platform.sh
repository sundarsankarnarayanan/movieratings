#!/bin/bash

# Master Start Script for Movie Intelligence Platform

echo "🚀 Starting Movie Intelligence Platform..."

# Warn and unset PYTHONPATH to ensure the project venv is used
if [ -n "$PYTHONPATH" ]; then
  echo "⚠️  PYTHONPATH is set — unsetting it to avoid importing incompatible system packages"
  unset PYTHONPATH
fi

# 1. Kill any existing processes on common ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# 2. Run initial data population if needed
echo "📊 Running initial data population..."
./populate_db.sh

# 3. Analyze trends
echo "📈 Analyzing movie trends..."
if [ -x ".venv/bin/python" ]; then
  .venv/bin/python agents/trend_analyzer.py
else
  python3 agents/trend_analyzer.py
fi

# 4. Start the Web App in the background
echo "🌐 Starting Web Dashboard..."
cd web-app
npm run dev &
WEB_PID=$!
cd ..

# 5. Start the Rating Monitor in the background (continuous mode)
echo "⏱️ Starting Real-Time Rating Monitor (multi-source)..."
if [ -x ".venv/bin/python" ]; then
  .venv/bin/python agents/rating_monitor.py --continuous 60 &
else
  python3 agents/rating_monitor.py --continuous 60 &
fi
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
