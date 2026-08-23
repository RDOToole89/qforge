"""Step 3: Grover's Search — Find a needle in a quantum haystack.

WHAT YOU'LL LEARN:
  Grover's algorithm searches an unstructured list of N items in
  O(√N) steps instead of O(N). This is a QUADRATIC speedup —
  not as dramatic as Deutsch-Jozsa's exponential speedup, but it
  applies to a much broader class of problems.

HOW IT WORKS:
  1. Start with uniform superposition (all items equally likely)
  2. Oracle: flip the phase of the target item (like Step 2's oracle)
  3. Diffusion: amplify the probability of the marked item
  4. Repeat steps 2-3 about √N times
  5. Measure — target appears with high probability

  The magic is in the "diffusion operator" — it reflects amplitudes
  around the mean, which progressively boosts the marked item.

THE EXPERIMENT:
  Search for a specific bitstring in a 4-qubit space (16 items).
  The target |1010⟩ should appear with >96% probability after
  the optimal number of iterations.

FRAMEWORK SKILL:
  You'll learn amplitude amplification — the most general technique
  in quantum algorithms. Grover's is a special case; the same idea
  powers quantum counting, optimization, and machine learning.

CIRCUIT (simplified 3-qubit, 1 iteration):
  q0: ─H── [oracle] ── [diffusion] ── M
  q1: ─H── [oracle] ── [diffusion] ── M
  q2: ─H── [oracle] ── [diffusion] ── M

  Oracle: flips phase of target |101⟩
  Diffusion: reflects amplitudes around mean (2|ψ⟩⟨ψ| - I)
  Repeat √N times for optimal success probability.

TRY IT:
    from qforge.experiments.advanced.steps.step03_grover_search import grover_search

    result = grover_search.run()
    results = grover_search.run_iteration_sweep()  # See success vs iterations
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


def _grover_circuit(n: int, target: str, n_iters: int | None = None) -> QuantumCircuit:
    """Build Grover's search circuit."""
    if n_iters is None:
        n_iters = max(1, int(np.pi / 4 * np.sqrt(2**n)))

    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    for _ in range(n_iters):
        # Oracle
        for i, bit in enumerate(target):
            if bit == "0":
                qc.x(i)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for i, bit in enumerate(target):
            if bit == "0":
                qc.x(i)

        # Diffusion
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))

    qc.measure(range(n), range(n))
    return qc


class GroverSearchExperiment(BaseExperiment):
    """Step 3: Grover's search with amplitude amplification."""

    name = "adv_03_grover_search"
    description = "Step 3: Grover's search — quadratic speedup via amplitude amplification"
    metrics_hint = (
        "The marked item should dominate. Concentration Index tracks how "
        "peaked the search became."
    )
    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _grover_circuit(4, "1010")
        return ExperimentConfig(
            num_qubits=4,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
            visualization_type=["histogram", "circuit"],
            metrics=["concentration_index", "asymmetry_index"],
        )

    def run_iteration_sweep(self) -> list[ExperimentResult]:
        """See how success probability changes with iteration count."""
        results = []
        for n_iters in [1, 2, 3, 4, 5]:
            circuit = _grover_circuit(4, "1010", n_iters)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": circuit},
                    }
                )
            )
        return results


grover_search = GroverSearchExperiment()
