.PHONY: help install run dev test clean init-db docker-up docker-down

help:
	@echo "Wedge Intelligence Engine (WIE) - Available Commands"
	@echo ""
	@echo "  make install      Install all dependencies"
	@echo "  make init-db      Initialize SQLite database"
	@echo "  make run          Run the full application (backend + frontend + scheduler)"
	@echo "  make dev          Run in development mode with hot reload"
	@echo "  make test         Run tests"
	@echo "  make clean        Clean up generated files and cache"
	@echo "  make docker-up    Start with Docker Compose"
	@echo "  make docker-down  Stop Docker Compose"
	@echo ""

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Node dependencies..."
	cd client && npm install
	@echo "Done!"

init-db:
	@echo "Initializing database..."
	python backend/database.py
	@echo "Database ready at ./data/wie.db"

run: init-db
	@echo "Starting Wedge Intelligence Engine..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo ""
	python backend/main.py

dev: init-db
	@echo "Starting in development mode..."
	python backend/main.py &
	cd client && npm run dev

test:
	@echo "Running tests..."
	pytest backend/tests/ -v

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf ./data/wie.db
	rm -rf ./logs/*.log
	@echo "Cleaned!"

docker-up:
	@echo "Starting with Docker Compose..."
	docker-compose up --build

docker-down:
	@echo "Stopping Docker Compose..."
	docker-compose down

.DEFAULT_GOAL := help
