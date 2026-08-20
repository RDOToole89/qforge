"""
Tests for Phase 2 visualization expansion.

Covers:
- DensityMatrixRenderer
- CorrelationRenderer
- CircuitDiagramRenderer
- Multi-format export (PNG/PDF/SVG)
- visualization_type="all" and "none"
- Config validation for new fields
- save_figure utility
"""

import os
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError
from qiskit import QuantumCircuit

from qforge.engine.api import run
from qforge.engine.models import ExperimentConfig
from qforge.engine.visualization import (
    CircuitDiagramRenderer,
    CorrelationRenderer,
    DensityMatrixRenderer,
    HistogramRenderer,
    create_default_service,
    save_figure,
)


def _has_pylatexenc() -> bool:
    try:
        import pylatexenc  # noqa: F401

        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestConfigValidation:
    """Verify new visualization_type and export_formats fields."""

    @pytest.mark.parametrize(
        "vt",
        ["histogram", "density_matrix", "correlation", "circuit", "all", "none"],
    )
    def test_visualization_type_accepted(self, vt: str):
        cfg = ExperimentConfig(num_qubits=2, state_type="GHZ", visualization_type=vt)
        assert cfg.visualization_type == vt

    def test_invalid_visualization_type_rejected(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(num_qubits=2, state_type="GHZ", visualization_type="invalid")

    def test_export_formats_default(self):
        cfg = ExperimentConfig(num_qubits=2, state_type="GHZ")
        assert cfg.export_formats == ["png"]

    def test_export_formats_custom(self):
        cfg = ExperimentConfig(num_qubits=2, state_type="GHZ", export_formats=["png", "pdf", "svg"])
        assert cfg.export_formats == ["png", "pdf", "svg"]

    def test_invalid_export_format_rejected(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(num_qubits=2, state_type="GHZ", export_formats=["png", "bmp"])


# ---------------------------------------------------------------------------
# save_figure utility
# ---------------------------------------------------------------------------


class TestSaveFigure:
    """Test the multi-format save_figure helper."""

    def test_single_format(self, tmp_path: Path):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        paths = save_figure(fig, tmp_path / "test_fig", ["png"])
        plt.close(fig)

        assert len(paths) == 1
        assert paths[0].endswith(".png")
        assert os.path.isfile(paths[0])

    def test_multi_format(self, tmp_path: Path):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        paths = save_figure(fig, tmp_path / "test_fig", ["png", "pdf", "svg"])
        plt.close(fig)

        assert len(paths) == 3
        exts = {Path(p).suffix for p in paths}
        assert exts == {".png", ".pdf", ".svg"}
        for p in paths:
            assert os.path.isfile(p)

    def test_default_format(self, tmp_path: Path):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        paths = save_figure(fig, tmp_path / "test_fig")
        plt.close(fig)

        assert len(paths) == 1
        assert paths[0].endswith(".png")


# ---------------------------------------------------------------------------
# Service registration
# ---------------------------------------------------------------------------


class TestServiceRegistration:
    """Verify all renderers are registered in the default service."""

    def test_default_service_has_all_renderers(self):
        service = create_default_service()
        names = service.list_renderers()
        assert "HistogramRenderer" in names
        assert "DensityMatrixRenderer" in names
        assert "CorrelationRenderer" in names
        assert "CircuitDiagramRenderer" in names


# ---------------------------------------------------------------------------
# DensityMatrixRenderer
# ---------------------------------------------------------------------------


class TestDensityMatrixRenderer:
    """Test density matrix heatmap rendering."""

    def test_can_render_with_density_matrix(self):
        renderer = DensityMatrixRenderer()
        # density_matrix is list of rows, each row is list of [real, imag]
        # For a 2x2 matrix: [[row0_col0, row0_col1], [row1_col0, row1_col1]]
        dm_2x2 = [
            [[0.5, 0.0], [0.5, 0.0]],
            [[0.5, 0.0], [0.5, 0.0]],
        ]
        data2 = {"analysis": {"measurement_results": {"density_matrix": dm_2x2}}}
        assert renderer.can_render("density_matrix", data2) is True

    def test_cannot_render_without_density_matrix(self):
        renderer = DensityMatrixRenderer()
        data = {"analysis": {"measurement_results": {"raw_counts": {"00": 500}}}}
        assert renderer.can_render("density_matrix", data) is False

    def test_cannot_render_wrong_type(self):
        renderer = DensityMatrixRenderer()
        dm_2x2 = [[[0.5, 0.0], [0.5, 0.0]], [[0.5, 0.0], [0.5, 0.0]]]
        data = {"analysis": {"measurement_results": {"density_matrix": dm_2x2}}}
        assert renderer.can_render("histogram", data) is False

    def test_render_produces_artifact(self, tmp_path: Path):
        renderer = DensityMatrixRenderer()
        # 2x2 Bell-like density matrix
        dm_2x2 = [
            [[0.5, 0.0], [0.0, 0.0]],
            [[0.0, 0.0], [0.5, 0.0]],
        ]
        data = {
            "analysis": {
                "measurement_results": {
                    "density_matrix": dm_2x2,
                    "fidelity": 0.95,
                },
                "experiment_parameters": {
                    "state_type": "GHZ",
                    "num_qubits": 2,
                },
            },
            "export_formats": ["png"],
        }
        artifact = renderer.render(data, str(tmp_path / "dm_test.png"))
        assert artifact.kind == "density_matrix"
        assert os.path.isfile(artifact.path)
        assert artifact.metadata["renderer"] == "DensityMatrixRenderer"
        assert artifact.metadata["dimension"] == 2

    def test_integration_density_matrix_mode(self):
        """Full integration: run density_matrix experiment and render."""
        result = run(
            ExperimentConfig(
                num_qubits=2,
                state_type="GHZ",
                sim_mode="density_matrix",
                noise_enabled=True,
                noise_type="depolarizing",
                error_rate=0.1,
                visualization_type="density_matrix",
                shots=500,
                rng_seed=42,
            )
        )
        dm_arts = [a for a in result.artifacts if a.kind == "density_matrix"]
        assert len(dm_arts) >= 1
        assert os.path.isfile(dm_arts[0].path)


# ---------------------------------------------------------------------------
# CorrelationRenderer
# ---------------------------------------------------------------------------


class TestCorrelationRenderer:
    """Test correlation heatmap rendering."""

    def _make_eec_data(self, n: int = 3) -> dict:
        """Create mock data with EEC extras including matrices."""
        mi = np.random.default_rng(42).random((n, n))
        mi = (mi + mi.T) / 2
        np.fill_diagonal(mi, 0)
        ent = np.ones((n, n)) * 0.5
        np.fill_diagonal(ent, 0)
        return {
            "analysis": {
                "measurement_results": {"raw_counts": {"000": 500, "111": 500}},
                "experiment_parameters": {"state_type": "GHZ", "num_qubits": n},
            },
            "metrics_bundle": {
                "metrics": {
                    "entanglement_error_correlation": {
                        "value": 0.65,
                        "extras": {
                            "error_correlation_matrix": mi.tolist(),
                            "entanglement_matrix": ent.tolist(),
                        },
                    }
                }
            },
            "export_formats": ["png"],
        }

    def test_can_render_with_eec_extras(self):
        renderer = CorrelationRenderer()
        data = self._make_eec_data()
        assert renderer.can_render("correlation", data) is True

    def test_cannot_render_without_matrices(self):
        renderer = CorrelationRenderer()
        data = {
            "metrics_bundle": {
                "metrics": {
                    "entanglement_error_correlation": {
                        "value": 0.5,
                        "extras": {"method": "eec"},
                    }
                }
            }
        }
        assert renderer.can_render("correlation", data) is False

    def test_render_produces_artifact(self, tmp_path: Path):
        renderer = CorrelationRenderer()
        data = self._make_eec_data()
        artifact = renderer.render(data, str(tmp_path / "corr_test.png"))
        assert artifact.kind == "correlation"
        assert os.path.isfile(artifact.path)
        assert artifact.metadata["renderer"] == "CorrelationRenderer"

    def test_integration_correlation_viz(self):
        """Full integration: run experiment with metrics, render correlation."""
        result = run(
            ExperimentConfig(
                num_qubits=4,
                state_type="GHZ",
                noise_enabled=True,
                noise_type="depolarizing",
                error_rate=0.05,
                visualization_type="correlation",
                metrics="decoherence",
                shots=1000,
                rng_seed=42,
            )
        )
        corr_arts = [a for a in result.artifacts if a.kind == "correlation"]
        assert len(corr_arts) >= 1
        assert os.path.isfile(corr_arts[0].path)


# ---------------------------------------------------------------------------
# CircuitDiagramRenderer
# ---------------------------------------------------------------------------


class TestCircuitDiagramRenderer:
    """Test circuit diagram rendering."""

    def test_can_render_with_circuit(self):
        renderer = CircuitDiagramRenderer()
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        data = {"circuit": qc}
        assert renderer.can_render("circuit", data) is True

    def test_cannot_render_without_circuit(self):
        renderer = CircuitDiagramRenderer()
        assert renderer.can_render("circuit", {}) is False

    def test_cannot_render_wrong_type(self):
        renderer = CircuitDiagramRenderer()
        data = {"circuit": QuantumCircuit(2)}
        assert renderer.can_render("histogram", data) is False

    @pytest.mark.skipif(not _has_pylatexenc(), reason="pylatexenc not installed")
    def test_render_produces_artifact(self, tmp_path: Path):
        renderer = CircuitDiagramRenderer()
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        data = {"circuit": qc, "export_formats": ["png"]}
        artifact = renderer.render(data, str(tmp_path / "circuit_test.png"))
        assert artifact.kind == "circuit"
        assert os.path.isfile(artifact.path)
        assert artifact.metadata["renderer"] == "CircuitDiagramRenderer"
        assert artifact.metadata["num_qubits"] == 2

    @pytest.mark.skipif(not _has_pylatexenc(), reason="pylatexenc not installed")
    def test_integration_circuit_viz(self):
        """Full integration: run experiment with circuit rendering."""
        result = run(
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                visualization_type="circuit",
                shots=100,
                rng_seed=42,
            )
        )
        circuit_arts = [a for a in result.artifacts if a.kind == "circuit"]
        assert len(circuit_arts) >= 1
        assert os.path.isfile(circuit_arts[0].path)


# ---------------------------------------------------------------------------
# Multi-format export
# ---------------------------------------------------------------------------


class TestMultiFormatExport:
    """Test that PDF and SVG are created alongside PNG."""

    def test_histogram_multi_format(self):
        result = run(
            ExperimentConfig(
                num_qubits=2,
                state_type="GHZ",
                visualization_type="histogram",
                export_formats=["png", "pdf", "svg"],
                shots=200,
                rng_seed=42,
            )
        )
        hist_arts = [a for a in result.artifacts if a.kind == "histogram"]
        assert len(hist_arts) >= 1
        # The primary artifact should exist
        assert os.path.isfile(hist_arts[0].path)
        # Check that the saved_formats metadata confirms multi-format
        saved_fmts = hist_arts[0].metadata.get("saved_formats", [])
        assert "png" in saved_fmts
        assert "pdf" in saved_fmts
        assert "svg" in saved_fmts
        # Verify sibling files exist
        primary = Path(hist_arts[0].path)
        for ext in [".pdf", ".svg"]:
            sibling = primary.with_suffix(ext)
            assert sibling.exists(), f"Expected {sibling} to exist"


# ---------------------------------------------------------------------------
# visualization_type="all" and "none"
# ---------------------------------------------------------------------------


class TestVizTypeAll:
    """Test that visualization_type='all' produces multiple artifact types."""

    def test_all_produces_multiple_artifacts(self):
        result = run(
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="density_matrix",
                noise_enabled=True,
                noise_type="depolarizing",
                error_rate=0.05,
                visualization_type="all",
                metrics="decoherence",
                shots=500,
                rng_seed=42,
            )
        )
        kinds = {a.kind for a in result.artifacts}
        # Should have at least histogram and density_matrix
        assert "histogram" in kinds
        assert "density_matrix" in kinds
        # Circuit rendering requires pylatexenc; check if available
        try:
            import pylatexenc  # noqa: F401

            assert "circuit" in kinds
        except ImportError:
            pass  # Circuit rendering skipped without pylatexenc


class TestVizTypeNone:
    """Test that visualization_type='none' produces no visualization artifacts."""

    def test_none_produces_no_viz_artifacts(self):
        result = run(
            ExperimentConfig(
                num_qubits=2,
                state_type="GHZ",
                visualization_type="none",
                shots=100,
                rng_seed=42,
            )
        )
        viz_kinds = {"histogram", "density_matrix", "correlation", "circuit"}
        viz_arts = [a for a in result.artifacts if a.kind in viz_kinds]
        assert len(viz_arts) == 0


# ---------------------------------------------------------------------------
# HistogramRenderer multi-format (unit test)
# ---------------------------------------------------------------------------


class TestHistogramRendererMultiFormat:
    """Verify HistogramRenderer uses save_figure for multi-format."""

    def test_render_with_multiple_formats(self, tmp_path: Path):
        renderer = HistogramRenderer()
        data = {
            "analysis": {
                "measurement_results": {"raw_counts": {"00": 500, "11": 500}},
                "experiment_parameters": {"state_type": "GHZ", "num_qubits": 2},
            },
            "export_formats": ["png", "pdf"],
        }
        artifact = renderer.render(data, str(tmp_path / "hist_test.png"))
        assert artifact.kind == "histogram"
        assert os.path.isfile(artifact.path)
        saved_fmts = artifact.metadata.get("saved_formats", [])
        assert "png" in saved_fmts
        assert "pdf" in saved_fmts
