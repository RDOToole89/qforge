"""
Pathway Persistence - Canonical alias for Temporal Pathway Stability

This module provides the canonical API name for temporal persistence analysis
while maintaining backward compatibility with the original implementation.
"""

from .temporal_pathway_stability import (
    TemporalAnalysis,
    compute_pathway_persistence_scores,
    compute_temporal_transition_matrix,
)
from .temporal_pathway_stability import (
    compute_temporal_pathway_stability as compute_pathway_persistence,
)

__all__ = [
    "compute_pathway_persistence",
    "compute_pathway_persistence_scores",
    "compute_temporal_transition_matrix",
    "TemporalAnalysis",
]
