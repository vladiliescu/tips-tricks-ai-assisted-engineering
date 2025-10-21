#!/bin/bash

# Frontend Quality Check Script
# This script runs ESLint, Prettier, and svelte-check for comprehensive code quality

set -e  # Exit on any error

echo "🔍 Running Frontend Quality Checks..."
echo "=================================="

# Change to the web-app directory
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

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "❌ Error: Not in web-app directory or package.json not found"
    exit 1
fi

# Parse command line arguments
FORMAT_FIX=false
LINT_FIX=false
QUICK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --format-fix)
            FORMAT_FIX=true
            shift
            ;;
        --lint-fix)
            LINT_FIX=true
            shift
            ;;
        --fix)
            FORMAT_FIX=true
            LINT_FIX=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --format-fix    Auto-fix formatting issues with Prettier"
            echo "  --lint-fix      Auto-fix linting issues with ESLint"
            echo "  --fix           Auto-fix both formatting and linting issues"
            echo "  --quick         Skip type checking (faster run)"
            echo "  -h, --help      Show this help message"
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

# 1. Format Check/Fix
print_status "📝 Checking code formatting with Prettier..."
if [ "$FORMAT_FIX" = true ]; then
    if pnpm run format; then
        print_success "✅ Code formatting fixed"
    else
        print_error "❌ Failed to fix formatting"
        OVERALL_SUCCESS=false
    fi
else
    if pnpm run format:check; then
        print_success "✅ Code formatting is correct"
    else
        print_error "❌ Code formatting issues found"
        echo "💡 Run with --format-fix to auto-fix formatting issues"
        OVERALL_SUCCESS=false
    fi
fi

echo ""

# 2. Lint Check/Fix
print_status "🔧 Running ESLint..."
if [ "$LINT_FIX" = true ]; then
    if pnpm run lint:fix; then
        print_success "✅ Linting issues fixed"
    else
        print_error "❌ Failed to fix linting issues"
        OVERALL_SUCCESS=false
    fi
else
    if pnpm run lint; then
        print_success "✅ No linting issues found"
    else
        print_error "❌ Linting issues found"
        echo "💡 Run with --lint-fix to auto-fix linting issues"
        OVERALL_SUCCESS=false
    fi
fi

echo ""

# 3. Type Check (skip if --quick)
if [ "$QUICK" = false ]; then
    print_status "🔍 Running Svelte type checking..."
    if pnpm run check; then
        print_success "✅ Type checking passed"
    else
        print_error "❌ Type checking failed"
        OVERALL_SUCCESS=false
    fi
    echo ""
fi

# Summary
echo "=================================="
if [ "$OVERALL_SUCCESS" = true ]; then
    print_success "🎉 All quality checks passed!"
    exit 0
else
    print_error "💥 Some quality checks failed"
    echo ""
    echo "Quick fixes:"
    echo "  • Format issues: $0 --format-fix"
    echo "  • Lint issues:   $0 --lint-fix"
    echo "  • Both:          $0 --fix"
    exit 1
fi
