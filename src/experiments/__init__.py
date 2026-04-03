"""Experiment Programs Registry.

This module provides a registry of available experiment programs.
Each experiment implements the ExperimentProgram protocol.

Usage:
    from src.experiments import get_experiment, list_experiments

    # List available experiments
    for name, description in list_experiments():
        print(f"{name}: {description}")

    # Get and run an experiment
    exp = get_experiment("sst_q1")
    result = exp.run()

    # Run with config overrides
    result = exp.run({"num_qubits": 3, "error_rate": 0.1})

    # Run parameter sweep
    results = exp.sweep({"error_rate": [0.01, 0.05, 0.1]})
"""

from src.experiments.base import BaseExperiment, ExperimentProgram
from src.experiments.bell_correlation import (
    BellCorrelation,
    BellCorrelationMetrics,
    bell_correlation,
    compute_bell_metrics,
)
from src.experiments.sst_hypothesis_q1 import SSTHypothesisQ1, sst_q1
from src.experiments.sst_hypothesis_q1_cluster import (
    SSTHypothesisQ1Cluster,
    sst_q1_cluster,
)
from src.experiments.sst_hypothesis_q1_extensions import (
    SSTHypothesisQ1Huge,
    SSTHypothesisQ1LargeDepolarizing,
    sst_q1_huge,
    sst_q1_large_depolarizing,
)
from src.experiments.sst_hypothesis_q1_large import (
    SSTHypothesisQ1Large,
    sst_q1_large,
)
from src.experiments.sst_hypothesis_q1_large_points import (
    SSTHypothesisQ1LargeHighNoise,
    SSTHypothesisQ1LargeMaxNoise,
    sst_q1_large_high_noise,
    sst_q1_large_max_noise,
)
from src.experiments.sst_hypothesis_q1_states import (
    SSTHypothesisQ1ProductState,
    SSTHypothesisQ1WState,
    sst_q1_product,
    sst_q1_w,
)
from src.experiments.sst_hypothesis_q1_structured import (
    SSTHypothesisQ1Structured,
    sst_q1_structured,
)
from src.experiments.state_probe_sensitivity import (
    StateProbeStudy,
    state_probe_sensitivity,
)

# Registry of available experiments
EXPERIMENT_REGISTRY: dict[str, ExperimentProgram] = {
    # SST experiments (structured decoherence research)
    "sst_q1": sst_q1,
    "sst_q1_structured": sst_q1_structured,
    "sst_q1_large": sst_q1_large,
    "sst_q1_large_high_noise": sst_q1_large_high_noise,
    "sst_q1_large_max_noise": sst_q1_large_max_noise,
    "sst_q1_w": sst_q1_w,
    "sst_q1_product": sst_q1_product,
    "sst_q1_cluster": sst_q1_cluster,
    "sst_q1_large_depolarizing": sst_q1_large_depolarizing,
    "sst_q1_huge": sst_q1_huge,
    # Bell experiments (quantum correlation tests)
    "bell_correlation": bell_correlation,
    # State probe sensitivity study (NTC-based noise characterisation)
    "state_probe_sensitivity": state_probe_sensitivity,
}


def get_experiment(name: str) -> ExperimentProgram:
    """Get experiment by name.

    Args:
        name: The experiment name (e.g., "sst_q1")

    Returns:
        The experiment instance

    Raises:
        KeyError: If experiment name not found
    """
    if name not in EXPERIMENT_REGISTRY:
        available = ", ".join(EXPERIMENT_REGISTRY.keys())
        raise KeyError(f"Unknown experiment: {name}. Available: {available}")
    return EXPERIMENT_REGISTRY[name]


def list_experiments() -> list[tuple[str, str]]:
    """List all available experiments.

    Returns:
        List of (name, description) tuples
    """
    return [(name, exp.description) for name, exp in EXPERIMENT_REGISTRY.items()]


__all__ = [
    # Core abstractions
    "ExperimentProgram",
    "BaseExperiment",
    # Registry access
    "EXPERIMENT_REGISTRY",
    "get_experiment",
    "list_experiments",
    # SST experiments
    "SSTHypothesisQ1",
    "SSTHypothesisQ1Structured",
    "SSTHypothesisQ1Large",
    "SSTHypothesisQ1LargeHighNoise",
    "SSTHypothesisQ1LargeMaxNoise",
    "sst_q1",
    "sst_q1_structured",
    "sst_q1_large",
    "sst_q1_large_high_noise",
    "sst_q1_large_max_noise",
    "SSTHypothesisQ1WState",
    "SSTHypothesisQ1ProductState",
    "SSTHypothesisQ1Cluster",
    "SSTHypothesisQ1LargeDepolarizing",
    "SSTHypothesisQ1Huge",
    "sst_q1_w",
    "sst_q1_product",
    "sst_q1_cluster",
    "sst_q1_large_depolarizing",
    "sst_q1_huge",
    # Bell experiments
    "BellCorrelation",
    "BellCorrelationMetrics",
    "bell_correlation",
    "compute_bell_metrics",
    # State probe sensitivity
    "StateProbeStudy",
    "state_probe_sensitivity",
]
