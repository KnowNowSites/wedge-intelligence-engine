.PHONY: help install run dev test clean init-db docker-up docker-down scrape detect

help:
	@echo "Wedge Intelligence Engine (WIE) - Available Commands"
	@echo ""
	@echo "  make install      Install all dependencies (Python + Node)"
	@echo "  make init-db      Initialize SQLite database at ./wie.db"
	@echo "  make run          Start full app (Python API on :5000, Node on :3000)"
	@echo "  make dev          Same as run (alias)"
	@echo "  make scrape       Run all working scrapers"
	@echo "  make detect       Run all 7 detectors + generate profiles"
	@echo "  make test         Run tests"
	@echo "  make clean        Delete wie.db and logs"
	@echo "  make docker-up    Start with Docker Compose"
	@echo "  make docker-down  Stop Docker Compose"
	@echo ""

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Node dependencies..."
	pnpm install
	@echo "Done!"

init-db:
	@echo "Initializing database..."
	python3 backend/database.py
	@echo "Database ready at ./wie.db"

run: init-db
	@echo ""
	@echo "Starting Wedge Intelligence Engine..."
	@echo "  Python API: http://localhost:5000"
	@echo "  Dashboard:  http://localhost:3000"
	@echo ""
	@echo "Tip: Run 'make scrape' in another terminal to populate data."
	@echo ""
	python3 backend/api_server.py &
	pnpm run dev

dev: run

scrape:
	@echo "Running scrapers..."
	python3 backend/scrapers/hackernews_scraper.py
	python3 backend/scrapers/yc_scraper.py
	python3 backend/scrapers/job_postings_scraper.py
	@echo "Scraping complete. Run 'make detect' to generate wedge profiles."

detect:
	@echo "Running detectors and generating profiles..."
	python3 backend/run_detectors.py
	@echo "Done. Open http://localhost:3000 to view results."

test:
	@echo "Running tests..."
	pytest backend/tests/ -v

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f ./wie.db
	rm -rf ./logs/*.log
	@echo "Cleaned!"

docker-up:
	@echo "Starting with Docker Compose..."
	docker-compose up --build

docker-down:
	@echo "Stopping Docker Compose..."
	docker-compose down

.DEFAULT_GOAL := help
