.PHONY: help test test-fast test-full test-perf test-cov test-watch lint format clean install

# Default target
help:
	@echo "Quaestor Test Suite Commands"
	@echo "============================"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests (excluding performance)"
	@echo "  make test-fast     - Run tests with fail-fast mode"
	@echo "  make test-full     - Run all tests including performance tests"
	@echo "  make test-perf     - Run only performance tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make test-watch    - Run tests in watch mode (requires pytest-watch)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Auto-format code"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install all dependencies"
	@echo "  make clean         - Clean up cache and temporary files"

# Run standard test suite (excluding performance tests)
test:
	uv run pytest -xvs

# Run tests with fail-fast mode
test-fast:
	uv run pytest -x --tb=short --maxfail=1

# Run all tests including performance tests
test-full:
	FULL_STRESS_TEST=1 uv run pytest -xvs tests/

# Run only performance tests
test-perf:
	uv run pytest -xvs tests/performance/

# Run tests with coverage
test-cov:
	uv run pytest -xvs --cov=src/quaestor --cov=src/a1 --cov-report=term-missing --cov-report=html

# Run tests in watch mode
test-watch:
	uv run pytest-watch -- -x --tb=short

# Run linting
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

# Format code
format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

# Install all dependencies
install:
	uv sync --dev
	uv run pre-commit install

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .coverage