"""Decoherence rate / probability conversions used by the noise models."""

from __future__ import annotations

import numpy as np


def relaxation_probability(t: float, tau: float) -> float:
    """Probability of a relaxation/dephasing event in time ``t`` for timescale ``tau``.

    Implements the standard exponential-decay error probability::

        p = 1 - exp(-t / tau)

    Used for amplitude damping (tau = T1), pure dephasing (tau = T2*), and the
    T1/T2 components of thermal relaxation.

    Args:
        t: Elapsed (gate) time, same units as ``tau``. Must be >= 0.
        tau: Characteristic timescale (T1, T2, T2*). Must be > 0.

    Returns:
        Error probability in [0, 1).

    Raises:
        ValueError: If ``tau <= 0`` or ``t < 0``.
    """
    if tau <= 0:
        raise ValueError(f"Timescale tau must be positive, got {tau}")
    if t < 0:
        raise ValueError(f"Time t must be non-negative, got {t}")
    return float(1 - np.exp(-t / tau))
