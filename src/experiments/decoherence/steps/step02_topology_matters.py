"""Step 2: Topology Matters — Four entanglement types, four behaviors.

WHAT YOU'LL LEARN:
  Step 1 showed River (GHZ) vs Fog (Product). But entanglement isn't
  binary — there are many TYPES of entanglement, each with a different
  topology. Does the topology determine the structure?

  We test four fundamentally different states:
  - GHZ: all-to-all correlation → "Correlated River" (2 peaks)
  - W: symmetric excitation sharing → "Distributed River" (N peaks)
  - Cluster: nearest-neighbor graph → "Fog" (uniform, despite entanglement!)
  - Product: no entanglement → "Fog" (uniform, as expected)

THE EXPERIMENT:
  Run all four at 6 qubits with amplitude damping noise.
  Compare Structure Score, Total Correlation, and Concentration Index.

WHAT TO LOOK FOR:
  - GHZ and W BOTH show high SS (>0.7) but with different TC
  - Cluster shows SS ≈ 0.05 — indistinguishable from Product!
  - This means entanglement is NECESSARY but NOT SUFFICIENT for structure
  - The entanglement TOPOLOGY determines whether structure survives

  The W state surprise: higher SS than GHZ despite a 2x deeper circuit.
  Structure comes from the state, not from circuit depth.

CIRCUIT:
  GHZ:     q0: ─H──●──●──●──●──●── M    (all-to-all via CNOT chain)
  W:       [Givens rotation cascade]      (symmetric excitation sharing)
  Cluster: q0: ─H──■─── ... ──── M       (nearest-neighbor CZ)
  Product: q0: ─H── M                    (independent, no entanglement)

TRY IT:
    from src.experiments.decoherence.steps.step02_topology_matters import topology_matters

    results = topology_matters.run_all_topologies()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class TopologyMattersExperiment(BaseExperiment):
    """Step 2: Compare four entanglement topologies under the same noise."""

    name = "dec_02_topology_matters"
    description = "Step 2: Four topologies, four behaviors — entanglement type determines structure"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            shots=8192,
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            rng_seed=42,
            metrics="structured_decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_all_topologies(self) -> list[ExperimentResult]:
        """Run GHZ, W, Cluster, and Product at 6 qubits."""
        return self.sweep(
            parameter_ranges={"state_type": ["GHZ", "W", "CLUSTER", "SUPERPOSITION"]},
        )


topology_matters = TopologyMattersExperiment()
