# AI.md — Repository Architecture Overview

Owner: Research Engineering (Roibín O'Toole)
Last updated: 2025-12-02
Token budget: 600

## 1. Overview

This is a **physics-first quantum experimentation framework** for Structured Quantum Mechanics (SQM) research using Qiskit. The framework investigates how entanglement topology influences decoherence pathways—a novel research question that standard quantum tools ignore.

**Core Philosophy**: Enforce physical validity at the schema level, maintain strict layer separation, and provide reproducible, schema-hardened experimental results.

## 2. Architectural Components

### `src/core/` — Scientific Kernel (Pure Physics)

- **Purpose**: Domain entities, physics calculations, metrics, and data schemas.
- **Constraints**: No side effects (IO, network). Pure functions only.
- **Key Modules**:
  - `state_preparation/`: Factory pattern for quantum states (GHZ, W, Cluster, Bell)
  - `noise_models/`: Physics-compliant decoherence channels with hardware validation
  - `analysis/`: Research metrics (EEC, PCR, Structure Score) and analysis pipelines

### `src/engine/` — Execution Engine (Orchestration + IO)

- **Purpose**: Runners, data persistence, analysis orchestration, execution backends.
- **Constraints**: Side effects allowed. Depends on `src/core` but never the reverse.
- **Key Modules**:
  - `models/`: Pydantic v2 schemas for configs and results
  - `experiment_runner.py`: Atomic execution unit (transpile, simulate, collect)
  - `sweep_driver.py`: Multi-dimensional parameter sweeps
  - `storage.py`: JSON serialization with provenance tracking
  - `api.py`: Public interface for running experiments

### `src/experiments/` — Concrete Implementations

- **Purpose**: Specific experiment definitions and research notebooks.
- **Constraints**: Imports from `engine` and `core` only. No new abstractions.
- **Current Experiments**:
  - `sst_hypothesis_q1.py`: SST research hypothesis testing
  - Notebooks for interactive exploration

### `docs/` — Documentation Hierarchy

- **`ai-context/`**: AI collaboration notes and documentation strategy
- **`architecture/`**: System design documents and refactor plans
- **`guides/`**: User-facing documentation (API reference, getting started)
- **`planning/`**: Roadmaps and future work
- **`research-docs/`**: Scientific theory (SST philosophy, research plans)

### `schemas/` — JSON Schema Definitions

- Strict contracts for experiment configs and results
- Ensures backward compatibility and data integrity

### `tests/` — Test Suite

- **`tests/physics/`**: Analytical validation against pen-and-paper physics
- Unit tests for core components
- Integration tests for experiment workflows

## 3. Boundaries

**Dependency Flow** (unidirectional):

```
experiments → engine → core
```

**Rules**:

- `core` **never** imports from `engine` or `experiments`
- `engine` **never** imports from `experiments`
- `experiments` can import from both `engine` and `core`

**Rationale**: Core physics logic must remain portable and reusable.

## 4. Patterns

### Configuration Pattern

- All experiments defined by **Pydantic v2 models** in `src/engine/models.py`
- Configs are validated before execution
- Unphysical parameters (e.g., T1 < T2) rejected at schema level

### Results Pattern

- All outputs validated against schemas in `src/engine/models.py`
- Results include provenance: config hash, timestamp, Qiskit version
- JSON serialization ensures 5-year readability

### State Factory Pattern

- Use `StatePreparationFactory` to create quantum circuits
- States are pure circuits without noise (noise added by engine)
- Educational comments embedded in circuit definitions

### Noise Validation Pattern

- `NoiseFactory` enforces physics constraints via `create_noise_model_for_hardware()`
- Thermodynamic laws (e.g., T₂ ≤ 2T₁) validated before simulation
- Hardware-specific noise profiles supported

### Analysis Pipeline Pattern

- Metrics computed in `src/core/analysis/metrics/`
- Pipelines orchestrate multi-step analysis in `src/core/analysis/pipelines/`
- Raw counts → classical probability → entropy → custom metrics

## 5. Guardrails

### Never

- Mix orchestration logic into `src/core`
- Bypass Pydantic validation or schema enforcement
- Introduce non-deterministic behavior (always use explicit seeds)
- Delete or modify experiment results without version tracking
- Create "god objects" that span multiple layers

### Always

- Run `pytest tests/physics/` after modifying `src/core`
- Use type hints for all public functions
- Document physical assumptions in docstrings
- Validate configs before execution
- Include provenance metadata in all results
- Follow existing folder patterns when adding new modules

## 6. Canonical Examples

### Running an Experiment

```python
from src.engine.api import run_experiment
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    noise_model_type="depolarizing",
    error_rate=0.01,
    shots=1024,
    seed=42
)

result = run_experiment(config)
print(result.metrics.structure_score)
```

### Creating a Custom State

```python
from src.core.state_preparation.factory import StatePreparationFactory

factory = StatePreparationFactory()
circuit = factory.create_state(
    state_type="GHZ",
    num_qubits=4,
    seed=42
)
```

### Running a Parameter Sweep

```python
from src.engine.execution.sweep import run_sweep

sweep_config = {
    "base_config": config,
    "sweep_params": {
        "error_rate": [0.001, 0.01, 0.1],
        "num_qubits": [3, 4, 5]
    }
}

results = run_sweep(sweep_config)
```

## 7. Key Dependencies

- **Qiskit**: Quantum circuit construction and simulation
- **Pydantic v2**: Schema validation and data contracts
- **NumPy/SciPy**: Numerical computation
- **Matplotlib**: Visualization (in `src/engine/visualization/`)
- **pytest**: Testing framework

## 8. Research Context

This framework is designed to answer: **"Does the shape of entanglement influence the shape of decoherence?"**

Standard quantum frameworks measure fidelity (success/failure). This framework measures **structure** via:

- **EEC (Entanglement-Error Correlation)**: Does error topology match entanglement topology?
- **PCR (Pathway Concentration Ratio)**: Do errors concentrate in specific qubits?
- **Structure Score**: Quantifies deviation from random noise using Total Variation Distance

These metrics enable "fingerprinting" quantum hardware and discovering which entanglement topologies are most robust to specific noise types.

## 9. Getting Started

1. **Installation**: See `docs/guides/getting-started/installation.md`
2. **First Experiment**: Run `python -m src.experiments.sst_hypothesis_q1`
3. **Understanding Metrics**: Read `docs/guides/api/metrics.md`
4. **Architecture Deep Dive**: Read `docs/architecture/ARCHITECTURE.md`
5. **AI Collaboration**: Read `docs/ai-context/AI_COLLABORATOR_NOTES.md`

## 10. Related Files

- Root `AGENTS.md`: Global architectural rules
- `docs/ai-context/AI_DOC_STRATEGY.md`: Documentation philosophy
- `src/core/AGENTS.md`: Physics layer constraints
- `src/engine/AGENTS.md`: Engine layer rules
- `src/experiments/AGENTS.md`: Experiment implementation guidelines
