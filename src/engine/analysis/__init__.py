"""Engine Analysis Module.

Bridge between the engine and core analysis metrics.

This package provides a *stable* engine-facing API for:
- extracting canonical counts from raw Qiskit results, and
- computing a generic MetricsBundle from measurement data.

Only re-export the small surface the engine needs to import.
"""

from .research_integration import (
    compute_metrics_bundle,
    extract_counts_from_result,
)

__all__ = [
    "extract_counts_from_result",
    "compute_metrics_bundle",
]
