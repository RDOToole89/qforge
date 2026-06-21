"""Step 2: Measurement — Probability and collapse.

WHAT YOU'LL LEARN:
  When you measure a qubit, the superposition collapses. The outcome
  is random, but the PROBABILITIES are determined by the quantum state.
  Run enough measurements ("shots") and the statistics converge to the
  true probabilities.

THE EXPERIMENT:
  We prepare a qubit rotated to different angles on the Bloch sphere
  using the Ry gate. Ry(theta) rotates the qubit from |0⟩ toward |1⟩:
  - Ry(0)    = |0⟩      → P(0) = 100%, P(1) = 0%
  - Ry(π/4)  = tilted   → P(0) ≈ 85%, P(1) ≈ 15%
  - Ry(π/2)  = |+⟩      → P(0) = 50%, P(1) = 50%
  - Ry(3π/4) = tilted   → P(0) ≈ 15%, P(1) ≈ 85%
  - Ry(π)    = |1⟩      → P(0) = 0%, P(1) = 100%

  The probability of measuring |1⟩ is sin²(theta/2).

WHAT TO LOOK FOR:
  - The measured fractions should match the predicted probabilities
  - More shots = better agreement (try 100 vs 10000)
  - This is the Born rule: P(outcome) = |⟨outcome|state⟩|²

CIRCUIT:
  q: ─Ry(θ)─ M ───

TRY IT:
    from src.experiments.basics.step02_measurement import measurement

    # Sweep rotation angles
    results = measurement.run_angle_sweep()
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class MeasurementExperiment(BaseExperiment):
    """Step 2: Explore measurement probability with rotation angles."""

    name = "02_measurement"
    description = "Step 2: How measurement probability depends on quantum state angle"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        qc = QuantumCircuit(1, 1)
        qc.ry(np.pi / 2, 0)  # |+⟩ state
        qc.measure(0, 0)
        return ExperimentConfig(
            num_qubits=1,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": qc},
        )

    def run_angle_sweep(self, steps: int = 9) -> list[ExperimentResult]:
        """Sweep Ry angle from 0 to pi and observe probability change."""
        angles = np.linspace(0, np.pi, steps).tolist()
        results = []
        for theta in angles:
            qc = QuantumCircuit(1, 1)
            qc.ry(theta, 0)
            qc.measure(0, 0)
            r = self.run(
                {
                    "custom_params": {"source": "circuit", "circuit": qc},
                }
            )
            results.append(r)
        return results


measurement = MeasurementExperiment()
