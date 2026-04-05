"""Step 6: Quantum Fourier Transform — The engine inside quantum algorithms.

WHAT YOU'LL LEARN:
  The QFT is the quantum analogue of the discrete Fourier transform.
  It's THE key subroutine — used inside Shor's factoring, phase
  estimation, quantum counting, and many other algorithms.

  Classically, the FFT takes O(N log N) operations.
  The QFT takes O(log²N) quantum gates — exponentially faster.

HOW IT WORKS:
  QFT transforms computational basis states into Fourier basis states:
  |j⟩ → (1/√N) Σ_k exp(2πijk/N) |k⟩

  In practice, it's a cascade of Hadamard and controlled-phase gates,
  followed by qubit reversal (swap).

THE EXPERIMENT:
  Apply QFT to various input states and observe the output distribution.
  - QFT on |000⟩ → uniform superposition (all outcomes equal)
  - QFT on |001⟩ → phases create interference pattern
  - QFT on periodic state → peaks at multiples of the period

  The periodic state is the key: QFT DETECTS PERIODICITY.
  This is why Shor's algorithm works — factoring reduces to period-finding.

FRAMEWORK SKILL:
  You now understand the most important subroutine in quantum computing.
  Combined with the oracle model from Step 2, you have the building
  blocks for every major quantum algorithm.

CIRCUIT (3-qubit QFT):
  q0: ──H──P(π/2)──P(π/4)──────────────×── M
  q1: ─────●───────────────H──P(π/2)───┼── M
  q2: ─────────────●──────────●─────H──×── M

  H = Hadamard, P(θ) = controlled phase rotation
  × = SWAP (bit reversal at the end)
  The cascade of decreasing phase rotations encodes Fourier coefficients.

TRY IT:
    from src.experiments.advanced.steps.step06_qft import qft

    results = qft.run_input_comparison()
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _qft_circuit(n: int, input_state: str | None = None) -> QuantumCircuit:
    """Build a QFT circuit with optional input state preparation."""
    qc = QuantumCircuit(n, n)

    # Prepare input state
    if input_state:
        for i, bit in enumerate(input_state):
            if bit == "1":
                qc.x(i)

    qc.barrier()

    # QFT
    for i in range(n):
        qc.h(i)
        for j in range(i + 1, n):
            qc.cp(np.pi / 2 ** (j - i), j, i)

    # Swap qubits (bit reversal)
    for i in range(n // 2):
        qc.swap(i, n - i - 1)

    qc.measure(range(n), range(n))
    return qc


class QFTExperiment(BaseExperiment):
    """Step 6: Quantum Fourier Transform — detect periodicity."""

    name = "adv_06_qft"
    description = "Step 6: QFT — the engine inside Shor's and phase estimation"

    def default_config(self) -> ExperimentConfig:
        circuit = _qft_circuit(4, "0000")
        return ExperimentConfig(
            num_qubits=4,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
        )

    def run_input_comparison(self) -> list[ExperimentResult]:
        """Run QFT on different input states to see different output patterns."""
        results = []
        for input_state in ["0000", "0001", "0010", "0100", "1000"]:
            circuit = _qft_circuit(4, input_state)
            results.append(self.run({
                "custom_params": {"source": "circuit", "circuit": circuit},
            }))
        return results


qft = QFTExperiment()
