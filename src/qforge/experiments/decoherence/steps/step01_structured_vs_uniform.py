"""Step 1: Structured vs Uniform — how entanglement shapes error distributions.

WHAT YOU'LL LEARN:
  When a quantum state decoheres, how are the measurement errors
  distributed? We compare two states under identical noise:
  - GHZ: maximally entangled (all-to-all correlation)
  - Product (Superposition): no entanglement at all

  The ideal GHZ-4 distribution has support on just 2 of 16 outcomes
  (|0000⟩ and |1111⟩); the ideal product state spreads probability over
  all 16 outcomes equally. Under moderate noise, the measured
  distributions inherit these shapes: GHZ stays concentrated near its
  two peaks (with bit-flip neighbors picking up the leaked probability),
  while the product state stays close to uniform.

THE EXPERIMENT:
  Run GHZ-4 and Product-4 with depolarizing noise at 5%.
  Compute the Structure Score (Jensen-Shannon divergence from a
  factorized null model) for each.

WHAT TO LOOK FOR:
  - GHZ: high Structure Score — probability concentrates in |0000⟩ and
    |1111⟩ plus their single-bit-flip neighbors.
  - Product: Structure Score near zero — all 16 outcomes roughly
    equally likely.

CIRCUIT:
  GHZ-4:                          Product-4:
  q0: ─H──●──●──●── [noise] M    q0: ─H── [noise] M
  q1: ────X──┼──┼── [noise] M    q1: ─H── [noise] M
  q2: ───────X──┼── [noise] M    q2: ─H── [noise] M
  q3: ──────────X── [noise] M    q3: ─H── [noise] M

  Same noise model. Same error rate. Different entanglement. Different structure.

TRY IT:
    from qforge.experiments.decoherence.steps.step01_structured_vs_uniform import (
        structured_vs_uniform,
    )

    ghz, product = structured_vs_uniform.run_comparison()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class StructuredVsUniformExperiment(BaseExperiment):
    """Step 1: Compare error distributions of entangled vs product states."""

    name = "dec_01_structured_vs_uniform"
    description = "Step 1: Structured vs uniform — errors with and without entanglement"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run GHZ (concentrated) and Product (near-uniform) for comparison."""
        ghz = self.run()
        product = self.run({"state_type": "SUPERPOSITION"})
        return ghz, product


structured_vs_uniform = StructuredVsUniformExperiment()
