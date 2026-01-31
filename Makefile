# Makefile for Real-Time Movie Review Trend Platform

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
NPM = npm
PYTHONPATH_VAL = 

.PHONY: help install venv setup-db populate monitor web start clean

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

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install psycopg2-binary requests beautifulsoup4 python-dotenv
	cd web-app && $(NPM) install

setup-db:
	$(PYTHON) apply_schema_v2.py

populate:
	@echo "🎬 Scraping movie releases..."
	$(PYTHON) agents/web_scraping_tracker.py
	@echo "🔍 Discovering top reviewers..."
	$(PYTHON) agents/reviewer_discovery.py
	@echo "📊 Fetching initial ratings..."
	$(PYTHON) agents/rating_monitor.py
	@echo "📈 Analyzing trends..."
	$(PYTHON) agents/trend_analyzer.py

analyze-trends:
	$(PYTHON) agents/trend_analyzer.py

monitor:
	$(PYTHON) agents/rating_monitor.py --continuous 60

web:
	cd web-app && $(NPM) run dev

start:
	./start_platform.sh

test:
	@echo "Running integration test: unset PYTHONPATH behavior"
	@bash tests/scripts/check_unset_pythonpath.sh

clean:
	@echo "🧹 Cleaning up existing processes..."
	-lsof -ti:3000 | xargs kill -9 2>/dev/null
	-lsof -ti:3001 | xargs kill -9 2>/dev/null
	@echo "✅ Done."
