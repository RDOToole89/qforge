from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def generate_markdown_report(analysis: Dict[str, Any]) -> str:
    meta = analysis.get("experiment_metadata", {})
    params = analysis.get("experiment_parameters", {})
    metrics = analysis.get("research_metrics", {})

    lines = []
    lines.append(f"# Experiment Report: {meta.get('experiment_id', 'N/A')}")
    lines.append("")
    lines.append(f"- Timestamp: {meta.get('timestamp')}")
    lines.append(f"- Research type: {meta.get('research_type')}")
    lines.append("")
    lines.append("## Parameters")
    for k in [
        "num_qubits",
        "state_type",
        "noise_type",
        "noise_enabled",
        "error_rate",
        "shots",
        "sim_mode",
    ]:
        if k in params:
            lines.append(f"- {k}: {params[k]}")
    lines.append("")
    lines.append("## Key Metrics")
    info = metrics.get("information_theory", {})
    if info:
        for mk in ["shannon_entropy", "normalized_entropy"]:
            if mk in info:
                lines.append(f"- {mk}: {info[mk]}")
    if "distribution_comparison" in metrics:
        dc = metrics["distribution_comparison"]
        for mk in ["tvd", "kl_divergence"]:
            if mk in dc:
                lines.append(f"- {mk}: {dc[mk]}")
    lines.append("")
    lines.append("## Provenance")
    prov = analysis.get("provenance", {})
    if prov:
        for k, v in prov.items():
            lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def save_report_from_json(json_path: str, fmt: str = "md") -> str:
    with open(json_path, "r") as f:
        analysis = json.load(f)
    if fmt == "md":
        content = generate_markdown_report(analysis)
        out = Path(json_path).with_suffix("")
        out = out.as_posix() + "_report.md"
        Path(out).write_text(content)
        return out
    raise ValueError(f"Unsupported report format: {fmt}")
