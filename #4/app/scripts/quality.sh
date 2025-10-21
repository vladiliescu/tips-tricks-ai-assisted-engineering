#!/bin/bash

# Backend Quality Check Script
# This script runs Ruff and ty (type checker) for comprehensive Python code quality

set -e  # Exit on any error

echo "🐍 Running Backend Quality Checks..."
echo "=================================="

# Change to the app directory
cd "$(dirname "$0")/.."

# Function to print colored output
print_status() {
    echo -e "\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m$1\033[0m"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "❌ Error: Not in app directory or pyproject.toml not found"
    exit 1
fi

# Parse command line arguments
RUFF_FIX=false
TYPE_CHECK=true
QUICK=false
FORMAT_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            RUFF_FIX=true
            shift
            ;;
        --format-only)
            FORMAT_ONLY=true
            shift
            ;;
        --no-type-check)
            TYPE_CHECK=false
            shift
            ;;
        --quick)
            QUICK=true
            TYPE_CHECK=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fix            Auto-fix linting and formatting issues with Ruff"
            echo "  --format-only    Only run formatting, skip linting checks"
            echo "  --no-type-check  Skip type checking (faster run)"
            echo "  --quick          Skip type checking and only check/fix format"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Check everything"
            echo "  $0 --fix             # Auto-fix issues"
            echo "  $0 --quick --fix     # Quick format fix"
            echo "  $0 --format-only     # Just format code"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for available options"
            exit 1
            ;;
    esac
done

# Track overall success
OVERALL_SUCCESS=true

# 1. Ruff Linting and Formatting
if [ "$FORMAT_ONLY" = true ]; then
    print_status "🎨 Formatting code with Ruff..."
    if uv run ruff format .; then
        print_success "✅ Code formatting complete"
    else
        print_error "❌ Code formatting failed"
        OVERALL_SUCCESS=false
    fi
else
    print_status "🔧 Running Ruff linter..."
    if [ "$RUFF_FIX" = true ]; then
        if uv run ruff check --fix .; then
            print_success "✅ Ruff linting issues fixed"
        else
            print_error "❌ Failed to fix some linting issues"
            OVERALL_SUCCESS=false
        fi

        # Also format after fixing
        echo ""
        print_status "🎨 Formatting code with Ruff..."
        if uv run ruff format .; then
            print_success "✅ Code formatting complete"
        else
            print_error "❌ Code formatting failed"
            OVERALL_SUCCESS=false
        fi
    else
        if uv run ruff check .; then
            print_success "✅ No linting issues found"
        else
            print_error "❌ Linting issues found"
            echo "💡 Run with --fix to auto-fix issues"
            OVERALL_SUCCESS=false
        fi

        # Check formatting
        echo ""
        print_status "🎨 Checking code formatting..."
        if uv run ruff format --check .; then
            print_success "✅ Code formatting is correct"
        else
            print_error "❌ Code formatting issues found"
            echo "💡 Run with --fix to auto-fix formatting"
            OVERALL_SUCCESS=false
        fi
    fi
fi

echo ""

# 2. Type Checking (if enabled)
if [ "$TYPE_CHECK" = true ]; then
    print_status "🔍 Running type checking..."

    # Use uvx ty for type checking
    if uvx ty check . 2>/dev/null; then
        print_success "✅ Type checking passed (ty)"
    else
        # Check if ty command exists but failed
        ty_exit_code=$?
        if [ $ty_exit_code -eq 127 ] || [ $ty_exit_code -eq 2 ]; then
            print_warning "⚠️  ty not available via uvx, skipping type checking"
            echo "💡 Make sure ty is available: uvx ty --version"
        else
            print_error "❌ Type checking failed (ty)"
            OVERALL_SUCCESS=false
        fi
    fi
    echo ""
fi

# 3. Quick Statistics
print_status "📊 Code Statistics..."
if command -v uv run ruff &> /dev/null; then
    echo "Lines of code (excluding comments/blanks):"
    find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*" | xargs wc -l 2>/dev/null | tail -1 || echo "Could not count lines"
fi
echo ""

# Summary
echo "=================================="
if [ "$OVERALL_SUCCESS" = true ]; then
    print_success "🎉 All quality checks passed!"
    echo ""
    echo "Your Python code is:"
    echo "  ✅ Properly formatted"
    echo "  ✅ Following linting rules"
    if [ "$TYPE_CHECK" = true ]; then
        echo "  ✅ Type-safe"
    fi
    exit 0
else
    print_error "💥 Some quality checks failed"
    echo ""
    echo "Quick fixes:"
    echo "  • Fix linting and formatting: $0 --fix"
    echo "  • Format only:                $0 --format-only"
    echo "  • Quick fix (no type check):  $0 --quick --fix"
    echo ""
    echo "For detailed help: $0 --help"
    exit 1
fi
