# src/quantum_experiment/__init__.py

"""
Quantum Experiment Framework

This package provides:
- **State preparation**: GHZ, W, CLUSTER states with entanglement control.
- **Noise modeling**: Depolarizing, phase flip, thermal relaxation, bit flip, etc.
- **Quantum execution**: Configurable simulation with Qiskit Aer.
- **Visualization tools**: Histograms, density matrices, hypergraph mapping.
- **Utilities**: Logging, input validation, experiment configuration.

Designed for modular quantum experiments, extensibility, and research integration.

🔹 Core Features:
- Supports hypergraph correlation analysis and structured decoherence studies.
- Provides CLI and interactive execution modes.
- Modular architecture for adding new noise models, states, and research tools.
"""

from .core.state_preparation import prepare_state
from .core.noise_models import create_noise_model
from .core.experiment_runner import run_experiment
# Lazy import for visualization components
def get_visualizer():
    from .visualization.visualizer import Visualizer
    return Visualizer
from .config.settings import settings  # Application settings

# Expose key functions and classes for easier package imports
__all__ = [
    "prepare_state",
    "create_noise_model",
    "run_experiment",
    "get_visualizer",
    "settings",
]
