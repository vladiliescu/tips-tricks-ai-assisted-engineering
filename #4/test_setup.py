#!/usr/bin/env python3
"""
Setup validation script for Predictive Analytics project.
Tests that both backend and frontend are properly configured.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_command(cmd):
    """Check if a command exists."""
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_file_exists(path):
    """Check if file exists."""
    return Path(path).exists()


def test_backend():
    """Test backend setup."""
    print("🔧 Testing Backend Setup")
    print("-" * 30)

    # Check if app directory exists
    if not check_file_exists("app"):
        print("❌ app/ directory not found")
        return False

    # Check main files
    required_files = ["app/main.py", "app/pyproject.toml", "app/.env.example"]

    for file in required_files:
        if check_file_exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            return False

    # Test Python import
    try:
        os.chdir("app")
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                "from main import app; print('FastAPI app imported successfully')",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ FastAPI app imports correctly")
        print(f"   {result.stdout.strip()}")
        os.chdir("..")
        return True
    except Exception as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        os.chdir("..")
        return False


def test_frontend():
    """Test frontend setup."""
    print("\n🎨 Testing Frontend Setup")
    print("-" * 30)

    # Check if web-app directory exists
    if not check_file_exists("web-app"):
        print("❌ web-app/ directory not found")
        return False

    # Check main files
    required_files = [
        "web-app/package.json",
        "web-app/svelte.config.js",
        "web-app/src/routes/+page.svelte",
        "web-app/src/routes/+layout.svelte",
    ]

    for file in required_files:
        if check_file_exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            return False

    # Check package.json content
    try:
        with open("web-app/package.json", "r") as f:
            pkg = json.load(f)

        if "svelte" in pkg.get("devDependencies", {}):
            print("✅ Svelte dependency found")
        else:
            print("❌ Svelte dependency not found")
            return False

        if "tailwindcss" in pkg.get("devDependencies", {}):
            print("✅ Tailwind CSS dependency found")
        else:
            print("❌ Tailwind CSS dependency not found")
            return False

    except Exception as e:
        print(f"❌ Failed to read package.json: {e}")
        return False

    return True


def test_integration():
    """Test backend/frontend integration."""
    print("\n🔗 Testing Integration")
    print("-" * 30)

    # Check CORS configuration in main.py
    try:
        with open("app/main.py", "r") as f:
            content = f.read()

        if "CORSMiddleware" in content:
            print("✅ CORS middleware configured")
        else:
            print("❌ CORS middleware not found")
            return False

        if "localhost:5173" in content:
            print("✅ SvelteKit dev server CORS configured")
        else:
            print("❌ SvelteKit dev server CORS not configured")
            return False

    except Exception as e:
        print(f"❌ Failed to check CORS config: {e}")
        return False

    # Check API endpoints
    try:
        with open("app/main.py", "r") as f:
            content = f.read()

        api_endpoints = [
            "/api/health",
            "/api/repositories",
            "/api/teams",
            "/api/predictions",
        ]
        for endpoint in api_endpoints:
            if endpoint in content:
                print(f"✅ API endpoint {endpoint} defined")
            else:
                print(f"❌ API endpoint {endpoint} not found")
                return False

    except Exception as e:
        print(f"❌ Failed to check API endpoints: {e}")
        return False

    return True


def check_dependencies():
    """Check required tools."""
    print("📦 Checking Dependencies")
    print("-" * 30)

    # Check Python/uv
    if check_command("uv --version"):
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"✅ uv: {result.stdout.strip()}")
    else:
        print("❌ uv not found - install from https://docs.astral.sh/uv/")
        return False

    # Check Node.js/pnpm
    if check_command("pnpm --version"):
        result = subprocess.run(["pnpm", "--version"], capture_output=True, text=True)
        print(f"✅ pnpm: {result.stdout.strip()}")
    else:
        print("❌ pnpm not found - install from https://pnpm.io/")
        return False

    return True


def main():
    """Run all tests."""
    print("🚀 Predictive Analytics - Setup Validation")
    print("=" * 50)

    # Check we're in the right directory
    if not check_file_exists("app") or not check_file_exists("web-app"):
        print("❌ Please run this script from the project root directory")
        print("   Expected directories: app/ and web-app/")
        sys.exit(1)

    all_tests_passed = True

    # Run tests
    tests = [
        ("Dependencies", check_dependencies),
        ("Backend", test_backend),
        ("Frontend", test_frontend),
        ("Integration", test_integration),
    ]

    for test_name, test_func in tests:
        try:
            if not test_func():
                all_tests_passed = False
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            all_tests_passed = False

    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start backend: cd app && uv run uvicorn main:app --reload")
        print("2. Start frontend: cd web-app && pnpm dev")
        print("3. Or use build script: python build.py dev")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
