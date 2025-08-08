from pathlib import Path
import json

from src.visualization.pipeline.run import render_from_json


def test_pipeline_render_from_json_histogram(tmp_path: Path):
    analysis = {
        "experiment_parameters": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
        },
        "measurement_results": {"raw_counts": {"000": 50, "111": 50}},
    }
    p = tmp_path / "analysis.json"
    p.write_text(json.dumps(analysis), encoding="utf-8")

    artifact = render_from_json(
        str(p),
        viz_type="histogram",
        backend="matplotlib",
        output_base_dir=str(tmp_path / "out"),
    )
    assert artifact.kind == "histogram"
    assert Path(artifact.path).exists()
