import json
import os
from pathlib import Path


def _fake_analysis(tmp_path: Path) -> str:
    payload = {
        "schema_version": "1.0.0",
        "experiment_metadata": {
            "experiment_id": "test-experiment",
            "timestamp": "2025-01-01T00:00:00",
            "framework_version": "2.0.0",
            "research_type": "structured_decoherence",
        },
        "experiment_parameters": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "error_rate": 0.05,
            "shots": 128,
            "sim_mode": "qasm",
            "multiple_runs": 1,
        },
        "circuit_statistics": {
            "depth": 3,
            "num_gates": 3,
            "num_qubits": 3,
            "gate_types": {"h": 1},
        },
        "measurement_results": {
            "raw_counts": {"000": 64, "111": 64},
            "total_shots": 128,
            "unique_outcomes": 2,
            "outcome_probabilities": {"000": 0.5, "111": 0.5},
        },
        "research_metrics": {
            "information_theory": {"shannon_entropy": 1.0, "normalized_entropy": 1.0},
        },
    }
    p = tmp_path / "analysis.json"
    with open(p, "w") as f:
        json.dump(payload, f)
    return str(p)


def test_visualize_histogram_from_json(tmp_path, monkeypatch):
    # Ensure results dir exists for auto-save
    os.makedirs("results/visualizations/histograms", exist_ok=True)
    path = _fake_analysis(tmp_path)
    from main import visualize_from_json

    # Should not raise
    visualize_from_json(path, "histogram")


def test_visualize_hypergraph_from_json(tmp_path):
    path = _fake_analysis(tmp_path)
    from main import visualize_from_json

    # Should not raise (uses counts as correlation_data)
    visualize_from_json(path, "hypergraph")
