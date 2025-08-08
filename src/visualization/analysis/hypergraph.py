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
    top_k_fallback: int = 3,
    min_abs_weight: float = 1e-3,
) -> Dict:
    from src.core.analysis import compute_correlations_for_hypergraph

    cfg = dict(config or {})
    mode, num_qubits, _ = determine_mode_and_qubits(correlation_data)
    edges = compute_correlations_for_hypergraph(correlation_data, num_qubits, mode, cfg)
    if edges:
        return edges

    # Fallback: select top-k strongest pairwise correlations if no edges survived
    try:
        from src.core.analysis import compute_pairwise_correlations

        pair = compute_pairwise_correlations(correlation_data, num_qubits, mode, 1.0)
        # pair expected as matrix-like or dict-of-dicts; normalize to list of (i,j,weight)
        pairs: list[tuple[int, int, float]] = []
        if isinstance(pair, dict):
            for i, row in pair.items():
                for j, w in row.items():
                    if j > i:
                        pairs.append((int(i), int(j), float(w)))
        else:
            # assume square matrix-like
            for i in range(num_qubits):
                for j in range(i + 1, num_qubits):
                    w = float(pair[i][j])
                    pairs.append((i, j, w))
        pairs.sort(key=lambda t: abs(t[2]), reverse=True)
        selected = [(i, j, w) for i, j, w in pairs if abs(w) >= min_abs_weight][
            :top_k_fallback
        ]
        fallback_edges: Dict[str, tuple[tuple[str, ...], dict]] = {}
        for idx, (i, j, w) in enumerate(selected):
            nodes = (f"q{i}", f"q{j}")
            fallback_edges[f"e{idx}"] = (nodes, {"weight": w, "fallback": True})
        return fallback_edges
    except Exception:
        return {}
