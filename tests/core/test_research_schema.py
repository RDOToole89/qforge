import json

from src.utils.schema import validate_results_schema


def test_validate_minimal_schema_passes():
    data = {
        "schema_version": "1.0.0",
        "experiment_metadata": {
            "experiment_id": "abc",
            "timestamp": "2025-01-01T00:00:00",
            "framework_version": "2.0.0",
            "research_type": "structured_decoherence",
        },
        "experiment_parameters": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "shots": 1024,
            "sim_mode": "qasm",
        },
        "measurement_results": {"raw_counts": {"000": 1}, "total_shots": 1},
    }
    assert validate_results_schema(data)


def test_validate_missing_field_raises():
    data = {
        "schema_version": "1.0.0",
        # "experiment_metadata": {},  # missing on purpose
        "experiment_parameters": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "shots": 1,
            "sim_mode": "qasm",
        },
        "measurement_results": {"raw_counts": {}, "total_shots": 0},
    }
    try:
        validate_results_schema(data)
        assert False, "Expected ValueError for missing experiment_metadata"
    except ValueError:
        pass
