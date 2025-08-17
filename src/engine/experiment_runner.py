"""
Engine-native experiment runner.

Uses core state preparation and noise models for sophisticated quantum experiments.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple, Optional, Mapping
import logging

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Import core modules for sophisticated state preparation and noise
from src.core.state_preparation import prepare_state
from src.core.noise_models import create_noise_model

# Canonical metrics + schema v1 (engine-facing)
try:
    from src.analysis.metrics.registry import compute_all
    from src.analysis.metrics.schema_bridge import metrics_to_schema
except Exception:  # keep engine runnable even if metrics not installed yet
    compute_all = None
    metrics_to_schema = None

logger = logging.getLogger(__name__)


class EngineExperimentRunner:
    """
    Engine-native experiment runner for quantum circuit execution.

    This replaces the legacy core experiment runner with a clean,
    schema-based implementation that integrates directly with the engine.
    """

    def __init__(self, experiment_id: str = "engine-run"):
        """
        Initialize the engine experiment runner.

        Args:
            experiment_id: Unique identifier for this experiment run
        """
        self.experiment_id = experiment_id
        self.logger = logging.getLogger(f"EngineExperimentRunner.{experiment_id}")
        self.noise_model = None  # Will be set if noise is enabled

    def run_experiment(
        self,
        num_qubits: int,
        state_type: str = "GHZ",
        noise_type: Optional[str] = None,
        noise_enabled: bool = False,
        shots: int = 1024,
        sim_mode: str = "qasm",
        error_rate: Optional[float] = None,
        z_prob: Optional[float] = None,
        i_prob: Optional[float] = None,
        t1: Optional[float] = None,
        t2: Optional[float] = None,
        custom_params: Optional[Dict] = None,
        rng_seed: Optional[int] = None,
    ) -> Tuple[QuantumCircuit, Any]:
        """
        Run a quantum experiment with specified parameters.

        Args:
            num_qubits: Number of qubits in the circuit
            state_type: Type of quantum state ("GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM")
            noise_type: Type of noise model to apply
            noise_enabled: Whether to apply noise
            shots: Number of shots for qasm simulation
            sim_mode: Simulation mode ("qasm" or "density")
            error_rate: Custom error rate for noise models
            z_prob: Z probability for PHASE_FLIP noise
            i_prob: I probability for PHASE_FLIP noise
            t1: T1 relaxation time for THERMAL_RELAXATION noise
            t2: T2 dephasing time for THERMAL_RELAXATION noise
            custom_params: Custom parameters for state preparation or noise
            rng_seed: Random seed for reproducibility

        Returns:
            Tuple of (QuantumCircuit, simulation result)
        """
        self.logger.info(
            f"Starting engine experiment: {state_type} state with {num_qubits} qubits"
        )

        # Create quantum circuit
        circuit = self._create_circuit(num_qubits, state_type, custom_params)

        # Apply noise if enabled
        if noise_enabled and noise_type:
            circuit = self._apply_noise(
                circuit, noise_type, error_rate, z_prob, i_prob, t1, t2
            )

        # Execute simulation
        result = self._execute_simulation(circuit, sim_mode, shots, rng_seed)

        self.logger.info(f"Completed experiment: {self.experiment_id}")
        return circuit, result

    # ---------- Convenience high-level APIs ----------

    def run_to_counts(
        self,
        *,
        num_qubits: int,
        state_type: str = "GHZ",
        noise_type: Optional[str] = None,
        noise_enabled: bool = False,
        shots: int = 1024,
        sim_mode: str = "qasm",
        error_rate: Optional[float] = None,
        z_prob: Optional[float] = None,
        i_prob: Optional[float] = None,
        t1: Optional[float] = None,
        t2: Optional[float] = None,
        custom_params: Optional[Dict] = None,
        rng_seed: Optional[int] = None,
    ) -> Tuple[QuantumCircuit, Mapping[str, int]]:
        """
        Run an experiment and return (circuit, canonical counts dict).
        Canonicalization: bitstrings are MSB-left, length == num_qubits.
        """
        circuit, raw = self.run_experiment(
            num_qubits=num_qubits,
            state_type=state_type,
            noise_type=noise_type,
            noise_enabled=noise_enabled,
            shots=shots,
            sim_mode=sim_mode,
            error_rate=error_rate,
            z_prob=z_prob,
            i_prob=i_prob,
            t1=t1,
            t2=t2,
            custom_params=custom_params,
            rng_seed=rng_seed,
        )
        counts = self._extract_canonical_counts(raw, num_qubits)
        return circuit, counts

    def run_to_schema(
        self,
        *,
        num_qubits: int,
        state_type: str = "GHZ",
        noise_type: Optional[str] = None,
        noise_enabled: bool = False,
        shots: int = 1024,
        sim_mode: str = "qasm",
        error_rate: Optional[float] = None,
        z_prob: Optional[float] = None,
        i_prob: Optional[float] = None,
        t1: Optional[float] = None,
        t2: Optional[float] = None,
        custom_params: Optional[Dict] = None,
        rng_seed: Optional[int] = None,
    ) -> Tuple[QuantumCircuit, Dict[str, Any]]:
        """
        Run an experiment and return (circuit, schema_v1 metrics dict).
        Requires src.analysis.metrics (registry + schema_bridge).
        """
        if compute_all is None or metrics_to_schema is None:
            raise RuntimeError(
                "Metrics registry/schema not available. Ensure src.analysis.metrics is importable."
            )

        circuit, counts = self.run_to_counts(
            num_qubits=num_qubits,
            state_type=state_type,
            noise_type=noise_type,
            noise_enabled=noise_enabled,
            shots=shots,
            sim_mode=sim_mode,
            error_rate=error_rate,
            z_prob=z_prob,
            i_prob=i_prob,
            t1=t1,
            t2=t2,
            custom_params=custom_params,
            rng_seed=rng_seed,
        )

        # Compute canonical metrics and convert to schema v1
        metric_results = compute_all(counts=counts)
        schema_v1 = metrics_to_schema(metric_results)
        return circuit, schema_v1

    # ---------- Circuit / noise / simulation internals ----------

    def _create_circuit(
        self, num_qubits: int, state_type: str, custom_params: Optional[Dict]
    ) -> QuantumCircuit:
        """Create quantum circuit using sophisticated core state preparation."""
        try:
            # Use core state preparation with custom parameters
            state_params = {
                "num_qubits": num_qubits,
                "state_type": state_type,
            }

            # Add custom parameters if provided
            if custom_params:
                state_params.update(custom_params)

            # Use the sophisticated core state preparation
            circuit = prepare_state(**state_params)

            # Ensure measurement is added
            if not circuit.clbits:
                circuit.measure_all()

            return circuit

        except Exception as e:
            self.logger.error(
                f"Failed to create circuit with core state preparation: {e}"
            )
            # Fallback to basic implementation for debugging
            return self._create_basic_circuit(num_qubits, state_type, custom_params)

    def _create_basic_circuit(
        self, num_qubits: int, state_type: str, custom_params: Optional[Dict]
    ) -> QuantumCircuit:
        """Fallback basic circuit creation for debugging."""
        circuit = QuantumCircuit(num_qubits, num_qubits)

        if state_type == "GHZ":
            circuit.h(0)
            for i in range(1, num_qubits):
                circuit.cx(0, i)
        elif state_type == "W":
            # W state: superposition of single excitations
            circuit.h(0)
            for i in range(1, num_qubits):
                circuit.cx(0, i)
                circuit.h(i)
        elif state_type == "BELL":
            if num_qubits < 2:
                raise ValueError("Bell state requires at least 2 qubits")
            circuit.h(0)
            circuit.cx(0, 1)
        elif state_type == "CLUSTER":
            # Linear cluster state
            for i in range(num_qubits):
                circuit.h(i)
            for i in range(num_qubits - 1):
                circuit.cx(i, i + 1)
        elif state_type == "SUPERPOSITION":
            # Simple superposition state
            for i in range(num_qubits):
                circuit.h(i)
        elif state_type == "CUSTOM":
            # Custom state preparation
            if custom_params and "circuit_operations" in custom_params:
                for op in custom_params["circuit_operations"]:
                    if op["gate"] == "h":
                        circuit.h(op["qubit"])
                    elif op["gate"] == "cx":
                        circuit.cx(op["control"], op["target"])
                    elif op["gate"] == "x":
                        circuit.x(op["qubit"])
            else:
                # Default to superposition if no custom operations
                for i in range(num_qubits):
                    circuit.h(i)
        else:
            raise ValueError(f"Unsupported state type: {state_type}")

        # Measure all qubits
        circuit.measure_all()
        return circuit

    def _apply_noise(
        self,
        circuit: QuantumCircuit,
        noise_type: str,
        error_rate: Optional[float],
        z_prob: Optional[float],
        i_prob: Optional[float],
        t1: Optional[float],
        t2: Optional[float],
    ) -> QuantumCircuit:
        """Apply sophisticated noise using core noise models."""
        try:
            # Map noise type to uppercase (core expects uppercase)
            noise_type_upper = noise_type.upper() if noise_type else "DEPOLARIZING"

            # Prepare noise parameters
            noise_params = {
                "noise_type": noise_type_upper,
                "num_qubits": circuit.num_qubits,
            }

            # Add specific noise parameters
            if error_rate is not None:
                noise_params["error_rate"] = error_rate
            if z_prob is not None:
                noise_params["z_prob"] = z_prob
            if i_prob is not None:
                noise_params["i_prob"] = i_prob
            if t1 is not None:
                noise_params["t1"] = t1
            if t2 is not None:
                noise_params["t2"] = t2

            # Create sophisticated noise model using core
            self.noise_model = create_noise_model(**noise_params)

            self.logger.info(
                f"Created {noise_type_upper} noise model with parameters: {noise_params}"
            )
            return circuit

        except Exception as e:
            self.logger.error(f"Failed to apply noise with core noise models: {e}")
            # Return original circuit if noise application fails
            self.logger.warning(f"Noise type '{noise_type}' not applied due to error")
            self.noise_model = None
            return circuit

    def _execute_simulation(
        self,
        circuit: QuantumCircuit,
        sim_mode: str,
        shots: int,
        rng_seed: Optional[int],
    ) -> Any:
        """Execute QASM simulation."""
        # Only support QASM simulation
        if sim_mode != "qasm":
            self.logger.warning(
                f"Simulation mode '{sim_mode}' not supported, using QASM"
            )

        # Build simulator and set options
        backend = AerSimulator()
        if rng_seed is not None:
            backend.set_options(seed_simulator=int(rng_seed))
        if self.noise_model is not None:
            backend.set_options(noise_model=self.noise_model)

        # Transpile for backend target
        tcirc = transpile(circuit, backend)

        # Run
        job = backend.run(tcirc, shots=int(shots))
        result = job.result()
        return result

    # ---------- Results helpers ----------

    def _extract_canonical_counts(self, result: Any, num_qubits: int) -> Dict[str, int]:
        """
        Extract counts from a Qiskit Result and canonicalize bitstrings.

        - Removes spaces Qiskit may include for registers
        - Pads/truncates to length = num_qubits
        - Keeps MSB-left ordering (compatible with metrics package)
        """
        try:
            raw_counts = result.get_counts()  # type: ignore[attr-defined]
        except Exception:
            # handle multi-experiment result (rare here)
            raw_counts = result.get_counts(0)  # type: ignore[attr-defined]

        counts: Dict[str, int] = {}
        for k, v in raw_counts.items():
            key = str(k).replace(" ", "")
            # Pad (left) to number of qubits, in case classical bits > qubits
            if len(key) < num_qubits:
                key = key.rjust(num_qubits, "0")
            elif len(key) > num_qubits:
                key = key[-num_qubits:]  # keep least significant num_qubits bits
            counts[key] = int(v)

        # Ensure non-empty dict for downstream metrics
        if not counts:
            self.logger.warning(
                "No counts found in Qiskit result; returning {'0'*n: 0}"
            )
            counts["0" * num_qubits] = 0

        return counts


def run_raw(config: Dict[str, Any]) -> Tuple[Any, Any]:
    """
    Execute experiment using engine-native runner.

    Args:
        config: experiment config dict
    Returns:
        (QuantumCircuit, qiskit result payload)
    """
    runner = EngineExperimentRunner(
        experiment_id=config.get("experiment_id", "engine-run")
    )

    circuit, raw = runner.run_experiment(
        num_qubits=int(config["num_qubits"]),
        state_type=str(config["state_type"]).upper(),
        noise_type=config.get("noise_type"),
        noise_enabled=bool(config.get("noise_enabled", False)),
        shots=int(config.get("shots", 1024)),
        sim_mode=str(config.get("sim_mode", "qasm")),
        error_rate=config.get("error_rate"),
        z_prob=config.get("z_prob"),
        i_prob=config.get("i_prob"),
        t1=config.get("t1"),
        t2=config.get("t2"),
        custom_params=config.get("custom_params"),
        rng_seed=config.get("rng_seed"),
    )
    return circuit, raw
