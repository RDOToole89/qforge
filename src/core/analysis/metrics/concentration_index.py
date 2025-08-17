"""
Concentration Index - Canonical alias for Pathway Concentration Ratio

This module provides the canonical API name for concentration analysis
while maintaining backward compatibility with the original implementation.
"""

from .pathway_concentration_ratio import (
    compute_pathway_concentration_ratio as compute_concentration_index,
    compute_concentration_with_gini,
    ConcentrationAnalysis,
)

__all__ = [
    "compute_concentration_index",
    "compute_concentration_with_gini", 
    "ConcentrationAnalysis",
]