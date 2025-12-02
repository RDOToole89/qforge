"""
Experiment Programs Registry

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
from src.experiments.sst_hypothesis_q1 import SSTHypothesisQ1, sst_q1
from src.experiments.sst_hypothesis_q1_structured import (
    SSTHypothesisQ1Structured,
    sst_q1_structured,
)

# Registry of available experiments
EXPERIMENT_REGISTRY: dict[str, ExperimentProgram] = {
    "sst_q1": sst_q1,
    "sst_q1_structured": sst_q1_structured,
}


def get_experiment(name: str) -> ExperimentProgram:
    """
    Get experiment by name.

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
    """
    List all available experiments.

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
    # Individual experiments
    "SSTHypothesisQ1",
    "SSTHypothesisQ1Structured",
    # Convenience instances
    "sst_q1",
    "sst_q1_structured",
]
