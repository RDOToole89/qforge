from src.visualization.pipeline.transform import (
    extract_counts_from_analysis,
    normalize_counts,
    filter_viz_params,
)


def test_extract_counts_from_analysis_handles_raw_and_counts():
    a1 = {"measurement_results": {"raw_counts": {"0": 1, "1": 1}}}
    a2 = {"measurement_results": {"counts": {"0": 2, "1": 2}}}
    assert extract_counts_from_analysis(a1) == {"0": 1.0, "1": 1.0}
    assert extract_counts_from_analysis(a2) == {"0": 2.0, "1": 2.0}


def test_normalize_counts():
    counts = {"000": 50.0, "111": 50.0}
    norm = normalize_counts(counts)
    assert abs(norm["000"] - 0.5) < 1e-9
    assert abs(norm["111"] - 0.5) < 1e-9


def test_filter_viz_params_defaults_and_passthrough():
    params = {"state_type": "GHZ", "num_qubits": 3}
    filtered = filter_viz_params(params)
    assert filtered["state_type"] == "GHZ"
    assert filtered["num_qubits"] == 3
    assert "noise_enabled" in filtered
