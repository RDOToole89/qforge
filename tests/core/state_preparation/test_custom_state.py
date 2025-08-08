import json
import textwrap
import pytest
from pathlib import Path
from src.core.state_preparation import prepare_state


def test_custom_gates_simple_h_cx(tmp_path):
    params = {
        'source': 'gates',
        'num_qubits': 2,
        'gates': [
            {'name': 'h', 'qargs': [0]},
            {'name': 'cx', 'qargs': [0, 1]},
        ],
    }
    qc = prepare_state('CUSTOM', 2, custom_params=params)
    ops = {k.lower(): v for k, v in qc.count_ops().items()}
    assert ops.get('h', 0) >= 1
    assert ops.get('cx', 0) >= 1


def test_custom_gates_invalid_index_raises():
    params = {
        'source': 'gates',
        'num_qubits': 2,
        'gates': [
            {'name': 'h', 'qargs': [2]},  # out of range
        ],
    }
    with pytest.raises(ValueError):
        prepare_state('CUSTOM', 2, custom_params=params)


def test_custom_openqasm(tmp_path):
    qasm = textwrap.dedent(
        """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        h q[0];
        cx q[0],q[1];
        """
    )
    p = tmp_path / "test.qasm"
    p.write_text(qasm)
    params = {
        'source': 'openqasm',
        'openqasm': str(p),
        'num_qubits': 2,
    }
    qc = prepare_state('CUSTOM', 2, custom_params=params)
    ops = {k.lower(): v for k, v in qc.count_ops().items()}
    assert ops.get('h', 0) >= 1
    assert ops.get('cx', 0) >= 1


def test_custom_builder(tmp_path, monkeypatch):
    # Create a temporary module with a builder function
    module_code = textwrap.dedent(
        """
        from qiskit import QuantumCircuit
        def make_qc(n):
            qc = QuantumCircuit(n)
            qc.h(0)
            return qc
        """
    )
    mod_dir = tmp_path / "m"
    mod_dir.mkdir()
    (mod_dir / "__init__.py").write_text("")
    (mod_dir / "builders.py").write_text(module_code)
    monkeypatch.syspath_prepend(str(tmp_path))

    params = {
        'source': 'builder',
        'builder': 'm.builders:make_qc',
        'num_qubits': 2,
    }
    qc = prepare_state('CUSTOM', 2, custom_params=params)
    ops = {k.lower(): v for k, v in qc.count_ops().items()}
    assert ops.get('h', 0) >= 1

