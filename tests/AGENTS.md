# AGENTS.md — Test Suite Guidelines

Owner: Roibín O'Toole
Last updated: 2026-04-05

## Purpose

395 tests validating both **software correctness** and **scientific validity**. Physics tests are non-negotiable — if they fail, the code violates quantum mechanics.

## Structure

```
tests/
├── physics/                          ⚛️ PHYSICS VALIDATION (NON-NEGOTIABLE)
│   ├── test_analytical.py            # Pen-and-paper physics verification
│   ├── test_bootstrap_calibration.py # CI estimation accuracy
│   ├── test_null_model.py            # Factorized null model properties
│   ├── test_numerical_stability.py   # Floating-point robustness
│   └── test_properties.py           # Mathematical property verification (requires hypothesis)
│
├── core/                             Unit tests for src/core
│   ├── test_core_modules.py          # State preparation, noise models, imports
│   ├── test_metrics.py               # AI, SS, EEC, TC, CI, PCR, TPS, CES
│   ├── test_information_theory.py    # Entropy, MI, KL/JS divergence, smoothing
│   ├── test_pipelines.py            # Analysis pipeline orchestration
│   └── test_fingerprint.py          # Delta-Cov fingerprinting
│
├── engine/                           Unit tests for src/engine
│   ├── test_constants.py            # Configuration thresholds
│   ├── test_registry.py             # Metric registry, dynamic computation
│   ├── test_simulation_backends.py  # qasm/statevector/density_matrix modes
│   ├── test_visualization.py        # Histogram, density matrix, correlation, circuit renderers
│   ├── test_bloch_api.py            # Partial traces, Bloch vectors, correlators, MI
│   ├── test_hardware_config.py      # Hardware sim_mode validation
│   ├── test_hardware_fidelity.py    # Counts-based fidelity estimation
│   └── test_circuit_preview.py      # Circuit preview endpoint
│
├── integration/                      End-to-end workflow tests
│   ├── test_integration.py          # Complete experiment pipelines
│   └── test_hardware_integration.py # Real hardware tests (skipped without credentials)
│
└── schemas/                          Data contract validation
    └── test_schema_bridge.py        # v1.0 schema compliance
```

## Test Categories

### Physics Tests (`physics/`) — NON-NEGOTIABLE

If physics tests fail, the code is scientifically invalid. Do not commit.

- Bell states have zero entropy
- GHZ states have correct correlation signatures
- Noise models preserve CPTP properties
- T1/T2 relationships obey thermodynamics
- Metrics satisfy mathematical bounds
- Numerical stability under extreme inputs

### Engine Tests (`engine/`)

- 4 simulation backends (qasm, statevector, density_matrix, hardware)
- 6 visualization renderers (histogram, density_matrix, correlation, circuit, metrics_summary, bloch_sphere)
- Hardware config validation (noise+hardware rejected, shots limit, etc.)
- Counts-based fidelity (Bhattacharyya coefficient)
- Bloch math (partial traces, correlators, mutual information)

### Hardware Tests (`integration/test_hardware_integration.py`)

Skipped by default (require IBM Quantum credentials). Run with:
```bash
IBM_QUANTUM_TOKEN=1 pytest tests/integration/test_hardware_integration.py -v
```

## When to Run Tests

| Changed | Run |
|---------|-----|
| `src/core/` | `pytest tests/physics/ tests/core/` |
| `src/engine/` | `pytest tests/engine/ tests/integration/` |
| `src/engine/visualization/` | `pytest tests/engine/test_visualization.py` |
| `src/experiments/` | `pytest tests/integration/` |
| Any change | `pytest tests/ --ignore=tests/physics/test_properties.py` |

## Rules

### Never
- Skip physics tests
- Mock quantum mechanics — use real quantum operations
- Commit failing tests
- Write tests without assertions
- Use random values without seeds

### Always
- Use descriptive test names: `test_bell_state_has_zero_entropy`
- Include docstrings explaining what and why
- Test edge cases (0 qubits, max values, empty input)
- Parameterize similar tests with `@pytest.mark.parametrize`
- Use fixtures for common setups

## Coverage

- `src/core/analysis/`: ~57% now, 55% gate enforced in pytest.ini (target 90% — critical physics code)
- `src/engine/`: 80%+ target
- `src/experiments/`: tested via integration, not unit coverage
