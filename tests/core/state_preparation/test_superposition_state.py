from src.core.state_preparation import prepare_state


def test_superposition_default_plus_state():
    qc = prepare_state('SUPERPOSITION', 3)
    # Should only contain H gates, depth 1
    assert qc.num_qubits == 3
    assert qc.depth() >= 1


def test_superposition_subset_qubits():
    qc = prepare_state('SUPERPOSITION', 3, custom_params={'qubits': [0, 2]})
    assert qc.num_qubits == 3
    # No entangling gates should be present
    assert 'cx' not in qc.count_ops()
    assert 'cz' not in qc.count_ops()


def test_superposition_parametric_angles():
    qc = prepare_state('SUPERPOSITION', 3, custom_params={'angles': {'theta': 1.0, 'phi': 0.5}})
    ops = qc.count_ops()
    # Ry and Rz present, no CX/CZ
    assert 'ry' in {k.lower() for k in ops.keys()}
    assert 'rz' in {k.lower() for k in ops.keys()}
    assert 'cx' not in {k.lower() for k in ops.keys()}
    assert 'cz' not in {k.lower() for k in ops.keys()}

