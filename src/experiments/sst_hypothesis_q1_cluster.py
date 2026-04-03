"""SST Hypothesis Q1 (Cluster State).

This experiment tests the "River Scaling" hypothesis on a Cluster State (Graph State).
Cluster states have a linear nearest-neighbor entanglement topology (1D chain),
unlike the all-to-all topology of GHZ states.

Hypothesis:
If the "River" effect is driven by the specific topology of the state,
the Cluster state should show a different PCR and EEC signature than GHZ.
We expect moderate EEC (errors following the linear chain) but lower PCR than GHZ.
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig
from src.experiments.base import BaseExperiment


class SSTHypothesisQ1Cluster(BaseExperiment):
    """SST Hypothesis Q1 with Linear Cluster State.

    Cluster states are created by applying Hadamard gates to all qubits
    and then CZ gates between nearest neighbors. They are the resource
    states for measurement-based quantum computing.

    Topology: Linear Chain (0-1-2-3-4-5)
    """

    name = "sst_q1_cluster"
    description = "SST Q1 with Linear Cluster state (1D graph state)"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for Cluster state experiment."""
        return ExperimentConfig(
            num_qubits=6,  # Match the "large" GHZ experiment size
            state_type="CLUSTER",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=8192,
            metrics="structured_decoherence",
        )


# Module-level instance
sst_q1_cluster = SSTHypothesisQ1Cluster()
