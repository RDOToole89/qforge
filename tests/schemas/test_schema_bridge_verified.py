"""Rigorous verified tests for the v1.0 schema bridge.

Covers metrics_to_schema, _convert_metric_result, _normalize_result_keys,
validate_schema_output, and get_schema_field_mapping with exact, asserted
behavior including alias normalization, ci95 canonicalization, and error paths.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.analysis.metrics.registry import MetricResult, compute_all
from src.core.analysis.metrics.schema_bridge import (
    get_schema_field_mapping,
    metrics_to_schema,
    validate_schema_output,
)

CORE_KEYS = [
    "structure_score",
    "entanglement_error_correlation",
    "concentration_index",
    "total_correlation",
]


def _canonical_results() -> dict[str, MetricResult]:
    return {
        "structure_score": MetricResult(
            value=0.3, ci95=(0.2, 0.4), status="validated", extras={"k": 1}
        ),
        "entanglement_error_correlation": MetricResult(
            value=0.1, ci95=(0.05, 0.15), status="experimental"
        ),
        "concentration_index": MetricResult(value=2.0, ci95=(1.0, 3.0), status="validated"),
        "total_correlation": MetricResult(value=0.5, ci95=(0.4, 0.6), status="validated"),
    }


class TestMetricsToSchemaEndToEnd:
    def test_compute_all_round_trip(self):
        results = compute_all(
            CORE_KEYS, counts={"00": 500, "11": 500}, rng=np.random.default_rng(0), B=80
        )
        schema = metrics_to_schema(results)
        assert schema["schema_version"] == "1.0"
        for key in CORE_KEYS:
            assert key in schema
            assert "value" in schema[key]
            assert "status" in schema[key]
        # structure_score is JSD-on-Bell exact value.
        assert schema["structure_score"]["value"] == pytest.approx(0.30637413339655933)
        # Optional metrics default to None when not supplied.
        assert schema["pathway_persistence"] is None
        assert schema["complexity_emergence_score"] is None
        assert validate_schema_output(schema) is True


class TestAliasNormalization:
    def test_aliases_map_to_canonical(self):
        results = {
            "asymmetry_index": MetricResult(value=0.42, ci95=(0.3, 0.5), status="validated"),
            "entanglement_error_correlation": MetricResult(value=0.1, status="experimental"),
            "pathway_concentration_ratio": MetricResult(
                value=3.0, ci95=(2.0, 4.0), status="validated"
            ),
            "total_correlation": MetricResult(value=0.5, status="validated"),
            "temporal_pathway_stability": MetricResult(
                value=0.9, ci95=(0.8, 1.0), status="validated"
            ),
        }
        schema = metrics_to_schema(results)
        # asymmetry_index -> structure_score
        assert schema["structure_score"]["value"] == pytest.approx(0.42)
        # pathway_concentration_ratio -> concentration_index
        assert schema["concentration_index"]["value"] == pytest.approx(3.0)
        # temporal_pathway_stability -> pathway_persistence
        assert schema["pathway_persistence"]["value"] == pytest.approx(0.9)

    def test_canonical_takes_precedence_over_alias(self):
        results = _canonical_results()
        # Add an alias that would conflict; canonical must win.
        results["asymmetry_index"] = MetricResult(value=99.0, status="validated")
        schema = metrics_to_schema(results)
        assert schema["structure_score"]["value"] == pytest.approx(0.3)

    def test_optional_insufficient_status_becomes_none(self):
        results = _canonical_results()
        results["pathway_persistence"] = MetricResult(value=0.0, status="insufficient_runs")
        results["complexity_emergence_score"] = MetricResult(value=0.0, status="insufficient_data")
        schema = metrics_to_schema(results)
        assert schema["pathway_persistence"] is None
        assert schema["complexity_emergence_score"] is None

    def test_optional_valid_status_kept(self):
        results = _canonical_results()
        results["complexity_emergence_score"] = MetricResult(
            value=1.5, ci95=(1.3, 1.7), status="validated"
        )
        schema = metrics_to_schema(results)
        assert schema["complexity_emergence_score"]["value"] == pytest.approx(1.5)


class TestCi95Canonicalization:
    def test_inverted_ci95_swapped(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(value=0.5, ci95=(0.6, 0.4), status="validated")
        schema = metrics_to_schema(results)
        assert schema["structure_score"]["ci95"] == [0.4, 0.6]

    def test_extras_passed_through(self):
        schema = metrics_to_schema(_canonical_results())
        assert schema["structure_score"]["extras"] == {"k": 1}


class TestErrorBranches:
    def test_missing_core_metric_raises_keyerror(self):
        with pytest.raises(KeyError):
            metrics_to_schema({"total_correlation": MetricResult(value=0.0, status="validated")})

    def test_non_finite_value_raises_valueerror(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(value=float("inf"), status="validated")
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_missing_value_field_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(status="validated")  # type: ignore[typeddict-item]
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_missing_status_field_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(value=0.3)  # type: ignore[typeddict-item]
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_non_numeric_value_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(value="bad", status="validated")  # type: ignore[typeddict-item]
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_invalid_status_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(value=0.3, status="totally_made_up")  # type: ignore[typeddict-item]
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_malformed_ci95_length_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(
            value=0.3,
            ci95=(0.1, 0.2, 0.3),
            status="validated",  # type: ignore[arg-type]
        )
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_non_finite_ci95_bound_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(
            value=0.3, ci95=(0.1, float("nan")), status="validated"
        )
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_non_numeric_ci95_bound_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(
            value=0.3,
            ci95=("a", "b"),
            status="validated",  # type: ignore[arg-type]
        )
        with pytest.raises(ValueError):
            metrics_to_schema(results)

    def test_extras_non_dict_raises(self):
        results = _canonical_results()
        results["structure_score"] = MetricResult(
            value=0.3,
            status="validated",
            extras=["not", "a", "dict"],  # type: ignore[typeddict-item]
        )
        with pytest.raises(ValueError):
            metrics_to_schema(results)


class TestValidateSchemaOutput:
    def test_valid_passes(self):
        schema = metrics_to_schema(_canonical_results())
        assert validate_schema_output(schema) is True

    def test_wrong_version_raises(self):
        schema = metrics_to_schema(_canonical_results())
        schema["schema_version"] = "2.0"
        with pytest.raises(ValueError):
            validate_schema_output(schema)

    def test_missing_required_field_raises(self):
        schema = metrics_to_schema(_canonical_results())
        del schema["structure_score"]
        with pytest.raises(ValueError):
            validate_schema_output(schema)

    def test_required_field_not_dict_raises(self):
        schema = metrics_to_schema(_canonical_results())
        schema["structure_score"] = 0.3  # type: ignore[assignment]
        with pytest.raises(ValueError):
            validate_schema_output(schema)

    def test_required_field_missing_value_subfield_raises(self):
        schema = metrics_to_schema(_canonical_results())
        schema["structure_score"] = {"status": "validated"}
        with pytest.raises(ValueError):
            validate_schema_output(schema)

    def test_required_field_missing_status_subfield_raises(self):
        schema = metrics_to_schema(_canonical_results())
        schema["structure_score"] = {"value": 0.3}
        with pytest.raises(ValueError):
            validate_schema_output(schema)

    def test_optional_field_not_dict_raises(self):
        schema = metrics_to_schema(_canonical_results())
        schema["pathway_persistence"] = 0.5  # type: ignore[assignment]
        with pytest.raises(ValueError):
            validate_schema_output(schema)

    def test_optional_field_none_ok(self):
        schema = metrics_to_schema(_canonical_results())
        schema["pathway_persistence"] = None
        assert validate_schema_output(schema) is True


class TestFieldMapping:
    def test_mapping_contains_canonical_and_aliases(self):
        mapping = get_schema_field_mapping()
        assert mapping["structure_score"] == "structure_score"
        assert mapping["asymmetry_index"] == "structure_score"
        assert mapping["pathway_concentration_ratio"] == "concentration_index"
        assert mapping["temporal_pathway_stability"] == "pathway_persistence"

    def test_mapping_stable(self):
        assert get_schema_field_mapping() == get_schema_field_mapping()
