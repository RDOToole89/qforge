"""Exact-value tests for intermediary theoretical-property calculations of states.

These quantities are returned by ``get_theoretical_properties()`` on each state
class but their numeric outputs were never asserted directly. Each value below is
a closed-form quantum-information quantity verified against the implementation.

Run with::

    pytest tests/physics/test_state_intermediates_verified.py
"""

from __future__ import annotations

import pytest

from qforge.core.state_preparation.bell_state import BellState
from qforge.core.state_preparation.cluster_state import ClusterState
from qforge.core.state_preparation.ghz_state import GHZState
from qforge.core.state_preparation.superposition_state import SuperpositionState
from qforge.core.state_preparation.w_state import WState

# --------------------------------------------------------------------------- #
# GHZ states
# --------------------------------------------------------------------------- #


def test_ghz_mermin_violation_three_qubits() -> None:
    """Mermin inequality violation 2^(n/2) = 2^1.5 for n=3."""
    props = GHZState(3).get_theoretical_properties()
    assert props["mermin_inequality_violation"] == pytest.approx(2.8284271247461903, rel=1e-12)


def test_ghz_mermin_violation_four_qubits() -> None:
    """Mermin inequality violation 2^(n/2) = 2^2 = 4.0 for n=4."""
    props = GHZState(4).get_theoretical_properties()
    assert props["mermin_inequality_violation"] == pytest.approx(4.0, rel=1e-12)


def test_ghz_schmidt_rank_and_measurement_probabilities() -> None:
    """GHZ has Schmidt rank 2 and 50/50 all-zeros/all-ones measurement weight."""
    props = GHZState(3).get_theoretical_properties()
    assert props["schmidt_rank"] == 2
    meas = props["measurement_probabilities"]
    assert meas["all_zeros"] == pytest.approx(0.5, rel=1e-12)
    assert meas["all_ones"] == pytest.approx(0.5, rel=1e-12)
    assert meas["mixed_outcomes"] == 0.0


# --------------------------------------------------------------------------- #
# W states
# --------------------------------------------------------------------------- #


def test_w_single_qubit_excitation_probability() -> None:
    """Single-qubit excitation probability 1/n = 1/3 for n=3."""
    props = WState(3).get_theoretical_properties()
    assert props["single_qubit_excitation_probability"] == pytest.approx(
        0.3333333333333333, rel=1e-12
    )


# --------------------------------------------------------------------------- #
# Bell states
# --------------------------------------------------------------------------- #


def test_bell_entropy_schmidt_and_classical_bound() -> None:
    """Bell state: von Neumann entropy log2(2)=1, Schmidt rank 2, CHSH bound 0.5."""
    props = BellState(2).get_theoretical_properties()
    assert props["von_neumann_entropy"] == pytest.approx(1.0, rel=1e-12)
    assert props["schmidt_rank"] == 2
    assert props["classical_correlation_bound"] == pytest.approx(0.5, rel=1e-12)


# --------------------------------------------------------------------------- #
# Cluster states
# --------------------------------------------------------------------------- #


def test_cluster_num_edges_2d_grid() -> None:
    """2D 2x3 grid edges = rows*(cols-1) + cols*(rows-1) = 2*2 + 3*1 = 7."""
    props = ClusterState(
        6, custom_params={"lattice": "2d", "rows": 2, "cols": 3}
    ).get_theoretical_properties()
    assert props["num_edges"] == 7


def test_cluster_schmidt_diameter_stabilizers_chain() -> None:
    """1D chain n=3: Schmidt rank 2^(n-1)=4, diameter n-1=2, n stabilizers."""
    props = ClusterState(3).get_theoretical_properties()
    assert props["schmidt_rank"] == 4
    assert props["graph_diameter"] == 2
    assert props["stabilizer_generators"] == 3


# --------------------------------------------------------------------------- #
# Superposition (product) states
# --------------------------------------------------------------------------- #


def test_superposition_entropy_and_schmidt_rank() -> None:
    """Fully separable product state: zero entanglement entropy, Schmidt rank 1."""
    props = SuperpositionState(3).get_theoretical_properties()
    assert props["von_neumann_entropy"] == 0.0
    assert props["schmidt_rank"] == 1
