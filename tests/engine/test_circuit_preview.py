"""Tests for the circuit preview converter.

Validates that _qiskit_to_circuit correctly converts Qiskit QuantumCircuit
objects into the frontend Circuit JSON format for all state types, qubit
counts, and edge cases.
"""

import sys

import pytest

sys.path.insert(0, "apps")
from api.routes.experiments import _qiskit_to_circuit

from src.core.state_preparation.state_factory import prepare_state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_GATE_TYPES = {
    "H", "X", "Y", "Z", "S", "T", "SX",
    "Rx", "Ry", "Rz",
    "CNOT", "CZ", "SWAP", "Toffoli",
}


def _preview(state_type: str, num_qubits: int) -> dict:
    """Generate a circuit preview for a given state type and qubit count."""
    circuit = prepare_state(state_type, num_qubits)
    circuit.measure_all()
    return _qiskit_to_circuit(circuit)


def _all_gates(result: dict) -> list[dict]:
    """Extract all gates from all moments."""
    return [g for m in result["moments"] for g in m["gates"]]


# ---------------------------------------------------------------------------
# Structure tests: every result must have correct shape
# ---------------------------------------------------------------------------


class TestCircuitStructure:
    """Verify the output structure matches the frontend Circuit type."""

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_top_level_keys(self, state_type, num_qubits):
        """Result must have numQubits and moments keys."""
        result = _preview(state_type, num_qubits)
        assert "numQubits" in result
        assert "moments" in result
        assert isinstance(result["moments"], list)

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_num_qubits_matches(self, state_type, num_qubits):
        """numQubits in output must match requested qubit count."""
        result = _preview(state_type, num_qubits)
        assert result["numQubits"] == num_qubits

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_gate_fields(self, state_type, num_qubits):
        """Every gate must have id, gateType, and qubits fields."""
        result = _preview(state_type, num_qubits)
        for gate in _all_gates(result):
            assert "id" in gate, f"Gate missing 'id': {gate}"
            assert "gateType" in gate, f"Gate missing 'gateType': {gate}"
            assert "qubits" in gate, f"Gate missing 'qubits': {gate}"
            assert isinstance(gate["qubits"], list)
            assert len(gate["qubits"]) >= 1

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_gate_types_valid(self, state_type, num_qubits):
        """Every gateType must be in the known set."""
        result = _preview(state_type, num_qubits)
        for gate in _all_gates(result):
            assert gate["gateType"] in VALID_GATE_TYPES, (
                f"Unknown gateType '{gate['gateType']}' in {state_type} {num_qubits}q"
            )

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_qubit_indices_in_range(self, state_type, num_qubits):
        """All qubit indices must be within [0, numQubits)."""
        result = _preview(state_type, num_qubits)
        for gate in _all_gates(result):
            for q in gate["qubits"]:
                assert 0 <= q < num_qubits, (
                    f"Qubit index {q} out of range for {num_qubits}-qubit "
                    f"circuit in gate {gate}"
                )

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_unique_gate_ids(self, state_type, num_qubits):
        """All gate IDs must be unique."""
        result = _preview(state_type, num_qubits)
        ids = [g["id"] for g in _all_gates(result)]
        assert len(ids) == len(set(ids)), f"Duplicate gate IDs in {state_type} {num_qubits}q"

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_no_empty_moments(self, state_type, num_qubits):
        """No moment should be completely empty."""
        result = _preview(state_type, num_qubits)
        for i, moment in enumerate(result["moments"]):
            assert len(moment["gates"]) > 0, (
                f"Empty moment at index {i} in {state_type} {num_qubits}q"
            )

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 3), ("W", 3), ("CLUSTER", 4), ("BELL", 2), ("SUPERPOSITION", 2),
    ])
    def test_parametric_gates_have_params(self, state_type, num_qubits):
        """Parametric gates (Rx, Ry, Rz) must have a params array."""
        result = _preview(state_type, num_qubits)
        parametric = {"Rx", "Ry", "Rz"}
        for gate in _all_gates(result):
            if gate["gateType"] in parametric:
                assert "params" in gate and gate["params"], (
                    f"Parametric gate {gate['gateType']} missing params: {gate}"
                )


# ---------------------------------------------------------------------------
# Physics correctness: verify gate patterns match expected circuits
# ---------------------------------------------------------------------------


class TestGHZCircuit:
    """GHZ state: H on qubit 0, then cascading CNOTs."""

    def test_starts_with_hadamard(self):
        """First gate should be H on qubit 0."""
        result = _preview("GHZ", 4)
        first_moment = result["moments"][0]["gates"]
        assert len(first_moment) == 1
        assert first_moment[0]["gateType"] == "H"
        assert first_moment[0]["qubits"] == [0]

    def test_cnot_cascade(self):
        """Remaining moments should be CNOT(i, i+1) cascade."""
        result = _preview("GHZ", 4)
        for i in range(1, 4):
            moment = result["moments"][i]["gates"]
            assert len(moment) == 1
            assert moment[0]["gateType"] == "CNOT"
            assert moment[0]["qubits"] == [i - 1, i]

    @pytest.mark.parametrize("n", [2, 3, 5, 8])
    def test_gate_count_scales(self, n):
        """GHZ should have 1 H + (n-1) CNOT = n gates total."""
        result = _preview("GHZ", n)
        gates = _all_gates(result)
        assert len(gates) == n


class TestClusterCircuit:
    """Cluster state: H on all qubits, then nearest-neighbor CZ gates."""

    def test_hadamards_on_all_qubits(self):
        """First moment: H on every qubit."""
        result = _preview("CLUSTER", 4)
        first_moment = result["moments"][0]["gates"]
        h_qubits = sorted(g["qubits"][0] for g in first_moment if g["gateType"] == "H")
        assert h_qubits == [0, 1, 2, 3]

    def test_cz_nearest_neighbors(self):
        """CZ gates connect adjacent qubits."""
        result = _preview("CLUSTER", 4)
        cz_gates = [g for g in _all_gates(result) if g["gateType"] == "CZ"]
        cz_pairs = [tuple(g["qubits"]) for g in cz_gates]
        assert (0, 1) in cz_pairs
        assert (1, 2) in cz_pairs
        assert (2, 3) in cz_pairs

    @pytest.mark.parametrize("n", [2, 3, 4, 6])
    def test_gate_count(self, n):
        """Cluster: n H + (n-1) CZ = 2n-1 gates."""
        result = _preview("CLUSTER", n)
        gates = _all_gates(result)
        assert len(gates) == 2 * n - 1


class TestBellCircuit:
    """Bell state: H on qubit 0, CNOT(0, 1)."""

    def test_two_gates(self):
        """Bell circuit has exactly 2 gates."""
        result = _preview("BELL", 2)
        gates = _all_gates(result)
        assert len(gates) == 2

    def test_h_then_cnot(self):
        """First gate is H(0), second is CNOT(0,1)."""
        result = _preview("BELL", 2)
        gates = _all_gates(result)
        assert gates[0]["gateType"] == "H"
        assert gates[0]["qubits"] == [0]
        assert gates[1]["gateType"] == "CNOT"
        assert gates[1]["qubits"] == [0, 1]


class TestSuperpositionCircuit:
    """Superposition: H on every qubit, all in one moment."""

    @pytest.mark.parametrize("n", [1, 2, 3, 4])
    def test_all_h_gates(self, n):
        """Should have n H gates, one per qubit."""
        result = _preview("SUPERPOSITION", n)
        gates = _all_gates(result)
        assert all(g["gateType"] == "H" for g in gates)
        assert len(gates) == n

    def test_single_moment(self):
        """All H gates should be in the same moment (parallel)."""
        result = _preview("SUPERPOSITION", 4)
        assert len(result["moments"]) == 1
        assert len(result["moments"][0]["gates"]) == 4


class TestWCircuit:
    """W state: complex transpiled circuit with Rz, SX, CNOT gates."""

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_produces_gates(self, n):
        """W state should produce a non-trivial circuit."""
        result = _preview("W", n)
        gates = _all_gates(result)
        assert len(gates) > n  # More complex than just H gates

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_contains_cnot(self, n):
        """W state circuit must contain entangling CNOT gates."""
        result = _preview("W", n)
        gate_types = {g["gateType"] for g in _all_gates(result)}
        assert "CNOT" in gate_types

    @pytest.mark.parametrize("n", [2, 3, 4])
    def test_contains_rotation_gates(self, n):
        """W state uses Rz rotations in its decomposition."""
        result = _preview("W", n)
        gate_types = {g["gateType"] for g in _all_gates(result)}
        assert "Rz" in gate_types


# ---------------------------------------------------------------------------
# Scaling tests
# ---------------------------------------------------------------------------


class TestScaling:
    """Verify the converter handles various qubit counts."""

    @pytest.mark.parametrize("n", [2, 4, 6, 8, 10, 12, 14])
    def test_ghz_scales(self, n):
        """GHZ circuit scales linearly."""
        result = _preview("GHZ", n)
        assert result["numQubits"] == n
        assert len(_all_gates(result)) == n

    @pytest.mark.parametrize("n", [2, 4, 6, 8, 10])
    def test_cluster_scales(self, n):
        """Cluster circuit scales linearly."""
        result = _preview("CLUSTER", n)
        assert result["numQubits"] == n
        assert len(_all_gates(result)) == 2 * n - 1

    def test_single_qubit_superposition(self):
        """Single qubit produces a valid circuit."""
        result = _preview("SUPERPOSITION", 1)
        assert result["numQubits"] == 1
        assert len(result["moments"]) == 1
        assert result["moments"][0]["gates"][0]["gateType"] == "H"


# ---------------------------------------------------------------------------
# Moment assignment (no qubit collisions)
# ---------------------------------------------------------------------------


class TestMomentAssignment:
    """Verify that no two gates in the same moment share a qubit."""

    @pytest.mark.parametrize("state_type,num_qubits", [
        ("GHZ", 6), ("W", 4), ("CLUSTER", 6), ("BELL", 2), ("SUPERPOSITION", 4),
    ])
    def test_no_qubit_collisions(self, state_type, num_qubits):
        """Within each moment, no qubit should be used by more than one gate."""
        result = _preview(state_type, num_qubits)
        for i, moment in enumerate(result["moments"]):
            used_qubits: set[int] = set()
            for gate in moment["gates"]:
                for q in gate["qubits"]:
                    assert q not in used_qubits, (
                        f"Qubit {q} used twice in moment {i} of "
                        f"{state_type} {num_qubits}q"
                    )
                    used_qubits.add(q)
