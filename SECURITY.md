# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, email **security@qforge.dev** with:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

You should receive an acknowledgment within 48 hours. We will work with you to understand and address the issue before any public disclosure.

## Scope

Security issues in the following areas are in scope:

- The Python engine and API server (`src/`, `apps/api/`)
- Credential handling (IBM Quantum tokens, environment variables)
- Dependency vulnerabilities

The frontend client (`apps/client/`) runs entirely in the browser and does not handle secrets directly, but XSS or injection issues are still in scope.

## Best Practices for Contributors

- Never commit credentials, tokens, or secrets (use `.env` files, which are gitignored)
- Use the `.env.example` template for environment variable documentation
- Run `ruff check` and `bandit` before submitting PRs
