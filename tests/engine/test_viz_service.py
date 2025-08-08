# tests/engine/test_viz_service.py

import json
from pathlib import Path

from src.engine.viz_service import VisualizationService, VisualizationRequest


def _dummy_analysis(tmp_path: Path) -> Path:
    analysis = {
        "experiment_parameters": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "error_rate": 0.05,
        },
        "measurement_results": {
            "raw_counts": {"000": 500, "111": 500}
        },
        "research_metrics": {
            "information_theory": {"shannon_entropy": 1.0, "normalized_entropy": 0.5}
        },
    }
    p = tmp_path / "analysis.json"
    p.write_text(json.dumps(analysis), encoding="utf-8")
    return p


def test_viz_service_histogram_saves_artifact(tmp_path):
    json_path = _dummy_analysis(tmp_path)

    svc = VisualizationService()
    req = VisualizationRequest(viz_type="histogram", output_base_dir=str(tmp_path / "viz_out"))
    artifact = svc.render_from_json(str(json_path), request=req)

    assert artifact.kind == "histogram"
    assert artifact.path.endswith(".png")
    out = Path(artifact.path)
    assert out.exists(), f"Expected saved artifact at {artifact.path}"