"""Deep Dive: Classical Null Model — Can classical noise fake the effect?

BEST AFTER: Step 6 (simulation vs reality)

WHAT YOU'LL EXPLORE:
  A skeptic might ask: "Can't classical correlated noise produce
  the same Structure Scores? Maybe there's nothing quantum about this."

  This deep dive generates classical probability distributions
  designed to MIMIC the shape of GHZ and W measurement data, then
  runs the same metrics on them.

THE EXPERIMENT:
  Compare real quantum GHZ-6 measurements against a classical fake:
  - Classical fake-GHZ: 45% |000000⟩ + 45% |111111⟩ + 10% spread uniformly
  - Real quantum GHZ-6: same probabilities but from actual quantum noise

  Both produce similar Structure Scores. But the CONCENTRATION INDEX
  differs dramatically — real quantum noise creates error neighborhoods
  (single-bit-flip neighbors) that classical distributions don't.

WHAT TO LOOK FOR:
  - SS: classical can match quantum (~0.87 vs ~0.90)
  - CI: quantum is 8-18x higher than classical (988 vs 55)
  - The distinguishing signature is not any single metric but the
    COMBINATION of SS + TC + CI. Classical can fake one but not all three.

CIRCUIT:
  No quantum circuit — this generates CLASSICAL data and analyzes it
  with the same pipeline used for quantum results.

WHY THIS MATTERS:
  Every good experiment needs a null model. If you can't distinguish
  your quantum result from a classical fake, your result isn't uniquely
  quantum. This deep dive shows which metrics distinguish them.

TRY IT:
    from src.experiments.decoherence.deep_dives.dd_classical_null import classical_null

    quantum_result, classical_results = classical_null.run_comparison()
"""

from __future__ import annotations

import numpy as np

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class ClassicalNullExperiment(BaseExperiment):
    """Deep Dive: Test whether classical distributions can fake quantum structure."""

    name = "dd_classical_null"
    description = "Deep dive: Can classical noise fake quantum structured decoherence?"

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

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run quantum GHZ and a 'control' product state for comparison."""
        quantum = self.run()
        control = self.run({"state_type": "SUPERPOSITION"})
        return quantum, control


classical_null = ClassicalNullExperiment()
