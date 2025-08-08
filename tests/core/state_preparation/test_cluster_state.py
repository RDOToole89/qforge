import pytest
from src.core.state_preparation import prepare_state


def test_cluster_1d_linear():
    qc = prepare_state('CLUSTER', 4, custom_params={'lattice': '1d'})
    ops = qc.count_ops()
    # Expect H on all and CZ entanglement
    assert 'h' in {k.lower() for k in ops}
    assert 'cz' in {k.lower() for k in ops}


def test_cluster_1d_ring():
    qc = prepare_state('CLUSTER', 4, custom_params={'lattice': '1d', 'ring': True})
    ops = qc.count_ops()
    assert 'cz' in {k.lower() for k in ops}


def test_cluster_2d_requires_rows_cols():
    with pytest.raises(ValueError):
        prepare_state('CLUSTER', 4, custom_params={'lattice': '2d'})


def test_cluster_2d_grid():
    # 2x3 grid → 6 qubits
    qc = prepare_state('CLUSTER', 6, custom_params={'lattice': '2d', 'rows': 2, 'cols': 3})
    ops = qc.count_ops()
    assert 'cz' in {k.lower() for k in ops}

