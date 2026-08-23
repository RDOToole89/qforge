"""Noise and entanglement experiments.

These experiments study how the choice of entangled state, noise model,
and system size shapes measured outcome distributions.

Organized into two parts:

  steps/       — 6-step guided progression
  deep_dives/  — Larger sweep-based studies
"""

# Steps
# Deep dives
from qforge.experiments.decoherence.deep_dives.dd_classical_null import classical_null
from qforge.experiments.decoherence.deep_dives.dd_state_probe import (
    StateProbeStudy,
    state_probe_sensitivity,
)
from qforge.experiments.decoherence.steps.step01_structured_vs_uniform import structured_vs_uniform
from qforge.experiments.decoherence.steps.step02_topology_matters import topology_matters
from qforge.experiments.decoherence.steps.step03_scaling import scaling
from qforge.experiments.decoherence.steps.step04_noise_resilience import noise_resilience
from qforge.experiments.decoherence.steps.step05_global_vs_local import global_vs_local
from qforge.experiments.decoherence.steps.step06_simulation_vs_reality import sim_vs_reality

state_probe = state_probe_sensitivity

__all__ = [
    "structured_vs_uniform",
    "topology_matters",
    "scaling",
    "noise_resilience",
    "global_vs_local",
    "sim_vs_reality",
    "classical_null",
    "StateProbeStudy",
    "state_probe",
]
