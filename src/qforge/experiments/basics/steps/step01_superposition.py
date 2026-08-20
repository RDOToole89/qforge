"""Step 1: Superposition — What IS a qubit?

WHAT YOU'LL LEARN:
  A classical bit is either 0 or 1. A qubit can be BOTH at the same time.
  This is called superposition. When you measure a qubit in superposition,
  it "collapses" to either 0 or 1 with some probability.

THE EXPERIMENT:
  We prepare a single qubit in three different states:
  - |0⟩ : always measures 0 (no superposition)
  - |1⟩ : always measures 1 (no superposition)
  - |+⟩ : equal superposition — measures 0 or 1 with 50/50 chance

  The |+⟩ state is created by applying a Hadamard gate (H) to |0⟩.
  The H gate is the "superposition gate" — it puts a qubit into
  an equal mix of 0 and 1.

WHAT TO LOOK FOR:
  - |0⟩ gives 100% "0" outcomes
  - |1⟩ gives 100% "1" outcomes
  - |+⟩ gives ~50% "0" and ~50% "1" (not exactly 50/50 due to randomness)

  This randomness is NOT measurement error. It's fundamental quantum
  mechanics — the qubit genuinely doesn't have a definite value until
  you measure it.

CIRCUIT:
  |0⟩ state:   q: ─── M ───     (do nothing, just measure)
  |1⟩ state:   q: ─X─ M ───     (X gate flips 0→1)
  |+⟩ state:   q: ─H─ M ───     (H gate creates superposition)

CIRCUITS:
  |0⟩ state:  q: ─── M ───        (just measure, always get 0)
  |1⟩ state:  q: ─X─ M ───        (X gate flips to 1, always get 1)
  |+⟩ state:  q: ─H─ M ───        (H gate creates superposition, 50/50)

TRY IT:
    from qforge import get_experiment

    exp = get_experiment("01_superposition")
    result = exp.run()              # default: |+⟩  (~50/50)
    results = exp.run_all_states()  # |0⟩, |1⟩, and |+⟩
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class SuperpositionExperiment(BaseExperiment):
    """Step 1: Explore superposition with a single qubit."""

    name = "01_superposition"
    description = (
        "Step 1: Superposition — measure |+⟩ (~50/50). Use run_all_states() for |0⟩/|1⟩/|+⟩"
    )
    metrics_hint = (
        "Asymmetry Index near 0 means the histogram looks like a fair coin. "
        "|0⟩ or |1⟩ would be near 1."
    )
    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=1,
            state_type="SUPERPOSITION",
            shots=1024,
            noise_enabled=False,
            metrics=["asymmetry_index"],
        )

    def run_all_states(self) -> list[ExperimentResult]:
        """Run |0⟩, |1⟩, and |+⟩ to compare outcomes."""
        from qiskit import QuantumCircuit

        results = []

        # |0⟩ — do nothing
        qc0 = QuantumCircuit(1, 1)
        qc0.measure(0, 0)
        results.append(
            self.run(
                {
                    "state_type": "CUSTOM",
                    "custom_params": {"source": "circuit", "circuit": qc0},
                }
            )
        )

        # |1⟩ — apply X gate
        qc1 = QuantumCircuit(1, 1)
        qc1.x(0)
        qc1.measure(0, 0)
        results.append(
            self.run(
                {
                    "state_type": "CUSTOM",
                    "custom_params": {"source": "circuit", "circuit": qc1},
                }
            )
        )

        # |+⟩ — apply H gate (superposition)
        qcH = QuantumCircuit(1, 1)
        qcH.h(0)
        qcH.measure(0, 0)
        results.append(
            self.run(
                {
                    "state_type": "CUSTOM",
                    "custom_params": {"source": "circuit", "circuit": qcH},
                }
            )
        )

        return results


superposition = SuperpositionExperiment()
