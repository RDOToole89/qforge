# src/state_preparation/custom_state.py

from __future__ import annotations

import json
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any

from qiskit import QuantumCircuit
from .base_state import BaseState


class CustomState(BaseState):
    """
    Flexible custom state preparation with research-grade validation and logging.

    custom_params schema (one and only one source must be provided):
      - source: 'gates' | 'builder' | 'openqasm'
      - gates: List[{
            'name': str,
            'qargs': List[int],
            'params': Optional[List[float]],
            'cargs': Optional[List[int]]
        }]
      - builder: str  # dotted path 'package.module:function'
      - openqasm: str # path to .qasm file
      - num_qubits: int (required for gates and builder; optional for openqasm)
      - validate: bool = True
      - metadata: Dict[str, Any] (optional)
    """

    def create(self, add_barrier: bool = False, experiment_id: str = "N/A") -> QuantumCircuit:
        params: Dict[str, Any] = self.custom_params or {}

        source = params.get("source")
        validate = bool(params.get("validate", True))
        metadata = params.get("metadata", {})

        if source not in {"gates", "builder", "openqasm"}:
            raise ValueError("CustomState requires 'source' to be one of 'gates'|'builder'|'openqasm'")

        if source == "gates":
            num_qubits = params.get("num_qubits")
            if not isinstance(num_qubits, int) or num_qubits <= 0:
                raise ValueError("'num_qubits' must be a positive integer for gates source")
            qc = QuantumCircuit(num_qubits)
            gates: List[Dict[str, Any]] = params.get("gates", [])
            if not isinstance(gates, list) or not gates:
                raise ValueError("'gates' must be a non-empty list for gates source")
            for i, g in enumerate(gates):
                if not isinstance(g, dict):
                    raise ValueError("Each gate entry must be a dict")
                name = g.get("name")
                qargs = g.get("qargs", [])
                par = g.get("params", [])
                cargs = g.get("cargs", [])
                if not isinstance(name, str) or not name:
                    raise ValueError("Gate 'name' must be a non-empty string")
                if not isinstance(qargs, list) or not all(isinstance(q, int) for q in qargs):
                    raise ValueError("Gate 'qargs' must be a list of integers")
                if validate:
                    for q in qargs:
                        if q < 0 or q >= num_qubits:
                            raise ValueError("qargs index out of range")
                # Append gate operation
                method = getattr(qc, name)
                if par and cargs:
                    method(*par, *qargs, *cargs)  # rarely used path
                elif par:
                    method(*par, *qargs)
                else:
                    method(*qargs)

        elif source == "builder":
            builder_path = params.get("builder")
            num_qubits = params.get("num_qubits")
            if not isinstance(builder_path, str) or ":" not in builder_path:
                raise ValueError("'builder' must be a dotted path 'package.module:function'")
            if not isinstance(num_qubits, int) or num_qubits <= 0:
                raise ValueError("'num_qubits' must be a positive integer for builder source")
            mod_path, func_name = builder_path.split(":", 1)
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name)
            qc = func(num_qubits)
            if not isinstance(qc, QuantumCircuit):
                raise ValueError("builder did not return a QuantumCircuit")
            if validate and qc.num_qubits != num_qubits:
                raise ValueError("builder returned circuit with unexpected num_qubits")

        else:  # openqasm
            qasm_path = params.get("openqasm")
            if not isinstance(qasm_path, str):
                raise ValueError("'openqasm' must be a file path string")
            path = Path(qasm_path)
            if not path.exists():
                raise ValueError("OpenQASM file not found")
            qc = QuantumCircuit.from_qasm_file(str(path))
            num_qubits = params.get("num_qubits")
            if num_qubits is not None and validate and qc.num_qubits != num_qubits:
                raise ValueError("QASM circuit num_qubits mismatch")

        if add_barrier:
            qc.barrier()

        # Structured logging with provenance metadata
        meta = {
            "source": source,
            "num_qubits": qc.num_qubits,
            "depth": qc.depth(),
            "gate_counts": {k.lower(): int(v) for k, v in qc.count_ops().items()},
        }
        if metadata:
            meta["user_metadata"] = metadata
        self.log_state_creation(state_type="CUSTOM", extra_info=meta)

        return qc

