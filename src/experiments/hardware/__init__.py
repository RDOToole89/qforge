"""Hardware experiments — run on real IBM Quantum processors.

Requires IBM Quantum credentials. See docs/guides/hardware-setup.md.

Organized into two parts:

  steps/       — 5-step progression from first run to real decoherence
  deep_dives/  — Full research suites and advanced hardware experiments
"""

# Steps
from src.experiments.hardware.deep_dives.dd_full_study import (
    run_all,
    run_backend_comparison,
    run_measurement_basis,
    run_optimization_comparison,
    run_scaling_ladder,
    run_topology_comparison,
)

# Deep dives
from src.experiments.hardware.deep_dives.dd_readout_errors import readout_errors
from src.experiments.hardware.steps.step01_first_hardware_run import first_hardware
from src.experiments.hardware.steps.step02_hardware_vs_simulation import hardware_vs_sim
from src.experiments.hardware.steps.step03_transpilation import transpilation
from src.experiments.hardware.steps.step04_backend_exploration import backend_exploration
from src.experiments.hardware.steps.step05_real_decoherence import real_decoherence

__all__ = [
    "first_hardware",
    "hardware_vs_sim",
    "transpilation",
    "backend_exploration",
    "real_decoherence",
    "readout_errors",
    "run_all",
    "run_scaling_ladder",
    "run_topology_comparison",
    "run_backend_comparison",
    "run_measurement_basis",
    "run_optimization_comparison",
]
