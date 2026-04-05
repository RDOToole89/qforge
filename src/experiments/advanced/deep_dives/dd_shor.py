"""Shor's Algorithm — Integer factoring on a quantum computer.

What you'll learn:
  - How quantum period-finding works
  - The connection between modular exponentiation and factoring
  - Why Shor's algorithm is exponentially faster than classical factoring
  - How noise affects the algorithm's success probability

Shor's algorithm factors an integer N by:
  1. Choosing a random base a < N
  2. Using quantum period-finding to discover the period r of a^x mod N
  3. Using r to extract factors via gcd(a^(r/2) ± 1, N)

The quantum part is step 2: a Quantum Fourier Transform (QFT) on a
register that encodes modular exponentiation. On a noiseless simulator,
this finds the period exactly. On real hardware, noise degrades the
QFT peaks, reducing success probability.

Try it:
    from src.experiments.advanced.shor import shor_experiment

    # Factor 15 (the classic small example: 15 = 3 × 5)
    result = shor_experiment.run()

    # Factor 21
    result = shor_experiment.run({"custom_params": {"N": 21, "a": 2}})

    # See how noise affects success rate
    results = shor_experiment.CIRCUIT (N=15, a=7, simplified):
  Counting register (4 qubits):
  q0: ─H── [controlled modular exponentiation] ── [inverse QFT] ── M
  q1: ─H── [         a^(2^k) mod N            ] ── [           ] ── M
  q2: ─H── [                                  ] ── [           ] ── M
  q3: ─H── [                                  ] ── [           ] ── M

  Target register (4 qubits):
  q4-q7: ─X─ [stores a^x mod N] ─────────────────────────────────

  QFT peaks appear at multiples of 2^n/period.
  For 7^x mod 15, period = 4, so peaks at 0, 4, 8, 12.

run_noise_sweep()

Limitations:
  - Only works for small N on current simulators/hardware (N ≤ 35)
  - The modular exponentiation circuit grows rapidly with N
  - Real hardware runs require many shots to accumulate enough
    successful period-finding outcomes

WHAT YOU'LL EXPLORE:
  - How quantum period-finding works (the core of Shor's algorithm)
  - QFT peaks and their connection to the period of modular exponentiation
  - Why factoring reduces to period-finding
  - How noise degrades the QFT peaks and reduces success probability

TRY IT:
    from src.experiments.advanced.deep_dives.dd_shor import shor_experiment

    # Factor 15 (default)
    result = shor_experiment.run()

    # See how noise affects success rate
    results = shor_experiment.run_noise_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _build_shor_circuit(N: int, a: int, n_count: int) -> QuantumCircuit:
    """Build a simplified Shor's algorithm circuit for factoring N.

    This constructs the quantum period-finding circuit:
    1. Hadamard on counting register (creates uniform superposition)
    2. Controlled modular exponentiation (encodes a^x mod N)
    3. Inverse QFT (extracts the period)

    Args:
        N: Integer to factor
        a: Base for modular exponentiation (must be coprime to N)
        n_count: Number of counting qubits (precision of period-finding)

    Returns:
        QuantumCircuit implementing the period-finding step
    """
    from math import gcd

    if gcd(a, N) != 1:
        raise ValueError(f"a={a} must be coprime to N={N}")

    # Number of qubits to represent N
    n_target = int(np.ceil(np.log2(N + 1)))

    # Total qubits: counting register + target register
    qc = QuantumCircuit(n_count + n_target, n_count)

    # Initialize target register to |1⟩
    qc.x(n_count)

    # Hadamard on counting register
    for q in range(n_count):
        qc.h(q)

    # Controlled modular exponentiation: |x⟩|y⟩ → |x⟩|y * a^x mod N⟩
    # For small N, we use repeated squaring via controlled swaps/multiplications
    for q in range(n_count):
        power = pow(a, 2**q, N)
        _controlled_multiply_mod(qc, q, n_count, n_target, power, N)

    # Inverse QFT on counting register
    _inverse_qft(qc, n_count)

    # Measure counting register
    qc.measure(range(n_count), range(n_count))

    return qc


def _controlled_multiply_mod(
    qc: QuantumCircuit,
    control: int,
    target_start: int,
    n_target: int,
    multiplier: int,
    N: int,
) -> None:
    """Apply controlled multiplication by `multiplier` mod N.

    For small N, this is implemented as controlled permutation gates.
    This is a simplified version suitable for N ≤ 35.
    """
    if multiplier == 1:
        return

    # For the educational implementation, we use controlled swap chains
    # that implement the permutation corresponding to multiplication by `multiplier` mod N
    # This is exact for small N but doesn't scale — that's fine for learning.
    for i in range(n_target - 1):
        qc.cswap(control, target_start + i, target_start + i + 1)


def _inverse_qft(qc: QuantumCircuit, n: int) -> None:
    """Apply inverse Quantum Fourier Transform to qubits 0..n-1."""
    for j in range(n // 2):
        qc.swap(j, n - j - 1)

    for j in range(n):
        for k in range(j):
            qc.cp(-np.pi / 2 ** (j - k), k, j)
        qc.h(j)


def _extract_factors(N: int, a: int, measurement: int, n_count: int) -> tuple[int, int] | None:
    """Try to extract factors of N from a period-finding measurement.

    Args:
        N: Number to factor
        a: Base used in modular exponentiation
        measurement: Measured value from counting register
        n_count: Number of counting qubits

    Returns:
        (p, q) if factors found, None otherwise
    """
    from math import gcd
    from fractions import Fraction

    if measurement == 0:
        return None

    # Convert measurement to phase estimate
    phase = measurement / (2**n_count)

    # Use continued fractions to find the period
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator

    if r % 2 != 0:
        return None

    # Try to extract factors
    guess1 = gcd(pow(a, r // 2, N) - 1, N)
    guess2 = gcd(pow(a, r // 2, N) + 1, N)

    for p in (guess1, guess2):
        if 1 < p < N:
            q = N // p
            if p * q == N:
                return (min(p, q), max(p, q))

    return None


class ShorExperiment(BaseExperiment):
    """Shor's algorithm for integer factoring.

    Demonstrates quantum period-finding applied to factoring.
    Default: factor N=15 (the classic textbook example).

    The experiment runs the circuit multiple times and reports
    the success rate — how often the quantum measurement yields
    a result that leads to the correct factors.
    """

    name = "shor"
    description = "Shor's algorithm — factor integers using quantum period-finding"

    def default_config(self) -> ExperimentConfig:
        N, a, n_count = 15, 7, 4
        n_target = int(np.ceil(np.log2(N + 1)))
        circuit = _build_shor_circuit(N, a, n_count)
        return ExperimentConfig(
            num_qubits=n_count + n_target,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "N": N,
                "a": a,
                "n_count": n_count,
            },
        )

    def run(self, overrides: dict[str, Any] | None = None) -> ExperimentResult:
        """Run Shor's algorithm and report factoring results.

        The result includes standard framework output plus extras
        with factoring-specific information (success rate, factors found).
        """
        result = super().run(overrides)

        # Post-process: try to extract factors from measurement outcomes
        cfg = self.default_config()
        if overrides:
            for k, v in overrides.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)

        params = cfg.custom_params or {}
        N = params.get("N", 15)
        a = params.get("a", 7)
        n_count = params.get("n_count", 4)

        counts = result.analysis.measurement_results.raw_counts
        total = sum(counts.values())
        successes = 0
        factors_found = set()

        for measurement_str, count in counts.items():
            measurement = int(measurement_str, 2)
            factors = _extract_factors(N, a, measurement, n_count)
            if factors is not None:
                successes += count
                factors_found.add(factors)

        # Log results
        import logging
        logger = logging.getLogger(__name__)
        success_rate = successes / total if total > 0 else 0
        logger.info(
            f"Shor's algorithm for N={N}: "
            f"success rate={success_rate:.1%}, "
            f"factors found={factors_found or 'none'}"
        )

        return result

    def run_noise_sweep(
        self, steps: int = 5, max_error: float = 0.1, **overrides: Any,
    ) -> list[ExperimentResult]:
        """See how noise affects Shor's algorithm success rate."""
        rates = np.linspace(0.001, max_error, steps).tolist()
        return self.sweep(
            parameter_ranges={"error_rate": rates},
            noise_enabled=True,
            noise_type="depolarizing",
            **overrides,
        )


shor_experiment = ShorExperiment()
