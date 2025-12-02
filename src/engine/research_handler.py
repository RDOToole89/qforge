"""
Engine-native experiment runner.

This module is the engine's execution workhorse:
- builds a quantum circuit via core state-preparation,
- (optionally) configures a noise model,
- transpiles and simulates on AerSimulator,
- exposes convenience helpers to return canonical counts or a schema-v1
  metrics payload (via the metrics registry).

Design notes
------------
- No backward compatibility shims: imports fail fast if dependencies are missing.
- QASM-only: density-matrix or statevector modes are intentionally out-of-scope here.
- Canonicalization: measurement bitstrings are MSB-left and padded/truncated to `num_qubits`.
- The runner does not manage storage or research integration; the API facade/orchestrator does.

Typical usage
-------------
    runner = EngineExperimentRunner("ghz-3q")
    circ, result = runner.run_experiment(num_qubits=3, state_type="GHZ", shots=4096)
    circ, counts = runner.run_to_counts(num_qubits=3, state_type="GHZ")
    circ, schema = runner.run_to_schema(num_qubits=3, state_type="GHZ")  # requires metrics package
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Canonical metrics + schema v1 (engine-facing; intentional hard dependency for run_to_schema)
from src.analysis.metrics.registry import compute_all
from src.analysis.metrics.schema_bridge import metrics_to_schema
from src.core.noise_models import create_noise_model

# Sophisticated state preparation and noise (engine-core)
from src.core.state_preparation import prepare_state

logger = logging.getLogger(__name__)


class EngineExperimentRunner:
    """
    Engine-native experiment runner for quantum circuit execution.

    Responsibilities
    ----------------
    - Build a circuit using `src.core.state_preparation.prepare_state`
    - Optionally attach a noise model created via `src.core.noise_models.create_noise_model`
    - Transpile and simulate with AerSimulator (QASM)
    - Offer helpers to return canonical counts or schema-v1 metric dicts

    This class deliberately avoids storage, visualization, or research
    persistence concerns (handled by the API facade/orchestrator).
    """

    def __init__(self, experiment_id: str = "engine-run"):
        """
        Initialize the runner.

        Args:
            experiment_id: Logical identifier used only for logging scoping.
        """
        self.experiment_id = experiment_id
        self.logger = logging.getLogger(f"EngineExperimentRunner.{experiment_id}")
        self.noise_model = None  # set when noise is configured

    # ---------- Public API ----------

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
    ) -> tuple[QuantumCircuit, Any]:
        """
        Build, (optionally) noise-configure, and simulate a circuit.

        Args:
            num_qubits: Number of qubits.
            state_type: "GHZ" | "W" | "CLUSTER" | "BELL" | "SUPERPOSITION" | "CUSTOM".
            noise_type: Noise model name (see core/noise_models).
            noise_enabled: Whether to attach a noise model.
            shots: Number of QASM shots.
            sim_mode: Only "qasm" is supported (others are warned and coerced).
            error_rate, z_prob, i_prob, t1, t2: Noise parameters (model-dependent).
            custom_params: Extra params forwarded to state preparation/noise (if supported).
            rng_seed: Simulator seed for reproducibility.

        Returns:
            (QuantumCircuit, Aer result payload)
        """
        self.logger.info("Starting engine experiment: %s (%d qubits)", state_type, num_qubits)

        circuit = self._create_circuit(num_qubits, state_type, custom_params)

        if noise_enabled and noise_type:
            circuit = self._apply_noise(circuit, noise_type, error_rate, z_prob, i_prob, t1, t2)

        result = self._execute_simulation(circuit, sim_mode, shots, rng_seed)

        self.logger.info("Completed experiment: %s", self.experiment_id)
        return circuit, result

    def run_to_counts(
        self,
        *,
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
    ) -> tuple[QuantumCircuit, Mapping[str, int]]:
        """
        Convenience: run and return (circuit, canonicalized counts dict).
        Canonicalization: MSB-left bitstrings of exact length `num_qubits`.
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
    ) -> tuple[QuantumCircuit, dict[str, Any]]:
        """
        Run an experiment and return (circuit, schema_v1 metrics dict).

        This requires the metrics registry & schema bridge to be importable:
        - src.analysis.metrics.registry.compute_all
        - src.analysis.metrics.schema_bridge.metrics_to_schema
        """
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

        metric_results = compute_all(counts=counts)
        schema_v1 = metrics_to_schema(metric_results)
        return circuit, schema_v1

    # ---------- Internals ----------

    def _create_circuit(
        self, num_qubits: int, state_type: str, custom_params: dict | None
    ) -> QuantumCircuit:
        """Create a circuit via sophisticated core state-prep. Falls back to a basic template if core prep fails."""
        try:
            params = {
                "num_qubits": int(num_qubits),
                "state_type": str(state_type).upper(),
            }
            if custom_params:
                params.update(custom_params)
            circ = prepare_state(**params)

            # Ensure measurement exists for QASM runs
            if not circ.clbits:
                circ.measure_all()
            return circ

        except Exception as e:
            self.logger.error("Core state preparation failed (%s); using basic template.", e)
            return self._create_basic_circuit(num_qubits, state_type, custom_params)

    def _create_basic_circuit(
        self, num_qubits: int, state_type: str, custom_params: dict | None
    ) -> QuantumCircuit:
        """Basic fallback patterns (dev safety)."""
        circuit = QuantumCircuit(num_qubits, num_qubits)
        st = str(state_type).upper()

        if st == "GHZ":
            circuit.h(0)
            for i in range(1, num_qubits):
                circuit.cx(0, i)
        elif st == "W":
            circuit.h(0)
            for i in range(1, num_qubits):
                circuit.cx(0, i)
                circuit.h(i)
        elif st == "BELL":
            if num_qubits < 2:
                raise ValueError("BELL state requires at least 2 qubits")
            circuit.h(0)
            circuit.cx(0, 1)
        elif st == "CLUSTER":
            for i in range(num_qubits):
                circuit.h(i)
            for i in range(num_qubits - 1):
                circuit.cx(i, i + 1)
        elif st == "SUPERPOSITION":
            for i in range(num_qubits):
                circuit.h(i)
        elif st == "CUSTOM":
            ops = (custom_params or {}).get("circuit_operations", [])
            for op in ops:
                g = op.get("gate", "").lower()
                if g == "h":
                    circuit.h(int(op["qubit"]))
                elif g == "cx":
                    circuit.cx(int(op["control"]), int(op["target"]))
                elif g == "x":
                    circuit.x(int(op["qubit"]))
            if not ops:
                for i in range(num_qubits):
                    circuit.h(i)
        else:
            raise ValueError(f"Unsupported state type: {state_type}")

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
    ) -> QuantumCircuit:
        """Create and attach a noise model produced by core noise models."""
        try:
            noise_params: dict[str, Any] = {
                "noise_type": str(noise_type).upper(),
                "num_qubits": circuit.num_qubits,
            }
            if error_rate is not None:
                noise_params["error_rate"] = float(error_rate)
            if z_prob is not None:
                noise_params["z_prob"] = float(z_prob)
            if i_prob is not None:
                noise_params["i_prob"] = float(i_prob)
            if t1 is not None:
                noise_params["t1"] = float(t1)
            if t2 is not None:
                noise_params["t2"] = float(t2)

            self.noise_model = create_noise_model(**noise_params)
            self.logger.info("Noise model created: %s", noise_params["noise_type"])
            return circuit

        except Exception as e:
            self.logger.error("Noise creation failed (%s); proceeding without noise.", e)
            self.noise_model = None
            return circuit

    def _execute_simulation(
        self,
        circuit: QuantumCircuit,
        sim_mode: str,
        shots: int,
        rng_seed: int | None,
    ) -> Any:
        """Transpile and run a QASM simulation on AerSimulator."""
        if sim_mode != "qasm":
            self.logger.warning("Simulation mode '%s' not supported; coercing to QASM.", sim_mode)

        backend = AerSimulator()
        if rng_seed is not None:
            backend.set_options(seed_simulator=int(rng_seed))
        if self.noise_model is not None:
            backend.set_options(noise_model=self.noise_model)

        tcirc = transpile(circuit, backend)
        job = backend.run(tcirc, shots=int(shots))
        return job.result()

    # ---------- Helpers ----------

    def _extract_canonical_counts(self, result: Any, num_qubits: int) -> dict[str, int]:
        """
        Extract counts from a Qiskit Result and canonicalize bitstrings.
        - Strip spaces Qiskit may insert for registers.
        - Pad/truncate to `num_qubits`.
        - Keep MSB-left ordering (compatible with metrics).
        """
        try:
            raw_counts = result.get_counts()  # type: ignore[attr-defined]
        except Exception:
            raw_counts = result.get_counts(0)  # type: ignore[attr-defined]

        counts: dict[str, int] = {}
        for k, v in raw_counts.items():
            key = str(k).replace(" ", "")
            if len(key) < num_qubits:
                key = key.rjust(num_qubits, "0")
            elif len(key) > num_qubits:
                key = key[-num_qubits:]
            counts[key] = int(v)

        if not counts:
            self.logger.warning("No counts in result; fabricating zero-count for '0'*n.")
            counts["0" * num_qubits] = 0
        return counts


def run_raw(config: dict[str, Any]) -> tuple[Any, Any]:
    """
    Thin convenience wrapper used by the API facade.

    Args:
        config: A dict compatible with ExperimentConfig.model_dump().

    Returns:
        (QuantumCircuit, Aer Result)
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
    )
    return circuit, raw
