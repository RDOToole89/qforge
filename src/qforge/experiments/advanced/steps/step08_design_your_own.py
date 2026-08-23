"""Step 8: Design Your Own Experiment — Putting it all together.

WHAT YOU'LL LEARN:
  You've now learned:
  - Quantum superpowers (parallelism, search) — Steps 1-3
  - Entanglement as a resource (teleportation, superdense) — Steps 4-5
  - Key subroutines (QFT, error correction) — Steps 6-7

  Now it's time to design YOUR OWN quantum experiment. This step
  walks you through the framework's experiment design pattern and
  shows you how to create a hypothesis, configure an experiment,
  run it, and analyze the results.

THE FRAMEWORK PATTERN:
  Every experiment in this framework follows the same structure:

  1. HYPOTHESIS: What do you expect to happen?
     "GHZ states should show higher structure than product states under noise"

  2. CONFIGURATION: Set up the experiment parameters
     State type, qubit count, noise model, shots, metrics

  3. EXECUTION: Run the experiment (simulation or hardware)
     result = run(config)

  4. ANALYSIS: Inspect the results
     Counts, fidelity, structure metrics, provenance

  5. COMPARISON: Run multiple configs and compare
     sweep() over parameter ranges

THE EXPERIMENT:
  This step IS the experiment. It's a template that you modify.
  The default runs a simple hypothesis test: "Does GHZ show more
  structure than SUPERPOSITION under depolarizing noise?"

  Modify the hypothesis, change the configs, add your own sweeps.
  When you're comfortable, create your own file in decoherence/
  or a new folder entirely.

HOW TO CREATE YOUR OWN:
  1. Copy this file as a starting point
  2. Change the class name, hypothesis, and configs
  3. Add convenience methods (run_my_sweep, run_comparison, etc.)
  4. Register in __init__.py
  5. Run via CLI: qforge run my_experiment

TRY IT:
    from qforge.experiments.advanced.steps.step08_design_your_own import design_your_own

    # Run the template hypothesis
    structured, control = design_your_own.run_hypothesis_test()

    # Or modify it
    result = design_your_own.run({"state_type": "W", "num_qubits": 5})
"""

from __future__ import annotations

from typing import Any

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class DesignYourOwnExperiment(BaseExperiment):
    """Step 8: Template for designing your own quantum experiment.

    MODIFY THIS. Change the hypothesis, configs, and sweep parameters
    to investigate whatever interests you.

    Current hypothesis:
      "GHZ states show more structured error distributions than product states
       under depolarizing noise at 5% error rate."
    """

    name = "adv_08_design_your_own"
    description = "Step 8: Design your own experiment — a template to build on"
    metrics_hint = (
        "Start with Structure Score. Add more metrics when you know what "
        "question they answer."
    )
    def default_config(self) -> ExperimentConfig:
        """YOUR DEFAULT CONFIG — modify this."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics=["structure_score"],
            visualization_type=["histogram", "circuit"],
        )

    def run_hypothesis_test(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run the structured state and the control state.

        MODIFY THIS to test your own hypothesis.
        The pattern: run the "interesting" config, run the "control",
        then compare the metrics.
        """
        # The hypothesis: GHZ shows structure
        structured = self.run()

        # The control: product state shows no structure
        control = self.run(
            {
                "state_type": "SUPERPOSITION",
            }
        )

        return structured, control

    def run_parameter_exploration(self, **overrides: Any) -> list[ExperimentResult]:
        """Sweep a parameter to explore its effect.

        MODIFY THIS to sweep whatever parameter interests you.

        Examples:
          - error_rate: how does noise affect your metric?
          - num_qubits: how does system size affect your metric?
          - noise_type: which noise model is most interesting?
        """
        return self.sweep(
            parameter_ranges={
                "error_rate": [0.01, 0.02, 0.05, 0.10, 0.20],
            },
            **overrides,
        )


design_your_own = DesignYourOwnExperiment()
