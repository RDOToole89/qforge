from src.utils.schema import validate_manifest_schema


def test_manifest_validates_minimal():
    manifest = {
        "base_preset": "ghz_structured_decoherence_ref",
        "parameter_ranges": {"error_rate": [0.01, 0.05]},
        "runs_per_config": 1,
    }
    assert validate_manifest_schema(manifest)


def test_manifest_missing_required_raises():
    bad = {"parameter_ranges": {}, "runs_per_config": 1}
    try:
        validate_manifest_schema(bad)
        assert False, "Expected ValueError for missing base_preset"
    except ValueError:
        pass
