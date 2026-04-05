"""Structured decoherence research experiments.

These experiments investigate how entanglement topology determines
the structure of decoherence pathways in quantum systems.

Progression:
  1. topology_comparison — Compare GHZ, W, Cluster, Product at 6 qubits.
     The foundational experiment: does entanglement type matter?

  2. scaling_ladder — GHZ and W from 2 to 8 qubits.
     Does structure grow with system size? How?

  3. noise_sweep — Structure Score vs noise rate.
     How robust is the structure? Does it degrade smoothly or collapse?

  4. state_probe — 47-condition sensitivity study.
     Which states detect correlated noise topologies best?
"""

from src.experiments.decoherence.noise_sweep import NoiseSweep, noise_sweep
from src.experiments.decoherence.scaling_ladder import ScalingLadder, scaling_ladder
from src.experiments.decoherence.state_probe import (
    StateProbeStudy,
    state_probe_sensitivity as state_probe,
)
from src.experiments.decoherence.topology_comparison import (
    TopologyComparison,
    topology_comparison,
)

__all__ = [
    "TopologyComparison",
    "topology_comparison",
    "ScalingLadder",
    "scaling_ladder",
    "NoiseSweep",
    "noise_sweep",
    "StateProbeStudy",
    "state_probe",
]
