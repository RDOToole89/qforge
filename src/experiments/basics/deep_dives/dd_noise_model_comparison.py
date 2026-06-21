"""Deep Dive: Noise Model Comparison — Same state, different noise.

What you'll learn:
  - Depolarizing noise: random Pauli errors (X, Y, Z equally likely)
  - Amplitude damping: energy relaxation (|1⟩ → |0⟩, models T1 decay)
  - How the same quantum state responds differently to each noise type

This experiment reveals that decoherence is not just "how much noise"
but "what kind of noise." Different noise channels create different
error patterns on the same entangled state.

Try it:
    from src.experiments.basics.noise_comparison import noise_comparison

    # Compare depolarizing vs amplitude damping on GHZ-4
    results = noise_comparison.CIRCUIT (same GHZ-4 for both noise models):
  q0: ─H──●──●──●── [NOISE] ── M
  q1: ────X──┼──┼── [NOISE] ── M
  q2: ───────X──┼── [NOISE] ── M
  q3: ──────────X── [NOISE] ── M

  Same circuit, different noise: depolarizing vs amplitude damping.
  Compare the error patterns side by side.

run_comparison()
    for r in results:
        params = r.analysis.experiment_parameters
        ss = r.metrics_bundle.metrics["structure_score"].value
        print(f"{params['noise_type']}: SS = {ss:.3f}")

WHAT YOU'LL EXPLORE:
  - How depolarizing (random) and amplitude damping (directional) noise
    produce different error patterns on the same GHZ state
  - Why the same quantum state responds differently to each noise type
  - The connection between noise physics and error structure

TRY IT:
    from src.experiments.basics.deep_dives.dd_noise_model_comparison import noise_comparison

    results = noise_comparison.run_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class NoiseComparison(BaseExperiment):
    """Compare noise models on the same quantum state.

    Runs GHZ-4 under depolarizing and amplitude damping noise
    to show how noise type affects error structure.
    """

    name = "noise_comparison"
    description = "Compare depolarizing vs amplitude damping on the same state"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=4096,
            metrics="structured_decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_comparison(self) -> list[ExperimentResult]:
        """Run GHZ-4 under both depolarizing and amplitude damping."""
        return self.sweep(
            parameter_ranges={
                "noise_type": ["depolarizing", "amplitude_damping"],
            },
        )


noise_comparison = NoiseComparison()
