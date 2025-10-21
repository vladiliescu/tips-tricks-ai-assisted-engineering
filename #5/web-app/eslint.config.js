import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';

export default [
	js.configs.recommended,
	...ts.configs.recommended,
	...svelte.configs['flat/recommended'],
	prettier,
	...svelte.configs['flat/prettier'],
	{
		languageOptions: {
			globals: {
				$$Generic: 'readonly',
				$$Props: 'readonly',
				$$Events: 'readonly',
				$$Slots: 'readonly',
				fetch: 'readonly',
				console: 'readonly',
				setTimeout: 'readonly',
				clearTimeout: 'readonly',
				setInterval: 'readonly',
				clearInterval: 'readonly',
				window: 'readonly',
				document: 'readonly',
				navigator: 'readonly',
				location: 'readonly',
				localStorage: 'readonly',
				sessionStorage: 'readonly',
				Event: 'readonly'
			}
		}
	},
	{
		files: ['**/*.svelte'],
		languageOptions: {
			parserOptions: {
				parser: ts.parser
			}
		}
	},
	{
		ignores: ['build/', '.svelte-kit/', 'dist/', 'node_modules/']
	},
	{
		rules: {
			// TypeScript rules
			'@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
			'@typescript-eslint/no-explicit-any': 'warn',

			// Svelte rules
			'svelte/no-at-html-tags': 'warn',
			'svelte/no-target-blank': 'error',
			'svelte/no-navigation-without-resolve': 'off',
			'svelte/require-each-key': 'warn',

			// General rules
			'no-console': 'warn',
			'prefer-const': 'error',
			'no-undef': 'error'
		}
	}
];
