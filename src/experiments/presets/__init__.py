"""
Preset experiments module for the Quantum Experiment Framework.

This module provides predefined experiments organized by difficulty level
and category for easy access and learning.
"""

from .beginner import BEGINNER_EXPERIMENTS
from .intermediate import INTERMEDIATE_EXPERIMENTS
from .advanced import ADVANCED_EXPERIMENTS
from .research import RESEARCH_EXPERIMENTS


def load_preset_experiments() -> dict:
    """
    Load all preset experiments.

    Returns:
        dict: Dictionary of all preset experiments.
    """
    all_experiments = {}

    # Load experiments from each difficulty level
    all_experiments.update(BEGINNER_EXPERIMENTS)
    all_experiments.update(INTERMEDIATE_EXPERIMENTS)
    all_experiments.update(ADVANCED_EXPERIMENTS)
    all_experiments.update(RESEARCH_EXPERIMENTS)

    return all_experiments


__all__ = [
    "load_preset_experiments",
    "BEGINNER_EXPERIMENTS",
    "INTERMEDIATE_EXPERIMENTS",
    "ADVANCED_EXPERIMENTS",
    "RESEARCH_EXPERIMENTS",
]
