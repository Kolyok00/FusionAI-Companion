# GarvisNeuralMind v2 - Makefile
# Easy build and development commands

.PHONY: help install dev test build run clean docker-build docker-run docker-stop

# Default target
help:
	@echo "GarvisNeuralMind v2 - Build Commands"
	@echo "=================================="
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  build       Build application"
	@echo "  run         Run production server"
	@echo "  clean       Clean build artifacts"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker Compose"
	@echo "  docker-stop  Stop Docker services"
	@echo "  docker-logs  View Docker logs"

# Python environment setup
install:
	@echo "Installing dependencies..."
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt

# Development server
dev:
	@echo "Starting development server..."
	python3 src/main.py

# Test suite
test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v

# Build application
build:
	@echo "Building application..."
	python3 -m py_compile src/main.py
	find . -name "*.py" -exec python3 -m py_compile {} \;

# Production server
run:
	@echo "Starting production server..."
	python3 src/main.py --production

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyo" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t garvis-neuralmind:latest .

docker-run:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Viewing Docker logs..."
	docker-compose logs -f

# Development with Docker
docker-dev:
	@echo "Starting development environment with Docker..."
	docker-compose --profile dev up -d

# GPU-enabled Docker
docker-gpu:
	@echo "Starting GPU-enabled environment with Docker..."
	docker-compose --profile gpu up -d

# Database operations
db-migrate:
	@echo "Running database migrations..."
	python3 -m alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose exec postgres psql -U garvis -d garvis_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker-compose exec postgres psql -U garvis -d garvis_db -f /docker-entrypoint-initdb.d/init_db.sql

# Lint and format
lint:
	@echo "Running linter..."
	python3 -m flake8 src/
	python3 -m black --check src/

format:
	@echo "Formatting code..."
	python3 -m black src/

# Check dependencies
check-deps:
	@echo "Checking dependencies..."
	python3 -m pip check

# Security check
security-check:
	@echo "Running security checks..."
	python3 -m safety check

# Full setup for new environment
setup: install build
	@echo "Setting up environment..."
	cp .env.example .env
	mkdir -p logs data uploads
	@echo "Setup complete! Edit .env file with your configuration."