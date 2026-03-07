"""
Run key experiments with full visualizations and metrics.

Covers the most informative conditions from the research:
1. GHZ - the proven probe (clean vs noise comparison)
2. W - structured state under noise (ChatGPT's interesting case)
3. Cluster - Pauli invariant control
4. Superposition - product state control
5. Density matrix mode - see decoherence in the quantum state itself

All runs: 6 qubits, 8192 shots, seed=42, all visualizations enabled.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine.api import run
from src.engine.models import ExperimentConfig


def print_result_summary(label: str, result):
    """Print a compact summary of an experiment result."""
    meas = result.analysis.measurement_results
    cstats = result.analysis.circuit_statistics
    print(f"\n{'=' * 70}")
    print(f"  {label}")
    print(f"{'=' * 70}")
    print(f"  Circuit: depth={cstats.depth}, gates={cstats.num_gates}, "
          f"2q-gates={cstats.two_qubit_gate_count}")
    print(f"  Shots: {meas.total_shots}, Unique outcomes: {meas.unique_outcomes}")
    if meas.fidelity is not None:
        print(f"  Fidelity: {meas.fidelity:.6f}")

    # Top 5 outcomes
    sorted_probs = sorted(meas.outcome_probabilities.items(), key=lambda x: -x[1])
    print(f"  Top 5 outcomes:")
    for bs, p in sorted_probs[:5]:
        print(f"    {bs}: {p:.4f} ({int(p * meas.total_shots)} shots)")

    # Metrics
    if result.metrics_bundle and result.metrics_bundle.metrics:
        print(f"  Metrics ({result.metrics_bundle.profile}):")
        for name, entry in result.metrics_bundle.metrics.items():
            ci = f" CI95={entry.ci95}" if entry.ci95 else ""
            print(f"    {name}: {entry.value:.4f} [{entry.status}]{ci}")

    # Artifacts
    viz_artifacts = [a for a in result.artifacts if a.kind != "analysis"]
    if viz_artifacts:
        print(f"  Visualizations saved:")
        for a in viz_artifacts:
            print(f"    [{a.kind}] {a.path}")
    print()


# Common settings
QUBITS = 6
SHOTS = 8192
SEED = 42
VIZ = "all"
FORMATS = ["png"]

experiments = []

# ============================================================
# 1. GHZ Clean (no noise) - the ideal reference
# ============================================================
experiments.append(("GHZ 6q Clean (ideal reference)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="GHZ",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=False,
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 2. GHZ with moderate correlated noise - the proven detector
# ============================================================
experiments.append(("GHZ 6q Correlated Noise (p=0.2, cs=0.6, chain)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="GHZ",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="correlated_depolarizing",
    error_rate=0.2,
    custom_params={"correlation_strength": 0.6, "topology": "chain"},
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 3. GHZ with heavy correlated noise - maximum signal
# ============================================================
experiments.append(("GHZ 6q Heavy Noise (p=0.3, cs=0.8, chain)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="GHZ",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="correlated_depolarizing",
    error_rate=0.3,
    custom_params={"correlation_strength": 0.8, "topology": "chain"},
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 4. W state clean - ideal single-excitation subspace
# ============================================================
experiments.append(("W 6q Clean (ideal reference)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="W",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=False,
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 5. W state with heavy correlated noise - ChatGPT's interesting case
# ============================================================
experiments.append(("W 6q Heavy Noise (p=0.3, cs=0.8, chain)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="W",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="correlated_depolarizing",
    error_rate=0.3,
    custom_params={"correlation_strength": 0.8, "topology": "chain"},
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 6. Cluster clean - uniform Z-basis (Pauli invariant)
# ============================================================
experiments.append(("Cluster 6q Clean (uniform Z-basis reference)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="CLUSTER",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=False,
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 7. Cluster with heavy noise - should show Pauli invariance
# ============================================================
experiments.append(("Cluster 6q Heavy Noise (p=0.3, cs=0.8) - Pauli invariant?", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="CLUSTER",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="correlated_depolarizing",
    error_rate=0.3,
    custom_params={"correlation_strength": 0.8, "topology": "chain"},
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 8. Superposition (product state) with noise - control baseline
# ============================================================
experiments.append(("Superposition 6q Heavy Noise (p=0.3, cs=0.8) - control", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="SUPERPOSITION",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="correlated_depolarizing",
    error_rate=0.3,
    custom_params={"correlation_strength": 0.8, "topology": "chain"},
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 9. GHZ Density Matrix mode - see decoherence in the state
# ============================================================
experiments.append(("GHZ 6q Density Matrix (p=0.2 depolarizing)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="GHZ",
    sim_mode="density_matrix",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.2,
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))

# ============================================================
# 10. W Density Matrix mode - see excitation structure under noise
# ============================================================
experiments.append(("W 6q Density Matrix (p=0.2 depolarizing)", ExperimentConfig(
    num_qubits=QUBITS,
    state_type="W",
    sim_mode="density_matrix",
    shots=SHOTS,
    rng_seed=SEED,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.2,
    metrics="structured_decoherence",
    visualization_type=VIZ,
    export_formats=FORMATS,
)))


# ============================================================
# Run all experiments
# ============================================================
if __name__ == "__main__":
    print(f"Running {len(experiments)} key experiments with full visualizations...")
    print(f"Settings: {QUBITS}q, {SHOTS} shots, seed={SEED}\n")

    results = []
    for i, (label, config) in enumerate(experiments, 1):
        print(f"[{i}/{len(experiments)}] Running: {label}...")
        try:
            result = run(config)
            results.append((label, result))
            print_result_summary(label, result)
        except Exception as e:
            print(f"  FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 70)
    print("  ALL EXPERIMENTS COMPLETE")
    print("=" * 70)
    print(f"\n  Total experiments: {len(results)}")
    total_artifacts = sum(
        len([a for a in r.artifacts if a.kind != "analysis"])
        for _, r in results
    )
    print(f"  Total visualizations generated: {total_artifacts}")

    # List all output directories
    print(f"\n  Output directories:")
    seen_dirs = set()
    for _, r in results:
        for a in r.artifacts:
            d = os.path.dirname(a.path)
            if d not in seen_dirs:
                seen_dirs.add(d)
                print(f"    {d}")
