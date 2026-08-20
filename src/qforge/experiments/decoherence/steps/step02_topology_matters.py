"""Step 2: Topology Matters — Four entanglement types, four distributions.

WHAT YOU'LL LEARN:
  Step 1 compared GHZ against a product state. But entanglement isn't
  binary — different entangled states have different structure, and
  their ideal Z-basis distributions look very different:
  - GHZ: probability on 2 outcomes (|00...0⟩ and |11...1⟩)
  - W: probability on the N single-excitation outcomes
  - Cluster: uniform over all outcomes (despite being entangled!)
  - Product: uniform over all outcomes (no entanglement)

THE EXPERIMENT:
  Run all four at 6 qubits with amplitude damping noise.
  Compare Structure Score, Total Correlation, and Concentration Index.

WHAT TO LOOK FOR:
  - GHZ and W both keep concentrated distributions under noise
    (high Structure Score), but with different Total Correlation.
  - Cluster's Z-basis counts look like the product state's — a reminder
    that these metrics describe the measured distribution, not the
    amount of entanglement. Entanglement that is invisible in the
    Z basis is invisible to these metrics.

CIRCUIT:
  GHZ:     q0: ─H──●──●──●──●──●── M    (all-to-all via CNOT chain)
  W:       [Givens rotation cascade]      (symmetric excitation sharing)
  Cluster: q0: ─H──■─── ... ──── M       (nearest-neighbor CZ)
  Product: q0: ─H── M                    (independent, no entanglement)

TRY IT:
    from qforge.experiments.decoherence.steps.step02_topology_matters import topology_matters

    results = topology_matters.run_all_topologies()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class TopologyMattersExperiment(BaseExperiment):
    """Step 2: Compare four entanglement topologies under the same noise."""

    name = "dec_02_topology_matters"
    description = "Step 2: Four entanglement topologies compared under identical noise"

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
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_all_topologies(self) -> list[ExperimentResult]:
        """Run GHZ, W, Cluster, and Product at 6 qubits."""
        return self.sweep(
            parameter_ranges={"state_type": ["GHZ", "W", "CLUSTER", "SUPERPOSITION"]},
        )


topology_matters = TopologyMattersExperiment()
