"""Step 5: Global vs Local Structure — Where does the structure live?

WHAT YOU'LL LEARN:
  Steps 1-4 measured structure at the FULL system level. But where
  does the structure actually LIVE? Is it in individual qubits
  (local) or only in the correlations between them (global)?

  This step performs MARGINAL ANALYSIS: trace out qubits and see
  what structure remains at each level (1-qubit, 2-qubit, 3-qubit...).

THE EXPERIMENT:
  Take the GHZ-6 and W-6 measurement data (from step 2 or 3) and
  compute KL divergence from uniform at each marginal level.

WHAT TO LOOK FOR:
  GHZ:
  - The ideal single-qubit marginals are exactly 50/50, so the 1-qubit
    KL divergence from uniform is ≈ 0 even though the full 6-qubit
    distribution is far from uniform. The deviation from uniform lives
    entirely in the correlations.

  W:
  - Each ideal single-qubit marginal is biased (P(1) = 1/N), so some
    deviation from uniform is visible even at the 1-qubit level, and
    more appears at each higher marginal level.

CIRCUIT:
  No new circuits — this is ANALYSIS of existing measurement data.
  Run GHZ-6 and W-6 (step 2), then analyze the counts.

WHY THIS MATTERS:
  It shows, concretely, the difference between a distribution whose
  deviation from uniform is visible in single-qubit marginals and one
  where it only appears in multi-qubit correlations.

TRY IT:
    from qforge.experiments.decoherence.steps.step05_global_vs_local import global_vs_local

    ghz_result, w_result = global_vs_local.run_both()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class GlobalVsLocalExperiment(BaseExperiment):
    """Step 5: Compare global (GHZ) and local (W) structure."""

    name = "dec_05_global_vs_local"
    description = "Step 5: Marginal analysis — correlations vs single-qubit statistics"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            shots=8192,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_both(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run GHZ-6 and W-6 for marginal comparison."""
        ghz = self.run()
        w = self.run({"state_type": "W"})
        return ghz, w


global_vs_local = GlobalVsLocalExperiment()
