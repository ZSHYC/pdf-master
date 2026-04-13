# ===========================================
# PDF-Master - Development Commands
# ===========================================
# Compatible with Windows Git Bash

.PHONY: install install-dev test test-cov lint format clean build help

# Default target
help:
	@echo "PDF-Master Development Commands"
	@echo ""
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run all linters"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Clean up generated files"
	@echo "  make build        - Build distribution packages"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=skills/pdf/scripts --cov-report=html --cov-report=term

# Code Quality
lint:
	@echo "Running black..."
	black --check skills/pdf/scripts tests/
	@echo "Running isort..."
	isort --check skills/pdf/scripts tests/
	@echo "Running flake8..."
	flake8 skills/pdf/scripts tests/ --max-line-length=100 --ignore=E501,W503
	@echo "Running mypy..."
	mypy skills/pdf/scripts --ignore-missing-imports

format:
	@echo "Formatting with black..."
	black skills/pdf/scripts tests/
	@echo "Sorting imports with isort..."
	isort skills/pdf/scripts tests/

# Build
build:
	python -m build

# Cleanup
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .mypy_cache
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete"

# Pre-commit
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files
