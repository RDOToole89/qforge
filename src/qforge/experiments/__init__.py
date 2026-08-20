"""Experiment Programs Registry.

Experiments are organized into three levels:

  basics/       — Learning experiments for newcomers
  advanced/     — Classic quantum algorithms
  decoherence/  — Noise and entanglement studies
  hardware/     — Real quantum hardware experiments

Usage:
    from qforge.experiments import get_experiment, list_experiments, register_experiment

    # List available experiments
    for name, description in list_experiments():
        print(f"{name}: {description}")

    # Get and run an experiment
    exp = get_experiment("01_superposition")
    result = exp.run()

    # Out-of-tree: register without editing this module
    register_experiment(MyExperiment())

    # Run with config overrides
    result = exp.run({"num_qubits": 3, "error_rate": 0.1})

    # Run parameter sweep
    results = exp.sweep({"error_rate": [0.01, 0.05, 0.1, 0.2]})
"""

from __future__ import annotations

import logging
from importlib.metadata import entry_points

from qforge.experiments.advanced.deep_dives.dd_bb84 import bb84

# Advanced — deep dives
from qforge.experiments.advanced.deep_dives.dd_bernstein_vazirani import bernstein_vazirani
from qforge.experiments.advanced.deep_dives.dd_grover import GroverExperiment, grover_experiment
from qforge.experiments.advanced.deep_dives.dd_qaoa import QAOAExperiment, qaoa_experiment
from qforge.experiments.advanced.deep_dives.dd_shor import ShorExperiment, shor_experiment
from qforge.experiments.advanced.deep_dives.dd_vqe import VQEExperiment, vqe_experiment

# Advanced — steps
from qforge.experiments.advanced.steps.step01_quantum_randomness import quantum_randomness
from qforge.experiments.advanced.steps.step02_deutsch_jozsa import deutsch_jozsa
from qforge.experiments.advanced.steps.step03_grover_search import grover_search
from qforge.experiments.advanced.steps.step04_teleportation import (
    teleportation as adv_teleportation,
)
from qforge.experiments.advanced.steps.step05_superdense_coding import superdense
from qforge.experiments.advanced.steps.step06_qft import qft
from qforge.experiments.advanced.steps.step07_error_correction import error_correction
from qforge.experiments.advanced.steps.step08_design_your_own import design_your_own
from qforge.experiments.base import BaseExperiment, ExperimentProgram

# Basics — deep dives
from qforge.experiments.basics.deep_dives.dd_bell_basics import BellExperiment, bell_experiment
from qforge.experiments.basics.deep_dives.dd_bell_correlations import (
    BellCorrelation,
    BellCorrelationMetrics,
    bell_correlation,
    compute_bell_metrics,
)
from qforge.experiments.basics.deep_dives.dd_bloch_geometry import bloch_geometry
from qforge.experiments.basics.deep_dives.dd_density_matrix import density_matrix_mode
from qforge.experiments.basics.deep_dives.dd_entanglement_fragility import entanglement_fragility
from qforge.experiments.basics.deep_dives.dd_ghz_structure_metrics import (
    GHZExploration,
    ghz_exploration,
)
from qforge.experiments.basics.deep_dives.dd_measurement_basis import measurement_basis
from qforge.experiments.basics.deep_dives.dd_noise_model_comparison import (
    NoiseComparison,
    noise_comparison,
)
from qforge.experiments.basics.deep_dives.dd_structure_scaling import structure_scaling
from qforge.experiments.basics.deep_dives.dd_teleportation_intro import teleportation_intro

# Basics — steps (core learning path)
from qforge.experiments.basics.steps.step01_superposition import superposition
from qforge.experiments.basics.steps.step02_measurement import measurement
from qforge.experiments.basics.steps.step03_single_gates import single_gates
from qforge.experiments.basics.steps.step04_two_qubits import two_qubits
from qforge.experiments.basics.steps.step05_bell_states import bell_states
from qforge.experiments.basics.steps.step06_ghz_states import ghz_states
from qforge.experiments.basics.steps.step07_w_states import w_states
from qforge.experiments.basics.steps.step08_cluster_states import cluster_states
from qforge.experiments.basics.steps.step09_noise_intro import noise_intro
from qforge.experiments.basics.steps.step10_noise_types import noise_types
from qforge.experiments.basics.steps.step11_noise_and_entanglement import noise_and_entanglement

# Decoherence — deep dives
from qforge.experiments.decoherence.deep_dives.dd_classical_null import classical_null
from qforge.experiments.decoherence.deep_dives.dd_state_probe import (
    StateProbeStudy,
    state_probe_sensitivity,
)

# Decoherence — steps
from qforge.experiments.decoherence.steps.step01_structured_vs_uniform import structured_vs_uniform
from qforge.experiments.decoherence.steps.step02_topology_matters import topology_matters
from qforge.experiments.decoherence.steps.step03_scaling import scaling as dec_scaling
from qforge.experiments.decoherence.steps.step04_noise_resilience import noise_resilience
from qforge.experiments.decoherence.steps.step05_global_vs_local import global_vs_local
from qforge.experiments.decoherence.steps.step06_simulation_vs_reality import sim_vs_reality

# Hardware — deep dives
from qforge.experiments.hardware.deep_dives.dd_readout_errors import readout_errors

# Hardware — steps
from qforge.experiments.hardware.steps.step01_first_hardware_run import first_hardware
from qforge.experiments.hardware.steps.step02_hardware_vs_simulation import hardware_vs_sim
from qforge.experiments.hardware.steps.step03_transpilation import transpilation as hw_transpilation
from qforge.experiments.hardware.steps.step04_backend_exploration import backend_exploration
from qforge.experiments.hardware.steps.step05_real_decoherence import real_decoherence

# Alias for state probe
state_probe = state_probe_sensitivity

logger = logging.getLogger(__name__)

EXPERIMENT_ENTRY_POINT_GROUP = "qforge.experiments"
_ENTRY_POINTS_LOADED = False

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
    "dec_01_structured_vs_uniform": structured_vs_uniform,
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


def register_experiment(
    experiment: ExperimentProgram,
    *,
    name: str | None = None,
    replace: bool = False,
) -> None:
    """Register an experiment program on the live registry.

    Call this from a user module or third-party package. ``qforge list``,
    ``qforge run``, and ``get_experiment`` resolve against this table. In-tree
    teaching tracks still belong in ``EXPERIMENT_REGISTRY`` above; this is the
    path that does not require editing this file.

    Args:
        experiment: Instance implementing ``ExperimentProgram``.
        name: Registry key. Defaults to ``experiment.name``.
        replace: If True, overwrite an existing experiment of the same name.

    Raises:
        TypeError: If ``experiment`` does not implement ``ExperimentProgram``.
        ValueError: If the resolved name is empty.
        KeyError: If ``name`` is already registered and ``replace`` is False.
    """
    if not isinstance(experiment, ExperimentProgram):
        raise TypeError(
            "register_experiment() expects an ExperimentProgram instance "
            "(subclass BaseExperiment or implement the protocol)."
        )
    key = (name if name is not None else experiment.name).strip()
    if not key:
        raise ValueError("Experiment name must be a non-empty string")
    if key in EXPERIMENT_REGISTRY and not replace:
        raise KeyError(f"Experiment '{key}' is already registered. Pass replace=True to overwrite.")
    EXPERIMENT_REGISTRY[key] = experiment


def unregister_experiment(name: str) -> None:
    """Remove an experiment. Intended for tests and plugin teardown."""
    EXPERIMENT_REGISTRY.pop(name, None)


def load_experiment_entry_points(*, force: bool = False) -> int:
    """Load ``qforge.experiments`` setuptools entry points. Idempotent.

    Each entry point may be an ``ExperimentProgram`` instance or a zero-arg
    callable that calls ``register_experiment``. This is discovery, not a
    plugin framework: failed entries are logged and skipped.

    Args:
        force: Reload even if this process already loaded the group.

    Returns:
        Number of entry points that loaded without error.
    """
    global _ENTRY_POINTS_LOADED
    if _ENTRY_POINTS_LOADED and not force:
        return 0
    _ENTRY_POINTS_LOADED = True
    loaded = 0
    try:
        discovered = entry_points().select(group=EXPERIMENT_ENTRY_POINT_GROUP)
    except Exception:  # pragma: no cover - metadata API edge on odd installs
        logger.warning("Could not read experiment entry points", exc_info=True)
        return 0
    for ep in discovered:
        try:
            obj = ep.load()
            if isinstance(obj, ExperimentProgram):
                try:
                    register_experiment(obj)
                except KeyError:
                    logger.info(
                        "Entry point %s skipped; experiment already registered",
                        ep.name,
                    )
                    continue
            elif callable(obj):
                obj()
            else:
                raise TypeError(
                    f"Entry point {ep.name!r} must be an ExperimentProgram "
                    "instance or a zero-arg callable"
                )
        except Exception:
            logger.warning("Failed to load experiment entry point %s", ep.name, exc_info=True)
            continue
        loaded += 1
    return loaded


def get_experiment(name: str) -> ExperimentProgram:
    """Get experiment by name.

    Args:
        name: The experiment name (e.g., "01_superposition", "dec_01_structured_vs_uniform")

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
    "register_experiment",
    "unregister_experiment",
    "load_experiment_entry_points",
    "EXPERIMENT_ENTRY_POINT_GROUP",
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

load_experiment_entry_points()
