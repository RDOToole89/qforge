# Quantum Experiment Simulator

A comprehensive, research-grade quantum simulation framework built with **Qiskit**. This advanced tool enables quantum experiments with configurable parameters, extensive analysis capabilities, and sophisticated visualization for studying quantum decoherence, entanglement, and quantum state dynamics.

---

## 🏗️ Project Structure

```
qiskit-experiments/
├── src/
│   ├── analysis/                    # 🔬 Advanced quantum analysis modules
│   │   ├── correlations.py          # Pairwise, conditional, permutation-symmetric correlations
│   │   ├── decoherence.py          # Fubini-Study distance metrics
│   │   ├── symmetry.py             # SU(2), SU(3), parity symmetry analysis
│   │   ├── clustering.py           # Qubit clustering algorithms
│   │   ├── bloch.py               # Bloch sphere computations
│   │   └── transitions.py         # Error transition analysis
│   │
│   ├── visualization/              # 📊 Comprehensive visualization suite
│   │   ├── hypergraph.py          # Original hypergraph analysis (880 lines)
│   │   ├── hypergraph_clean.py    # Clean modular hypergraph visualization
│   │   ├── visualization_handler.py # Main visualization orchestrator
│   │   ├── histogram.py           # Measurement histogram plots
│   │   ├── density_matrix.py      # Density matrix visualization
│   │   └── visualizer.py          # Core visualization utilities
│   │
│   ├── state_preparation/         # 🎯 Quantum state preparation
│   │   ├── base_state.py          # Base class for quantum states
│   │   ├── ghz_state.py          # GHZ state preparation
│   │   ├── w_state.py            # W state preparation
│   │   ├── cluster_state.py      # Cluster state preparation
│   │   ├── state_factory.py      # State factory pattern
│   │   └── state_constants.py    # State type definitions
│   │
│   ├── noise_models/              # 🔧 Quantum noise models
│   │   ├── base_noise.py         # Base noise class
│   │   ├── noise_factory.py      # Noise model factory
│   │   ├── depolarizing.py       # Depolarizing noise
│   │   ├── phase_flip.py         # Phase flip noise
│   │   ├── amplitude_damping.py  # Amplitude damping
│   │   ├── phase_damping.py      # Phase damping
│   │   ├── thermal_relaxation.py # Thermal relaxation
│   │   └── bit_flip.py          # Bit flip noise
│   │
│   ├── config/                   # ⚙️ Configuration management
│   │   ├── constants.py          # System constants
│   │   ├── params.py            # Parameter validation
│   │   ├── defaults.py          # Default configurations
│   │   └── config.py            # Configuration loader
│   │
│   ├── utils/                    # 🛠️ Utility modules
│   │   ├── logger.py            # Structured logging
│   │   ├── results.py           # Result management
│   │   ├── input_handler.py     # Interactive input handling
│   │   ├── validation.py        # Parameter validation
│   │   ├── messages.py          # User interface messages
│   │   ├── cli.py              # Command-line utilities
│   │   └── config_loader.py    # Configuration loading
│   │
│   ├── tests/                   # 🧪 Test suite
│   └── run_experiment.py        # Core experiment runner
│
├── scripts/                      # 📜 Command-line scripts
│   └── run_experiment_cli.py    # CLI experiment runner
│
├── logs/                         # 📝 Log files directory
├── results/                      # 📊 Experiment results directory
├── archived_experiments/         # 📁 Archived experiment data
├── main.py                       # 🚀 Interactive experiment runner
└── requirements.txt              # 📦 Python dependencies
```

---

## 🔬 Advanced Features

### **Quantum State Analysis**

- **Correlation Analysis**: Pairwise, conditional, and permutation-symmetric correlations
- **Decoherence Metrics**: Fubini-Study distance calculations for quantum state evolution
- **Symmetry Analysis**: SU(2), SU(3), and parity symmetry detection
- **Clustering Algorithms**: K-means clustering of qubits based on correlation patterns
- **Bloch Sphere Analysis**: Bloch vector computations and trajectory analysis
- **Error Transition Analysis**: Markov chain analysis of quantum error dynamics

### **Quantum State Preparation**

- **GHZ States**: (|000...⟩ + |111...⟩)/√2 multipartite entanglement
- **W States**: (|100...⟩ + |010...⟩ + |001...⟩)/√3 symmetric states
- **Cluster States**: Entangled lattice structures
- **Extensible Architecture**: Easy addition of new quantum states

### **Noise Models**

- **Depolarizing Noise**: Random Pauli errors
- **Phase Flip Noise**: Z-basis errors with configurable probabilities
- **Amplitude Damping**: Energy relaxation (T1 processes)
- **Phase Damping**: Pure dephasing (T2 processes)
- **Thermal Relaxation**: Realistic T1/T2 thermal noise
- **Bit Flip Noise**: X-basis errors

### **Visualization Suite**

- **Hypergraph Visualization**: Multi-qubit correlation networks
- **Density Matrix Plots**: Real/imaginary component visualization
- **Histogram Plots**: Measurement outcome distributions
- **Bloch Sphere Trajectories**: 3D qubit state evolution
- **Fubini-Study Distance Plots**: Decoherence tracking over time
- **Error Transition Graphs**: Markov chain visualization

---

## 🔧 Installation & Setup

### **Prerequisites**

- **Python 3.8+**
- **Qiskit 1.3.2+**
- **Scientific computing stack** (NumPy, Matplotlib, SciPy)

### **1️⃣ Virtual Environment Setup**

```bash
python3 -m venv qiskit_env
source qiskit_env/bin/activate  # macOS/Linux
# or
qiskit_env\Scripts\activate     # Windows
```

### **2️⃣ Install Dependencies**

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### **3️⃣ Verify Installation**

```bash
python main.py --help
```

---

## 🚀 Usage

### **Interactive Mode (Recommended)**

```bash
python main.py
```

**Features:**

- Dynamic parameter selection with case-insensitive input
- Real-time visualization with non-blocking plots
- Time-stepped simulations for decoherence analysis
- Comprehensive logging and result saving
- Full rerun and parameter modification support

### **Command-Line Mode**

```bash
# Basic experiment
python main.py --num-qubits 3 --state-type GHZ --noise-type DEPOLARIZING --shots 1024

# Density matrix simulation
python main.py --num-qubits 4 --state-type W --sim-mode density --error-rate 0.05

# Advanced parameters
python main.py --num-qubits 3 --state-type CLUSTER --noise-type THERMAL_RELAXATION --t1 100 --t2 80
```

### **CLI Script Mode**

```bash
python scripts/run_experiment_cli.py --num_qubits 3 --state_type GHZ --noise_type DEPOLARIZING
```

---

## 📊 Available Parameters

### **Core Parameters**

| Parameter      | Description        | Default        | Options                                                                                              |
| -------------- | ------------------ | -------------- | ---------------------------------------------------------------------------------------------------- |
| `--num-qubits` | Number of qubits   | `3`            | `1-10`                                                                                               |
| `--state-type` | Quantum state type | `GHZ`          | `GHZ`, `W`, `CLUSTER`                                                                                |
| `--noise-type` | Noise model        | `DEPOLARIZING` | `DEPOLARIZING`, `PHASE_FLIP`, `AMPLITUDE_DAMPING`, `PHASE_DAMPING`, `THERMAL_RELAXATION`, `BIT_FLIP` |
| `--sim-mode`   | Simulation mode    | `qasm`         | `qasm`, `density`                                                                                    |
| `--shots`      | Number of shots    | `1024`         | `1-10000`                                                                                            |

### **Noise Parameters**

| Parameter      | Description             | Default | Applicable Noise     |
| -------------- | ----------------------- | ------- | -------------------- |
| `--error-rate` | Custom error rate       | `0.1`   | All noise types      |
| `--z-prob`     | Z probability           | `None`  | `PHASE_FLIP`         |
| `--i-prob`     | I probability           | `None`  | `PHASE_FLIP`         |
| `--t1`         | T1 relaxation time (µs) | `100`   | `THERMAL_RELAXATION` |
| `--t2`         | T2 dephasing time (µs)  | `80`    | `THERMAL_RELAXATION` |

### **Visualization Parameters**

| Parameter     | Description               | Default     |
| ------------- | ------------------------- | ----------- |
| `--plot-type` | Visualization type        | `histogram` |
| `--save-plot` | Save plot to file         | `False`     |
| `--show-real` | Show real components      | `False`     |
| `--show-imag` | Show imaginary components | `False`     |

---

## 🔬 Analysis Capabilities

### **Correlation Analysis**

```python
# Pairwise correlations between qubits
correlations = compute_pairwise_correlations(data, num_qubits, mode, shots)

# Conditional correlations for density matrices
conditional_corrs = compute_conditional_correlations(density_matrix, num_qubits)

# Permutation-symmetric correlations
symmetric_corr = compute_permutation_symmetric_correlations(counts, num_qubits, shots)
```

### **Decoherence Analysis**

```python
# Fubini-Study distance between quantum states
distance = compute_fubini_study_distance(rho1, rho2)

# Decoherence rate analysis
analysis = analyze_decoherence_rate(distances, time_steps)
```

### **Symmetry Analysis**

```python
# SU(2) symmetry analysis
su2_analysis = compute_su2_symmetry(counts, num_qubits, shots)

# SU(3) symmetry analysis
su3_value = compute_su3_symmetry(density_matrix, num_qubits)

# Parity distribution
parity = compute_parity_distribution(counts, num_qubits)
```

### **Clustering Analysis**

```python
# Qubit clustering based on correlations
clusters = cluster_qubits(pairwise_corrs, num_qubits, num_clusters=2)

# Optimal clustering analysis
optimal = find_optimal_clusters(pairwise_corrs, num_qubits, max_clusters=5)
```

### **Bloch Sphere Analysis**

```python
# Bloch vector computation
bloch_vector = compute_bloch_vector(rho)

# Bloch trajectories over time
trajectories = compute_bloch_trajectories(density_matrices, num_qubits)

# Bloch evolution analysis
evolution = analyze_bloch_evolution(bloch_trajectories)
```

---

## 📊 Visualization Features

### **Hypergraph Visualization**

- **Multi-qubit correlations**: Visualize entanglement structure
- **Color-coded edges**: Correlation strength visualization
- **Analysis panels**: Real-time statistics and metrics
- **Time evolution**: Track decoherence over time

### **Density Matrix Visualization**

- **Real/imaginary components**: Separate visualization options
- **Color mapping**: Viridis colormap for clarity
- **Component analysis**: Detailed matrix element analysis

### **Bloch Sphere Trajectories**

- **3D visualization**: Interactive 3D Bloch sphere
- **Trajectory tracking**: Qubit state evolution over time
- **Purity analysis**: State purity tracking

### **Error Transition Analysis**

- **Markov chain visualization**: Error transition probabilities
- **State population tracking**: Quantum state populations over time
- **Entropy analysis**: Transition entropy calculations

---

## 📁 Results & Logging

### **Structured Logging**

- **JSON logs**: Structured logging in `logs/structured_logs.json`
- **Console output**: Rich formatted terminal output
- **Experiment tracking**: Unique experiment IDs for all runs

### **Result Storage**

- **JSON results**: Comprehensive experiment results in `results/`
- **Metadata**: Full parameter sets and analysis results
- **Archived experiments**: Historical experiment preservation

### **Analysis Output**

- **Correlation data**: Pairwise and conditional correlations
- **Decoherence metrics**: Fubini-Study distances and rates
- **Symmetry analysis**: SU(2), SU(3), and parity metrics
- **Clustering results**: Qubit grouping and optimal clusters

---

## 🔧 Extending the Framework

### **Adding New Quantum States**

1. Create new state class inheriting from `BaseState`
2. Implement `create()` method
3. Register in `src/state_preparation/state_constants.py`

```python
class CustomState(BaseState):
    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)
        # Custom state preparation logic
        return qc

# Register in state_constants.py
STATE_CLASSES["CUSTOM"] = CustomState
```

### **Adding New Noise Models**

1. Create new noise class inheriting from `BaseNoise`
2. Implement `apply()` method
3. Register in `src/noise_models/noise_factory.py`

```python
class CustomNoise(BaseNoise):
    def apply(self, noise_model: NoiseModel, gate_list: list) -> None:
        # Custom noise application logic
        pass

# Register in noise_factory.py
NOISE_CLASSES["CUSTOM"] = CustomNoise
```

### **Adding New Analysis Methods**

1. Create new analysis module in `src/analysis/`
2. Implement analysis functions
3. Export in `src/analysis/__init__.py`

### **Adding New Visualizations**

1. Create new visualization module in `src/visualization/`
2. Implement plotting functions
3. Register in `src/visualization/visualization_handler.py`

---

## 🧪 Testing

### **Run All Tests**

```bash
python -m pytest src/tests/
```

### **Run Specific Test Categories**

```bash
# State preparation tests
python -m pytest src/tests/test_state_preparation.py

# Noise model tests
python -m pytest src/tests/test_noise_models.py

# Analysis tests
python -m pytest src/tests/test_analysis.py
```

---

## 📚 Research Applications

This framework is designed for **quantum research** and supports:

### **Decoherence Studies**

- **Fubini-Study distance tracking** for quantum state evolution
- **Time-stepped simulations** for decoherence dynamics
- **Multi-noise analysis** for realistic quantum environments

### **Entanglement Analysis**

- **Correlation quantification** for multi-qubit systems
- **Clustering algorithms** for entanglement structure detection
- **Symmetry analysis** for quantum state classification

### **Quantum Error Analysis**

- **Error transition tracking** via Markov chain analysis
- **Bloch sphere trajectories** for single-qubit decoherence
- **Entropy analysis** for quantum information loss

### **Quantum State Engineering**

- **Custom state preparation** for novel quantum states
- **Noise model customization** for realistic quantum systems
- **Parameter optimization** for quantum state control

---

## 🤝 Contributing

### **Development Setup**

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### **Code Style**

- **Type hints**: All functions should have type annotations
- **Docstrings**: Comprehensive documentation for all functions
- **Logging**: Structured logging for all operations
- **Testing**: Unit tests for all new functionality

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Qiskit Team**: For the excellent quantum computing framework
- **Scientific Python Community**: For the robust scientific computing stack
- **Quantum Research Community**: For inspiration and feedback

---

## 📞 Support

For questions, issues, or contributions:

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Check the inline code documentation for detailed usage

---

**Built with ❤️ for quantum research and education**
