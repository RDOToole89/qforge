"""Step 10: Noise Types — Not all noise is the same.

WHAT YOU'LL LEARN:
  Different physical processes cause different types of quantum noise.
  Each noise type has a distinctive "fingerprint" in the measurement
  data. Understanding noise types is essential for error correction.

THE NOISE MODELS:
  1. Depolarizing: Random Pauli errors (X, Y, Z equally likely).
     The "generic" noise model. Like shaking a snow globe —
     everything gets scrambled uniformly.

  2. Amplitude Damping: Energy relaxation (|1⟩ → |0⟩).
     Models T1 decay in real hardware. Like a ball rolling downhill —
     the qubit relaxes to its ground state. DIRECTIONAL noise.

  3. Phase Damping: Pure dephasing (phase information lost).
     Models T2* processes. The qubit stays at the same energy
     but loses track of its phase. Like a spinning top wobbling.

  4. Bit Flip: Random X errors only.
     |0⟩ ↔ |1⟩ with some probability. Classical-like noise.

  5. Phase Flip: Random Z errors only.
     Phase gets randomly inverted. Invisible in Z-basis
     but destructive for superpositions.

THE EXPERIMENT:
  Apply each noise type to a GHZ-4 state at the same error rate
  and compare the measurement distributions.

WHAT TO LOOK FOR:
  - Depolarizing: errors spread uniformly across all outcomes
  - Amplitude damping: errors biased toward |0000⟩ (energy loss)
  - Phase damping: errors in specific pattern (phase-sensitive)
  - Bit flip: symmetric errors (0↔1 equally likely)
  - Phase flip: looks similar to depolarizing in Z-basis

  The KEY insight: the same quantum state responds DIFFERENTLY
  to each noise type. This is why noise characterization matters.

CIRCUIT (same for all noise types):
  q0: ─H──●──●──●── [NOISE] ── M
  q1: ────X──┼──┼── [NOISE] ── M
  q2: ───────X──┼── [NOISE] ── M
  q3: ──────────X── [NOISE] ── M

  Same GHZ-4 state, different noise channels applied by the engine.
  The circuit is identical — only the noise model changes.

TRY IT:
    from qforge.experiments.basics.step10_noise_types import noise_types

    results = noise_types.run_all_types()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class NoiseTypesExperiment(BaseExperiment):
    """Step 10: Compare five noise models on the same quantum state."""

    name = "10_noise_types"
    description = (
        "Step 10: Compare depolarizing, amplitude damping, phase damping, bit flip, phase flip"
    )

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_all_types(self) -> list[ExperimentResult]:
        """Run GHZ-4 under five different noise models."""
        noise_models = [
            "depolarizing",
            "amplitude_damping",
            "phase_damping",
            "bit_flip",
            "phase_flip",
        ]
        return self.sweep(parameter_ranges={"noise_type": noise_models})


noise_types = NoiseTypesExperiment()
