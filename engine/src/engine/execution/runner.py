"""
Engine-native experiment runner.

Uses core state preparation and noise models for sophisticated quantum experiments.
"""

from __future__ import annotations

import logging
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from src.core.noise_models import create_noise_model

# Import core modules for sophisticated state preparation and noise
from src.core.state_preparation import prepare_state

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
        noise_type: str | None = None,
        noise_enabled: bool = False,
        shots: int = 1024,
        sim_mode: str = "qasm",
        error_rate: float | None = None,
        z_prob: float | None = None,
        i_prob: float | None = None,
        t1: float | None = None,
        t2: float | None = None,
        custom_params: dict | None = None,
        rng_seed: int | None = None,
        balance: str | None = None,
    ) -> tuple[QuantumCircuit, Any]:
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
            balance: Circuit depth balancing strategy (e.g., "gate_count")

        Returns:
            Tuple of (QuantumCircuit, simulation result)
        """
        self.logger.info(f"Starting engine experiment: {state_type} state with {num_qubits} qubits")

        # Create quantum circuit
        circuit = self._create_circuit(num_qubits, state_type, custom_params, balance=balance)

        # Apply noise if enabled
        if noise_enabled and noise_type:
            circuit = self._apply_noise(
                circuit, noise_type, error_rate, z_prob, i_prob, t1, t2,
                custom_params=custom_params,
            )

        # Execute simulation
        result = self._execute_simulation(circuit, sim_mode, shots, rng_seed)

        self.logger.info(f"Completed experiment: {self.experiment_id}")
        return circuit, result

    # ---------- Circuit / noise / simulation internals ----------

    def _create_circuit(
        self, num_qubits: int, state_type: str, custom_params: dict | None,
        balance: str | None = None,
    ) -> QuantumCircuit:
        """Create quantum circuit using core state preparation."""
        state_params = {
            "num_qubits": num_qubits,
            "state_type": state_type,
        }

        if custom_params:
            state_params["custom_params"] = custom_params

        if balance:
            state_params["balance"] = balance

        circuit = prepare_state(**state_params)

        # Ensure measurement is added
        if not circuit.clbits:
            circuit.measure_all()

        return circuit

    def _apply_noise(
        self,
        circuit: QuantumCircuit,
        noise_type: str,
        error_rate: float | None,
        z_prob: float | None,
        i_prob: float | None,
        t1: float | None,
        t2: float | None,
        custom_params: dict | None = None,
    ) -> QuantumCircuit:
        """Apply noise using core noise models. Raises on failure."""
        # Map noise type to uppercase (core expects uppercase)
        noise_type_upper = noise_type.upper() if noise_type else "DEPOLARIZING"

        # Prepare noise parameters
        noise_params: dict[str, Any] = {
            "noise_type": noise_type_upper,
            "num_qubits": circuit.num_qubits,
        }

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
        if custom_params:
            noise_params["custom_params"] = custom_params

        self.noise_model = create_noise_model(**noise_params)

        if self.noise_model is None:
            raise RuntimeError(
                f"create_noise_model returned None for noise_type='{noise_type_upper}'"
            )

        self.logger.info(
            f"Created {noise_type_upper} noise model with parameters: {noise_params}"
        )
        return circuit

    def _execute_simulation(
        self,
        circuit: QuantumCircuit,
        sim_mode: str,
        shots: int,
        rng_seed: int | None,
    ) -> Any:
        """Execute QASM simulation."""
        # Only support QASM simulation
        if sim_mode != "qasm":
            self.logger.warning(f"Simulation mode '{sim_mode}' not supported, using QASM")

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

    def _extract_canonical_counts(self, result: Any, num_qubits: int) -> dict[str, int]:
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

        counts: dict[str, int] = {}
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
            self.logger.warning("No counts found in Qiskit result; returning {'0'*n: 0}")
            counts["0" * num_qubits] = 0

        return counts


def run_raw(config: dict[str, Any]) -> tuple[Any, Any]:
    """
    Execute experiment using engine-native runner.

    Args:
        config: experiment config dict
    Returns:
        (QuantumCircuit, qiskit result payload)
    """
    runner = EngineExperimentRunner(experiment_id=config.get("experiment_id", "engine-run"))

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
        balance=config.get("balance_circuit"),
    )
    return circuit, raw
