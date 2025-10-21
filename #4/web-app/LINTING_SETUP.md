# Frontend Linting and Code Quality Setup

This document describes the ESLint, Prettier, and svelte-check setup for the SvelteKit frontend application.

## Overview

The project uses three main tools for code quality:

- **ESLint**: JavaScript/TypeScript linting and code analysis
- **Prettier**: Code formatting
- **svelte-check**: Svelte-specific type checking and diagnostics

## Tools Installed

### ESLint Dependencies

- `eslint` - Core ESLint functionality
- `@eslint/js` - ESLint JavaScript configurations
- `typescript-eslint` - TypeScript support for ESLint
- `eslint-plugin-svelte` - Svelte-specific ESLint rules
- `eslint-config-prettier` - Disables ESLint rules that conflict with Prettier
- `@eslint/compat` - Compatibility utilities for ESLint configs

### Prettier Dependencies

- `prettier` - Core Prettier functionality
- `prettier-plugin-svelte` - Svelte formatting support

### Type Checking

- `svelte-check` - Already included in the project for Svelte type checking

## Configuration Files

### ESLint Configuration (`eslint.config.js`)

Uses the new flat config format with:

- JavaScript recommended rules
- TypeScript recommended rules
- Svelte recommended rules
- Prettier compatibility
- Browser globals (fetch, console, setTimeout, etc.)
- Custom rules for TypeScript and Svelte

Key rules configured:

- `@typescript-eslint/no-unused-vars`: Error for unused variables (ignores variables starting with `_`)
- `@typescript-eslint/no-explicit-any`: Warning for explicit `any` types
- `svelte/no-at-html-tags`: Warning for `@html` usage
- `svelte/no-target-blank`: Error for unsafe `target="_blank"` links
- `svelte/require-each-key`: Warning for missing keys in `{#each}` blocks
- `no-console`: Warning for console statements
- `prefer-const`: Error for variables that should be const

### Prettier Configuration (`.prettierrc`)

Configured for consistent formatting:

- Uses tabs for indentation
- Single quotes for strings
- No trailing commas
- 100 character line width
- Svelte plugin integration

### Prettier Ignore (`.prettierignore`)

Excludes build outputs, lock files, and configuration files that should maintain their format.

## Available Scripts

The following npm scripts are available in `package.json`:

### Individual Tools

- `pnpm run lint` - Run ESLint to check for issues
- `pnpm run lint:fix` - Run ESLint and automatically fix issues
- `pnpm run format` - Format code with Prettier
- `pnpm run format:check` - Check if code is formatted correctly
- `pnpm run check` - Run svelte-check for type checking
- `pnpm run check:watch` - Run svelte-check in watch mode

### Combined Scripts

- `pnpm run quality:check` - Run format check, lint check, and type check
- `pnpm run quality` - Auto-fix formatting and linting, then run type check

## Quality Check Script

A comprehensive bash script is available at `scripts/quality.sh` that provides:

### Usage

```bash
# Run all checks
./scripts/quality.sh

# Auto-fix formatting issues
./scripts/quality.sh --format-fix

# Auto-fix linting issues
./scripts/quality.sh --lint-fix

# Auto-fix both formatting and linting
./scripts/quality.sh --fix

# Skip type checking for faster runs
./scripts/quality.sh --quick

# Show help
./scripts/quality.sh --help
```

### Features

- Colored output for better readability
- Detailed error reporting
- Automatic fix suggestions
- Option to skip slow type checking
- Exit codes for CI/CD integration

## Integration with Development Workflow

### Recommended Workflow

1. **Before committing**:

   ```bash
   pnpm run quality
   ```

2. **During development** (quick checks):

   ```bash
   ./scripts/quality.sh --quick --fix
   ```

3. **CI/CD pipeline**:
   ```bash
   pnpm run quality:check
   ```

### Editor Integration

For the best development experience, configure your editor to:

1. **ESLint**: Enable ESLint extension/plugin
2. **Prettier**: Enable format-on-save with Prettier
3. **TypeScript**: Enable TypeScript language server

### VS Code Settings Example

Add to `.vscode/settings.json`:

```json
{
	"editor.formatOnSave": true,
	"editor.defaultFormatter": "esbenp.prettier-vscode",
	"editor.codeActionsOnSave": {
		"source.fixAll.eslint": true
	},
	"eslint.validate": ["javascript", "typescript", "svelte"]
}
```

## Common Issues and Solutions

### 1. ESLint Errors for Browser Globals

**Problem**: ESLint complains about `fetch`, `console`, etc.
**Solution**: These are configured as globals in `eslint.config.js`

### 2. Prettier vs ESLint Conflicts

**Problem**: Prettier and ESLint rules conflict
**Solution**: `eslint-config-prettier` is configured to disable conflicting rules

### 3. Svelte-specific Linting Issues

**Problem**: ESLint doesn't understand Svelte syntax
**Solution**: `eslint-plugin-svelte` provides Svelte-specific rules

### 4. Type Checking Performance

**Problem**: `svelte-check` is slow
**Solution**: Use `--quick` flag to skip type checking during development

## Customization

### Adding New ESLint Rules

Edit `eslint.config.js` and add rules to the `rules` object:

```javascript
{
  rules: {
    // Your custom rules here
    'no-var': 'error',
    'prefer-arrow-callback': 'warn'
  }
}
```

### Customizing Prettier

Edit `.prettierrc` to change formatting preferences:

```json
{
	"useTabs": false,
	"tabWidth": 2,
	"singleQuote": false
}
```

### Ignoring Files

- **ESLint**: Add patterns to the `ignores` array in `eslint.config.js`
- **Prettier**: Add patterns to `.prettierignore`
- **svelte-check**: Uses TypeScript's exclude patterns from `tsconfig.json`

## Troubleshooting

### Clear Caches

If you encounter strange issues:

```bash
# Clear ESLint cache
rm -rf .eslintcache

# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Check Tool Versions

Ensure all tools are up-to-date:

```bash
pnpm list eslint prettier svelte-check
```

### Verbose Output

For debugging, run tools with verbose flags:

```bash
pnpm run lint -- --debug
prettier --check . --debug-check
```

## Maintenance

### Regular Updates

Keep linting tools updated regularly:

```bash
pnpm update eslint prettier svelte-check typescript-eslint eslint-plugin-svelte
```

### Rule Reviews

Periodically review and adjust ESLint rules based on team preferences and project needs.
