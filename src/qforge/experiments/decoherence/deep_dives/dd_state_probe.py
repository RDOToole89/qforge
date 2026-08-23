"""State Probe Sensitivity Study.

Three-phase experiment testing which entangled states best detect correlated
noise topologies using the NTC (Noise Topology Correlation) metric.

Phase 1: Sensitivity ranking across 4 states x 3 error rates x 3 correlation strengths
Phase 2: Topology matching (3 states x 2 noise topologies)
Phase 3: Scaling with qubit count (best state from Phase 1, n=4..8)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal, cast

import numpy as np

from qforge.core.analysis.core.correlations import cosine_similarity_matrix, fingerprint_vector
from qforge.core.analysis.core.topology import TOPOLOGY_BUILDERS, chain_adjacency
from qforge.core.analysis.metrics.noise_topology_correlation import noise_topology_correlation
from qforge.engine.api import run
from qforge.engine.models import ExperimentConfig
from qforge.experiments.base import BaseExperiment

logger = logging.getLogger(__name__)

StateTypeLiteral = Literal["GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM"]

# --- Study constants ---

STATES = ["SUPERPOSITION", "GHZ", "W", "CLUSTER"]

# G_circuit type for provenance (how the preparation circuit is wired)
G_CIRCUIT_TYPE = {
    "SUPERPOSITION": "minimal",
    "GHZ": "chain",
    "W": "tree",
    "CLUSTER": "chain",
}

PHASE1_ERROR_RATES = [0.1, 0.2, 0.3]
PHASE1_CS_VALUES = [0.3, 0.6, 0.8]
DEFAULT_SHOTS = 8192
DEFAULT_N_QUBITS = 6
DEFAULT_N_PERMUTATIONS = 1000
PHASE3_QUBIT_COUNTS = [4, 5, 6, 7, 8]


class StateProbeStudy(BaseExperiment):
    """Three-phase state probe sensitivity study."""

    name = "state_probe_sensitivity"
    description = "Test which entangled states best detect correlated noise topologies via NTC"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for the state probe sensitivity study."""
        return ExperimentConfig(
            num_qubits=DEFAULT_N_QUBITS,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="correlated_depolarizing",
            error_rate=0.2,
            shots=DEFAULT_SHOTS,
            balance_circuit="gate_count",
            visualization_type="all",
            custom_params={"correlation_strength": 0.6, "topology": "CHAIN"},
        )

    # ----- Low-level helpers -----

    def _run_single(
        self,
        state: str,
        n: int,
        p: float,
        cs: float,
        noise_topology: str,
        seed: int,
    ) -> dict[str, int]:
        """Run one experiment, return raw measurement counts.

        cs=0 uses standard depolarizing (clean baseline).
        cs>0 uses correlated_depolarizing with the given topology.
        """
        if abs(cs) < 1e-10:
            config = ExperimentConfig(
                num_qubits=n,
                state_type=cast(StateTypeLiteral, state),
                noise_enabled=True,
                noise_type="depolarizing",
                error_rate=p,
                shots=DEFAULT_SHOTS,
                balance_circuit="gate_count",
                visualization_type="all",
                rng_seed=seed,
            )
        else:
            config = ExperimentConfig(
                num_qubits=n,
                state_type=cast(StateTypeLiteral, state),
                noise_enabled=True,
                noise_type="correlated_depolarizing",
                error_rate=p,
                shots=DEFAULT_SHOTS,
                balance_circuit="gate_count",
                visualization_type="all",
                rng_seed=seed,
                custom_params={
                    "correlation_strength": cs,
                    "topology": noise_topology.upper(),
                },
            )

        result = run(config)
        return result.analysis.measurement_results.raw_counts

    def _compute_row(
        self,
        state: str,
        n: int,
        p: float,
        cs: float,
        noise_topology: str,
        test_counts: dict[str, int],
        baseline_counts: dict[str, int],
        seed: int,
        rng: np.random.Generator,
    ) -> dict[str, Any]:
        """Compute NTC and return one Appendix B schema row."""
        adj = TOPOLOGY_BUILDERS[noise_topology.upper()](n)
        ntc_result = noise_topology_correlation(
            counts=test_counts,
            baseline_counts=baseline_counts,
            noise_adjacency=adj,
            n_qubits=n,
            n_permutations=DEFAULT_N_PERMUTATIONS,
            rng=rng,
        )

        return {
            "state": state,
            "n": n,
            "p": p,
            "cs": cs,
            "noise_topology": noise_topology.lower(),
            "ntc": ntc_result["ntc"],
            "p_value": ntc_result["p_value"],
            "effect_size": ntc_result["effect_size"],
            "edge_excess": ntc_result["edge_excess_mean"],
            "non_edge_excess": ntc_result["non_edge_excess_mean"],
            "g_circuit_type": G_CIRCUIT_TYPE.get(state, "unknown"),
            "seed": seed,
            "shots": DEFAULT_SHOTS,
        }

    # ----- Phase runners -----

    def run_phase1(self, rng_seed: int = 42) -> list[dict[str, Any]]:
        """Phase 1: Sensitivity ranking — 4 states x 3 p x 3 cs = 36 rows.

        For each (state, p) pair, runs baseline (cs=0) then each cs value.
        Uses the same seed for baseline and test within each (state, p) pair.
        """
        rng = np.random.default_rng(rng_seed)
        rows: list[dict[str, Any]] = []
        n = DEFAULT_N_QUBITS

        for state in STATES:
            for p in PHASE1_ERROR_RATES:
                seed = int(rng.integers(0, 2**31))
                logger.info(f"Phase 1: {state} p={p} — running baseline (cs=0)")
                baseline_counts = self._run_single(state, n, p, 0.0, "CHAIN", seed)

                for cs in PHASE1_CS_VALUES:
                    logger.info(f"Phase 1: {state} p={p} cs={cs}")
                    test_counts = self._run_single(state, n, p, cs, "CHAIN", seed)
                    row = self._compute_row(
                        state, n, p, cs, "chain", test_counts, baseline_counts, seed, rng
                    )
                    rows.append(row)
                    logger.info(
                        f"  NTC={row['ntc']:.4f} p={row['p_value']:.3f} d={row['effect_size']:.2f}"
                    )

        return rows

    def run_phase2(self, rng_seed: int = 42) -> list[dict[str, Any]]:
        """Phase 2: Topology matching — 3 states x 2 topologies = 6 rows.

        Tests GHZ, W, Cluster against chain and star noise at n=6, p=0.2, cs=0.6.
        """
        rng = np.random.default_rng(rng_seed)
        rows: list[dict[str, Any]] = []
        n = DEFAULT_N_QUBITS
        p = 0.2
        cs = 0.6
        states = ["GHZ", "W", "CLUSTER"]
        topologies = ["CHAIN", "STAR"]

        for state in states:
            seed = int(rng.integers(0, 2**31))
            # Baseline is always independent noise (same for both topologies)
            baseline_counts = self._run_single(state, n, p, 0.0, "CHAIN", seed)

            for topo in topologies:
                logger.info(f"Phase 2: {state} x {topo}")
                test_counts = self._run_single(state, n, p, cs, topo, seed)
                row = self._compute_row(
                    state, n, p, cs, topo, test_counts, baseline_counts, seed, rng
                )
                rows.append(row)
                logger.info(
                    f"  NTC={row['ntc']:.4f} p={row['p_value']:.3f} d={row['effect_size']:.2f}"
                )

        return rows

    def run_phase3(self, best_state: str, rng_seed: int = 42) -> list[dict[str, Any]]:
        """Phase 3: Scaling — 1 state x 5 qubit counts = 5 rows.

        Sweeps n in {4,5,6,7,8} at p=0.2, cs=0.6, chain topology.
        """
        rng = np.random.default_rng(rng_seed)
        rows: list[dict[str, Any]] = []
        p = 0.2
        cs = 0.6

        for n in PHASE3_QUBIT_COUNTS:
            seed = int(rng.integers(0, 2**31))
            logger.info(f"Phase 3: {best_state} n={n}")
            baseline_counts = self._run_single(best_state, n, p, 0.0, "CHAIN", seed)
            test_counts = self._run_single(best_state, n, p, cs, "CHAIN", seed)
            row = self._compute_row(
                best_state, n, p, cs, "chain", test_counts, baseline_counts, seed, rng
            )
            rows.append(row)
            logger.info(f"  NTC={row['ntc']:.4f} p={row['p_value']:.3f} d={row['effect_size']:.2f}")

        return rows

    def run_all(
        self,
        output_path: str = "results/state_probe_study.jsonl",
        rng_seed: int = 42,
    ) -> list[dict[str, Any]]:
        """Run all three phases and write JSONL results table.

        Auto-selects best state from Phase 1 for Phase 3.
        Returns combined list of all rows.
        """
        all_rows: list[dict[str, Any]] = []

        # Phase 1
        logger.info("=== Phase 1: Sensitivity Ranking ===")
        phase1_rows = self.run_phase1(rng_seed)
        for row in phase1_rows:
            row["phase"] = 1
        all_rows.extend(phase1_rows)

        # Auto-select best state: highest mean NTC across all Phase 1 conditions
        state_ntc: dict[str, list[float]] = {}
        for row in phase1_rows:
            state_ntc.setdefault(row["state"], []).append(row["ntc"])
        best_state = max(state_ntc, key=lambda s: float(np.mean(state_ntc[s])))
        logger.info(f"Best state from Phase 1: {best_state}")

        # Phase 2
        logger.info("=== Phase 2: Topology Matching ===")
        phase2_rows = self.run_phase2(rng_seed + 1)
        for row in phase2_rows:
            row["phase"] = 2
        all_rows.extend(phase2_rows)

        # Phase 3
        logger.info(f"=== Phase 3: Scaling ({best_state}) ===")
        phase3_rows = self.run_phase3(best_state, rng_seed + 2)
        for row in phase3_rows:
            row["phase"] = 3
        all_rows.extend(phase3_rows)

        # Write JSONL
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            for row in all_rows:
                f.write(json.dumps(row, default=str) + "\n")
        logger.info(f"Wrote {len(all_rows)} rows to {out}")

        return all_rows

    # ----- Validation experiments -----

    @staticmethod
    def _shuffled_adjacency(n: int, n_edges: int, rng: np.random.Generator) -> list[list[float]]:
        """Generate a random adjacency matrix with exactly n_edges edges.

        Returns a list-of-lists (JSON-serializable) so it can flow through
        ExperimentConfig.custom_params → noise factory → CorrelatedDepolarizingNoise.
        """
        all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        chosen = rng.choice(len(all_pairs), size=n_edges, replace=False)
        adj = [[0.0] * n for _ in range(n)]
        for idx in chosen:
            i, j = all_pairs[idx]
            adj[i][j] = 1.0
            adj[j][i] = 1.0
        return adj

    def _run_single_custom_topology(
        self,
        state: str,
        n: int,
        p: float,
        cs: float,
        custom_adj: list[list[float]],
        seed: int,
    ) -> dict[str, int]:
        """Run one experiment with a custom noise adjacency matrix."""
        config = ExperimentConfig(
            num_qubits=n,
            state_type=cast(StateTypeLiteral, state),
            noise_enabled=True,
            noise_type="correlated_depolarizing",
            error_rate=p,
            shots=DEFAULT_SHOTS,
            balance_circuit="gate_count",
            visualization_type="all",
            rng_seed=seed,
            custom_params={
                "correlation_strength": cs,
                "topology": "CHAIN",  # fallback name; custom_topology overrides
                "custom_topology": custom_adj,
            },
        )
        result = run(config)
        return result.analysis.measurement_results.raw_counts

    def run_shuffled_control(
        self, n_repeats: int = 10, rng_seed: int = 100
    ) -> list[dict[str, Any]]:
        """Shuffled-topology control: random edges, NTC measured against chain.

        Injects correlated noise on random qubit pairs (same edge count as
        chain = n-1 edges) but computes NTC against the true chain adjacency.
        Prediction: NTC ≈ 0 because noise is not at the expected locations.

        Runs GHZ at n=6, p=0.2, cs=0.6 with n_repeats different random topologies.
        """
        rng = np.random.default_rng(rng_seed)
        rows: list[dict[str, Any]] = []
        n = DEFAULT_N_QUBITS
        p = 0.2
        cs = 0.6
        n_edges = n - 1  # same count as chain

        for i in range(n_repeats):
            seed = int(rng.integers(0, 2**31))
            shuffled_adj = self._shuffled_adjacency(n, n_edges, rng)

            logger.info(f"Shuffled control {i + 1}/{n_repeats}")
            baseline_counts = self._run_single("GHZ", n, p, 0.0, "CHAIN", seed)
            test_counts = self._run_single_custom_topology("GHZ", n, p, cs, shuffled_adj, seed)

            # NTC computed against TRUE chain adjacency (not shuffled)
            chain_adj = chain_adjacency(n)
            ntc_result = noise_topology_correlation(
                counts=test_counts,
                baseline_counts=baseline_counts,
                noise_adjacency=chain_adj,
                n_qubits=n,
                n_permutations=DEFAULT_N_PERMUTATIONS,
                rng=rng,
            )

            row = {
                "state": "GHZ",
                "n": n,
                "p": p,
                "cs": cs,
                "noise_topology": "shuffled",
                "ntc": ntc_result["ntc"],
                "p_value": ntc_result["p_value"],
                "effect_size": ntc_result["effect_size"],
                "edge_excess": ntc_result["edge_excess_mean"],
                "non_edge_excess": ntc_result["non_edge_excess_mean"],
                "g_circuit_type": "chain",
                "seed": seed,
                "shots": DEFAULT_SHOTS,
                "phase": "shuffled_control",
            }
            rows.append(row)
            logger.info(f"  NTC={row['ntc']:.4f} p={row['p_value']:.3f} d={row['effect_size']:.2f}")

        return rows

    def run_multi_seed_w(self, n_seeds: int = 10, rng_seed: int = 200) -> list[dict[str, Any]]:
        """Multi-seed W state validation at key conditions.

        Runs W state at n=6, p=0.2, cs=0.6, chain noise with multiple seeds
        to distinguish "truly weak signal" from "unlucky seed."
        """
        rng = np.random.default_rng(rng_seed)
        rows: list[dict[str, Any]] = []
        n = DEFAULT_N_QUBITS
        p = 0.2
        cs = 0.6

        for i in range(n_seeds):
            seed = int(rng.integers(0, 2**31))
            logger.info(f"Multi-seed W {i + 1}/{n_seeds} (seed={seed})")
            baseline_counts = self._run_single("W", n, p, 0.0, "CHAIN", seed)
            test_counts = self._run_single("W", n, p, cs, "CHAIN", seed)
            row = self._compute_row("W", n, p, cs, "chain", test_counts, baseline_counts, seed, rng)
            row["phase"] = "multi_seed_w"
            rows.append(row)
            logger.info(f"  NTC={row['ntc']:.4f} p={row['p_value']:.3f} d={row['effect_size']:.2f}")

        return rows

    # ----- Fingerprint analysis -----

    def run_fingerprint_analysis(
        self,
        output_dir: str = "results/fingerprint_analysis",
        rng_seed: int = 42,
    ) -> dict[str, Any]:
        """Direction 2: Noise Fingerprint Analysis.

        Re-runs Phase 1 + Phase 2 experiments using deterministic seeds,
        computes full ΔCov fingerprint vectors, and analyzes geometric
        relationships (cosine similarity, PCA) to determine whether noise
        signatures scale (same direction, varying magnitude) or shift
        (direction changes) as parameters vary.

        Returns summary dict with verdict and key statistics.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        n = DEFAULT_N_QUBITS

        # --- Replay Phase 1 seeds (same RNG sequence as run_phase1(42)) ---
        rng1 = np.random.default_rng(rng_seed)
        phase1_seeds: dict[tuple[str, float], int] = {}
        for state in STATES:
            for p in PHASE1_ERROR_RATES:
                seed = int(rng1.integers(0, 2**31))
                phase1_seeds[(state, p)] = seed

        # --- Replay Phase 2 seeds (same RNG sequence as run_phase2(43)) ---
        rng2 = np.random.default_rng(rng_seed + 1)
        phase2_seeds: dict[str, int] = {}
        for state in ["GHZ", "W", "CLUSTER"]:
            phase2_seeds[state] = int(rng2.integers(0, 2**31))

        # --- Compute fingerprints for Phase 1 ---
        fingerprints: list[dict[str, Any]] = []
        vectors: list[np.ndarray] = []

        logger.info("=== Fingerprint Analysis: Phase 1 replay ===")
        for state in STATES:
            for p in PHASE1_ERROR_RATES:
                seed = phase1_seeds[(state, p)]
                baseline_counts = self._run_single(state, n, p, 0.0, "CHAIN", seed)

                for cs in PHASE1_CS_VALUES:
                    logger.info(f"Fingerprint: {state} p={p} cs={cs}")
                    test_counts = self._run_single(state, n, p, cs, "CHAIN", seed)
                    fv = fingerprint_vector(test_counts, baseline_counts, n)
                    norm = float(np.linalg.norm(fv))
                    vectors.append(fv)
                    fingerprints.append(
                        {
                            "phase": 1,
                            "state": state,
                            "p": p,
                            "cs": cs,
                            "topology": "chain",
                            "seed": seed,
                            "fingerprint": fv.tolist(),
                            "norm": norm,
                        }
                    )
                    logger.info(f"  norm={norm:.6f}")

        # --- Compute fingerprints for Phase 2 ---
        logger.info("=== Fingerprint Analysis: Phase 2 replay ===")
        for state in ["GHZ", "W", "CLUSTER"]:
            seed = phase2_seeds[state]
            baseline_counts = self._run_single(state, n, 0.2, 0.0, "CHAIN", seed)

            for topo in ["CHAIN", "STAR"]:
                logger.info(f"Fingerprint: {state} x {topo}")
                test_counts = self._run_single(state, n, 0.2, 0.6, topo, seed)
                fv = fingerprint_vector(test_counts, baseline_counts, n)
                norm = float(np.linalg.norm(fv))
                vectors.append(fv)
                fingerprints.append(
                    {
                        "phase": 2,
                        "state": state,
                        "p": 0.2,
                        "cs": 0.6,
                        "topology": topo.lower(),
                        "seed": seed,
                        "fingerprint": fv.tolist(),
                        "norm": norm,
                    }
                )
                logger.info(f"  norm={norm:.6f}")

        # --- Cosine similarity matrix ---
        sim_matrix = cosine_similarity_matrix(vectors)

        # --- PCA via SVD (no sklearn needed) ---
        mat = np.stack(vectors, axis=0)  # k x 15
        mat_centered = mat - mat.mean(axis=0)
        U, S, Vt = np.linalg.svd(mat_centered, full_matrices=False)
        pca_coords = U[:, :2] * S[:2]  # project onto first 2 PCs
        variance_explained = (S**2) / (S**2).sum()

        # --- Summary statistics ---
        labels = [f"{fp['state']}_{fp['topology']}_p{fp['p']}_cs{fp['cs']}" for fp in fingerprints]
        states_arr = np.array([fp["state"] for fp in fingerprints])
        norms = np.array([fp["norm"] for fp in fingerprints])

        # GHZ-only cosine similarities (Phase 1, chain)
        ghz_mask = np.array([fp["state"] == "GHZ" and fp["phase"] == 1 for fp in fingerprints])
        ghz_indices = np.where(ghz_mask)[0]
        ghz_sim = sim_matrix[np.ix_(ghz_indices, ghz_indices)]
        ghz_upper = ghz_sim[np.triu_indices(len(ghz_indices), k=1)]

        # Per-p stability: for each state, cosine sim across cs values at fixed p
        per_p_stability: dict[str, dict[str, float]] = {}
        for state in STATES:
            state_stab: dict[str, float] = {}
            for p in PHASE1_ERROR_RATES:
                idxs = [
                    i
                    for i, fp in enumerate(fingerprints)
                    if fp["state"] == state and fp["p"] == p and fp["phase"] == 1
                ]
                if len(idxs) >= 2:
                    sub_sim = sim_matrix[np.ix_(idxs, idxs)]
                    upper = sub_sim[np.triu_indices(len(idxs), k=1)]
                    state_stab[str(p)] = float(np.mean(upper))
                else:
                    state_stab[str(p)] = float("nan")
            per_p_stability[state] = state_stab

        # Scaling vs shifting verdict
        # "Scaling" = high cosine similarity (same direction) across cs values
        # "Shifting" = low cosine similarity (direction changes)
        ghz_mean_cos = float(np.mean(ghz_upper)) if len(ghz_upper) > 0 else 0.0
        if ghz_mean_cos > 0.8:
            verdict = "SCALING"
            explanation = (
                f"GHZ fingerprints are highly aligned (mean cosine={ghz_mean_cos:.3f}): "
                "noise signature scales in magnitude but preserves direction."
            )
        elif ghz_mean_cos > 0.5:
            verdict = "MIXED"
            explanation = (
                f"GHZ fingerprints show moderate alignment (mean cosine={ghz_mean_cos:.3f}): "
                "noise signature partially shifts direction with parameter changes."
            )
        else:
            verdict = "SHIFTING"
            explanation = (
                f"GHZ fingerprints are weakly aligned (mean cosine={ghz_mean_cos:.3f}): "
                "noise signature direction changes substantially with parameters."
            )

        summary = {
            "n_fingerprints": len(fingerprints),
            "n_qubits": n,
            "vector_dim": int(n * (n - 1) / 2),
            "ghz_mean_cosine": ghz_mean_cos,
            "ghz_min_cosine": float(np.min(ghz_upper)) if len(ghz_upper) > 0 else 0.0,
            "ghz_max_cosine": float(np.max(ghz_upper)) if len(ghz_upper) > 0 else 0.0,
            "per_p_stability": per_p_stability,
            "pca_variance_explained": variance_explained[:3].tolist(),
            "verdict": verdict,
            "explanation": explanation,
            "norms_by_state": {
                s: {
                    "mean": float(np.mean(norms[states_arr == s])),
                    "std": float(np.std(norms[states_arr == s])),
                }
                for s in np.unique(states_arr)
            },
        }

        # --- Write outputs ---
        # fingerprints.jsonl
        with open(out / "fingerprints.jsonl", "w") as f:
            for fp in fingerprints:
                f.write(json.dumps(fp, default=str) + "\n")

        # summary.json
        with open(out / "summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Verdict: {verdict} — {explanation}")

        # --- Plots ---
        # 1. Similarity heatmap
        fig, ax = plt.subplots(figsize=(14, 12))
        im = ax.imshow(sim_matrix, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=6)
        ax.set_yticklabels(labels, fontsize=6)
        plt.colorbar(im, ax=ax, label="Cosine similarity")
        ax.set_title("Noise Fingerprint Cosine Similarity")
        fig.tight_layout()
        fig.savefig(out / "similarity_heatmap.png", dpi=150)
        plt.close(fig)

        # 2. PCA scatter
        state_colors = {
            "SUPERPOSITION": "tab:blue",
            "GHZ": "tab:red",
            "W": "tab:green",
            "CLUSTER": "tab:orange",
        }
        fig, ax = plt.subplots(figsize=(10, 8))
        for state in np.unique(states_arr):
            mask = states_arr == state
            ax.scatter(
                pca_coords[mask, 0],
                pca_coords[mask, 1],
                label=state,
                color=state_colors.get(state, "gray"),
                alpha=0.7,
                s=60,
            )
        ax.set_xlabel(f"PC1 ({variance_explained[0]:.1%} var)")
        ax.set_ylabel(f"PC2 ({variance_explained[1]:.1%} var)")
        ax.set_title("Noise Fingerprint PCA")
        ax.legend()
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.axvline(0, color="gray", linewidth=0.5)
        fig.tight_layout()
        fig.savefig(out / "pca_scatter.png", dpi=150)
        plt.close(fig)

        # 3. ΔCov heatmaps (one per state, using p=0.2, cs=0.6 from Phase 1)
        fig, axes = plt.subplots(1, len(STATES), figsize=(4 * len(STATES), 4))
        for ax_i, state in enumerate(STATES):
            # Find the Phase 1 fingerprint at p=0.2, cs=0.6
            idx = next(
                (
                    i
                    for i, fp in enumerate(fingerprints)
                    if fp["state"] == state
                    and fp["p"] == 0.2
                    and fp["cs"] == 0.6
                    and fp["phase"] == 1
                ),
                None,
            )
            if idx is not None:
                fv = np.array(fingerprints[idx]["fingerprint"])
                # Reconstruct matrix from upper triangle
                dcov = np.zeros((n, n))
                dcov[np.triu_indices(n, k=1)] = fv
                dcov = dcov + dcov.T
                vmax = max(abs(dcov.max()), abs(dcov.min()), 1e-10)
                axes[ax_i].imshow(dcov, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
                axes[ax_i].set_title(f"{state}\n||fv||={fingerprints[idx]['norm']:.4f}")
            else:
                axes[ax_i].set_title(f"{state}\n(not found)")
            axes[ax_i].set_xticks(range(n))
            axes[ax_i].set_yticks(range(n))
        fig.suptitle("Excess Covariance (ΔCov) at p=0.2, cs=0.6", fontsize=12)
        fig.tight_layout()
        fig.savefig(out / "deltacov_heatmaps.png", dpi=150)
        plt.close(fig)

        logger.info(f"Wrote outputs to {out}/")
        return summary


# Module-level instance for registry
state_probe_sensitivity = StateProbeStudy()
