from src.core.experiment_runner import run_experiment


def test_rng_seed_repro_qasm():
    # Same seed should yield identical counts
    qc1, res1 = run_experiment(
        num_qubits=3,
        state_type="GHZ",
        noise_type="DEPOLARIZING",
        noise_enabled=True,
        shots=256,
        sim_mode="qasm",
        error_rate=0.05,
        rng_seed=123,
    )
    qc2, res2 = run_experiment(
        num_qubits=3,
        state_type="GHZ",
        noise_type="DEPOLARIZING",
        noise_enabled=True,
        shots=256,
        sim_mode="qasm",
        error_rate=0.05,
        rng_seed=123,
    )
    assert isinstance(res1, dict) and isinstance(res2, dict)
    assert res1 == res2
