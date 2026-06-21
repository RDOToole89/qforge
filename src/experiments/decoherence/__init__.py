"""Structured decoherence research experiments.

This is the author's primary research interest: investigating how
entanglement topology determines the structure of decoherence pathways.

Organized into two parts:

  steps/       — 6-step guided research progression
  deep_dives/  — Full research experiments and validation
"""

# Steps
# Deep dives
from src.experiments.decoherence.deep_dives.dd_classical_null import classical_null
from src.experiments.decoherence.deep_dives.dd_state_probe import (
    StateProbeStudy,
    state_probe_sensitivity,
)
from src.experiments.decoherence.steps.step01_river_vs_fog import river_vs_fog
from src.experiments.decoherence.steps.step02_topology_matters import topology_matters
from src.experiments.decoherence.steps.step03_scaling import scaling
from src.experiments.decoherence.steps.step04_noise_resilience import noise_resilience
from src.experiments.decoherence.steps.step05_global_vs_local import global_vs_local
from src.experiments.decoherence.steps.step06_simulation_vs_reality import sim_vs_reality

state_probe = state_probe_sensitivity

__all__ = [
    "river_vs_fog",
    "topology_matters",
    "scaling",
    "noise_resilience",
    "global_vs_local",
    "sim_vs_reality",
    "classical_null",
    "StateProbeStudy",
    "state_probe",
]
