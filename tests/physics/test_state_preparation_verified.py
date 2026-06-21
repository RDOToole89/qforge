"""Physics-verified tests for quantum state preparation.

Every entangling / superposition state is built with the real Qiskit
``Statevector.from_instruction(state.create())`` and compared, amplitude by
amplitude, against a closed-form reference computed independently here.

Conventions
-----------
Qiskit little-endian: qubit 0 is the least-significant bit, so the integer
index of a basis state is ``sum(q_i * 2**i)``.  All references below are written
directly in this little-endian basis ordering.

The goal is rigorous correctness plus near-100% line coverage of
``src/core/state_preparation/``.
"""

from __future__ import annotations

import sys
import types

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from src.core.state_preparation import (
    BellState,
    ClusterState,
    CustomState,
    GHZState,
    SuperpositionState,
    WState,
    create_state_instance,
    get_available_states,
    prepare_state,
    prepare_state_for_hardware,
    validate_state_request,
)
from src.core.state_preparation import state_constants as sc
from src.core.state_preparation.base_state import BaseState
from tests._qhelpers import BELL_STATEVECTORS, INV_SQRT2, ghz_statevector, w_statevector

ATOL = 1e-9


def actual(state: BaseState) -> np.ndarray:
    """Build the exact statevector from the circuit the state produces."""
    return np.asarray(Statevector.from_instruction(state.create()).data, dtype=complex)


def popcount(i: int) -> int:
    return bin(i).count("1")


# ===========================================================================
# GHZ
# ===========================================================================


class TestGHZ:
    def test_ghz3_closed_form(self):
        expected = ghz_statevector(3)
        sv = actual(GHZState(3))
        assert np.allclose(sv, expected, atol=ATOL)
        # Spot-check the published numeric vector.
        assert np.allclose(
            sv,
            [0.70710678, 0, 0, 0, 0, 0, 0, 0.70710678],
            atol=1e-8,
        )

    def test_ghz3_theoretical_matches_circuit(self):
        st = GHZState(3)
        assert np.allclose(st.get_theoretical_state_vector(), actual(st), atol=ATOL)

    def test_ghz2_is_bell_phi_plus(self):
        expected = np.array([INV_SQRT2, 0, 0, INV_SQRT2], dtype=complex)
        st = GHZState(2)
        assert np.allclose(actual(st), expected, atol=ATOL)
        assert np.allclose(st.get_theoretical_state_vector(), expected, atol=ATOL)

    def test_ghz1_is_ground_state(self):
        st = GHZState(1)
        assert np.allclose(actual(st), [1, 0], atol=ATOL)
        assert np.allclose(st.get_theoretical_state_vector(), [1, 0], atol=ATOL)

    def test_ghz_create_raises_below_one_qubit(self):
        # base __init__ already guards, so build an instance then corrupt count
        st = GHZState(2)
        st.num_qubits = 0
        with pytest.raises(ValueError):
            st.create()

    def test_ghz_metadata_and_props(self):
        st = GHZState(3)
        assert st._estimate_circuit_depth() == 3
        assert st._get_required_gates() == ["h", "cx"]
        assert GHZState(1)._get_required_gates() == []
        assert st.get_theoretical_properties()["entanglement_type"] == "maximal_multipartite"
        assert GHZState(1).get_theoretical_properties()["entanglement_type"] == "none"
        assert GHZState(2).get_theoretical_properties()["bell_inequality_violation"] == "maximal"
        assert "mermin_inequality_violation" in GHZState(4).get_theoretical_properties()
        assert "pathway_hypothesis" in st.get_research_context()
        assert "GHZ(3" in str(st)
        assert "no entanglement" in str(GHZState(1))

    def test_ghz_balanced_circuit_unchanged_state(self):
        # Gate-count balancing pads identities; physical state must be identical.
        st = GHZState(3, balance="gate_count")
        assert np.allclose(actual(st), actual(GHZState(3)), atol=ATOL)

    def test_ghz_multiqubit_barrier(self):
        circ = GHZState(3).create(add_barrier=True)
        assert any(instr.operation.name == "barrier" for instr in circ.data)


# ===========================================================================
# W
# ===========================================================================


class TestW:
    @pytest.mark.parametrize("n", [2, 3, 4, 5])
    def test_w_single_excitation_structure(self, n):
        sv = actual(WState(n))
        nonzero = np.flatnonzero(~np.isclose(sv, 0, atol=ATOL))
        # Exactly n nonzero amplitudes.
        assert len(nonzero) == n
        for idx in nonzero:
            # Each at a single-excitation index.
            assert popcount(int(idx)) == 1
            # Each |amp|^2 == 1/n.
            assert abs(sv[idx]) ** 2 == pytest.approx(1.0 / n, abs=1e-9)

    def test_w3_exact_amplitudes(self):
        amp = 1.0 / np.sqrt(3.0)
        assert amp == pytest.approx(0.5773502691896257, abs=1e-15)
        expected = w_statevector(3)
        sv = actual(WState(3))
        # Global phase can appear from transpilation; compare up to phase, then
        # confirm the theoretical vector is exactly the closed form.
        assert _equal_up_to_global_phase(sv, expected)
        assert np.allclose(WState(3).get_theoretical_state_vector(), expected, atol=ATOL)

    def test_w2_closed_form(self):
        expected = w_statevector(2)
        assert _equal_up_to_global_phase(actual(WState(2)), expected)
        assert np.allclose(WState(2).get_theoretical_state_vector(), expected, atol=ATOL)

    def test_w4_indices(self):
        expected = w_statevector(4)
        assert _equal_up_to_global_phase(actual(WState(4)), expected)
        assert np.allclose(WState(4).get_theoretical_state_vector(), expected, atol=ATOL)

    def test_w1_is_excited(self):
        st = WState(1)
        assert np.allclose(actual(st), [0, 1], atol=ATOL)
        assert np.allclose(st.get_theoretical_state_vector(), [0, 1], atol=ATOL)

    def test_w_create_raises_below_one_qubit(self):
        st = WState(2)
        st.num_qubits = 0
        with pytest.raises(ValueError):
            st.create()

    def test_w_barrier_and_metadata(self):
        # add_barrier path for single and multi qubit.
        assert WState(1).create(add_barrier=True).num_qubits == 1
        assert WState(3).create(add_barrier=True).num_qubits == 3
        assert WState(1)._estimate_circuit_depth() == 1
        assert WState(3)._estimate_circuit_depth() == 4
        assert WState(1)._get_required_gates() == ["x"]
        assert "cx" in WState(3)._get_required_gates()
        assert WState(1).get_theoretical_properties()["entanglement_type"] == "none"
        assert WState(3).get_theoretical_properties()["excitation_number"] == 1
        assert "pathway_hypothesis" in WState(3).get_research_context()
        assert "W(1 qubit)" in str(WState(1))
        assert "W(3 qubits)" in str(WState(3))
        assert "..." in str(WState(6))

    def test_w_balanced(self):
        st = WState(3, balance="gate_count")
        assert _equal_up_to_global_phase(actual(st), WState(3).get_theoretical_state_vector())


def _equal_up_to_global_phase(a: np.ndarray, b: np.ndarray) -> bool:
    a = np.asarray(a, dtype=complex)
    b = np.asarray(b, dtype=complex)
    # Align global phase using the largest-magnitude component of b.
    k = int(np.argmax(np.abs(b)))
    if abs(b[k]) < 1e-12 or abs(a[k]) < 1e-12:
        return bool(np.allclose(a, b, atol=ATOL))
    phase = (b[k] / abs(b[k])) * (abs(a[k]) / a[k])
    return bool(np.allclose(a * phase, b, atol=ATOL))


# ===========================================================================
# Bell
# ===========================================================================


BELL_REFS = BELL_STATEVECTORS


class TestBell:
    @pytest.mark.parametrize("variant", list(BELL_REFS))
    def test_bell_exact_no_phase_fudge(self, variant):
        st = BellState(2, {"variant": variant})
        expected = BELL_REFS[variant]
        # Exact equality (psi_minus was fixed to match this precisely).
        assert np.allclose(actual(st), expected, atol=ATOL)
        assert np.allclose(st.get_theoretical_state_vector(), expected, atol=ATOL)

    def test_bell_default_variant_phi_plus(self):
        st = BellState(2)
        assert np.allclose(actual(st), BELL_REFS["phi_plus"], atol=ATOL)

    def test_bell_requires_two_qubits(self):
        with pytest.raises(ValueError):
            BellState(3)

    def test_bell_invalid_variant(self):
        with pytest.raises(ValueError):
            BellState(2, {"variant": "nonsense"})

    @pytest.mark.parametrize(
        "variant,depth",
        [("phi_plus", 2), ("phi_minus", 3), ("psi_plus", 3), ("psi_minus", 3)],
    )
    def test_bell_depth_estimates(self, variant, depth):
        assert BellState(2, {"variant": variant})._estimate_circuit_depth() == depth

    @pytest.mark.parametrize(
        "variant,gates",
        [
            ("phi_plus", ["h", "cx"]),
            ("phi_minus", ["h", "cx", "z"]),
            ("psi_plus", ["h", "cx", "x"]),
            ("psi_minus", ["h", "cx", "z", "x"]),
        ],
    )
    def test_bell_required_gates(self, variant, gates):
        assert BellState(2, {"variant": variant})._get_required_gates() == gates

    def test_bell_props_and_context_and_str(self):
        for variant in BELL_REFS:
            st = BellState(2, {"variant": variant})
            props = st.get_theoretical_properties()
            assert props["variant"] == variant
            assert props["concurrence"] == 1.0
            assert "pathway_hypothesis" in st.get_research_context()
            assert variant.upper() in str(st)
        assert BellState(2, {"variant": "phi_plus"}).create(add_barrier=True).num_qubits == 2


# ===========================================================================
# Superposition
# ===========================================================================


class TestSuperposition:
    def test_uniform_two_qubit(self):
        st = SuperpositionState(2)
        expected = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
        assert np.allclose(actual(st), expected, atol=ATOL)
        assert np.allclose(st.get_theoretical_state_vector(), expected, atol=ATOL)

    def test_uniform_three_qubit(self):
        st = SuperpositionState(3)
        amp = 1.0 / np.sqrt(8.0)
        assert amp == pytest.approx(0.3535533905932738, abs=1e-15)
        expected = np.full(8, amp, dtype=complex)
        assert np.allclose(actual(st), expected, atol=ATOL)
        assert np.allclose(st.get_theoretical_state_vector(), expected, atol=ATOL)

    def test_endianness_regression_nonuniform(self):
        # Non-uniform per-qubit angles: theoretical kron must equal real circuit.
        angles = [{"theta": 1.0, "phi": 0.0}, {"theta": 0.5, "phi": 0.0}]
        st = SuperpositionState(2, {"angles": angles})
        assert np.allclose(
            st.get_theoretical_state_vector(),
            actual(st),
            atol=ATOL,
        )

    def test_single_qubit_plus_and_one(self):
        # theta = pi/2 -> |+>
        plus = SuperpositionState(1, {"angles": {"theta": np.pi / 2, "phi": 0.0}})
        assert np.allclose(plus.get_theoretical_state_vector(), [INV_SQRT2, INV_SQRT2], atol=ATOL)
        assert np.allclose(actual(plus), plus.get_theoretical_state_vector(), atol=ATOL)
        # theta = pi -> |1>
        one = SuperpositionState(1, {"angles": {"theta": np.pi, "phi": 0.0}})
        assert np.allclose(one.get_theoretical_state_vector(), [0, 1], atol=ATOL)
        assert np.allclose(actual(one), one.get_theoretical_state_vector(), atol=ATOL)

    def test_complex_phase_nonuniform(self):
        # With phi != 0 the circuit's Rz(phi) adds a per-qubit phase e^{-i phi/2},
        # so the prepared state equals the theoretical vector only up to a global
        # phase. Probabilities (|amp|^2) match exactly.
        angles = [{"theta": 0.7, "phi": 1.1}, {"theta": 1.3, "phi": -0.4}]
        st = SuperpositionState(2, {"angles": angles})
        th = st.get_theoretical_state_vector()
        sv = actual(st)
        assert np.allclose(np.abs(th), np.abs(sv), atol=ATOL)
        assert _equal_up_to_global_phase(sv, th)

    def test_single_dict_broadcast(self):
        st = SuperpositionState(3, {"angles": {"theta": 0.9, "phi": 0.2}})
        th = st.get_theoretical_state_vector()
        sv = actual(st)
        assert np.allclose(np.abs(th), np.abs(sv), atol=ATOL)
        assert _equal_up_to_global_phase(sv, th)

    def test_subset_qubits(self):
        st = SuperpositionState(3, {"qubits": [0, 2]})
        sv = st.get_theoretical_state_vector()
        # Qubit 1 stays |0>; only indices with bit1 == 0 are populated.
        assert np.allclose(sv, actual(st), atol=ATOL)
        for idx in range(8):
            if (idx >> 1) & 1:
                assert np.isclose(sv[idx], 0, atol=ATOL)

    def test_angles_list_with_none_entry(self):
        # None entry -> that qubit defaults to |+>.
        angles = [{"theta": 0.5, "phi": 0.0}, None]
        st = SuperpositionState(2, {"angles": angles})
        assert np.allclose(st.get_theoretical_state_vector(), actual(st), atol=ATOL)

    def test_angles_list_matches_target_subset(self):
        st = SuperpositionState(
            3,
            {"qubits": [0, 2], "angles": [{"theta": 0.3, "phi": 0.1}, {"theta": 1.0, "phi": 0.0}]},
        )
        th = st.get_theoretical_state_vector()
        sv = actual(st)
        # phi != 0 on qubit 0 -> equal up to global phase.
        assert np.allclose(np.abs(th), np.abs(sv), atol=ATOL)
        assert _equal_up_to_global_phase(sv, th)

    # --- validation / error branches ---
    def test_bad_qubits_type(self):
        with pytest.raises(ValueError):
            SuperpositionState(2, {"qubits": "some"}).create()

    def test_qubits_out_of_range(self):
        with pytest.raises(ValueError):
            SuperpositionState(2, {"qubits": [0, 5]}).create()

    def test_angles_entry_not_dict(self):
        with pytest.raises(ValueError):
            SuperpositionState(2, {"angles": [1, 2]}).create()

    def test_angles_missing_keys(self):
        with pytest.raises(ValueError):
            SuperpositionState(2, {"angles": {"theta": 0.5}}).create()

    def test_angles_bad_float(self):
        with pytest.raises(ValueError):
            SuperpositionState(2, {"angles": {"theta": "x", "phi": 0.0}}).create()

    def test_angles_wrong_length(self):
        with pytest.raises(ValueError):
            SuperpositionState(3, {"angles": [{"theta": 0.1, "phi": 0.0}]}).create()

    def test_angles_wrong_type(self):
        with pytest.raises(ValueError):
            SuperpositionState(2, {"angles": 42}).create()

    def test_metadata(self):
        assert SuperpositionState(2)._estimate_circuit_depth() == 1
        assert (
            SuperpositionState(2, {"angles": {"theta": 0.1, "phi": 0.0}})._estimate_circuit_depth()
            == 2
        )
        assert SuperpositionState(2)._get_required_gates() == ["h"]
        assert SuperpositionState(
            2, {"angles": {"theta": 0.1, "phi": 0.0}}
        )._get_required_gates() == ["ry", "rz"]
        assert SuperpositionState(2).get_theoretical_properties()["entanglement_type"] == "none"
        assert "pathway_hypothesis" in SuperpositionState(2).get_research_context()
        assert "no entanglement" in str(SuperpositionState(2))
        assert "qubits [0, 2]" in str(SuperpositionState(3, {"qubits": [0, 2]}))
        assert "Parametric" in str(SuperpositionState(2, {"angles": {"theta": 0.1, "phi": 0.0}}))
        assert SuperpositionState(2).create(add_barrier=True).num_qubits == 2
        # balanced via constructor kwarg: state unchanged by identity padding
        bal = SuperpositionState(2, {"qubits": [0]}, balance="gate_count")
        assert np.allclose(actual(bal), actual(SuperpositionState(2, {"qubits": [0]})), atol=ATOL)


# ===========================================================================
# Cluster
# ===========================================================================


class TestCluster:
    def test_1d_chain_n3_signs(self):
        st = ClusterState(3, {"lattice": "1d"})
        sv = actual(st)
        amp = 1.0 / (2.0 * np.sqrt(2.0))
        assert amp == pytest.approx(0.35355339059327373, abs=1e-15)
        expected = np.full(8, amp, dtype=complex)
        expected[3] = -amp  # |011>
        expected[6] = -amp  # |110>
        assert np.allclose(sv, expected, atol=ATOL)
        # theoretical (simulated) path
        assert np.allclose(st.get_theoretical_state_vector(), expected, atol=ATOL)

    def test_1d_chain_is_graph_state_stabilizers(self):
        # Verify K_i = X_i prod_{j in N(i)} Z_j stabilizes the n=3 chain state.
        from qiskit.quantum_info import Pauli, Statevector

        n = 3
        sv = Statevector.from_instruction(ClusterState(n, {"lattice": "1d"}).create())
        neighbors = {0: [1], 1: [0, 2], 2: [1]}
        for i in range(n):
            label = ["I"] * n
            label[i] = "X"
            for j in neighbors[i]:
                label[j] = "Z"
            # Pauli label is big-endian (qubit n-1 first); reverse our list.
            pauli = Pauli("".join(reversed(label)))
            evolved = sv.evolve(pauli)
            assert np.allclose(evolved.data, sv.data, atol=ATOL), f"K_{i} not a stabilizer"

    def test_1d_ring(self):
        st = ClusterState(4, {"lattice": "1d", "ring": True})
        sv = actual(st)
        assert np.isclose(np.linalg.norm(sv), 1.0, atol=ATOL)
        # ring adds the (n-1,0) edge -> appears in metadata via num_edges
        props = st.get_theoretical_properties()
        assert props["num_edges"] == 4  # 3 chain + 1 wrap

    def test_2d_grid(self):
        st = ClusterState(6, {"lattice": "2d", "rows": 2, "cols": 3})
        sv = actual(st)
        assert np.isclose(np.linalg.norm(sv), 1.0, atol=ATOL)
        # all amplitudes have equal magnitude (graph state from H^n + CZ)
        assert np.allclose(np.abs(sv), 1.0 / np.sqrt(64), atol=ATOL)

    def test_2d_torus(self):
        st = ClusterState(9, {"lattice": "2d", "rows": 3, "cols": 3, "ring": True})
        sv = actual(st)
        assert np.isclose(np.linalg.norm(sv), 1.0, atol=ATOL)
        assert "torus" in str(st)

    def test_invalid_lattice(self):
        with pytest.raises(ValueError):
            ClusterState(3, {"lattice": "3d"}).create()

    def test_2d_missing_dims(self):
        with pytest.raises(ValueError):
            ClusterState(4, {"lattice": "2d"}).create()

    def test_2d_bad_dims(self):
        with pytest.raises(ValueError):
            ClusterState(4, {"lattice": "2d", "rows": 0, "cols": 4}).create()

    def test_2d_dim_mismatch(self):
        with pytest.raises(ValueError):
            ClusterState(5, {"lattice": "2d", "rows": 2, "cols": 3}).create()

    def test_create_raises_below_one_qubit(self):
        st = ClusterState(2)
        st.num_qubits = 0
        with pytest.raises(ValueError):
            st.create()

    def test_large_system_blocks_statevector(self):
        # >15 qubits should raise in _validate_large_system before simulation.
        st = ClusterState(16, {"lattice": "1d"})
        with pytest.raises(ValueError):
            st.get_theoretical_state_vector()

    def test_metadata(self):
        st = ClusterState(3, {"lattice": "1d"})
        assert st._estimate_circuit_depth() == 2
        assert st._get_required_gates() == ["h", "cz"]
        props = st.get_theoretical_properties()
        assert props["graph_topology"] == "1d"
        props2d = ClusterState(
            6, {"lattice": "2d", "rows": 2, "cols": 3}
        ).get_theoretical_properties()
        assert props2d["graph_topology"] == "2d"
        assert "pathway_hypothesis" in st.get_research_context()
        assert "chain" in str(st)
        assert "ring" in str(ClusterState(4, {"lattice": "1d", "ring": True}))
        assert "grid" in str(ClusterState(6, {"lattice": "2d", "rows": 2, "cols": 3}))
        assert st.create(add_barrier=True).num_qubits == 3

    def test_balanced(self):
        # exercise the config-dict balance path (construction must succeed)
        ClusterState(3, {"lattice": "1d", "balance": "gate_count"})
        # balance only via constructor kwarg
        bal = ClusterState(3, {"lattice": "1d"}, balance="gate_count")
        assert np.allclose(actual(bal), actual(ClusterState(3, {"lattice": "1d"})), atol=ATOL)


# ===========================================================================
# Custom
# ===========================================================================


@pytest.fixture
def fake_builder_module():
    mod = types.ModuleType("qf_test_builder_mod")

    def make(n):
        qc = QuantumCircuit(n)
        qc.h(0)
        qc.cx(0, 1)
        return qc

    def wrong_num(n):
        return QuantumCircuit(n + 1)

    def not_a_circuit(n):
        return "not a circuit"

    mod.make = make
    mod.wrong_num = wrong_num
    mod.not_a_circuit = not_a_circuit
    sys.modules["qf_test_builder_mod"] = mod
    yield mod
    del sys.modules["qf_test_builder_mod"]


class TestCustom:
    def test_gates_source_builds_bell(self):
        st = CustomState(
            2,
            {
                "source": "gates",
                "num_qubits": 2,
                "gates": [
                    {"name": "h", "qargs": [0]},
                    {"name": "cx", "qargs": [0, 1]},
                ],
            },
        )
        expected = np.array([INV_SQRT2, 0, 0, INV_SQRT2], dtype=complex)
        assert np.allclose(actual(st), expected, atol=ATOL)
        # theoretical (simulated) path
        assert np.allclose(st.get_theoretical_state_vector(), expected, atol=ATOL)

    def test_gates_source_with_params(self):
        st = CustomState(
            1,
            {
                "source": "gates",
                "num_qubits": 1,
                "gates": [{"name": "rx", "qargs": [0], "params": [np.pi]}],
            },
        )
        sv = actual(st)
        # Rx(pi)|0> = -i|1>
        assert np.isclose(abs(sv[1]), 1.0, atol=ATOL)

    def test_circuit_source_passthrough(self):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        st = CustomState(2, {"source": "circuit", "circuit": qc})
        expected = np.array([INV_SQRT2, 0, 0, INV_SQRT2], dtype=complex)
        assert np.allclose(actual(st), expected, atol=ATOL)

    def test_builder_source(self, fake_builder_module):
        st = CustomState(
            2, {"source": "builder", "num_qubits": 2, "builder": "qf_test_builder_mod:make"}
        )
        expected = np.array([INV_SQRT2, 0, 0, INV_SQRT2], dtype=complex)
        assert np.allclose(actual(st), expected, atol=ATOL)

    def test_openqasm_source(self, tmp_path):
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nh q[0];\ncx q[0],q[1];\n'
        path = tmp_path / "bell.qasm"
        path.write_text(qasm)
        st = CustomState(2, {"source": "openqasm", "openqasm": str(path), "num_qubits": 2})
        expected = np.array([INV_SQRT2, 0, 0, INV_SQRT2], dtype=complex)
        assert np.allclose(actual(st), expected, atol=ATOL)

    # --- validation errors ---
    def test_bad_source(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "bogus"}).create()

    def test_gates_bad_num_qubits(self):
        with pytest.raises(ValueError):
            CustomState(
                2, {"source": "gates", "num_qubits": 0, "gates": [{"name": "h", "qargs": [0]}]}
            ).create()

    def test_gates_empty(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "gates", "num_qubits": 2, "gates": []}).create()

    def test_gates_not_list(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "gates", "num_qubits": 2, "gates": "h"}).create()

    def test_gates_entry_not_dict(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "gates", "num_qubits": 2, "gates": ["h"]}).create()

    def test_gates_bad_name(self):
        with pytest.raises(ValueError):
            CustomState(
                2, {"source": "gates", "num_qubits": 2, "gates": [{"name": "", "qargs": [0]}]}
            ).create()

    def test_gates_bad_qargs(self):
        with pytest.raises(ValueError):
            CustomState(
                2, {"source": "gates", "num_qubits": 2, "gates": [{"name": "h", "qargs": "0"}]}
            ).create()

    def test_gates_qargs_out_of_range(self):
        with pytest.raises(ValueError):
            CustomState(
                2, {"source": "gates", "num_qubits": 2, "gates": [{"name": "h", "qargs": [9]}]}
            ).create()

    def test_circuit_source_not_circuit(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "circuit", "circuit": "nope"}).create()

    def test_circuit_source_num_mismatch(self):
        qc = QuantumCircuit(3)
        with pytest.raises(ValueError):
            CustomState(2, {"source": "circuit", "circuit": qc}).create()

    def test_builder_not_dotted(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "builder", "num_qubits": 2, "builder": "nodots"}).create()

    def test_builder_bad_num(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "builder", "num_qubits": 0, "builder": "a.b:c"}).create()

    def test_builder_returns_non_circuit(self, fake_builder_module):
        with pytest.raises(ValueError):
            CustomState(
                2,
                {
                    "source": "builder",
                    "num_qubits": 2,
                    "builder": "qf_test_builder_mod:not_a_circuit",
                },
            ).create()

    def test_builder_wrong_num(self, fake_builder_module):
        with pytest.raises(ValueError):
            CustomState(
                2,
                {"source": "builder", "num_qubits": 2, "builder": "qf_test_builder_mod:wrong_num"},
            ).create()

    def test_openqasm_not_str(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "openqasm", "openqasm": 123}).create()

    def test_openqasm_missing_file(self):
        with pytest.raises(ValueError):
            CustomState(2, {"source": "openqasm", "openqasm": "does_not_exist_12345.qasm"}).create()

    def test_openqasm_num_mismatch(self, tmp_path):
        qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nh q[0];\n'
        path = tmp_path / "x.qasm"
        path.write_text(qasm)
        with pytest.raises(ValueError):
            CustomState(2, {"source": "openqasm", "openqasm": str(path), "num_qubits": 3}).create()

    def test_metadata_and_fallbacks(self):
        good = {
            "source": "gates",
            "num_qubits": 2,
            "gates": [{"name": "h", "qargs": [0]}, {"name": "cx", "qargs": [0, 1]}],
        }
        st = CustomState(2, good)
        assert st._estimate_circuit_depth() >= 1
        assert "h" in st._get_required_gates()
        assert st.get_theoretical_properties()["entanglement_type"] == "user_defined"
        assert "pathway_hypothesis" in st.get_research_context()
        assert "user-defined" in str(st)
        assert st.create(add_barrier=True).num_qubits == 2
        # __str__ for each source variant
        assert "builder" in str(CustomState(2, {"source": "builder", "builder": "m:f"}))
        assert "from" in str(CustomState(2, {"source": "openqasm", "openqasm": "/tmp/a.qasm"}))
        assert "source: circuit" in str(CustomState(2, {"source": "circuit"}))

    def test_estimate_depth_exception_fallback(self):
        # invalid spec -> create() raises -> _estimate_circuit_depth returns n
        bad = CustomState(3, {"source": "bogus"})
        assert bad._estimate_circuit_depth() == 3
        assert bad._get_required_gates() == ["h", "cx", "u3"]

    def test_gates_many_names_str(self):
        gates = [{"name": "h", "qargs": [0]} for _ in range(5)]
        st = CustomState(1, {"source": "gates", "num_qubits": 1, "gates": gates})
        assert "more" in str(st)


# ===========================================================================
# Factory + constants
# ===========================================================================


class TestFactory:
    @pytest.mark.parametrize(
        "state_type,n,params",
        [
            ("GHZ", 3, None),
            ("BELL", 2, {"variant": "phi_plus"}),
            ("W", 3, None),
            ("CLUSTER", 3, {"lattice": "1d"}),
            ("SUPERPOSITION", 2, None),
            (
                "CUSTOM",
                2,
                {"source": "gates", "num_qubits": 2, "gates": [{"name": "h", "qargs": [0]}]},
            ),
        ],
    )
    def test_prepare_state_each_type(self, state_type, n, params):
        circ = prepare_state(state_type, n, custom_params=params)
        assert isinstance(circ, QuantumCircuit)
        assert circ.num_qubits == n

    def test_prepare_state_unknown_type(self):
        with pytest.raises(ValueError) as exc:
            prepare_state("BOGUS", 3)
        # error lists available states
        assert "Available states" in str(exc.value)

    def test_prepare_state_wraps_inner_error(self):
        # BELL with 3 qubits raises inside -> wrapped as "Failed to create"
        with pytest.raises(ValueError) as exc:
            prepare_state("BELL", 3)
        assert "Failed to create" in str(exc.value)

    def test_prepare_state_with_balance(self):
        circ = prepare_state("GHZ", 3, balance="gate_count")
        assert isinstance(circ, QuantumCircuit)

    def test_create_state_instance(self):
        inst = create_state_instance("GHZ", 3)
        assert isinstance(inst, GHZState)
        with pytest.raises(ValueError):
            create_state_instance("BOGUS", 3)

    def test_get_available_states_six_keys(self):
        states = get_available_states()
        assert set(states) == {"GHZ", "BELL", "W", "CLUSTER", "SUPERPOSITION", "CUSTOM"}
        assert len(states) == 6

    def test_validate_state_request_branches(self):
        assert validate_state_request("BOGUS", 3) == ["Unknown state type: BOGUS"]
        assert any("at least 1 qubit" in w for w in validate_state_request("GHZ", 0))
        assert any("Large quantum system" in w for w in validate_state_request("GHZ", 25))
        assert any("exactly 2 qubits" in w for w in validate_state_request("BELL", 3))
        assert any("at least 2 qubits" in w for w in validate_state_request("W", 1))
        assert validate_state_request("GHZ", 3) == []

    def test_prepare_state_for_hardware_no_backend(self):
        circ = prepare_state_for_hardware("GHZ", 3)
        assert isinstance(circ, QuantumCircuit)

    def test_prepare_state_for_hardware_compatible(self):
        backend = _FakeBackend(n_qubits=10)
        circ = prepare_state_for_hardware("GHZ", 3, backend=backend)
        assert isinstance(circ, QuantumCircuit)

    def test_prepare_state_for_hardware_incompatible(self):
        backend = _FakeBackend(n_qubits=1)
        with pytest.raises(ValueError):
            prepare_state_for_hardware("GHZ", 3, backend=backend)

    def test_prepare_state_for_hardware_config_error(self):
        with pytest.raises(ValueError):
            prepare_state_for_hardware("GHZ", 3, backend=_BrokenBackend())


class TestConstants:
    def test_get_state_class(self):
        assert sc.get_state_class("GHZ") is GHZState
        with pytest.raises(ValueError):
            sc.get_state_class("BOGUS")

    def test_get_available_states_sorted(self):
        assert sc.get_available_states() == sorted(
            ["BELL", "CLUSTER", "CUSTOM", "GHZ", "SUPERPOSITION", "W"]
        )

    def test_get_state_info(self):
        info = sc.get_state_info()
        assert len(info) == 6
        assert info["GHZ"]["entanglement_type"] == "maximal_multipartite"

    def test_validate_registry(self):
        assert sc.validate_state_registry() is True

    def test_validate_registry_rejects_non_basestate(self, monkeypatch):
        class NotAState:
            pass

        monkeypatch.setitem(sc.STATE_CLASSES, "BAD", NotAState)
        with pytest.raises(TypeError):
            sc.validate_state_registry()

    def test_validate_registry_rejects_missing_method(self, monkeypatch):
        # Subclass of BaseState but missing a required method.
        class PartialState(BaseState):
            def create(self, add_barrier: bool = False) -> QuantumCircuit:
                return QuantumCircuit(self.num_qubits)

        # Remove a required method so the registry check fails.
        monkeypatch.delattr(PartialState, "get_research_context", raising=False)
        monkeypatch.setitem(sc.STATE_CLASSES, "PARTIAL", PartialState)
        with pytest.raises(RuntimeError):
            sc.validate_state_registry()


# ===========================================================================
# Base state helpers
# ===========================================================================


class _MinimalState(BaseState):
    """Concrete BaseState used to exercise default base-class behavior."""

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)
        if add_barrier:
            qc.barrier()
        return qc


class TestBaseState:
    def test_default_theoretical_state_vector(self):
        st = _MinimalState(2)
        sv = st.get_theoretical_state_vector()
        expected = np.zeros(4, dtype=complex)
        expected[0] = 1.0
        assert np.allclose(sv, expected, atol=ATOL)

    def test_init_rejects_zero_qubits(self):
        with pytest.raises(ValueError):
            _MinimalState(0)

    def test_init_warns_large_system(self):
        # >25 qubits triggers a warning but still constructs.
        st = _MinimalState(26)
        assert st.num_qubits == 26

    def test_basic_properties_and_metadata(self):
        st = _MinimalState(3)
        bp = st.get_basic_properties()
        assert bp["num_qubits"] == 3
        assert bp["hilbert_dimension"] == 8
        assert bp["has_entanglement"] is True
        meta = st.get_research_metadata()
        assert meta["num_qubits"] == 3
        assert "structured_decoherence_pathways" in meta["research_framework"]

    def test_default_depth_and_gates(self):
        st = _MinimalState(4)
        assert st._estimate_circuit_depth() == 4
        assert st._get_required_gates() == ["h", "cx"]

    def test_str_and_repr(self):
        st = _MinimalState(2)
        assert "_MinimalState" in str(st)
        assert "num_qubits=2" in repr(st)
        st.log_state_creation("Test", {"k": "v"})  # exercise logging path

    def test_validate_for_hardware_branches(self):
        st = _MinimalState(3)
        assert any("supports maximum" in w for w in st.validate_for_hardware({"max_qubits": 2}))
        assert any("depth" in w for w in st.validate_for_hardware({"max_circuit_depth": 1}))
        assert any(
            "unsupported gates" in w for w in st.validate_for_hardware({"supported_gates": ["h"]})
        )
        assert any(
            "sensitive to decoherence" in w for w in _MinimalState(11).validate_for_hardware({})
        )
        assert st.validate_for_hardware({}) == []

    def test_validate_large_system(self):
        # warning branch (>10, <=15)
        _MinimalState(12)._validate_large_system("op")  # no raise
        # hard limit
        with pytest.raises(ValueError):
            _MinimalState(16)._validate_large_system("op")

    def test_generate_fallback_state_normalized(self):
        st = _MinimalState(3)
        fb = st._generate_fallback_state(3)
        assert fb.shape == (8,)
        assert np.isclose(np.linalg.norm(fb), 1.0, atol=ATOL)

    def test_simulate_too_many_qubits(self):
        st = _MinimalState(2)
        big = QuantumCircuit(21)
        with pytest.raises(ValueError):
            st._simulate_circuit_state_vector(big)

    def test_simulate_success(self):
        st = _MinimalState(2)
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        sv = st._simulate_circuit_state_vector(qc)
        assert np.isclose(np.linalg.norm(sv), 1.0, atol=ATOL)

    def test_simulate_fallback_on_import_failure(self, monkeypatch):
        # Make `from qiskit_aer import AerSimulator` fail -> fallback path.
        broken = types.ModuleType("qiskit_aer")  # no AerSimulator attribute
        monkeypatch.setitem(sys.modules, "qiskit_aer", broken)
        st = _MinimalState(2)
        qc = QuantumCircuit(2)
        qc.h(0)
        sv = st._simulate_circuit_state_vector(qc)
        # Random normalized fallback.
        assert sv.shape == (4,)
        assert np.isclose(np.linalg.norm(sv), 1.0, atol=ATOL)

    def test_gate_count_balancing(self):
        st = _MinimalState(3)
        qc = QuantumCircuit(3)
        qc.h(0)
        qc.cx(0, 1)
        qc.barrier()
        out = st._apply_gate_count_balancing(qc)
        assert out.metadata["balanced"] is True
        assert "padding_per_qubit" in out.metadata


# ===========================================================================
# Fake backends for hardware-aware factory tests
# ===========================================================================


class _FakeConfig:
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.basis_gates = ["h", "cx", "z", "x", "cz", "rz", "sx"]
        self.coupling_map = None
        self.max_shots = 8192
        self.backend_name = "fake_backend"


class _FakeBackend:
    def __init__(self, n_qubits):
        self._cfg = _FakeConfig(n_qubits)

    def configuration(self):
        return self._cfg


class _BrokenBackend:
    def configuration(self):
        raise RuntimeError("config unavailable")
