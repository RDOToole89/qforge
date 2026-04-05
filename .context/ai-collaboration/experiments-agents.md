# AGENTS.md — Experiment Programs

Owner: Research Engineering (Roibín O'Toole)
Last updated: 2025-12-02
Token budget: 400

## Purpose

This module contains **experiment programs** - pluggable, discoverable experiment implementations that use the engine API. Each experiment encapsulates a specific research question with its default configuration.

## Architecture Pattern: ExperimentProgram

All experiments follow the `ExperimentProgram` protocol:

```python
class ExperimentProgram(Protocol):
    name: str           # Short identifier (e.g., "sst_q1")
    description: str    # Human-readable description

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        ...

    def run(self, overrides: Mapping[str, Any] | None = None) -> ExperimentResult:
        """Run the experiment with optional config overrides."""
        ...
```

## Structure

```
src/experiments/
├── __init__.py                      # Registry and exports
├── base.py                          # Protocol + BaseExperiment
├── sst_hypothesis_q1.py             # SST Q1 (depolarizing noise)
├── sst_hypothesis_q1_structured.py  # SST Q1 (amplitude damping)
└── AGENTS.md                        # This file
```

## Key Design Decisions

### 1. Use Engine API, Not Internals

Experiments MUST use `src/engine/api.py` functions (`run()`, `sweep()`), NOT internal components like `EngineExperimentRunner`.

**Why**: The engine API is the stable interface. It handles metrics computation, storage, and validation automatically.

### 2. BaseExperiment Helper

Most experiments should inherit from `BaseExperiment` which provides:
- `run(overrides)` - Single experiment execution via engine API
- `sweep(parameter_ranges)` - Parameter sweep via engine API

### 3. Metrics via Config, Not Manual

Enable research metrics through configuration:

```python
ExperimentConfig(
    metrics="structured_decoherence",  # profile name, list, or None
)
```

**Don't** compute metrics manually in experiment code.

### 4. Module-Level Instances

Each experiment module provides a convenience instance:

```python
# In sst_hypothesis_q1.py
sst_q1 = SSTHypothesisQ1()
```

This enables quick usage: `from src.experiments import sst_q1; sst_q1.run()`

## Local Boundaries

### Allowed Imports

- `src.engine.api` — `run()`, `sweep()` functions
- `src.engine.models` — `ExperimentConfig`, `ExperimentResult`, `SweepManifest`
- `src.experiments.base` — `BaseExperiment`, `ExperimentProgram`
- `numpy` — For parameter generation (e.g., `linspace`)
- Standard library

### Forbidden Imports

- `src.engine.execution.*` — Use engine API, not internals
- `src.core.*` — Let engine handle core integration
- Direct Qiskit imports — Let engine handle execution

## Do Not

- **Use `EngineExperimentRunner` directly** — Use engine API
- **Compute metrics manually** — Enable via `research_type` config
- **Serialize results manually** — Engine handles storage
- **Create backward-compatibility wrappers** — Breaking changes are fine (Beta v0.2)
- **Define new abstractions** — Add them to `core/` or `engine/`
- **Hardcode paths** — Let engine handle storage

## Always

- **Inherit from `BaseExperiment`** or implement `ExperimentProgram`
- **Document the hypothesis** in module and class docstrings
- **Provide `default_config()`** with sensible defaults
- **Register in `EXPERIMENT_REGISTRY`** in `__init__.py`
- **Provide module-level instance** for convenience
- **Include pass criteria** — What defines success?

## Adding a New Experiment

1. **Create the file** (e.g., `bell_chsh.py`):

```python
from src.experiments.base import BaseExperiment
from src.engine.models import ExperimentConfig

class BellCHSH(BaseExperiment):
    """Bell/CHSH inequality violation test."""

    name = "bell_chsh"
    description = "Bell/CHSH inequality violation test"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=2,
            state_type="Bell",
            shots=4096,
            # ... other config
        )

# Module-level instance
bell_chsh = BellCHSH()
```

1. **Register in `__init__.py`**:

```python
from src.experiments.bell_chsh import BellCHSH, bell_chsh

EXPERIMENT_REGISTRY["bell_chsh"] = bell_chsh

__all__ = [
    # ... existing exports
    "BellCHSH",
    "bell_chsh",
]
```

## Usage Examples

```python
from src.experiments import get_experiment, list_experiments

# List available experiments
for name, desc in list_experiments():
    print(f"{name}: {desc}")

# Run experiment with defaults
exp = get_experiment("sst_q1")
result = exp.run()
print(result.metrics_bundle.value("structure_score"))

# Run with overrides
result = exp.run({"num_qubits": 3, "error_rate": 0.1})

# Run parameter sweep
results = exp.sweep({"error_rate": [0.01, 0.05, 0.1, 0.2]})

# Use convenience methods
from src.experiments import sst_q1
results = sst_q1.run_noise_sweep(noise_steps=10, max_error_rate=0.3)
```

## Research Documentation

Each experiment docstring should include:

1. **Research question** — What are you testing?
2. **Hypothesis** — What do you expect to find?
3. **Protocol** — What states, noise, metrics?
4. **Pass criteria** — What thresholds define success?
5. **References** — Links to `docs/research-docs/`

## Dependencies

- `src/engine/api.py` — Execution entry points
- `src/engine/models/` — Pydantic models for config and results
