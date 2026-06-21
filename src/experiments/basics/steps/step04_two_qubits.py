"""Step 4: Two Qubits — Independent vs entangled.

WHAT YOU'LL LEARN:
  Two qubits can be independent (product state) or entangled.
  Independent qubits: measuring one tells you nothing about the other.
  Entangled qubits: measuring one instantly determines the other.

THE EXPERIMENT:
  We compare two scenarios:

  1. INDEPENDENT: H on both qubits (no entangling gate)
     Each qubit is in |+⟩ independently.
     All four outcomes (00, 01, 10, 11) are equally likely at 25%.

  2. ENTANGLED: H on qubit 0, then CNOT(0→1)
     This creates a Bell state: (|00⟩ + |11⟩)/√2.
     Only 00 and 11 appear (~50% each). Never 01 or 10.

WHAT TO LOOK FOR:
  - Independent: all four outcomes at ~25%
  - Entangled: only 00 and 11 at ~50% each
  - The CNOT gate is what creates the entanglement

WHY THIS MATTERS:
  Entanglement is the key resource that makes quantum computers
  powerful. Two entangled qubits share information in a way that
  has no classical analogue. Einstein called it "spooky action at
  a distance" — but it's just how quantum mechanics works.

CIRCUIT:
  Independent:  q0: ─H─── M     Entangled:  q0: ─H──●── M
                q1: ─H─── M                 q1: ────X── M

CIRCUITS:
  Independent:                  Entangled (Bell state):
  q0: ─H───── M ───            q0: ─H──●── M ───
  q1: ─H───── M ───            q1: ────X── M ───

  Independent: 25% each of 00, 01, 10, 11
  Entangled:   50% each of 00 and 11 only

TRY IT:
    from src.experiments.basics.step04_two_qubits import two_qubits

    # Compare independent vs entangled
    independent, entangled = two_qubits.run_comparison()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class TwoQubitsExperiment(BaseExperiment):
    """Step 4: Compare independent and entangled two-qubit states."""

    name = "04_two_qubits"
    description = "Step 4: Independent vs entangled — see how CNOT creates correlations"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        # Default: Bell state (entangled)
        return ExperimentConfig(
            num_qubits=2,
            state_type="GHZ",
            shots=4096,
            noise_enabled=False,
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run both independent and entangled, return (independent, entangled)."""
        # Independent: H on both, no CNOT
        qc_indep = QuantumCircuit(2, 2)
        qc_indep.h(0)
        qc_indep.h(1)
        qc_indep.measure([0, 1], [0, 1])
        independent = self.run(
            {
                "state_type": "CUSTOM",
                "custom_params": {"source": "circuit", "circuit": qc_indep},
            }
        )

        # Entangled: H + CNOT (Bell state)
        entangled = self.run()  # default is GHZ-2 = Bell

        return independent, entangled


two_qubits = TwoQubitsExperiment()
