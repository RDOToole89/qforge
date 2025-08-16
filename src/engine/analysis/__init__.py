"""
Engine Analysis Module

Bridge between engine and core analysis modules for research integration.
"""

from .research_integration import compute_research_metrics, extract_counts_from_result

__all__ = [
    "compute_research_metrics",
    "extract_counts_from_result"
]