# Changelog

All notable changes to QForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed (breaking)
- Public import is `qforge`, not `src`: `from qforge import run` and
  `qforge run 01_superposition`. The installable package lives at
  `src/qforge/` (src-layout). There is no `src.*` compatibility shim.
- Metric profile `decoherence` renamed to `structure` (same metric list).
  No core alias remains. Single-run teaching experiments (including the
  decoherence track) request an explicit metric list — not the named
  `structure` profile, whose extra-input metrics print empty on one run.
  They may set `experiment_type="decoherence"` as a free-string label.
- `ExperimentConfig.experiment_type` is an optional free string, not a closed
  Literal taxonomy.
- FastAPI / uvicorn are no longer required runtime deps. Install
  `qforge[api]` (or `uv sync --extra api`) for the HTTP server. Docker
  installs that extra.
- `ExperimentConfig.research_type` renamed to `experiment_type`
- Metric profile `structured_decoherence` renamed to `decoherence` (then to
  `structure`); metrics are requested via `metrics=` (profile name or explicit
  list) and results are exposed as `result.metrics_bundle` (dict of name →
  entry with value/ci95/status)
- `src/qforge/engine/models/research.py` renamed to `src/qforge/engine/models/analysis.py`;
  `src/qforge/engine/analysis/research_integration.py` renamed to
  `src/qforge/engine/analysis/metrics.py`
- Noise catalog key `research_application` renamed to `use_case`
- Experiment `dec_01_river_vs_fog` renamed to `dec_01_structured_vs_uniform`

### Removed
- `enable_research_metrics` config flag and `result.structured_decoherence_metrics`
  (replaced by `metrics=` / `metrics_bundle`)
- `ResearchMetadata`, `SweepResearchMetadata`, `SweepResearchInsights`,
  `publication_ready`, `publication_readiness`, `research_significance` model
  fields, and `get_research_context`
- Personal research-program documentation (docs/research/, docs/planning/, and
  stale historical design documents); docs now describe the general-purpose
  framework only
- `SECURITY.md` — placeholder policy (unused inbox, version table, 48-hour SLA)
  for a package that is not published
- `CODE_OF_CONDUCT.md` — Contributor Covenant pointing at unused
  `conduct@qforge.dev`

### Added
- `src/qforge/core/math/` shared math primitives — single source of truth for Pauli
  matrices, `relaxation_probability`, total-variation-distance / Gini, and the
  canonical qubit/bit indexing convention; imported across noise models,
  analysis metrics, and the engine
- ~700 new exact-value tests asserting calculations against analytical/closed-form
  results; suite now ~1,100 tests
- Coverage gate now spans the whole physics/math core (all of `src/qforge/core` plus the
  engine math modules `fidelity`, `bloch_math`, `analysis/metrics`,
  `models/measurement`) at ~97% behind a 95% gate
- Deployment configs: Dockerfile, railway.json, vercel.json
- Environment variable handling for CORS origins and API URL
- `.env.example` template for contributor onboarding
- Community files: CONTRIBUTING improvements
- GitHub issue and PR templates
- Docker build smoke test in CI
- Dynamic version injection via `importlib.metadata`
- `register()` / `register_profile()` as the public path to add metrics and
  named profiles without editing core specs
- `register_experiment()` / `unregister_experiment()` as the public path to
  add experiment programs without editing `EXPERIMENT_REGISTRY`
- Setuptools entry points in group `qforge.experiments` (an
  `ExperimentProgram` instance or a zero-arg callable). Discovery only —
  not a plugin framework. Failed entries are logged and skipped.
- `ExperimentConfig.observables`: Pauli strings in MSB-left (bitstring)
  order. Estimates land on `MeasurementResults.observables`. Statevector /
  density-matrix modes are exact; qasm/hardware reuse Z-basis shots for
  I/Z and run extra circuits for X/Y. Not a VQE energy — programs interpret
  ⟨P⟩.
- Learning-path experiments choose default metrics for the question they ask
  (with a CLI `metrics_hint`); protocol experiments leave metrics off
- VQE deep dive estimates the 2-qubit H2 Pauli terms via `observables=`
  and reports ⟨H⟩ / FCI on the result. Energy is experiment interpretation,
  not a core metric. `qforge run` calls `ExperimentProgram.run()` so
  programs can attach that interpretation.
- QAOA deep dive estimates one ⟨ZZ⟩ per MaxCut edge via `observables=`
  and reports ⟨C⟩ / exact MaxCut on the result. Same pattern as VQE —
  a cost, not a core metric.
- Circuit visualization uses Qiskit's `circuit.draw`. Matplotlib/PNG
  needs `pylatexenc` (now a runtime dep). If the mpl drawer is missing,
  the text drawer is saved instead so `visualization_type=circuit` never
  silently skips. Unique-gate explainers print in the CLI. Omit `circuit`
  or set `none` to skip.
- Architecture, engine, and CLI docs: Mermaid maps of the three layers and
  `run()` pipeline (`docs/architecture/`), full CLI reference, README
  pointers for a first clone.
- README is engine-first: CLI / `run()` as the product, FastAPI as
  `qforge[api]`, visual lab marked optional and frozen. Does not claim the
  circuit builder submits to IBM. Notes that PyPI `qforge` is a different
  project.

### Changed
- Migrated Python tooling to `uv` (pyproject.toml + uv.lock; `uv sync` / `uv run`);
  removed `requirements.txt`
- `structure_score` now computes the Jensen-Shannon divergence between the
  observed distribution and its factorized (independent-marginals) null model
  (previously TVD-from-uniform, which duplicated the Asymmetry Index)
- Noise channels made physically consistent: each model's `get_kraus_operators()`
  now matches the channel its `apply()` simulates, using standard textbook
  conventions. `bit_flip`, `phase_flip`, and `phase_damping` `apply()` now apply a
  uniform error to all gates (the per-gate "gate sensitivity" heuristic was
  removed); phase damping uses the standard 2-operator form (coherence factor
  √(1−λ)); amplitude damping is the standard T=0 channel; multi-qubit depolarizing
  `get_kraus_operators()` returns the genuine n-qubit Qiskit channel
- CORS origins now configurable via `CORS_ORIGINS` env var (was `*`)
- Client API URL uses `EXPO_PUBLIC_API_URL` for production builds
- App metadata renamed from "mobile" to "qforge"

### Fixed
- Superposition state fidelity endianness (qubit-ordering) bug
- Missing `fastapi` and `uvicorn` in dependency declarations

## [0.2.0] - 2026-04-03

### Added
- Analysis framework with 8 information-theoretic metrics
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
