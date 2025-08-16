# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **research-grade quantum experiment framework** built on Qiskit for conducting quantum computing experiments with noise modeling, state preparation, and advanced analysis. The project uses an **engine-first architecture** with a clean API for running structured decoherence pathway experiments.

## Research Focus: Structured Decoherence Pathways

**Central Hypothesis**: Quantum decoherence follows structured pathways determined by entanglement network topology rather than random patterns. The framework implements the **Spring Network Model** where entanglement bonds act as springs and decoherence flows along tension patterns.

**Key Research Metrics (automatically computed):**
- **AI (Asymmetry Index)**: Deviation from uniform error distribution  
- **PCR (Pathway Concentration Ratio)**: Concentration of errors in top vs bottom pathways
- **EEC (Entanglement-Error Correlation)**: Correlation between topology and error patterns
- **TPS (Temporal Pathway Stability)**: Consistency across noise levels
- **CES (Complexity Emergence Score)**: Critical threshold detection

## Engine-First Architecture

The framework is built around a clean, decoupled engine API:

### Core Components
- **Engine API** (`src/engine/api.py`) - Clean entry points: `run()` and `sweep()`
- **Pydantic Models** (`src/engine/models/`) - Type-safe configuration and results
- **Core Logic** (`src/core/`) - Quantum mechanics and analysis
- **Research Integration** (`src/engine/analysis/`) - Structured decoherence metrics

### Usage Examples

**Basic Research Experiment:**
```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    enable_research_metrics=True,
    research_type="structured_decoherence",
    shots=1024,
    noise_enabled=True,
    noise_type="depolarizing", 
    error_rate=0.05
)

result = run(config)

# Access structured decoherence metrics
metrics = result.structured_decoherence_metrics
print(f"Asymmetry Index: {metrics.asymmetry_index:.4f}")
print(f"Pathway Concentration: {metrics.pathway_concentration_ratio:.4f}")
print(f"Topology Correlation: {metrics.entanglement_error_correlation:.4f}")
```

**Parameter Sweeps:**
```python
from src.engine.api import sweep
from src.engine.models import SweepManifest

manifest = SweepManifest(
    base_config=config,
    parameter_ranges={
        "error_rate": [0.0, 0.01, 0.02, 0.05, 0.1],
        "num_qubits": [3, 4, 5]
    },
    runs_per_config=3  # Statistical validation
)

results = sweep(manifest)

# Analyze pathway emergence across parameter space
for result in results:
    cfg = result.analysis.experiment_parameters
    metrics = result.structured_decoherence_metrics
    print(f"Q={cfg['num_qubits']}, p={cfg['error_rate']}: AI={metrics.asymmetry_index:.4f}")
```

## Development Commands

### Testing
```bash
# Run engine tests
pytest tests/engine/ -v

# Test baseline functionality  
pytest tests/engine/test_baseline.py -v

# Test research integration
pytest tests/engine/test_research_integration.py -v
```

### Research Validation
```bash
# Test critical research metrics computation
python -c "
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=4, 
    state_type='GHZ',
    enable_research_metrics=True,
    research_type='structured_decoherence',
    noise_enabled=True,
    noise_type='depolarizing',
    error_rate=0.05
)

result = run(config)
metrics = result.structured_decoherence_metrics
print(f'AI: {metrics.asymmetry_index:.4f}')
print(f'PCR: {metrics.pathway_concentration_ratio:.4f}')
print(f'Evidence for structured pathways: {metrics.asymmetry_index > 0.2}')
"
```

## File Organization

### Engine (Primary Interface)
- `src/engine/api.py` - Main entry points: `run()`, `sweep()`
- `src/engine/models/` - Pydantic models (config, results, research metrics)
- `src/engine/analysis/` - Research metrics integration bridge
- `src/engine/storage.py` - Deterministic result storage

### Core Logic
- `src/core/experiment_runner.py` - Quantum circuit execution
- `src/core/analysis/structured_decoherence/` - Research metrics implementation
- `src/core/noise_factory.py` - Physics-compliant noise models
- `src/core/state_factory.py` - Quantum state preparation

### Tests
- `tests/engine/` - Engine API and integration tests
- `tests/core/` - Core quantum mechanics tests

### Results Structure
```
results/
├── YYYYMMDD/
│   ├── HHMMSS_STATE_Nq_NOISE_SHOTSshots_RESEARCH_HASH.json
│   ├── 190743_GHZ_3q_clean_1024shots_structured_decoherence_*.json
│   └── 190744_BELL_2q_depolarizing_0.05_2048shots_control_*.json
```

**Descriptive Filenames**: Each result file includes all key experiment parameters for easy browsing and identification without opening the file.

## Architecture Principles

1. **Engine-First**: All functionality accessible via clean Python API
2. **Type Safety**: Pydantic models ensure runtime validation  
3. **Interface Agnostic**: Engine works with CLI, web frontend, Jupyter notebooks
4. **Research Focused**: Built specifically for structured decoherence studies
5. **Reproducible**: Complete provenance tracking and deterministic results
6. **Physics Compliant**: All noise models respect quantum mechanics constraints

## Research Workflow

1. **Design Experiment**: Configure quantum state, noise model, research parameters
2. **Run via Engine**: Use `run()` for single experiments, `sweep()` for parameter studies  
3. **Analyze Results**: Structured decoherence metrics computed automatically
4. **Validate Findings**: Statistical validation across multiple runs
5. **Publish**: Results include complete provenance for reproducibility

This framework enables systematic investigation of the **Spring Network Model** hypothesis and discovery of structured decoherence pathways in quantum systems.