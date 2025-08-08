from pathlib import Path
import json

from src.visualization.report import save_report_from_json


def test_reporting_writes_md_and_html(tmp_path: Path):
    analysis = {
        "experiment_metadata": {"experiment_id": "demo-1", "timestamp": "now"},
        "experiment_parameters": {"num_qubits": 3, "state_type": "GHZ"},
        "research_metrics": {
            "information_theory": {"shannon_entropy": 1.0, "normalized_entropy": 0.5}
        },
    }
    p = tmp_path / "analysis.json"
    p.write_text(json.dumps(analysis), encoding="utf-8")

    md = save_report_from_json(str(p), fmt="md")
    html = save_report_from_json(str(p), fmt="html")

    assert Path(md).exists()
    assert Path(html).exists()
    assert "Experiment Report" in Path(md).read_text(encoding="utf-8")
    assert "<html>" in Path(html).read_text(encoding="utf-8")
