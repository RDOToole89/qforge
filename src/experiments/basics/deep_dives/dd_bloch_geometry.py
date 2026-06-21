"""Deep Dive: Bloch Sphere Geometry — Gates as rotations.

BEST AFTER: Steps 1-3 (superposition, measurement, gates)

WHAT YOU'LL LEARN:
  Every single-qubit gate is a ROTATION on the Bloch sphere.
  The Bloch sphere is a unit sphere where:
  - North pole = |0⟩
  - South pole = |1⟩
  - Equator = superposition states (|+⟩, |−⟩, |+i⟩, |−i⟩)

  Understanding this geometry turns abstract gate matrices into
  physical rotations you can visualize.

THE ROTATIONS:
  Rx(θ): Rotate around X axis by θ. At θ=π, this is the X gate.
  Ry(θ): Rotate around Y axis by θ. At θ=π/2, goes from |0⟩ to |+⟩.
  Rz(θ): Rotate around Z axis by θ. Changes phase without affecting
         the probability of measuring 0 vs 1.

THE EXPERIMENT:
  We trace paths on the Bloch sphere by applying Ry at 12 angles
  from 0 to 2π. This draws a great circle from |0⟩ down through
  |+⟩ to |1⟩ and back.

  Then we do the same with Rx and Rz to see different circles.

WHAT TO LOOK FOR:
  - Ry sweep: P(1) goes 0% → 50% → 100% → 50% → 0% (smooth sine wave)
  - Rx sweep: same probabilities but different phase (invisible in Z-basis)
  - Rz sweep: P(1) stays 0% always! Z rotation starting from |0⟩ is invisible.
    But if you start from |+⟩, Rz changes the outcome.

  This teaches why measurement basis matters — some rotations are
  "invisible" depending on how you measure.

CIRCUITS (tracing a circle with Ry):
  θ=0:     q: ──────── M    → always 0 (north pole)
  θ=π/4:   q: ─Ry(π/4) M    → ~15% chance of 1
  θ=π/2:   q: ─Ry(π/2) M    → 50/50 (equator = |+⟩)
  θ=π:     q: ─Ry(π)── M    → always 1 (south pole)
  θ=3π/2:  q: ─Ry(3π/2) M   → 50/50 (back through equator)
  θ=2π:    q: ─Ry(2π)─ M    → always 0 (full circle, back to north)

  Same idea with Rx (X-axis rotation) and Rz (Z-axis rotation).
  Rz starting from |0⟩ is invisible in Z-basis measurement!

TRY IT:
    from src.experiments.basics.deep_dives.dd_bloch_geometry import bloch_geometry

    results = bloch_geometry.run_ry_circle()
    results = bloch_geometry.run_all_axes()
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class BlochGeometryExperiment(BaseExperiment):
    """Deep Dive: Trace paths on the Bloch sphere with rotation gates."""

    name = "dd_bloch_geometry"
    description = "Deep dive: Gates as rotations — trace paths on the Bloch sphere"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        qc = QuantumCircuit(1, 1)
        qc.ry(np.pi / 4, 0)
        qc.measure(0, 0)
        return ExperimentConfig(
            num_qubits=1,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": qc},
        )

    def run_ry_circle(self, steps: int = 12) -> list[ExperimentResult]:
        """Trace a great circle on the Bloch sphere using Ry."""
        results = []
        for theta in np.linspace(0, 2 * np.pi, steps):
            qc = QuantumCircuit(1, 1)
            qc.ry(float(theta), 0)
            qc.measure(0, 0)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": qc},
                    }
                )
            )
        return results

    def run_all_axes(self) -> dict[str, list[ExperimentResult]]:
        """Trace circles around all three axes (Rx, Ry, Rz)."""
        axes = {}
        for axis in ["rx", "ry", "rz"]:
            results = []
            for theta in np.linspace(0, 2 * np.pi, 8):
                qc = QuantumCircuit(1, 1)
                getattr(qc, axis)(float(theta), 0)
                qc.measure(0, 0)
                results.append(
                    self.run(
                        {
                            "custom_params": {"source": "circuit", "circuit": qc},
                        }
                    )
                )
            axes[axis] = results
        return axes


bloch_geometry = BlochGeometryExperiment()
