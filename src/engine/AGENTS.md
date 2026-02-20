# AGENTS.md — Execution Engine & Orchestration

Owner: Research Engineering (Roibín O'Toole)
Last updated: 2025-12-02
Token budget: 450

## Purpose

This layer orchestrates experiment execution, manages IO operations, and provides the public API for running experiments. It is the **bridge between pure physics (core) and concrete implementations (experiments)**.

Responsibilities:

- Experiment execution and coordination
- Data persistence and artifact management
- Qiskit backend integration
- Result validation and provenance tracking
- Visualization and reporting
- Public API surface (`api.py`)

## Local Boundaries

### Allowed Imports

- `src.core.*` — All core physics modules
- `qiskit` (all modules) — Quantum simulation and transpilation
- `pydantic` — Schema validation
- `json`, `pathlib`, `pickle` — Persistence
- `matplotlib`, `seaborn` — Visualization
- `logging` — Execution tracking
- `typing`, `dataclasses`, `enum` — Type safety
- Standard library IO and file operations

### Forbidden Imports

- `src.experiments.*` — Engine must not depend on specific experiments
- Direct hardware access libraries (unless approved for hardware integration)

## Structure

```
src/engine/
├── api.py                  # Public interface: run(), sweep()
├── execution/              # Experiment execution
│   ├── runner.py           # Core execution: transpile → simulate → collect
│   ├── context.py          # Execution context and configuration
│   └── sweep.py            # Parameter sweep orchestration
├── persistence/            # Data management
│   ├── storage.py          # Result persistence and artifact management
│   └── hashing.py          # Deterministic config hashing
├── infrastructure/         # Cross-cutting concerns
│   └── events.py           # Event bus for progress tracking
├── models/                 # Pydantic schemas (ExperimentConfig, ExperimentResult)
├── analysis/               # Research metrics integration
└── visualization/          # Plotting and rendering
```

## Do Not

- **Import from experiments** — Engine is domain-agnostic
- **Embed physics calculations** — Delegate to `src.core`
- **Create god objects** — Keep runner, storage, and API separate
- **Bypass schema validation** — All configs and results must validate
- **Use implicit configuration** — Always pass context explicitly
- **Mutate configs** — Treat configs as immutable after validation
- **Ignore provenance** — Every result must include hash, timestamp, versions

## Always

- **Validate configs** before execution via Pydantic models
- **Use explicit seeds** for reproducibility
- **Include provenance** in all results: config hash, timestamp, Qiskit version
- **Handle errors gracefully** — Return structured errors, not raw exceptions
- **Log execution flow** — Use `logging` for progress tracking
- **Save results atomically** — Avoid partial writes
- **Version result schemas** — Include schema version in saved JSON
- **Use type hints** for all public functions

## Key Patterns

### Execution Pattern

```python
# Good: Clean separation of concerns
from src.engine.api import run
from src.engine.models import ExperimentConfig

# QASM mode (default, shot-based)
config = ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    noise_enabled=True, noise_type="depolarizing", error_rate=0.01,
    shots=1024, rng_seed=42,
)

# Statevector mode (exact noiseless state, counts synthesized)
config_sv = ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="statevector", shots=1024, rng_seed=42,
)

# Density matrix mode (full mixed state, supports noise)
config_dm = ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="density_matrix",
    noise_enabled=True, noise_type="depolarizing", error_rate=0.05,
    shots=1024, rng_seed=42,
)

result = run(config)  # Returns validated ExperimentResult

# Bad: Mixing layers or skipping validation
circuit = create_ghz(3)  # Importing from core directly
result = AerSimulator().run(circuit).result()  # Raw Qiskit, no validation
```

### Storage Pattern

```python
# Good: Atomic save with provenance
from src.engine.persistence.storage import save_result

save_result(
    result=experiment_result,  # Validated Pydantic model
    output_dir="results/",
    include_provenance=True
)

# Bad: Manual JSON serialization
import json
with open("result.json", "w") as f:
    json.dump(result.__dict__, f)  # Missing provenance, no validation
```

### Sweep Pattern

```python
# Good: Declarative sweep configuration
from src.engine.execution.sweep import run_sweep

sweep_results = run_sweep(
    base_config=base_config,
    sweep_params={
        "error_rate": [0.001, 0.01, 0.1],
        "num_qubits": [3, 4, 5]
    },
    output_dir="results/sweep/"
)

# Bad: Manual loops without structure
results = []
for error_rate in [0.001, 0.01, 0.1]:
    for num_qubits in [3, 4, 5]:
        # Manual config creation, no validation
        result = run_experiment(...)
        results.append(result)
```

### Event Pattern

```python
# Good: Use event bus for progress tracking
from src.engine.infrastructure.events import SimpleEventBus, RUN_START, RUN_END, make_event

def run_with_events(config: ExperimentConfig, event_bus: SimpleEventBus):
    event_bus.emit(make_event(RUN_START, config=config))
    # ... execution ...
    event_bus.emit(make_event(RUN_END, result=result))

# Bad: Print statements or direct UI updates
def run_with_events(config):
    print("Starting experiment...")  # Not structured
    # ... execution ...
    update_ui(result)  # Tight coupling
```

## Validation Requirements

All configs must pass Pydantic validation:

```python
# Automatic validation via Pydantic
config = ExperimentConfig(
    num_qubits=3,
    state_type="INVALID"  # Raises ValidationError
)

# Physical constraints validated in core layer
noise = NoiseFactory.create(T1=10, T2=25)  # Raises ValueError (T2 > 2*T1)
```

## API Surface

The public API in `api.py` should be minimal and stable:

```python
# Public functions
def run_experiment(config: ExperimentConfig) -> ExperimentResult: ...
def run_sweep(sweep_config: SweepConfig) -> List[ExperimentResult]: ...

# Everything else is internal
```

## Integration Points

### With Core Layer

```python
# Good: Use factories and pure functions
from src.core.state_preparation.factory import StatePreparationFactory
from src.core.noise_models.factory import NoiseFactory

circuit = StatePreparationFactory().create_state(...)
noise_model = NoiseFactory.create_noise_model(...)
```

### With Qiskit

```python
# Good: Wrap Qiskit in engine abstractions
from qiskit_aer import AerSimulator
from src.engine.execution.runner import EngineExperimentRunner

runner = EngineExperimentRunner(experiment_id="example")
result = runner.run(circuit, noise_model, shots, seed)
```

## Testing Requirements

Run integration tests after engine changes:

```bash
pytest tests/engine/
pytest tests/integration/
```

These validate:

- Config → Result pipeline integrity
- Provenance tracking accuracy
- Storage/retrieval round-trips
- Event emission correctness

## Examples

See canonical implementations:

- `src/engine/api.py` — Clean public API
- `src/engine/execution/runner.py` — Execution orchestration
- `src/engine/persistence/storage.py` — Atomic persistence with provenance
- `src/engine/models/config.py` — Pydantic schema patterns
