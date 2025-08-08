import os
from src.visualization.save_manager import get_save_manager, get_organized_save_path


def test_default_base_dir_is_results_visualizations(tmp_path, monkeypatch):
    # Ensure we work in a temp CWD
    monkeypatch.chdir(tmp_path)
    sm = get_save_manager()
    assert str(sm.base_dir).endswith("results/visualizations")


def test_generate_histogram_path_in_correct_subdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = {
        'state_type': 'GHZ',
        'noise_type': 'DEPOLARIZING',
        'num_qubits': 3,
        'noise_enabled': True,
        'error_rate': 0.05,
    }
    path = get_organized_save_path('histogram', experiment_config=config)
    assert os.path.normpath(path).startswith(os.path.normpath("results/visualizations/histograms"))

