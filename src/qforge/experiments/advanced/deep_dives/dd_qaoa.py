"""QAOA — Quantum Approximate Optimization Algorithm for MaxCut.

WHAT YOU'LL LEARN:
  - MaxCut cost is a sum of ZZ correlators, one per graph edge
  - The engine estimates each ⟨Z_i Z_j⟩; this program turns those into a cut value
  - One evaluation is not a full optimizer loop — γ, β, and depth p are chosen, then ⟨C⟩ is measured

For an undirected graph G=(V,E) the cost is

  C = Σ_{(i,j)∈E} (1 − Z_i Z_j) / 2

so ⟨C⟩ = Σ (1 − ⟨Z_i Z_j⟩) / 2. Qubit indices on the circuit are Qiskit
physical indices; Pauli labels use QForge MSB-left order. Cost lives here,
not in core metrics.

CIRCUIT (4-qubit QAOA, p=1, square graph):
  q0: ─H── [ZZ(γ)] ── [Rx(2β)] ── M
  q1: ─H── [ZZ(γ)] ── [Rx(2β)] ── M
  q2: ─H── [ZZ(γ)] ── [Rx(2β)] ── M
  q3: ─H── [ZZ(γ)] ── [Rx(2β)] ── M

  ZZ(γ): CNOT-Rz-CNOT for each edge
  Rx(2β): mixer on every qubit
  p=0 is Hadamards only (⟨C⟩ = |E|/2 on a uniform superposition)

TRY IT:
    from qforge.experiments.advanced.deep_dives.dd_qaoa import qaoa_experiment

    result = qaoa_experiment.run()
    print(result.maxcut_cost, result.maxcut_optimal)

    results = qaoa_experiment.run_depth_sweep()
    # Circuit draw is on by default (Qiskit mpl). Off: visualization_type="none"
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from qiskit import QuantumCircuit

from qforge.core.math.indexing import physical_qubit_of_index
from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.engine.models.measurement import ObservableEstimate
from qforge.experiments.base import BaseExperiment

# C_4 (square): bipartite, so the exact MaxCut is all 4 edges.
DEFAULT_EDGES: tuple[tuple[int, int], ...] = ((0, 1), (1, 2), (2, 3), (0, 3))
DEFAULT_N_QUBITS = 4


def normalize_edges(edges: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    """Return unique undirected edges with i < j, preserving first-seen order."""
    seen: dict[tuple[int, int], None] = {}
    for pair in edges:
        if len(pair) != 2:
            raise ValueError(f"Each edge must be a pair of qubit indices, got {pair!r}")
        left, right = int(pair[0]), int(pair[1])
        if left == right:
            raise ValueError(f"MaxCut edges cannot be self-loops: {left}")
        edge = (left, right) if left < right else (right, left)
        seen.setdefault(edge, None)
    if not seen:
        raise ValueError("MaxCut graph must have at least one edge")
    return tuple(seen)


def zz_pauli(n_qubits: int, qubit_i: int, qubit_j: int) -> str:
    """ZZ on circuit (Qiskit physical) qubits, labeled in MSB-left Pauli order.

    Logical index L satisfies ``physical_qubit_of_index(L, n) == physical``.
    """
    chars = ["I"] * n_qubits
    for physical in (qubit_i, qubit_j):
        if not 0 <= physical < n_qubits:
            raise ValueError(f"Qubit {physical} is outside 0..{n_qubits - 1}")
        logical = n_qubits - 1 - physical
        if physical_qubit_of_index(logical, n_qubits) != physical:
            raise RuntimeError("Qubit indexing convention mismatch")
        chars[logical] = "Z"
    return "".join(chars)


def measured_zz_paulis(n_qubits: int, edges: Sequence[tuple[int, int]]) -> list[str]:
    """Unique ZZ Pauli strings the engine must estimate, one per edge."""
    labels: list[str] = []
    seen: set[str] = set()
    for left, right in edges:
        label = zz_pauli(n_qubits, left, right)
        if label not in seen:
            seen.add(label)
            labels.append(label)
    return labels


def maxcut_optimal(n_qubits: int, edges: Sequence[tuple[int, int]]) -> int:
    """Exact MaxCut by enumerating bitstrings on physical qubit indices."""
    best = 0
    n_edges = len(edges)
    for bits in range(1 << n_qubits):
        cut = 0
        for left, right in edges:
            if ((bits >> left) & 1) != ((bits >> right) & 1):
                cut += 1
        if cut > best:
            best = cut
            if best == n_edges:
                return best
    return best


def maxcut_from_estimates(
    estimates: Mapping[str, ObservableEstimate],
    n_qubits: int,
    edges: Sequence[tuple[int, int]],
) -> tuple[float, float | None]:
    """⟨C⟩ = Σ (1 − ⟨Z_i Z_j⟩) / 2. Stderr assumes independent edge terms."""
    cost = 0.0
    variance = 0.0
    have_stderr = True
    for left, right in edges:
        entry = estimates[zz_pauli(n_qubits, left, right)]
        cost += 0.5 * (1.0 - entry.value)
        if entry.stderr is None:
            have_stderr = False
        else:
            variance += (0.5 * entry.stderr) ** 2
    stderr = math.sqrt(variance) if have_stderr else None
    return float(cost), stderr


def _build_qaoa_circuit(
    n_qubits: int,
    edges: Sequence[tuple[int, int]],
    p: int = 1,
    gamma: float = 0.5,
    beta: float = 0.5,
) -> QuantumCircuit:
    """Build a QAOA circuit for MaxCut. ``p=0`` is Hadamards only."""
    if p < 0:
        raise ValueError(f"QAOA depth p must be >= 0, got {p}")
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        scale = (layer + 1) / p
        for left, right in edges:
            qc.cx(left, right)
            qc.rz(gamma * scale, right)
            qc.cx(left, right)
        for qubit in range(n_qubits):
            qc.rx(2 * beta * scale, qubit)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


class QAOAExperiment(BaseExperiment):
    """QAOA for MaxCut on small graphs.

    The default graph is C_4 (a square). Exact MaxCut is 4. The engine
    estimates one ⟨ZZ⟩ per edge; this program reports ⟨C⟩.
    """

    name = "qaoa"
    description = "QAOA — estimate MaxCut cost from ZZ observables (one variational evaluation)"
    metrics_hint = (
        "⟨C⟩ is the expected number of cut edges from the estimated ⟨ZZ⟩ terms. "
        "maxcut_optimal is the exact MaxCut of this graph (4 on the default square)."
    )

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return self._config()

    def _config(
        self,
        *,
        n_qubits: int = DEFAULT_N_QUBITS,
        edges: Sequence[Sequence[int]] | None = None,
        p: int = 1,
        gamma: float = 0.5,
        beta: float = 0.5,
        **kwargs: Any,
    ) -> ExperimentConfig:
        graph = normalize_edges(edges if edges is not None else DEFAULT_EDGES)
        needed = max(max(pair) for pair in graph) + 1
        if n_qubits < needed:
            raise ValueError(f"num_qubits={n_qubits} cannot host edges {graph}")
        circuit = _build_qaoa_circuit(n_qubits, graph, p=p, gamma=gamma, beta=beta)
        return ExperimentConfig(
            num_qubits=n_qubits,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            observables=measured_zz_paulis(n_qubits, graph),
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "p": p,
                "gamma": gamma,
                "beta": beta,
                "edges": [list(pair) for pair in graph],
            },
            visualization_type=["histogram", "circuit"],
            **kwargs,
        )

    def run(
        self,
        overrides: Mapping[str, Any] | None = None,
        *,
        ctx: Any | None = None,
    ) -> ExperimentResult:
        """Run one QAOA evaluation and attach ⟨C⟩ / exact MaxCut as extra fields."""
        merged = dict(overrides or {})
        incoming = dict(merged.get("custom_params") or {})
        n_qubits = int(merged.get("num_qubits", incoming.get("n_qubits", DEFAULT_N_QUBITS)))
        graph = normalize_edges(incoming.get("edges", DEFAULT_EDGES))
        p = int(incoming.get("p", 1))
        gamma = float(incoming.get("gamma", 0.5))
        beta = float(incoming.get("beta", 0.5))
        merged["num_qubits"] = n_qubits
        merged["custom_params"] = {
            "source": "circuit",
            "circuit": _build_qaoa_circuit(n_qubits, graph, p=p, gamma=gamma, beta=beta),
            "p": p,
            "gamma": gamma,
            "beta": beta,
            "edges": [list(pair) for pair in graph],
        }
        merged.setdefault("observables", measured_zz_paulis(n_qubits, graph))
        result = super().run(merged, ctx=ctx)
        estimates = result.analysis.measurement_results.observables or {}
        cost, stderr = maxcut_from_estimates(estimates, n_qubits, graph)
        optimal = maxcut_optimal(n_qubits, graph)
        ratio = (cost / optimal) if optimal else None
        return result.model_copy(
            update={
                "maxcut_cost": cost,
                "maxcut_cost_stderr": stderr,
                "maxcut_optimal": optimal,
                "maxcut_approximation_ratio": ratio,
                "qaoa_p": p,
            }
        )

    def run_depth_sweep(
        self,
        depths: list[int] | None = None,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Run QAOA at increasing depths to see the expected cut change."""
        custom = dict(overrides.pop("custom_params", {}) or {})
        results: list[ExperimentResult] = []
        for p in depths if depths is not None else [1, 2, 3, 4, 5]:
            merged = {**overrides, "custom_params": {**custom, "p": p}}
            results.append(self.run(merged))
        return results


qaoa_experiment = QAOAExperiment()
