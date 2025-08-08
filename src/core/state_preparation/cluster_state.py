# src/state_preparation/cluster_state.py

from qiskit import QuantumCircuit
from .base_state import BaseState

class ClusterState(BaseState):
    """
    Cluster state preparation for a 1D or 2D lattice.
    """

    def create(self, add_barrier: bool = False, experiment_id: str = "N/A") -> QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)
        # Parameters
        lattice = (self.custom_params or {}).get("lattice", "1d").lower()
        ring = bool((self.custom_params or {}).get("ring", False))
        rows = (self.custom_params or {}).get("rows")
        cols = (self.custom_params or {}).get("cols")

        # Prepare H on all qubits
        qc.h(range(self.num_qubits))

        if lattice == "1d":
            # Linear chain CZ; optional periodic coupling
            for i in range(self.num_qubits - 1):
                qc.cz(i, i + 1)
            if ring and self.num_qubits > 2:
                qc.cz(self.num_qubits - 1, 0)
            meta = {"lattice": lattice, "ring": ring}

        elif lattice == "2d":
            if rows is None or cols is None:
                raise ValueError("2d cluster requires 'rows' and 'cols' in custom_params")
            if not isinstance(rows, int) or not isinstance(cols, int) or rows <= 0 or cols <= 0:
                raise ValueError("'rows' and 'cols' must be positive integers")
            if rows * cols != self.num_qubits:
                raise ValueError("rows*cols must equal num_qubits for 2d cluster")

            # Index map: (r, c) -> q = r*cols + c
            def qidx(r, c):
                return r * cols + c

            # Horizontal edges
            for r in range(rows):
                for c in range(cols - 1):
                    qc.cz(qidx(r, c), qidx(r, c + 1))
                if ring and cols > 2:
                    qc.cz(qidx(r, cols - 1), qidx(r, 0))

            # Vertical edges
            for c in range(cols):
                for r in range(rows - 1):
                    qc.cz(qidx(r, c), qidx(r + 1, c))
                if ring and rows > 2:
                    qc.cz(qidx(rows - 1, c), qidx(0, c))

            meta = {"lattice": lattice, "rows": rows, "cols": cols, "ring": ring}
        else:
            raise ValueError("Unsupported lattice. Use '1d' or '2d'")

        if add_barrier:
            qc.barrier()
        self.log_state_creation(state_type="CLUSTER", extra_info=meta)
        return qc
