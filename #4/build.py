#!/usr/bin/env python3
"""
Build script for integrating SvelteKit frontend with FastAPI backend.
Builds the frontend and copies static files to backend for serving.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, cwd: str = None) -> bool:
    """Run a shell command and return success status."""
    print(f"Running: {cmd}")
    if cwd:
        print(f"  in directory: {cwd}")

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, cwd=cwd, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def build_frontend():
    """Build the SvelteKit frontend."""
    print("=" * 50)
    print("Building Frontend")
    print("=" * 50)

    frontend_dir = Path("web-app")
    if not frontend_dir.exists():
        print("Error: web-app directory not found")
        return False

    # Install dependencies
    if not run_command("pnpm install", str(frontend_dir)):
        print("Failed to install frontend dependencies")
        return False

    # Build the frontend
    if not run_command("pnpm run build", str(frontend_dir)):
        print("Failed to build frontend")
        return False

    print("Frontend build completed successfully!")
    return True


def copy_static_files():
    """Copy built frontend files to backend static directory."""
    print("=" * 50)
    print("Copying Static Files")
    print("=" * 50)

    frontend_build = Path("web-app/build")
    backend_static = Path("app/static")

    if not frontend_build.exists():
        print("Error: Frontend build directory not found")
        return False

    # Remove existing static files
    if backend_static.exists():
        shutil.rmtree(backend_static)
        print("Removed existing static files")

    # Copy new build files
    try:
        shutil.copytree(frontend_build, backend_static)
        print(f"Copied frontend build to {backend_static}")
        return True
    except Exception as e:
        print(f"Error copying files: {e}")
        return False


def setup_backend():
    """Set up backend dependencies."""
    print("=" * 50)
    print("Setting Up Backend")
    print("=" * 50)

    backend_dir = Path("app")
    if not backend_dir.exists():
        print("Error: app directory not found")
        return False

    # Sync backend dependencies
    if not run_command("uv sync", str(backend_dir)):
        print("Failed to sync backend dependencies")
        return False

    print("Backend setup completed successfully!")
    return True


def start_backend():
    """Start the FastAPI backend server."""
    print("=" * 50)
    print("Starting Backend Server")
    print("=" * 50)

    backend_dir = Path("app")
    if not backend_dir.exists():
        print("Error: app directory not found")
        return False

    print("Starting server at http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")

    # Start the server (this will block)
    return run_command(
        "uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000", str(backend_dir)
    )


def main():
    """Main build process."""
    print("🚀 Building Predictive Analytics Application")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("web-app").exists() or not Path("app").exists():
        print("Error: Please run this script from the project root directory")
        print("Expected directories: web-app/ and app/")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "frontend":
            if build_frontend():
                print("✅ Frontend build completed!")
            else:
                print("❌ Frontend build failed!")
                sys.exit(1)

        elif command == "backend":
            if setup_backend():
                print("✅ Backend setup completed!")
            else:
                print("❌ Backend setup failed!")
                sys.exit(1)

        elif command == "serve":
            # Build frontend and copy files first
            if not build_frontend():
                print("❌ Frontend build failed!")
                sys.exit(1)

            if not copy_static_files():
                print("❌ Failed to copy static files!")
                sys.exit(1)

            if not setup_backend():
                print("❌ Backend setup failed!")
                sys.exit(1)

            # Start the server
            start_backend()

        elif command == "dev":
            print("Development mode: Building and starting server...")

            # Build everything
            if not setup_backend():
                print("❌ Backend setup failed!")
                sys.exit(1)

            if not build_frontend():
                print("❌ Frontend build failed!")
                sys.exit(1)

            if not copy_static_files():
                print("❌ Failed to copy static files!")
                sys.exit(1)

            print("✅ Build completed successfully!")
            print("\n🌟 Starting development server...")
            start_backend()

        else:
            print(f"Unknown command: {command}")
            print_help()
            sys.exit(1)

    else:
        # Default: full build
        print("Running full build process...")

        if not setup_backend():
            print("❌ Backend setup failed!")
            sys.exit(1)

        if not build_frontend():
            print("❌ Frontend build failed!")
            sys.exit(1)

        if not copy_static_files():
            print("❌ Failed to copy static files!")
            sys.exit(1)

        print("✅ Build completed successfully!")
        print("\n🌟 To start the server, run: python build.py serve")


def print_help():
    """Print help information."""
    print("""
Usage: python build.py [command]

Commands:
  (no args)  - Full build (backend setup + frontend build + copy files)
  frontend   - Build frontend only
  backend    - Setup backend only
  serve      - Build everything and start the server
  dev        - Development mode (build + serve with auto-reload)

Examples:
  python build.py              # Full build
  python build.py dev          # Build and start development server
  python build.py frontend     # Build frontend only
  python build.py serve        # Build everything and serve
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print_help()
    else:
        main()
