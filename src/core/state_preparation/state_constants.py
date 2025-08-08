# src/state_preparation/state_constants.py

from .ghz_state import GHZState
from .w_state import WState
from .cluster_state import ClusterState
from .superposition_state import SuperpositionState
from .bell_state import BellState

STATE_CLASSES = {
    "GHZ": GHZState,
    "W": WState,
    "CLUSTER": ClusterState,
    "SUPERPOSITION": SuperpositionState,
    "BELL": BellState,
}
