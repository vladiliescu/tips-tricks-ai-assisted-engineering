#!/usr/bin/env python3
"""
Helper scripts for common development tasks.
Quick commands for the Predictive Analytics project.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: str, cwd: str = None) -> bool:
    """Run a command and return success status."""
    print(f"$ {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        return False


def dev():
    """Start development servers."""
    print("🚀 Starting development environment...")
    print("This will start both backend and frontend in development mode")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("Press Ctrl+C to stop\n")

    # Start backend in background
    backend_cmd = "cd app && uv run uvicorn main:app --reload --port 8000"
    frontend_cmd = "cd web-app && pnpm dev"

    print("Starting backend...")
    backend_process = subprocess.Popen(backend_cmd, shell=True)

    try:
        print("Starting frontend...")
        subprocess.run(frontend_cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        backend_process.wait()


def backend():
    """Start only the backend server."""
    print("🔧 Starting FastAPI backend...")
    return run_cmd("uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000", "app")


def frontend():
    """Start only the frontend dev server."""
    print("🎨 Starting SvelteKit frontend...")
    return run_cmd("pnpm dev", "web-app")


def build():
    """Build the frontend for production."""
    print("📦 Building frontend for production...")
    if not run_cmd("pnpm install", "web-app"):
        return False
    return run_cmd("pnpm build", "web-app")


def test():
    """Run all tests."""
    print("🧪 Running tests...")

    # Backend tests
    print("Running backend tests...")
    if not run_cmd("uv run pytest", "app"):
        print("Backend tests failed")
        return False

    # Frontend tests (if any)
    print("Running frontend tests...")
    if Path("web-app/src/lib").exists():
        run_cmd("pnpm test", "web-app")

    return True


def format_code():
    """Format all code."""
    print("🎯 Formatting code...")

    # Format Python code
    print("Formatting Python code...")
    run_cmd("uv run black .", "app")
    run_cmd("uv run isort .", "app")

    # Format frontend code (if prettier is available)
    print("Formatting frontend code...")
    run_cmd("pnpm exec prettier --write src/", "web-app")


def lint():
    """Run linting on all code."""
    print("🔍 Linting code...")

    # Python linting
    print("Linting Python code...")
    run_cmd("uv run mypy .", "app")

    # Frontend linting (if available)
    print("Checking frontend...")
    run_cmd("pnpm run check", "web-app")


def clean():
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")

    # Clean frontend build
    build_dir = Path("web-app/build")
    if build_dir.exists():
        import shutil

        shutil.rmtree(build_dir)
        print("Removed web-app/build/")

    # Clean backend static files
    static_dir = Path("app/static")
    if static_dir.exists():
        import shutil

        shutil.rmtree(static_dir)
        print("Removed app/static/")

    # Clean Python cache
    run_cmd("find . -type d -name __pycache__ -exec rm -rf {} +", ".")
    run_cmd("find . -name '*.pyc' -delete", ".")

    print("Clean completed!")


def setup():
    """Initial project setup."""
    print("⚙️  Setting up project...")

    # Setup backend
    print("Setting up backend...")
    if not run_cmd("uv sync", "app"):
        return False

    # Setup frontend
    print("Setting up frontend...")
    if not run_cmd("pnpm install", "web-app"):
        return False

    # Create .env file if it doesn't exist
    if not Path("app/.env").exists():
        import shutil

        shutil.copy("app/.env.example", "app/.env")
        print("Created app/.env from template")

    print("✅ Setup completed!")
    return True


def validate():
    """Validate project setup."""
    print("✅ Validating project setup...")
    return run_cmd("python3 test_setup.py", ".")


def deploy():
    """Build and prepare for deployment."""
    print("🚀 Preparing for deployment...")

    # Build frontend
    if not build():
        return False

    # Copy to backend static
    import shutil

    frontend_build = Path("web-app/build")
    backend_static = Path("app/static")

    if backend_static.exists():
        shutil.rmtree(backend_static)

    shutil.copytree(frontend_build, backend_static)
    print("Copied frontend build to backend static/")

    print("✅ Deployment build ready!")
    print("Deploy the app/ directory to your server")
    return True


def db_init():
    """Initialize database (placeholder)."""
    print("🗄️  Initializing database...")
    print("Database initialization not yet implemented")
    print("Future: Run Alembic migrations here")


def help_cmd():
    """Show available commands."""
    commands = {
        "dev": "Start both backend and frontend in development mode",
        "backend": "Start only the FastAPI backend server",
        "frontend": "Start only the SvelteKit frontend dev server",
        "build": "Build frontend for production",
        "test": "Run all tests",
        "format": "Format all code (Python and frontend)",
        "lint": "Run linting on all code",
        "clean": "Clean build artifacts and cache",
        "setup": "Initial project setup (install dependencies)",
        "validate": "Validate project setup",
        "deploy": "Build everything for deployment",
        "db-init": "Initialize database (placeholder)",
        "help": "Show this help message",
    }

    print("🛠️  Available Commands:")
    print("=" * 50)
    for cmd, desc in commands.items():
        print(f"  {cmd:<12} - {desc}")
    print("\nUsage: python3 scripts.py <command>")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        help_cmd()
        return

    command = sys.argv[1].replace("-", "_")

    # Map of commands to functions
    commands = {
        "dev": dev,
        "backend": backend,
        "frontend": frontend,
        "build": build,
        "test": test,
        "format": format_code,
        "lint": lint,
        "clean": clean,
        "setup": setup,
        "validate": validate,
        "deploy": deploy,
        "db_init": db_init,
        "help": help_cmd,
    }

    if command in commands:
        try:
            commands[command]()
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command: {sys.argv[1]}")
        help_cmd()
        sys.exit(1)


if __name__ == "__main__":
    main()
