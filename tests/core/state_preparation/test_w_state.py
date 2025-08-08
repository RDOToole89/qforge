from qiskit.quantum_info import Statevector
from src.core.state_preparation import prepare_state
import numpy as np


def test_w_state_initialize_exact_norm():
    n = 3
    qc = prepare_state('W', n)
    sv = Statevector.from_instruction(qc)
    probs = np.abs(sv.data) ** 2
    # Exactly n basis states with 1/n probability
    assert np.isclose(probs.sum(), 1.0)
    assert np.isclose((probs > 0).sum(), n)
    assert np.allclose(sorted([p for p in probs if p > 0]), [1/n]*n)

