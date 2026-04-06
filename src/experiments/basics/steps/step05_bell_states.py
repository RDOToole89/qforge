"""Step 5: Bell States — The four maximally entangled pairs.

WHAT YOU'LL LEARN:
  There are exactly four maximally entangled two-qubit states,
  called Bell states. They form a complete basis for two-qubit
  entanglement and are the foundation for teleportation,
  superdense coding, and quantum key distribution.

THE FOUR BELL STATES:
  |Φ+⟩ = (|00⟩ + |11⟩)/√2  — "both same, positive phase"
  |Φ−⟩ = (|00⟩ − |11⟩)/√2  — "both same, negative phase"
  |Ψ+⟩ = (|01⟩ + |10⟩)/√2  — "both different, positive phase"
  |Ψ−⟩ = (|01⟩ − |10⟩)/√2  — "both different, negative phase"

THE EXPERIMENT:
  We prepare all four Bell states and measure. In the Z basis:
  - Φ+ and Φ−: you see 00 and 11 (qubits agree)
  - Ψ+ and Ψ−: you see 01 and 10 (qubits disagree)

  The ± phase difference is INVISIBLE in Z-basis measurement!
  Φ+ and Φ− look identical (both give 50/50 of 00/11).
  You'd need to measure in a different basis to distinguish them.

WHAT TO LOOK FOR:
  - Φ+: ~50% |00⟩, ~50% |11⟩
  - Φ−: ~50% |00⟩, ~50% |11⟩ (looks the same!)
  - Ψ+: ~50% |01⟩, ~50% |10⟩
  - Ψ−: ~50% |01⟩, ~50% |10⟩ (looks the same!)

  This is a deep lesson: quantum states can be physically different
  but produce identical measurement statistics in a given basis.

CIRCUITS:
  Φ+: q0: ─H──●──    Φ−: q0: ─H──●──    Ψ+: q0: ─H──●──    Ψ−: q0: ─H──●──
      q1: ────X──        q1: ─X──X──        q1: ─X──X──        q1: ─X──X──
                                (Z on q0)        (X on q1)       (X+Z)

TRY IT:
    from src.experiments.basics.step05_bell_states import bell_states

    results = bell_states.run_all_variants()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class BellStatesExperiment(BaseExperiment):
    """Step 5: Prepare and measure all four Bell states."""

    name = "05_bell_states"
    description = "Step 5: The four Bell states — foundation of quantum entanglement"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=2,
            state_type="GHZ",
            shots=4096,
            noise_enabled=False,
        )

    def run_all_variants(self) -> list[ExperimentResult]:
        """Prepare and measure all four Bell states."""
        results = []

        # Φ+: H, CNOT
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        results.append(self.run({
            "state_type": "CUSTOM",
            "custom_params": {"source": "circuit", "circuit": qc},
        }))

        # Φ−: X, H, CNOT (or H, CNOT, Z)
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.z(0)
        qc.measure([0, 1], [0, 1])
        results.append(self.run({
            "state_type": "CUSTOM",
            "custom_params": {"source": "circuit", "circuit": qc},
        }))

        # Ψ+: H, CNOT, X on q1
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.x(1)
        qc.measure([0, 1], [0, 1])
        results.append(self.run({
            "state_type": "CUSTOM",
            "custom_params": {"source": "circuit", "circuit": qc},
        }))

        # Ψ−: H, CNOT, X and Z
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.x(1)
        qc.z(0)
        qc.measure([0, 1], [0, 1])
        results.append(self.run({
            "state_type": "CUSTOM",
            "custom_params": {"source": "circuit", "circuit": qc},
        }))

        return results


bell_states = BellStatesExperiment()
