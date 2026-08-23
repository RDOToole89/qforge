# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QForge is a **general-purpose quantum experiment framework** built on Qiskit — for learning, experimentation, and real hardware. It combines noise modeling, state preparation, and information-theoretic analysis behind a clean, **engine-first architecture**.

## Engine-First Architecture

- **Engine API** (`src/qforge/engine/api.py`) — Entry points: `run()`, `sweep()`, `iter_experiment_configs()`
- **Pydantic Models** (`src/qforge/engine/models/`) — Type-safe configuration and results
- **Core Logic** (`src/qforge/core/`) — Pure quantum mechanics and analysis
- **Experiment Programs** (`src/qforge/experiments/`) — Pluggable, self-contained experiments

### Usage Examples

**Basic experiment with metrics:**

```python
from qforge import run, ExperimentConfig

config = ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    metrics="structure",          # profile string, or list of metric names
    shots=1024,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
)

result = run(config)

# Access computed metrics (MetricsBundle of MetricEntry: value/ci95/status/extras)
for name, entry in result.metrics_bundle.metrics.items():
    print(f"{name}: {entry.value:.4f}")
```

**Statevector mode (exact noiseless state):**

```python
result = run(ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="statevector", shots=1000, rng_seed=42,
))
meas = result.analysis.measurement_results
print(f"Fidelity: {meas.fidelity:.6f}")       # ~1.0 (exact state)
```

**Density matrix mode (full mixed state with noise):**

```python
result = run(ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="density_matrix",
    noise_enabled=True, noise_type="depolarizing", error_rate=0.1,
    shots=1000,
))
print(f"Fidelity: {result.analysis.measurement_results.fidelity:.4f}")  # < 1.0
```

**Direct analysis pipeline (no engine needed):**

```python
from qforge.core.analysis.pipelines.pathway_analysis import run_all_to_schema

counts = {"000": 400, "111": 400, "001": 100, "110": 100}
results = run_all_to_schema(counts)   # v1.0 schema output, all metrics
print(f"Structure Score: {results['structure_score']['value']:.4f}")
```

## Analysis Metrics

`src/qforge/core/analysis/metrics/` provides general **information-theoretic and statistical measures of measurement-outcome distributions** — e.g. `structure_score` (Jensen-Shannon divergence from a factorized null model), `asymmetry_index` (TVD from uniform), `total_correlation` (multi-information), `concentration_index` (top-vs-bottom quartile probability ratio), `entanglement_error_correlation` (topology/MI correlation), and temporal-stability measures. All support bootstrap confidence intervals, deterministic ordering, and full-support Jeffreys smoothing.

Metric selection uses profiles (`metrics="structure" | "quick" | "information_theory"`) or an explicit list of metric names. Register more with `register_profile()`. `ExperimentConfig.experiment_type` is an optional free-string label for grouping and storage — not a closed taxonomy.

## Development Commands

> **Environment**: This project uses [uv](https://docs.astral.sh/uv/) for Python
> dependency management. `pyproject.toml` is the single source of truth for
> dependencies; `uv.lock` pins them; `.python-version` pins Python to 3.12.
> Set up with `uv sync`, and prefix Python commands with `uv run` (e.g.
> `uv run pytest`, `uv run python -c "..."`). There is no `requirements.txt`.

```bash
# Quick metric check
uv run python -c "
from qforge.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
print(compute_asymmetry_index({'000': 400, '111': 400, '001': 100, '110': 100}))
"

# Full test suite (mirrors CI)
uv run pytest
```

## File Organization

- `src/qforge/core/analysis/metrics/` — Individual metric implementations, `registry.py` (declarative MetricSpec pattern), `profiles.py` (metric selection profiles), `schema_bridge.py` (v1.0 schema output)
- `src/qforge/core/analysis/core/` — Information theory, null models, correlations, bootstrap, topology builders
- `src/qforge/core/analysis/pipelines/` — High-level orchestration (`run_all_to_schema`)
- `src/qforge/core/analysis/constants.py` — Centralized thresholds and parameters
- `src/qforge/core/math/` — **Single source of truth for low-level math** (Pauli matrices, `relaxation_probability`, TVD/Gini, canonical qubit/bit indexing)
- `src/qforge/core/noise_models/` — Physics-compliant noise channels (each declares `NOISE_TYPE`, `IS_UNITAL`, `CATALOG` class attributes)
- `src/qforge/core/state_preparation/` — Quantum state factory (GHZ, Bell, W, Cluster, Superposition, Custom)
- `src/qforge/engine/api.py` — `run()`, `sweep()`, `iter_experiment_configs()`
- `src/qforge/engine/models/` — Pydantic submodules: `config`, `metadata`, `circuit`, `measurement`, `provenance`, `quality`, `results`, `analysis` (MetricsBundle/MetricEntry/AnalysisMetadata), `sweep`, `storage`
- `src/qforge/engine/analysis/metrics.py` — Counts canonicalization + metrics bundle computation
- `src/qforge/engine/` — Also: `bloch_math.py`, `provenance.py`, `fidelity.py`, `viz_pipeline.py`, `execution/`, `visualization/`
- `src/qforge/experiments/` — Experiment programs across `basics/`, `advanced/`, `decoherence/`, `hardware/`
- `apps/api/` — FastAPI REST endpoints; `apps/client/` — React Native / Expo frontend

## Code Quality

- **Linting**: ruff with pydocstyle (D), complexity (C901 max 15), Google convention
- **Pre-commit hooks**: ruff check + format, trailing whitespace, YAML/JSON/TOML validation
- **Type checking**: mypy strict mode
- **Testing**: pytest, ~1,100 tests; the physics/math core sits behind a 95% coverage gate, with verified-value suites asserting outputs against analytical/closed-form calculations

## Framework Generalizability

The architecture is **deliberately general**:

- `src/qforge/core/` is not tied to any specific experiment — it's pure physics + metrics
- `src/qforge/engine/` just orchestrates; it doesn't know what any experiment means
- Only `src/qforge/experiments/` carries experiment-specific semantics

### ExperimentProgram Abstraction

Experiments follow a pluggable protocol:

```python
# src/qforge/experiments/base.py
from typing import Protocol, Mapping, Any
from qforge.engine.models import ExperimentConfig, ExperimentResult

class ExperimentProgram(Protocol):
    """A pluggable experiment program."""

    name: str
    description: str

    def default_config(self) -> ExperimentConfig: ...
    def run(self, overrides: Mapping[str, Any] | None = None) -> ExperimentResult: ...
```

All in-tree experiments are registered in `EXPERIMENT_REGISTRY` (`src/qforge/experiments/__init__.py`) across `basics/`, `advanced/`, `decoherence/`, and `hardware/`. Out-of-tree programs call `register_experiment()` instead of editing that dict.

### CLI Principles

The CLI is **thin and boring**: parse args → call `run()` / `ExperimentProgram.run()` → print results. No orchestration logic, domain decisions, or complex branching in the CLI layer.

### Metrics Stay General, Interpretation Specializes

- `src/qforge/core/analysis/metrics/` — strictly general information-theoretic/statistical measures
- Experiment programs may *interpret* metric values in their own domain context
- The engine routes metric selection via `metrics=` (profile or list), and labels runs via `experiment_type`
- Core has no chemistry, no Hamiltonian type, and no energy metric. `observables=` returns ⟨P⟩; VQE turns those into an energy and QAOA into a MaxCut cost

## Rules for Claude in This Repo

### DO

- Respect the layered architecture (`experiments → engine → core`)
- Keep everything deterministic and reproducible
- Keep metrics mathematically and physically faithful
- Treat any single experiment topic as **one experiment program**, not the framework's identity
- Keep CLI/UI layers thin — they call into the framework, not the reverse

### DO NOT (without being asked)

- "Simplify" metrics just to make code shorter — the mathematical rigor is deliberate
- Fold `core` and `engine` together — the layered architecture is a feature
- Turn this into a product-like framework with web UI, auth, etc.
- Move physics or metric logic into CLI/UI layers
- Add "Co-Authored-By", "Powered by", "Generated with", or any AI attribution to commits, PRs, code comments, or docs

### Breaking Changes Policy

**We are at Beta v0.2, NOT v1.0.** Breaking changes are allowed and preferred over:

- Backward compatibility shims
- Legacy function wrappers
- Dead code accumulation
- Deprecation warnings that never get resolved

**Rule:** Remove old code, don't wrap it. Clean breaks > cruft.

When refactoring:

- Delete procedural code, replace with class-based implementations
- Don't keep old function signatures "for compatibility"
- Don't add `# deprecated` comments — just remove the code
- Update imports and tests to use new patterns
