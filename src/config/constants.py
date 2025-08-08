"""
Constants for the Quantum Experiment Framework.

This module defines all constant values used throughout the framework,
including valid types, shortcuts, and configuration constants.
"""

# === 🧪 Valid Experiment Types ===
VALID_NOISE_TYPES = [
    "DEPOLARIZING",
    "PHASE_FLIP",
    "AMPLITUDE_DAMPING",
    "PHASE_DAMPING",
    "THERMAL_RELAXATION",
    "BIT_FLIP",
]

VALID_STATE_TYPES = [
    "GHZ",
    "W",
    "CLUSTER",
    "BELL",
    "SUPERPOSITION",
    "CUSTOM",
    "RANDOM",
]

VALID_SIM_MODES = ["qasm", "density"]

# === ⌨️ User Interface Shortcuts ===
NOISE_SHORTCUTS = {
    "d": "DEPOLARIZING",
    "p": "PHASE_FLIP",
    "a": "AMPLITUDE_DAMPING",
    "z": "PHASE_DAMPING",
    "t": "THERMAL_RELAXATION",
    "b": "BIT_FLIP",
}

STATE_SHORTCUTS = {
    "g": "GHZ",
    "w": "W",
    "c": "CLUSTER",
}

# === 🔧 Technical Constants ===
SINGLE_QUBIT_NOISE_TYPES = ["AMPLITUDE_DAMPING", "PHASE_DAMPING", "BIT_FLIP"]

# === 📊 Analysis Constants ===
MAX_CORRELATION_ORDER = 4
MIN_OCCURRENCES_THRESHOLD = 0.001
DEFAULT_CLUSTERING_THRESHOLD = 0.5

# === 🎨 Visualization Constants ===
DEFAULT_NODE_COLOR = "blue"
DEFAULT_EDGE_COLOR = "red"
DEFAULT_PLOT_STYLE = "default"
