"""
Balanced Topology Comparison Experiment

Compares decoherence across topologies (GHZ, W, Cluster) with:
- Circuit depth balancing (gate_count padding)
- State-aware null model (proper baseline)
- EEC permutation test (significance testing)
- Correlated noise comparison (definitive hypothesis test)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from itertools import permutations as iter_permutations
from math import factorial
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import pearsonr

from src.core.analysis.core.null_models import state_aware_null_model
from src.core.analysis.metrics.entanglement_error_correlation import (
    PermutationTestResult,
    eec_permutation_test,
)
from src.engine.execution.context import AppContext
from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment

logger = logging.getLogger(__name__)


class BalancedTopologyComparison(BaseExperiment):
    """Compare decoherence across topologies with balanced circuits and proper nulls."""

    name = "balanced_topology"
    description = "Compare decoherence across topologies with balanced circuits and proper nulls"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=8192,
            balance_circuit="gate_count",
            metrics="structured_decoherence",
        )

    def run_comparison(
        self,
        num_qubits: int = 4,
        error_rate: float = 0.05,
        shots: int = 8192,
        rng_seed: int | None = None,
        ctx: AppContext | None = None,
    ) -> dict[str, ExperimentResult]:
        """Run balanced experiments across GHZ, W, and Cluster topologies."""
        results: dict[str, ExperimentResult] = {}

        for state_type in ("GHZ", "W", "CLUSTER"):
            result = self.run({
                "num_qubits": num_qubits,
                "state_type": state_type,
                "error_rate": error_rate,
                "shots": shots,
                "balance_circuit": "gate_count",
                "rng_seed": rng_seed,
            }, ctx=ctx)
            results[state_type] = result

        return results

    def run_with_null_comparison(
        self,
        num_qubits: int = 4,
        error_rate: float = 0.05,
        shots: int = 10000,
        rng_seed: int | None = None,
        n_permutations: int = 1000,
    ) -> dict[str, dict[str, Any]]:
        """Run comparison with state-aware null model and EEC permutation test.

        Returns dict keyed by state_type with:
        - result: ExperimentResult
        - state_aware_null: dict of expected probabilities
        - excess_structure_jsd: JSD(observed || state_aware_null)
        - permutation_test: PermutationTestResult
        """
        now = datetime.now()
        session_id = f"null_comparison_{now.strftime('%H%M%S')}"
        ctx = AppContext(session_id=session_id)

        rng = np.random.default_rng(rng_seed)
        output: dict[str, dict[str, Any]] = {}

        for state_type in ("GHZ", "W", "CLUSTER"):
            # Run experiment with balanced circuit
            result = self.run({
                "num_qubits": num_qubits,
                "state_type": state_type,
                "error_rate": error_rate,
                "shots": shots,
                "balance_circuit": "gate_count",
                "rng_seed": int(rng.integers(0, 2**31)),
            }, ctx=ctx)

            counts = result.analysis.measurement_results.raw_counts

            # Compute state-aware null
            null_dist = state_aware_null_model(
                state_type=state_type,
                num_qubits=num_qubits,
                error_rate=error_rate,
            )

            # Compute JSD(observed || state_aware_null)
            excess_jsd = _jsd_from_counts(counts, null_dist)

            # EEC permutation test
            perm_result = eec_permutation_test(
                counts,
                state_type=state_type,
                n_permutations=n_permutations,
                rng=rng,
            )

            output[state_type] = {
                "result": result,
                "state_aware_null": null_dist,
                "excess_structure_jsd": excess_jsd,
                "permutation_test": perm_result,
            }

            logger.info(
                f"{state_type}: EEC={perm_result.observed:.3f}, "
                f"p={perm_result.p_value:.3f}, "
                f"excess_JSD={excess_jsd:.6f}"
            )

        # Save session summary
        session_dir = Path(ctx.base_results_dir) / now.strftime("%Y%m%d") / _slug(session_id)
        conditions = {}
        for state_type, data in output.items():
            perm = data["permutation_test"]
            conditions[state_type] = {
                "eec": round(perm.observed, 4),
                "eec_p_value": round(perm.p_value, 4),
                "eec_significant": perm.p_value < 0.05,
                "excess_jsd": round(data["excess_structure_jsd"], 6),
            }

        _save_session_summary(
            session_dir=session_dir,
            session_id=session_id,
            experiment="null_model_comparison",
            timestamp=now,
            parameters={
                "num_qubits": num_qubits,
                "error_rate": error_rate,
                "shots": shots,
                "n_permutations": n_permutations,
                "topologies": ["GHZ", "W", "CLUSTER"],
            },
            conditions=conditions,
            readme_header="Null Model Comparison",
            readme_description=(
                f"- Topologies: GHZ, W, Cluster ({num_qubits} qubits)\n"
                f"- Error rate: {error_rate}, Shots: {shots}\n"
                f"- Permutations: {n_permutations}"
            ),
            columns=["Topology", "EEC", "p-value", "Significant", "Excess JSD"],
            row_fn=lambda name, d: (
                f"| {name} | {d['eec']:+.3f} | {d['eec_p_value']:.3f} "
                f"| {'Yes' if d['eec_significant'] else 'No'} | {d['excess_jsd']:.6f} |"
            ),
        )

        return output

    def run_correlated_comparison(
        self,
        num_qubits: int = 4,
        error_rate: float = 0.05,
        shots: int = 10000,
        correlation_strength: float = 0.3,
        rng_seed: int | None = None,
        n_permutations: int = 1000,
    ) -> dict[str, dict[str, Any]]:
        """Run the definitive test: correlated vs independent vs anti-correlated noise.

        Runs GHZ state under three noise conditions:
        1. aligned: correlation_strength > 0 (topology-correlated errors)
        2. independent: correlation_strength = 0 (standard depolarizing)
        3. anti_aligned: correlation_strength < 0 (anti-correlated errors)

        Uses the Noise Topology Correlation (NTC) metric that specifically measures
        correlation between the circuit topology adjacency and pairwise error
        covariance. This isolates noise-induced correlations from state-inherent
        correlations that dominate the standard EEC (MI-based) metric.

        Expected results if framework is correct:
        - aligned: NTC > 0 (errors correlated along topology edges)
        - independent: NTC ~ 0 (no topology-dependent noise correlation)
        - anti_aligned: NTC < 0 (errors anti-correlated along topology edges)
        """
        from src.engine.api import run

        now = datetime.now()
        session_id = f"correlated_comparison_{now.strftime('%H%M%S')}"
        ctx = AppContext(session_id=session_id)

        rng = np.random.default_rng(rng_seed)
        output: dict[str, dict[str, Any]] = {}

        conditions = {
            "aligned": correlation_strength,
            "independent": 0.0,
            "anti_aligned": -correlation_strength,
        }

        # Run all conditions and collect counts
        all_counts: dict[str, dict[str, int]] = {}
        all_results: dict[str, ExperimentResult] = {}

        for condition_name, cs in conditions.items():
            seed = int(rng.integers(0, 2**31))

            if abs(cs) < 1e-10:
                config = ExperimentConfig(
                    num_qubits=num_qubits,
                    state_type="GHZ",
                    noise_enabled=True,
                    noise_type="depolarizing",
                    error_rate=error_rate,
                    shots=shots,
                    balance_circuit="gate_count",
                    metrics="structured_decoherence",
                    rng_seed=seed,
                )
            else:
                config = ExperimentConfig(
                    num_qubits=num_qubits,
                    state_type="GHZ",
                    noise_enabled=True,
                    noise_type="correlated_depolarizing",
                    error_rate=error_rate,
                    shots=shots,
                    balance_circuit="gate_count",
                    metrics="structured_decoherence",
                    rng_seed=seed,
                    custom_params={
                        "correlation_strength": cs,
                        "topology": "GHZ",
                    },
                )

            result = run(config, ctx=ctx)
            all_results[condition_name] = result
            all_counts[condition_name] = result.analysis.measurement_results.raw_counts

        # Use the independent condition as baseline for NTC
        baseline_counts = all_counts["independent"]

        for condition_name, cs in conditions.items():
            counts = all_counts[condition_name]

            # Standard EEC (MI-based) — for reference
            perm_result = eec_permutation_test(
                counts,
                state_type="GHZ",
                n_permutations=n_permutations,
                rng=rng,
            )

            # Noise Topology Correlation — excess covariance selectivity
            ntc_result = _noise_topology_correlation(
                counts,
                baseline_counts,
                state_type="GHZ",
                n_qubits=num_qubits,
                n_permutations=n_permutations,
                rng=rng,
            )

            output[condition_name] = {
                "result": all_results[condition_name],
                "correlation_strength": cs,
                "permutation_test": perm_result,
                "noise_topology_correlation": ntc_result,
            }

            logger.info(
                f"{condition_name} (cs={cs:.2f}): "
                f"EEC={perm_result.observed:.3f}, "
                f"NTC={ntc_result['observed']:.4f}, "
                f"NTC_p={ntc_result['p_value']:.3f}, "
                f"NTC_sig={ntc_result['significant']}"
            )

        # Save session summary
        session_dir = Path(ctx.base_results_dir) / now.strftime("%Y%m%d") / _slug(session_id)
        summary_conditions = {}
        for condition_name, data in output.items():
            ntc = data["noise_topology_correlation"]
            perm = data["permutation_test"]
            summary_conditions[condition_name] = {
                "correlation_strength": round(data["correlation_strength"], 2),
                "ntc": round(ntc["observed"], 4),
                "ntc_p_value": round(ntc["p_value"], 4),
                "ntc_significant": ntc["significant"],
                "ntc_effect_size": round(ntc["effect_size"], 2),
                "eec": round(perm.observed, 4),
            }

        _save_session_summary(
            session_dir=session_dir,
            session_id=session_id,
            experiment="correlated_noise_comparison",
            timestamp=now,
            parameters={
                "num_qubits": num_qubits,
                "error_rate": error_rate,
                "correlation_strength": correlation_strength,
                "shots": shots,
                "n_permutations": n_permutations,
            },
            conditions=summary_conditions,
            readme_header="Correlated Noise Comparison",
            readme_description=(
                f"- State: GHZ, {num_qubits} qubits\n"
                f"- Error rate: {error_rate:.2f}, Shots: {shots}\n"
                f"- Correlation strength: +/-{correlation_strength:.2f}"
            ),
            columns=["Condition", "cs", "NTC", "p-value", "Significant", "Effect Size", "EEC"],
            row_fn=lambda name, d: (
                f"| {name} | {d['correlation_strength']:+.2f} | {d['ntc']:+.4f} "
                f"| {d['ntc_p_value']:.3f} | {'Yes' if d['ntc_significant'] else 'No'} "
                f"| {d['ntc_effect_size']:+.2f} | {d['eec']:.3f} |"
            ),
        )

        return output


def _slug(text: str) -> str:
    """Filesystem-safe token: letters, digits, underscore only; lower-cased."""
    import re
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_") or "unknown"


def _save_session_summary(
    *,
    session_dir: Path,
    session_id: str,
    experiment: str,
    timestamp: datetime,
    parameters: dict[str, Any],
    conditions: dict[str, dict[str, Any]],
    readme_header: str,
    readme_description: str,
    columns: list[str],
    row_fn: Any,
) -> None:
    """Write summary.json and README.md to a session directory.

    Wrapped in try/except so summary failure never crashes the experiment.
    """
    try:
        session_dir.mkdir(parents=True, exist_ok=True)

        # summary.json
        summary = {
            "session_id": session_id,
            "experiment": experiment,
            "timestamp": timestamp.isoformat(),
            "parameters": parameters,
            "conditions": conditions,
        }
        with open(session_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        # README.md
        header_sep = " | ".join("---" for _ in columns)
        header_row = "| " + " | ".join(columns) + " |"
        table_rows = [row_fn(name, data) for name, data in conditions.items()]

        # Count data files in session directory
        json_files = list(session_dir.glob("*.json"))
        json_count = len([f for f in json_files if f.name != "summary.json"])
        png_count = len(list(session_dir.glob("*.png")))

        readme = (
            f"# {readme_header} - {timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"## Parameters\n{readme_description}\n\n"
            f"## Results\n\n"
            f"{header_row}\n"
            f"| {header_sep} |\n"
            + "\n".join(table_rows)
            + "\n\n"
            f"## Files\n"
            f"- {json_count} individual result JSONs with histograms\n"
            f"- summary.json (machine-readable aggregate)\n"
        )
        with open(session_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme)

        logger.info(f"Session summary saved to {session_dir}")
    except Exception as e:
        logger.warning(f"Failed to save session summary: {e}")


def _jsd_from_counts(
    counts: dict[str, int], null_dist: dict[str, float]
) -> float:
    """Compute JSD between empirical counts and a probability distribution."""
    total = sum(counts.values())
    if total == 0:
        return 0.0

    # Align keys
    all_keys = sorted(set(counts.keys()) | set(null_dist.keys()))
    p = np.array([counts.get(k, 0) / total for k in all_keys])
    q = np.array([null_dist.get(k, 0.0) for k in all_keys])

    # Normalize q defensively
    q_sum = q.sum()
    if q_sum > 0:
        q = q / q_sum

    return float(jensenshannon(p, q, base=2) ** 2)  # JSD (squared JS distance)


def _chain_adjacency(n: int) -> np.ndarray:
    """Linear chain adjacency matrix (matches GHZ/Cluster circuit connectivity)."""
    W = np.zeros((n, n))
    for i in range(n - 1):
        W[i, i + 1] = W[i + 1, i] = 1.0
    return W


def _compute_bit_covariance_matrix(
    counts: dict[str, int],
    n_qubits: int,
) -> np.ndarray:
    """Compute pairwise bit covariance from measurement counts.

    Cov(b_i, b_j) = E[b_i * b_j] - E[b_i] * E[b_j]

    where b_i ∈ {0, 1} is the measured bit value for qubit i.

    This is symmetric for GHZ (all pairs have equal expected covariance
    under independent noise), so any deviation between pairs must come
    from correlated noise effects.
    """
    total = sum(counts.values())
    if total == 0:
        return np.zeros((n_qubits, n_qubits))

    b_mean = np.zeros(n_qubits)
    bb_mean = np.zeros((n_qubits, n_qubits))

    for bitstring, count in counts.items():
        b = np.array([float(bitstring[i]) for i in range(n_qubits)])
        weight = count / total
        b_mean += weight * b
        bb_mean += weight * np.outer(b, b)

    cov = bb_mean - np.outer(b_mean, b_mean)
    np.fill_diagonal(cov, 0.0)
    return cov


def _noise_topology_correlation(
    counts: dict[str, int],
    baseline_counts: dict[str, int],
    state_type: str,
    n_qubits: int,
    n_permutations: int = 1000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Compute Noise Topology Correlation (NTC) with permutation test.

    Measures whether EXCESS pairwise covariance (relative to a baseline with
    independent noise) concentrates on topology-adjacent qubit pairs.

    NTC = mean(excess_cov_adjacent) - mean(excess_cov_nonadjacent)

    This is the "topology selectivity" of the correlated noise effect.
    Positive NTC means noise correlations prefer topology-connected pairs.

    The permutation test shuffles qubit labels on the adjacency matrix to
    determine whether the observed selectivity is significant.

    Args:
        counts: Measurement counts from the condition being tested
        baseline_counts: Measurement counts from the independent noise baseline
        state_type: Quantum state type
        n_qubits: Number of qubits
        n_permutations: Permutation count for significance test
        alpha: Significance threshold
        rng: Random generator for reproducibility

    Returns dict with: observed, p_value, significant, effect_size,
        adj_excess_mean, nonadj_excess_mean
    """
    if rng is None:
        rng = np.random.default_rng()

    W = _chain_adjacency(n_qubits)
    mask = np.triu(np.ones((n_qubits, n_qubits), dtype=bool), k=1)
    w_flat = W[mask]
    adj_idx = w_flat > 0.5

    # Compute covariance matrices
    cov_obs = _compute_bit_covariance_matrix(counts, n_qubits)
    cov_base = _compute_bit_covariance_matrix(baseline_counts, n_qubits)

    # Excess covariance
    excess = cov_obs - cov_base
    excess_flat = excess[mask]

    # Observed NTC: topology selectivity
    adj_mean = float(np.mean(excess_flat[adj_idx]))
    nonadj_mean = float(np.mean(excess_flat[~adj_idx]))
    observed = adj_mean - nonadj_mean

    # Permutation test: shuffle qubit labels on adjacency, recompute selectivity
    n_fact = factorial(n_qubits)
    exhaustive = n_fact <= n_permutations

    null_ntcs: list[float] = []

    if exhaustive:
        for perm in iter_permutations(range(n_qubits)):
            perm_arr = np.array(perm)
            W_perm = W[np.ix_(perm_arr, perm_arr)]
            w_perm_flat = W_perm[mask]
            adj_perm = w_perm_flat > 0.5
            if adj_perm.sum() == 0 or (~adj_perm).sum() == 0:
                null_ntcs.append(0.0)
            else:
                null_ntcs.append(
                    float(np.mean(excess_flat[adj_perm]) - np.mean(excess_flat[~adj_perm]))
                )
    else:
        for _ in range(n_permutations):
            perm_arr = rng.permutation(n_qubits)
            W_perm = W[np.ix_(perm_arr, perm_arr)]
            w_perm_flat = W_perm[mask]
            adj_perm = w_perm_flat > 0.5
            if adj_perm.sum() == 0 or (~adj_perm).sum() == 0:
                null_ntcs.append(0.0)
            else:
                null_ntcs.append(
                    float(np.mean(excess_flat[adj_perm]) - np.mean(excess_flat[~adj_perm]))
                )

    null_array = np.array(null_ntcs)
    p_value = float(np.mean(null_array >= observed))

    null_mean = float(np.mean(null_array))
    null_std = float(np.std(null_array))
    effect_size = (observed - null_mean) / null_std if null_std > 1e-12 else 0.0

    return {
        "observed": float(observed),
        "p_value": p_value,
        "significant": p_value < alpha,
        "effect_size": effect_size,
        "adj_excess_mean": adj_mean,
        "nonadj_excess_mean": nonadj_mean,
        "null_distribution": null_ntcs,
    }


# Module-level instance for registry
balanced_topology = BalancedTopologyComparison()
