# Changelog

All notable changes to QForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Deployment configs: Dockerfile, railway.json, vercel.json
- Environment variable handling for CORS origins and API URL
- `.env.example` template for contributor onboarding
- Community files: CODE_OF_CONDUCT, SECURITY, CONTRIBUTING improvements
- GitHub issue and PR templates
- Docker build smoke test in CI
- Dynamic version injection via `importlib.metadata`

### Changed
- CORS origins now configurable via `CORS_ORIGINS` env var (was `*`)
- Client API URL uses `EXPO_PUBLIC_API_URL` for production builds
- App metadata renamed from "mobile" to "qforge"

### Fixed
- Missing `fastapi` and `uvicorn` in dependency declarations

## [0.2.0] - 2026-04-03

### Added
- Research-grade analysis framework with 8 structured decoherence metrics
- Engine-first architecture with `run()` and `sweep()` API
- Interactive quantum circuit builder with learn mode (18 lessons)
- Bloch sphere 3D visualizer with noise channel exploration
- Quantum glossary with 100+ terms across 16 categories
- 6 quantum state types: GHZ, Bell, W, Cluster, Superposition, Custom
- Parameter sweep system with Cartesian product expansion
- Provenance tracking for reproducible experiments
- 335+ tests with 90% coverage on core analysis
- Pre-commit hooks with ruff and formatting enforcement

## [0.1.0] - 2024-12-01

### Added
- Initial framework with basic experiment runner
- Qiskit integration for circuit execution
- Simple noise model support
- CLI with `list` and `run` commands
