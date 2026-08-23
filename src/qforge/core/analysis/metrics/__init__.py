"""Distribution-structure metrics - Canonical Registry API.

Metrics for quantifying structure in quantum measurement outcome
distributions. All metrics follow rigorous mathematical definitions with
educational documentation and statistical validation.

Canonical API:
- compute_metric(name, **kwargs): Compute single metric by name
- compute_all(**kwargs): Compute all available metrics
- metrics_to_schema(results): Convert to v1.0 schema format

Core Metrics (Canonical Names):
- structure_score: Jensen-Shannon divergence from null model
- entanglement_error_correlation: Topology-error pattern correlation
- concentration_index: Economic inequality measures (Gini coefficient)
- total_correlation: Multi-information across all qubits
- pathway_persistence: Temporal stability analysis
- complexity_emergence_score: Critical threshold detection

Educational Features:
- Unified registry system with type safety
- Schema compliance for reproducible output
- Bootstrap confidence intervals and statistical validation
- Educational documentation bridging quantum mechanics and information theory
"""

# Registry and schema bridge (canonical API)
# Canonical alias modules
from .concentration_index import (
    ConcentrationAnalysis,
    compute_concentration_index,
    compute_concentration_with_gini,
)
from .pathway_persistence import (
    TemporalAnalysis,
    compute_pathway_persistence,
    compute_pathway_persistence_scores,
    compute_temporal_transition_matrix,
)
from .profiles import list_profiles, register_profile, resolve_metrics, unregister_profile
from .registry import (
    MetricResult,
    Status,
    compute_all,
    compute_metric,
    determine_status,
    register,
    unregister,
)
from .schema_bridge import (
    get_schema_field_mapping,
    metrics_to_schema,
    validate_schema_output,
)

# Original implementation modules (backward compatibility)
# Asymmetry Index (with graceful fallback if extras aren't present)
try:
    from .asymmetry_index import (
        AsymmetryAnalysis,
        compute_asymmetry_index,
        compute_asymmetry_index_with_null_comparison,
    )
except Exception:  # pragma: no cover
    from .asymmetry_index import compute_asymmetry_index  # required

    compute_asymmetry_index_with_null_comparison = None  # type: ignore[assignment]
    AsymmetryAnalysis = None  # type: ignore[assignment, misc]

# PCR original module (also expose original dataclass alias for clarity)
# CES
from .complexity_emergence_score import (
    EmergenceAnalysis,
    compute_complexity_emergence_score,
    compute_emergence_across_metrics,
)

# EEC
from .entanglement_error_correlation import (
    TopologyAnalysis,
    compute_entanglement_error_correlation,
    compute_multiway_entanglement_correlation,
)
from .pathway_concentration_ratio import (
    ConcentrationAnalysis as PCRConcentrationAnalysis,
)
from .pathway_concentration_ratio import (
    compute_pathway_concentration_ratio,
)
from .temporal_pathway_stability import (
    TemporalAnalysis as TPSTemporalAnalysis,
)

# TPS original (expose original dataclass alias too)
from .temporal_pathway_stability import (
    compute_temporal_pathway_stability,
)

# Total Correlation (canonical implementation)
from .total_correlation import compute_total_correlation

# ---- Public API surface -----------------------------------------------------

__all__: tuple[str, ...] = (
    # Canonical Registry API (PRIMARY)
    "MetricResult",
    "Status",
    "register",
    "unregister",
    "register_profile",
    "unregister_profile",
    "resolve_metrics",
    "list_profiles",
    "compute_metric",
    "compute_all",
    "metrics_to_schema",
    "determine_status",
    "validate_schema_output",
    "get_schema_field_mapping",
    # Canonical Metric Names (Aliases)
    "compute_concentration_index",
    "compute_pathway_persistence",
    "compute_total_correlation",
    # Original Implementation (Backward Compatibility)
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio",
    "compute_concentration_with_gini",
    "ConcentrationAnalysis",  # canonical CI dataclass
    "PCRConcentrationAnalysis",  # original PCR dataclass alias
    "compute_entanglement_error_correlation",
    "compute_multiway_entanglement_correlation",
    "TopologyAnalysis",
    "compute_temporal_pathway_stability",
    "compute_pathway_persistence_scores",
    "compute_temporal_transition_matrix",
    "TemporalAnalysis",  # canonical PP dataclass
    "TPSTemporalAnalysis",  # original TPS dataclass alias
    "compute_complexity_emergence_score",
    "compute_emergence_across_metrics",
    "EmergenceAnalysis",
)

# Optionally expose these only if available (keeps imports safe in partial installs)
if AsymmetryAnalysis is not None:
    __all__ += ("AsymmetryAnalysis",)
if compute_asymmetry_index_with_null_comparison is not None:
    __all__ += ("compute_asymmetry_index_with_null_comparison",)
