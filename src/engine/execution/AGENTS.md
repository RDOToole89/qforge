# AGENTS.md — Execution Subsystem

Owner: Research Engineering
Last updated: 2026-02-20
Token budget: 250

## Purpose

Circuit execution and backend management. Translates an `ExperimentConfig` into a Qiskit simulation job and returns raw results (counts, statevector, density matrix).

## Simulation Modes

| sim_mode | Backend | Noise | Returns |
|----------|---------|-------|---------|
| `qasm` | `AerSimulator()` | Yes | Qiskit `Result` (counts) |
| `statevector` | `AerSimulator(method="statevector")` | **No** (rejected at config) | `dict` with `counts` + `statevector` |
| `density_matrix` | `AerSimulator(method="density_matrix")` | Yes | `dict` with `counts` + `density_matrix` |

Statevector mode synthesizes counts via `np.random.multinomial` from exact probabilities.

## Structure

```
execution/
├── runner.py    # EngineExperimentRunner: circuit build, noise, 3 backend methods
├── context.py   # AppContext: base dirs, env, logging config
└── sweep.py     # Parameter sweep orchestration
```

## Allowed Imports

- `qiskit`, `qiskit_aer` — simulation
- `numpy` — multinomial sampling for statevector mode
- `src.core.state_preparation` — state factories
- `src.core.noise_models` — noise model creation
- Standard library (`logging`, `typing`)

## Forbidden Imports

- `src.engine.models` — runner must not import Pydantic models (api.py owns that)
- `src.engine.analysis` — metrics are computed upstream in api.py
- `src.experiments` — engine is domain-agnostic

## Do Not

- Add metric computation or analysis logic here
- Modify the circuit for analysis purposes (that belongs in api.py)
- Import Pydantic models or construct result objects

## Always

- Return raw Qiskit objects or plain dicts — let api.py do the typing
- Propagate `rng_seed` to the backend for reproducibility
- Log backend method and noise model status
