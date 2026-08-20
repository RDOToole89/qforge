"""Hardware Decoherence Structure Study.

A documented experiment suite that runs on both real quantum hardware
and simulation, saving all results for comparative analysis.

Experiments:
  1. Scaling ladder:  GHZ at 2, 3, 4, 5, 6 qubits
  2. Topology comparison: GHZ, W, Cluster, Product at 6 qubits
  3. Backend comparison:  GHZ-6 on all available backends
  4. Measurement basis:   Cluster-6 in Z-basis vs X-basis
  5. Optimization level:  GHZ-6 at opt_level 0 vs 1 vs 3

Usage:
    # Run on real hardware
    python -m qforge.experiments.hardware_decoherence_study --mode hardware

    # Run same experiments in simulation (for comparison)
    python -m qforge.experiments.hardware_decoherence_study --mode simulation

    # Run a single experiment
    python -m qforge.experiments.hardware_decoherence_study --mode hardware --experiment basis
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit

from qforge.core.analysis.metrics.registry import compute_all as _compute_all_metrics
from qforge.engine.api import run
from qforge.engine.models import ExperimentConfig, ExperimentResult

logger = logging.getLogger(__name__)

RESULTS_DIR = Path("results/hardware_study")
SHOTS = 8192


def _save_result(experiment_name: str, label: str, data: dict[str, Any]) -> Path:
    """Save experiment result to JSON with timestamp."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = RESULTS_DIR / experiment_name
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{label}_{ts}.json"
    path.write_text(json.dumps(data, indent=2, default=str))
    logger.info(f"Saved: {path}")
    return path


def _extract_metrics(result: ExperimentResult) -> dict[str, float]:
    """Extract metric values from an ExperimentResult."""
    metrics: dict[str, float] = {}
    mb = result.metrics_bundle
    if mb and mb.metrics:
        for name, m in mb.metrics.items():
            # Cast to Any: metrics may be MetricEntry or raw dicts at runtime;
            # keeping both branches reachable for type-checking purposes.
            m_any: Any = m
            val = (
                m_any.value
                if hasattr(m_any, "value")
                else m_any.get("value")
                if isinstance(m_any, dict)
                else None
            )
            if val is not None:
                metrics[name] = val
    return metrics


def _run_single(cfg_dict: dict[str, Any], label: str) -> dict[str, Any]:
    """Run a single experiment and return a summary dict."""
    result = run(ExperimentConfig(**cfg_dict))

    counts = result.analysis.measurement_results.raw_counts
    fidelity = result.analysis.measurement_results.fidelity
    metrics = _extract_metrics(result)
    prov = result.provenance

    summary = {
        "label": label,
        "config": cfg_dict,
        "counts": counts,
        "fidelity": fidelity,
        "metrics": metrics,
        "total_shots": sum(counts.values()),
        "provenance": {
            "timestamp": prov.timestamp,
            "simulator_info": prov.simulator_info,
            "transpilation_summary": prov.transpilation_summary,
            "software_versions": prov.software_versions,
            "git_sha": prov.git_sha,
        },
    }

    # Print summary
    ss = metrics.get("structure_score", 0)
    tc = metrics.get("total_correlation", 0)
    ci = metrics.get("concentration_index", 0)
    print(f"  {label}: fidelity={fidelity:.4f}  SS={ss:.4f}  TC={tc:.4f}  CI={ci:.2f}")

    return summary


def _base_config(mode: str, **overrides: Any) -> dict[str, Any]:
    """Build config dict for hardware or simulation mode."""
    if mode == "hardware":
        cfg = {
            "sim_mode": "hardware",
            "shots": SHOTS,
            "optimization_level": 1,
            "visualization_type": "none",
            "metrics": "decoherence",
        }
    else:
        cfg = {
            "sim_mode": "qasm",
            "shots": SHOTS,
            "noise_enabled": True,
            "noise_type": "depolarizing",
            "error_rate": 0.02,
            "rng_seed": 42,
            "visualization_type": "none",
            "metrics": "decoherence",
        }
    cfg.update(overrides)
    return cfg


# ── Experiment 1: Scaling Ladder ─────────────────────────────────────


def run_scaling_ladder(mode: str = "hardware") -> list[dict]:
    """GHZ at 2, 3, 4, 5, 6 qubits."""
    print(f"\n{'=' * 60}")
    print(f"SCALING LADDER ({mode})")
    print(f"{'=' * 60}")

    results = []
    for n in [2, 3, 4, 5, 6]:
        cfg = _base_config(mode, num_qubits=n, state_type="GHZ")
        summary = _run_single(cfg, f"GHZ_{n}q")
        results.append(summary)

    _save_result("scaling_ladder", mode, {"mode": mode, "experiments": results})
    return results


# ── Experiment 2: Topology Comparison ────────────────────────────────


def run_topology_comparison(mode: str = "hardware") -> list[dict]:
    """GHZ, W, Cluster, Product at 6 qubits."""
    print(f"\n{'=' * 60}")
    print(f"TOPOLOGY COMPARISON ({mode})")
    print(f"{'=' * 60}")

    results = []
    for state in ["GHZ", "W", "CLUSTER", "SUPERPOSITION"]:
        cfg = _base_config(mode, num_qubits=6, state_type=state)
        summary = _run_single(cfg, f"{state}_6q")
        results.append(summary)

    _save_result("topology_comparison", mode, {"mode": mode, "experiments": results})
    return results


# ── Experiment 3: Backend Comparison ─────────────────────────────────


def run_backend_comparison() -> list[dict]:
    """GHZ-6 on all available backends (hardware only)."""
    print(f"\n{'=' * 60}")
    print("BACKEND COMPARISON (hardware only)")
    print(f"{'=' * 60}")

    backends = ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]
    results = []
    for backend_name in backends:
        cfg = _base_config("hardware", num_qubits=6, state_type="GHZ", backend_name=backend_name)
        summary = _run_single(cfg, f"GHZ_6q_{backend_name}")
        results.append(summary)

    _save_result("backend_comparison", "hardware", {"mode": "hardware", "experiments": results})
    return results


# ── Experiment 4: Measurement Basis ──────────────────────────────────


def _make_cluster_circuit(n: int, x_basis: bool = False) -> QuantumCircuit:
    """Build a Cluster state circuit with optional X-basis measurement."""
    qc = QuantumCircuit(n, n)
    for i in range(n):
        qc.h(i)
    for i in range(n - 1):
        qc.cz(i, i + 1)
    if x_basis:
        for i in range(n):
            qc.h(i)
    qc.measure(range(n), range(n))
    return qc


def run_measurement_basis(mode: str = "hardware") -> list[dict]:
    """Cluster-6 in Z-basis vs X-basis."""
    print(f"\n{'=' * 60}")
    print(f"MEASUREMENT BASIS COMPARISON ({mode})")
    print(f"{'=' * 60}")

    results = []
    n = 6

    for basis, x_basis in [("Z", False), ("X", True)]:
        circuit = _make_cluster_circuit(n, x_basis=x_basis)
        label = f"Cluster_6q_{basis}_basis"

        if mode == "hardware":
            from qforge.engine.execution.hardware import execute_on_hardware, resolve_backend

            backend = resolve_backend(backend_name="ibm_fez")
            hw_result = execute_on_hardware(circuit, backend, shots=SHOTS, optimization_level=1)
            counts = hw_result.counts
            metrics = _compute_all_metrics(counts=counts)

            metrics_flat = {}
            for name, m in metrics.items():
                val = (
                    getattr(m, "value", None)
                    if hasattr(m, "value")
                    else m.get("value")
                    if isinstance(m, dict)
                    else None
                )
                if val is not None:
                    metrics_flat[name] = val

            summary = {
                "label": label,
                "basis": basis,
                "counts": counts,
                "fidelity": None,
                "metrics": metrics_flat,
                "total_shots": sum(counts.values()),
                "provenance": {
                    "backend": hw_result.job_info.backend_name,
                    "job_id": hw_result.job_info.job_id,
                    "transpiled_depth": hw_result.transpilation_info.transpiled_depth,
                    "calibration": hw_result.calibration_snapshot,
                },
            }
        else:
            from qiskit import transpile
            from qiskit_aer import AerSimulator

            from qforge.core.noise_models import create_noise_model

            noise_model = create_noise_model("DEPOLARIZING", n, error_rate=0.02)
            backend = AerSimulator()
            backend.set_options(noise_model=noise_model, seed_simulator=42)
            tcirc = transpile(circuit, backend)
            job = backend.run(tcirc, shots=SHOTS)
            raw_counts = job.result().get_counts()

            # Canonicalize bitstrings
            counts = {}
            for k, v in raw_counts.items():
                key = k.replace(" ", "").rjust(n, "0")
                counts[key] = int(v)

            metrics = _compute_all_metrics(counts=counts)
            metrics_flat = {}
            for name, m in metrics.items():
                val = (
                    getattr(m, "value", None)
                    if hasattr(m, "value")
                    else m.get("value")
                    if isinstance(m, dict)
                    else None
                )
                if val is not None:
                    metrics_flat[name] = val

            summary = {
                "label": label,
                "basis": basis,
                "counts": counts,
                "fidelity": None,
                "metrics": metrics_flat,
                "total_shots": sum(counts.values()),
                "provenance": {"sim_mode": "qasm", "noise": "depolarizing", "error_rate": 0.02},
            }

        ss = metrics_flat.get("structure_score", 0)
        tc = metrics_flat.get("total_correlation", 0)
        ci = metrics_flat.get("concentration_index", 0)
        print(f"  {label}: SS={ss:.4f}  TC={tc:.4f}  CI={ci:.2f}")

        results.append(summary)

    _save_result("measurement_basis", mode, {"mode": mode, "experiments": results})
    return results


# ── Experiment 5: Optimization Level ─────────────────────────────────


def run_optimization_comparison() -> list[dict]:
    """GHZ-6 at optimization levels 0, 1, 3 (hardware only)."""
    print(f"\n{'=' * 60}")
    print("OPTIMIZATION LEVEL COMPARISON (hardware only)")
    print(f"{'=' * 60}")

    results = []
    for opt_level in [0, 1, 3]:
        cfg = _base_config(
            "hardware",
            num_qubits=6,
            state_type="GHZ",
            optimization_level=opt_level,
        )
        summary = _run_single(cfg, f"GHZ_6q_opt{opt_level}")
        results.append(summary)

    _save_result(
        "optimization_comparison",
        "hardware",
        {"mode": "hardware", "experiments": results},
    )
    return results


# ── Run All ──────────────────────────────────────────────────────────


def run_all(mode: str = "hardware") -> dict[str, list[dict]]:
    """Run the complete study."""
    print(f"\n{'#' * 60}")
    print("HARDWARE DECOHERENCE STRUCTURE STUDY")
    print(f"Mode: {mode}")
    print(f"Shots: {SHOTS}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'#' * 60}")

    all_results = {
        "scaling": run_scaling_ladder(mode),
        "topology": run_topology_comparison(mode),
        "basis": run_measurement_basis(mode),
    }

    if mode == "hardware":
        all_results["backends"] = run_backend_comparison()
        all_results["optimization"] = run_optimization_comparison()

    # Save combined results
    _save_result(
        "combined",
        mode,
        {
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "experiments": all_results,
        },
    )

    return all_results


# ── CLI ──────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hardware Decoherence Structure Study")
    parser.add_argument("--mode", choices=["hardware", "simulation"], default="hardware")
    parser.add_argument(
        "--experiment",
        choices=["scaling", "topology", "backends", "basis", "optimization", "all"],
        default="all",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(name)s:%(levelname)s: %(message)s")

    if args.experiment == "all":
        run_all(args.mode)
    elif args.experiment == "scaling":
        run_scaling_ladder(args.mode)
    elif args.experiment == "topology":
        run_topology_comparison(args.mode)
    elif args.experiment == "backends":
        if args.mode != "hardware":
            print("Backend comparison only runs on hardware.")
        else:
            run_backend_comparison()
    elif args.experiment == "basis":
        run_measurement_basis(args.mode)
    elif args.experiment == "optimization":
        if args.mode != "hardware":
            print("Optimization comparison only runs on hardware.")
        else:
            run_optimization_comparison()
