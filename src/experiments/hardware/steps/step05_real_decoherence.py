"""Step 5: Real Decoherence — See structured pathways on real hardware.

WHAT YOU'LL LEARN:
  This is the culmination of the entire learning journey. You started
  with "what is a qubit?" and now you're observing structured decoherence
  on a real quantum processor.

  In basics step 11, you saw River vs Fog in simulation. Now you'll
  see it on REAL HARDWARE. The question: does the River effect persist
  when the noise is physical, not modeled?

THE EXPERIMENT:
  Run GHZ, W, and Product states at 6 qubits on hardware with
  structured decoherence metrics. Compare Structure Scores.

WHAT TO LOOK FOR:
  - GHZ: SS ≈ 0.7-0.9 (River — concentrated in |000000⟩ and |111111⟩)
  - W:   SS ≈ 0.7-0.8 (Distributed River — spread across 6 single-excitation states)
  - Product: SS ≈ 0.05 (Fog — uniform across all 64 outcomes)
  - The 12x separation between GHZ and Product is the key finding
  - Compare with your simulation results from basics/decoherence experiments

CIRCUITS:
  GHZ-6:    q0: ─H──●──●──●──●──●── M     (depth 24 after transpilation)
  W-6:      [Givens rotation cascade]       (depth 52 after transpilation)
  Product:  q0: ─H── M, q1: ─H── M, ...   (depth 4 after transpilation)

  Same noise (physical). Different states. Different structure.

WHY THIS MATTERS:
  Real hardware confirmation of structured decoherence is what turns
  a simulation finding into an empirical result. This is the bridge
  from "interesting simulation" to "real physics."

  After this step, you have all the tools to design your own hardware
  experiments. You understand the full pipeline: state → noise → measure →
  analyze → interpret. You're ready for independent research.

TRY IT:
    from src.experiments.hardware.steps.step05_real_decoherence import real_decoherence

    results = real_decoherence.run_topology_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class RealDecoherenceExperiment(BaseExperiment):
    """Step 5: Observe structured decoherence on real quantum hardware."""

    name = "hw_05_real_decoherence"
    description = "Step 5: River vs Fog on real hardware — the culmination of your journey"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            sim_mode="hardware",
            shots=8192,
            optimization_level=1,
            metrics="structured_decoherence",
            visualization_type="histogram",
        )

    def run_topology_comparison(self) -> list[ExperimentResult]:
        """Run GHZ, W, and Product on hardware for comparison."""
        results = []
        for state in ["GHZ", "W", "SUPERPOSITION"]:
            results.append(self.run({"state_type": state}))
        return results


real_decoherence = RealDecoherenceExperiment()
