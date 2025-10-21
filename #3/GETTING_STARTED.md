# Getting Started with GitHub Predictive Analytics

Welcome! This guide will help you get the GitHub Predictive Analytics application up and running on your development machine.

## What This Application Does

GitHub Predictive Analytics is an AI-powered tool that helps development teams:

- **Estimate Effort**: Predict story points and hours for development tasks
- **Track Performance**: Monitor team velocity and estimation accuracy
- **Analyze GitHub Data**: Sync and analyze repository metrics
- **Improve Planning**: Use historical data to make better project estimates

## Prerequisites

Before you start, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Verify Your Installation

```bash
python --version  # Should show 3.9+
node --version    # Should show 18+
npm --version     # Should be included with Node.js
git --version     # Any recent version
```

## Quick Start (Recommended)

The fastest way to get started is using our automated setup script:

```bash
# 1. Navigate to the project directory
cd "#3"

# 2. Run the development setup script
python scripts/start_dev.py
```

This single command will:
- ✅ Check all prerequisites
- ✅ Set up Python virtual environment
- ✅ Install backend dependencies
- ✅ Install frontend dependencies
- ✅ Initialize SQLite database with sample data
- ✅ Start backend server (http://localhost:8000)
- ✅ Start frontend server (http://localhost:5173)
- ✅ Open the application in your browser

## Manual Setup (Alternative)

If you prefer to set things up step by step:

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install Node.js dependencies
npm install
```

### Step 3: Database Setup

```bash
# From the project root directory
python database/init_db.py
```

When prompted:
- Press `y` to recreate the database if it exists
- Press `Y` (or Enter) to seed with sample data

### Step 4: Start the Servers

**Backend Server (Terminal 1):**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Frontend Server (Terminal 2):**
```bash
cd frontend
npm run dev
```

## Accessing the Application

Once everything is running:

- **Main Application**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## First Steps in the Application

### 1. Explore the Dashboard
- Visit http://localhost:5173
- View team metrics, prediction stats, and recent activity
- Check system status indicators

### 2. Browse Sample Data
The database comes pre-loaded with:
- **3 Teams**: Frontend, Backend, and DevOps teams
- **5 Team Members** with different seniority levels
- **2 Repositories** with sample issues
- **Sample Predictions** with validation data
- **Sprint Data** showing team performance

### 3. Try Core Features

**Create a Prediction:**
1. Click "New Prediction" on the dashboard
2. Enter task details (title, description, type)
3. Select a team
4. Get AI-powered estimation

**Explore Teams:**
1. Go to "Teams" in the sidebar
2. View team composition and performance metrics
3. Add new team members or create teams

**View Analytics:**
1. Visit the "Analytics" section
2. Explore team velocity and accuracy trends
3. Review prediction performance

## Configuration

### Environment Variables

Create `.env` files for customization:

**Backend (`backend/.env`):**
```env
# Copy from backend/.env.example
GITHUB_TOKEN=your_github_token_here
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
DEBUG=true
```

**Frontend (`frontend/.env`):**
```env
# Copy from frontend/.env.example
PUBLIC_API_BASE_URL=http://localhost:8000
PUBLIC_APP_NAME=GitHub Predictive Analytics
```

### GitHub Integration

To sync real GitHub data:

1. Create a GitHub Personal Access Token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate token with `repo` and `read:org` scopes
   - Add token to `GITHUB_TOKEN` in `backend/.env`

2. Use the sync feature:
   - Go to Repositories page
   - Click "Sync Repository"
   - Enter repository name (e.g., "username/repo-name")

## Troubleshooting

### Common Issues

**"Command not found" errors:**
- Ensure Python, Node.js, and npm are in your system PATH
- Try restarting your terminal after installation

**Port already in use:**
- Backend (port 8000): Stop any running FastAPI/uvicorn processes
- Frontend (port 5173): Stop any running Vite/npm dev processes

**Database errors:**
- Delete `backend/app.db` and run `python database/init_db.py` again
- Check file permissions in the backend directory

**Virtual environment issues:**
- Delete `backend/venv` directory and recreate it
- Ensure you're using the correct Python version

**Frontend build errors:**
- Delete `frontend/node_modules` and run `npm install` again
- Clear npm cache with `npm cache clean --force`

### Getting Help

1. **Check the logs**: Both servers output detailed error messages
2. **API Documentation**: Visit http://localhost:8000/docs for API details
3. **Database Issues**: Re-run the database initialization script
4. **Port Conflicts**: Use different ports in the configuration

### Development Commands

```bash
# Start only backend
python scripts/start_dev.py --backend-only

# Start only frontend
python scripts/start_dev.py --frontend-only

# Start without opening browser
python scripts/start_dev.py --no-browser

# Reset database
python database/init_db.py

# Run backend tests (if available)
cd backend && python -m pytest

# Build frontend for production
cd frontend && npm run build
```

## Next Steps

Once you have the application running:

1. **Explore the Sample Data**: Understand the data model and relationships
2. **Create Your Own Teams**: Add your actual development teams
3. **Sync GitHub Repositories**: Connect your real repositories
4. **Make Predictions**: Try estimating effort for actual tasks
5. **Validate Predictions**: Compare predictions with actual outcomes
6. **Analyze Performance**: Use the analytics to improve estimation accuracy

## Architecture Overview

- **Backend**: FastAPI (Python) - Handles API requests, database operations, and ML predictions
- **Frontend**: SvelteKit (TypeScript) - Modern reactive UI with Tailwind CSS
- **Database**: SQLite - Stores teams, predictions, GitHub data, and analytics
- **ML Models**: Scikit-learn - Regression models for effort estimation
- **Integration**: GitHub API - Syncs repository data and issues

## Development Notes

- The application uses a minimal ML implementation for demonstration
- Database schema supports complex team and prediction analytics
- Frontend is fully responsive and mobile-friendly
- API follows RESTful conventions with comprehensive documentation
- All components are designed for easy extension and customization

Happy coding! 🚀