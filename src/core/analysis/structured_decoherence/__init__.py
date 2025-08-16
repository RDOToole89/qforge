"""
Structured Decoherence Analysis Module

This module implements the quantitative metrics for structured decoherence pathway research,
investigating whether quantum decoherence follows structured pathways determined by 
entanglement network topology.

Core Research Hypothesis:
    Quantum decoherence is not purely stochastic, but follows preferred pathways - 
    structured, constraint-based transitions that emerge above a critical complexity 
    threshold (≥3 qubits).

Key Metrics:
    - AI: Asymmetry Index - Deviation from uniform error distribution
    - PCR: Pathway Concentration Ratio - Concentration of errors in top pathways  
    - EEC: Entanglement-Error Correlation - Correlation between topology and errors
    - TPS: Temporal Pathway Stability - Consistency across noise levels
    - CES: Complexity Emergence Score - Threshold for entanglement complexity
"""

from .pathway_metrics import (
    compute_asymmetry_index,
    compute_pathway_concentration_ratio, 
    compute_entanglement_error_correlation,
    compute_temporal_pathway_stability,
    compute_complexity_emergence_score,
)

from .pathway_analysis import (
    compute_all_pathway_metrics,
    analyze_decoherence_structure,
)

__all__ = [
    # Individual metrics
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio", 
    "compute_entanglement_error_correlation",
    "compute_temporal_pathway_stability",
    "compute_complexity_emergence_score",
    
    # Combined analysis
    "compute_all_pathway_metrics",
    "analyze_decoherence_structure",
]