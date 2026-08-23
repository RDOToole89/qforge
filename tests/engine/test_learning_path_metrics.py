"""Learning-path experiments pick metrics that match the question they ask."""

from __future__ import annotations

from qforge.experiments import get_experiment

# name -> default metrics. Teleportation / superdense stay None: the lesson is
# protocol success, not distribution structure.
_EXPECTED: dict[str, list[str] | None] = {
    "01_superposition": ["asymmetry_index"],
    "02_measurement": ["asymmetry_index"],
    "03_single_gates": ["asymmetry_index"],
    "04_two_qubits": ["structure_score", "total_correlation"],
    "05_bell_states": ["structure_score", "total_correlation"],
    "06_ghz_states": ["structure_score", "total_correlation", "concentration_index"],
    "07_w_states": ["structure_score", "total_correlation", "concentration_index"],
    "08_cluster_states": ["structure_score", "concentration_index"],
    "09_noise_intro": ["asymmetry_index"],
    "10_noise_types": ["structure_score", "concentration_index"],
    "11_noise_and_entanglement": [
        "structure_score",
        "total_correlation",
        "concentration_index",
        "entanglement_error_correlation",
    ],
    "adv_01_quantum_randomness": ["structure_score", "total_correlation"],
    "adv_02_deutsch_jozsa": ["concentration_index", "asymmetry_index"],
    "adv_03_grover_search": ["concentration_index", "asymmetry_index"],
    "adv_04_teleportation": None,
    "adv_05_superdense_coding": None,
    "adv_06_qft": ["asymmetry_index", "concentration_index"],
    "adv_07_error_correction": ["concentration_index", "asymmetry_index"],
    "adv_08_design_your_own": ["structure_score"],
}


def test_learning_path_default_metrics() -> None:
    for name, expected in _EXPECTED.items():
        cfg = get_experiment(name).default_config()
        assert cfg.metrics == expected, name


def test_bell_has_a_metrics_hint() -> None:
    exp = get_experiment("05_bell_states")
    assert exp.metrics_hint
    assert "Structure Score" in exp.metrics_hint
