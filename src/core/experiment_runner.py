"""
Experiment Runner module for the Quantum Experiment Framework.

This module contains the ExperimentRunner class which orchestrates
quantum circuit preparation, noise application, simulation, and measurement.
"""

import time
import logging
from typing import Optional, Dict, Union, Tuple
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer, AerSimulator
from qiskit.quantum_info import DensityMatrix

from .state_preparation import prepare_state
from .noise_models import create_noise_model
from src.utils import logger as logger_utils

# Initialize logger for this module
logger = logging.getLogger("QuantumExperiment.ExperimentRunner")


class ExperimentRunner:
    """
    Orchestrates quantum circuit preparation, noise application, simulation, and measurement.

    This class provides a research-grade interface for running quantum experiments
    with configurable parameters, extensible noise models, and comprehensive logging.
    """

    def __init__(self, experiment_id: str = "N/A"):
        """
        Initialize the experiment runner.

        Args:
            experiment_id (str): Unique identifier for this experiment run.
        """
        self.experiment_id = experiment_id
        self.logger = logging.getLogger("QuantumExperiment.ExperimentRunner")

    def run_experiment(
        self,
        num_qubits: int,
        state_type: str = "GHZ",
        noise_type: str = "DEPOLARIZING",
        noise_enabled: bool = True,
        shots: int = 1024,
        sim_mode: str = "qasm",
        error_rate: Optional[float] = None,
        z_prob: Optional[float] = None,
        i_prob: Optional[float] = None,
        t1: Optional[float] = None,
        t2: Optional[float] = None,
        custom_params: Optional[Dict] = None,
    ) -> Tuple[QuantumCircuit, Union[Dict, DensityMatrix]]:
        """
        Run a quantum experiment with specified parameters.

        Args:
            num_qubits (int): Number of qubits in the circuit.
            state_type (str): Type of quantum state ("GHZ", "W", "CLUSTER").
            noise_type (str): Type of noise model to apply.
            noise_enabled (bool): Whether to apply noise.
            shots (int): Number of shots for qasm simulation.
            sim_mode (str): Simulation mode ("qasm" or "density").
            error_rate (float, optional): Custom error rate for noise models.
            z_prob (float, optional): Z probability for PHASE_FLIP noise.
            i_prob (float, optional): I probability for PHASE_FLIP noise.
            t1 (float, optional): T1 relaxation time for THERMAL_RELAXATION noise.
            t2 (float, optional): T2 dephasing time for THERMAL_RELAXATION noise.
            custom_params (dict, optional): Custom parameters for state preparation or noise.

        Returns:
            Tuple[QuantumCircuit, Union[Dict, DensityMatrix]]: The quantum circuit and simulation result.

        Raises:
            ValueError: If invalid parameters are provided.
            Exception: If simulation fails.
        """
        # Prepare the quantum circuit
        qc = self._prepare_circuit(state_type, num_qubits, custom_params)

        # Apply noise if enabled
        noise_model = self._apply_noise(
            noise_enabled,
            noise_type,
            num_qubits,
            error_rate,
            z_prob,
            i_prob,
            t1,
            t2,
            sim_mode,
        )

        # Configure backend and circuit
        backend, qc = self._configure_simulation(qc, sim_mode)

        # Transpile and run
        circuit_compiled = self._transpile_circuit(qc, backend)
        result_data = self._run_simulation(
            circuit_compiled, backend, shots, noise_model, sim_mode
        )

        return qc, result_data

    def _prepare_circuit(
        self, state_type: str, num_qubits: int, custom_params: Optional[Dict] = None
    ) -> QuantumCircuit:
        """
        Prepare the quantum circuit with the specified state.

        Args:
            state_type (str): Type of quantum state.
            num_qubits (int): Number of qubits.
            custom_params (dict, optional): Custom parameters.

        Returns:
            QuantumCircuit: The prepared quantum circuit.
        """
        qc = prepare_state(
            state_type,
            num_qubits,
            custom_params=custom_params,
            add_barrier=False,
            experiment_id=self.experiment_id,
        )

        logger_utils.log_with_experiment_id(
            self.logger,
            "info",
            f"Prepared {state_type} state with {num_qubits} qubits",
            self.experiment_id,
            extra_info={
                "num_qubits": num_qubits,
                "state_type": state_type,
                "circuit_depth": qc.depth(),
                "num_gates": sum(qc.count_ops().values()),
            },
        )

        if custom_params:
            logger_utils.log_with_experiment_id(
                self.logger,
                "debug",
                f"Applied custom parameters: {custom_params}",
                self.experiment_id,
                extra_info={"custom_params": custom_params},
            )

        return qc

    def _apply_noise(
        self,
        noise_enabled: bool,
        noise_type: str,
        num_qubits: int,
        error_rate: Optional[float],
        z_prob: Optional[float],
        i_prob: Optional[float],
        t1: Optional[float],
        t2: Optional[float],
        sim_mode: str,
    ) -> Optional[object]:
        """
        Apply noise model to the experiment.

        Args:
            noise_enabled (bool): Whether to apply noise.
            noise_type (str): Type of noise model.
            num_qubits (int): Number of qubits.
            error_rate (float, optional): Custom error rate.
            z_prob (float, optional): Z probability for PHASE_FLIP.
            i_prob (float, optional): I probability for PHASE_FLIP.
            t1 (float, optional): T1 relaxation time.
            t2 (float, optional): T2 dephasing time.
            sim_mode (str): Simulation mode.

        Returns:
            Optional[object]: The noise model or None.
        """
        if not noise_enabled:
            return None

        try:
            noise_model = create_noise_model(
                noise_type=noise_type,
                num_qubits=num_qubits,
                error_rate=error_rate,
                z_prob=z_prob,
                i_prob=i_prob,
                t1=t1,
                t2=t2,
                simulate_density=(sim_mode == "density"),
                experiment_id=self.experiment_id,
            )

            logger_utils.log_with_experiment_id(
                self.logger,
                "info",
                (
                    f"Applied {noise_type} noise with params: error_rate={error_rate}, "
                    f"z_prob={z_prob}, i_prob={i_prob}, t1={t1}, t2={t2}"
                ),
                self.experiment_id,
                extra_info={
                    "noise_type": noise_type,
                    "error_rate": error_rate,
                    "z_prob": z_prob,
                    "i_prob": i_prob,
                    "t1": t1,
                    "t2": t2,
                },
            )

            return noise_model

        except Exception as e:
            logger_utils.log_with_experiment_id(
                self.logger,
                "error",
                f"Failed to apply noise model: {str(e)}",
                self.experiment_id,
            )
            raise

    def _configure_simulation(
        self, qc: QuantumCircuit, sim_mode: str
    ) -> Tuple[object, QuantumCircuit]:
        """
        Configure the backend and circuit for simulation.

        Args:
            qc (QuantumCircuit): The quantum circuit.
            sim_mode (str): Simulation mode.

        Returns:
            Tuple[object, QuantumCircuit]: Backend and configured circuit.
        """
        if sim_mode == "density":
            # TODO: Revert to method="density_matrix" once Qiskit-Aer bug is fixed
            backend = AerSimulator(method="statevector")
            qc.save_statevector()
            logger_utils.log_with_experiment_id(
                self.logger,
                "debug",
                "Configured circuit for density simulation using statevector workaround",
                self.experiment_id,
            )
        else:
            backend = Aer.get_backend("qasm_simulator")
            qc.measure_all()
            logger_utils.log_with_experiment_id(
                self.logger,
                "debug",
                "Added measurements for qasm simulation",
                self.experiment_id,
            )

        return backend, qc

    def _transpile_circuit(self, qc: QuantumCircuit, backend: object) -> QuantumCircuit:
        """
        Transpile the circuit for the backend.

        Args:
            qc (QuantumCircuit): The quantum circuit.
            backend (object): The backend to transpile for.

        Returns:
            QuantumCircuit: The transpiled circuit.
        """
        logger_utils.log_with_experiment_id(
            self.logger, "info", "Transpiling circuit", self.experiment_id
        )

        start_time = time.time()
        circuit_compiled = transpile(qc, backend)
        transpile_time = time.time() - start_time

        logger_utils.log_with_experiment_id(
            self.logger,
            "info",
            f"Transpilation completed in {transpile_time:.3f} seconds",
            self.experiment_id,
            extra_info={
                "transpile_time": transpile_time,
                "compiled_circuit_depth": circuit_compiled.depth(),
                "compiled_num_gates": sum(circuit_compiled.count_ops().values()),
            },
        )

        logger.info("Circuit transpilation completed")
        return circuit_compiled

    def _run_simulation(
        self,
        circuit_compiled: QuantumCircuit,
        backend: object,
        shots: int,
        noise_model: Optional[object],
        sim_mode: str,
    ) -> Union[Dict, DensityMatrix]:
        """
        Run the simulation and process results.

        Args:
            circuit_compiled (QuantumCircuit): The compiled circuit.
            backend (object): The backend to run on.
            shots (int): Number of shots.
            noise_model (object, optional): The noise model.
            sim_mode (str): Simulation mode.

        Returns:
            Union[Dict, DensityMatrix]: The simulation results.
        """
        start_time = time.time()

        try:
            job = backend.run(
                circuit_compiled,
                shots=shots if sim_mode == "qasm" else 1,
                noise_model=noise_model,
            )
            result = job.result()
        except Exception as e:
            logger_utils.log_with_experiment_id(
                self.logger, "error", f"Simulation failed: {str(e)}", self.experiment_id
            )
            raise

        simulation_time = time.time() - start_time
        logger_utils.log_with_experiment_id(
            self.logger,
            "info",
            f"Simulation completed in {simulation_time:.3f} seconds",
            self.experiment_id,
            extra_info={"simulation_time": simulation_time},
        )

        # Process results
        if sim_mode == "qasm":
            return self._process_qasm_results(result)
        else:
            return self._process_density_results(result)

    def _process_qasm_results(self, result: object) -> Dict:
        """
        Process qasm simulation results.

        Args:
            result (object): The simulation result.

        Returns:
            Dict: Processed results.
        """
        counts = result.get_counts()
        total_counts = sum(counts.values())
        probabilities = {state: count / total_counts for state, count in counts.items()}

        logger_utils.log_with_experiment_id(
            self.logger,
            "info",
            "Qasm simulation completed",
            self.experiment_id,
            extra_info={
                "counts": counts,
                "probabilities": probabilities,
                "total_shots": total_counts,
            },
        )

        return {"counts": counts, "metadata_file": "results_placeholder"}

    def _process_density_results(self, result: object) -> DensityMatrix:
        """
        Process density simulation results.

        Args:
            result (object): The simulation result.

        Returns:
            DensityMatrix: The density matrix.
        """
        statevector = result.get_statevector()
        density_matrix = DensityMatrix(statevector)

        logger_utils.log_with_experiment_id(
            self.logger,
            "info",
            "Density simulation completed via statevector workaround",
            self.experiment_id,
            extra_info={
                "density_matrix_shape": density_matrix.data.shape,
                "trace": float(np.real(np.trace(density_matrix.data))),
            },
        )

        return density_matrix


def run_experiment(
    num_qubits: int,
    state_type: str = "GHZ",
    noise_type: str = "DEPOLARIZING",
    noise_enabled: bool = True,
    shots: int = 1024,
    sim_mode: str = "qasm",
    error_rate: Optional[float] = None,
    z_prob: Optional[float] = None,
    i_prob: Optional[float] = None,
    t1: Optional[float] = None,
    t2: Optional[float] = None,
    custom_params: Optional[Dict] = None,
    experiment_id: str = "N/A",
) -> Tuple[QuantumCircuit, Union[Dict, DensityMatrix]]:
    """
    Convenience function to run a quantum experiment.

    This function provides a simple interface to the ExperimentRunner class.

    Args:
        num_qubits (int): Number of qubits in the circuit.
        state_type (str): Type of quantum state ("GHZ", "W", "CLUSTER").
        noise_type (str): Type of noise model to apply.
        noise_enabled (bool): Whether to apply noise.
        shots (int): Number of shots for qasm simulation.
        sim_mode (str): Simulation mode ("qasm" or "density").
        error_rate (float, optional): Custom error rate for noise models.
        z_prob (float, optional): Z probability for PHASE_FLIP noise.
        i_prob (float, optional): I probability for PHASE_FLIP noise.
        t1 (float, optional): T1 relaxation time for THERMAL_RELAXATION noise.
        t2 (float, optional): T2 dephasing time for THERMAL_RELAXATION noise.
        custom_params (dict, optional): Custom parameters for state preparation or noise.
        experiment_id (str): Unique identifier for this experiment run.

    Returns:
        Tuple[QuantumCircuit, Union[Dict, DensityMatrix]]: The quantum circuit and simulation result.
    """
    runner = ExperimentRunner(experiment_id)
    return runner.run_experiment(
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
    )
