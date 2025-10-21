# Predictive Analytics Backend

FastAPI backend for GitHub-based effort estimation using machine learning.

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

## Development

Run tests:
```bash
uv run pytest
```

Format code:
```bash
uv run black .
uv run isort .
```

Type checking:
```bash
uv run mypy .
```
