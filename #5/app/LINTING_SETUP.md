# Backend Linting and Code Quality Setup

This document describes the Ruff and ty setup for the FastAPI backend application.

## Overview

The project uses modern Python tooling for code quality:

- **Ruff**: Ultra-fast Python linter and formatter (replaces Black, isort, Flake8, and more)
- **ty**: Modern type checker (alternative to mypy)

## Tools Installed

### Dependencies
- `ruff>=0.14.0` - All-in-one linter and formatter
- `ty` - Fast type checker (installed via uvx)

### Replaced Tools
This setup replaces the following traditional tools:
- ~~Black~~ → Ruff formatter
- ~~isort~~ → Ruff import sorting
- ~~Flake8~~ → Ruff linting
- ~~mypy~~ → ty type checking (via uvx)

## Configuration Files

### Ruff Configuration

#### `pyproject.toml` (Primary Config)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "PTH"]
ignore = ["E501", "B008", "A003"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### `ruff.toml` (Extended Config)
Comprehensive configuration with:
- 80+ rule categories enabled
- Per-file ignore patterns
- Import sorting configuration
- Security checks (bandit)
- Performance checks
- Code complexity checks

### ty Configuration (`ty.toml`)
```toml
[tool.ty]
python-version = "3.11"
show-error-codes = true
pretty = true
warn-return-any = true
check-untyped-defs = true
strict-optional = true
```

## Available Commands

### Individual Tools
```bash
# Ruff linting
uv run ruff check .              # Check for issues
uv run ruff check --fix .        # Auto-fix issues

# Ruff formatting
uv run ruff format .             # Format code
uv run ruff format --check .     # Check formatting

# Type checking
uvx ty check .                   # Run type checker
```

### Direct Commands
```bash
# Quick commands
uv run ruff check .              # Check linting
uv run ruff check --fix .        # Fix linting issues
uv run ruff format .             # Format code
uv run ruff format --check .     # Check formatting
uvx ty check .                   # Type checking
```

## Quality Check Script

A comprehensive bash script is available at `scripts/quality.sh`:

### Usage
```bash
# Run all checks
./scripts/quality.sh

# Auto-fix all issues
./scripts/quality.sh --fix

# Format code only
./scripts/quality.sh --format-only

# Quick check (skip type checking)
./scripts/quality.sh --quick

# Show help
./scripts/quality.sh --help
```

### Features
- **Colored output** for better readability
- **Modern type checking** with ty via uvx
- **Detailed error reporting** with fix suggestions
- **Code statistics** showing lines of code
- **Exit codes** for CI/CD integration
- **Flexible options** for different workflows

## Rules and Checks

### Ruff Linting Rules

#### Core Rules (Always Enabled)
- **E/W**: pycodestyle errors and warnings
- **F**: Pyflakes (undefined variables, imports)
- **I**: isort (import sorting)
- **N**: PEP 8 naming conventions
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (likely bugs)

#### Additional Rules (Extended Config)
- **A**: flake8-builtins (builtin shadowing)
- **C4**: flake8-comprehensions (list/dict comprehensions)
- **SIM**: flake8-simplify (code simplification)
- **TCH**: flake8-type-checking (type checking imports)
- **PTH**: flake8-use-pathlib (prefer pathlib over os.path)
- **S**: flake8-bandit (security issues)
- **PL**: Pylint rules
- **PERF**: Performance anti-patterns
- **RUF**: Ruff-specific rules

### Common Issues Found
Based on the current codebase scan:

1. **Import sorting** (I001): Imports not properly organized
2. **Path usage** (PTH110): Using `os.path.exists()` instead of `Path.exists()`
3. **Unused arguments** (ARG001): Function parameters not used
4. **Security** (S104): Binding to all interfaces (`0.0.0.0`)

## Integration with Development Workflow

### Recommended Workflow

1. **Before committing**:
   ```bash
   ./scripts/quality.sh --fix
   ```

2. **During development** (quick checks):
   ```bash
   ./scripts/quality.sh --quick --fix
   ```

3. **CI/CD pipeline**:
   ```bash
   ./scripts/quality.sh
   ```

### Editor Integration

#### VS Code
Install these extensions:
- **Ruff** (`charliermarsh.ruff`) - Official Ruff extension
- **Python** (`ms-python.python`) - Python language support

#### VS Code Settings
Add to `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    },
    "editor.formatOnSave": true
  }
}
```

#### PyCharm/IntelliJ
1. Install Ruff plugin from marketplace
2. Configure external tools for ty type checking
3. Set up file watchers for auto-formatting

## Configuration Customization

### Adding New Ruff Rules
Edit `ruff.toml` or `pyproject.toml`:

```toml
[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "PTH",
    "YOUR_NEW_RULE",  # Add here
]
```

### Ignoring Specific Rules
```toml
[tool.ruff.lint]
ignore = [
    "E501",  # Line too long (handled by formatter)
    "YOUR_RULE_TO_IGNORE",
]
```

### Per-File Ignores
```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "PLR2004"]  # Allow assertions and magic values in tests
"__init__.py" = ["F401"]          # Allow unused imports in __init__.py
```

### Customizing Formatting
```toml
[tool.ruff.format]
quote-style = "single"        # Use single quotes
line-ending = "lf"           # Force LF line endings
indent-style = "tab"         # Use tabs instead of spaces
```

## Troubleshooting

### ty Installation Issues

The ty type checker is accessed via uvx. If you encounter problems:

1. **Check installation**:
   ```bash
   uvx ty check --help
   ```

2. **Force reinstall**:
   ```bash
   uvx --force ty --version
   ```

3. **Verbose output**:
   ```bash
   uvx ty check .
   ```

### Ruff Issues

1. **Clear cache**:
   ```bash
   uv run ruff clean
   ```

2. **Check configuration**:
   ```bash
   uv run ruff check --show-settings
   ```

3. **Verbose output**:
   ```bash
   uv run ruff check --verbose .
   ```

### Performance Issues

If linting is slow:

1. **Use .ruffignore** to exclude large directories:
   ```
   __pycache__/
   .venv/
   node_modules/
   build/
   dist/
   ```

2. **Reduce rule set** for faster checks during development

3. **Use --quiet flag** to reduce output

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync --extra dev
      - name: Install ty
        run: uvx ty check --help  # This will install ty
      - name: Run quality checks
        run: ./scripts/quality.sh
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Performance Benefits

### Speed Improvements
Compared to traditional tools:
- **Ruff vs Black + isort + Flake8**: 10-100x faster
- **ty vs mypy**: 5-10x faster (when working)

### Single Tool Benefits
- Consistent configuration
- Fewer dependencies
- Faster CI/CD pipelines
- Simplified setup

## Migration Notes

### From Black + isort + Flake8
1. Remove old dependencies:
   ```bash
   uv remove --dev black isort flake8
   ```

2. Remove old config files:
   ```bash
   rm setup.cfg .flake8 pyproject.toml[tool.black] pyproject.toml[tool.isort]
   ```

3. Update scripts and CI/CD to use ruff

### From mypy
1. Remove mypy dependency:
   ```bash
   uv remove --dev mypy
   ```

2. Use ty via uvx instead:
   ```bash
   uvx ty check .
   ```

## Best Practices

### Code Organization
- Use `__init__.py` files for proper package structure
- Organize imports: stdlib → third-party → local
- Use type hints consistently
- Follow PEP 8 naming conventions

### Performance
- Use pathlib instead of os.path
- Prefer list comprehensions over loops
- Use f-strings for string formatting
- Avoid mutable default arguments

### Security
- Validate user inputs
- Use specific exception handling
- Avoid shell injection vulnerabilities
- Don't bind to all interfaces in production

## Maintenance

### Regular Updates
```bash
uv add --dev ruff@latest ty@latest
```

### Configuration Reviews
- Review and adjust rules quarterly
- Monitor new Ruff releases for new rules
- Update target Python version as needed

### Team Alignment
- Document team-specific rule exceptions
- Share editor configurations
- Regular code review focusing on quality