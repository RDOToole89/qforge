# Quantum State Preparation

An educational quantum state preparation system for studying how entanglement topology shapes quantum behavior under noise. Each component serves both as a learning resource and a production tool for quantum experiments.

## State Types at a Glance

Different quantum states exhibit different entanglement topologies:

- **GHZ States**: Global entanglement — correlations span all qubits
- **Bell States**: Bipartite entanglement — the fundamental two-qubit building block
- **W States**: Symmetric, distributed entanglement — robust to single-qubit loss
- **Cluster States**: Local correlations forming network-like topologies
- **Superposition States**: Non-entangled product states — the natural control baseline
- **Custom States**: Arbitrary user-defined circuits for novel topologies and algorithms

---

## Framework Architecture

### Design Principles

- **Single Responsibility**: Each component has one clear purpose
- **Separation of Concerns**: State preparation cleanly separated from analysis
- **Educational Value**: Every component teaches quantum mechanics principles
- **Framework Integration**: Clean interfaces with engine and analysis modules

### Data Flow

```
User Request → Factory → State.create() → Circuit → Engine → Noise → Analysis
                ↑              ↑
         Registry Pattern   BaseState
```

---

## File Organization & Connections

### Core Components

#### 1. `base_state.py` - **Foundation Class**

```python
class BaseState(ABC):
    """Abstract base for all quantum state preparation"""
```

**Purpose**:

- Provides common interface for all state types
- Implements shared utilities (simulation, validation, logging)
- Enforces consistent behavior across framework
- Teaches fundamental quantum state concepts

**Key Methods**:

- `create()`: Abstract method each state implements
- `get_theoretical_state_vector()`: Calculate ideal state
- `get_experiment_metadata()`: State metadata for provenance and reporting
- `validate_for_hardware()`: Check real device compatibility
- `_simulate_circuit_state_vector()`: Common simulation helper
- `_validate_large_system()`: Consistent size validation
- `_generate_fallback_state()`: Error recovery helper

**Framework Integration**: BaseState is the contract between factory and engine

---

#### 2. `state_factory.py` - **Creation Interface**

```python
def prepare_state(state_type: str, num_qubits: int, ...) -> QuantumCircuit
def prepare_state_for_hardware(state_type: str, backend=None, ...) -> QuantumCircuit
```

**Purpose**:

- Implements Factory Pattern for unified state creation
- Provides hardware validation for real quantum devices
- Validates inputs before state instantiation
- Serves as main interface between engine and states

**Key Functions**:

- `prepare_state()`: Standard factory function
- `prepare_state_for_hardware()`: Hardware-aware creation
- `create_state_instance()`: Direct state object creation
- `validate_state_request()`: Input validation
- `get_available_states()`: Discovery interface

**Framework Integration**: Factory is the primary interface used by engine

---

#### 3. `state_constants.py` - **Registry System**

```python
STATE_CLASSES = {
    "GHZ": GHZState,
    "BELL": BellState,
    # ... etc
}
```

**Purpose**:

- Implements Registry Pattern for state type management
- Provides type-safe state class lookup
- Enables dynamic state discovery
- Maintains separation between factory logic and state implementation

**Key Components**:

- `STATE_CLASSES`: Central registry mapping
- `get_state_class()`: Type-safe class retrieval
- `get_state_info()`: Comprehensive state documentation
- `validate_state_registry()`: Import-time validation

**Framework Integration**: Registry enables dynamic state loading and discovery

---

### State Implementation Classes

#### 4. `ghz_state.py` - **Global Entanglement**

```python
class GHZState(BaseState):
    """|GHZ_n⟩ = (|00...0⟩ + |11...1⟩)/√2"""
```

**Quantum Mechanics**: Maximally entangled state with global correlations
**Implementation**: Analytical formula (H + CNOT chain)
**Educational Value**: Teaches global entanglement and multipartite correlations

---

#### 5. `bell_state.py` - **Fundamental Bipartite Entanglement**

```python
class BellState(BaseState):
    """Four Bell states: |Φ±⟩, |Ψ±⟩"""
```

**Quantum Mechanics**: Maximally entangled two-qubit states
**Implementation**: Analytical formulas for all four variants
**Educational Value**: Foundation of quantum entanglement theory and Bell inequality violations

---

#### 6. `w_state.py` - **Symmetric Multipartite Entanglement**

```python
class WState(BaseState):
    """|W_n⟩ = (|100...0⟩ + |010...0⟩ + ... + |00...01⟩)/√n"""
```

**Quantum Mechanics**: Symmetric multipartite entanglement with robustness
**Implementation**: Analytical W-state vector with optimized circuit construction
**Educational Value**: Demonstrates robustness vs fragility in quantum states

---

#### 7. `cluster_state.py` - **Graph-Based Network States**

```python
class ClusterState(BaseState):
    """Graph states with local correlations"""
```

**Quantum Mechanics**: Local correlations creating global entanglement
**Implementation**: Circuit simulation (topology-dependent)
**Educational Value**: Bridges quantum computing and network science; foundation of measurement-based computation

---

#### 8. `superposition_state.py` - **Non-Entangled Control States**

```python
class SuperpositionState(BaseState):
    """Product superposition: |+⟩^n (no entanglement)"""
```

**Quantum Mechanics**: Separable states with classical correlations only
**Implementation**: Tensor product of single-qubit superpositions
**Educational Value**: Contrast between quantum and classical correlations; natural control baseline

---

#### 9. `custom_state.py` - **Arbitrary Circuits**

```python
class CustomState(BaseState):
    """User-defined arbitrary quantum circuits"""
```

**Quantum Mechanics**: Arbitrary quantum states via circuit specification
**Implementation**: Circuit simulation with multiple input methods
**Educational Value**: Demonstrates quantum circuit model flexibility; enables algorithm experiments

---

### Package Interface

#### 10. `__init__.py` - **Public API**

```python
from .state_factory import prepare_state, prepare_state_for_hardware
from .state_constants import STATE_CLASSES, get_available_states
# ... all public interfaces
```

**Purpose**: Clean public API for external framework components
**Integration**: Primary import point for engine and other modules

---

## Framework Integration

#### 1. **Engine Layer**

```python
# In engine/api.py
from qforge.core.state_preparation import prepare_state

def run_experiment(config):
    circuit = prepare_state(
        config.state_type,
        config.num_qubits,
        config.state_params
    )
    # → Pass to noise models
    # → Pass to analysis
```

#### 2. **CLI Layer**

```python
from qforge.core.state_preparation import get_available_states, prepare_state

available = get_available_states()
# Display to user for selection
circuit = prepare_state(user_choice, user_qubits, user_params)
```

#### 3. **Visualization Layer**

```python
circuit = prepare_state("GHZ", 3)
# → Generate circuit diagrams
# → Create educational visualizations
```

#### 4. **Analysis Layer**

```python
# Analysis modules receive prepared circuits.
# State preparation provides metadata for context:
state_info = state.get_theoretical_properties()
metadata = state.get_experiment_metadata()
```

---

## Educational Architecture

### Teaching Quantum Mechanics Concepts

#### **Fundamental Concepts**

- **Quantum Superposition**: Demonstrated in all states
- **Quantum Entanglement**: Different topologies in each state type
- **Quantum Measurement**: Correlation predictions per state type
- **Quantum Circuits**: Gate sequences for state preparation

#### **Advanced Topics**

- **Entanglement Topology**: How correlation structure affects behavior
- **Quantum Error Correction**: Foundation in cluster states
- **Quantum Algorithms**: State preparation for algorithm development
- **Hardware Constraints**: Real device limitations and compatibility

#### **Experimental Method**

- **Experimental Design**: Control states and systematic comparisons
- **Data Analysis**: Theoretical predictions vs experimental results
- **Reproducibility**: Exact state specifications and provenance tracking

---

## Quality Standards

### Code Quality

- **Test Coverage**: >95% for all core functionality
- **Documentation**: Every method includes educational explanations
- **Type Safety**: Full typing annotations throughout
- **Error Handling**: Graceful degradation with educational messages

### Educational Quality

- **Clarity**: Every concept explained with quantum mechanics context
- **Completeness**: Full coverage of relevant quantum computing topics
- **Accuracy**: All theoretical calculations verified against known results
- **Accessibility**: Explanations appropriate for different skill levels

---

## Usage Examples

### Basic State Creation

```python
from qforge.core.state_preparation import prepare_state

# Create GHZ state for 3 qubits
circuit = prepare_state("GHZ", 3)

# Create Bell state with specific variant
circuit = prepare_state("BELL", 2, {"variant": "phi_plus"})

# Create cluster state with 2D topology
circuit = prepare_state("CLUSTER", 6, {
    "lattice": "2d",
    "rows": 2,
    "cols": 3
})
```

### Hardware-Aware Creation

```python
from qforge.core.state_preparation import prepare_state_for_hardware
from qiskit_ibm_runtime import QiskitRuntimeService

# Load a real quantum backend
service = QiskitRuntimeService()
backend = service.backend("ibm_brisbane")

# Create state with hardware validation
circuit = prepare_state_for_hardware(
    "GHZ", 3,
    backend=backend
)
```

### Advanced State Instance Access

```python
from qforge.core.state_preparation import create_state_instance

# Create state object for detailed analysis
ghz_state = create_state_instance("GHZ", 3)

# Access theoretical properties
properties = ghz_state.get_theoretical_properties()
metadata = ghz_state.get_experiment_metadata()
state_vector = ghz_state.get_theoretical_state_vector()

# Hardware validation
warnings = ghz_state.validate_for_hardware(backend_constraints)
```

### State Discovery and Documentation

```python
from qforge.core.state_preparation import get_available_states, get_state_info

# Discover available states
available = get_available_states()
# ['BELL', 'CLUSTER', 'CUSTOM', 'GHZ', 'SUPERPOSITION', 'W']

# Get comprehensive documentation
info = get_state_info()
print(info["GHZ"]["description"])
# "Global multipartite entanglement state"
```

---

## Future Extensions

- **Additional State Types**: Spin squeezed states, NOON states, Dicke states
- **Hardware Optimization**: Automatic circuit compilation for specific devices
- **Educational Tools**: Interactive visualizations and quantum mechanics tutorials
- **Applications**: Error-correction code states, algorithm initialization, many-body state preparation

---

## Learning Resources

### For Beginners

1. Start with `ghz_state.py` - demonstrates basic entanglement
2. Explore `bell_state.py` - foundation of quantum mechanics
3. Try `superposition_state.py` - understand separable states
4. Use factory functions for hands-on experimentation

### For Intermediate Users

1. Study `cluster_state.py` - network quantum computing
2. Examine `w_state.py` - multipartite entanglement
3. Explore custom states for algorithm development
4. Investigate hardware validation for real devices

### For Advanced Users

1. Extend the framework with novel state types
2. Combine with the noise models and analysis metrics
3. Develop hardware-specific optimizations
