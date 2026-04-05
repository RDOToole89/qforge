"""Step 1: River vs Fog — The foundational observation.

WHAT YOU'LL LEARN:
  This is the experiment that started the whole research direction.
  The question: when an entangled quantum state decoheres, do errors
  spread UNIFORMLY (like fog) or follow STRUCTURED PATHWAYS (like a river)?

  We test this by comparing two states under the same noise:
  - GHZ: maximally entangled (all-to-all correlation)
  - Product (Superposition): no entanglement at all

  If errors are random, both should look similar. If entanglement
  creates structure, they should look very different.

THE EXPERIMENT:
  Run GHZ-4 and Product-4 with depolarizing noise at 5%.
  Compute Structure Score (SS) for each.

WHAT TO LOOK FOR:
  - GHZ: SS ≈ 0.7-0.9 — probability concentrates in |0000⟩ and |1111⟩
    with single-bit-flip errors as "tributaries." This is the RIVER.
  - Product: SS ≈ 0.05 — all 16 outcomes roughly equally likely.
    This is the FOG.
  - The separation is ~12x. Not subtle.

  The river exists because entanglement CONSTRAINS which error transitions
  are quantum-mechanically accessible. GHZ can only reach nearby states
  through single-qubit flips. Product has no such constraint.

CIRCUIT:
  GHZ-4:                          Product-4:
  q0: ─H──●──●──●── [noise] M    q0: ─H── [noise] M
  q1: ────X──┼──┼── [noise] M    q1: ─H── [noise] M
  q2: ───────X──┼── [noise] M    q2: ─H── [noise] M
  q3: ──────────X── [noise] M    q3: ─H── [noise] M

  Same noise model. Same error rate. Different entanglement. Different structure.

TRY IT:
    from src.experiments.decoherence.steps.step01_river_vs_fog import river_vs_fog

    ghz, product = river_vs_fog.run_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class RiverVsFogExperiment(BaseExperiment):
    """Step 1: The foundational River vs Fog observation."""

    name = "dec_01_river_vs_fog"
    description = "Step 1: River vs Fog — do errors follow structured pathways?"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="structured_decoherence",
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run GHZ (river) and Product (fog) for comparison."""
        ghz = self.run()
        product = self.run({"state_type": "SUPERPOSITION"})
        return ghz, product


river_vs_fog = RiverVsFogExperiment()
