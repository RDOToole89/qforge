# AGENTS.md — Quantum State Preparation

Owner: Roibín O'Toole
Token budget: 350

## Purpose

Educational quantum state factory. States are pure circuits (no noise) with comprehensive physics documentation.

**Supported States**: GHZ, W, Bell, Cluster, Superposition, Custom (6 types)

## Critical Patterns

### 1. BaseState Inheritance

**All states extend BaseState:**

```python
from .base_state import BaseState

class MyState(BaseState):
    """
    Docstring with:
    - Quantum state definition (|ψ⟩ = ...)
    - Physical significance
    - Typical use cases
    """

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """Create the quantum circuit."""
        circuit = QuantumCircuit(self.num_qubits)
        # ... add gates ...
        return circuit
```

### 2. Educational Docstrings

**Every state needs physics context:**

```python
"""
GHZ State Preparation

# The Greenberger-Horne-Zeilinger (GHZ) State
|GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2

# Physical Significance
GHZ states exhibit maximal multipartite entanglement...

# What Experiments Can Explore
- Noise sensitivity: How does decoherence affect the state?
- Measurement correlations: Which basis states remain correlated?
"""
```

### 3. Factory Pattern

**Use factory for state creation:**

```python
# Good: Factory pattern
from .state_factory import prepare_state

circuit = prepare_state(
    state_type="GHZ",
    num_qubits=4,
    seed=42
)

# Bad: Direct instantiation in experiments
from .ghz_state import GHZState
state = GHZState(4)  # Bypasses validation
```

### 4. Hardware Compatibility

**Support real quantum device constraints:**

```python
from .state_factory import prepare_state_for_hardware

circuit = prepare_state_for_hardware(
    state_type="GHZ",
    num_qubits=4,
    backend=real_backend,
    optimization_level=2
)
```

### 5. Registry Pattern

**Register new states in state_constants.py:**

```python
# In state_constants.py
STATE_CLASSES: dict[str, type[BaseState]] = {
    "GHZ": GHZState,
    "W": WState,
    "Bell": BellState,
    "Cluster": ClusterState,
    "Superposition": SuperpositionState,
    "Custom": CustomState,
}
```

## Do Not

- **Add noise in states** — Noise belongs in engine layer, states are pure
- **Skip physics docstrings** — Educational value is core requirement
- **Bypass factory** — Always use `prepare_state()` or `prepare_state_for_hardware()`
- **Hardcode qubit counts** — States should work for any valid n
- **Forget edge cases** — Handle n=1, n=2 specially when needed

## Always

- **Inherit from BaseState** — Ensures consistent interface
- **Document quantum state** — Include |ψ⟩ definition in docstring
- **Explain circuit construction** — Step-by-step gate sequence
- **Validate inputs** — Check num_qubits constraints in create()
- **Register in STATE_CLASSES** — Enable factory discovery
- **Add to __init__.py exports** — Public API surface

## File Structure

```
state_preparation/
├── base_state.py        # BaseState abstract class
├── state_factory.py     # prepare_state(), prepare_state_for_hardware()
├── state_constants.py   # STATE_CLASSES registry
├── ghz_state.py         # |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2
├── w_state.py           # |W⟩ = (|100⟩ + |010⟩ + |001⟩)/√3
├── bell_state.py        # |Φ+⟩ = (|00⟩ + |11⟩)/√2
├── cluster_state.py     # Graph state with CZ gates
├── superposition_state.py  # Equal superposition
└── custom_state.py      # User-defined circuits (4 source modes)
```

## CustomState Source Modes

CustomState supports four ways to define a circuit:

| Source | Description | Use Case |
|--------|-------------|----------|
| `"circuit"` | Pass a pre-built `QuantumCircuit` object directly | Algorithms (Shor, Grover, VQE, QAOA) |
| `"gates"` | Define circuit as a list of gate dicts | Simple programmatic definitions |
| `"builder"` | Call a Python function that returns a circuit | Complex parameterized circuits |
| `"openqasm"` | Load from an OpenQASM file | External circuit import |

The `"circuit"` source is the most flexible — experiments build their own `QuantumCircuit` in Python and pass it through `custom_params`:

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(4, 4)
qc.h(range(4))
qc.measure(range(4), range(4))

config = ExperimentConfig(
    num_qubits=4,
    state_type="CUSTOM",
    custom_params={"source": "circuit", "circuit": qc},
)
```

## Adding a New State

1. Create `my_state.py` inheriting from BaseState
2. Add comprehensive physics docstring
3. Implement `create()` method with educational comments
4. Register in `state_constants.py` STATE_CLASSES dict
5. Export in `__init__.py`
6. Add tests in `tests/core/state_preparation/`
7. Document the educational context and typical use cases

## State Properties

Each state has unique decoherence signatures:

| State | Entanglement | Key Property |
|-------|--------------|--------------|
| GHZ | Global (all-or-nothing) | Maximum correlation, fragile |
| W | Symmetric (distributed) | Robust to single-qubit loss |
| Bell | Bipartite (2-qubit) | Foundation for larger states |
| Cluster | Graph-based | Measurement-based computation |
