"""
Engine-native research handler.

Replaces legacy core research handler with a clean, schema-based implementation.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import platform
import subprocess
import sys

logger = logging.getLogger(__name__)


class EngineResearchHandler:
    """
    Engine-native research handler for experiment analysis.

    This replaces the legacy core research handler with a clean,
    schema-based implementation that integrates directly with the engine.
    """

    def __init__(self, results_dir: str = "results"):
        """
        Initialize the engine research handler.

        Args:
            results_dir: Directory to save research results
        """
        self.results_dir = results_dir
        self.logger = logging.getLogger(__name__)

    def process_experiment_result(
        self,
        circuit: Any,
        result: Any,
        experiment_config: Dict[str, Any],
        experiment_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a quantum experiment result with engine-native analysis.

        Args:
            circuit: Qiskit quantum circuit
            result: Qiskit experiment result
            experiment_config: Experiment configuration parameters
            experiment_id: Unique experiment identifier

        Returns:
            Engine-native analysis dictionary
        """
        if experiment_id is None:
            experiment_id = f"{experiment_config.get('state_type', 'UNKNOWN')}_engine"

        self.logger.info(f"Processing engine experiment: {experiment_id}")

        # Extract basic experiment metadata
        analysis = {
            "experiment_metadata": {
                "experiment_id": experiment_id,
                "timestamp": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "research_type": experiment_config.get("research_type", "baseline"),
                "experiment_description": f"{experiment_config.get('state_type', 'UNKNOWN')} state experiment with {experiment_config.get('num_qubits', 0)} qubits",
            },
            "experiment_parameters": experiment_config,
            "circuit_statistics": self._create_circuit_statistics(circuit),
            "measurement_results": self._create_measurement_results(result),
            "provenance": self._create_provenance(experiment_config),
            "research_metrics": {},  # Will be populated by engine analysis
        }

        # Extract counts if available
        if hasattr(result, "get_counts"):
            counts = result.get_counts()
            analysis["measurement_counts"] = dict(counts)
            analysis["total_shots"] = sum(counts.values())
            analysis["unique_outcomes"] = len(counts)
        elif isinstance(result, dict) and "counts" in result:
            counts = result["counts"]
            analysis["measurement_counts"] = dict(counts)
            analysis["total_shots"] = sum(counts.values())
            analysis["unique_outcomes"] = len(counts)
        else:
            analysis["measurement_counts"] = {}
            analysis["total_shots"] = 0
            analysis["unique_outcomes"] = 0
            self.logger.warning("No measurement counts available in result")

        self.logger.info(f"Completed engine analysis for: {experiment_id}")
        return analysis

    def _create_circuit_statistics(self, circuit: Any) -> Dict[str, Any]:
        """Create circuit statistics from quantum circuit."""
        if not circuit:
            return {
                "depth": 0,
                "num_gates": 0,
                "num_qubits": 0,
                "gate_types": {},
                "two_qubit_gate_count": 0,
            }

        gate_counts = circuit.count_ops()
        two_qubit_count = sum(
            count
            for gate, count in gate_counts.items()
            if gate in ["cx", "cz", "swap", "crx", "cry", "crz"]
        )

        return {
            "depth": circuit.depth(),
            "num_gates": circuit.size(),
            "num_qubits": circuit.num_qubits,
            "gate_types": gate_counts,
            "two_qubit_gate_count": two_qubit_count,
        }

    def _create_measurement_results(self, result: Any) -> Dict[str, Any]:
        """Create measurement results from quantum result."""
        if hasattr(result, "get_counts"):
            counts = result.get_counts()
            total_shots = sum(counts.values())
            unique_outcomes = len(counts)
            # Calculate probabilities
            probabilities = {k: v / total_shots for k, v in counts.items()}
        elif isinstance(result, dict) and "counts" in result:
            counts = result["counts"]
            total_shots = sum(counts.values())
            unique_outcomes = len(counts)
            probabilities = {k: v / total_shots for k, v in counts.items()}
        else:
            counts = {}
            total_shots = 0
            unique_outcomes = 0
            probabilities = {}
            self.logger.warning("No measurement counts available in result")

        return {
            "raw_counts": dict(counts),
            "total_shots": total_shots,
            "unique_outcomes": unique_outcomes,
            "outcome_probabilities": probabilities,
        }

    def _create_provenance(self, experiment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create provenance information for the experiment."""
        try:
            git_sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            git_sha = "unknown"

        return {
            "software_versions": {
                "python": sys.version,
                "qiskit": self._get_qiskit_version(),
            },
            "host": {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_implementation": platform.python_implementation(),
            },
            "git_commit": git_sha,
            "timestamp": datetime.now().isoformat(),
            "config_hash": str(hash(str(experiment_config)))[:8],
        }

    def _get_qiskit_version(self) -> str:
        """Get Qiskit version."""
        try:
            import qiskit

            return qiskit.__version__
        except ImportError:
            return "unknown"
