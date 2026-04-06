"""Basic experiments for learning quantum computing concepts.

Organized into two parts:

  steps/       — 11-step core learning path (do these in order)
  deep_dives/  — Go deeper on specific topics (do after the relevant step)

See README.md for the full progression with descriptions.
"""

# Steps — core learning path
from src.experiments.basics.steps.step01_superposition import SuperpositionExperiment, superposition
from src.experiments.basics.steps.step02_measurement import MeasurementExperiment, measurement
from src.experiments.basics.steps.step03_single_gates import SingleGatesExperiment, single_gates
from src.experiments.basics.steps.step04_two_qubits import TwoQubitsExperiment, two_qubits
from src.experiments.basics.steps.step05_bell_states import BellStatesExperiment, bell_states
from src.experiments.basics.steps.step06_ghz_states import GHZStatesExperiment, ghz_states
from src.experiments.basics.steps.step07_w_states import WStatesExperiment, w_states
from src.experiments.basics.steps.step08_cluster_states import ClusterStatesExperiment, cluster_states
from src.experiments.basics.steps.step09_noise_intro import NoiseIntroExperiment, noise_intro
from src.experiments.basics.steps.step10_noise_types import NoiseTypesExperiment, noise_types
from src.experiments.basics.steps.step11_noise_and_entanglement import (
    NoiseAndEntanglementExperiment,
    noise_and_entanglement,
)

# Deep dives
from src.experiments.basics.deep_dives.dd_bell_basics import BellExperiment, bell_experiment
from src.experiments.basics.deep_dives.dd_bell_correlations import (
    BellCorrelation,
    bell_correlation,
)
from src.experiments.basics.deep_dives.dd_bloch_geometry import BlochGeometryExperiment, bloch_geometry
from src.experiments.basics.deep_dives.dd_density_matrix import DensityMatrixExperiment, density_matrix_mode
from src.experiments.basics.deep_dives.dd_entanglement_fragility import (
    EntanglementFragilityExperiment,
    entanglement_fragility,
)
from src.experiments.basics.deep_dives.dd_ghz_structure_metrics import GHZExploration, ghz_exploration
from src.experiments.basics.deep_dives.dd_measurement_basis import MeasurementBasisExperiment, measurement_basis
from src.experiments.basics.deep_dives.dd_noise_model_comparison import NoiseComparison, noise_comparison
from src.experiments.basics.deep_dives.dd_structure_scaling import StructureScalingExperiment, structure_scaling
from src.experiments.basics.deep_dives.dd_teleportation_intro import (
    TeleportationIntroExperiment,
    teleportation_intro,
)

__all__ = [
    # Steps
    "SuperpositionExperiment", "superposition",
    "MeasurementExperiment", "measurement",
    "SingleGatesExperiment", "single_gates",
    "TwoQubitsExperiment", "two_qubits",
    "BellStatesExperiment", "bell_states",
    "GHZStatesExperiment", "ghz_states",
    "WStatesExperiment", "w_states",
    "ClusterStatesExperiment", "cluster_states",
    "NoiseIntroExperiment", "noise_intro",
    "NoiseTypesExperiment", "noise_types",
    "NoiseAndEntanglementExperiment", "noise_and_entanglement",
    # Deep dives
    "BlochGeometryExperiment", "bloch_geometry",
    "BellExperiment", "bell_experiment",
    "BellCorrelation", "bell_correlation",
    "TeleportationIntroExperiment", "teleportation_intro",
    "GHZExploration", "ghz_exploration",
    "EntanglementFragilityExperiment", "entanglement_fragility",
    "MeasurementBasisExperiment", "measurement_basis",
    "NoiseComparison", "noise_comparison",
    "DensityMatrixExperiment", "density_matrix_mode",
    "StructureScalingExperiment", "structure_scaling",
]
