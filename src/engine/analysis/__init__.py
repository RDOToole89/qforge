"""
Engine Analysis Module

Bridge between the engine and core structured-decoherence analysis.

This package provides a *stable* engine-facing API for:
- extracting canonical counts from raw Qiskit results, and
- computing research metrics either as typed engine models or schema_v1 dicts.

Only re-export the small surface the engine needs to import.
"""

from .research_integration import (
    extract_counts_from_result,
    compute_research_schema,
    compute_research_metrics,
)

__all__ = [
    "extract_counts_from_result",
    "compute_research_schema",
    "compute_research_metrics",
]
