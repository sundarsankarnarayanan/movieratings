# Makefile for Real-Time Movie Review Trend Platform

PYTHON = python3
PIP = pip3
NPM = npm
PYTHONPATH_VAL = PYTHONPATH=/Users/sundar/Library/Python/3.9/lib/python/site-packages

.PHONY: help install setup-db populate monitor web start clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install all Python and Node.js dependencies"
	@echo "  make setup-db      - Initialize the database schema"
	@echo "  make populate      - Run initial data population (releases, reviewers, ratings)"
	@echo "  make analyze-trends - Analyze review trends and classify movies"
	@echo "  make monitor       - Start real-time rating monitor (continuous mode)"
	@echo "  make web           - Start the web dashboard (development)"
	@echo "  make start         - Run the full system (cleanup + populate + start all)"
	@echo "  make clean         - Kill all processes on ports 3000 and 3001"

install:
	$(PIP) install psycopg2-binary requests beautifulsoup4 python-dotenv
	cd web-app && $(NPM) install

setup-db:
	$(PYTHONPATH_VAL) $(PYTHON) -c "\
	import psycopg2, os; \
	from dotenv import load_dotenv; \
	load_dotenv(); \
	conn = psycopg2.connect( \
	    host=os.environ.get('DB_HOST'), \
	    port=os.environ.get('DB_PORT'), \
	    database=os.environ.get('DB_NAME'), \
	    user=os.environ.get('DB_USER'), \
	    password=os.environ.get('DB_PASSWORD') \
	); \
	conn.autocommit = True; \
	with conn.cursor() as cur: \
	    with open('schema_v2.sql', 'r') as f: \
	        cur.execute(f.read()); \
	conn.close(); \
	print('✅ Database schema initialized.')"

populate:
	@echo "🎬 Scraping movie releases..."
	$(PYTHONPATH_VAL) $(PYTHON) agents/web_scraping_tracker.py
	@echo "🔍 Discovering top reviewers..."
	$(PYTHONPATH_VAL) $(PYTHON) agents/reviewer_discovery.py
	@echo "📊 Fetching initial ratings..."
	$(PYTHONPATH_VAL) $(PYTHON) agents/rating_monitor.py
	@echo "📈 Analyzing trends..."
	$(PYTHONPATH_VAL) $(PYTHON) agents/trend_analyzer.py

analyze-trends:
	$(PYTHONPATH_VAL) $(PYTHON) agents/trend_analyzer.py

monitor:
	$(PYTHONPATH_VAL) $(PYTHON) agents/rating_monitor.py --continuous 60

web:
	cd web-app && $(NPM) run dev

start:
	./start_platform.sh

clean:
	@echo "🧹 Cleaning up existing processes..."
	-lsof -ti:3000 | xargs kill -9 2>/dev/null
	-lsof -ti:3001 | xargs kill -9 2>/dev/null
	@echo "✅ Done."
