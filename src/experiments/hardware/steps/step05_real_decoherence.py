"""Step 5: Real Decoherence — error distributions on real hardware.

WHAT YOU'LL LEARN:
  This is the culmination of the learning journey. You started with
  "what is a qubit?" and now you're measuring how different entangled
  states decohere on a real quantum processor.

  In basics step 11 and the decoherence steps, you compared error
  distributions in simulation. Now the noise is physical, not modeled.

THE EXPERIMENT:
  Run GHZ, W, and Product states at 6 qubits on hardware and compute
  the distribution metrics. Compare Structure Scores.

WHAT TO LOOK FOR:
  - GHZ: counts concentrated around |000000⟩ and |111111⟩
  - W: counts concentrated on the 6 single-excitation states
  - Product: counts spread across all 64 outcomes
  - Compare against your simulation results from the basics and
    decoherence experiments — how well did the noise models predict
    what the hardware actually does?

CIRCUITS:
  GHZ-6:    q0: ─H──●──●──●──●──●── M     (CNOT chain)
  W-6:      [Givens rotation cascade]
  Product:  q0: ─H── M, q1: ─H── M, ...

  Same physical noise. Different states. Different distributions.

WHY THIS MATTERS:
  Hardware runs are the reality check for everything the simulator
  told you. After this step, you have the full pipeline in hand:
  state → noise → measure → analyze — and you can design your own
  hardware experiments.

TRY IT:
    from src.experiments.hardware.steps.step05_real_decoherence import real_decoherence

    results = real_decoherence.run_topology_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class RealDecoherenceExperiment(BaseExperiment):
    """Step 5: Measure decoherence of entangled states on real hardware."""

    name = "hw_05_real_decoherence"
    description = "Step 5: Compare state decoherence on real hardware — the culmination"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            sim_mode="hardware",
            shots=8192,
            optimization_level=1,
            metrics="decoherence",
            visualization_type="histogram",
        )

    def run_topology_comparison(self) -> list[ExperimentResult]:
        """Run GHZ, W, and Product on hardware for comparison."""
        results = []
        for state in ["GHZ", "W", "SUPERPOSITION"]:
            results.append(self.run({"state_type": state}))
        return results


real_decoherence = RealDecoherenceExperiment()
