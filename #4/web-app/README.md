# Web App Frontend

SvelteKit + TypeScript + Tailwind CSS frontend application with comprehensive code quality tooling.

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project in the current directory
npx sv create

# create a new project in my-app
npx sv create my-app
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.

## Code Quality

This project includes ESLint, Prettier, and svelte-check for maintaining code quality.

### Quick Commands

```sh
# Run all quality checks
pnpm run quality:check

# Auto-fix formatting and linting issues
pnpm run quality

# Individual tools
pnpm run lint          # Check for linting issues
pnpm run lint:fix      # Fix linting issues
pnpm run format        # Format code
pnpm run format:check  # Check formatting
pnpm run check         # Type checking
```

### Quality Script

Use the comprehensive quality script for more control:

```sh
# Run all checks with colored output
./scripts/quality.sh

# Auto-fix issues
./scripts/quality.sh --fix

# Quick check (skip type checking)
./scripts/quality.sh --quick

# Show help
./scripts/quality.sh --help
```

### Documentation

See [LINTING_SETUP.md](LINTING_SETUP.md) for detailed configuration and troubleshooting information.
