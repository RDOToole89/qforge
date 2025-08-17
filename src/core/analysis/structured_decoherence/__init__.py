"""
Structured Decoherence Analysis Module

This module implements the quantitative metrics for structured decoherence pathway research,
investigating whether quantum decoherence follows structured pathways determined by 
entanglement network topology.

Core Research Hypothesis:
    Quantum decoherence is not purely stochastic, but follows preferred pathways - 
    structured, constraint-based transitions that emerge above a critical complexity 
    threshold (≥3 qubits).

Complete Metric Suite (8 metrics as per v1.0 schemas):
    Original 5 metrics:
    - AI: Asymmetry Index - Deviation from uniform error distribution
    - PCR: Pathway Concentration Ratio - Concentration of errors in top pathways  
    - EEC: Entanglement-Error Correlation - Correlation between topology and errors
    - TPS: Temporal Pathway Stability - Consistency across noise levels
    - CES: Complexity Emergence Score - Threshold for entanglement complexity
    
    New schema-required metrics:
    - SS: Structure Score - Jensen-Shannon divergence from null model
    - CI: Concentration Index - Gini coefficient of error distribution
    - TC: Total Correlation - Multi-information in quantum measurements
"""

# Original 5 metrics
from .pathway_metrics import (
    compute_asymmetry_index,
    compute_pathway_concentration_ratio, 
    compute_entanglement_error_correlation,
    compute_temporal_pathway_stability,
    compute_complexity_emergence_score,
)

# New schema-required metrics
from .schema_metrics import (
    compute_structure_score,
    compute_concentration_index,
    compute_total_correlation,
    create_null_model
)

# Statistical confidence methods
from .statistical_confidence import (
    MetricWithConfidence,
    bootstrap_confidence_interval,
    determine_validation_status,
    compute_metric_with_confidence,
    compute_all_metrics_with_confidence
)

# Analysis functions
from .pathway_analysis import (
    compute_all_pathway_metrics,
    analyze_decoherence_structure,
)

__all__ = [
    # Original metrics
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio", 
    "compute_entanglement_error_correlation",
    "compute_temporal_pathway_stability",
    "compute_complexity_emergence_score",
    
    # New schema metrics
    "compute_structure_score",
    "compute_concentration_index",
    "compute_total_correlation",
    "create_null_model",
    
    # Statistical confidence
    "MetricWithConfidence",
    "bootstrap_confidence_interval",
    "determine_validation_status",
    "compute_metric_with_confidence",
    "compute_all_metrics_with_confidence",
    
    # Combined analysis
    "compute_all_pathway_metrics",
    "analyze_decoherence_structure",
]