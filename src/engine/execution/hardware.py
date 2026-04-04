"""IBM Quantum hardware execution backend.

Manages connections to IBM Quantum via qiskit-ibm-runtime,
handles transpilation to ISA circuits, and retrieves measurement
results from real quantum hardware.

Requires saved IBM Quantum credentials:
    from qiskit_ibm_runtime import QiskitRuntimeService
    QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token="...")
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from qiskit import QuantumCircuit

logger = logging.getLogger(__name__)


# ── Data classes for provenance capture ──────────────────────────────


@dataclass
class HardwareTranspilationInfo:
    """Transpilation details captured for provenance."""

    original_depth: int
    transpiled_depth: int
    original_gate_count: int
    transpiled_gate_count: int
    swap_count: int
    qubit_layout: list[int]
    basis_gates: list[str]
    optimization_level: int


@dataclass
class HardwareJobInfo:
    """Job metadata captured for provenance."""

    job_id: str
    backend_name: str
    creation_date: str
    status: str
    execution_time_seconds: float | None = None


@dataclass
class HardwareResult:
    """Complete result from hardware execution."""

    counts: dict[str, int]
    transpilation_info: HardwareTranspilationInfo
    job_info: HardwareJobInfo
    calibration_snapshot: dict[str, Any]
    isa_circuit: QuantumCircuit


# ── Backend resolution ───────────────────────────────────────────────


def resolve_backend(
    backend_name: str | None = None,
    min_qubits: int = 1,
) -> Any:
    """Resolve an IBM Quantum backend.

    If backend_name is provided, connects to that specific backend.
    Otherwise, selects the least busy operational backend with at
    least min_qubits qubits.

    Raises RuntimeError with setup instructions if credentials
    are not configured.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    try:
        service = QiskitRuntimeService()
    except Exception as e:
        raise RuntimeError(
            "Failed to connect to IBM Quantum. "
            "Have you saved your credentials? Run:\n\n"
            "  from qiskit_ibm_runtime import QiskitRuntimeService\n"
            "  QiskitRuntimeService.save_account(\n"
            "      channel='ibm_quantum_platform', token='YOUR_TOKEN'\n"
            "  )\n\n"
            f"Error: {e}"
        ) from e

    if backend_name:
        try:
            backend = service.backend(backend_name)
            logger.info(f"Using specified backend: {backend.name}")
            return backend
        except Exception as e:
            raise RuntimeError(
                f"Backend '{backend_name}' not found or not accessible: {e}"
            ) from e

    backend = service.least_busy(
        operational=True,
        simulator=False,
        min_num_qubits=min_qubits,
    )
    if backend is None:
        raise RuntimeError(
            f"No operational hardware backends found with >= {min_qubits} qubits."
        )
    logger.info(f"Auto-selected least busy backend: {backend.name}")
    return backend


# ── Transpilation ────────────────────────────────────────────────────


def transpile_for_hardware(
    circuit: QuantumCircuit,
    backend: Any,
    optimization_level: int = 1,
) -> tuple[QuantumCircuit, HardwareTranspilationInfo]:
    """Transpile a circuit to an ISA circuit for the target backend.

    Returns the transpiled circuit and a HardwareTranspilationInfo
    capturing depth change, SWAP count, and qubit layout.
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    original_depth = circuit.depth()
    original_gate_count = len(circuit.data)

    pm = generate_preset_pass_manager(
        backend=backend,
        optimization_level=optimization_level,
    )
    isa_circuit = pm.run(circuit)

    # Extract logical→physical qubit layout
    qubit_layout = _extract_qubit_layout(isa_circuit, circuit.num_qubits)

    # Count SWAPs inserted by the transpiler
    ops = dict(isa_circuit.count_ops())
    swap_count = ops.get("swap", 0) + ops.get("SWAP", 0)

    # Get basis gates from backend
    try:
        basis_gates = list(backend.operation_names)
    except Exception:
        basis_gates = list(ops.keys())

    info = HardwareTranspilationInfo(
        original_depth=original_depth,
        transpiled_depth=isa_circuit.depth(),
        original_gate_count=original_gate_count,
        transpiled_gate_count=len(isa_circuit.data),
        swap_count=swap_count,
        qubit_layout=qubit_layout,
        basis_gates=basis_gates,
        optimization_level=optimization_level,
    )

    logger.info(
        f"Transpilation: depth {original_depth} -> {info.transpiled_depth}, "
        f"gates {original_gate_count} -> {info.transpiled_gate_count}, "
        f"SWAPs inserted: {swap_count}"
    )

    return isa_circuit, info


def _extract_qubit_layout(
    isa_circuit: QuantumCircuit, num_logical_qubits: int
) -> list[int]:
    """Extract logical→physical qubit mapping from transpiled circuit layout."""
    layout = getattr(isa_circuit, "layout", None)
    if layout is None:
        return list(range(num_logical_qubits))

    # Try final_layout first, then initial_layout
    for layout_map in (
        getattr(layout, "final_layout", None),
        getattr(layout, "initial_layout", None),
    ):
        if layout_map is not None:
            try:
                return [
                    layout_map[isa_circuit.qubits[i]]
                    for i in range(num_logical_qubits)
                ]
            except (KeyError, IndexError):
                pass

    return list(range(num_logical_qubits))


# ── Calibration capture ──────────────────────────────────────────────


def capture_calibration_snapshot(backend: Any) -> dict[str, Any]:
    """Capture a lightweight snapshot of backend calibration data.

    Includes backend name, qubit count, and aggregate T1/T2 statistics.
    Wrapped in try/except for resilience — calibration APIs vary by
    backend version.
    """
    snapshot: dict[str, Any] = {
        "backend_name": backend.name,
        "num_qubits": backend.num_qubits,
    }

    try:
        props = backend.properties()
        if props:
            snapshot["last_update"] = str(props.last_update_date)
            t1_vals = []
            t2_vals = []
            for qubit_idx in range(backend.num_qubits):
                try:
                    t1 = props.t1(qubit_idx)
                    t2 = props.t2(qubit_idx)
                    if t1 is not None:
                        t1_vals.append(float(t1))
                    if t2 is not None:
                        t2_vals.append(float(t2))
                except Exception:
                    pass
            if t1_vals:
                t1_sorted = sorted(t1_vals)
                snapshot["t1_us_median"] = round(t1_sorted[len(t1_sorted) // 2] * 1e6, 2)
            if t2_vals:
                t2_sorted = sorted(t2_vals)
                snapshot["t2_us_median"] = round(t2_sorted[len(t2_sorted) // 2] * 1e6, 2)
    except Exception as e:
        logger.debug(f"Could not capture calibration properties: {e}")

    try:
        snapshot["backend_version"] = str(backend.backend_version)
    except Exception:
        pass

    return snapshot


# ── Execution ────────────────────────────────────────────────────────


def execute_on_hardware(
    circuit: QuantumCircuit,
    backend: Any,
    shots: int = 1024,
    optimization_level: int = 1,
    session: Any | None = None,
) -> HardwareResult:
    """Execute a circuit on IBM Quantum hardware.

    Handles transpilation, calibration capture, job submission,
    blocking wait, and result extraction.

    Args:
        circuit: Quantum circuit with measurements.
        backend: IBM Quantum backend instance.
        shots: Number of measurement shots.
        optimization_level: Transpiler optimization (0-3).
        session: Optional qiskit-ibm-runtime Session for batching.

    Returns:
        HardwareResult with counts, transpilation info, job info,
        and calibration snapshot.
    """
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    # 1. Transpile for target hardware
    isa_circuit, transpilation_info = transpile_for_hardware(
        circuit, backend, optimization_level
    )

    # 2. Capture calibration snapshot before submission
    calibration_snapshot = capture_calibration_snapshot(backend)

    # 3. Submit job via SamplerV2
    sampler_mode = session if session is not None else backend
    sampler = Sampler(mode=sampler_mode)
    sampler.options.default_shots = shots

    logger.info(
        f"Submitting job to {backend.name} "
        f"(shots={shots}, opt_level={optimization_level})..."
    )

    t0 = time.monotonic()
    job = sampler.run([isa_circuit])
    job_id = job.job_id()
    logger.info(f"Job submitted: {job_id}. Waiting for results...")

    # 4. Block until results are ready
    result = job.result()
    execution_time = time.monotonic() - t0

    logger.info(f"Job {job_id} completed in {execution_time:.1f}s")

    # 5. Extract counts (register name varies: 'meas' from measure_all(), 'c' from manual)
    pub_result = result[0]
    data_bin = pub_result.data
    for attr in ("meas", "c", "cr"):
        if hasattr(data_bin, attr):
            counts = getattr(data_bin, attr).get_counts()
            break
    else:
        # Fallback: grab the first attribute that has get_counts
        for attr in dir(data_bin):
            obj = getattr(data_bin, attr, None)
            if hasattr(obj, "get_counts"):
                counts = obj.get_counts()
                break
        else:
            raise RuntimeError(
                f"Could not extract counts from result. "
                f"DataBin attributes: {[a for a in dir(data_bin) if not a.startswith('_')]}"
            )

    # 6. Package result
    job_info = HardwareJobInfo(
        job_id=job_id,
        backend_name=backend.name,
        creation_date=str(getattr(job, "creation_date", "")),
        status="completed",
        execution_time_seconds=round(execution_time, 2),
    )

    return HardwareResult(
        counts=counts,
        transpilation_info=transpilation_info,
        job_info=job_info,
        calibration_snapshot=calibration_snapshot,
        isa_circuit=isa_circuit,
    )


# ── Session management ───────────────────────────────────────────────


def create_session(backend: Any) -> Any:
    """Create a Session for batching multiple jobs on the same backend.

    Use as a context manager to keep the backend reserved
    across multiple experiments in a sweep:

        with create_session(backend) as session:
            execute_on_hardware(circuit, backend, session=session)
    """
    from qiskit_ibm_runtime import Session

    return Session(backend=backend)
