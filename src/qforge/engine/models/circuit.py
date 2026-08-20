"""Circuit Statistics Model."""

from __future__ import annotations

import logging
from typing import Any, cast

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class CircuitStatistics(BaseModel):
    """Quantum circuit characteristics and statistics."""

    depth: int = Field(ge=0, description="Circuit depth (number of time steps)")
    num_gates: int = Field(ge=0, description="Total number of gates")
    num_qubits: int = Field(ge=1, description="Number of qubits")

    gate_types: dict[str, int] = Field(
        default_factory=dict, description="Count of each gate type used"
    )

    two_qubit_gate_count: int | None = Field(
        default=None,
        ge=0,
        description="Number of two-qubit gates (entangling operations)",
    )

    connectivity_graph: list[list[int]] | None = Field(
        default=None,
        description="Qubit connectivity graph for multi-qubit operations",
    )

    @model_validator(mode="after")
    def _reconcile_circuit_stats(self) -> CircuitStatistics:
        """Auto-heal common inconsistencies.

        - If gate_types sum doesn't match num_gates, set num_gates = sum(gate_types)
        - Clamp two_qubit_gate_count to [0, num_gates]
        - Sanitize connectivity_graph as list of 2-int edges within [0, num_qubits-1].
        """
        if self.gate_types:
            summed = sum(int(v) for v in self.gate_types.values())
            if summed != self.num_gates:
                logger.warning(
                    f"[CircuitStatistics] num_gates={self.num_gates} "
                    f"!= sum(gate_types)={summed}; reconciling to {summed}"
                )
                self.num_gates = summed

        if self.two_qubit_gate_count is not None:
            if self.two_qubit_gate_count > self.num_gates:
                logger.warning(
                    f"[CircuitStatistics] two_qubit_gate_count="
                    f"{self.two_qubit_gate_count} > "
                    f"num_gates={self.num_gates}; "
                    f"clamping to {self.num_gates}"
                )
                self.two_qubit_gate_count = self.num_gates
            if self.two_qubit_gate_count < 0:
                self.two_qubit_gate_count = 0

        if self.connectivity_graph is not None:
            cleaned: list[list[int]] = []
            # Cast to Any: validators run defensively against unsanitized input,
            # so the runtime checks below are intentional despite the declared type.
            for edge in cast("list[Any]", self.connectivity_graph):
                if not isinstance(edge, list) or len(edge) != 2:
                    continue
                u, v = edge
                if not (isinstance(u, int) and isinstance(v, int)):
                    continue
                if 0 <= u < self.num_qubits and 0 <= v < self.num_qubits and u != v:
                    cleaned.append([u, v])
            dropped = len(self.connectivity_graph) - len(cleaned)
            if dropped > 0:
                logger.warning(
                    f"[CircuitStatistics] Dropped {dropped} invalid edges from connectivity_graph"
                )
            self.connectivity_graph = cleaned if cleaned else None

        return self
