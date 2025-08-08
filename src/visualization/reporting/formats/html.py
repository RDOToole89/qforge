from __future__ import annotations

from typing import Dict, Any
import json


def render_html(ctx: Dict[str, Any]) -> str:
    meta = ctx.get("meta", {})
    params = ctx.get("params", {})
    metrics = ctx.get("metrics", {})
    provenance = ctx.get("provenance", {})

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
    if provenance:
        html.append("<h2>Provenance</h2><table>")
        for k, v in provenance.items():
            html.append(
                f"<tr><th>{k}</th><td><pre>{json.dumps(v, indent=2)}</pre></td></tr>"
            )
        html.append("</table>")
    html.append("</body></html>")
    return "\n".join(html)
