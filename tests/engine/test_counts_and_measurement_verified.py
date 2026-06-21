"""Verified exact-value tests for measurement-data math and canonicalization.

These tests lock the numeric/canonicalization behavior of the measurement
pipeline that feeds every research metric:

  * src/engine/analysis/research_integration.py  -> extract_counts_from_result,
    compute_metrics_bundle
  * src/engine/models/measurement.py             -> probability/normalization,
    auto-healing validators
  * src/engine/models/circuit.py                 -> circuit-stat reconciliation

Bit-ordering convention (verified end-to-end against Qiskit):
  - Qiskit `get_counts` returns MSB-left bitstrings: the RIGHTMOST character is
    physical qubit 0, the LEFTMOST is physical qubit (n-1).
  - extract_counts_from_result performs NO reversal: it strips spaces and
    pads/truncates only. The canonical key therefore preserves Qiskit's order
    (rightmost char == qubit 0).
  - The information-theory metrics index `bitstring[i]` positionally from the
    LEFT, so metric "qubit i" == physical qubit (n-1-i). This mirror is a
    consistent relabeling and does NOT affect symmetric topologies (GHZ ring,
    W, linear cluster) or distribution-level metrics (AI/SS/PCR/...). The tests
    below assert the actual (no-reversal) behavior so any endianness regression
    is caught immediately.
"""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from src.engine.analysis.research_integration import (
    compute_metrics_bundle,
    extract_counts_from_result,
)
from src.engine.models.circuit import CircuitStatistics
from src.engine.models.config import ExperimentConfig
from src.engine.models.measurement import MeasurementResults

# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------


class _FakeResult:
    """Mimics a Qiskit Result exposing get_counts()."""

    def __init__(self, counts, *, raise_noarg=False):
        self._counts = counts
        self._raise_noarg = raise_noarg

    def get_counts(self, index=None):
        if self._raise_noarg and index is None:
            raise TypeError("needs experiment index")
        return self._counts


class _BrokenResult:
    """get_counts always raises -> drives the outer except -> {}."""

    def get_counts(self, index=None):
        raise RuntimeError("boom")


# ---------------------------------------------------------------------------
# extract_counts_from_result: canonicalization + bit ordering
# ---------------------------------------------------------------------------


def test_extract_plain_dict_identity():
    out = extract_counts_from_result({"00": 750, "01": 250}, num_qubits=2)
    assert out == {"00": 750, "01": 250}


def test_extract_asymmetric_no_reversal():
    """CRITICAL endianness guard: '01' and '10' must NOT be swapped.

    extract performs no bit reversal, so an asymmetric input is preserved
    verbatim. If a future change reverses bits, this asymmetric pair flips.
    """
    out = extract_counts_from_result({"01": 5, "10": 7}, num_qubits=2)
    assert out == {"01": 5, "10": 7}
    assert out["01"] == 5
    assert out["10"] == 7


def test_extract_strips_register_spaces():
    out = extract_counts_from_result({"0 1": 3, "1 0": 4}, num_qubits=2)
    assert out == {"01": 3, "10": 4}


def test_extract_left_pads_short_keys():
    out = extract_counts_from_result({"1": 10, "10": 5}, num_qubits=3)
    assert out == {"001": 10, "010": 5}


def test_extract_truncates_keeps_rightmost_lsb():
    """Over-wide keys keep the least-significant (rightmost) num_qubits bits."""
    out = extract_counts_from_result({"11001": 8}, num_qubits=3)
    assert out == {"001": 8}


def test_extract_counts_subdict():
    out = extract_counts_from_result({"counts": {"00": 1, "11": 2}}, num_qubits=2)
    assert out == {"00": 1, "11": 2}


def test_extract_qiskit_result_object():
    res = _FakeResult({"01": 9, "10": 1})
    out = extract_counts_from_result(res, num_qubits=2)
    assert out == {"01": 9, "10": 1}


def test_extract_qiskit_result_needs_index_fallback():
    res = _FakeResult({"11": 4}, raise_noarg=True)
    out = extract_counts_from_result(res, num_qubits=2)
    assert out == {"11": 4}


def test_extract_width_inference_when_none():
    out = extract_counts_from_result({"010": 1, "101": 2})
    assert out == {"010": 1, "101": 2}


def test_extract_unsupported_type_returns_empty():
    assert extract_counts_from_result(12345) == {}


def test_extract_broken_result_returns_empty():
    assert extract_counts_from_result(_BrokenResult(), num_qubits=2) == {}


def test_extract_x0_excites_rightmost_qubit_position():
    """Physical qubit 0 (Qiskit) lands in the rightmost string position.

    Mirrors the verified Qiskit behavior: x(0) on a 3-qubit register yields
    '001'. Documents that the canonical key's rightmost char == qubit 0.
    """
    out = extract_counts_from_result({"001": 64}, num_qubits=3)
    assert out == {"001": 64}
    only_key = next(iter(out))
    assert only_key[-1] == "1"  # qubit 0 excited -> rightmost char
    assert only_key[0] == "0"  # qubit 2 ground   -> leftmost char


# ---------------------------------------------------------------------------
# MeasurementResults: probabilities / normalization / auto-heal
# ---------------------------------------------------------------------------


def test_from_counts_exact_probabilities():
    m = MeasurementResults.from_counts({"00": 750, "01": 250})
    assert m.total_shots == 1000
    assert m.unique_outcomes == 2
    assert m.outcome_probabilities["00"] == pytest.approx(0.75)
    assert m.outcome_probabilities["01"] == pytest.approx(0.25)
    assert sum(m.outcome_probabilities.values()) == pytest.approx(1.0)


def test_from_counts_empty_raises():
    with pytest.raises(ValueError):
        MeasurementResults.from_counts({})


def test_from_counts_zero_total_raises():
    with pytest.raises(ValueError):
        MeasurementResults.from_counts({"00": 0, "11": 0})


def test_before_validator_computes_missing_probabilities():
    m = MeasurementResults(
        raw_counts={"00": 3, "11": 1},
        total_shots=4,
        unique_outcomes=2,
        outcome_probabilities={},
    )
    assert m.outcome_probabilities["00"] == pytest.approx(0.75)
    assert m.outcome_probabilities["11"] == pytest.approx(0.25)


def test_after_validator_heals_total_shots():
    m = MeasurementResults(
        raw_counts={"00": 30, "11": 70},
        total_shots=999,  # wrong
        unique_outcomes=2,
        outcome_probabilities={"00": 0.3, "11": 0.7},
    )
    assert m.total_shots == 100


def test_after_validator_heals_unique_outcomes():
    m = MeasurementResults(
        raw_counts={"00": 1, "01": 1, "11": 1},
        total_shots=3,
        unique_outcomes=99,  # wrong
        outcome_probabilities={"00": 1 / 3, "01": 1 / 3, "11": 1 / 3},
    )
    assert m.unique_outcomes == 3


def test_after_validator_recomputes_on_key_mismatch():
    m = MeasurementResults(
        raw_counts={"00": 3, "01": 1},
        total_shots=4,
        unique_outcomes=2,
        outcome_probabilities={"wrong_key": 1.0},  # keys mismatch -> recompute
    )
    assert set(m.outcome_probabilities) == {"00", "01"}
    assert m.outcome_probabilities["00"] == pytest.approx(0.75)
    assert m.outcome_probabilities["01"] == pytest.approx(0.25)


def test_after_validator_renormalizes_when_sum_off():
    m = MeasurementResults(
        raw_counts={"00": 1, "11": 1},
        total_shots=2,
        unique_outcomes=2,
        outcome_probabilities={"00": 2.0, "11": 2.0},  # sum=4, keys match
    )
    assert sum(m.outcome_probabilities.values()) == pytest.approx(1.0)
    assert m.outcome_probabilities["00"] == pytest.approx(0.5)


def test_after_validator_recomputes_on_nonfinite_sum():
    m = MeasurementResults(
        raw_counts={"00": 1, "11": 3},
        total_shots=4,
        unique_outcomes=2,
        outcome_probabilities={"00": math.inf, "11": 0.0},  # keys match, sum nonfinite
    )
    assert m.outcome_probabilities["00"] == pytest.approx(0.25)
    assert m.outcome_probabilities["11"] == pytest.approx(0.75)


def test_after_validator_clamps_tiny_fp_drift():
    # sum within 1e-8 of 1.0 so no renormalization; clamp loop fixes bounds.
    m = MeasurementResults(
        raw_counts={"00": 1, "11": 1},
        total_shots=2,
        unique_outcomes=2,
        outcome_probabilities={"00": -1e-13, "11": 1.0 + 1e-13},
    )
    assert m.outcome_probabilities["00"] == 0.0
    assert m.outcome_probabilities["11"] == 1.0


def test_before_validator_passes_through_non_dict():
    # Non-dict input hits the early return in the before-validator, then fails
    # normal model validation.
    with pytest.raises(ValidationError):
        MeasurementResults.model_validate("not-a-dict")


def test_before_validator_swallows_bad_total_shots():
    # int(total) raises inside the before-validator try/except; the model then
    # rejects the non-integer total_shots at field validation.
    with pytest.raises(ValidationError):
        MeasurementResults(
            raw_counts={"00": 1},
            total_shots="abc",  # type: ignore[arg-type]
            unique_outcomes=1,
            outcome_probabilities={},
        )


def test_empty_raw_counts_rejected():
    with pytest.raises(ValueError):
        MeasurementResults(
            raw_counts={},
            total_shots=1,
            unique_outcomes=1,
            outcome_probabilities={"00": 1.0},
        )


def test_zero_total_raw_counts_rejected():
    with pytest.raises(ValueError):
        MeasurementResults(
            raw_counts={"00": 0},
            total_shots=1,
            unique_outcomes=1,
            outcome_probabilities={"00": 1.0},
        )


def test_statevector_and_density_matrix_passthrough():
    m = MeasurementResults(
        raw_counts={"00": 1, "11": 1},
        total_shots=2,
        unique_outcomes=2,
        outcome_probabilities={"00": 0.5, "11": 0.5},
        statevector=[[0.70710678, 0.0], [0.70710678, 0.0]],
        density_matrix=[[[1.0, 0.0]], [[0.0, 0.0]]],
        fidelity=0.987,
    )
    assert m.fidelity == pytest.approx(0.987)
    assert m.statevector[0] == [0.70710678, 0.0]
    assert m.density_matrix[0][0] == [1.0, 0.0]


# ---------------------------------------------------------------------------
# CircuitStatistics: numeric reconciliation / sanitization
# ---------------------------------------------------------------------------


def test_circuit_stats_bell_exact_values():
    """A real h+cx 2-qubit circuit: depth 2, 2 gates, 1 two-qubit gate."""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    gate_types: dict[str, int] = {}
    two_q = 0
    for inst in qc.data:
        name = inst.operation.name
        gate_types[name] = gate_types.get(name, 0) + 1
        if len(inst.qubits) == 2:
            two_q += 1

    cs = CircuitStatistics(
        depth=qc.depth(),
        num_gates=len(qc.data),
        num_qubits=qc.num_qubits,
        gate_types=gate_types,
        two_qubit_gate_count=two_q,
    )
    assert cs.depth == 2
    assert cs.num_gates == 2
    assert cs.num_qubits == 2
    assert cs.gate_types == {"h": 1, "cx": 1}
    assert cs.two_qubit_gate_count == 1


def test_circuit_stats_reconciles_num_gates_to_gate_types_sum():
    cs = CircuitStatistics(
        depth=1,
        num_gates=99,  # wrong
        num_qubits=2,
        gate_types={"h": 1, "cx": 1},
    )
    assert cs.num_gates == 2


def test_circuit_stats_clamps_two_qubit_count():
    cs = CircuitStatistics(
        depth=1,
        num_gates=2,
        num_qubits=2,
        gate_types={"h": 1, "cx": 1},
        two_qubit_gate_count=100,  # exceeds num_gates
    )
    assert cs.two_qubit_gate_count == 2


def test_circuit_stats_sanitizes_connectivity_graph():
    cs = CircuitStatistics(
        depth=1,
        num_gates=2,
        num_qubits=3,
        gate_types={"h": 1, "cx": 1},
        connectivity_graph=[[0, 1], [1, 1], [0, 5], [2, 3], [0]],
    )
    # [1,1] self-loop, [0,5]/[2,3] out-of-range, [0] wrong arity -> all dropped
    assert cs.connectivity_graph == [[0, 1]]


def test_circuit_stats_all_invalid_edges_become_none():
    cs = CircuitStatistics(
        depth=1,
        num_gates=1,
        num_qubits=2,
        gate_types={"h": 1},
        connectivity_graph=[[5, 6], [9, 9]],
    )
    assert cs.connectivity_graph is None


# ---------------------------------------------------------------------------
# compute_metrics_bundle: wiring + metadata
# ---------------------------------------------------------------------------


def test_compute_metrics_bundle_none_when_metrics_disabled():
    cfg = ExperimentConfig(num_qubits=2, state_type="GHZ", metrics=None)
    assert compute_metrics_bundle({"00": 1, "11": 1}, cfg) is None


def test_compute_metrics_bundle_none_on_empty_counts():
    cfg = ExperimentConfig(num_qubits=3, state_type="GHZ", metrics="structured_decoherence")
    assert compute_metrics_bundle({}, cfg) is None


def test_compute_metrics_bundle_metadata_and_entries():
    cfg = ExperimentConfig(num_qubits=3, state_type="GHZ", metrics="structured_decoherence")
    counts = {"000": 400, "111": 400, "001": 100, "110": 100}
    bundle = compute_metrics_bundle(counts, cfg)
    assert bundle is not None
    assert bundle.profile == "structured_decoherence"
    assert bundle.metadata.total_shots == 1000
    assert bundle.metadata.unique_outcomes == 4
    assert bundle.metadata.num_qubits == 3
    assert len(bundle.metrics) >= 1
    for entry in bundle.metrics.values():
        assert isinstance(entry.value, float)
        assert math.isfinite(entry.value)


def test_compute_metrics_bundle_includes_noise_conditions():
    """Noise-enabled config -> metadata.noise_conditions populated."""
    cfg = ExperimentConfig(
        num_qubits=2,
        state_type="GHZ",
        metrics="structured_decoherence",
        noise_enabled=True,
        noise_type="phase_flip",
        error_rate=0.05,
        z_prob=0.1,
        i_prob=0.9,
        t1=50.0,
        t2=70.0,
    )
    bundle = compute_metrics_bundle({"00": 400, "11": 400, "01": 200}, cfg)
    assert bundle is not None
    nc = bundle.metadata.noise_conditions
    assert nc is not None
    assert nc["noise_type"] == "phase_flip"
    assert nc["error_rate"] == pytest.approx(0.05)
    assert nc["z_prob"] == pytest.approx(0.1)
    assert nc["i_prob"] == pytest.approx(0.9)
    assert nc["t1"] == pytest.approx(50.0)
    assert nc["t2"] == pytest.approx(70.0)


def test_compute_metrics_bundle_no_noise_conditions_when_disabled():
    cfg = ExperimentConfig(
        num_qubits=2,
        state_type="GHZ",
        metrics="structured_decoherence",
        noise_enabled=False,
    )
    bundle = compute_metrics_bundle({"00": 1, "11": 1}, cfg)
    assert bundle is not None
    assert bundle.metadata.noise_conditions is None


# ---------------------------------------------------------------------------
# End-to-end ordering consistency (Qiskit -> extract -> metric indexing)
# ---------------------------------------------------------------------------


def test_e2e_ghz_mass_on_all_zero_and_all_one():
    """GHZ via state_preparation, deterministic sim -> mass on 000/111 only.

    This is exactly where the metrics expect GHZ pathway mass to live, so it
    confirms the extraction convention is consistent with the analysis layer.
    """
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    from src.core.state_preparation import prepare_state

    qc = prepare_state(num_qubits=3, state_type="GHZ")
    qc.measure_all()
    backend = AerSimulator()
    backend.set_options(seed_simulator=7)
    result = backend.run(transpile(qc, backend), shots=512).result()

    counts = extract_counts_from_result(result, num_qubits=3)
    assert set(counts) == {"000", "111"}
    assert sum(counts.values()) == 512
    for key in counts:
        assert len(key) == 3


def test_e2e_metric_qubit_index_is_left_positional():
    """Documents the metric/physical qubit mirror with an asymmetric circuit.

    x(0) excites physical qubit 0 -> canonical key '001'. The IT metric reads
    bitstring[i] positionally from the left, so the excited bit is seen at
    metric index 2 (= n-1). Locking this catches any silent endianness change
    on either side of the boundary.
    """
    from src.core.analysis.core.information_theory import marginal_distribution

    counts = extract_counts_from_result({"001": 100}, num_qubits=3)
    # metric index 2 (rightmost) sees the excited bit -> P(bit=1) dominant
    m_right = marginal_distribution(counts, 2)
    m_left = marginal_distribution(counts, 0)
    assert m_right[1] > m_right[0]  # rightmost position is excited
    assert m_left[0] > m_left[1]  # leftmost position is ground
