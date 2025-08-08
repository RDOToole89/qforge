from __future__ import annotations

from typing import Mapping, Any, Dict


def extract_counts_from_analysis(analysis: Mapping[str, Any]) -> Dict[str, float]:
    mm = analysis.get("measurement_results", {}) if isinstance(analysis, dict) else {}
    counts = mm.get("raw_counts") or mm.get("counts") or {}
    if not isinstance(counts, dict):
        return {}
    # Convert to {str: float}
    out: Dict[str, float] = {}
    for k, v in counts.items():
        try:
            out[str(k)] = float(v)
        except Exception:
            continue
    return out


def normalize_counts(counts: Mapping[str, float]) -> Dict[str, float]:
    if not counts:
        return {}
    total = sum(float(v) for v in counts.values())
    if total <= 0:
        return {str(k): 0.0 for k in counts}
    return {str(k): float(v) / total for k, v in counts.items()}


def filter_viz_params(params: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a minimal, safe param dict for organizing outputs.

    Keeps common keys and applies simple defaults.
    """
    keep = {
        "state_type": None,
        "noise_type": None,
        "noise_enabled": True,
        "num_qubits": 1,
        "error_rate": None,
    }
    out: Dict[str, Any] = {}
    for key, default in keep.items():
        value = params.get(key) if isinstance(params, dict) else default
        out[key] = value if value is not None else default
    return out
