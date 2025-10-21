# Predictive Analytics Backend

FastAPI backend for GitHub-based effort estimation using machine learning with comprehensive code quality tooling.

## Features

- GitHub API integration for historical data collection
- Team management and parameter tracking
- ML-powered effort prediction models
- REST API for frontend integration
- SQLite database for data storage

## Quick Start

1. Install dependencies:
```bash
uv sync --extra dev
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the development server:
```bash
uv run uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Code Quality

This project uses Ruff and ty for maintaining code quality.

### Quick Commands

```bash
# Run all quality checks
./scripts/quality.sh

# Auto-fix linting and formatting issues
./scripts/quality.sh --fix

# Quick check (skip type checking)
./scripts/quality.sh --quick --fix

# Individual tools
uv run ruff check .          # Check for linting issues
uv run ruff check --fix .    # Fix linting issues
uv run ruff format .         # Format code
uv run ruff format --check . # Check formatting
uvx ty check .               # Type checking
```

### Quality Script Options

```bash
./scripts/quality.sh [OPTIONS]

--fix            Auto-fix linting and formatting issues
--format-only    Only run formatting, skip linting checks
--no-type-check  Skip type checking (faster run)
--quick          Skip type checking and only check/fix format
--help           Show help message
```

## Development

Run tests:
```bash
uv run pytest
```

### Documentation

See [LINTING_SETUP.md](LINTING_SETUP.md) for detailed configuration and troubleshooting information.
