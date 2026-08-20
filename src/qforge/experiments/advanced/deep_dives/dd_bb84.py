"""Deep Dive: BB84 — Quantum Key Distribution.

BEST AFTER: Step 4 (Teleportation) + Basics dd_measurement_basis

WHAT YOU'LL LEARN:
  BB84 is the first quantum cryptography protocol (Bennett & Brassard, 1984).
  It uses the fact that measuring a quantum state in the wrong basis
  irreversibly disturbs it — an eavesdropper CANNOT copy quantum
  information without being detected.

THE PROTOCOL (simplified):
  1. Alice randomly prepares qubits in Z or X basis (|0⟩,|1⟩ or |+⟩,|−⟩)
  2. Bob randomly measures each in Z or X basis
  3. They publicly compare BASES (not values)
  4. Where bases match → they share a secret bit
  5. Where bases differ → they discard

  If Eve intercepts and re-sends, she introduces ~25% error rate
  in the matching-basis bits → Alice and Bob detect the eavesdropper.

CIRCUIT (simplified, 4 bits):
  q0: ─[A prepares in Z or X basis]─ ░ ─[B measures in same basis]─ M
  q1: ─[A prepares in Z or X basis]─ ░ ─[B measures in same basis]─ M
  q2: ─[A prepares in Z or X basis]─ ░ ─[B measures in same basis]─ M
  q3: ─[A prepares in Z or X basis]─ ░ ─[B measures in same basis]─ M

  Z-basis: |0⟩ or |1⟩  (no H gate)
  X-basis: |+⟩ or |−⟩  (H gate applied)

  When bases match → Bob gets Alice's bit perfectly.
  When bases differ → 50/50 random (discarded).
  Eavesdropper → introduces ~25% errors in matching-basis bits.

TRY IT:
    from qforge.experiments.advanced.deep_dives.dd_bb84 import bb84

    result = bb84.run()
    results = bb84.run_with_and_without_eve()
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


def _bb84_circuit(n_bits: int = 8, seed: int = 42) -> QuantumCircuit:
    """Build a simplified BB84 circuit (Alice prepares, Bob measures same basis)."""
    rng = np.random.default_rng(seed)

    qc = QuantumCircuit(n_bits, n_bits)

    alice_bases = rng.integers(0, 2, size=n_bits)  # 0=Z, 1=X
    alice_bits = rng.integers(0, 2, size=n_bits)

    for i in range(n_bits):
        # Alice prepares
        if alice_bits[i] == 1:
            qc.x(i)
        if alice_bases[i] == 1:
            qc.h(i)  # X-basis encoding

    qc.barrier()

    # Bob measures in same bases (ideal case — no errors expected)
    for i in range(n_bits):
        if alice_bases[i] == 1:
            qc.h(i)  # X-basis measurement

    qc.measure(range(n_bits), range(n_bits))
    return qc


class BB84Experiment(BaseExperiment):
    """Deep Dive: BB84 quantum key distribution protocol."""

    name = "dd_bb84"
    description = "Deep dive: BB84 — quantum key distribution using basis choice"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _bb84_circuit(8)
        return ExperimentConfig(
            num_qubits=8,
            state_type="CUSTOM",
            shots=1024,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
            visualization_type=["histogram", "circuit"],
        )

    def run_with_and_without_eve(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run with and without noise (noise simulates eavesdropping)."""
        clean = self.run({"noise_enabled": False})
        noisy = self.run(
            {
                "noise_enabled": True,
                "noise_type": "depolarizing",
                "error_rate": 0.15,
            }
        )
        return clean, noisy


bb84 = BB84Experiment()
