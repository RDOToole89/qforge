from src.engine.api import run

def test_run_smoke_ghz_qasm_baseline():
    cfg = {
        "num_qubits": 3,
        "state_type": "GHZ",
        "sim_mode": "qasm",
        "shots": 128,
        "noise_enabled": True,
        "noise_type": "depolarizing",
        "error_rate": 0.05,
    }
    res = run(cfg)
    assert res.metrics and isinstance(res.config_hash, str)
