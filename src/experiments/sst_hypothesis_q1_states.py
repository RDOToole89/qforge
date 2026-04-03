"""SST Hypothesis Q1 (States): W State and Product State.

This module extends the SST hypothesis testing to different quantum states
to verify that the "River Scaling" effect is specific to certain entanglement structures.

We compare:
1. GHZ State (Reference): "River" effect (high PCR).
2. W State: Different entanglement topology.
3. Product State (Superposition): No entanglement. Should show "Fog" (low PCR).
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig
from src.experiments.base import BaseExperiment


class SSTHypothesisQ1WState(BaseExperiment):
    """SST Hypothesis Q1 with W State.

    W states have a different entanglement structure than GHZ states.
    They are robust against particle loss but have different correlation properties.
    We test if they exhibit the same "River" effect under amplitude damping.
    """

    name = "sst_q1_w"
    description = "SST Q1 with W state (multipartite entanglement)"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for W state experiment."""
        return ExperimentConfig(
            num_qubits=6,  # Match the "large" GHZ experiment size
            state_type="W",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=8192,
            metrics="structured_decoherence",
        )


class SSTHypothesisQ1ProductState(BaseExperiment):
    """SST Hypothesis Q1 with Product State (Superposition).

    A separable state (|+>|+>...|+>) has no entanglement.
    Under amplitude damping, errors should be independent on each qubit.
    We expect this to show a "Fog" pattern (low PCR, uniform spreading)
    rather than a "River", serving as a negative control.
    """

    name = "sst_q1_product"
    description = "SST Q1 with Product state (no entanglement)"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for Product state experiment."""
        return ExperimentConfig(
            num_qubits=6,  # Match the "large" GHZ experiment size
            state_type="SUPERPOSITION",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=8192,
            metrics="structured_decoherence",
        )


# Module-level instances
sst_q1_w = SSTHypothesisQ1WState()
sst_q1_product = SSTHypothesisQ1ProductState()
