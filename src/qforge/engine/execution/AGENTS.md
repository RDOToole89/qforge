# AGENTS.md — Execution Subsystem

Owner: Roibín O'Toole
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
- `qforge.core.state_preparation` — state factories
- `qforge.core.noise_models` — noise model creation
- Standard library (`logging`, `typing`, `time`, `dataclasses`)

## Forbidden Imports

- `qforge.engine.models` — runner must not import Pydantic models (api.py owns that)
- `qforge.engine.analysis` — metrics are computed upstream in api.py
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

## Important: custom_params Separation

`custom_params` carries both state-preparation keys (e.g., `source`, `circuit`, `target`) and noise-model keys (e.g., `correlation_strength`, `topology`, `temperature`). The runner uses an **allowlist** to pass only noise-relevant keys to `create_noise_model()`. State-prep keys stay with the circuit builder.

If you add a new noise parameter that needs to flow through `custom_params`, add it to the allowlist in `runner.py` (`_apply_noise` method).
