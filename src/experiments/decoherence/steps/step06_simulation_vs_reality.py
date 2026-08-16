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
  - Depolarizing noise is symmetric: it mixes in errors uniformly.
  - Amplitude damping is directional (|1⟩→|0⟩), modeling T1 relaxation.
  - The two models give different Structure Scores for the same state,
    because they redistribute probability differently.
  - Real hardware combines several physical error mechanisms, so no
    single textbook model matches it exactly.

CIRCUIT:
  Same GHZ-6 and W-6 circuits as step 2.
  What changes is the noise model applied by the engine.

WHY THIS MATTERS:
  Simulated noise models are simplifications. Comparing models against
  each other (and later against hardware in the hardware/ steps) shows
  where those simplifications matter — a healthy dose of skepticism
  about simulation results.

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
            metrics="decoherence",
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
