# Use bash with strict mode (prevents silent failures)
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Default recipe
default:
    @just --list

# Create or sync virtual environment
venv:
    uv venv
    uv sync

# Re-sync dependencies (after pyproject change)
sync:
    uv sync

# Remove environment
clean-venv:
    rm -rf .venv

# Run python inside uv environment
run *args:
    uv run python {{args}}

# Python REPL
repl:
    uv run python

# Build docs
docs:
    uv run python ./scripts/generate_docs.py

# Run ruff linter
lint:
    uv run ruff check .

# Run ruff formatter
format:
    uv run ruff format .

# Run pyright type checker
typecheck:
    uv run pyright

# Build python package
build:
    rm -rf dist
    uv build

# Publish python package
publish:
    uv publish

# Run all tests
test:
    uv run pytest -v tests/unit tests/realtime

# Run unit tests
test-unit:
    uv run pytest tests/unit -v

# Run realtime websocket tests
test-realtime:
    uv run pytest tests/realtime/ -v

# Run tests with coverage report (HTML output in htmlcov/)
cov:
    uv run pytest --cov --cov-report=term-missing --cov-report=html tests/

# Download latest published OpenAPI schema from Soniox docs (YAML) into the JSON test fixture
download-schema:
    curl -sSL https://soniox.com/docs/openapi.yaml | \
        uv run python -c "import sys, json, yaml; json.dump(yaml.safe_load(sys.stdin), open('tests/data/openapi.json', 'w'), indent=2)"

# Clean caches
clean-cache:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    rm -rf .pytest_cache .mypy_cache dist build
