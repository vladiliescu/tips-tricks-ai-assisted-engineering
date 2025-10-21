# Predictive Analytics for GitHub Teams

A web application that analyzes GitHub repository data and team parameters to predict effort estimation for future tasks and features.

## Project Overview

This application combines historical GitHub data (issues, PRs, commits) with team metadata (size, seniority, experience) to train predictive models that can estimate effort for new development tasks.

### Core Features

- **GitHub Integration**: Connect to repositories and extract historical data
- **Team Management**: Define team composition and experience levels
- **Effort Prediction**: ML-powered estimates for new tasks/features
- **Analytics Dashboard**: Insights on team velocity and estimation accuracy
- **Manual Input**: Add custom data points for improved predictions

## Architecture

- **Backend**: Python FastAPI with SQLite database
- **Frontend**: SvelteKit web application
- **ML Models**: Regression and NLP-enhanced prediction models
- **Integration**: REST API communication between frontend and backend

## Project Structure

```
├── backend/           # FastAPI application
│   ├── app/          # Main application code
│   ├── models/       # Database models
│   ├── api/          # API endpoints
│   └── ml/           # Machine learning components
├── frontend/         # SvelteKit application
│   ├── src/          # Source code
│   └── static/       # Static assets
├── database/         # Database schema and migrations
├── docs/             # Project documentation
└── scripts/          # Utility scripts
```

## Quick Start

The fastest way to get the development environment running is to use our automated startup script:

```bash
# Clone and navigate to the project
git clone <repository-url>
cd "2025 - Using AI to develop MVPs - Lite/code/#3"

# Start everything with one command
python scripts/start_dev.py
```

This script will:
- Check all prerequisites (Python 3.9+, Node.js 18+)
- Set up Python virtual environment and install backend dependencies
- Install frontend dependencies
- Initialize the database with sample data
- Start both backend and frontend servers
- Open the application in your browser

### Manual Setup

If you prefer to set things up manually:

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
```

#### 3. Database Setup
```bash
python database/init_db.py
```

#### 4. Start Development Servers
```bash
# Terminal 1 - Backend (runs on http://localhost:8000)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend (runs on http://localhost:5173)
cd frontend
npm run dev
```

## Environment Configuration

Copy the example environment files and customize as needed:

```bash
# Backend configuration
cp backend/.env.example backend/.env

# Frontend configuration  
cp frontend/.env.example frontend/.env
```

Key configuration options:
- `GITHUB_TOKEN`: Your GitHub personal access token for API access
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `PUBLIC_API_BASE_URL`: Backend API URL for frontend integration

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Development Workflow

1. **Backend** (FastAPI): http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

2. **Frontend** (SvelteKit): http://localhost:5173
   - Auto-reloads on file changes
   - Built with TypeScript and Tailwind CSS

3. **Database**: SQLite (default) with sample data included

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License