"""Advanced experiments — from quantum superpowers to designing your own.

Organized into two parts:

  steps/       — 8-step progression: algorithms → protocols → design your own
  deep_dives/  — Apply techniques to real problems (Shor's, VQE, BB84, etc.)
"""

# Steps
from src.experiments.advanced.deep_dives.dd_bb84 import bb84

# Deep dives
from src.experiments.advanced.deep_dives.dd_bernstein_vazirani import bernstein_vazirani
from src.experiments.advanced.deep_dives.dd_grover import GroverExperiment, grover_experiment
from src.experiments.advanced.deep_dives.dd_qaoa import QAOAExperiment, qaoa_experiment
from src.experiments.advanced.deep_dives.dd_shor import ShorExperiment, shor_experiment
from src.experiments.advanced.deep_dives.dd_teleportation import TeleportationExperiment
from src.experiments.advanced.deep_dives.dd_vqe import VQEExperiment, vqe_experiment
from src.experiments.advanced.steps.step01_quantum_randomness import quantum_randomness
from src.experiments.advanced.steps.step02_deutsch_jozsa import deutsch_jozsa
from src.experiments.advanced.steps.step03_grover_search import grover_search
from src.experiments.advanced.steps.step04_teleportation import teleportation
from src.experiments.advanced.steps.step05_superdense_coding import superdense
from src.experiments.advanced.steps.step06_qft import qft
from src.experiments.advanced.steps.step07_error_correction import error_correction
from src.experiments.advanced.steps.step08_design_your_own import design_your_own

__all__ = [
    # Steps
    "quantum_randomness",
    "deutsch_jozsa",
    "grover_search",
    "teleportation",
    "superdense",
    "qft",
    "error_correction",
    "design_your_own",
    # Deep dives
    "bernstein_vazirani",
    "bb84",
    "ShorExperiment",
    "shor_experiment",
    "GroverExperiment",
    "grover_experiment",
    "TeleportationExperiment",
    "VQEExperiment",
    "vqe_experiment",
    "QAOAExperiment",
    "qaoa_experiment",
]
