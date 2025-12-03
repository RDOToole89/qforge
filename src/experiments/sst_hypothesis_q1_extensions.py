"""
SST Hypothesis Q1 (Extensions): Control and Scaling

This module adds two critical experiments to complete the SST hypothesis testing:

1. Depolarizing Control (6q):
   Tests if the "River" effect persists under random noise in large systems.
   Hypothesis: PCR should collapse to ~1 (Fog), proving that Entanglement ALONE
   is not enough; you need Structured Noise + Entanglement.

2. Huge Scale (8q):
   Tests the limits of the "River Scaling" effect.
   Hypothesis: PCR should increase exponentially with system size.
   4q (~200) -> 6q (~500) -> 8q (???)
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig
from src.experiments.base import BaseExperiment


class SSTHypothesisQ1LargeDepolarizing(BaseExperiment):
    """
    SST Q1 Large Scale Control (6 Qubits, Depolarizing).

    The "Null Hypothesis" test. We apply random (depolarizing) noise to the
    highly entangled 6-qubit GHZ state.

    Prediction:
    Despite the high entanglement, the random noise will scatter errors isotropically.
    PCR should be low (~1-2), confirming that the "River" requires structured noise.
    """

    name = "sst_q1_large_depolarizing"
    description = "SST Q1 Large Control (6q GHZ + Depolarizing Noise)"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",  # Random noise
            error_rate=0.1,
            shots=8192,
            enable_research_metrics=True,
            research_type="structured_decoherence",
        )


class SSTHypothesisQ1Huge(BaseExperiment):
    """
    SST Q1 Huge Scale (8 Qubits).

    Pushing the "River Scaling" to the limit of classical simulation comfort.
    8 qubits = 256 states.

    Prediction:
    If the "River" effect scales with system size, the PCR for 8 qubits
    should be significantly higher than for 6 qubits (which was ~520).
    This would demonstrate robust protection of the error channel.
    """

    name = "sst_q1_huge"
    description = "SST Q1 Huge Scale (8q GHZ) to test exponential scaling"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=8,  # Scaling up to 8
            state_type="GHZ",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=16384,  # Doubled shots for larger Hilbert space
            enable_research_metrics=True,
            research_type="structured_decoherence",
        )


# Module-level instances
sst_q1_large_depolarizing = SSTHypothesisQ1LargeDepolarizing()
sst_q1_huge = SSTHypothesisQ1Huge()
