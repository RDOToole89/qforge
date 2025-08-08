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
    if fmt == "html":
        # Simple HTML without external deps
        meta = analysis.get("experiment_metadata", {})
        params = analysis.get("experiment_parameters", {})
        metrics = analysis.get("research_metrics", {})
        prov = analysis.get("provenance", {})
        html = [
            "<html><head><meta charset='utf-8'><title>Experiment Report</title>",
            "<style>body{font-family:Arial,Helvetica,sans-serif;margin:24px} h1,h2{color:#222} table{border-collapse:collapse} td,th{border:1px solid #ddd;padding:6px}</style>",
            "</head><body>",
            f"<h1>Experiment Report: {meta.get('experiment_id','N/A')}</h1>",
            f"<p><b>Timestamp:</b> {meta.get('timestamp','')}</p>",
            f"<p><b>Research type:</b> {meta.get('research_type','')}</p>",
            "<h2>Parameters</h2><table>",
        ]
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
                html.append(f"<tr><th>{k}</th><td>{params[k]}</td></tr>")
        html.append("</table>")
        html.append("<h2>Key Metrics</h2><table>")
        info = metrics.get("information_theory", {})
        if info:
            for mk in ["shannon_entropy", "normalized_entropy"]:
                if mk in info:
                    html.append(f"<tr><th>{mk}</th><td>{info[mk]}</td></tr>")
        if "distribution_comparison" in metrics:
            dc = metrics["distribution_comparison"]
            for mk in ["tvd", "kl_divergence"]:
                if mk in dc:
                    html.append(f"<tr><th>{mk}</th><td>{dc[mk]}</td></tr>")
        html.append("</table>")
        if prov:
            html.append("<h2>Provenance</h2><table>")
            for k, v in prov.items():
                html.append(
                    f"<tr><th>{k}</th><td><pre>{json.dumps(v, indent=2)}</pre></td></tr>"
                )
            html.append("</table>")
        html.append("</body></html>")
        out = Path(json_path).with_suffix("")
        out = out.as_posix() + "_report.html"
        Path(out).write_text("\n".join(html))
        return out
    raise ValueError(f"Unsupported report format: {fmt}")
