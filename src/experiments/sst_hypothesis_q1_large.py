"""
SST Hypothesis Q1 (Large Scale): River Scaling Test

This experiment tests the "River Scaling" hypothesis: that structured decoherence
pathways become *more* concentrated (higher PCR) as system size increases.

Hypothesis:
    PCR(6 qubits) > PCR(4 qubits) under identical noise strength.

Configuration:
    - 6 Qubits (GHZ State)
    - Amplitude Damping Noise
    - 8192 Shots (High precision for rare pathways)
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig
from src.experiments.sst_hypothesis_q1_structured import SSTHypothesisQ1Structured


class SSTHypothesisQ1Large(SSTHypothesisQ1Structured):
    """
    SST Q1 Large Scale Experiment (6 Qubits).

    Designed to test the scaling of structured decoherence metrics.
    Inherits logic from SSTHypothesisQ1Structured but overrides defaults
    for the larger system size.
    """

    name = "sst_q1_large"
    description = "SST Q1 Large Scale (6-qubit GHZ) to test PCR scaling"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for Large Scale SST experiment."""
        return ExperimentConfig(
            num_qubits=6,  # Increased from 4 to 6
            state_type="GHZ",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,  # Standard testing point for "River" effect
            shots=8192,  # Increased shots for better statistics on 2^6 states
            enable_research_metrics=True,
            research_type="structured_decoherence",
        )


# Module-level instance
sst_q1_large = SSTHypothesisQ1Large()
