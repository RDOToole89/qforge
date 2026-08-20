# Architecture

QForge is built around a decoupled quantum experiment engine that can serve any frontend — CLI, programmatic Python, the FastAPI server, or the React Native client — through the same two-function API.

## The Three Layers

```
src/qforge/experiments/    Opinionated experiment programs (basics, advanced, decoherence, hardware)
       |
       v
src/qforge/engine/         Orchestration: run(), sweep(), Pydantic models, provenance, storage
       |
       v
src/qforge/core/           Pure physics and statistics: state prep, noise models, analysis metrics, math
```

**Dependency rules:**

- `core/` must not import from `engine/` or `experiments/`
- `engine/` must not import from `experiments/`
- `experiments/` may import from both

**Key principle**: `src/qforge/core/` is pure physics and statistics — it knows nothing about experiment programs. `src/qforge/engine/` orchestrates without domain knowledge. Only `src/qforge/experiments/` carries opinionated experiment programs. New experiment suites can be built on the same engine without touching the lower layers.

## Engine API

The engine exposes two entry points:

```python
from qforge import ExperimentConfig, run, sweep

result = run(ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    shots=1024,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    metrics="structure",          # profile name or explicit metric list
    experiment_type="decoherence",  # optional label — your research track, not an engine enum
))
```

`run()` executes a single configuration; `sweep()` expands a `SweepManifest` (base config + parameter ranges, Cartesian product) into many runs.

### Configuration (`src/qforge/engine/models/config.py`)

`ExperimentConfig` is a typed Pydantic model. Highlights:

| Field | Purpose |
|-------|---------|
| `num_qubits`, `state_type` | State preparation (GHZ, W, Bell, Cluster, Superposition, Custom) |
| `sim_mode` | `qasm`, `statevector`, `density_matrix`, or `hardware` (IBM Quantum) |
| `noise_enabled`, `noise_type`, `error_rate` | Noise channel selection and strength |
| `shots`, `rng_seed` | Sampling and reproducibility |
| `metrics` | Metric profile name (`"structure"`, `"quick"`, `"information_theory"`) or an explicit list of metric names |
| `observables` | Optional Pauli strings (MSB-left, same order as bitstrings). Estimates are ⟨P⟩ ∈ [-1, 1], not a VQE energy |
| `experiment_type` | Optional free-string label for grouping and storage (not a closed taxonomy) |

### Results

`run()` returns an `ExperimentResult` composed of focused submodels (`src/qforge/engine/models/`):

- `analysis` — circuit statistics and measurement results (counts, probabilities, fidelity, optional Pauli `observables`, statevector or density matrix depending on `sim_mode`)
- `metrics_bundle` — a `MetricsBundle`: dict of metric name → entry with `value`, `ci95` (bootstrap confidence interval), `status`, and `extras`
- `provenance` — git SHA, software versions, host info, backend/job identifiers for hardware runs
- `quality` — quality assessment of the run

### Engine modules

```
src/qforge/engine/
├── api.py               # run(), sweep(), iter_experiment_configs()
├── observables.py       # Pauli ⟨P⟩ estimates (extra X/Y circuits; math is core)
├── bloch_math.py        # Bloch sphere coordinate math for visualization
├── fidelity.py          # Statevector / density matrix / fidelity extraction
├── provenance.py        # Provenance building (versions, git SHA, host info)
├── viz_pipeline.py      # Visualization rendering orchestration
├── analysis/
│   └── metrics.py       # Bridges core metric registry into engine results
├── execution/           # Backend execution (Aer simulators, IBM Runtime SamplerV2)
├── models/              # Pydantic models: config, results, measurement, sweep, storage, analysis, ...
├── persistence/         # Result storage and manifests
└── visualization/       # Plot rendering
```

## Core Layer

```
src/qforge/core/
├── state_preparation/   # 6 state types, factory + registry pattern
├── noise_models/        # 8 physics-based channels with Kraus operators
├── math/                # Shared primitives: Pauli matrices, Pauli-string ⟨P⟩, rates, distances, indexing
└── analysis/
    ├── core/            # Information theory, null models, correlations, bootstrap, topology
    ├── metrics/         # Individual metric implementations + declarative registry
    ├── pipelines/       # High-level orchestration (run_all_to_schema)
    └── constants.py     # Centralized thresholds and validation
```

### Analysis metrics

All metrics are general-purpose information-theoretic and statistical measures over measurement outcome distributions:

| Metric | Definition |
|--------|-----------|
| `asymmetry_index` | Total variation distance from the uniform distribution (full 2^n support) |
| `structure_score` | Jensen-Shannon divergence from the factorized (independent-marginals) null model |
| `entanglement_error_correlation` | Pearson correlation between a topology adjacency matrix and the pairwise mutual-information matrix |
| `concentration_index` | Ratio of probability mass in the top vs bottom quartile of outcomes |
| `pathway_persistence` | Persistence of outcome rankings (alias: `temporal_pathway_stability`), via Spearman rank correlation across conditions |
| `pathway_concentration_ratio` | Probability mass in top vs bottom outcome quartiles (alias of concentration measures) |
| `complexity_emergence_score` | Logistic fit locating a threshold in a metric-vs-size curve |
| `total_correlation` | Multi-information across all qubits |

Metrics are registered via `@register` / `MetricSpec` in `src/qforge/core/analysis/metrics/registry.py`, with bootstrap 95% confidence intervals and per-metric status. Built-in profiles in `profiles.py` are topic-free (`structure`, `quick`, `information_theory`). User code and experiment packages add more with `register_profile()`.

## Experiments Layer

Experiment programs follow a pluggable pattern (`src/qforge/experiments/base.py`): each program has a name, a description, a default `ExperimentConfig`, and a `run(overrides)` method. In-tree programs live in a central registry grouped into:

- `basics/` — an 11-step learning path plus deep dives
- `advanced/` — classic algorithms (Shor, Grover, teleportation, VQE, QAOA)
- `decoherence/` — a 6-step noise study path plus deep dives
- `hardware/` — a 5-step path to real IBM Quantum processors

Out-of-tree programs call `register_experiment()` so they appear in `qforge list` / `qforge run` without editing `EXPERIMENT_REGISTRY`. Installed packages can also declare setuptools entry points in group `qforge.experiments`. Metrics have the same pattern: `register()` / `register_profile()`.

## Frontends

All frontends are thin — they call the engine, never the reverse:

- **CLI** (`src/qforge/cli.py`): parse args → look up the experiment program → `run()` → print. No orchestration logic.
- **FastAPI server** (`apps/api/`): HTTP endpoints for experiments, results, and Bloch visualization data.
- **React Native / Expo client** (`apps/client/`): Bloch sphere visualizer, circuit builder with playback, experiment configurator, glossary.

## Execution Backends

| `sim_mode` | Backend | What you get |
|------------|---------|--------------|
| `qasm` | AerSimulator | Shot-based sampling, optional noise model |
| `statevector` | AerSimulator | Exact noiseless state amplitudes |
| `density_matrix` | AerSimulator | Full mixed state under noise |
| `hardware` | IBM Quantum (SamplerV2) | Real-device counts with transpilation and calibration capture |

## Reproducibility

- Deterministic RNG plumbing (`rng_seed`) through simulation and bootstrap resampling
- Canonical ordering of outcome enumeration to prevent run-to-run drift
- Provenance on every result: git SHA, package versions, host info, execution time
- Versioned result schema for downstream programmatic analysis
