import pytest
from qiskit.quantum_info import Statevector
from src.core.state_preparation import prepare_state


@pytest.mark.parametrize("variant,expected",
    [
        ("phi_plus",  (1, 0, 0, 1)),
        ("phi_minus", (1, 0, 0, -1)),
        ("psi_plus",  (0, 1, 1, 0)),
        ("psi_minus", (0, 1, -1, 0)),
    ]
)
def test_bell_variants_statevector(variant, expected):
    qc = prepare_state('BELL', 2, custom_params={'variant': variant})
    sv = Statevector.from_instruction(qc)
    amps = tuple(round(a, 6) for a in sv.data)
    # Compare magnitude pattern (signs included where applicable)
    # Normalize expected by 1/sqrt(2)
    import numpy as np
    norm = 1/np.sqrt(2)
    expected_sv = tuple(e*norm for e in expected)
    # Allow small numerical differences
    for a, b in zip(amps, expected_sv):
        assert pytest.approx(a.real, rel=1e-6, abs=1e-6) == b


def test_bell_requires_two_qubits():
    with pytest.raises(ValueError):
        prepare_state('BELL', 3)

