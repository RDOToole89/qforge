"""Hardware experiments — run on real IBM Quantum processors.

These experiments require IBM Quantum credentials. See docs/guides/hardware-setup.md.

Available:
  - hardware_study: The complete 10-experiment structured decoherence study
    (scaling, topology, backend comparison, measurement basis, noise model comparison)
"""

from src.experiments.hardware.hardware_study import (
    run_all,
    run_backend_comparison,
    run_measurement_basis,
    run_optimization_comparison,
    run_scaling_ladder,
    run_topology_comparison,
)

__all__ = [
    "run_all",
    "run_scaling_ladder",
    "run_topology_comparison",
    "run_backend_comparison",
    "run_measurement_basis",
    "run_optimization_comparison",
]
