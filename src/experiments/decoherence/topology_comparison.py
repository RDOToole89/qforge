"""Topology Comparison — Do different entanglement types decohere differently?

This is the foundational structured decoherence experiment. It tests four
quantum states with different entanglement topologies under the same noise
and compares their decoherence structure.

States tested:
  - GHZ: All-to-all correlation → "Correlated River"
  - W: Symmetric excitation sharing → "Distributed River"
  - Cluster: Nearest-neighbor graph state → "Fog" (on current hardware)
  - Product: No entanglement → "Fog" (negative control)

Key finding (on IBM hardware):
  GHZ and W show 12x higher Structure Score than Cluster and Product,
  demonstrating that entanglement topology determines decoherence structure.

Usage:
    from src.experiments.decoherence import topology_comparison

    # Run all four states
    results = topology_comparison.run_all_states()

    # Run a single state
    result = topology_comparison.run({"state_type": "W"})
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class TopologyComparison(BaseExperiment):
    """Compare decoherence structure across entanglement topologies.

    Runs GHZ, W, Cluster, and Product states at 6 qubits to test
    whether entanglement topology determines the shape of decoherence.
    """

    name = "topology_comparison"
    description = "Compare decoherence structure across GHZ, W, Cluster, and Product states"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=8192,
            metrics="structured_decoherence",
        )

    def run_all_states(self) -> list[ExperimentResult]:
        """Run all four topologies for comparison."""
        return self.sweep(
            parameter_ranges={
                "state_type": ["GHZ", "W", "CLUSTER", "SUPERPOSITION"],
            },
        )


topology_comparison = TopologyComparison()
