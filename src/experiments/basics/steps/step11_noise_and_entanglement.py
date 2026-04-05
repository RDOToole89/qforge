"""Step 11: Noise + Entanglement — How noise shapes error patterns.

WHAT YOU'LL LEARN:
  This is where things get interesting. When noise hits an ENTANGLED
  state, the errors don't spread randomly. They follow patterns
  determined by the entanglement topology.

  This is the "River vs Fog" phenomenon:
  - FOG: errors spread uniformly (product/unentangled states)
  - RIVER: errors flow along specific pathways (entangled states)

THE EXPERIMENT:
  Apply the same depolarizing noise to four different states:
  - GHZ: all-to-all entanglement
  - W: symmetric excitation
  - Cluster: nearest-neighbor
  - Product (Superposition): no entanglement

  Then look at the structure metrics — especially Structure Score.

WHAT TO LOOK FOR:
  - GHZ: high Structure Score (~0.7-0.9). Errors concentrate in
    |000...0⟩ and |111...1⟩ and their single-bit-flip neighbors.
  - W: high Structure Score (~0.7-0.8). Errors concentrate in
    the N single-excitation states.
  - Cluster: low Structure Score (~0.05). Errors spread uniformly.
  - Product: low Structure Score (~0.05). Errors spread uniformly.

  The 12x difference between GHZ and Product is the "River vs Fog"
  separation. Entanglement topology determines error structure.

WHY THIS MATTERS:
  If errors follow predictable patterns, error correction can be
  TARGETED at those patterns instead of defending against everything.
  This is the core idea behind structured decoherence research.

CIRCUITS (four different states, same noise):
  GHZ:          q0: ─H──●──●──●── M      (all-to-all entanglement)
  W:            Complex Givens cascade     (symmetric excitation)
  Cluster:      q0: ─H──■─ ... ── M      (nearest-neighbor CZ)
  Superposition: q0: ─H── M               (no entanglement)

  All run with depolarizing noise at 5%. Compare the metrics!

TRY IT:
    from src.experiments.basics.step11_noise_and_entanglement import noise_and_entanglement

    results = noise_and_entanglement.run_all_topologies()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class NoiseAndEntanglementExperiment(BaseExperiment):
    """Step 11: See how different entanglement topologies shape noise patterns."""

    name = "11_noise_and_entanglement"
    description = "Step 11: River vs Fog — how entanglement shapes decoherence patterns"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            metrics="structured_decoherence",
        )

    def run_all_topologies(self) -> list[ExperimentResult]:
        """Compare four entanglement topologies under the same noise."""
        return self.sweep(
            parameter_ranges={
                "state_type": ["GHZ", "W", "CLUSTER", "SUPERPOSITION"],
            },
        )


noise_and_entanglement = NoiseAndEntanglementExperiment()
