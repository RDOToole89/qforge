# Experiments

49 pre-built quantum experiments organized into four progressive journeys. Each journey has numbered **steps** (guided path) and **deep dives** (go further).

## Structure

```
experiments/
├── basics/          11 steps + 10 deep dives    Learn quantum computing from scratch
├── advanced/         8 steps +  7 deep dives    Quantum algorithms → design your own
├── decoherence/      6 steps +  2 deep dives    Decoherence structure experiments
└── hardware/         5 steps +  3 deep dives    Real IBM Quantum processors
```

## The Learning Journey

```
Basics (11 steps)          Advanced (8 steps)         Decoherence (6 steps)     Hardware (5 steps)
─────────────────          ──────────────────         ─────────────────────     ─────────────────
What is a qubit?     →     True randomness      →     Structured vs uniform →  First hardware run
Gates & measurement  →     Deutsch-Jozsa        →     Topology matters     →   HW vs simulation
Entanglement         →     Grover's search      →     Scaling              →   Transpilation
Noise & decoherence  →     Teleportation        →     Noise resilience     →   Backend comparison
Noise & entanglement →     Superdense coding    →     Global vs local      →   Real decoherence
                     →     QFT                  →     Sim vs reality
                     →     Error correction
                     →     Design your own
```

Each experiment requests the metrics that match its question. `qforge run`
prints those numbers plus a one-line hint. Teleportation and superdense coding
leave metrics off — the lesson is the protocol, not histogram shape.

## Quick Start

```bash
# List all 49 experiments
qforge list

# Start the basics journey
qforge run 01_superposition

# Jump to advanced
qforge run adv_01_quantum_randomness

# Start the decoherence experiments
qforge run dec_01_structured_vs_uniform

# Run on real hardware (requires IBM Quantum credentials)
qforge run hw_01_first_hardware_run
```

## Using the Python API

```python
from qforge.experiments import get_experiment, list_experiments

# See what's available
for name, desc in list_experiments():
    print(f"{name}: {desc}")

# Run an experiment
result = get_experiment("01_superposition").run()

# Override defaults
result = get_experiment("dec_03_scaling").run({"num_qubits": 5})

# Parameter sweep
results = get_experiment("dec_04_noise_resilience").sweep(
    parameter_ranges={"error_rate": [0.01, 0.05, 0.1]}
)
```

## Adding New Experiments

**In this repo:** subclass `BaseExperiment`, pick `metrics=` for the question, and register in four places (folder `__init__.py`, root `__init__.py`, folder `README.md`, `AGENTS.md`).

**In your own package:** do not fork the registry.

```python
from qforge.engine.models import ExperimentConfig
from qforge.experiments import register_experiment
from qforge.experiments.base import BaseExperiment

class MyExperiment(BaseExperiment):
    name = "my_ghz_probe"
    description = "GHZ under depolarizing noise"
    metrics_hint = "Structure Score stays high while stray outcomes appear."

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            shots=1024,
            metrics=["structure_score", "total_correlation"],
        )

register_experiment(MyExperiment())
```

Then `qforge list` and `qforge run my_ghz_probe` see it in that process. Combine with `register()` / `register_profile()` if you also ship a metric.

See `basics/steps/step01_superposition.py` for a minimal in-tree example, or `advanced/steps/step08_design_your_own.py` for the experiment design template.
