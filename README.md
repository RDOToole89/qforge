# Qiskit Experiment Framework

A research-grade quantum experiment framework built on Qiskit for investigating structured decoherence pathways in quantum systems — and for learning how quantum computing actually works.

I started building this about a year ago as a side project to teach myself quantum mechanics and Qiskit. It grew into something I think is genuinely useful: a framework that sits between a learning tool and a research instrument. Educational enough to teach concepts, rigorous enough to produce results worth publishing. I'm open-sourcing it because I think others might find it useful too — whether you're learning quantum computing, running experiments, or building your own analysis tools on top.

This is still actively developing. Comments, ideas, and contributions are welcome. Feel free to use it however you like.

---

## What It Does

### Quantum Experiment Engine (Python)

Run structured quantum experiments with a clean two-function API:

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

result = run(ExperimentConfig(
    num_qubits=4,
    state_type="GHZ",
    shots=4096,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    metrics="structured_decoherence",
))

print(f"Fidelity: {result.analysis.measurement_results.fidelity:.4f}")
for name, m in result.metrics_bundle.metrics.items():
    print(f"  {name}: {m.value:.4f} (95% CI: {m.ci95})")
```

Or run the analysis pipeline directly on any measurement data:

```python
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

results = run_all_to_schema({"000": 400, "111": 400, "001": 100, "110": 100})
print(f"Structure Score: {results['structure_score']['value']:.4f}")
```

### Interactive Visualizer (React Native / Expo)

A full-screen Bloch sphere visualizer with two modes:

- **Built-in mode**: Hardcoded educational examples — watch how 5 noise channels deform the Bloch sphere in real-time, compare probe state responses, explore 2-qubit correlator space
- **Experiment mode**: Live data from the Python engine — per-qubit Bloch vectors from partial traces, real correlators, mutual information heatmaps, animated decoherence sweeps

### Quantum Glossary

A searchable reference of ~100+ quantum computing terms across 16 categories, with formal definitions, intuitive explanations, key equations, symbol annotations, and cross-linked related terms. Built into the app as a learning companion.

---

## Features

### Simulation Modes

| Mode | Description | Noise Support |
|------|-------------|---------------|
| `qasm` | Shot-based measurement sampling | Yes |
| `statevector` | Exact noiseless state (counts via multinomial) | No |
| `density_matrix` | Full mixed-state simulation | Yes |
| `hardware` | Real IBM Quantum devices via SamplerV2 | Physical |

### Quantum States (6 types)

| State | Entanglement | Use Case |
|-------|-------------|----------|
| **GHZ** | Global (all-to-all) | Primary structured decoherence probe |
| **W** | Symmetric single-excitation | Non-global entanglement studies |
| **Bell** | Maximal bipartite | 2-qubit correlation benchmarks |
| **Cluster** | Nearest-neighbor graph | Topological structure analysis |
| **Superposition** | None (product state) | Control baseline |
| **Custom** | User-defined | Extensibility |

### Noise Models (7 types)

- **Depolarizing** — uniform random Pauli errors
- **Amplitude Damping** — energy relaxation (T1)
- **Phase Damping** — pure dephasing (T2*)
- **Bit Flip** / **Phase Flip** — single-axis stochastic errors
- **Thermal Relaxation** — combined T1 + T2 + temperature
- **Correlated Depolarizing** — topology-dependent multi-qubit errors

### Research Metrics (8 metrics with bootstrap CIs)

| Metric | What It Measures |
|--------|-----------------|
| **Asymmetry Index** | TVD from uniform distribution (structure detection) |
| **Pathway Concentration Ratio** | Top vs bottom quartile concentration |
| **Entanglement-Error Correlation** | Topology-error pattern correlation |
| **Temporal Pathway Stability** | Rank correlation across conditions |
| **Complexity Emergence Score** | Phase transition detection (logistic fit) |
| **Structure Score** | Jensen-Shannon divergence from null model |
| **Concentration Index** | Gini-like pathway concentration |
| **Total Correlation** | Multi-information across all qubits |

All metrics include 95% bootstrap confidence intervals and v1.0 schema compliance.

### Bloch Sphere Visualizer

| View | What You See |
|------|-------------|
| **1-Qubit** | Bloch sphere with original + noise-transformed point clouds, state vector arrow |
| **2-Qubit** | 3D correlator space (ZI, IZ, ZZ) with multi-topology comparison |
| **PTM** | 4x4 Pauli Transfer Matrix heatmap |
| **Data** | Experimental fingerprint norms + cosine similarity matrix |

Features: drag-to-rotate, error rate slider, sweep animation, per-qubit selection, educational explainer panels, JSON config editor with import/export.

### Hardware Integration

Run experiments on real IBM Quantum devices:

- Backend auto-selection or manual specification
- Session management for parameter sweeps
- Full provenance capture: transpilation details, calibration snapshots, job metadata
- Counts-based fidelity estimation (Bhattacharyya coefficient)

### Additional Features

- **13 pre-built experiment programs** (SST hypothesis tests, Bell correlations, state probe sensitivity)
- **CLI** (`qxf list`, `qxf run <experiment>`) with parameter overrides
- **REST API** (FastAPI) with 8 endpoints for experiments, results, and Bloch visualization
- **Full provenance tracking**: software versions, git SHA, host info, execution time
- **Deterministic reproducibility**: RNG plumbing, canonical ordering, seed control
- **Pre-commit hooks**: ruff linting + formatting, YAML/TOML/JSON validation

---

## Quick Start

### Python Engine

```bash
git clone https://github.com/your-username/qiskit-experiment-framework.git
cd qiskit-experiment-framework
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# List available experiments
python -m src.cli list

# Run an experiment
python -m src.cli run sst_q1
```

### Frontend (Bloch Sphere Visualizer)

```bash
# Start the API server
venv/bin/python -m uvicorn apps.api.main:app --reload --port 8000

# In another terminal, start the Expo app
cd apps/client
pnpm install
pnpm run web
```

### Development

```bash
# Set up pre-commit hooks
pre-commit install

# Lint, format, type-check, test (mirrors CI)
make check

# Or individually
make lint        # ruff check
make format      # ruff format
make typecheck   # mypy strict
make test        # pytest with 90% coverage
```

---

## Architecture

```
src/
  experiments/         Pluggable experiment programs (13 registered)
      |
      v
  engine/              Orchestration: run(), sweep(), Pydantic models
      |                  provenance.py, fidelity.py, viz_pipeline.py, bloch_math.py
      v
  core/                Pure physics — no experiment-specific logic
      |-- analysis/       8 research metrics, pipelines, schema bridge
      |-- noise_models/   7 physics-compliant noise channels
      |-- state_preparation/  6 quantum state types

apps/
  api/                 FastAPI REST API (experiments, results, Bloch endpoints)
  client/              React Native (Expo) app
      |-- bloch-sphere/   Interactive 3D Bloch sphere visualizer
      |-- quantum-glossary/  Searchable quantum computing reference (~100+ terms)
```

- **`src/core/`** is pure quantum mechanics, information theory, and statistics — no experiment-specific logic
- **`src/engine/`** orchestrates experiments without domain knowledge
- **`src/experiments/`** carries research-specific semantics
- **`apps/`** contains the API and frontend — thin layers over the engine

---

## Research Background

The framework's flagship research investigates the **Spring Network Model** hypothesis: that quantum decoherence follows structured pathways determined by entanglement topology, rather than random patterns. Key findings so far:

- GHZ states detect correlated noise patterns with 100% sensitivity across tested conditions
- Cluster and product states are provably Pauli-invariant under Z-basis measurement
- Noise fingerprints **scale** (same direction, growing magnitude) rather than shift — mean cosine similarity 0.874
- The "Fog vs River" phenomenon: decoherence in some regimes looks like uniform fog (random), in others like a river following the entanglement topology

See `docs/research-docs/` for detailed findings and hypotheses.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Quantum simulation | Qiskit 2.1, Qiskit Aer 0.17 |
| Hardware execution | Qiskit IBM Runtime (SamplerV2) |
| Engine | Python 3.9+, Pydantic 2, NumPy, SciPy |
| API | FastAPI, Uvicorn |
| Frontend | React Native 0.81, Expo SDK 54, TypeScript 5.9 |
| 3D Visualization | Three.js 0.183 |
| Monorepo | Turborepo, pnpm |
| Code quality | ruff, mypy (strict), pytest (90% coverage), pre-commit |

---

## Status

This is **Beta (v0.2)** — actively developing. The core engine and analysis framework are stable and research-grade. Breaking changes are allowed and preferred over backward-compatibility shims.

What's solid:
- All 8 research metrics with bootstrap CIs and schema compliance
- Engine API (`run()`, `sweep()`) with full provenance
- Bloch sphere visualizer with built-in and experiment modes
- Hardware integration via IBM Quantum
- 277+ passing tests with 90% coverage on core analysis

What's next:
- Measurement basis selection (X/Y basis, not just Z)
- Non-Markovian noise models
- Performance benchmarking for large-scale studies
- More experiment programs beyond SST

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

Apache-2.0. See [LICENSE](LICENSE) for details.
