# Test Suite

~1,100 tests organized by layer (core, engine, integration, physics, schemas) with custom pytest markers. The physics/math core (all of `src/core` plus the engine math modules: `fidelity`, `bloch_math`, `analysis/metrics`, `models/measurement`) sits behind a 95% coverage gate; the verified-value suites assert outputs against analytical/closed-form calculations.

---

## Running Tests

```bash
# Full suite with coverage (default, mirrors CI)
pytest

# Specific layer
pytest tests/core/
pytest tests/engine/
pytest tests/physics/

# By marker
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Quick check (no coverage enforcement)
pytest --no-cov -x -q

# Via Makefile
make test
```

---

## Test Organization

| Directory | What It Tests | Files |
|-----------|---------------|-------|
| `tests/core/` | Analysis metrics, information theory, pipelines, fingerprints | 5 |
| `tests/engine/` | Bloch API, simulation backends, visualization, registry, hardware | 7 |
| `tests/integration/` | End-to-end pipeline, hardware integration | 2 |
| `tests/physics/` | Analytical validation, bootstrap calibration, null models, numerical stability | 5 |
| `tests/schemas/` | Schema bridge compliance | 1 |

---

## Test Files

### Core (pure analysis logic)

- `test_metrics.py` -- All canonical metrics: AI, PCR, EEC, TPS, CI, TC. Tests known-good values, edge cases, and mathematical properties.
- `test_core_modules.py` -- Null models, bootstrap CIs, correlations, topology analysis.
- `test_information_theory.py` -- Entropy, mutual information, Jeffreys smoothing, canonical ordering.
- `test_pipelines.py` -- `run_all_to_schema()` pipeline, v1.0 schema output validation.
- `test_fingerprint.py` -- Fingerprint vector generation and similarity computation.

### Engine (orchestration + execution)

- `test_simulation_backends.py` -- qasm, statevector, density_matrix simulation modes.
- `test_visualization.py` -- Histogram, density matrix, correlation renderers.
- `test_registry.py` -- Experiment registry and metric computation.
- `test_bloch_api.py` -- Bloch sphere coordinate math.
- `test_constants.py` -- Configuration validation.
- `test_hardware_config.py` -- IBM Quantum backend configuration.
- `test_hardware_fidelity.py` -- Hardware fidelity extraction.

### Integration (cross-layer)

- `test_integration.py` -- Full `run()` pipeline end-to-end with metrics.
- `test_hardware_integration.py` -- Hardware backend integration (skipped without credentials).

### Physics (mathematical validation)

- `test_analytical.py` -- Known analytical results verification.
- `test_bootstrap_calibration.py` -- Bootstrap CI coverage calibration.
- `test_null_model.py` -- Null model statistical properties.
- `test_numerical_stability.py` -- Edge cases, overflow, underflow, extreme values.
- `test_properties.py` -- Mathematical invariants and property-based tests.

### Schemas

- `test_schema_bridge.py` -- v1.0 schema compliance for all metrics.

---

## Markers

Custom markers from `pytest.ini`:

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.unit` | Unit tests for individual functions |
| `@pytest.mark.integration` | Integration tests across components |
| `@pytest.mark.edge_case` | Edge case and error handling tests |
| `@pytest.mark.property` | Mathematical property validation tests |
| `@pytest.mark.schema` | Schema compliance tests |
| `@pytest.mark.slow` | Tests that take longer to run |

---

## Coverage

- **Gate**: 95% on `src/core`, enforced by `--cov-fail-under=95` (remaining uncovered lines are unreachable defensive guards)
- **Report**: HTML report generated at `htmlcov/`
- **Scope**: Coverage is measured on `src/core/analysis` only; other modules are tested but not coverage-gated
- **CI**: `make test` runs the full suite with coverage enforcement
