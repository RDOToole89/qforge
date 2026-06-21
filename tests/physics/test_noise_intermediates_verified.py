"""Exact-value tests for intermediary physics calculations in noise models.

These helper methods are executed during noise-model construction/application but
their numeric outputs were never asserted directly. Each value below is a
closed-form physics quantity verified independently against the implementation.

Run with::

    pytest tests/physics/test_noise_intermediates_verified.py
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.noise_models.amplitude_damping import AmplitudeDampingNoise
from src.core.noise_models.bit_flip import BitFlipNoise
from src.core.noise_models.correlated_depolarizing import CorrelatedDepolarizingNoise
from src.core.noise_models.depolarizing import DepolarizingNoise
from src.core.noise_models.phase_damping import PhaseDampingNoise
from src.core.noise_models.phase_flip import PhaseFlipNoise
from src.core.noise_models.thermal_relaxation import ThermalRelaxationNoise

# --------------------------------------------------------------------------- #
# Thermal relaxation intermediates
# --------------------------------------------------------------------------- #


def test_thermal_population_temperature_half() -> None:
    """Boltzmann excited-state population at T=0.5K (5.5 GHz qubit)."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, temperature=0.5)
    assert noise._thermal_population == pytest.approx(0.370988243178081, rel=1e-12)


def test_thermal_population_default_temperature_negligible() -> None:
    """At the default dilution-fridge T=0.015K the excited population is tiny."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6)  # temperature=0.015 default
    assert noise._thermal_population == pytest.approx(2.2735933e-08, rel=1e-6)
    assert noise._thermal_population < 1e-6


def test_thermal_t1_error_rate() -> None:
    """T1 gate error rate 1 - exp(-gate_time/T1) for 20ns gate, T1=100us."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, gate_time=20e-9)
    assert noise._calculate_t1_error_rate() == pytest.approx(1.9998000133325533e-4, rel=1e-12)


def test_thermal_t2_error_rate() -> None:
    """T2 gate error rate 1 - exp(-gate_time/T2) for 20ns gate, T2=80us."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, gate_time=20e-9)
    assert noise._calculate_t2_error_rate() == pytest.approx(2.4996875260396845e-4, rel=1e-12)


def test_thermal_combined_error_rate() -> None:
    """Combined rate r1 + r2 - r1*r2 (avoids double counting)."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, gate_time=20e-9)
    assert noise._calculate_combined_error_rate() == pytest.approx(4.4989876518574474e-4, rel=1e-12)


def test_thermal_channel_capacity() -> None:
    """Channel capacity max(0, 1 - combined_error_rate)."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, gate_time=20e-9)
    assert noise._calculate_channel_capacity() == pytest.approx(0.9995501012348142, rel=1e-12)


def test_thermal_gate_times() -> None:
    """Gate-specific durations: CX=2x, SWAP=3x gate_time, virtual gates 0."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, gate_time=20e-9)
    gate_times = noise._get_gate_times()
    assert gate_times["cx"] == pytest.approx(4e-8, rel=1e-12)
    assert gate_times["swap"] == pytest.approx(6e-8, rel=1e-12)
    assert gate_times["z"] == 0.0
    assert gate_times["rz"] == 0.0


# --------------------------------------------------------------------------- #
# Amplitude damping intermediates
# --------------------------------------------------------------------------- #


def test_amplitude_damping_thermal_population_temperature_tenth() -> None:
    """Boltzmann excited-state population at T=0.1K (5.5 GHz qubit)."""
    noise = AmplitudeDampingNoise(error_rate=0.05, temperature=0.1)
    assert noise._thermal_population == pytest.approx(0.06661438503059611, rel=1e-12)


# --------------------------------------------------------------------------- #
# Phase damping intermediates
# --------------------------------------------------------------------------- #


def test_phase_damping_thermal_dephasing_temperature_tenth() -> None:
    """Thermal dephasing min(0.01, kT/1e-3) at T=0.1K -> 8.617e-5*0.1/1e-3."""
    noise = PhaseDampingNoise(error_rate=0.05, temperature=0.1)
    assert noise._thermal_dephasing == pytest.approx(0.008617, rel=1e-12)


def test_phase_damping_thermal_dephasing_zero_temperature() -> None:
    """At T=0 thermal dephasing vanishes exactly."""
    noise = PhaseDampingNoise(error_rate=0.05, temperature=0.0)
    assert noise._thermal_dephasing == 0.0


# --------------------------------------------------------------------------- #
# Depolarizing intermediates
# --------------------------------------------------------------------------- #


def test_depolarizing_max_error_rate_one_qubit() -> None:
    """Single-qubit complete-positivity bound 1 - 1/4 = 0.75."""
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    assert noise._max_error_rate == pytest.approx(0.75, rel=1e-12)


def test_depolarizing_max_error_rate_two_qubit() -> None:
    """Two-qubit complete-positivity bound 1 - 1/16 = 0.9375."""
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=2)
    assert noise._max_error_rate == pytest.approx(0.9375, rel=1e-12)


def test_depolarizing_pauli_probabilities() -> None:
    """At p=0.1: identity 1-3p/4=0.925, each Pauli p/4=0.025."""
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    probs = noise._calculate_pauli_probabilities()
    assert probs["identity"] == pytest.approx(0.925, rel=1e-12)
    assert probs["pauli_x"] == pytest.approx(0.025, rel=1e-12)
    assert probs["pauli_y"] == pytest.approx(0.025, rel=1e-12)
    assert probs["pauli_z"] == pytest.approx(0.025, rel=1e-12)


def test_depolarizing_information_capacity() -> None:
    """information_capacity = max(0, 1 - 2p) -> 0.8 at p=0.1."""
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    assert noise.get_theoretical_properties()["information_capacity"] == pytest.approx(
        0.8, rel=1e-12
    )


# --------------------------------------------------------------------------- #
# Bit flip intermediates
# --------------------------------------------------------------------------- #


def test_bit_flip_channel_capacity() -> None:
    """Binary symmetric channel capacity 1 - H(p) at p=0.1."""
    noise = BitFlipNoise(error_rate=0.1)
    assert noise._calculate_channel_capacity() == pytest.approx(0.5310044064107188, rel=1e-12)


# --------------------------------------------------------------------------- #
# Phase flip intermediates (physics-based magnetic-field path)
# --------------------------------------------------------------------------- #


def test_phase_flip_magnetic_physics_rate() -> None:
    """Magnetic term: min(1, (gamma*B*t)^2 / (2*pi)^2).

    With B=1e-6 T, gamma=2.8e10 rad/(s*T), t=20e-9 s and no charge noise,
    the effective phase-flip rate equals this magnetic contribution exactly.
    """
    noise = PhaseFlipNoise(magnetic_field_noise=1e-6)
    expected = min(1.0, (2.8e10 * 1e-6 * 20e-9) ** 2 / (2 * np.pi) ** 2)
    assert expected == pytest.approx(7.943580797559283e-9, rel=1e-12)
    assert noise.error_rate == pytest.approx(7.943580797559283e-9, rel=1e-12)
    assert noise._calculate_physics_flip_rate() == pytest.approx(7.943580797559283e-9, rel=1e-12)


# --------------------------------------------------------------------------- #
# Correlated depolarizing per-Pauli probabilities (anti-correlated branch)
# --------------------------------------------------------------------------- #


def test_correlated_depolarizing_anticorrelated_per_pauli() -> None:
    """cs=-0.5, p=0.15 anti-correlated: 3 correlated Paulis at 0.005,
    12 uncorrelated Paulis at 0.01125, identity 0.85, total error 0.15.
    """
    p, cs = 0.15, -0.5
    noise = CorrelatedDepolarizingNoise(
        error_rate=p, num_qubits=3, correlation_strength=cs, topology="GHZ"
    )
    channel = noise._build_correlated_2q_channel()
    probs = sorted(channel.probabilities, reverse=True)
    identity_prob, others = probs[0], probs[1:]

    # Closed-form values from the anti-correlated mixing formula.
    t = abs(cs)
    corr_prob = (1 - t) * p / 15.0  # 0.005
    uncorr_prob = (1 - t) * p / 15.0 + t * p / 12.0  # 0.01125
    assert corr_prob == pytest.approx(0.005, rel=1e-12)
    assert uncorr_prob == pytest.approx(0.01125, rel=1e-12)

    assert identity_prob == pytest.approx(0.85, abs=1e-12)
    assert len(others) == 15
    assert sum(1 for x in others if x == pytest.approx(corr_prob, abs=1e-12)) == 3
    assert sum(1 for x in others if x == pytest.approx(uncorr_prob, abs=1e-12)) == 12
    assert sum(others) == pytest.approx(p, abs=1e-12)
