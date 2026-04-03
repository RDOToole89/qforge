"""SST Hypothesis Q1 (Large Scale): Specific Noise Points.

These experiments represent specific data points on the "River Scaling" curve.
Registered separately to ensure exact reproducibility via CLI.
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig
from src.experiments.sst_hypothesis_q1_large import SSTHypothesisQ1Large


class SSTHypothesisQ1LargeHighNoise(SSTHypothesisQ1Large):
    """SST Q1 Large Scale (6-qubit) at High Noise (0.2).

    Tests the "River" behavior as it approaches saturation.
    """

    name = "sst_q1_large_high_noise"
    description = "SST Q1 Large Scale (6q) at High Noise (gamma=0.2)"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration with high noise rate of 0.2."""
        config = super().default_config()
        config.error_rate = 0.2
        return config


class SSTHypothesisQ1LargeMaxNoise(SSTHypothesisQ1Large):
    """SST Q1 Large Scale (6-qubit) at Max Noise (0.3).

    Tests the "River" behavior at deep saturation (Fog).
    """

    name = "sst_q1_large_max_noise"
    description = "SST Q1 Large Scale (6q) at Max Noise (gamma=0.3)"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration with max noise rate of 0.3."""
        config = super().default_config()
        config.error_rate = 0.3
        return config


# Module-level instances
sst_q1_large_high_noise = SSTHypothesisQ1LargeHighNoise()
sst_q1_large_max_noise = SSTHypothesisQ1LargeMaxNoise()
