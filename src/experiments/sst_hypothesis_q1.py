
import numpy as np
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from src.engine.experiment_runner import EngineExperimentRunner
from src.core.analysis.metrics.pathway_concentration_ratio import compute_concentration_with_gini
from src.core.analysis.core.information_theory import counts_to_probabilities

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SST_Experiment")

def run_sst_hypothesis_q1(
    num_qubits: int = 4,
    noise_steps: int = 20,
    max_error_rate: float = 0.5,
    shots: int = 4096,
    output_dir: str = "results/sst_q1"
):
    """
    Executes the protocol for H_Q1: Structured Decoherence Pathways.

    Hypothesis:
    Realistic quantum noise produces distributions with higher Pathway Concentration Ratio (PCR)
    and lower Entropy than maximal ignorance models, indicating structured decoherence.
    """
    runner = EngineExperimentRunner(experiment_id="sst-h-q1")

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results_data = []
    error_rates = np.linspace(0.0, max_error_rate, noise_steps)

    logger.info(f"Starting H_Q1 Experiment: GHZ-{num_qubits}, {noise_steps} steps")

    for error_rate in error_rates:
        logger.info(f"Running step: error_rate={error_rate:.3f}")

        # 1. Run Experiment (GHZ + Depolarizing Noise)
        # Note: We use 'DEPOLARIZING' as a proxy for generic environmental noise
        # In a real hardware run, we would just measure the hardware.
        circuit, counts = runner.run_to_counts(
            num_qubits=num_qubits,
            state_type="GHZ",
            noise_type="DEPOLARIZING",
            noise_enabled=True,
            error_rate=error_rate,
            shots=shots,
            sim_mode="qasm"
        )

        # 2. Compute Metrics
        pcr, gini = compute_concentration_with_gini(counts)

        # Compute Entropy (manual implementation if module missing)
        probs = np.array(list(counts.values())) / sum(counts.values())
        entropy = -np.sum(probs * np.log2(probs + 1e-10))

        # 3. Store Data
        step_result = {
            "error_rate": float(error_rate),
            "pcr": float(pcr),
            "gini": float(gini),
            "entropy": float(entropy),
            "counts": counts
        }
        results_data.append(step_result)

    # 4. Save Results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/sst_h_q1_ghz{num_qubits}_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump({
            "meta": {
                "hypothesis": "H_Q1",
                "num_qubits": num_qubits,
                "shots": shots,
                "noise_model": "DEPOLARIZING"
            },
            "data": results_data
        }, f, indent=2)

    logger.info(f"Experiment complete. Results saved to {filename}")
    return filename

if __name__ == "__main__":
    run_sst_hypothesis_q1()
