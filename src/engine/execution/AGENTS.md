# AGENTS.md — Execution Subsystem

Owner: Research Engineering
Last updated: 2026-04-04
Token budget: 250

## Purpose

Circuit execution and backend management. Translates an `ExperimentConfig` into a Qiskit simulation job (or IBM Quantum hardware job) and returns raw results (counts, statevector, density matrix).

## Execution Modes

| sim_mode | Backend | Noise | Returns |
|----------|---------|-------|---------|
| `qasm` | `AerSimulator()` | Simulated (configurable) | Qiskit `Result` (counts) |
| `statevector` | `AerSimulator(method="statevector")` | **No** (rejected at config) | `dict` with `counts` + `statevector` |
| `density_matrix` | `AerSimulator(method="density_matrix")` | Simulated (configurable) | `dict` with `counts` + `density_matrix` |
| `hardware` | IBM Quantum via `SamplerV2` | **Physical** (real device) | `dict` with `counts` + `HardwareResult` |

Statevector mode synthesizes counts via `np.random.multinomial` from exact probabilities.
Hardware mode transpiles circuits to ISA, captures calibration/transpilation provenance.

## Structure

```
execution/
├── runner.py    # EngineExperimentRunner: circuit build, noise, 4 backend dispatch methods
├── hardware.py  # IBM Quantum Runtime: backend resolution, transpilation, calibration, execution
├── context.py   # AppContext: base dirs, env, logging config
└── sweep.py     # Parameter sweep orchestration
```

## Allowed Imports

- `qiskit`, `qiskit_aer` — simulation
- `qiskit_ibm_runtime` — hardware execution (lazy import in hardware.py)
- `numpy` — multinomial sampling for statevector mode
- `src.core.state_preparation` — state factories
- `src.core.noise_models` — noise model creation
- Standard library (`logging`, `typing`, `time`, `dataclasses`)

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
- Propagate `rng_seed` to the backend for reproducibility (simulation only)
- Log backend method, noise model status, and hardware job IDs
- Capture transpilation and calibration metadata for hardware provenance
