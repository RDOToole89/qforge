# src/visualization/backends/plotly_backend.py

"""
Plotly backend for interactive quantum visualizations.

Provides interactive plots with zoom, pan, hover tooltips, and export capabilities.
Perfect for research exploration and publication-ready interactive figures.
"""

import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("QuantumExperiment.Visualization.Backends.Plotly")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    logger.warning("Plotly not available. Install with: pip install plotly")
    PLOTLY_AVAILABLE = False


def plot_interactive_histogram(
    counts: Dict[str, int],
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    research_metrics: Optional[Dict] = None,
    **kwargs,
) -> Optional[go.Figure]:
    """
    Create interactive histogram with Plotly.

    Features:
    - Hover tooltips with detailed state information
    - Zoomable and pannable
    - Export to HTML, PNG, SVG
    - Color-coded by quantum state type
    """
    if not PLOTLY_AVAILABLE:
        logger.error("Plotly not available for interactive histogram")
        return None

    # Prepare data
    states = list(counts.keys())
    values = list(counts.values())
    total_shots = sum(values)
    probabilities = [v / total_shots for v in values]

    # Quantum-aware colors
    colors = []
    for state in states:
        if state_type == "GHZ":
            if state in ["000", "111"]:
                colors.append("#1f77b4")  # Blue for expected states
            else:
                colors.append("#ff7f0e")  # Orange for error states
        elif state_type == "W":
            ones_count = state.count("1")
            if ones_count == 1:
                colors.append("#2ca02c")  # Green for W states
            else:
                colors.append("#d62728")  # Red for errors
        else:
            colors.append("#1f77b4")  # Default blue

    # Create interactive histogram
    fig = go.Figure(
        data=[
            go.Bar(
                x=states,
                y=values,
                marker_color=colors,
                hovertemplate="<b>State:</b> |%{x}⟩<br>"
                + "<b>Count:</b> %{y}<br>"
                + "<b>Probability:</b> %{customdata:.4f}<br>"
                + "<extra></extra>",
                customdata=probabilities,
                name="Measurement Counts",
            )
        ]
    )

    # Enhanced layout
    title = f"{state_type or 'Quantum'} State Measurements"
    if noise_type:
        title += f" (with {noise_type} noise)"

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=18, family="Arial, sans-serif")),
        xaxis_title="Quantum States",
        yaxis_title="Measurement Counts",
        template="plotly_white",
        hovermode="closest",
        showlegend=False,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50),
    )

    # Add research metrics annotation if available
    if research_metrics and "information_theory" in research_metrics:
        metrics = research_metrics["information_theory"]
        annotation_text = (
            f"Shannon Entropy: {metrics.get('shannon_entropy', 0):.3f}<br>"
        )
        annotation_text += f"Normalized H: {metrics.get('normalized_entropy', 0):.3f}"

        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text=annotation_text,
            showarrow=False,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
            font=dict(size=10),
        )

    # Display
    fig.show()
    return fig


def plot_interactive_density_matrix(
    density_matrix: Any,
    state_type: Optional[str] = None,
    research_metrics: Optional[Dict] = None,
    **kwargs,
) -> Optional[go.Figure]:
    """
    Create interactive 3D density matrix visualization.

    Features:
    - 3D surface plot with rotation
    - Separate real/imaginary components
    - Hover information with matrix elements
    """
    if not PLOTLY_AVAILABLE:
        logger.error("Plotly not available for interactive density matrix")
        return None

    # Extract matrix data
    if hasattr(density_matrix, "data"):
        matrix = density_matrix.data
    else:
        matrix = np.array(density_matrix)

    n = matrix.shape[0]
    indices = np.arange(n)
    x_mesh, y_mesh = np.meshgrid(indices, indices)

    # Create subplots for real and imaginary parts
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Real Part", "Imaginary Part"),
        specs=[[{"type": "surface"}, {"type": "surface"}]],
    )

    # Real part
    fig.add_trace(
        go.Surface(
            x=x_mesh,
            y=y_mesh,
            z=np.real(matrix),
            colorscale="RdBu",
            name="Real",
            hovertemplate="<b>Element:</b> ρ[%{y},%{x}]<br>"
            + "<b>Real:</b> %{z:.4f}<br>"
            + "<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Imaginary part
    fig.add_trace(
        go.Surface(
            x=x_mesh,
            y=y_mesh,
            z=np.imag(matrix),
            colorscale="Viridis",
            name="Imaginary",
            hovertemplate="<b>Element:</b> ρ[%{y},%{x}]<br>"
            + "<b>Imaginary:</b> %{z:.4f}<br>"
            + "<extra></extra>",
        ),
        row=1,
        col=2,
    )

    # Update layout
    title = f"{state_type or 'Quantum'} State Density Matrix"
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        scene=dict(
            xaxis_title="Column Index", yaxis_title="Row Index", zaxis_title="Amplitude"
        ),
        scene2=dict(
            xaxis_title="Column Index", yaxis_title="Row Index", zaxis_title="Amplitude"
        ),
        height=600,
    )

    fig.show()
    return fig


def plot_interactive_bloch_sphere(
    bloch_vectors: List[tuple],
    time_steps: Optional[List[float]] = None,
    state_type: Optional[str] = None,
    **kwargs,
) -> Optional[go.Figure]:
    """
    Create interactive 3D Bloch sphere with trajectory.

    Features:
    - 3D Bloch sphere with rotation
    - Animated trajectory over time
    - Color-coded by time or fidelity
    """
    if not PLOTLY_AVAILABLE:
        logger.error("Plotly not available for interactive Bloch sphere")
        return None

    fig = go.Figure()

    # Add Bloch sphere surface
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    fig.add_trace(
        go.Surface(
            x=x_sphere,
            y=y_sphere,
            z=z_sphere,
            opacity=0.3,
            colorscale="Blues",
            showscale=False,
            hoverinfo="skip",
        )
    )

    # Add Bloch vectors trajectory
    if isinstance(bloch_vectors[0], dict):
        # Multiple qubits case
        for qubit_id, vectors in enumerate(bloch_vectors):
            if isinstance(vectors, dict):
                x_vals = [v[0] for v in vectors.values()]
                y_vals = [v[1] for v in vectors.values()]
                z_vals = [v[2] for v in vectors.values()]
            else:
                x_vals, y_vals, z_vals = zip(*vectors)

            fig.add_trace(
                go.Scatter3d(
                    x=x_vals,
                    y=y_vals,
                    z=z_vals,
                    mode="lines+markers",
                    name=f"Qubit {qubit_id}",
                    line=dict(width=4),
                    marker=dict(size=4),
                )
            )
    else:
        # Single trajectory
        x_vals, y_vals, z_vals = zip(*bloch_vectors)

        fig.add_trace(
            go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode="lines+markers",
                name="Bloch Vector",
                line=dict(width=6),
                marker=dict(size=6, color=np.arange(len(x_vals)), colorscale="Viridis"),
            )
        )

    # Update layout
    fig.update_layout(
        title=f"{state_type or 'Quantum'} State Bloch Sphere Evolution",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            aspectmode="cube",
            xaxis=dict(range=[-1.5, 1.5]),
            yaxis=dict(range=[-1.5, 1.5]),
            zaxis=dict(range=[-1.5, 1.5]),
        ),
        height=700,
    )

    fig.show()
    return fig


# Register plotly backend functions
def register_plotly_backend():
    """Register Plotly backend with the backend registry."""
    if not PLOTLY_AVAILABLE:
        return

    from . import backend_registry

    plotly_functions = {
        "plot_histogram": plot_interactive_histogram,
        "plot_density_matrix": plot_interactive_density_matrix,
        "plot_bloch_sphere": plot_interactive_bloch_sphere,
    }

    backend_registry.register_backend("plotly", plotly_functions)


# Auto-register when imported
if PLOTLY_AVAILABLE:
    register_plotly_backend()
