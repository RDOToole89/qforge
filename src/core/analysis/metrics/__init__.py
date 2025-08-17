"""
Structured Decoherence Metrics

Research-grade metrics for detecting and quantifying structured decoherence
patterns in quantum measurements. All metrics follow rigorous mathematical
definitions with educational documentation and statistical validation.

Core Metrics:
- Asymmetry Index (AI): Primary structure detection via Total Variation Distance
- Pathway Concentration Ratio (PCR): Error concentration analysis using economic inequality measures  
- Entanglement-Error Correlation (EEC): Topology-error pattern correlation analysis
- Temporal Pathway Stability (TPS): Time series analysis of pathway consistency
- Complexity Emergence Score (CES): Critical threshold detection for structure emergence

Educational Features:
- Comprehensive mathematical documentation with physics interpretation
- Research-grade edge case handling and validation
- Bootstrap confidence intervals for statistical rigor
- Integration with v1.0 JSON schemas for reproducible research
"""

from .asymmetry_index import (
    compute_asymmetry_index,
    compute_asymmetry_index_with_null_comparison,
    AsymmetryAnalysis,
)
from .pathway_concentration_ratio import (
    compute_pathway_concentration_ratio,
    compute_concentration_with_gini,
    ConcentrationAnalysis,
)
from .entanglement_error_correlation import (
    compute_entanglement_error_correlation,
    compute_multiway_entanglement_correlation,
    TopologyAnalysis,
)
from .temporal_pathway_stability import (
    compute_temporal_pathway_stability,
    compute_pathway_persistence_scores,
    compute_temporal_transition_matrix,
    TemporalAnalysis,
)
from .complexity_emergence_score import (
    compute_complexity_emergence_score,
    compute_emergence_across_metrics,
    EmergenceAnalysis,
)

__all__ = [
    # Asymmetry Index
    "compute_asymmetry_index",
    "compute_asymmetry_index_with_null_comparison",
    "AsymmetryAnalysis",
    # Pathway Concentration Ratio
    "compute_pathway_concentration_ratio", 
    "compute_concentration_with_gini",
    "ConcentrationAnalysis",
    # Entanglement-Error Correlation
    "compute_entanglement_error_correlation",
    "compute_multiway_entanglement_correlation",
    "TopologyAnalysis",
    # Temporal Pathway Stability
    "compute_temporal_pathway_stability",
    "compute_pathway_persistence_scores",
    "compute_temporal_transition_matrix",
    "TemporalAnalysis",
    # Complexity Emergence Score
    "compute_complexity_emergence_score",
    "compute_emergence_across_metrics",
    "EmergenceAnalysis",
]