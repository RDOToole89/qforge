from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple
import math


def ideal_distribution(state_type: Optional[str], num_qubits: int) -> Dict[str, float]:
    if not state_type:
        return {}
    st = str(state_type).upper()
    size = 2**num_qubits
    if st == "GHZ":
        a = "0" * num_qubits
        b = "1" * num_qubits
        return {
            format(i, f"0{num_qubits}b"): (
                0.5 if format(i, f"0{num_qubits}b") in {a, b} else 0.0
            )
            for i in range(size)
        }
    if st == "W":
        w = {format(1 << i, f"0{num_qubits}b") for i in range(num_qubits)}
        p = 1.0 / num_qubits
        return {
            format(i, f"0{num_qubits}b"): (
                p if format(i, f"0{num_qubits}b") in w else 0.0
            )
            for i in range(size)
        }
    if st == "CLUSTER":
        p = 1.0 / size
        return {format(i, f"0{num_qubits}b"): p for i in range(size)}
    return {}


def expected_set(state_type: Optional[str], num_qubits: int) -> set[str]:
    if not state_type:
        return set()
    st = str(state_type).upper()
    if st == "GHZ":
        return {"0" * num_qubits, "1" * num_qubits}
    if st == "W":
        return {format(1 << i, f"0{num_qubits}b") for i in range(num_qubits)}
    if st == "CLUSTER":
        return {format(i, f"0{num_qubits}b") for i in range(2**num_qubits)}
    return set()


def counts_to_probabilities(
    counts: Mapping[str, int],
) -> Tuple[List[str], List[float], int, List[int]]:
    states = sorted(counts.keys())
    shot_counts = [int(counts[s]) for s in states]
    shots = sum(shot_counts) if shot_counts else 0
    probs = [c / shots if shots else 0.0 for c in shot_counts]
    return states, probs, shots, shot_counts


def binomial_ci(p: float, shots: int, z: float = 1.96) -> Tuple[float, float]:
    if shots <= 0:
        return (0.0, 0.0)
    sigma = math.sqrt(max(p * (1 - p), 0.0) / shots)
    return max(0.0, p - z * sigma), min(1.0, p + z * sigma)


def prepare_histogram_data(
    counts: Mapping[str, int],
    *,
    state_type: Optional[str],
    num_qubits: int,
    shots: Optional[int] = None,
    include_ci: bool = True,
) -> Dict[str, object]:
    states, probs, shots_auto, shot_counts = counts_to_probabilities(counts)
    shots_eff = int(shots if shots is not None else shots_auto)
    ideal = ideal_distribution(state_type, num_qubits)
    ideals = [ideal.get(s, 0.0) for s in states]
    deltas = [probs[i] - ideals[i] for i in range(len(states))]
    ci_low: List[float] = []
    ci_high: List[float] = []
    z_scores: List[float] = []
    if include_ci:
        for p, d in zip(probs, deltas):
            lo, hi = binomial_ci(p, shots_eff) if shots_eff > 0 else (p, p)
            ci_low.append(lo)
            ci_high.append(hi)
            sigma = (
                math.sqrt(max(p * (1 - p), 0.0) / shots_eff) if shots_eff > 0 else 0.0
            )
            z_scores.append(d / sigma if sigma > 0 else 0.0)
    exp = expected_set(state_type, num_qubits)
    expected_mask = [s in exp for s in states]
    return {
        "states": states,
        "probabilities": probs,
        "counts": shot_counts,
        "shots": shots_eff,
        "ideal": ideals,
        "delta": deltas,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "z": z_scores,
        "expected_mask": expected_mask,
    }
