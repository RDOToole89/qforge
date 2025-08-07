# src/visualization/animations.py

"""
Quantum state evolution animations.

This module provides animated visualizations of quantum decoherence,
including Bloch sphere trajectories and state evolution over time.

Perfect for visualizing:
- GHZ decoherence patterns
- Quantum state collapse
- Error propagation dynamics
- Entanglement loss over time
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import logging

logger = logging.getLogger("QuantumExperiment.Visualization.Animations")


def compute_bloch_trajectory(density_matrices: List[Any],
                           qubit_index: int = 0) -> List[Tuple[float, float, float]]:
    """
    Compute Bloch vector trajectory from density matrix evolution.

    This is the KEY function for your decoherence animation idea!

    Args:
        density_matrices: List of density matrices over time
        qubit_index: Which qubit to trace (for multi-qubit states)

    Returns:
        List of (x, y, z) Bloch coordinates over time
    """
    from src.core.analysis.bloch import compute_bloch_vector
    from qiskit.quantum_info import partial_trace, DensityMatrix

    trajectory = []

    for dm in density_matrices:
        try:
            # Handle different input types
            if hasattr(dm, 'data'):
                matrix = dm.data
            else:
                matrix = np.array(dm)

            # For multi-qubit states, trace out other qubits
            if matrix.shape[0] > 2:  # Multi-qubit system
                num_qubits = int(np.log2(matrix.shape[0]))
                if qubit_index < num_qubits:
                    # Trace out all qubits except the target one
                    qubits_to_trace = [i for i in range(num_qubits) if i != qubit_index]
                    dm_single = partial_trace(DensityMatrix(matrix), qubits_to_trace)
                    matrix = dm_single.data

            # Compute Bloch vector for single qubit
            x, y, z = compute_bloch_vector(matrix)
            trajectory.append((x, y, z))

        except Exception as e:
            logger.warning(f"Failed to compute Bloch vector at time step: {e}")
            # Use previous point or origin
            if trajectory:
                trajectory.append(trajectory[-1])
            else:
                trajectory.append((0, 0, 1))  # |0⟩ state

    return trajectory


def create_decoherence_animation(experiment_results: List[Dict],
                                time_steps: List[float],
                                state_type: str = "GHZ",
                                backend: str = "plotly") -> Any:
    """
    Create animated visualization of quantum decoherence.

    This visualizes your "structured decoherence" hypothesis by showing
    how quantum states evolve on the Bloch sphere over time.

    Args:
        experiment_results: List of experiment results at different time steps
        time_steps: Time points for animation frames
        state_type: Type of quantum state (GHZ, W, etc.)
        backend: Visualization backend ('plotly', 'matplotlib', 'manim')

    Returns:
        Animation object (depends on backend)
    """

    # Extract density matrices if available
    density_matrices = []
    for result in experiment_results:
        if 'density_matrix' in result:
            density_matrices.append(result['density_matrix'])
        elif hasattr(result, 'data'):  # Direct DensityMatrix object
            density_matrices.append(result)

    if not density_matrices:
        logger.error("No density matrices found for animation")
        return None

    # Determine number of qubits
    first_dm = density_matrices[0]
    if hasattr(first_dm, 'data'):
        matrix_size = first_dm.data.shape[0]
    else:
        matrix_size = np.array(first_dm).shape[0]
    num_qubits = int(np.log2(matrix_size))

    logger.info(f"Creating {state_type} decoherence animation for {num_qubits} qubits")

    if backend == "plotly":
        return _create_plotly_decoherence_animation(
            density_matrices, time_steps, state_type, num_qubits
        )
    elif backend == "matplotlib":
        return _create_matplotlib_decoherence_animation(
            density_matrices, time_steps, state_type, num_qubits
        )
    elif backend == "manim":
        return _create_manim_decoherence_animation(
            density_matrices, time_steps, state_type, num_qubits
        )
    else:
        raise ValueError(f"Unsupported animation backend: {backend}")


def _create_plotly_decoherence_animation(density_matrices: List[Any],
                                       time_steps: List[float],
                                       state_type: str,
                                       num_qubits: int) -> Any:
    """Create Plotly animated Bloch sphere decoherence visualization."""

    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        logger.error("Plotly not available for animation")
        return None

    # Compute trajectories for each qubit
    trajectories = {}
    for qubit in range(num_qubits):
        trajectory = compute_bloch_trajectory(density_matrices, qubit)
        trajectories[qubit] = trajectory

    # Create subplots for multiple qubits
    if num_qubits == 1:
        fig = go.Figure()
        _add_bloch_sphere(fig)
        _add_animated_trajectory(fig, trajectories[0], time_steps, f"{state_type} State")
    else:
        # Multiple qubits - create subplot for each
        cols = min(num_qubits, 3)  # Max 3 columns
        rows = (num_qubits + cols - 1) // cols

        fig = make_subplots(
            rows=rows, cols=cols,
            specs=[[{'type': 'scatter3d'} for _ in range(cols)] for _ in range(rows)],
            subplot_titles=[f"Qubit {i}" for i in range(num_qubits)]
        )

        for qubit in range(num_qubits):
            row = qubit // cols + 1
            col = qubit % cols + 1

            _add_bloch_sphere(fig, row=row, col=col)
            _add_animated_trajectory(
                fig, trajectories[qubit], time_steps,
                f"{state_type} Qubit {qubit}", row=row, col=col
            )

    # Animation controls
    fig.update_layout(
        title=f"{state_type} State Decoherence Animation",
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'Play', 'method': 'animate', 'args': [None, {'frame': {'duration': 100}}]},
                {'label': 'Pause', 'method': 'animate', 'args': [[None], {'frame': {'duration': 0}}]}
            ]
        }],
        height=600 if num_qubits == 1 else 400 * rows
    )

    return fig


def _add_bloch_sphere(fig: Any, row: Optional[int] = None, col: Optional[int] = None):
    """Add Bloch sphere surface to plot."""
    # Create sphere surface
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))

    fig.add_trace(
        go.Surface(
            x=x, y=y, z=z,
            opacity=0.3,
            colorscale='Blues',
            showscale=False,
            hoverinfo='skip',
            name='Bloch Sphere'
        ),
        row=row, col=col
    )

    # Add coordinate axes
    for axis, color in [('x', 'red'), ('y', 'green'), ('z', 'blue')]:
        if axis == 'x':
            coords = ([-1, 1], [0, 0], [0, 0])
        elif axis == 'y':
            coords = ([0, 0], [-1, 1], [0, 0])
        else:  # z
            coords = ([0, 0], [0, 0], [-1, 1])

        fig.add_trace(
            go.Scatter3d(
                x=coords[0], y=coords[1], z=coords[2],
                mode='lines',
                line=dict(color=color, width=4),
                name=f'{axis.upper()}-axis',
                showlegend=False
            ),
            row=row, col=col
        )


def _add_animated_trajectory(fig: Any, trajectory: List[Tuple[float, float, float]],
                           time_steps: List[float], name: str,
                           row: Optional[int] = None, col: Optional[int] = None):
    """Add animated Bloch vector trajectory."""
    import plotly.graph_objects as go

    # Extract coordinates
    x_vals, y_vals, z_vals = zip(*trajectory)

    # Create frames for animation
    frames = []
    for i in range(len(trajectory)):
        frame_data = []

        # Trajectory up to current point
        frame_data.append(
            go.Scatter3d(
                x=x_vals[:i+1],
                y=y_vals[:i+1],
                z=z_vals[:i+1],
                mode='lines',
                line=dict(color='red', width=6),
                name='Trajectory',
                showlegend=False
            )
        )

        # Current position marker
        frame_data.append(
            go.Scatter3d(
                x=[x_vals[i]],
                y=[y_vals[i]],
                z=[z_vals[i]],
                mode='markers',
                marker=dict(size=10, color='red'),
                name=f't={time_steps[i]:.3f}',
                showlegend=False
            )
        )

        frames.append(go.Frame(data=frame_data, name=str(i)))

    fig.frames = frames

    # Add initial trajectory
    fig.add_trace(
        go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='lines+markers',
            line=dict(color='red', width=4),
            marker=dict(size=6, color=np.arange(len(x_vals)), colorscale='Viridis'),
            name=name
        ),
        row=row, col=col
    )


def _create_matplotlib_decoherence_animation(density_matrices: List[Any],
                                           time_steps: List[float],
                                           state_type: str,
                                           num_qubits: int) -> Any:
    """Create matplotlib animated Bloch sphere (for fallback)."""

    try:
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from mpl_toolkits.mplot3d import Axes3D
    except ImportError:
        logger.error("Matplotlib not available for animation")
        return None

    # Compute trajectory for first qubit
    trajectory = compute_bloch_trajectory(density_matrices, 0)
    x_vals, y_vals, z_vals = zip(*trajectory)

    # Create figure
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot Bloch sphere
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.3, color='lightblue')

    # Initialize trajectory plot
    trajectory_line, = ax.plot([], [], [], 'r-', linewidth=3, label='Trajectory')
    current_point, = ax.plot([], [], [], 'ro', markersize=10, label='Current State')

    ax.set_xlim([-1.2, 1.2])
    ax.set_ylim([-1.2, 1.2])
    ax.set_zlim([-1.2, 1.2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'{state_type} State Decoherence Animation')
    ax.legend()

    def animate(frame):
        """Animation function."""
        # Update trajectory up to current frame
        trajectory_line.set_data_3d(x_vals[:frame+1], y_vals[:frame+1], z_vals[:frame+1])

        # Update current point
        current_point.set_data_3d([x_vals[frame]], [y_vals[frame]], [z_vals[frame]])

        # Update title with time
        ax.set_title(f'{state_type} State Decoherence (t={time_steps[frame]:.3f})')

        return trajectory_line, current_point

    # Create animation
    anim = FuncAnimation(fig, animate, frames=len(trajectory),
                        interval=200, blit=False, repeat=True)

    return anim


def analyze_decoherence_patterns(trajectories: Dict[int, List[Tuple[float, float, float]]],
                               time_steps: List[float],
                               state_type: str = "GHZ") -> Dict[str, Any]:
    """
    Analyze decoherence patterns from Bloch trajectories.

    This supports your structured decoherence research by quantifying
    how different qubits lose coherence over time.
    """

    analysis = {
        'state_type': state_type,
        'num_qubits': len(trajectories),
        'time_steps': time_steps,
        'qubit_analysis': {}
    }

    for qubit_id, trajectory in trajectories.items():
        # Compute decoherence metrics
        x_vals, y_vals, z_vals = zip(*trajectory)

        # Distance from initial state
        initial_state = trajectory[0]
        distances = [
            np.sqrt((x - initial_state[0])**2 +
                   (y - initial_state[1])**2 +
                   (z - initial_state[2])**2)
            for x, y, z in trajectory
        ]

        # Purity evolution (distance from origin)
        purities = [np.sqrt(x**2 + y**2 + z**2) for x, y, z in trajectory]

        # Decoherence rate (approximate)
        if len(time_steps) > 1:
            decoherence_rate = (purities[0] - purities[-1]) / (time_steps[-1] - time_steps[0])
        else:
            decoherence_rate = 0

        analysis['qubit_analysis'][qubit_id] = {
            'initial_purity': purities[0],
            'final_purity': purities[-1],
            'decoherence_rate': decoherence_rate,
            'max_deviation': max(distances),
            'trajectory_length': len(trajectory)
        }

    # Global analysis
    all_purities = [data['final_purity'] for data in analysis['qubit_analysis'].values()]
    analysis['global_metrics'] = {
        'average_final_purity': np.mean(all_purities),
        'purity_variance': np.var(all_purities),
        'coherence_asymmetry': np.std(all_purities)  # How differently qubits decohere
    }

    return analysis


# Example usage for your research
def create_ghz_decoherence_study(num_qubits: int = 3,
                               noise_rates: List[float] = [0.01, 0.05, 0.1, 0.15, 0.2],
                               time_steps: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Create a comprehensive GHZ decoherence study with animations.

    This is perfect for your structured decoherence research!
    """

    if time_steps is None:
        time_steps = np.linspace(0, 1.0, 20)

    study_results = {
        'state_type': 'GHZ',
        'num_qubits': num_qubits,
        'noise_rates': noise_rates,
        'time_steps': time_steps,
        'animations': {},
        'analysis': {}
    }

    for noise_rate in noise_rates:
        logger.info(f"Generating GHZ decoherence animation for noise rate: {noise_rate}")

        # Here you would run your experiments with different noise rates
        # For now, we'll create a placeholder structure

        study_results['animations'][noise_rate] = {
            'description': f'GHZ decoherence with {noise_rate} error rate',
            'ready_for_generation': True
        }

        study_results['analysis'][noise_rate] = {
            'structured_patterns': 'Analysis pending',
            'decoherence_signature': 'To be computed'
        }

    return study_results
