# Quantum Experiment Engine

The engine is the primary API surface for running quantum experiments. It orchestrates the full pipeline from configuration validation through circuit execution, analysis assembly, metrics computation, provenance capture, and visualization -- returning a strongly-typed `ExperimentResult`.

Your CLI, API, and UI should call this module. Everything below it (core physics, noise models, state preparation) is pure computation with no orchestration logic.

---

## Quick Start

```python
# Single experiment
from src.engine.api import run
from src.engine.models import ExperimentConfig

result = run(ExperimentConfig(
    num_qubits=4,
    state_type="GHZ",
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    metrics="decoherence",
    shots=4096,
))
print(f"Fidelity: {result.analysis.measurement_results.fidelity:.4f}")
```

```python
# Parameter sweep
from src.engine.api import sweep
from src.engine.models import ExperimentConfig, SweepManifest

results = sweep(SweepManifest(
    base_config=ExperimentConfig(num_qubits=3, state_type="GHZ"),
    parameter_ranges={"error_rate": [0.01, 0.05, 0.1, 0.2]},
))
for r in results:
    print(f"error={r.analysis.experiment_parameters['error_rate']:.2f} "
          f"fidelity={r.analysis.measurement_results.fidelity:.4f}")
```

```python
# Custom driver (for parallelization, Slurm, etc.)
from src.engine.api import iter_experiment_configs

for cfg in iter_experiment_configs(manifest):
    submit_to_pool(lambda c=cfg: run(c))
```

---

## Pipeline Architecture

```
ExperimentConfig
    |
    v
(1) Config validation (Pydantic)
    |
    v
(2) Circuit execution (Qiskit backend)
    |
    v
(3) Counts canonicalization (MSB-left, fixed bit-width)
    |
    v
(4) Simulation data extraction (statevector / density matrix / fidelity)
    |
    v
(5) Typed ExperimentAnalysis assembly (metadata, circuit stats, measurements)
    |
    v
(6) Optional: analysis metrics (via analysis/registry)
    |
    v
(7) Provenance + persist analysis JSON to disk
    |
    v
(8) Optional: visualization rendering (histogram, correlation, etc.)
    |
    v
ExperimentResult (Pydantic-validated, fully typed)
```

---

## Module Map

| File / Directory | Purpose |
|-----------------|---------|
| `api.py` | Public entry points: `run()`, `sweep()`, `iter_experiment_configs()` |
| `bloch_math.py` | Bloch sphere coordinate math for the visualization frontend |
| `fidelity.py` | Simulation data extraction (statevector, density matrix, fidelity) |
| `provenance.py` | Provenance building: software versions, git SHA, host info |
| `viz_pipeline.py` | Visualization rendering orchestration |
| `models/` | Pydantic models: config, metadata, circuit, measurement, provenance, quality, results, analysis, sweep, storage |
| `execution/` | Runners (qasm, statevector, density_matrix, hardware), context management, sweep driver |
| `persistence/` | Result storage (`LocalStorage`) and config hashing (SHA1) |
| `infrastructure/` | Event bus (`SimpleEventBus`), structured logging |
| `analysis/` | Metrics integration bridge: counts canonicalization, metrics bundle computation |
| `visualization/` | Renderers (histogram, density matrix, correlation, circuit), export, service |

---

## Simulation Modes

| Mode | Description | Noise Support | Output |
|------|-------------|---------------|--------|
| `qasm` | Shot-based measurement sampling (default) | Yes | Counts only |
| `statevector` | Exact noiseless state, counts via multinomial | No | Counts + statevector + fidelity |
| `density_matrix` | Full mixed-state simulation with noise | Yes | Counts + density matrix + fidelity |
| `hardware` | Real IBM Quantum devices via SamplerV2 | Physical | Counts + hardware metadata |

---

## Key Models

- **`ExperimentConfig`** -- Everything needed to define an experiment: state type, qubit count, noise model, shots, simulation mode, metrics profile, hardware options.
- **`ExperimentResult`** -- Complete output: analysis, metrics bundle, provenance, artifacts, quality metrics.
- **`ExperimentAnalysis`** -- Core data: metadata, circuit statistics, measurement results, optional information-theoretic analysis.
- **`SweepManifest`** -- Sweep specification: base config, parameter ranges, runs per config, overrides.

All models are Pydantic v2 with strict validation and auto-healing validators for common inconsistencies.
