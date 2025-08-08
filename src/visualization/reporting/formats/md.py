from __future__ import annotations

from typing import Dict, Any


def render_markdown(ctx: Dict[str, Any]) -> str:
    meta = ctx.get("meta", {})
    params = ctx.get("params", {})
    metrics = ctx.get("metrics", {})
    provenance = ctx.get("provenance", {})

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
    if provenance:
        for k, v in provenance.items():
            lines.append(f"- {k}: {v}")
    return "\n".join(lines)