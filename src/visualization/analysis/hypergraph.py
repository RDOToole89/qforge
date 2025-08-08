from __future__ import annotations

from typing import Mapping, Tuple, Dict, Any
import numpy as np


def determine_mode_and_qubits(
    correlation_data: Mapping[str, Any],
) -> Tuple[str, int, float]:
    if not correlation_data:
        return "qasm", 1, 0.0
    if "density" in correlation_data:
        dm = np.array(correlation_data["density"])
        num_qubits = int(np.log2(dm.shape[0])) if dm.size else 1
        return "density", num_qubits, 1.0
    first_key = next(iter(correlation_data.keys()))
    num_qubits = len(first_key) if isinstance(first_key, str) else 1
    try:
        shots = float(sum(float(v) for v in correlation_data.values()))
    except Exception:
        shots = 0.0
    return "qasm", num_qubits, shots


def build_hypergraph_edges(
    correlation_data: Mapping[str, Any],
    *,
    config: Mapping[str, Any] | None = None,
) -> Dict:
    from src.core.analysis import compute_correlations_for_hypergraph

    cfg = dict(config or {})
    mode, num_qubits, _ = determine_mode_and_qubits(correlation_data)
    return compute_correlations_for_hypergraph(correlation_data, num_qubits, mode, cfg)
