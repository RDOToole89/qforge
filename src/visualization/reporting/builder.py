from __future__ import annotations

from typing import Any, Dict


def build_report_context(analysis: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "meta": analysis.get("experiment_metadata", {}),
        "params": analysis.get("experiment_parameters", {}),
        "metrics": analysis.get("research_metrics", {}),
        "provenance": analysis.get("provenance", {}),
    }