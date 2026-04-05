# Experiments

Pluggable experiment programs organized into three progressive levels.

## Structure

```
experiments/
├── basics/          Start here — learn quantum concepts hands-on
├── advanced/        Classic quantum algorithms (Shor, Grover, VQE, QAOA, Teleportation)
├── decoherence/     Core research on structured decoherence pathways
└── hardware/        Run experiments on real IBM Quantum processors
```

## Quick Start

```python
from src.experiments import get_experiment, list_experiments

# See what's available
for name, desc in list_experiments():
    print(f"{name}: {desc}")

# Run an experiment
result = get_experiment("bell_state").run()

# Override defaults
result = get_experiment("ghz_exploration").run({"num_qubits": 5})

# Parameter sweep
results = get_experiment("noise_sweep").sweep(
    parameter_ranges={"error_rate": [0.01, 0.05, 0.1]}
)
```

## Adding New Experiments

1. Create a module in the appropriate folder
2. Subclass `BaseExperiment` and define `name`, `description`, `default_config()`
3. Register in `__init__.py`

See `basics/bell_state.py` for a minimal example.
