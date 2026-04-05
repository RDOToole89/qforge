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
  - Full 6-qubit: KL = 4.4 (high structure)
  - Mean 3-qubit: KL = 1.7
  - Mean 2-qubit: KL = 0.8
  - Mean 1-qubit: KL ≈ 0 (NO local structure!)
  → GHZ structure is PURELY GLOBAL. Individual qubits are 50/50.

  W:
  - Full 6-qubit: KL = 2.3
  - Mean 3-qubit: KL = 1.0
  - Mean 2-qubit: KL = 0.6
  - Mean 1-qubit: KL = 0.3 (LOCAL structure persists!)
  → W structure is LOCAL AND GLOBAL. Each qubit is biased ~80/20.

  The analogy:
  - GHZ = a canyon visible only from satellite. Up close, flat terrain.
  - W = a river delta visible at every zoom level. Even single streams show flow.

CIRCUIT:
  No new circuits — this is ANALYSIS of existing measurement data.
  Run GHZ-6 and W-6 (step 2), then analyze the counts.

WHY THIS MATTERS:
  The global vs local distinction has practical implications:
  - GHZ errors require full-system monitoring to detect
  - W errors are detectable at the individual qubit level
  - This affects error correction strategy choices

TRY IT:
    from src.experiments.decoherence.steps.step05_global_vs_local import global_vs_local

    ghz_result, w_result = global_vs_local.run_both()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class GlobalVsLocalExperiment(BaseExperiment):
    """Step 5: Compare global (GHZ) and local (W) structure."""

    name = "dec_05_global_vs_local"
    description = "Step 5: Global vs local — where does the structure live?"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            shots=8192,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="structured_decoherence",
        )

    def run_both(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run GHZ-6 and W-6 for marginal comparison."""
        ghz = self.run()
        w = self.run({"state_type": "W"})
        return ghz, w


global_vs_local = GlobalVsLocalExperiment()
