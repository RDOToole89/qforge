"""Step 11: Noise + Entanglement — How noise shapes error patterns.

WHAT YOU'LL LEARN:
  Different quantum states produce very differently shaped measurement
  distributions under the same noise. A state whose ideal distribution
  is concentrated (like GHZ) stays concentrated under moderate noise; a
  state whose ideal distribution is uniform (like a product of |+⟩
  states) stays close to uniform.

THE EXPERIMENT:
  Apply the same depolarizing noise to four different states:
  - GHZ: all-to-all entanglement
  - W: symmetric excitation
  - Cluster: nearest-neighbor
  - Product (Superposition): no entanglement

  Then look at the structure metrics — especially Structure Score
  (Jensen-Shannon divergence from a factorized null model).

WHAT TO LOOK FOR:
  - GHZ: high Structure Score. Counts concentrate in |000...0⟩ and
    |111...1⟩ and their single-bit-flip neighbors.
  - W: high Structure Score. Counts concentrate in the N
    single-excitation states.
  - Cluster: low Structure Score. In the Z basis, the ideal cluster
    state distribution is uniform, so counts stay spread out.
  - Product: low Structure Score. Counts stay near-uniform.

  Note that a low Structure Score does not mean "no entanglement" —
  the cluster state is entangled but its Z-basis distribution is
  uniform. The metric measures the shape of the measured distribution,
  nothing more.

CIRCUITS (four different states, same noise):
  GHZ:          q0: ─H──●──●──●── M      (all-to-all entanglement)
  W:            Complex Givens cascade     (symmetric excitation)
  Cluster:      q0: ─H──■─ ... ── M      (nearest-neighbor CZ)
  Superposition: q0: ─H── M               (no entanglement)

  All run with depolarizing noise at 5%. Compare the metrics!

TRY IT:
    from qforge.experiments.basics.step11_noise_and_entanglement import noise_and_entanglement

    results = noise_and_entanglement.run_all_topologies()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class NoiseAndEntanglementExperiment(BaseExperiment):
    """Step 11: See how different entanglement topologies shape noise patterns."""

    name = "11_noise_and_entanglement"
    description = "Step 11: How entanglement changes the shape of error distributions"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_all_topologies(self) -> list[ExperimentResult]:
        """Compare four entanglement topologies under the same noise."""
        return self.sweep(
            parameter_ranges={
                "state_type": ["GHZ", "W", "CLUSTER", "SUPERPOSITION"],
            },
        )


noise_and_entanglement = NoiseAndEntanglementExperiment()
