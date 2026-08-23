"""Deep Dive: Density Matrix Mode — See the full quantum state.

BEST AFTER: Step 10 (noise types)

WHAT YOU'LL LEARN:
  Normal measurement gives you counts (classical data). But the
  framework can also show you the FULL quantum state as a density
  matrix — including coherences that measurement destroys.

  A density matrix ρ is an NxN matrix (N = 2^n for n qubits) where:
  - Diagonal elements = probabilities of each outcome
  - Off-diagonal elements = quantum coherences (superposition info)
  - Trace(ρ) = 1 always
  - Trace(ρ²) = 1 for pure states, < 1 for mixed states

  Noise turns pure states into mixed states by destroying off-diagonal
  coherences. This is decoherence in its most literal form.

THE EXPERIMENT:
  Run GHZ-3 in density_matrix mode with and without noise.
  Compare the density matrices to see coherences shrink.

WHAT TO LOOK FOR:
  - Clean GHZ-3: large off-diagonal elements at (0,7) and (7,0)
    These represent the coherence between |000⟩ and |111⟩
  - Noisy GHZ-3: off-diagonal elements shrink toward zero
    The state becomes more "classical" — just a mixture of |000⟩ and |111⟩
  - Fidelity drops as coherences are lost

CIRCUIT (same GHZ-3 in both modes):
  q0: ─H──●──●── M
  q1: ────X──┼── M
  q2: ───────X── M

  statevector mode: returns exact |ψ⟩, fidelity = 1.0
  density_matrix mode + noise: returns ρ (mixed state), fidelity < 1.0

  The density matrix ρ shows coherences (off-diagonal elements)
  that measurement destroys. Noise shrinks these coherences —
  that IS decoherence, literally "loss of coherence."

TRY IT:
    from qforge.experiments.basics.deep_dives.dd_density_matrix import density_matrix_mode

    clean, noisy = density_matrix_mode.run_comparison()
    # clean.analysis.measurement_results.density_matrix contains the full state
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class DensityMatrixExperiment(BaseExperiment):
    """Deep Dive: Use density_matrix sim mode to see the full quantum state."""

    name = "dd_density_matrix"
    description = "Deep dive: See the full quantum state with density matrix simulation"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            sim_mode="density_matrix",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            visualization_type=["histogram", "density_matrix"],
            metrics=["structure_score", "total_correlation"],
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run GHZ-3 clean (statevector) and noisy (density_matrix)."""
        clean = self.run(
            {
                "sim_mode": "statevector",
                "noise_enabled": False,
                "rng_seed": 42,
            }
        )
        noisy = self.run(
            {
                "sim_mode": "density_matrix",
                "noise_enabled": True,
                "error_rate": 0.1,
            }
        )
        return clean, noisy


density_matrix_mode = DensityMatrixExperiment()
