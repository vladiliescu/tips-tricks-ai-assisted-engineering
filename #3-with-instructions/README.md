# Predictive Analytics - GitHub Effort Estimation

AI-powered effort estimation for development tasks using GitHub data and team parameters.

## Overview

This application combines a **FastAPI backend** with a **SvelteKit frontend** to provide predictive analytics for software development effort estimation. It analyzes historical GitHub data (issues, PRs, commits) and team parameters to predict effort for new tasks.

## Architecture

- **Backend**: FastAPI + Python (SQLite database)
- **Frontend**: SvelteKit + TypeScript + Tailwind CSS
- **Integration**: Backend serves the built frontend as static files

## Quick Start

### Prerequisites

- Python 3.11+ with `uv` package manager
- Node.js 18+ with `pnpm` package manager
- Git

### Option 1: Full Development Setup

```bash
# Clone and navigate to project
git clone <repository-url>
cd #3-with-instructions

# Build and start development server
python build.py dev
```

This will:
1. Install backend dependencies
2. Install frontend dependencies  
3. Build the frontend
4. Copy static files to backend
5. Start the server at http://localhost:8000

### Option 2: Step-by-Step Setup

```bash
# 1. Setup backend
python build.py backend

# 2. Build frontend
python build.py frontend

# 3. Start the integrated server
python build.py serve
```

## Build Commands

```bash
python build.py              # Full build (no server start)
python build.py dev          # Build + start development server
python build.py frontend     # Build frontend only
python build.py backend      # Setup backend only
python build.py serve        # Build everything + start server
```

## Development

### Backend Development

```bash
cd app

# Install dependencies
uv sync --extra dev

# Start backend only (API mode)
uv run uvicorn main:app --reload --port 8000

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .
```

### Frontend Development

```bash
cd web-app

# Install dependencies
pnpm install

# Start dev server (requires backend running on :8000)
pnpm dev

# Build for production
pnpm build

# Preview build
pnpm preview
```

## API Documentation

Once running, visit:
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## Features

### Current (MVP)
- ✅ Basic project structure
- ✅ FastAPI backend with health endpoints
- ✅ SvelteKit frontend with Tailwind CSS
- ✅ Frontend/backend integration
- ✅ Repository management UI
- ✅ Team management UI  
- ✅ Prediction interface UI
- ✅ Build system for deployment

### Planned
- [ ] GitHub API integration
- [ ] Database models and migrations
- [ ] Authentication & authorization
- [ ] Data collection from GitHub
- [ ] ML model training pipeline
- [ ] Real prediction algorithms
- [ ] Team parameter tracking
- [ ] Historical data analysis
- [ ] Prediction accuracy tracking

## Project Structure

```
#3-with-instructions/
├── app/                     # FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── pyproject.toml      # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── static/             # Built frontend files (auto-generated)
├── web-app/                # SvelteKit frontend
│   ├── src/
│   │   ├── routes/         # Application pages
│   │   ├── lib/            # Shared components
│   │   └── app.css         # Global styles
│   ├── package.json        # Node.js dependencies
│   └── svelte.config.js    # SvelteKit configuration
├── docs/
│   └── SPEC.md             # Detailed specification
├── build.py                # Build and deployment script
└── README.md               # This file
```

## Configuration

### Backend Configuration

Copy `app/.env.example` to `app/.env` and configure:

```bash
# Database
DATABASE_URL=sqlite:///./predictive_analytics.db

# GitHub API
GITHUB_TOKEN=your_github_token_here

# JWT Secret
SECRET_KEY=your_super_secret_jwt_key_here

# Environment
ENVIRONMENT=development
```

### CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:5173` (SvelteKit dev server)
- `http://localhost:4173` (SvelteKit preview server)

## Deployment

The build system creates a single deployable backend that serves both API and frontend:

```bash
# Build for production
python build.py

# Deploy the app/ directory to your server
# The backend will serve the frontend at the root path
```

## Contributing

1. Follow the existing code style
2. Backend: Use `black` and `isort` for formatting
3. Frontend: Follow SvelteKit and TypeScript best practices
4. Test your changes with `python build.py dev`

## License

[Your License Here]