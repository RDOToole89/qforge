# AGENTS.md — Core Physics Primitives

Owner: Roibín O'Toole
Token budget: 400

## Purpose

This layer contains **pure physics calculations, metrics, and data schemas**. It is the scientific kernel of the framework and must remain:

- Free of side effects (no IO, network, or external state)
- Fully deterministic and reproducible
- Portable and reusable across different execution contexts

## Local Boundaries

### Allowed Imports

- `numpy`, `scipy` — Numerical computation
- `qiskit` (core modules only) — Quantum circuits and operators
- `pydantic` — Data validation (for schemas, not execution)
- Standard library — `typing`, `dataclasses`, `enum`, etc.

### Forbidden Imports

- `qforge.engine.*` — Orchestration belongs in engine layer
- `matplotlib`, `seaborn` — Visualization belongs in engine/visualization
- `json`, `pickle`, file IO libraries — Persistence belongs in engine
- `logging` (for side effects) — Use return values and exceptions
- External APIs or network libraries

## Structure

```
src/qforge/core/
├── math/               # Shared math primitives — SINGLE SOURCE OF TRUTH
│                       #   (Pauli matrices, Pauli-string ⟨P⟩, relaxation_probability,
│                       #    TVD/Gini, canonical qubit/bit indexing). Import, don't re-derive.
├── analysis/
│   ├── core/           # Information theory (entropy, mutual info)
│   ├── metrics/        # Statistical metrics over measurement distributions (EEC, PCR, Structure Score)
│   └── pipelines/      # Analysis workflows (pure functions)
├── noise_models/       # Physics-compliant noise channels
└── state_preparation/  # Quantum state factory
```

## Do Not

- **Perform file IO** — Return data structures; let engine handle persistence
- **Log to console or files** — Use exceptions and return values to communicate errors
- **Create side effects** — Every function should be pure: same input → same output
- **Import from engine or experiments** — Maintain strict unidirectional dependency flow
- **Embed orchestration logic** — This layer defines "what" not "how" or "when"
- **Use global mutable state** — Pass context explicitly via function parameters
- **Create hardware-specific code** — Keep physics generic; engine handles backends
- **Name metric profiles after a research topic** — built-in profiles stay topic-free (`structure`, `quick`, `information_theory`)

## Always

- **Use Pydantic v2** for all data structures (configs, results, intermediate data)
- **Ensure functions are pure** — No hidden state, no mutations of inputs
- **Add type hints** to all public functions and classes
- **Write docstrings** with physics context: formulas, assumptions, references
- **Validate physics constraints** — Reject unphysical parameters (e.g., T₁ < T₂) early
- **Include educational comments** — Explain quantum mechanics concepts for future readers
- **Use explicit random seeds** — All randomness must be reproducible
- **Return structured data** — Use dataclasses or Pydantic models, not raw dicts

## Key Patterns

### State Preparation

```python
# Good: Pure function returning a circuit
def create_ghz_state(num_qubits: int, seed: int) -> QuantumCircuit:
    circuit = QuantumCircuit(num_qubits)
    # ... quantum operations ...
    return circuit

# Bad: Side effects or implicit state
def create_ghz_state(num_qubits: int):  # Missing seed!
    print("Creating GHZ state...")  # Side effect!
    circuit = QuantumCircuit(num_qubits)
    # ... uses random.random() without seed ...
    return circuit
```

### Noise Model Validation

```python
# Good: Validate physics constraints
def create_thermal_noise(T1: float, T2: float) -> NoiseModel:
    if T2 > 2 * T1:
        raise ValueError(f"Unphysical: T2={T2} > 2*T1={2*T1}")
    # ... create noise model ...
    return noise_model

# Bad: Accept invalid physics
def create_thermal_noise(T1: float, T2: float) -> NoiseModel:
    # No validation!
    return NoiseModel(...)
```

### Metrics Computation

```python
# Good: Pure function with explicit inputs
def compute_eec(
    counts: Dict[str, int],
    entanglement_map: np.ndarray,
    shots: int
) -> float:
    """
    Entanglement-Error Correlation (EEC).

    Measures correlation between error topology and entanglement topology.
    Returns value in [-1, 1] where 1 = perfect correlation.
    """
    # ... computation ...
    return eec_value

# Bad: Hidden dependencies or side effects
def compute_eec(experiment_result):  # Unclear input type
    counts = experiment_result.get_counts()  # Hidden dependency
    logging.info(f"Computing EEC...")  # Side effect
    # ... computation ...
```

## Physics Test Requirements

When modifying this layer, **always run**:

```bash
pytest tests/physics/
```

These tests validate analytical correctness:

- Bell states have zero entropy
- GHZ states have correct correlation signatures
- Entanglement measures match theoretical values
- Noise models preserve quantum channel properties

**If physics tests fail, you've broken the laws of physics—not just the code.**

## Examples

See canonical implementations:

- `src/qforge/core/state_preparation/state_factory.py` — State factory pattern
- `src/qforge/core/noise_models/noise_factory.py` — Noise validation pattern
- `src/qforge/core/analysis/metrics/entanglement_error_correlation.py` — Pure metric computation
- `tests/physics/test_analytical.py` — Physics validation examples
