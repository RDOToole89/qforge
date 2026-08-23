"""Rigorous physics verification tests for ``src/qforge/core/noise_models``.

These tests verify *real* quantum physics of every noise channel:

- Kraus completeness  Σ Kᵢ† Kᵢ = I  (CPTP / trace preservation)
- Exact closed-form Kraus operators against analytic values
- Channel action on density matrices vs. analytic output
- Cross-checks against Qiskit's own error channels via the Choi matrix
  (the canonical, decomposition-independent way to compare two channels)
- Probability conservation for the correlated depolarizing channel
- Parameter-validation / error branches

The channels were recently hardened so that ``get_kraus_operators()`` matches the
channel that ``apply()`` actually simulates, using standard textbook conventions.
These tests assert that *new* behaviour.
"""

from __future__ import annotations

import numpy as np
import pytest
from qiskit_aer.noise import (
    NoiseModel,
    amplitude_damping_error,
    depolarizing_error,
    phase_damping_error,
)

from qforge.core.noise_models.amplitude_damping import AmplitudeDampingNoise
from qforge.core.noise_models.bit_flip import BitFlipNoise
from qforge.core.noise_models.correlated_depolarizing import CorrelatedDepolarizingNoise
from qforge.core.noise_models.depolarizing import DepolarizingNoise
from qforge.core.noise_models.noise_factory import (
    NOISE_CLASSES,
    _apply_readout_errors,
    create_noise_instance,
    create_noise_model,
    create_noise_model_for_hardware,
    get_available_noise_types,
    get_noise_info,
    validate_noise_request,
)
from qforge.core.noise_models.phase_damping import PhaseDampingNoise
from qforge.core.noise_models.phase_flip import PhaseFlipNoise
from qforge.core.noise_models.thermal_relaxation import ThermalRelaxationNoise
from tests._qhelpers import I2, X, Y, Z, apply_channel, choi_equal, completeness_sum

# --------------------------------------------------------------------------- #
# Constants and helpers
# --------------------------------------------------------------------------- #

ATOL = 1e-12


# Kraus-bearing channels (correlated depolarizing returns [] by design).
KRAUS_CHANNEL_FACTORIES = {
    "depolarizing_1q": lambda: DepolarizingNoise(error_rate=0.1, num_qubits=1),
    "depolarizing_2q": lambda: DepolarizingNoise(error_rate=0.1, num_qubits=2),
    "bit_flip": lambda: BitFlipNoise(error_rate=0.1),
    "phase_flip": lambda: PhaseFlipNoise(error_rate=0.1),
    "amplitude_damping": lambda: AmplitudeDampingNoise(error_rate=0.1),
    "phase_damping": lambda: PhaseDampingNoise(error_rate=0.2),
    "thermal_relaxation": lambda: ThermalRelaxationNoise(t1=100e-6, t2=80e-6),
}


# --------------------------------------------------------------------------- #
# Generic Kraus completeness (trace preservation)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", list(KRAUS_CHANNEL_FACTORIES))
def test_kraus_completeness(name: str) -> None:
    """Every Kraus-bearing channel must satisfy Σ Kᵢ† Kᵢ = I."""
    noise = KRAUS_CHANNEL_FACTORIES[name]()
    kraus = noise.get_kraus_operators()
    dim = kraus[0].shape[0]
    assert np.allclose(completeness_sum(kraus), np.eye(dim), atol=ATOL)


# --------------------------------------------------------------------------- #
# Depolarizing channel
# --------------------------------------------------------------------------- #


def test_depolarizing_identity_at_zero() -> None:
    """p=0 → K0 == I and all other operators vanish."""
    kraus = DepolarizingNoise(error_rate=0.0, num_qubits=1).get_kraus_operators()
    assert np.allclose(kraus[0], I2, atol=ATOL)
    for k in kraus[1:]:
        assert np.allclose(k, np.zeros((2, 2)), atol=ATOL)


def test_depolarizing_exact_operators() -> None:
    """p=0.1 → K0=√0.925 I, K1=√0.025 X, K2=√0.025 Y, K3=√0.025 Z."""
    kraus = DepolarizingNoise(error_rate=0.1, num_qubits=1).get_kraus_operators()
    assert np.allclose(kraus[0], np.sqrt(0.925) * I2, atol=ATOL)
    assert np.allclose(kraus[1], np.sqrt(0.025) * X, atol=ATOL)
    assert np.allclose(kraus[2], np.sqrt(0.025) * Y, atol=ATOL)
    assert np.allclose(kraus[3], np.sqrt(0.025) * Z, atol=ATOL)


def test_depolarizing_matches_qiskit_choi() -> None:
    """Framework 1-qubit depolarizing channel == Qiskit depolarizing_error(0.1,1)."""
    kraus = DepolarizingNoise(error_rate=0.1, num_qubits=1).get_kraus_operators()
    assert choi_equal(kraus, depolarizing_error(0.1, 1))


def test_depolarizing_2qubit_operator_count_and_completeness() -> None:
    """2-qubit depolarizing → 16 Kraus operators, Σ Kᵢ† Kᵢ = I₄."""
    kraus = DepolarizingNoise(error_rate=0.1, num_qubits=2).get_kraus_operators()
    assert len(kraus) == 16
    assert all(k.shape == (4, 4) for k in kraus)
    assert np.allclose(completeness_sum(kraus), np.eye(4), atol=ATOL)


def test_depolarizing_2qubit_matches_qiskit_channel() -> None:
    """2-qubit get_kraus() == genuine Qiskit depolarizing_error(p, 2), matching apply().

    Fixed: get_kraus_operators() now returns the true n-qubit depolarizing channel
    (identity weight 1 - p + p/16 = 0.90625), the same channel apply() simulates.
    Previously it returned the tensor product of two 1-qubit channels (identity
    weight (1-3p/4)^2 = 0.855625), which did not match apply().
    """
    p = 0.1
    kraus = DepolarizingNoise(error_rate=p, num_qubits=2).get_kraus_operators()
    # Channel represented by get_kraus() is the genuine 2-qubit depolarizing channel.
    assert choi_equal(kraus, depolarizing_error(p, 2))
    # Sanity: genuine 2-qubit identity weight is 0.90625 (not the tensor 0.855625).
    assert max(depolarizing_error(p, 2).probabilities) == pytest.approx(0.90625, abs=1e-12)


def test_depolarizing_action_uniform_mixing() -> None:
    """ρ → (1-p)ρ + p·I/2 on |0><0|."""
    p = 0.1
    kraus = DepolarizingNoise(error_rate=p, num_qubits=1).get_kraus_operators()
    rho = np.array([[1, 0], [0, 0]], dtype=complex)
    out = apply_channel(kraus, rho)
    expected = (1 - p) * rho + p * I2 / 2
    assert np.allclose(out, expected, atol=ATOL)


def test_depolarizing_max_rate_bound_1q() -> None:
    """1-qubit: p > 1 - 1/4 = 0.75 raises ValueError."""
    with pytest.raises(ValueError):
        DepolarizingNoise(error_rate=0.8, num_qubits=1)
    # Exactly at the bound is allowed.
    DepolarizingNoise(error_rate=0.75, num_qubits=1)


def test_depolarizing_max_rate_bound_2q() -> None:
    """2-qubit: p > 1 - 1/16 = 0.9375 raises ValueError."""
    with pytest.raises(ValueError):
        DepolarizingNoise(error_rate=0.95, num_qubits=2)


def test_depolarizing_negative_rate_raises() -> None:
    with pytest.raises(ValueError):
        DepolarizingNoise(error_rate=-0.1, num_qubits=1)


# --------------------------------------------------------------------------- #
# Bit flip channel (uniform, no gate sensitivity)
# --------------------------------------------------------------------------- #


def test_bit_flip_exact_operators() -> None:
    """p=0.1 → K0=√0.9 I, K1=√0.1 X."""
    kraus = BitFlipNoise(error_rate=0.1).get_kraus_operators()
    assert np.allclose(kraus[0], np.sqrt(0.9) * I2, atol=ATOL)
    assert np.allclose(kraus[1], np.sqrt(0.1) * X, atol=ATOL)


def test_bit_flip_completeness() -> None:
    kraus = BitFlipNoise(error_rate=0.1).get_kraus_operators()
    assert np.allclose(completeness_sum(kraus), I2, atol=ATOL)


def test_bit_flip_channel_action() -> None:
    """ρ=diag(1,0), p=0.1 → diag(0.9,0.1)."""
    kraus = BitFlipNoise(error_rate=0.1).get_kraus_operators()
    rho = np.array([[1, 0], [0, 0]], dtype=complex)
    out = apply_channel(kraus, rho)
    assert np.allclose(out, np.diag([0.9, 0.1]).astype(complex), atol=ATOL)


def test_bit_flip_identity_and_full_flip() -> None:
    """p=0 → identity channel; p=1 → pure X."""
    k0 = BitFlipNoise(error_rate=0.0).get_kraus_operators()
    assert np.allclose(k0[0], I2, atol=ATOL)
    assert np.allclose(k0[1], np.zeros((2, 2)), atol=ATOL)

    k1 = BitFlipNoise(error_rate=1.0).get_kraus_operators()
    assert np.allclose(k1[0], np.zeros((2, 2)), atol=ATOL)
    assert np.allclose(k1[1], X, atol=ATOL)
    rho = np.array([[1, 0], [0, 0]], dtype=complex)
    out = apply_channel(k1, rho)
    assert np.allclose(out, np.array([[0, 0], [0, 1]], dtype=complex), atol=ATOL)


def test_bit_flip_physics_pulse_amplitude_path() -> None:
    """Physics-based rate: p ≈ (Δa/a)² = 0.02² = 4e-4."""
    noise = BitFlipNoise(pulse_amplitude_error=0.02, coherent_error=True)
    assert noise.error_rate == pytest.approx(0.02**2)
    assert noise.coherent_error is True


def test_bit_flip_large_pulse_amplitude_warns(caplog) -> None:
    """pulse_amplitude_error > 0.5 takes the warning branch but still builds."""
    noise = BitFlipNoise(pulse_amplitude_error=0.7)
    assert noise.error_rate == pytest.approx(min(1.0, 0.7**2))


def test_bit_flip_validation() -> None:
    with pytest.raises(ValueError):
        BitFlipNoise(error_rate=1.5)
    with pytest.raises(ValueError):
        BitFlipNoise(pulse_amplitude_error=-0.1)


# --------------------------------------------------------------------------- #
# Phase flip channel (uniform)
# --------------------------------------------------------------------------- #


def test_phase_flip_exact_operators() -> None:
    """p=0.1 → K0=√0.9 I, K1=√0.1 Z."""
    kraus = PhaseFlipNoise(error_rate=0.1).get_kraus_operators()
    assert np.allclose(kraus[0], np.sqrt(0.9) * I2, atol=ATOL)
    assert np.allclose(kraus[1], np.sqrt(0.1) * Z, atol=ATOL)


def test_phase_flip_completeness() -> None:
    kraus = PhaseFlipNoise(error_rate=0.1).get_kraus_operators()
    assert np.allclose(completeness_sum(kraus), I2, atol=ATOL)


def test_phase_flip_dephases_plus_state() -> None:
    """|+><+| with p=0.1 → off-diagonal 0.5·(1-2p) = 0.4."""
    kraus = PhaseFlipNoise(error_rate=0.1).get_kraus_operators()
    plus = 0.5 * np.array([[1, 1], [1, 1]], dtype=complex)
    out = apply_channel(kraus, plus)
    assert out[0, 1].real == pytest.approx(0.5 * (1 - 2 * 0.1))
    assert out[0, 1].real == pytest.approx(0.4)
    # Populations preserved.
    assert out[0, 0].real == pytest.approx(0.5)
    assert out[1, 1].real == pytest.approx(0.5)


def test_phase_flip_full_dephasing_at_half() -> None:
    """p=0.5 → off-diagonal coherence fully destroyed."""
    kraus = PhaseFlipNoise(error_rate=0.5).get_kraus_operators()
    plus = 0.5 * np.array([[1, 1], [1, 1]], dtype=complex)
    out = apply_channel(kraus, plus)
    assert out[0, 1] == pytest.approx(0.0)


def test_phase_flip_physics_magnetic_and_charge() -> None:
    """Physics-based rate paths from magnetic field and charge noise."""
    n_mag = PhaseFlipNoise(magnetic_field_noise=1e-6)
    assert 0.0 <= n_mag.error_rate <= 1.0
    n_q = PhaseFlipNoise(charge_noise=1e-3)
    assert n_q.error_rate == pytest.approx(min(1.0, (1e-3 / 1e-3) ** 2))
    n_both = PhaseFlipNoise(magnetic_field_noise=1e-6, charge_noise=5e-4)
    assert 0.0 <= n_both.error_rate <= 1.0


def test_phase_flip_validation() -> None:
    with pytest.raises(ValueError):
        PhaseFlipNoise(error_rate=2.0)
    with pytest.raises(ValueError):
        PhaseFlipNoise(magnetic_field_noise=-1.0)
    with pytest.raises(ValueError):
        PhaseFlipNoise(charge_noise=-1.0)


# --------------------------------------------------------------------------- #
# Amplitude damping channel (standard T=0)
# --------------------------------------------------------------------------- #


def test_amplitude_damping_exact_operators() -> None:
    """γ=0.1 → K0=diag(1,√0.9), K1=[[0,√0.1],[0,0]]."""
    kraus = AmplitudeDampingNoise(error_rate=0.1).get_kraus_operators()
    assert np.allclose(kraus[0], np.array([[1, 0], [0, np.sqrt(0.9)]], dtype=complex), atol=ATOL)
    assert kraus[0][1, 1].real == pytest.approx(0.9486832980505138)
    assert np.allclose(kraus[1], np.array([[0, np.sqrt(0.1)], [0, 0]], dtype=complex), atol=ATOL)
    assert kraus[1][0, 1].real == pytest.approx(0.31622776601683794)


def test_amplitude_damping_completeness() -> None:
    kraus = AmplitudeDampingNoise(error_rate=0.1).get_kraus_operators()
    assert np.allclose(completeness_sum(kraus), I2, atol=ATOL)


def test_amplitude_damping_matches_qiskit_choi() -> None:
    kraus = AmplitudeDampingNoise(error_rate=0.1).get_kraus_operators()
    assert choi_equal(kraus, amplitude_damping_error(0.1))


def test_amplitude_damping_decays_excited_state() -> None:
    """ρ=diag(0,1), γ=0.1 → diag(0.1,0.9)."""
    kraus = AmplitudeDampingNoise(error_rate=0.1).get_kraus_operators()
    rho = np.array([[0, 0], [0, 1]], dtype=complex)
    out = apply_channel(kraus, rho)
    assert np.allclose(out, np.diag([0.1, 0.9]).astype(complex), atol=ATOL)


def test_amplitude_damping_gamma_from_t1() -> None:
    """γ from T1: t1=100e-6, gate_time=20e-9 → γ = 1 - exp(-gate/T1)."""
    t1, gate_time = 100e-6, 20e-9
    noise = AmplitudeDampingNoise(t1=t1, gate_time=gate_time)
    expected = 1 - np.exp(-gate_time / t1)
    assert noise.error_rate == pytest.approx(expected, rel=1e-12)
    # The physically correct value (~1.9998000133e-4); the channel uses this γ.
    assert noise.error_rate == pytest.approx(1.9998000133325533e-4, rel=1e-9)
    assert noise.get_kraus_operators()[1][0, 1].real == pytest.approx(np.sqrt(expected))


def test_amplitude_damping_thermal_population_branch() -> None:
    """Non-zero temperature exercises the Boltzmann thermal-population branch."""
    noise = AmplitudeDampingNoise(error_rate=0.05, temperature=0.1)
    assert 0.0 <= noise._thermal_population < 0.5


def test_amplitude_damping_gate_time_exceeds_t1_warns() -> None:
    """gate_time > T1 hits the warning branch but still constructs."""
    noise = AmplitudeDampingNoise(t1=10e-9, gate_time=20e-9)
    assert 0.0 <= noise.error_rate <= 1.0


def test_amplitude_damping_validation() -> None:
    with pytest.raises(ValueError):
        AmplitudeDampingNoise(error_rate=1.5)
    with pytest.raises(ValueError):
        AmplitudeDampingNoise(t1=-1.0)
    with pytest.raises(ValueError):
        AmplitudeDampingNoise(gate_time=0.0)
    with pytest.raises(ValueError):
        AmplitudeDampingNoise(temperature=-1.0)


# --------------------------------------------------------------------------- #
# Phase damping channel (standard 2-operator form)
# --------------------------------------------------------------------------- #


def test_phase_damping_exact_operators() -> None:
    """λ=0.2 → K0=diag(1,√0.8), K1=diag(0,√0.2)."""
    kraus = PhaseDampingNoise(error_rate=0.2).get_kraus_operators()
    assert np.allclose(kraus[0], np.array([[1, 0], [0, np.sqrt(0.8)]], dtype=complex), atol=ATOL)
    assert np.allclose(kraus[1], np.array([[0, 0], [0, np.sqrt(0.2)]], dtype=complex), atol=ATOL)


def test_phase_damping_completeness() -> None:
    kraus = PhaseDampingNoise(error_rate=0.2).get_kraus_operators()
    assert np.allclose(completeness_sum(kraus), I2, atol=ATOL)


def test_phase_damping_matches_qiskit_choi() -> None:
    kraus = PhaseDampingNoise(error_rate=0.2).get_kraus_operators()
    assert choi_equal(kraus, phase_damping_error(0.2))


def test_phase_damping_coherence_decay() -> None:
    """|+><+| → off-diagonal 0.5·√(1-λ) = 0.5·√0.8 = 0.4472135954999579."""
    kraus = PhaseDampingNoise(error_rate=0.2).get_kraus_operators()
    plus = 0.5 * np.array([[1, 1], [1, 1]], dtype=complex)
    out = apply_channel(kraus, plus)
    assert out[0, 1].real == pytest.approx(0.5 * np.sqrt(0.8))
    assert out[0, 1].real == pytest.approx(0.4472135954999579)
    # Populations preserved exactly.
    assert out[0, 0].real == pytest.approx(0.5)
    assert out[1, 1].real == pytest.approx(0.5)


def test_phase_damping_physics_t2_star_path() -> None:
    """λ from T2*: λ = 1 - exp(-gate/T2*)."""
    t2s, gate_time = 50e-6, 20e-9
    noise = PhaseDampingNoise(t2_star=t2s, gate_time=gate_time)
    assert noise.error_rate == pytest.approx(1 - np.exp(-gate_time / t2s), rel=1e-12)


def test_phase_damping_thermal_branch_and_gate_warning() -> None:
    """Temperature>0 thermal-dephasing branch and gate_time>T2* warning."""
    noise = PhaseDampingNoise(t2_star=10e-9, gate_time=20e-9, temperature=0.1)
    assert noise._thermal_dephasing > 0.0


def test_phase_damping_validation() -> None:
    with pytest.raises(ValueError):
        PhaseDampingNoise(error_rate=1.5)
    with pytest.raises(ValueError):
        PhaseDampingNoise(t2_star=-1.0)
    with pytest.raises(ValueError):
        PhaseDampingNoise(gate_time=0.0)
    with pytest.raises(ValueError):
        PhaseDampingNoise(temperature=-1.0)


# --------------------------------------------------------------------------- #
# Thermal relaxation channel
# --------------------------------------------------------------------------- #


def test_thermal_t2_exceeds_2t1_raises() -> None:
    """T2 > 2·T1 violates physics → ValueError."""
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(t1=10e-6, t2=30e-6)


def test_thermal_t2_equals_2t1_allowed() -> None:
    """T2 == 2·T1 is the boundary and is allowed."""
    noise = ThermalRelaxationNoise(t1=10e-6, t2=20e-6)
    assert noise.t2 == pytest.approx(2 * noise.t1)


def test_thermal_excited_population_zero_temperature() -> None:
    """Boltzmann excited population at T=0 → 0.0."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, temperature=0.0)
    assert noise._thermal_population == 0.0


def test_thermal_effective_t2() -> None:
    """Effective T2 = 1/(1/T2 + 1/(2T1)); t1=100e-6,t2=80e-6 → 5.714285714e-5."""
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6)
    assert noise._effective_t2 == pytest.approx(5.714285714285714e-5, rel=1e-9)


def test_thermal_kraus_completeness() -> None:
    """Approximate T1 Kraus operators still form a valid CPTP map."""
    kraus = ThermalRelaxationNoise(t1=100e-6, t2=80e-6).get_kraus_operators()
    assert np.allclose(completeness_sum(kraus), I2, atol=ATOL)


def test_thermal_population_nonzero_temperature() -> None:
    noise = ThermalRelaxationNoise(t1=100e-6, t2=80e-6, temperature=0.5)
    assert 0.0 < noise._thermal_population < 0.5


def test_thermal_validation() -> None:
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(error_rate=1.5, t1=100e-6, t2=80e-6)
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(t1=-1.0, t2=80e-6)
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(t1=100e-6, t2=-1.0)
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(t1=100e-6, t2=80e-6, gate_time=0.0)
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(t1=100e-6, t2=80e-6, temperature=-1.0)
    with pytest.raises(ValueError):
        ThermalRelaxationNoise(t1=100e-6, t2=80e-6, qubit_frequency=0.0)


def test_thermal_gate_time_warnings() -> None:
    """gate_time exceeding T1 and T2 hits both warning branches."""
    noise = ThermalRelaxationNoise(t1=10e-9, t2=15e-9, gate_time=20e-9)
    assert noise._combined_error_rate <= 1.0


# --------------------------------------------------------------------------- #
# Correlated depolarizing channel (probability algebra)
# --------------------------------------------------------------------------- #


def _channel_error_probabilities(channel) -> tuple[float, list[float]]:
    """Return (identity_prob, sorted non-identity probs) for a QuantumError."""
    probs = sorted(channel.probabilities, reverse=True)
    identity_prob = probs[0]  # II dominates (1 - p)
    return identity_prob, probs[1:]


@pytest.mark.parametrize("cs", [-0.5, 0.0, 0.5])
def test_correlated_depolarizing_probability_conservation(cs: float) -> None:
    """Total two-qubit error probability == p for all correlation strengths."""
    p = 0.15
    noise = CorrelatedDepolarizingNoise(
        error_rate=p, num_qubits=3, correlation_strength=cs, topology="GHZ"
    )
    channel = noise._build_correlated_2q_channel()
    identity_prob, others = _channel_error_probabilities(channel)
    assert (1.0 - identity_prob) == pytest.approx(p, abs=1e-12)
    assert sum(others) == pytest.approx(p, abs=1e-12)


def test_correlated_depolarizing_cs_zero_reduces_to_standard() -> None:
    """cs=0 → each of the 15 two-qubit Paulis has probability p/15."""
    p = 0.15
    noise = CorrelatedDepolarizingNoise(
        error_rate=p, num_qubits=3, correlation_strength=0.0, topology="GHZ"
    )
    channel = noise._build_correlated_2q_channel()
    _, others = _channel_error_probabilities(channel)
    assert len(others) == 15
    for prob in others:
        assert prob == pytest.approx(p / 15.0, abs=1e-12)


def test_correlated_depolarizing_positive_cs_boosts_correlated() -> None:
    """cs>0: correlated Paulis (XX,YY,ZZ) exceed uncorrelated ones."""
    p = 0.15
    noise = CorrelatedDepolarizingNoise(
        error_rate=p, num_qubits=3, correlation_strength=0.5, topology="GHZ"
    )
    channel = noise._build_correlated_2q_channel()
    _, others = _channel_error_probabilities(channel)
    corr_prob = (1 - 0.5) * p / 15.0 + 0.5 * p / 3.0
    uncorr_prob = (1 - 0.5) * p / 15.0
    # 3 correlated terms equal to corr_prob, 12 uncorrelated equal to uncorr_prob.
    assert sum(1 for x in others if x == pytest.approx(corr_prob, abs=1e-12)) == 3
    assert sum(1 for x in others if x == pytest.approx(uncorr_prob, abs=1e-12)) == 12


def test_correlated_depolarizing_correlation_strength_bounds() -> None:
    with pytest.raises(ValueError):
        CorrelatedDepolarizingNoise(num_qubits=3, correlation_strength=1.5)
    with pytest.raises(ValueError):
        CorrelatedDepolarizingNoise(num_qubits=3, correlation_strength=-1.5)


def test_correlated_depolarizing_unknown_topology_raises() -> None:
    with pytest.raises(ValueError):
        CorrelatedDepolarizingNoise(num_qubits=3, topology="NONSENSE")


def test_correlated_depolarizing_custom_topology() -> None:
    """Custom adjacency matrix selects connected pairs explicitly."""
    adj = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
    noise = CorrelatedDepolarizingNoise(num_qubits=3, custom_topology=adj)
    assert noise.connected_pairs == [(0, 1)]


def test_correlated_depolarizing_kraus_empty() -> None:
    """get_kraus_operators() is delegated to Qiskit and returns []."""
    noise = CorrelatedDepolarizingNoise(num_qubits=3)
    assert noise.get_kraus_operators() == []
    assert "mechanism" in noise.get_physics_description()


def test_correlated_depolarizing_apply_paths() -> None:
    """Both cs=0 (standard) and cs!=0 (per-pair) apply branches build models."""
    gates = ["h", "x", "cx"]
    nm0 = NoiseModel()
    CorrelatedDepolarizingNoise(error_rate=0.05, num_qubits=3, correlation_strength=0.0).apply(
        nm0, gates
    )
    assert nm0.noise_instructions

    nm1 = NoiseModel()
    CorrelatedDepolarizingNoise(error_rate=0.05, num_qubits=3, correlation_strength=0.5).apply(
        nm1, gates
    )
    assert nm1.noise_instructions


# --------------------------------------------------------------------------- #
# Base noise validation branches
# --------------------------------------------------------------------------- #


def test_base_validate_error_rate_value_error() -> None:
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    with pytest.raises(ValueError):
        noise._validate_error_rate(1.5)


def test_base_validate_error_rate_type_error() -> None:
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    with pytest.raises(TypeError):
        noise._validate_error_rate("x")


def test_base_validate_qubit_count() -> None:
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    with pytest.raises(ValueError):
        noise._validate_qubit_count(0)
    with pytest.raises(TypeError):
        noise._validate_qubit_count("two")


def test_base_large_qubit_count_warns() -> None:
    """num_qubits > 10 takes the warning branch (still valid)."""
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    noise._validate_qubit_count(11)  # should not raise


def test_base_properties_smoke() -> None:
    """Exercise shared informational methods across every channel."""
    for factory in KRAUS_CHANNEL_FACTORIES.values():
        noise = factory()
        props = noise.get_basic_properties()
        assert "noise_type" in props and "kraus_rank" in props
        assert isinstance(str(noise), str)
        assert isinstance(noise.get_physics_description(), dict)


def test_base_decoherence_timescale_branches() -> None:
    """Cover all branches of _estimate_decoherence_timescale."""
    # t1 in physics params
    assert "T1" in AmplitudeDampingNoise(t1=100e-6)._estimate_decoherence_timescale()
    # (The 't2' branch is unreachable in practice: the only class storing a "t2"
    #  physics param, thermal_relaxation, also stores "t1", which is checked first.)
    # rate-estimated (no t1/t2, rate > 0)
    bf = BitFlipNoise(error_rate=0.1)
    assert "Rate-estimated" in bf._estimate_decoherence_timescale()
    # zero error rate
    bf0 = BitFlipNoise(error_rate=0.0)
    assert "No decoherence" in bf0._estimate_decoherence_timescale()


def test_base_validate_for_hardware_branches() -> None:
    """Cover every warning branch of validate_for_hardware."""
    # AD with explicit t1 puts "t1" in physics_params (covers the min_t1 branch).
    noise = AmplitudeDampingNoise(error_rate=0.2, num_qubits=3, t1=5e-6)
    constraints = {
        "min_t1": 50e-6,
        "supported_gates": {"h"},  # missing required gates
        "max_qubits": 2,
    }
    warnings = noise.validate_for_hardware(constraints)
    assert len(warnings) >= 3  # T1-below, unsupported-gates, too-many-qubits
    # Fully-compatible case returns no warnings.
    assert noise.validate_for_hardware({"max_error_rate": 1.0}) == []
    # error_rate-exceeds branch (use a channel that keeps its phenomenological rate).
    depol = DepolarizingNoise(error_rate=0.2, num_qubits=1)
    assert any("exceeds" in w for w in depol.validate_for_hardware({"max_error_rate": 0.1}))


def test_base_channel_capacity_branches() -> None:
    """_estimate_channel_capacity perfect / degraded / moderate."""
    assert DepolarizingNoise(error_rate=0.0)._estimate_channel_capacity() == 1.0
    assert DepolarizingNoise(error_rate=0.6)._estimate_channel_capacity() == 0.0
    assert 0.0 < DepolarizingNoise(error_rate=0.1)._estimate_channel_capacity() < 1.0


def test_base_log_noise_creation_extra_info() -> None:
    noise = DepolarizingNoise(error_rate=0.1, num_qubits=1)
    noise.log_noise_creation("DEPOLARIZING", {"extra": "value"})


# --------------------------------------------------------------------------- #
# Noise factory
# --------------------------------------------------------------------------- #


def test_factory_create_instance_error_rate() -> None:
    noise = create_noise_instance("DEPOLARIZING", 1, 0.1)
    assert noise.error_rate == 0.1


def test_factory_create_instance_unknown_raises() -> None:
    with pytest.raises(ValueError):
        create_noise_instance("BOGUS", 1, 0.1)


def test_factory_create_instance_with_custom_params() -> None:
    noise = create_noise_instance(
        "THERMAL_RELAXATION", 1, custom_params={"t1": 100e-6, "t2": 80e-6}
    )
    assert isinstance(noise, ThermalRelaxationNoise)


def test_factory_available_types() -> None:
    """get_available_noise_types() == the 7 registered keys."""
    types = get_available_noise_types()
    assert set(types) == set(NOISE_CLASSES)
    assert len(types) == 7
    assert "CORRELATED_DEPOLARIZING" in types


@pytest.mark.parametrize(
    "noise_type",
    [
        "DEPOLARIZING",
        "AMPLITUDE_DAMPING",
        "PHASE_DAMPING",
        "BIT_FLIP",
        "PHASE_FLIP",
        "THERMAL_RELAXATION",
        "CORRELATED_DEPOLARIZING",
    ],
)
def test_factory_create_noise_model_nonempty(noise_type: str) -> None:
    """create_noise_model returns a NoiseModel with noise instructions."""
    nm = create_noise_model(noise_type, num_qubits=2, error_rate=0.05)
    assert isinstance(nm, NoiseModel)
    assert nm.noise_instructions


def test_factory_create_noise_model_single_qubit() -> None:
    """Single-qubit system path in _get_appropriate_gates."""
    nm = create_noise_model("DEPOLARIZING", num_qubits=1, error_rate=0.05)
    assert nm.noise_instructions


def test_factory_create_noise_model_unknown_raises() -> None:
    with pytest.raises(ValueError):
        create_noise_model("BOGUS", num_qubits=2, error_rate=0.05)


def test_factory_create_noise_model_bad_params_raises() -> None:
    """Physics violation inside construction is re-raised as ValueError."""
    with pytest.raises(ValueError):
        create_noise_model("DEPOLARIZING", num_qubits=1, error_rate=0.9)


def test_factory_create_noise_model_with_readout() -> None:
    nm = create_noise_model("DEPOLARIZING", num_qubits=2, error_rate=0.05, readout_error_rate=0.1)
    assert nm.noise_instructions


def test_factory_apply_readout_errors_confusion_matrix() -> None:
    """_apply_readout_errors registers ReadoutError [[0.9,0.1],[0.1,0.9]]."""
    nm = NoiseModel()
    _apply_readout_errors(nm, num_qubits=2, readout_error_rate=0.1)
    # Qiskit stores readout errors; verify the probability matrix round-trips.
    ro = nm._local_readout_errors[(0,)]
    assert np.allclose(np.asarray(ro.probabilities), [[0.9, 0.1], [0.1, 0.9]], atol=1e-12)


def test_factory_validate_noise_request() -> None:
    assert validate_noise_request("DEPOLARIZING", 1, 0.05) == []
    assert validate_noise_request("BOGUS", 1) == ["Unknown noise type: BOGUS"]
    # qubit count too small / too large
    assert validate_noise_request("DEPOLARIZING", 0) != []
    assert validate_noise_request("DEPOLARIZING", 16) != []
    # error rate out of range and high
    assert validate_noise_request("DEPOLARIZING", 1, 1.5) != []
    assert validate_noise_request("DEPOLARIZING", 1, 0.6) != []
    # depolarizing physical bound
    assert validate_noise_request("DEPOLARIZING", 1, 0.8) != []
    # T2 > 2T1 physics violation
    assert (
        validate_noise_request("THERMAL_RELAXATION", 1, custom_params={"t1": 10e-6, "t2": 30e-6})
        != []
    )
    # negative temperature
    assert (
        validate_noise_request("THERMAL_RELAXATION", 1, custom_params={"temperature": -1.0}) != []
    )


def test_factory_get_noise_info() -> None:
    info = get_noise_info()
    assert "DEPOLARIZING" in info
    assert "description" in info["DEPOLARIZING"]
    assert len(info) == 6  # informational catalog excludes correlated variant


def test_factory_hardware_no_backend() -> None:
    """No backend → simulation path, no hardware validation."""
    nm = create_noise_model_for_hardware("DEPOLARIZING", 2, error_rate=0.05)
    assert isinstance(nm, NoiseModel)


class _FakeConfig:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _FakeBackend:
    def __init__(self, **kw):
        self._cfg = _FakeConfig(**kw)

    def configuration(self):
        return self._cfg


def test_factory_hardware_with_compatible_backend() -> None:
    """Backend present and compatible → validation passes, model built."""
    backend = _FakeBackend(
        n_qubits=5,
        basis_gates=["id", "u1", "u2", "u3", "cx"],
        backend_name="fake",
    )
    nm = create_noise_model_for_hardware("DEPOLARIZING", 2, backend=backend, error_rate=0.05)
    assert isinstance(nm, NoiseModel)


def test_factory_hardware_with_incompatible_backend_raises() -> None:
    """Error rate exceeding the backend limit triggers a critical raise."""
    backend = _FakeBackend(
        n_qubits=5,
        basis_gates=["id", "u1", "u2", "u3", "cx"],
        backend_name="fake",
        max_error_rate=0.001,
    )
    with pytest.raises(ValueError):
        create_noise_model_for_hardware("DEPOLARIZING", 2, backend=backend, error_rate=0.5)


# --------------------------------------------------------------------------- #
# apply() coverage for single-channel models
# --------------------------------------------------------------------------- #


def test_depolarizing_apply_unknown_and_override_gates() -> None:
    """Unknown gate skipped; qubits_for_error override creates n-qubit channel."""
    noise = DepolarizingNoise(error_rate=0.05, num_qubits=3)
    nm = NoiseModel()
    # Unknown gate with no override -> skipped (debug branch).
    noise.apply(nm, ["mystery"], qubits_for_error=None)
    # Unknown gate with override -> uses qubits_for_error.
    noise.apply(nm, ["mystery"], qubits_for_error=2)
    assert nm.noise_instructions


def test_single_qubit_channels_apply_warn_on_multiqubit_override() -> None:
    """qubits_for_error != 1 hits the single-qubit warning branch."""
    nm = NoiseModel()
    BitFlipNoise(error_rate=0.05).apply(nm, ["h"], qubits_for_error=2)
    PhaseFlipNoise(error_rate=0.05).apply(nm, ["h"], qubits_for_error=2)
    assert nm.noise_instructions


def test_phase_damping_apply_no_valid_gates() -> None:
    """Only multi-qubit gates -> early-return warning branch, nothing added."""
    nm = NoiseModel()
    PhaseDampingNoise(error_rate=0.05).apply(nm, ["cx"], qubits_for_error=2)
    assert not nm.noise_instructions


def test_phase_damping_apply_zero_rate() -> None:
    """error_rate=0 -> channel not applied (effective_rate > 0 is False)."""
    nm = NoiseModel()
    PhaseDampingNoise(error_rate=0.0).apply(nm, ["h", "x"])
    assert not nm.noise_instructions


def test_amplitude_damping_apply_one_and_two_qubit() -> None:
    """AD applies 1q channel to 1q gates and AD⊗AD to 2q gates."""
    nm = NoiseModel()
    AmplitudeDampingNoise(error_rate=0.05).apply(nm, ["h", "cx", "unknown3q"])
    assert nm.noise_instructions


def test_thermal_apply_virtual_and_physical_gates() -> None:
    """Thermal apply covers virtual (zero-duration) and physical gate branches."""
    nm = NoiseModel()
    ThermalRelaxationNoise(t1=100e-6, t2=80e-6).apply(nm, ["rz", "z", "h", "x", "cx", "swap"])
    assert nm.noise_instructions


# --------------------------------------------------------------------------- #
# Informational / educational methods (theoretical properties)
# --------------------------------------------------------------------------- #

ALL_FACTORIES = [
    lambda: DepolarizingNoise(error_rate=0.1, num_qubits=1),
    lambda: BitFlipNoise(error_rate=0.1),
    lambda: PhaseFlipNoise(error_rate=0.1),
    lambda: AmplitudeDampingNoise(error_rate=0.1),
    lambda: PhaseDampingNoise(error_rate=0.2),
    lambda: ThermalRelaxationNoise(t1=100e-6, t2=80e-6),
]


def test_theoretical_properties_all_channels() -> None:
    for factory in ALL_FACTORIES:
        props = factory().get_theoretical_properties()
        assert isinstance(props, dict)
        assert "decoherence_type" in props


def test_correlated_uses_base_info_methods() -> None:
    """CorrelatedDepolarizing does not override base info methods → cover base."""
    noise = CorrelatedDepolarizingNoise(error_rate=0.05, num_qubits=3)
    props = noise.get_basic_properties()  # base; kraus_rank == 0 (delegated)
    assert props["kraus_rank"] == 0
    assert isinstance(str(noise), str)  # base __str__


def test_str_with_physics_parameters() -> None:
    """__str__ physics-parameter branches for each channel."""
    assert "T1" in str(AmplitudeDampingNoise(t1=100e-6))
    assert "phenomenological" in str(AmplitudeDampingNoise(error_rate=0.1))
    assert "pulse_error" in str(BitFlipNoise(pulse_amplitude_error=0.02))
    assert "phenomenological" in str(BitFlipNoise(error_rate=0.1))
    assert "B_noise" in str(PhaseFlipNoise(magnetic_field_noise=1e-6, charge_noise=5e-4))
    assert "phenomenological" in str(PhaseFlipNoise(error_rate=0.1))
    assert "T2*" in str(PhaseDampingNoise(t2_star=50e-6))
    assert "phenomenological" in str(PhaseDampingNoise(error_rate=0.1))
    assert "T1" in str(ThermalRelaxationNoise(t1=100e-6, t2=80e-6))


def test_channel_capacity_edges() -> None:
    """Cover perfect / deterministic / maximally-noisy capacity branches."""
    # Bit flip binary-symmetric-channel capacity.
    assert BitFlipNoise(error_rate=0.0)._calculate_channel_capacity() == 1.0
    assert BitFlipNoise(error_rate=1.0)._calculate_channel_capacity() == 0.0
    assert BitFlipNoise(error_rate=0.5)._calculate_channel_capacity() == 0.0
    assert 0.0 <= BitFlipNoise(error_rate=0.1)._calculate_channel_capacity() <= 1.0
    # Phase flip.
    assert PhaseFlipNoise(error_rate=0.0)._calculate_channel_capacity() == 1.0
    assert PhaseFlipNoise(error_rate=1.0)._calculate_channel_capacity() == 0.0
    assert PhaseFlipNoise(error_rate=0.5)._calculate_channel_capacity() == 0.0
    assert 0.0 <= PhaseFlipNoise(error_rate=0.1)._calculate_channel_capacity() <= 1.0
    # Amplitude damping.
    assert AmplitudeDampingNoise(error_rate=0.0)._calculate_channel_capacity() == 1.0
    assert AmplitudeDampingNoise(error_rate=1.0)._calculate_channel_capacity() == 0.0
    assert 0.0 <= AmplitudeDampingNoise(error_rate=0.5)._calculate_channel_capacity() <= 1.0
    # Phase damping.
    assert PhaseDampingNoise(error_rate=0.0)._calculate_channel_capacity() == 1.0
    assert PhaseDampingNoise(error_rate=1.0)._calculate_channel_capacity() == 0.0
    assert 0.0 <= PhaseDampingNoise(error_rate=0.5)._calculate_channel_capacity() <= 1.0


def test_zero_temperature_thermal_branches() -> None:
    """temperature=0 returns 0.0 for AD thermal pop and phase-damping thermal dephasing."""
    assert AmplitudeDampingNoise(error_rate=0.1, temperature=0.0)._thermal_population == 0.0
    assert PhaseDampingNoise(error_rate=0.1, temperature=0.0)._thermal_dephasing == 0.0


def test_factory_three_qubit_gate_selection_and_custom_params() -> None:
    """num_qubits>2 gate-selection branch and custom_params merge in create_noise_model."""
    nm = create_noise_model(
        "THERMAL_RELAXATION", num_qubits=3, custom_params={"t1": 100e-6, "t2": 80e-6}
    )
    assert nm.noise_instructions


def test_thermal_apply_multiqubit_override_warns() -> None:
    """qubits_for_error != 1 hits the thermal single-qubit warning branch."""
    nm = NoiseModel()
    ThermalRelaxationNoise(t1=100e-6, t2=80e-6).apply(nm, ["h"], qubits_for_error=2)
    assert nm.noise_instructions


def _raise(*_a, **_k):
    raise RuntimeError("forced failure")


def test_depolarizing_apply_error_branches(monkeypatch) -> None:
    """Channel-creation failure and per-gate failure branches log and continue."""
    import qforge.core.noise_models.depolarizing as depol_mod

    noise = DepolarizingNoise(error_rate=0.05, num_qubits=1)
    # Channel creation failure -> warning + continue (no exception escapes).
    monkeypatch.setattr(depol_mod, "depolarizing_error", _raise)
    noise.apply(NoiseModel(), ["h"])

    # Per-gate add failure -> failed_gates branch + warning log.
    monkeypatch.undo()
    nm = NoiseModel()
    monkeypatch.setattr(nm, "add_all_qubit_quantum_error", _raise)
    noise.apply(nm, ["h"])


def test_amplitude_damping_apply_error_branches(monkeypatch) -> None:
    """AD channel-creation failure raises ValueError; add failure is captured."""
    import qforge.core.noise_models.amplitude_damping as ad_mod

    noise = AmplitudeDampingNoise(error_rate=0.05)
    monkeypatch.setattr(ad_mod, "amplitude_damping_error", _raise)
    with pytest.raises(ValueError):
        noise.apply(NoiseModel(), ["h"])

    monkeypatch.undo()
    nm = NoiseModel()
    monkeypatch.setattr(nm, "add_all_qubit_quantum_error", _raise)
    noise.apply(nm, ["h", "cx"])  # populates failed_gates, logs warning


def test_phase_damping_apply_error_branch(monkeypatch) -> None:
    """Per-gate add failure is captured in failed_gates and logged."""
    noise = PhaseDampingNoise(error_rate=0.05)
    nm = NoiseModel()
    monkeypatch.setattr(nm, "add_all_qubit_quantum_error", _raise)
    noise.apply(nm, ["h", "x"])


def test_correlated_apply_error_branches(monkeypatch) -> None:
    """Depolarizing-error failures in correlated apply are swallowed gracefully."""
    import qiskit_aer.noise as aer_noise

    # correlated apply() imports depolarizing_error locally from qiskit_aer.noise.
    monkeypatch.setattr(aer_noise, "depolarizing_error", _raise)
    nm = NoiseModel()
    # Both the 1q (except pass) and 2q (except continue) creation paths fail.
    CorrelatedDepolarizingNoise(error_rate=0.05, num_qubits=3, correlation_strength=0.5).apply(
        nm, ["h", "cx"]
    )


def test_depolarizing_entropy_increase_branches() -> None:
    """_calculate_entropy_increase: zero / maximal / partial via theoretical props."""
    assert DepolarizingNoise(error_rate=0.0, num_qubits=1)._calculate_entropy_increase() == 0.0
    # Maximal rate for 1 qubit is 0.75 → entropy increase == num_qubits.
    assert DepolarizingNoise(error_rate=0.75, num_qubits=1)._calculate_entropy_increase() == 1.0
    assert DepolarizingNoise(error_rate=0.1, num_qubits=1)._calculate_entropy_increase() > 0.0
