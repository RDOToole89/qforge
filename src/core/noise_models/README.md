# Quantum Noise Models

An educational, physics-compliant quantum noise modeling system for studying how environmental coupling affects quantum information. Each component serves both as a learning resource and a production tool for decoherence experiments.

## Noise Models at a Glance

Each noise model represents one environmental coupling mechanism:

- **Depolarizing Noise**: Uniform random Pauli errors — the worst-case baseline
- **Amplitude Damping**: Energy relaxation (T1 processes)
- **Phase Damping**: Pure dephasing (T2* processes) without energy exchange
- **Bit Flip**: Classical digital errors (random X)
- **Phase Flip**: Longitudinal coupling (random Z), preserves measurement statistics
- **Thermal Relaxation**: Combined T1/T2 with finite temperature — most realistic hardware model

---

## Framework Architecture

### Design Principles

- **Single Responsibility**: Each noise model represents one environmental coupling mechanism
- **Separation of Concerns**: Noise generation cleanly separated from analysis
- **Educational Value**: Every component teaches quantum decoherence physics
- **Engine Integration**: Clean interfaces with the experiment execution engine

### Data Flow

```
User Request → Factory → Noise.apply() → NoiseModel → Engine → Analysis
                ↑              ↑
         Registry Pattern   BaseNoise
```

---

## File Organization & Connections

### Core Components

#### 1. `base_noise.py` - **Foundation Class**

```python
class BaseNoise(ABC):
    """Abstract base for all quantum noise models"""
```

**Purpose**:

- Provides common interface for all noise types
- Implements shared utilities (validation, logging, hardware compatibility)
- Enforces consistent behavior across the framework
- Teaches fundamental quantum decoherence concepts

**Class attributes** (declared by every concrete noise model):

- `NOISE_TYPE`: Canonical noise-type string
- `IS_UNITAL`: Whether the channel is unital (preserves the maximally mixed state)
- `CATALOG`: Descriptive metadata (mechanism summary, `use_case`, etc.)

**Key Methods**:

- `apply()`: Abstract method each noise implements
- `get_basic_properties()`: Common noise metadata
- `validate_for_hardware()`: Check real device compatibility
- `log_noise_creation()`: Consistent logging helper
- `get_physics_description()`: Educational physics content

**Framework Integration**: BaseNoise is the contract between factory and engine

---

#### 2. `noise_factory.py` - **Creation Interface**

```python
def create_noise_model(noise_type: str, num_qubits: int, ...) -> NoiseModel
def create_noise_model_for_hardware(noise_type: str, backend=None, ...) -> NoiseModel
```

**Purpose**:

- Implements Factory Pattern for unified noise creation
- Provides hardware validation for real quantum devices
- Validates inputs before noise instantiation
- Serves as main interface between engine and noise models

**Key Functions**:

- `create_noise_model()`: Standard factory function
- `create_noise_model_for_hardware()`: Hardware-aware creation
- `create_noise_instance()`: Direct noise object creation
- `validate_noise_request()`: Input validation
- `get_available_noise_types()`: Discovery interface
- `get_noise_info()`: Educational descriptions

**Framework Integration**: Factory is the primary interface used by engine

---

#### 3. Individual Noise Models - **Physics Implementation**

Each noise model implements a specific environmental coupling mechanism:

##### **`depolarizing.py` - Uniform Random Errors**

- **Physics**: Random Pauli X, Y, Z errors with equal probability
- **Educational Focus**: Worst-case noise, channel unitality, Pauli decomposition
- **Hardware Origin**: High-temperature environments, multiple error sources

##### **`amplitude_damping.py` - Energy Relaxation**

- **Physics**: T1 processes with spontaneous emission and thermal excitation
- **Educational Focus**: Non-unital channels, energy conservation, master equations
- **Hardware Origin**: Electromagnetic coupling, finite temperature effects

##### **`phase_damping.py` - Pure Dephasing**

- **Physics**: T2\* processes with elastic environmental scattering
- **Educational Focus**: T2\* measurements, elastic coupling, coherence preservation
- **Hardware Origin**: Charge noise, magnetic field fluctuations

##### **`bit_flip.py` - Classical Digital Errors**

- **Physics**: Random X rotations preserving computational basis structure
- **Educational Focus**: Classical error generalization, transverse coupling
- **Hardware Origin**: Drive field errors, crosstalk, amplitude noise

##### **`phase_flip.py` - Longitudinal Coupling**

- **Physics**: Random Z rotations preserving measurement statistics
- **Educational Focus**: Longitudinal coupling, interference destruction
- **Hardware Origin**: Magnetic flux noise, charge fluctuations

##### **`thermal_relaxation.py` - Realistic Hardware**

- **Physics**: Combined T1/T2 processes with finite temperature effects
- **Educational Focus**: Master equations, thermal equilibrium, T1/T2 relationship
- **Hardware Origin**: Dilution refrigerator environments, comprehensive coupling

---

## Channel Conventions (Physics Consistency)

The noise channels follow standard textbook conventions, and each model's
`get_kraus_operators()` returns the SAME channel that its `apply()` simulates:

- **Uniform application**: `bit_flip`, `phase_flip`, and `phase_damping` apply a
  single error channel uniformly to every gate in `gate_list`. (There is no
  per-gate "gate sensitivity" heuristic — that earlier behavior was removed.)
- **Phase damping**: standard 2-operator Kraus form with off-diagonal coherence
  factor √(1 − λ).
- **Amplitude damping**: standard zero-temperature (T = 0) amplitude-damping
  channel.
- **Depolarizing**: multi-qubit `get_kraus_operators()` returns the genuine
  n-qubit Qiskit depolarizing channel.

Pauli matrices and the `relaxation_probability(t, τ) = 1 − exp(−t/τ)` conversion
come from the shared `src/core/math/` primitives (single source of truth).

---

## Educational Framework

### Physics Education Hierarchy

```
Level 1: Basic Concepts (BitFlip, PhaseFlip)
├── Classical error mechanisms
├── Pauli operator physics
└── Single-axis environmental coupling

Level 2: Quantum Phenomena (Depolarizing, PhaseDamping, AmplitudeDamping)
├── Quantum channel theory
├── Unitality and information theory
└── Energy vs coherence effects

Level 3: Hardware Reality (ThermalRelaxation)
├── Combined T1/T2 physics
├── Finite temperature effects
└── Realistic device constraints
```

---

## Implementation Patterns

### Consistent Interface Pattern

Every noise model implements the same interface:

```python
class MyNoise(BaseNoise):
    NOISE_TYPE = "MY_NOISE"       # canonical type string
    IS_UNITAL = True               # channel unitality
    CATALOG = {                    # descriptive metadata
        "mechanism": "...",
        "use_case": "...",
    }

    def __init__(self, error_rate, num_qubits, experiment_id, **physics_params):
        # Physics parameter validation
        # Store parameters
        # Calculate derived properties
        # Initialize BaseNoise
        # Log creation with context

    def apply(self, noise_model, gate_list, qubits_for_error=None):
        # Build the Qiskit error channel for this mechanism
        # Apply it UNIFORMLY to every gate in gate_list
        # Log application results

    def get_physics_description(self) -> Dict[str, str]:
        # Educational physics content

    def get_theoretical_properties(self) -> Dict[str, Any]:
        # Quantum channel properties
```

### Educational Documentation Pattern

Every component includes comprehensive educational content:

- **Module docstrings**: Physical mechanism explanation
- **Class docstrings**: Quantum channel theory and typical use cases
- **Method docstrings**: Implementation details and educational notes
- **Physics descriptions**: Real-world examples and principles

### Physics Validation Pattern

All models enforce physics constraints:

- **Parameter bounds**: Probabilities ∈ [0,1], times > 0
- **Quantum constraints**: T2 ≤ 2T1, unitarity preservation
- **Hardware limits**: Realistic parameter ranges with warnings
- **Consistency checks**: Cross-parameter validation

### Hardware Integration Pattern

Consistent hardware compatibility checking:

- **Device constraints**: Max qubits, supported gates, error rate limits
- **Timing validation**: Gate times vs coherence times
- **Temperature effects**: Thermal population calculations
- **Warning system**: Guidance for unrealistic parameters

---

## Framework Integration

### Engine Integration

The noise models integrate with the experiment engine:

```python
# Engine uses factory for noise creation
from src.core.noise_models.noise_factory import create_noise_model

# Create noise model for an experiment
noise_model = create_noise_model(
    noise_type="DEPOLARIZING",
    num_qubits=3,
    error_rate=0.05,
    experiment_id="noise_study_001"
)

# Engine applies noise to quantum circuits
circuit = prepare_quantum_state("GHZ", 3)
experiment_runner.run_with_noise(circuit, noise_model)
```

### State Preparation Separation

Clean separation between quantum state creation and noise application:

- **State Preparation**: Creates ideal quantum states
- **Noise Models**: Models environmental decoherence
- **Engine**: Coordinates state + noise → realistic quantum evolution
- **Analysis**: Computes metrics over the resulting measurement distributions

---

## Usage Examples

### Basic Noise Modeling

```python
from src.core.noise_models.noise_factory import create_noise_model, create_noise_instance

# Create an educational noise model
noise_model = create_noise_model("DEPOLARIZING", 2, error_rate=0.1)

# Learn about the physics
noise = create_noise_instance("DEPOLARIZING", 2, error_rate=0.1)
physics = noise.get_physics_description()
print(f"Mechanism: {physics['mechanism']}")
print(f"Origin: {physics['origin']}")
```

### Full Experiment Setup

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

# Configure an experiment with noise and analysis metrics
config = ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    noise_enabled=True,
    noise_type="amplitude_damping",
    noise_params={"t1": 100e-6, "temperature": 0.015},
    metrics="decoherence",
)

# Run and access the metrics bundle
result = run(config)
metrics = result.metrics_bundle
```

### Hardware Validation

```python
from qiskit_ibm_runtime import QiskitRuntimeService
from src.core.noise_models.noise_factory import create_noise_model_for_hardware

# Load a real quantum backend
service = QiskitRuntimeService()
backend = service.backend("ibm_brisbane")

# Create hardware-validated noise model
noise_model = create_noise_model_for_hardware(
    'THERMAL_RELAXATION', 3, backend=backend,
    custom_params={'t1': 100e-6, 't2': 80e-6}
)
```

---

## Typical Experiment Designs

1. **Baseline Studies**: Use depolarizing noise for a uniform-degradation baseline
2. **Mechanism Studies**: Compare different environmental coupling types
3. **Hardware Studies**: Use thermal relaxation for realistic device behavior
4. **Control Studies**: No noise vs specific noise types
5. **Parameter Sweeps**: Error rates, timescales, temperatures
6. **State Comparisons**: Different entanglement topologies under identical noise

### Educational Progression

1. **Classical Foundations**: Start with bit flip and phase flip
2. **Quantum Channels**: Progress to depolarizing and pure dephasing
3. **Energy Dynamics**: Study amplitude damping and thermal effects
4. **Hardware Reality**: Complete with thermal relaxation studies

---

## Development Guidelines

### Adding New Noise Models

1. **Inherit from BaseNoise**: Use established patterns
2. **Declare class attributes**: `NOISE_TYPE`, `IS_UNITAL`, and `CATALOG`
3. **Physics First**: Start with physical mechanism understanding
4. **Educational Focus**: Comprehensive documentation required
5. **Hardware Validation**: Include realistic parameter constraints

### Code Quality Standards

- **Physics Accuracy**: All parameters must respect quantum constraints
- **Educational Value**: Every component teaches quantum mechanics
- **Hardware Reality**: Realistic parameter ranges and validation
- **Interface Consistency**: Follow established patterns exactly

### Testing Requirements

- **Physics Validation**: Parameter constraint testing
- **Interface Compliance**: BaseNoise contract fulfillment
- **Educational Content**: Documentation completeness
- **Hardware Integration**: Real device compatibility

---

## Future Enhancements

1. **Non-Markovian noise**: Memory effects and non-exponential decay
2. **Gate-Dependent noise**: Noise that depends on specific gate operations
3. **Measurement Noise**: POVM and readout error modeling
4. **Dynamic Noise**: Time-varying environmental coupling
5. **Device Characterization**: Automated parameter extraction
