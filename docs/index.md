# QForge

A general-purpose quantum experiment framework built on Qiskit — for learning, tinkering, and running real experiments.

## Overview

QForge abstracts away the plumbing of quantum experimentation. You pick a quantum state, choose a noise model, configure a simulation mode (or point it at real IBM Quantum hardware), and hit run. The framework handles circuit construction, noise application, execution, measurement canonicalization, and analysis — all through a clean two-function API (`run()` and `sweep()`).

## Key Features

- **State preparation**: GHZ, W, Bell, Cluster, Superposition, and custom circuits
- **Noise models**: 8 physics-based noise channels (depolarizing, amplitude/phase damping, bit/phase flip, thermal relaxation, correlated depolarizing, readout error)
- **Simulation modes**: `qasm` (shot-based), `statevector` (exact), `density_matrix` (mixed state), `hardware` (IBM Quantum)
- **Analysis metrics**: 8 information-theoretic metrics with bootstrap 95% confidence intervals
- **Parameter sweeps**: Multi-dimensional sweeps over any configuration field
- **Provenance**: Git SHA, software versions, host info, and full reproducibility tracking
- **Schema output**: Versioned, standardized result format for programmatic analysis

## Analysis Metrics

All metrics are general-purpose information-theoretic and statistical measures over measurement outcome distributions:

### Distribution Structure

- **Asymmetry Index**: Total variation distance from the uniform distribution (full 2^n support)
- **Structure Score**: Jensen-Shannon divergence from the factorized (independent-marginals) null model
- **Concentration Index**: ratio of probability mass in the most-likely vs least-likely quartile of outcomes
- **Pathway Concentration Ratio**: Probability mass in top vs bottom outcome quartiles

### Correlation & Stability

- **Entanglement-Error Correlation**: Pearson correlation between an entanglement topology matrix and the pairwise mutual-information matrix
- **Temporal Pathway Stability**: Spearman rank correlation of outcome orderings across conditions
- **Complexity Emergence Score**: Logistic fit locating a threshold in a metric-vs-size curve

### Information Theory

- **Total Correlation**: Multi-information across all qubits

## Quick Start

**Using the CLI:**

```bash
# List available experiments
uv run python -m src.cli list

# Run an experiment
uv run python -m src.cli run 01_superposition

# With custom parameters
uv run python -m src.cli run 01_superposition -s error_rate=0.1 -s num_qubits=3
```

See [CLI Reference](reference/cli.md) for full documentation.

**Using the Engine API:**

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    shots=1024,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    metrics="decoherence",
)

result = run(config)
for name, entry in result.metrics_bundle.metrics.items():
    print(f"{name}: {entry.value:.4f}")
```

See the [Quick Start](guides/getting-started/quickstart.md) for more usage examples.

## Use Cases

- **Learning quantum mechanics**: Preset experiments with step-by-step explanations, from superposition to entanglement
- **Noise characterization**: Compare noise channels and their effect on different entangled states
- **Entanglement studies**: See how different topologies (GHZ, W, Cluster) respond to noise
- **Hardware experiments**: Run the same experiments on real IBM Quantum processors with full provenance

## Architecture

The framework follows an **engine-first architecture** with clean separation:

- **Engine API**: Clean entry points via `run()` and `sweep()` functions
- **Core Logic**: Quantum mechanics implementation and analysis algorithms
- **Analysis Framework**: Information-theoretic metrics and statistical methods
- **Schema System**: Standardized data formats for reproducible experiments

See [Architecture](architecture/architecture.md) for the detailed design.

## Documentation Structure

- **[CLI Reference](reference/cli.md)**: Command-line tool usage and examples
- **Getting Started**: [Installation](guides/getting-started/installation.md) and [Quick Start](guides/getting-started/quickstart.md)
- **API Reference**: [Metrics](guides/api/metrics.md) and [Constants](guides/api/constants.md)
- **[Hardware Setup](guides/hardware-setup.md)**: Running on IBM Quantum
- **[Architecture](architecture/architecture.md)**: System design and integration patterns

## Getting Started

Continue to the [Installation Guide](guides/getting-started/installation.md) to set up the framework, or jump to the [Quick Start](guides/getting-started/quickstart.md) for immediate usage examples.
