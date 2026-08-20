"""Topology Comparison — do different entanglement types decohere differently?

Runs four quantum states with different entanglement topologies under the
same noise and compares the shapes of their measured distributions.

States tested:
  - GHZ: all-to-all correlation (ideal distribution: 2 peaks)
  - W: symmetric excitation sharing (ideal distribution: N peaks)
  - Cluster: nearest-neighbor graph state (ideal Z-basis distribution: uniform)
  - Product: no entanglement (ideal distribution: uniform; negative control)

Usage:
    from qforge.experiments.decoherence import topology_comparison

    # Run all four states
    results = topology_comparison.run_all_states()

    # Run a single state
    result = topology_comparison.run({"state_type": "W"})
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class TopologyComparison(BaseExperiment):
    """Compare measured distribution shape across entanglement topologies.

    Runs GHZ, W, Cluster, and Product states at 6 qubits under the same
    noise and compares their distribution metrics.
    """

    name = "topology_comparison"
    description = "Compare decoherence structure across GHZ, W, Cluster, and Product states"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=8192,
            metrics="decoherence",
            visualization_type="all",
        )

    def run_all_states(self) -> list[ExperimentResult]:
        """Run all four topologies for comparison."""
        return self.sweep(
            parameter_ranges={
                "state_type": ["GHZ", "W", "CLUSTER", "SUPERPOSITION"],
            },
        )


topology_comparison = TopologyComparison()
