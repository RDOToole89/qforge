"""Step 3: Transpilation — What happens to your circuit on real hardware.

WHAT YOU'LL LEARN:
  Your logical circuit (H, CNOT) can't run directly on hardware.
  Real qubits only support specific "native" gates (sx, rz, cz on IBM Heron)
  and have limited connectivity (not every qubit connects to every other).

  The TRANSPILER converts your logical circuit into a physical one:
  - Decomposes gates into native operations
  - Routes qubits to physical positions (may insert SWAP gates)
  - Optimizes the circuit to reduce depth

  This step lets you see the transpilation in detail.

THE EXPERIMENT:
  Run a 4-qubit GHZ state at three optimization levels:
  - Level 0: No optimization (maximum depth, worst performance)
  - Level 1: Light optimization (default, good balance)
  - Level 3: Heavy optimization (minimum depth, best performance)

  Compare the transpiled depth, gate count, and SWAP insertion.

WHAT TO LOOK FOR:
  - Depth INCREASES from logical to physical (always)
  - Higher optimization = lower transpiled depth (usually)
  - SWAP count may vary (depends on qubit placement)
  - All three should give similar measurement results (same logical circuit)
  - But Structure Score may differ if depth affects decoherence

CIRCUIT (logical):
  q0: ─H──●──●──●── M         Logical depth: 4
  q1: ────X──┼──┼── M         Native gates: none (H, CNOT not native)
  q2: ───────X──┼── M
  q3: ──────────X── M

  After transpilation (example):
  q0: ─√X──Rz──CZ──Rz──√X──CZ──... ── M    Transpiled depth: ~16-24
  q1: ──────────CZ──Rz──√X──CZ──... ── M    Native gates: sx, rz, cz
  ...

  The transpiler turned 4 gates into ~20+. That's the cost of real hardware.

TRY IT:
    from src.experiments.hardware.steps.step03_transpilation import transpilation

    results = transpilation.run_optimization_sweep()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class TranspilationExperiment(BaseExperiment):
    """Step 3: See how transpilation changes your circuit for real hardware."""

    name = "hw_03_transpilation"
    description = "Step 3: Transpilation — see your logical circuit become physical gates"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            sim_mode="hardware",
            shots=4096,
            optimization_level=1,
            visualization_type="histogram",
        )

    def run_optimization_sweep(self) -> list[ExperimentResult]:
        """Run at optimization levels 0, 1, and 3."""
        results = []
        for level in [0, 1, 3]:
            results.append(self.run({"optimization_level": level}))
        return results


transpilation = TranspilationExperiment()
