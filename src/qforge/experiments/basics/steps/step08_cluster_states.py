"""Step 8: Cluster States — Nearest-neighbor entanglement.

WHAT YOU'LL LEARN:
  Not all entanglement is the same. Cluster states entangle only
  NEIGHBORING qubits in a chain, creating a "graph state."

  - GHZ: all qubits connected to all others (all-to-all)
  - W: one excitation shared across all (symmetric)
  - Cluster: each qubit connected only to its neighbors (local)

  Cluster states are the resource for "measurement-based quantum
  computation" — a completely different model of quantum computing
  where you compute by measuring qubits one at a time.

THE EXPERIMENT:
  Prepare a 6-qubit Cluster state and compare its measurement
  distribution with GHZ and Superposition (product state).

WHAT TO LOOK FOR:
  - Cluster looks surprisingly UNIFORM — all 64 outcomes roughly equal
  - This is because Cluster's entanglement is "hidden" in Z-basis
  - GHZ shows 2 peaks; W shows 6 peaks; Cluster shows 64 equal peaks
  - Yet Cluster IS genuinely entangled (in a different way)

  This teaches an important lesson: entanglement doesn't always
  mean concentrated measurement outcomes. It depends on the
  measurement basis and the entanglement topology.

CIRCUIT (4-qubit Cluster):
  q0: ─H──■────────── M
  q1: ─H──■──■─────── M
  q2: ─H─────■──■──── M
  q3: ─H────────■──── M

  H on all qubits, then CZ between neighbors.
  CZ = controlled-Z (phase gate, not bit flip).
  Creates nearest-neighbor entanglement only.

TRY IT:
    from qforge.experiments.basics.step08_cluster_states import cluster_states

    ghz, cluster, product = cluster_states.run_comparison()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class ClusterStatesExperiment(BaseExperiment):
    """Step 8: Cluster states and the surprise of hidden entanglement."""

    name = "08_cluster_states"
    description = "Step 8: Cluster states — entangled but 'invisible' in Z-basis measurement"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="CLUSTER",
            shots=4096,
            noise_enabled=False,
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult, ExperimentResult]:
        """Compare GHZ, Cluster, and Product at 6 qubits."""
        ghz = self.run({"state_type": "GHZ"})
        cluster = self.run({"state_type": "CLUSTER"})
        product = self.run({"state_type": "SUPERPOSITION"})
        return ghz, cluster, product


cluster_states = ClusterStatesExperiment()
