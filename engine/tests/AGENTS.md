# AGENTS.md — Test Suite Guidelines

Owner: Research Engineering (Roibín O'Toole)
Last updated: 2025-12-02
Token budget: 400

## Purpose

This directory contains the test suite that validates both **software correctness** and **scientific validity**. Tests are the final gatekeepers of quality—if tests pass, the framework can be trusted for research.

**Critical Distinction**: Physics tests (`tests/physics/`) are not optional. They verify that the code obeys quantum mechanics and thermodynamics.

## Structure

```
tests/
├── physics/                      # ⚛️ PHYSICS VALIDATION (NON-NEGOTIABLE)
│   └── test_analytical.py        # Pen-and-paper physics verification
├── core/                         # Unit tests for src/core
│   ├── test_core_modules.py      # State preparation, noise models
│   ├── test_metrics.py           # EEC, PCR, Structure Score
│   ├── test_information_theory.py # Entropy, mutual information
│   └── test_pipelines.py         # Analysis pipeline logic
├── engine/                       # Unit tests for src/engine
│   ├── test_constants.py         # Configuration constants
│   └── test_registry.py          # Component registry
├── integration/                  # End-to-end workflow tests
│   └── test_integration.py       # Complete experiment pipelines
├── schemas/                      # Schema validation tests
│   └── test_schema_bridge.py     # Pydantic ↔ JSON Schema sync
├── AGENTS.md                     # This file
└── __init__.py
```

## Test Categories

### 1. Physics Tests (`physics/`) — NON-NEGOTIABLE

**Purpose**: Validate that code matches theoretical quantum mechanics.

**What they test**:
- Bell states have zero entropy
- GHZ states have correct correlation signatures
- Entanglement measures match analytical formulas
- Noise models preserve quantum channel properties
- T₁/T₂ relationships obey thermodynamics

**Critical Rule**: **If physics tests fail, the code is scientifically invalid.** Do not commit code that breaks these tests.

**When to run**:
- After any change to `src/core/`
- Before every commit
- In CI/CD pipeline (blocking)

**Example**:
```python
def test_bell_state_has_zero_entropy():
    """Bell states are maximally entangled → entropy = 0"""
    circuit = create_bell_state()
    statevector = Statevector(circuit)
    entropy = compute_entropy(statevector)
    assert abs(entropy) < 1e-10, "Bell state must have zero entropy"
```

### 2. Unit Tests — SOFTWARE CORRECTNESS

**Purpose**: Validate that individual components work correctly.

**Files**:
- `core/test_core_modules.py` — State preparation, noise models
- `core/test_metrics.py` — EEC, PCR, Structure Score computation
- `core/test_information_theory.py` — Entropy, mutual information
- `engine/test_constants.py` — Configuration constants
- `engine/test_registry.py` — Component registry

**Rules**:
- Test pure functions in isolation
- Use fixtures for common setups
- Mock external dependencies (Qiskit backends)
- Fast execution (< 1s per test)

### 3. Integration Tests — WORKFLOW VALIDATION

**Purpose**: Validate that components work together correctly.

**Files**:
- `integration/test_integration.py` — End-to-end experiment workflows
- `core/test_pipelines.py` — Analysis pipeline orchestration

**Rules**:
- Test realistic scenarios
- Use actual Qiskit simulators (not mocks)
- Validate data flow through layers
- Slower execution acceptable (< 10s per test)

### 4. Schema Tests — DATA CONTRACT VALIDATION

**Purpose**: Ensure Pydantic models match JSON schemas.

**Files**:
- `schemas/test_schema_bridge.py` — Pydantic ↔ JSON Schema synchronization

**Rules**:
- Validate against actual schema files in `schemas/`
- Test valid and invalid examples
- Ensure provenance fields are complete

## Local Boundaries

### Allowed Imports

- `pytest` — Testing framework
- `src.*` — All framework modules
- `qiskit` — For actual quantum operations
- `numpy`, `scipy` — Numerical comparisons
- `pydantic`, `jsonschema` — Validation
- Standard library testing utilities

### Forbidden Imports

- Production dependencies not needed for testing
- External network services (tests must run offline)
- GUI or visualization libraries (unless testing viz code)

## Do Not

- **Skip physics tests** — They are mandatory, not optional
- **Mock quantum mechanics** — Use real quantum operations or analytical formulas
- **Commit failing tests** — All tests must pass before merge
- **Write tests without assertions** — Every test must validate something
- **Test implementation details** — Test behavior, not internal structure
- **Use random values without seeds** — Tests must be reproducible
- **Create flaky tests** — Tests should be deterministic

## Always

- **Run physics tests first** — `pytest tests/physics/` before anything else
- **Use descriptive test names** — `test_bell_state_has_zero_entropy` not `test1`
- **Include docstrings** — Explain what the test validates and why
- **Use explicit assertions** — `assert value == expected` with clear messages
- **Parameterize similar tests** — Use `@pytest.mark.parametrize`
- **Use fixtures for setup** — Avoid code duplication in tests
- **Test edge cases** — Zero qubits, maximum values, invalid inputs
- **Verify error handling** — Test that invalid inputs raise proper exceptions

## Test Requirements by Layer

### When modifying `src/core/`:
```bash
# MANDATORY
pytest tests/physics/              # Physics validation
pytest tests/core/                 # Unit tests for core layer
```

### When modifying `src/engine/`:
```bash
pytest tests/engine/               # Engine unit tests
pytest tests/integration/          # Workflow validation
pytest tests/schemas/              # Schema sync
```

### When modifying `schemas/`:
```bash
pytest tests/schemas/              # Pydantic ↔ JSON sync
# Validate examples against schemas manually
```

## Key Patterns

### Physics Test Pattern

```python
def test_ghz_state_correlation():
    """
    GHZ state should have perfect correlation:
    All qubits measure same value (all 0 or all 1).
    """
    num_qubits = 3
    circuit = create_ghz_state(num_qubits)

    # Run on statevector simulator (exact)
    statevector = Statevector(circuit)

    # Analytical expectation: ⟨Z₀Z₁Z₂⟩ = 1
    correlation = compute_correlation(statevector, [0, 1, 2])

    assert abs(correlation - 1.0) < 1e-10, \
        f"GHZ correlation should be 1.0, got {correlation}"
```

### Unit Test Pattern

```python
@pytest.mark.parametrize("state_type,expected_entropy", [
    ("bell", 0.0),
    ("product", 0.0),
    ("GHZ", 0.0),
])
def test_pure_states_have_zero_entropy(state_type, expected_entropy):
    """Pure states always have zero entropy."""
    circuit = StateFactory.create(state_type, num_qubits=2)
    statevector = Statevector(circuit)
    entropy = compute_entropy(statevector)

    assert abs(entropy - expected_entropy) < 1e-10
```

### Integration Test Pattern

```python
def test_end_to_end_experiment():
    """Complete workflow: config → execute → validate."""
    config = ExperimentConfig(
        num_qubits=3,
        state_type="GHZ",
        noise_model_type="depolarizing",
        error_rate=0.01,
        shots=1024,
        seed=42
    )

    result = run_experiment(config)

    # Validate structure
    assert result.config.num_qubits == 3
    assert result.provenance.config_hash is not None
    assert result.metrics.structure_score is not None

    # Validate physics
    assert 0 <= result.metrics.structure_score <= 1
```

### Schema Test Pattern

```python
def test_experiment_result_matches_schema():
    """Pydantic model must produce valid JSON Schema."""
    result = ExperimentResult(...)
    result_dict = result.model_dump()

    with open("schemas/v1/execution/experiment_result.schema.json") as f:
        schema = json.load(f)

    jsonschema.validate(result_dict, schema)  # Raises if invalid
```

## CI/CD Integration

Tests run in this order (fail-fast):

1. **Physics tests** — If these fail, stop immediately
2. **Unit tests** — Fast validation of components
3. **Integration tests** — Slower end-to-end validation
4. **Schema tests** — Data contract validation

```bash
# Complete test suite
pytest tests/ -v

# Quick validation (physics + core units only)
pytest tests/physics/ tests/core/ -v

# Slow full suite
pytest tests/ -v --durations=10
```

## Coverage Requirements

- **`src/core/`**: 90%+ coverage (critical physics code)
- **`src/engine/`**: 80%+ coverage (orchestration)
- **`src/experiments/`**: 50%+ coverage (research scripts, less critical)

```bash
pytest --cov=src/core --cov=src/engine --cov-report=html
```

## Debugging Failed Tests

1. **Physics test fails** → Code violates quantum mechanics
   - Check analytical formulas
   - Verify circuit construction
   - Compare with pen-and-paper derivation

2. **Unit test fails** → Component logic error
   - Check function inputs/outputs
   - Verify edge cases
   - Review recent changes

3. **Integration test fails** → Layer interaction broken
   - Check data flow between core/engine
   - Verify schema validation
   - Test components individually first

4. **Schema test fails** → Pydantic/JSON mismatch
   - Update Pydantic model to match schema
   - Or update schema and bump version

## Examples

See canonical test implementations:

- `tests/physics/test_analytical.py` — Physics validation gold standard
- `tests/core/test_core_modules.py` — Unit test patterns
- `tests/integration/test_integration.py` — End-to-end workflow tests
- `tests/schemas/test_schema_bridge.py` — Schema synchronization tests
