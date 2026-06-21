"""Step 6: Simulation vs Reality — Where do our models break down?

WHAT YOU'LL LEARN:
  Steps 1-5 ran in simulation. But simulation uses mathematical noise
  models (depolarizing, amplitude damping) that are simplifications of
  real hardware physics. How well do they match?

  This step runs the topology comparison (step 2) in BOTH simulation
  and matches it against hardware data (if available) or prepares you
  to run it on hardware (hardware/ steps).

THE EXPERIMENT:
  Run GHZ-6 and W-6 with depolarizing noise (2%), then with amplitude
  damping (2%), and compare the Structure Scores.

WHAT TO LOOK FOR:
  - Depolarizing: symmetric noise. Over-predicts GHZ structure (sim SS ~0.89
    vs hardware SS ~0.75-0.80). The model is too "clean."
  - Amplitude damping: directional noise (|1⟩→|0⟩). Better match for W
    (sim SS ~0.76 vs hardware SS ~0.73). Models the real T1 relaxation.
  - Different topologies need different noise models to predict accurately
  - This IS the research frontier: finding which models best capture reality

CIRCUIT:
  Same GHZ-6 and W-6 circuits as step 2.
  What changes is the noise model applied by the engine.

WHY THIS MATTERS:
  Understanding simulation accuracy is essential before claiming any
  result is "real physics." This step teaches you to be skeptical of
  your own simulations — the right mindset for research.

  After this step, you're ready for hardware/ steps to see the real thing.

TRY IT:
    from src.experiments.decoherence.steps.step06_simulation_vs_reality import sim_vs_reality

    depol_results, amp_results = sim_vs_reality.run_noise_model_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class SimVsRealityExperiment(BaseExperiment):
    """Step 6: Compare depolarizing and amplitude damping predictions."""

    name = "dec_06_simulation_vs_reality"
    description = "Step 6: Simulation vs reality — where do noise models break down?"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            shots=8192,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.02,
            rng_seed=42,
            metrics="structured_decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_noise_model_comparison(self) -> tuple[list[ExperimentResult], list[ExperimentResult]]:
        """Run GHZ and W under both depolarizing and amplitude damping."""
        depol = []
        amp = []
        for state in ["GHZ", "W"]:
            depol.append(self.run({"state_type": state, "noise_type": "depolarizing"}))
            amp.append(self.run({"state_type": state, "noise_type": "amplitude_damping"}))
        return depol, amp


sim_vs_reality = SimVsRealityExperiment()
