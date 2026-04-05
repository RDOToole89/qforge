# AGENTS.md — Experiments Module

Owner: Research Engineering
Last updated: 2026-04-05

## Purpose

Pluggable experiment programs built on a **general-purpose quantum experiment engine**. The current research focus is structured decoherence, but the engine and experiment infrastructure are designed to support any quantum experiment — entanglement witnesses, variational circuits, benchmarking, error correction studies, or anything else that can be expressed as "prepare state → apply noise/operations → measure → analyze."

New experiment types that have nothing to do with decoherence are welcome. The `basics/` folder already includes Bell correlation experiments that are general quantum mechanics, not decoherence-specific. The architecture deliberately separates the engine (which is domain-agnostic) from the experiments (which carry research semantics).

Experiments are organized into three progressive levels so users can learn, research, and deploy to hardware through a consistent interface.

## Structure

```
experiments/
├── __init__.py              # Registry: EXPERIMENT_REGISTRY, get_experiment(), list_experiments()
├── base.py                  # ExperimentProgram protocol + BaseExperiment helper
├── README.md                # User-facing overview with quick start
├── AGENTS.md                # This file — agent guidance
│
├── basics/                  # Level 1: Learning experiments
│   ├── README.md            # Explains each experiment, suggested order
│   ├── bell_state.py        # BellExperiment — 2-qubit entanglement
│   ├── bell_correlation.py  # BellCorrelation — full Bell metrics + variants
│   ├── ghz_exploration.py   # GHZExploration — multi-qubit GHZ + structure metrics
│   └── noise_comparison.py  # NoiseComparison — depolarizing vs amplitude damping
│
├── advanced/                # Classic quantum algorithms and protocols
│   ├── README.md            # Algorithm descriptions and usage
│   ├── shor.py              # ShorExperiment — integer factoring via period-finding
│   ├── grover.py            # GroverExperiment — unstructured search with quadratic speedup
│   ├── teleportation.py     # TeleportationExperiment — state transfer via entanglement
│   ├── vqe.py               # VQEExperiment — variational eigensolver for H2
│   └── qaoa.py              # QAOAExperiment — approximate optimization for MaxCut
│
├── decoherence/             # Level 2: Core structured decoherence research
│   ├── README.md            # Research context, experiment progression
│   ├── topology_comparison.py  # TopologyComparison — GHZ/W/Cluster/Product
│   ├── scaling_ladder.py       # ScalingLadder — 2→6+ qubits, GHZ and W
│   ├── noise_sweep.py          # NoiseSweep — structure vs noise rate
│   └── state_probe.py          # StateProbeStudy — 47-condition NTC sensitivity
│
└── hardware/                # Level 3: Real IBM Quantum hardware
    ├── README.md            # Prerequisites, setup, what we found
    └── hardware_study.py    # 10-experiment hardware decoherence suite
```

## Registry

All experiments are registered in `__init__.py` under `EXPERIMENT_REGISTRY`. Current entries:

| Key | Class | Folder | Description |
|-----|-------|--------|-------------|
| `bell_state` | BellExperiment | basics/ | Two-qubit Bell state |
| `bell_correlation` | BellCorrelation | basics/ | Bell metrics + variant comparison |
| `ghz_exploration` | GHZExploration | basics/ | Multi-qubit GHZ + structure metrics |
| `noise_comparison` | NoiseComparison | basics/ | Depolarizing vs amplitude damping |
| `topology_comparison` | TopologyComparison | decoherence/ | GHZ/W/Cluster/Product comparison |
| `scaling_ladder` | ScalingLadder | decoherence/ | Structure scaling with qubit count |
| `noise_sweep` | NoiseSweep | decoherence/ | Structure resilience under noise |
| `state_probe` | StateProbeStudy | decoherence/ | Correlated noise sensitivity study |
| `shor` | ShorExperiment | advanced/ | Shor's algorithm for integer factoring |
| `grover` | GroverExperiment | advanced/ | Grover's search with quadratic speedup |
| `teleportation` | TeleportationExperiment | advanced/ | Quantum state transfer via entanglement |
| `vqe` | VQEExperiment | advanced/ | Variational Quantum Eigensolver for H2 |
| `qaoa` | QAOAExperiment | advanced/ | QAOA for MaxCut optimization |

Hardware experiments (`hardware/hardware_study.py`) are run directly via their module functions, not through the registry, because they manage backend connections and sessions internally.

## How to Add a New Experiment

### 1. Decide which folder it belongs in

- **basics/** — Teaches a concept. Simple config, clear output, good docstring with "What you'll learn" and "Try it" sections. Aimed at newcomers. Can be about any quantum topic (entanglement, noise, gates, etc.).
- **decoherence/** — Tests a hypothesis about structured decoherence. Has a research question, uses `metrics="structured_decoherence"`, documents expected findings. This is the current research focus.
- **hardware/** — Requires IBM Quantum credentials. Manages backend connections. Saves full provenance.
- **New folders welcome** — If a new research direction doesn't fit decoherence (e.g., `benchmarking/`, `error_correction/`, `variational/`), create a new folder at the same level with its own README.md.

If unsure, default to **basics/** for learning experiments or create a new folder for a new research direction.

### 2. Create the module

Follow this template (see `basics/bell_state.py` for the minimal version):

```python
"""One-line title — What this experiment tests.

What you'll learn / What this tests:
  - Point 1
  - Point 2

Usage:
    from src.experiments.{folder}.{module} import {instance}
    result = {instance}.run()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig
from src.experiments.base import BaseExperiment


class MyExperiment(BaseExperiment):
    """One-line description."""

    name = "my_experiment"
    description = "Short description for the registry listing"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=4096,
            metrics="structured_decoherence",
        )


my_experiment = MyExperiment()
```

### 3. Register it

Add to **three** places:

1. **The folder's `__init__.py`** — import the class and instance
2. **`src/experiments/__init__.py`** — import and add to `EXPERIMENT_REGISTRY` and `__all__`
3. **The folder's `README.md`** — add a section explaining the experiment

### 4. Update this file

Add a row to the registry table above so the next agent knows what exists.

## Naming Conventions

- **File names**: lowercase-kebab or lowercase-underscore (e.g., `noise_sweep.py`)
- **Class names**: PascalCase (e.g., `NoiseSweep`)
- **Instance names**: snake_case, matching the registry key (e.g., `noise_sweep`)
- **Registry keys**: snake_case, descriptive (e.g., `"topology_comparison"`)

## Architecture Rules

### DO

- Subclass `BaseExperiment` — it provides `run()`, `sweep()`, and config merging for free
- Define `name`, `description`, and `default_config()` — these are the protocol contract
- Add convenience methods for common workflows (e.g., `run_all_states()`, `run_noise_sweep()`)
- Use `metrics="structured_decoherence"` for research experiments
- Include a module-level instance for convenience imports
- Write docstrings with usage examples — these are the primary documentation

### DO NOT

- Import from `src.engine.models` beyond `ExperimentConfig` and `ExperimentResult`
- Put analysis logic in experiments — that belongs in `src/core/analysis/`
- Put visualization logic here — that's handled by the engine
- Hardcode backend names or hardware-specific logic in basics/ or decoherence/ experiments
- Reference SST, SQM, or other personal theory branding — use "structured decoherence"

### ALWAYS

- Update the folder's README.md when adding an experiment
- Update this AGENTS.md registry table when adding or removing experiments
- Update `__init__.py` at both the folder and root level
- Keep experiments self-contained — each module should be runnable independently
