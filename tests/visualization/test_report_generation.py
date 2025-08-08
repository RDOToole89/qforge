import json
from pathlib import Path


def test_generate_markdown_report_from_results(tmp_path):
    analysis = {
        "schema_version": "1.0.0",
        "experiment_metadata": {
            "experiment_id": "abc12345",
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
        },
        "measurement_results": {
            "raw_counts": {"000": 64, "111": 64},
            "total_shots": 128,
        },
        "research_metrics": {
            "information_theory": {"shannon_entropy": 1.0, "normalized_entropy": 0.5},
            "distribution_comparison": {"tvd": 0.1, "kl_divergence": 0.01},
        },
        "provenance": {"software_versions": {"python": "3.13"}},
    }
    json_path = tmp_path / "analysis.json"
    json_path.write_text(json.dumps(analysis))

    from src.visualization.report import save_report_from_json

    out = save_report_from_json(str(json_path), fmt="md")
    outp = Path(out)
    assert outp.exists()
    content = outp.read_text()
    assert "Experiment Report" in content and "Key Metrics" in content
