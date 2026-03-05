.PHONY: help install test lint format type-check security-check clean run docker-build docker-run all

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo "  make lint             - Run linting (ruff)"
	@echo "  make lint-fix         - Run linting and auto-fix issues"
	@echo "  make format           - Format code with ruff"
	@echo "  make type-check       - Run type checking with mypy"
	@echo "  make security-check   - Run security checks (bandit)"
	@echo "  make check-all        - Run all checks (lint, type, test)"
	@echo "  make clean            - Clean cache and temporary files"
	@echo "  make run              - Run the application"
	@echo "  make run-lab          - Run the application with LAB_MODE=1"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run Docker container"
	@echo "  make all              - Install, lint, test"

install:
	pip install -r requirements.txt

test:
	python3 -m pytest -v

test-cov:
	python3 -m pytest --cov=app --cov-report=html --cov-report=term

lint:
	@echo "Running ruff linter..."
	python3 -m ruff check app/ tests/

lint-fix:
	@echo "Running ruff linter with auto-fix..."
	python3 -m ruff check --fix app/ tests/

format:
	@echo "Formatting code with ruff..."
	python3 -m ruff format app/ tests/

format-check:
	@echo "Checking code formatting..."
	python3 -m ruff format --check app/ tests/

type-check:
	@echo "Running mypy type checker..."
	python3 -m mypy app/

security-check:
	@echo "Running bandit security scanner..."
	python3 -m bandit -r app/ -ll

check-all: lint type-check test
	@echo "All checks passed!"

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Clean complete!"

run:
	@echo "Starting FastAPI application..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-lab:
	@echo "Starting FastAPI application with LAB_MODE=1..."
	LAB_MODE=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	@echo "Building Docker image..."
	docker build -t devsecops-fastapi:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -d -p 8000:80 --name devsecops-fastapi devsecops-fastapi:latest

docker-stop:
	@echo "Stopping Docker container..."
	docker stop devsecops-fastapi || true
	docker rm devsecops-fastapi || true

all: install lint test
	@echo "Setup complete!"
