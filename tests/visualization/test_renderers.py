import tempfile
from pathlib import Path

import numpy as np
from qiskit.quantum_info import DensityMatrix

from src.visualization.plots.histogram import render_histogram
from src.visualization.plots.density_matrix import render_density_matrix


def test_render_histogram_saves_png(tmp_path: Path):
    counts = {"000": 50, "111": 50}
    out = tmp_path / "hist.png"
    saved = render_histogram(counts, save_path=str(out))
    assert saved == str(out)
    assert out.exists() and out.stat().st_size > 0


def test_render_density_matrix_saves_png(tmp_path: Path):
    dm = DensityMatrix(np.eye(4) / 4)
    out = tmp_path / "dm.png"
    saved = render_density_matrix(dm, save_path=str(out))
    assert saved == str(out)
    assert out.exists() and out.stat().st_size > 0
