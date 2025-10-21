#!/usr/bin/env python3
"""
Development startup script for GitHub Predictive Analytics.

This script helps start the development environment by:
1. Checking prerequisites
2. Starting the backend server
3. Starting the frontend development server
4. Opening the application in the browser

Usage:
    python scripts/start_dev.py [--backend-only] [--frontend-only] [--no-browser]
"""

import os
import sys
import subprocess
import time
import webbrowser
import argparse
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests


class Colors:
    """ANSI color codes for terminal output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_colored(message, color=Colors.WHITE):
    """Print a colored message to the terminal."""
    print(f"{color}{message}{Colors.END}")


def print_header(title):
    """Print a formatted header."""
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored(f"  {title}", Colors.CYAN + Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)


def print_step(step, message):
    """Print a step with number."""
    print_colored(f"\n{step}. {message}", Colors.BLUE + Colors.BOLD)


def print_success(message):
    """Print a success message."""
    print_colored(f"✅ {message}", Colors.GREEN)


def print_error(message):
    """Print an error message."""
    print_colored(f"❌ {message}", Colors.RED)


def print_warning(message):
    """Print a warning message."""
    print_colored(f"⚠️  {message}", Colors.YELLOW)


def print_info(message):
    """Print an info message."""
    print_colored(f"ℹ️  {message}", Colors.BLUE)


class DevEnvironment:
    """Manages the development environment."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.processes = []

    def check_prerequisites(self):
        """Check if all prerequisites are installed."""
        print_step("1", "Checking prerequisites...")

        # Check Python
        try:
            python_version = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            print_success(f"Python: {python_version}")
        except subprocess.CalledProcessError:
            print_error("Python is not installed or not accessible")
            return False

        # Check Node.js
        try:
            node_version = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=True
            ).stdout.strip()
            print_success(f"Node.js: {node_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("Node.js is not installed or not in PATH")
            return False

        # Check npm
        try:
            npm_version = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, check=True
            ).stdout.strip()
            print_success(f"npm: v{npm_version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error("npm is not installed or not accessible")
            return False

        return True

    def check_directories(self):
        """Check if project directories exist."""
        print_step("2", "Checking project structure...")

        if not self.backend_dir.exists():
            print_error(f"Backend directory not found: {self.backend_dir}")
            return False
        print_success(f"Backend directory: {self.backend_dir}")

        if not self.frontend_dir.exists():
            print_error(f"Frontend directory not found: {self.frontend_dir}")
            return False
        print_success(f"Frontend directory: {self.frontend_dir}")

        return True

    def setup_backend(self):
        """Set up the backend environment."""
        print_step("3", "Setting up backend...")

        # Check if virtual environment exists
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            print_info("Creating Python virtual environment...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "venv", "venv"],
                    cwd=self.backend_dir,
                    check=True,
                )
                print_success("Virtual environment created")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to create virtual environment: {e}")
                return False

        # Check if dependencies are installed
        requirements_file = self.backend_dir / "requirements.txt"
        if requirements_file.exists():
            # Get the python executable from the virtual environment
            if os.name == "nt":  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:  # Unix/Linux/macOS
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"

            if not python_exe.exists():
                print_error("Virtual environment Python executable not found")
                return False

            print_info("Installing/checking Python dependencies...")
            try:
                subprocess.run(
                    [str(pip_exe), "install", "-r", "requirements.txt"],
                    cwd=self.backend_dir,
                    check=True,
                )
                print_success("Backend dependencies ready")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install backend dependencies: {e}")
                return False
        else:
            print_warning(
                "requirements.txt not found, skipping dependency installation"
            )

        return True

    def setup_frontend(self):
        """Set up the frontend environment."""
        print_step("4", "Setting up frontend...")

        # Check if node_modules exists
        node_modules = self.frontend_dir / "node_modules"
        package_json = self.frontend_dir / "package.json"

        if not package_json.exists():
            print_error("package.json not found in frontend directory")
            return False

        if not node_modules.exists():
            print_info("Installing Node.js dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd=self.frontend_dir, check=True)
                print_success("Frontend dependencies installed")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install frontend dependencies: {e}")
                return False
        else:
            print_success("Frontend dependencies already installed")

        return True

    def initialize_database(self):
        """Initialize the database if needed."""
        print_step("5", "Checking database...")

        db_init_script = self.project_root / "database" / "init_db.py"
        if db_init_script.exists():
            # Check if database file exists (for SQLite)
            db_file = self.backend_dir / "app.db"
            if not db_file.exists():
                print_info("Database not found. Initializing...")
                try:
                    subprocess.run(
                        [sys.executable, str(db_init_script)],
                        cwd=self.project_root,
                        input="y\n",  # Auto-answer yes to seed sample data
                        text=True,
                        check=True,
                    )
                    print_success("Database initialized with sample data")
                except subprocess.CalledProcessError as e:
                    print_warning(f"Database initialization may have failed: {e}")
            else:
                print_success("Database file exists")
        else:
            print_warning("Database initialization script not found")

        return True

    def start_backend(self):
        """Start the backend server."""
        print_info("Starting backend server...")

        # Get the python executable from the virtual environment
        venv_path = self.backend_dir / "venv"
        if os.name == "nt":  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_path / "bin" / "python"

        if not python_exe.exists():
            # Fallback to system python
            python_exe = sys.executable

        try:
            process = subprocess.Popen(
                [
                    str(python_exe),
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--reload",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.processes.append(("Backend", process))

            # Wait a bit and check if it started successfully
            time.sleep(3)
            if process.poll() is None:
                print_success("Backend server started on http://localhost:8000")
                return True
            else:
                stdout, stderr = process.communicate()
                print_error(f"Backend server failed to start: {stderr}")
                return False

        except Exception as e:
            print_error(f"Failed to start backend server: {e}")
            return False

    def start_frontend(self):
        """Start the frontend development server."""
        print_info("Starting frontend development server...")

        try:
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.processes.append(("Frontend", process))

            # Wait a bit and check if it started successfully
            time.sleep(3)
            if process.poll() is None:
                print_success(
                    "Frontend development server started on http://localhost:5173"
                )
                return True
            else:
                stdout, stderr = process.communicate()
                print_error(f"Frontend server failed to start: {stderr}")
                return False

        except Exception as e:
            print_error(f"Failed to start frontend server: {e}")
            return False

    def wait_for_backend(self, timeout=30):
        """Wait for the backend server to be ready."""
        print_info("Waiting for backend server to be ready...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print_success("Backend server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)

        print_warning("Backend server took longer than expected to start")
        return False

    def open_browser(self):
        """Open the application in the default browser."""
        print_info("Opening application in browser...")
        try:
            webbrowser.open("http://localhost:5173")
            print_success("Application opened in browser")
        except Exception as e:
            print_warning(f"Failed to open browser: {e}")
            print_info("Please manually open http://localhost:5173 in your browser")

    def cleanup(self):
        """Clean up running processes."""
        print_info("\nStopping development servers...")

        for name, process in self.processes:
            if process.poll() is None:
                print_info(f"Stopping {name} server...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print_success(f"{name} server stopped")
                except subprocess.TimeoutExpired:
                    print_warning(f"Force killing {name} server...")
                    process.kill()

        print_success("Development environment stopped")

    def run(self, backend_only=False, frontend_only=False, no_browser=False):
        """Run the development environment."""

        def signal_handler(signum, frame):
            print_info("\nReceived interrupt signal...")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            # Prerequisites check
            if not self.check_prerequisites():
                return False

            if not self.check_directories():
                return False

            # Setup
            if not backend_only:
                if not self.setup_frontend():
                    return False

            if not frontend_only:
                if not self.setup_backend():
                    return False

                if not self.initialize_database():
                    return False

            print_step("6", "Starting development servers...")

            # Start servers
            if not frontend_only:
                if not self.start_backend():
                    return False

            if not backend_only:
                if not self.start_frontend():
                    return False

            # Wait for backend to be ready
            if not frontend_only:
                self.wait_for_backend()

            # Open browser
            if not backend_only and not no_browser:
                time.sleep(2)  # Give frontend a moment to fully start
                self.open_browser()

            # Print status
            print_header("Development Environment Ready!")
            if not frontend_only:
                print_success("Backend API: http://localhost:8000")
                print_success("API Docs: http://localhost:8000/docs")
            if not backend_only:
                print_success("Frontend App: http://localhost:5173")
            print_info("Press Ctrl+C to stop all servers")

            # Keep running
            try:
                while True:
                    # Check if any process has died
                    for name, process in self.processes:
                        if process.poll() is not None:
                            print_error(f"{name} server has stopped unexpectedly")
                            return False
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        except Exception as e:
            print_error(f"Unexpected error: {e}")
            return False
        finally:
            self.cleanup()

        return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Start the GitHub Predictive Analytics development environment"
    )
    parser.add_argument(
        "--backend-only", action="store_true", help="Start only the backend server"
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Start only the frontend development server",
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't automatically open the browser"
    )

    args = parser.parse_args()

    if args.backend_only and args.frontend_only:
        print_error("Cannot specify both --backend-only and --frontend-only")
        return 1

    print_header("GitHub Predictive Analytics - Development Environment")

    env = DevEnvironment()
    success = env.run(
        backend_only=args.backend_only,
        frontend_only=args.frontend_only,
        no_browser=args.no_browser,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
