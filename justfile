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

# Build python package
build:
    rm -rf dist
    uv build

# Publish python package
publish:
    uv publish

# Clean caches
clean-cache:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    rm -rf .pytest_cache .mypy_cache dist build
