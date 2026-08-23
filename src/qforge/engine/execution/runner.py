"""Engine-native experiment runner.

Uses core state preparation and noise models for sophisticated quantum experiments.
Supports three simulation backends: qasm, statevector, density_matrix.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qforge.core.noise_models import create_noise_model

if TYPE_CHECKING:
    from qiskit_aer.noise import NoiseModel

# Import core modules for sophisticated state preparation and noise
from qforge.core.state_preparation import prepare_state

logger = logging.getLogger(__name__)


class EngineExperimentRunner:
    """Engine-native experiment runner for quantum circuit execution.

    This replaces the legacy core experiment runner with a clean,
    schema-based implementation that integrates directly with the engine.
    """

    def __init__(self, experiment_id: str = "engine-run"):
        """Initialize the engine experiment runner.

        Args:
            experiment_id: Unique identifier for this experiment run
        """
        self.experiment_id = experiment_id
        self.logger = logging.getLogger(f"{__name__}.{experiment_id}")
        self.noise_model: NoiseModel | None = None  # Will be set if noise is enabled
        self._sim_mode = "qasm"
        self._shots = 1024
        self._rng_seed: int | None = None
        self._backend_name: str | None = None
        self._optimization_level = 1
        self._hardware_session: Any = None

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
        readout_error_rate: float | None = None,
        backend_name: str | None = None,
        optimization_level: int = 1,
        hardware_session: Any = None,
    ) -> tuple[QuantumCircuit, Any]:
        """Run a quantum experiment with specified parameters.

        Args:
            num_qubits: Number of qubits in the circuit
            state_type: Type of quantum state
                ("GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM")
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
            balance: Optional circuit balancing strategy name.
            readout_error_rate: Optional measurement readout error probability.
            backend_name: IBM Quantum backend name (hardware mode only).
            optimization_level: Transpiler optimization level (0-3).
            hardware_session: Pre-existing hardware session for batch runs.

        Returns:
            Tuple of (QuantumCircuit, simulation result)
        """
        self.logger.info(f"Starting engine experiment: {state_type} state with {num_qubits} qubits")

        # Create quantum circuit
        circuit = self._create_circuit(num_qubits, state_type, custom_params, balance=balance)

        # Apply noise if enabled
        if noise_enabled and noise_type:
            circuit = self._apply_noise(
                circuit,
                noise_type,
                error_rate,
                z_prob,
                i_prob,
                t1,
                t2,
                custom_params=custom_params,
                readout_error_rate=readout_error_rate,
            )
        elif readout_error_rate is not None and readout_error_rate > 0:
            # Readout errors can be applied independently of gate noise
            self._apply_readout_only(circuit.num_qubits, readout_error_rate)

        # Remember backend settings so extra Pauli circuits reuse them
        self._sim_mode = sim_mode
        self._shots = shots
        self._rng_seed = rng_seed
        self._backend_name = backend_name
        self._optimization_level = optimization_level
        self._hardware_session = hardware_session

        result = self._execute_simulation(
            circuit,
            sim_mode,
            shots,
            rng_seed,
            backend_name=backend_name,
            optimization_level=optimization_level,
            hardware_session=hardware_session,
        )

        self.logger.info(f"Completed experiment: {self.experiment_id}")
        return circuit, result

    def execute_circuit(self, circuit: QuantumCircuit) -> Any:
        """Execute ``circuit`` with the same backend, noise, shots, and seed.

        Used for extra Pauli-basis measurements after the prepared-state run.
        The circuit is not rebuilt; callers rotate and measure it themselves.
        """
        return self._execute_simulation(
            circuit,
            self._sim_mode,
            self._shots,
            self._rng_seed,
            backend_name=self._backend_name,
            optimization_level=self._optimization_level,
            hardware_session=self._hardware_session,
        )

    # ---------- Circuit / noise / simulation internals ----------

    def _create_circuit(
        self,
        num_qubits: int,
        state_type: str,
        custom_params: dict | None,
        balance: str | None = None,
    ) -> QuantumCircuit:
        """Create quantum circuit using sophisticated core state preparation."""
        try:
            # Use core state preparation with custom parameters
            state_params: dict[str, Any] = {
                "num_qubits": num_qubits,
                "state_type": state_type,
            }

            # Pass custom parameters as a dict (don't spread them)
            if custom_params:
                state_params["custom_params"] = custom_params

            if balance:
                state_params["balance"] = balance

            # Use the sophisticated core state preparation
            circuit = prepare_state(**state_params)

            # Ensure measurement is added
            if not circuit.clbits:
                circuit.measure_all()

            return circuit

        except Exception as e:
            self.logger.error(f"Failed to create circuit with core state preparation: {e}")
            # Fallback to basic implementation for debugging
            return self._create_basic_circuit(num_qubits, state_type, custom_params)

    def _create_basic_circuit(
        self, num_qubits: int, state_type: str, custom_params: dict | None
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
        error_rate: float | None,
        z_prob: float | None,
        i_prob: float | None,
        t1: float | None,
        t2: float | None,
        custom_params: dict | None = None,
        readout_error_rate: float | None = None,
    ) -> QuantumCircuit:
        """Apply sophisticated noise using core noise models."""
        try:
            # Map noise type to uppercase (core expects uppercase)
            noise_type_upper = noise_type.upper() if noise_type else "DEPOLARIZING"

            # Prepare noise parameters
            noise_params: dict[str, Any] = {
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

            # Pass noise-relevant custom_params only (allowlist of noise keys)
            if custom_params:
                noise_keys = {
                    "correlation_strength",
                    "topology",
                    "temperature",
                    "gate_time",
                    "dt",
                    "qubit_frequency",
                }
                filtered = {k: v for k, v in custom_params.items() if k in noise_keys}
                if filtered:
                    noise_params["custom_params"] = filtered

            if readout_error_rate is not None:
                noise_params["readout_error_rate"] = readout_error_rate

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

    def _apply_readout_only(self, num_qubits: int, readout_error_rate: float) -> None:
        """Apply readout errors without any gate noise."""
        from qiskit_aer.noise import NoiseModel, ReadoutError

        noise_model = NoiseModel()
        p = float(readout_error_rate)
        probs = [[1 - p, p], [p, 1 - p]]
        for qubit in range(num_qubits):
            noise_model.add_readout_error(ReadoutError(probs), [qubit])
        self.noise_model = noise_model
        self.logger.info(f"Applied readout-only noise (rate={p:.4f}) to {num_qubits} qubits")

    def _execute_simulation(
        self,
        circuit: QuantumCircuit,
        sim_mode: str,
        shots: int,
        rng_seed: int | None,
        backend_name: str | None = None,
        optimization_level: int = 1,
        hardware_session: Any = None,
    ) -> Any:
        """Dispatch to the appropriate backend method."""
        if sim_mode == "hardware":
            return self._execute_hardware(
                circuit,
                shots,
                backend_name,
                optimization_level,
                hardware_session,
            )
        elif sim_mode == "statevector":
            return self._execute_statevector(circuit, shots, rng_seed)
        elif sim_mode == "density_matrix":
            return self._execute_density_matrix(circuit, shots, rng_seed)
        else:
            return self._execute_qasm(circuit, shots, rng_seed)

    def _execute_hardware(
        self,
        circuit: QuantumCircuit,
        shots: int,
        backend_name: str | None = None,
        optimization_level: int = 1,
        session: Any = None,
    ) -> dict[str, Any]:
        """Execute on IBM Quantum hardware via qiskit-ibm-runtime."""
        from qforge.engine.execution.hardware import execute_on_hardware, resolve_backend

        backend = resolve_backend(
            backend_name=backend_name,
            min_qubits=circuit.num_qubits,
        )

        hw_result = execute_on_hardware(
            circuit=circuit,
            backend=backend,
            shots=shots,
            optimization_level=optimization_level,
            session=session,
        )

        return {"counts": hw_result.counts, "hardware_result": hw_result}

    def _execute_qasm(
        self,
        circuit: QuantumCircuit,
        shots: int,
        rng_seed: int | None,
    ) -> Any:
        """Execute shot-based QASM simulation (original behaviour)."""
        backend = AerSimulator()
        if rng_seed is not None:
            backend.set_options(seed_simulator=int(rng_seed))
        if self.noise_model is not None:
            backend.set_options(noise_model=self.noise_model)

        tcirc = transpile(circuit, backend)
        job = backend.run(tcirc, shots=int(shots))
        return job.result()

    def _execute_statevector(
        self,
        circuit: QuantumCircuit,
        shots: int,
        rng_seed: int | None,
    ) -> dict[str, Any]:
        """Execute exact statevector simulation (noiseless).

        Returns a dict with 'counts' (synthesized via multinomial sampling)
        and 'statevector' (Qiskit Statevector object).
        """
        if self.noise_model is not None:
            self.logger.warning("Noise model is set but will be ignored in statevector mode")

        # Prepare a measurement-free copy for statevector extraction
        sv_circuit = circuit.copy()
        sv_circuit.remove_final_measurements()
        sv_circuit.save_statevector()

        backend = AerSimulator(method="statevector")
        if rng_seed is not None:
            backend.set_options(seed_simulator=int(rng_seed))

        tcirc = transpile(sv_circuit, backend)
        job = backend.run(tcirc, shots=1)
        result = job.result()
        statevector = result.get_statevector()

        # Synthesize counts from exact probabilities
        probs = np.abs(statevector.data) ** 2
        rng = np.random.default_rng(rng_seed)
        samples = rng.multinomial(shots, probs)
        n_qubits = circuit.num_qubits
        counts: dict[str, int] = {}
        for idx, count in enumerate(samples):
            if count > 0:
                bitstring = format(idx, f"0{n_qubits}b")
                counts[bitstring] = int(count)

        return {"counts": counts, "statevector": statevector}

    def _execute_density_matrix(
        self,
        circuit: QuantumCircuit,
        shots: int,
        rng_seed: int | None,
    ) -> dict[str, Any]:
        """Execute density matrix simulation (supports noise).

        Returns a dict with 'counts' (from shot-based measurement) and
        'density_matrix' (DensityMatrix object from the save instruction).
        """
        # Build a circuit that saves the density matrix *before* measurement
        dm_circuit = circuit.copy()
        dm_circuit.remove_final_measurements()
        dm_circuit.save_density_matrix()
        dm_circuit.measure_all()

        backend = AerSimulator(method="density_matrix")
        if rng_seed is not None:
            backend.set_options(seed_simulator=int(rng_seed))
        if self.noise_model is not None:
            backend.set_options(noise_model=self.noise_model)

        tcirc = transpile(dm_circuit, backend)
        job = backend.run(tcirc, shots=int(shots))
        result = job.result()

        counts = result.get_counts()
        dm = result.data(0).get("density_matrix")

        return {"counts": counts, "density_matrix": dm}

    # ---------- Results helpers ----------

    def _extract_canonical_counts(self, result: Any, num_qubits: int) -> dict[str, int]:
        """Extract counts from a Qiskit Result and canonicalize bitstrings.

        - Removes spaces Qiskit may include for registers
        - Pads/truncates to length = num_qubits
        - Keeps MSB-left ordering (compatible with metrics package)
        """
        try:
            raw_counts = result.get_counts()
        except Exception:
            # handle multi-experiment result (rare here)
            raw_counts = result.get_counts(0)

        counts: dict[str, int] = {}
        for k, v in raw_counts.items():
            key = str(k).replace(" ", "")
            # Pad (left) to number of qubits, in case classical bits > qubits
            if len(key) < num_qubits:
                key = key.rjust(num_qubits, "0")
            elif len(key) > num_qubits:
                self.logger.debug(
                    "Bitstring '%s' longer than num_qubits=%d; truncating to "
                    "rightmost %d bits (MSB-left convention).",
                    key,
                    num_qubits,
                    num_qubits,
                )
                key = key[-num_qubits:]
            counts[key] = int(v)

        # Ensure non-empty dict for downstream metrics
        if not counts:
            self.logger.warning("No counts found in Qiskit result; returning {'0'*n: 0}")
            counts["0" * num_qubits] = 0

        return counts


def run_raw(config: dict[str, Any]) -> tuple[Any, Any, EngineExperimentRunner]:
    """Execute experiment using engine-native runner.

    Args:
        config: experiment config dict
    Returns:
        (QuantumCircuit, qiskit result payload, runner)
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
        readout_error_rate=config.get("readout_error_rate"),
        backend_name=config.get("backend_name"),
        optimization_level=int(config.get("optimization_level", 1)),
        hardware_session=config.get("_hardware_session"),
    )
    return circuit, raw, runner
