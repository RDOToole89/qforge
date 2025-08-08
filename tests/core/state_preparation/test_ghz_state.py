from src.core.state_preparation import prepare_state


def test_ghz_min_qubits_and_structure():
    qc = prepare_state('GHZ', 3)
    ops = {k.lower(): v for k, v in qc.count_ops().items()}
    assert qc.num_qubits == 3
    assert 'h' in ops and ops['h'] >= 1
    assert 'cx' in ops and ops['cx'] >= 2  # chain entanglement

