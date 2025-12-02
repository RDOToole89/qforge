# AGENTS.md — Experiment Implementations

Owner: Research Engineering (Roibín O'Toole)
Last updated: 2025-12-02
Token budget: 350

## Purpose

This layer contains **concrete experiment implementations** and research notebooks. It is where scientific hypotheses are tested using the core physics primitives and engine orchestration.

This layer should:

- Define specific research questions and hypotheses
- Compose core and engine components to run experiments
- Document experimental methodology and results
- Provide reproducible scripts and notebooks

## Local Boundaries

### Allowed Imports

- `src.core.*` — Physics primitives, metrics, analysis
- `src.engine.*` — Execution API, configs, storage
- `qiskit` — Direct usage for custom experiments
- `numpy`, `scipy`, `matplotlib` — Analysis and visualization
- `pandas` — Data manipulation for large sweeps
- Standard library

### Forbidden Imports

- None — Experiments sit at the top of the dependency graph
- However, experiments should **not define new abstractions** that would belong in core/engine

## Structure

```
src/experiments/
├── sst_hypothesis_q1.py              # Structured decoherence research
├── sst_hypothesis_q1_structured.py   # Alternative implementation
└── notebooks/                         # Jupyter notebooks (future)
    ├── exploratory/
    └── published/
```

## Do Not

- **Create new physics primitives** — Add them to `src.core` instead
- **Create new orchestration logic** — Add it to `src.engine` instead
- **Duplicate code between experiments** — Extract to core/engine
- **Hardcode paths or configurations** — Use config files or CLI arguments
- **Commit large result files** — Use `.gitignore` for results/
- **Mix multiple hypotheses in one file** — Keep experiments focused
- **Skip documentation** — Each experiment needs a docstring explaining its purpose

## Always

- **Document the research question** at the top of each experiment file
- **Use the engine API** (`run_experiment`, `run_sweep`) instead of raw Qiskit
- **Include reproducibility metadata** — Seeds, versions, timestamps
- **Save results to standard locations** — Use `results/<experiment_name>/`
- **Reference related papers or theory** — Link to `docs/research-docs/`
- **Provide clear success criteria** — What does a "positive" result look like?
- **Use descriptive variable names** — `entanglement_map` not `em`

## Key Patterns

### Experiment Script Pattern

```python
"""
SST Hypothesis Q1: Entanglement Topology Influences Decoherence Pathways

Research Question:
    Does the geometric structure of entanglement (GHZ vs W vs Cluster)
    correlate with the spatial distribution of decoherence errors?

Methodology:
    1. Prepare different entangled states (same qubit count)
    2. Apply identical noise models
    3. Measure EEC (Entanglement-Error Correlation) for each state
    4. Compare EEC values to determine if topology matters

Expected Outcome:
    If SST hypothesis is correct, EEC should vary significantly
    across different topologies under identical noise conditions.

References:
    - docs/research-docs/sst-ext.md
    - docs/research-docs/RESEARCH_PLAN.md
"""

from src.engine.api import run_sweep
from src.engine.models import ExperimentConfig

def run_sst_hypothesis_q1():
    base_config = ExperimentConfig(
        num_qubits=4,
        state_type="GHZ",  # Will sweep over different states
        noise_model_type="depolarizing",
        error_rate=0.01,
        shots=2048,
        seed=42
    )

    results = run_sweep(
        base_config=base_config,
        sweep_params={
            "state_type": ["GHZ", "W", "Cluster"],
            "error_rate": [0.001, 0.01, 0.05]
        },
        output_dir="results/sst_hypothesis_q1/"
    )

    # Analysis
    for result in results:
        print(f"{result.config.state_type} @ {result.config.error_rate}: "
              f"EEC = {result.metrics.eec:.3f}")

if __name__ == "__main__":
    run_sst_hypothesis_q1()
```

### Notebook Pattern

```python
# Good: Structured notebook with clear sections
"""
# SST Hypothesis Q1 — Interactive Exploration

This notebook allows interactive investigation of the SST hypothesis
using the qiskit-experiment-framework.

## Setup
"""

from src.engine.api import run_experiment
from src.engine.models import ExperimentConfig
import matplotlib.pyplot as plt

"""
## Experiment Configuration
"""

config = ExperimentConfig(...)

"""
## Results & Analysis
"""

result = run_experiment(config)
# ... visualization ...

"""
## Conclusions

Based on the results above, we observe that...
[Document findings here]
"""
```

## Research Documentation

Each experiment should have:

1. **Research question** — What are you testing?
2. **Hypothesis** — What do you expect to find?
3. **Methodology** — How are you testing it?
4. **Expected outcomes** — What would confirm/refute the hypothesis?
5. **References** — Links to theory docs or papers

## Reproducibility Requirements

All experiments must be reproducible:

- **Explicit seeds** for random number generation
- **Version tracking** — Document Qiskit, Python versions
- **Config files** — Save experimental parameters
- **Result provenance** — Use engine's built-in tracking
- **Environment specs** — Use `requirements.txt` or `pyproject.toml`

## Naming Conventions

- **Scripts**: `<hypothesis>_<variant>.py` (e.g., `sst_hypothesis_q1.py`)
- **Notebooks**: `<hypothesis>_<date>_<author>.ipynb` (e.g., `sst_q1_2025_12_02_rob.ipynb`)
- **Results**: `results/<experiment_name>/<timestamp>/`

## Integration with Engine

```python
# Good: Use high-level API
from src.engine.api import run_experiment, run_sweep

result = run_experiment(config)  # Handles everything

# Acceptable: Direct runner usage for custom needs
from src.engine.experiment_runner import ExperimentRunner

runner = ExperimentRunner(backend=custom_backend)
result = runner.run(circuit, noise_model, shots, seed)

# Bad: Reimplementing engine logic
circuit = create_state(...)
noise = create_noise(...)
backend = AerSimulator()
result = backend.run(circuit).result()  # Bypasses validation, provenance
```

## Examples

See canonical implementations:

- `src/experiments/sst_hypothesis_q1.py` — Research hypothesis testing
- `tests/integration/test_end_to_end.py` — Full workflow example
- `docs/guides/getting-started/` — Tutorial for new experiments
