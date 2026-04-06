"""Experiment Programs Registry.

Experiments are organized into three levels:

  basics/       — Learning experiments for newcomers
  decoherence/  — Core structured decoherence research
  hardware/     — Real quantum hardware experiments

Usage:
    from src.experiments import get_experiment, list_experiments

    # List available experiments
    for name, description in list_experiments():
        print(f"{name}: {description}")

    # Get and run an experiment
    exp = get_experiment("bell_state")
    result = exp.run()

    # Run with config overrides
    result = exp.run({"num_qubits": 3, "error_rate": 0.1})

    # Run parameter sweep
    results = exp.sweep({"error_rate": [0.01, 0.05, 0.1, 0.2]})
"""

from src.experiments.base import BaseExperiment, ExperimentProgram

# Basics — steps (core learning path)
from src.experiments.basics.steps.step01_superposition import superposition
from src.experiments.basics.steps.step02_measurement import measurement
from src.experiments.basics.steps.step03_single_gates import single_gates
from src.experiments.basics.steps.step04_two_qubits import two_qubits
from src.experiments.basics.steps.step05_bell_states import bell_states
from src.experiments.basics.steps.step06_ghz_states import ghz_states
from src.experiments.basics.steps.step07_w_states import w_states
from src.experiments.basics.steps.step08_cluster_states import cluster_states
from src.experiments.basics.steps.step09_noise_intro import noise_intro
from src.experiments.basics.steps.step10_noise_types import noise_types
from src.experiments.basics.steps.step11_noise_and_entanglement import noise_and_entanglement

# Basics — deep dives
from src.experiments.basics.deep_dives.dd_bell_basics import BellExperiment, bell_experiment
from src.experiments.basics.deep_dives.dd_bell_correlations import (
    BellCorrelation,
    BellCorrelationMetrics,
    bell_correlation,
    compute_bell_metrics,
)
from src.experiments.basics.deep_dives.dd_bloch_geometry import bloch_geometry
from src.experiments.basics.deep_dives.dd_density_matrix import density_matrix_mode
from src.experiments.basics.deep_dives.dd_entanglement_fragility import entanglement_fragility
from src.experiments.basics.deep_dives.dd_ghz_structure_metrics import GHZExploration, ghz_exploration
from src.experiments.basics.deep_dives.dd_measurement_basis import measurement_basis
from src.experiments.basics.deep_dives.dd_noise_model_comparison import NoiseComparison, noise_comparison
from src.experiments.basics.deep_dives.dd_structure_scaling import structure_scaling
from src.experiments.basics.deep_dives.dd_teleportation_intro import teleportation_intro

# Advanced — steps
from src.experiments.advanced.steps.step01_quantum_randomness import quantum_randomness
from src.experiments.advanced.steps.step02_deutsch_jozsa import deutsch_jozsa
from src.experiments.advanced.steps.step03_grover_search import grover_search
from src.experiments.advanced.steps.step04_teleportation import teleportation as adv_teleportation
from src.experiments.advanced.steps.step05_superdense_coding import superdense
from src.experiments.advanced.steps.step06_qft import qft
from src.experiments.advanced.steps.step07_error_correction import error_correction
from src.experiments.advanced.steps.step08_design_your_own import design_your_own

# Advanced — deep dives
from src.experiments.advanced.deep_dives.dd_bernstein_vazirani import bernstein_vazirani
from src.experiments.advanced.deep_dives.dd_bb84 import bb84
from src.experiments.advanced.deep_dives.dd_shor import ShorExperiment, shor_experiment
from src.experiments.advanced.deep_dives.dd_grover import GroverExperiment, grover_experiment
from src.experiments.advanced.deep_dives.dd_vqe import VQEExperiment, vqe_experiment
from src.experiments.advanced.deep_dives.dd_qaoa import QAOAExperiment, qaoa_experiment

# Decoherence — steps
from src.experiments.decoherence.steps.step01_river_vs_fog import river_vs_fog
from src.experiments.decoherence.steps.step02_topology_matters import topology_matters
from src.experiments.decoherence.steps.step03_scaling import scaling as dec_scaling
from src.experiments.decoherence.steps.step04_noise_resilience import noise_resilience
from src.experiments.decoherence.steps.step05_global_vs_local import global_vs_local
from src.experiments.decoherence.steps.step06_simulation_vs_reality import sim_vs_reality

# Decoherence — deep dives
from src.experiments.decoherence.deep_dives.dd_classical_null import classical_null
from src.experiments.decoherence.deep_dives.dd_state_probe import (
    StateProbeStudy,
    state_probe_sensitivity,
)

# Hardware — steps
from src.experiments.hardware.steps.step01_first_hardware_run import first_hardware
from src.experiments.hardware.steps.step02_hardware_vs_simulation import hardware_vs_sim
from src.experiments.hardware.steps.step03_transpilation import transpilation as hw_transpilation
from src.experiments.hardware.steps.step04_backend_exploration import backend_exploration
from src.experiments.hardware.steps.step05_real_decoherence import real_decoherence

# Hardware — deep dives
from src.experiments.hardware.deep_dives.dd_readout_errors import readout_errors

# Alias for state probe
state_probe = state_probe_sensitivity

# Registry of available experiments
EXPERIMENT_REGISTRY: dict[str, ExperimentProgram] = {
    # Basics — step-by-step learning progression
    "01_superposition": superposition,
    "02_measurement": measurement,
    "03_single_gates": single_gates,
    "04_two_qubits": two_qubits,
    "05_bell_states": bell_states,
    "06_ghz_states": ghz_states,
    "07_w_states": w_states,
    "08_cluster_states": cluster_states,
    "09_noise_intro": noise_intro,
    "10_noise_types": noise_types,
    "11_noise_and_entanglement": noise_and_entanglement,
    # Basics — deep dives
    "dd_bloch_geometry": bloch_geometry,
    "dd_bell_correlations": bell_correlation,
    "dd_teleportation_intro": teleportation_intro,
    "dd_ghz_structure_metrics": ghz_exploration,
    "dd_entanglement_fragility": entanglement_fragility,
    "dd_measurement_basis": measurement_basis,
    "dd_noise_model_comparison": noise_comparison,
    "dd_density_matrix": density_matrix_mode,
    "dd_structure_scaling": structure_scaling,
    "bell_state": bell_experiment,
    # Advanced steps
    "adv_01_quantum_randomness": quantum_randomness,
    "adv_02_deutsch_jozsa": deutsch_jozsa,
    "adv_03_grover_search": grover_search,
    "adv_04_teleportation": adv_teleportation,
    "adv_05_superdense_coding": superdense,
    "adv_06_qft": qft,
    "adv_07_error_correction": error_correction,
    "adv_08_design_your_own": design_your_own,
    # Advanced deep dives
    "dd_bernstein_vazirani": bernstein_vazirani,
    "dd_bb84": bb84,
    "shor": shor_experiment,
    "grover": grover_experiment,
    "vqe": vqe_experiment,
    "qaoa": qaoa_experiment,
    # Decoherence steps
    "dec_01_river_vs_fog": river_vs_fog,
    "dec_02_topology_matters": topology_matters,
    "dec_03_scaling": dec_scaling,
    "dec_04_noise_resilience": noise_resilience,
    "dec_05_global_vs_local": global_vs_local,
    "dec_06_simulation_vs_reality": sim_vs_reality,
    # Decoherence deep dives
    "dd_classical_null": classical_null,
    "state_probe": state_probe,
    # Hardware steps (require IBM Quantum credentials)
    "hw_01_first_hardware_run": first_hardware,
    "hw_02_hardware_vs_simulation": hardware_vs_sim,
    "hw_03_transpilation": hw_transpilation,
    "hw_04_backend_exploration": backend_exploration,
    "hw_05_real_decoherence": real_decoherence,
    # Hardware deep dives
    "dd_readout_errors": readout_errors,
}


def get_experiment(name: str) -> ExperimentProgram:
    """Get experiment by name.

    Args:
        name: The experiment name (e.g., "bell_state", "topology_comparison")

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
    # Basics
    "BellExperiment",
    "bell_experiment",
    "BellCorrelation",
    "BellCorrelationMetrics",
    "bell_correlation",
    "compute_bell_metrics",
    "GHZExploration",
    "ghz_exploration",
    "NoiseComparison",
    "noise_comparison",
    # Advanced
    "ShorExperiment",
    "shor_experiment",
    "GroverExperiment",
    "grover_experiment",
    "TeleportationExperiment",
    "teleportation_experiment",
    "VQEExperiment",
    "vqe_experiment",
    "QAOAExperiment",
    "qaoa_experiment",
    # Decoherence
    "TopologyComparison",
    "topology_comparison",
    "ScalingLadder",
    "scaling_ladder",
    "NoiseSweep",
    "noise_sweep",
    "StateProbeStudy",
    "state_probe",
]
