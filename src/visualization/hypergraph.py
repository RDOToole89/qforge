# src/visualization/hypergraph_clean.py

"""
Clean hypergraph visualization module.

This module provides hypergraph visualization functionality that calls
the analysis modules for computations, keeping the visualization layer
separate from the analysis logic.
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import networkx as nx
import hypernetx as hnx
import logging
from typing import Optional, Dict, List, Union, Callable
from scipy.spatial import ConvexHull

# Import analysis modules
from src.core.analysis.correlations import (
    compute_pairwise_correlations,
    compute_correlations_for_hypergraph,
)
from src.core.analysis.decoherence import compute_fubini_study_distance
from src.core.analysis.symmetry import (
    compute_su2_symmetry,
    compute_su3_symmetry,
    compute_parity_distribution,
)
from src.core.analysis.clustering import cluster_qubits
from src.core.analysis.bloch import compute_bloch_vector
from src.core.analysis.transitions import compute_error_transitions

logger = logging.getLogger("QuantumExperiment.Visualization.Hypergraph")


def compute_quantum_layout(
    num_qubits: int,
    state_type: str = "GHZ",
    layout_type: str = "quantum_circuit"
) -> Dict[str, tuple]:
    """
    Computes quantum-specific node layouts for hypergraph visualization.

    Args:
        num_qubits (int): Number of qubits in the system.
        state_type (str): Type of quantum state (GHZ, Bell, W, etc.).
        layout_type (str): Type of layout algorithm to use.

    Returns:
        Dict[str, tuple]: Node positions as {node_id: (x, y)}.
    """
    positions = {}

    if layout_type == "quantum_circuit":
        # Linear arrangement like a quantum circuit
        for i in range(num_qubits):
            positions[f"q{i}"] = (i, 0)

    elif layout_type == "entanglement_tree":
        # Tree layout based on entanglement structure
        if state_type in ["GHZ", "W"]:
            # Star topology: first qubit at center, others around
            center_x, center_y = 0, 0
            radius = 1.5
            positions[f"q0"] = (center_x, center_y)

            for i in range(1, num_qubits):
                angle = 2 * np.pi * (i - 1) / (num_qubits - 1)
                x = center_x + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)
                positions[f"q{i}"] = (x, y)

        elif state_type == "Bell":
            # Simple pair layout for Bell states
            positions[f"q0"] = (-0.5, 0)
            positions[f"q1"] = (0.5, 0)
            for i in range(2, num_qubits):
                positions[f"q{i}"] = (i - 1, 1)

    elif layout_type == "correlation_strength":
        # Position based on correlation strengths (placeholder - requires correlation data)
        # For now, use a circular layout with some randomness
        radius = 2.0
        for i in range(num_qubits):
            angle = 2 * np.pi * i / num_qubits
            # Add small random offset based on qubit index for distinguishability
            offset = 0.1 * (i % 3 - 1)
            x = radius * np.cos(angle) + offset
            y = radius * np.sin(angle) + offset
            positions[f"q{i}"] = (x, y)

    elif layout_type == "bloch_sphere":
        # 3D-inspired layout projecting Bloch sphere positions to 2D
        if num_qubits <= 3:
            # For small systems, use special arrangements
            if num_qubits == 2:
                positions[f"q0"] = (0, 1)    # |0⟩ at north pole
                positions[f"q1"] = (0, -1)   # |1⟩ at south pole
            elif num_qubits == 3:
                # Triangle arrangement
                positions[f"q0"] = (0, 1)
                positions[f"q1"] = (-0.866, -0.5)
                positions[f"q2"] = (0.866, -0.5)
        else:
            # For larger systems, use spherical projection
            for i in range(num_qubits):
                phi = 2 * np.pi * i / num_qubits  # Azimuthal angle
                theta = np.pi * (i + 0.5) / num_qubits  # Polar angle

                # Project sphere to plane using stereographic projection
                x = 2 * np.sin(theta) * np.cos(phi) / (1 + np.cos(theta))
                y = 2 * np.sin(theta) * np.sin(phi) / (1 + np.cos(theta))
                positions[f"q{i}"] = (x, y)

    elif layout_type == "tensor_network":
        # Layout based on tensor network structure
        if num_qubits <= 4:
            # Small tensor networks: rectangular grid
            cols = int(np.ceil(np.sqrt(num_qubits)))
            rows = int(np.ceil(num_qubits / cols))

            for i in range(num_qubits):
                row = i // cols
                col = i % cols
                positions[f"q{i}"] = (col, -row)  # Negative for upward growth
        else:
            # Larger networks: hexagonal close packing
            layer = 0
            positions_per_layer = 1
            qubit_count = 0

            while qubit_count < num_qubits:
                if layer == 0:
                    positions[f"q{qubit_count}"] = (0, 0)
                    qubit_count += 1
                else:
                    radius = layer * 1.5
                    for i in range(min(6 * layer, num_qubits - qubit_count)):
                        angle = 2 * np.pi * i / (6 * layer)
                        x = radius * np.cos(angle)
                        y = radius * np.sin(angle)
                        positions[f"q{qubit_count}"] = (x, y)
                        qubit_count += 1
                layer += 1

    else:
        # Default to circular layout
        radius = max(1.5, num_qubits * 0.3)
        for i in range(num_qubits):
            angle = 2 * np.pi * i / num_qubits
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            positions[f"q{i}"] = (x, y)

    logger.info(f"Generated {layout_type} layout for {num_qubits} qubits in {state_type} state")
    return positions


def get_quantum_color_scheme(
    num_qubits: int,
    state_type: str = "GHZ",
    scheme: str = "entanglement"
) -> Dict[str, str]:
    """
    Generate quantum-aware color schemes for nodes and edges.

    Args:
        num_qubits (int): Number of qubits.
        state_type (str): Type of quantum state.
        scheme (str): Color scheme type.

    Returns:
        Dict[str, str]: Color mapping for nodes.
    """
    colors = {}

    if scheme == "entanglement":
        # Color based on entanglement role
        if state_type in ["GHZ", "W"]:
            # Special color for the "central" qubit
            colors[f"q0"] = "#FF6B6B"  # Red for central qubit

            # Gradient for other qubits
            for i in range(1, num_qubits):
                intensity = 1.0 - (i / num_qubits) * 0.5
                blue_val = int(255 * intensity)
                colors[f"q{i}"] = f"#{blue_val:02x}{blue_val:02x}FF"

        elif state_type == "Bell":
            # Symmetric colors for Bell pairs
            colors[f"q0"] = "#FF6B6B"  # Red
            colors[f"q1"] = "#4ECDC4"  # Teal
            for i in range(2, num_qubits):
                colors[f"q{i}"] = "#95E1D3"  # Light green

    elif scheme == "bloch_phase":
        # Color based on Bloch sphere position (simulated)
        for i in range(num_qubits):
            phase = 2 * np.pi * i / num_qubits
            r = int(127 + 127 * np.cos(phase))
            g = int(127 + 127 * np.cos(phase + 2*np.pi/3))
            b = int(127 + 127 * np.cos(phase + 4*np.pi/3))
            colors[f"q{i}"] = f"#{r:02x}{g:02x}{b:02x}"

    elif scheme == "correlation_strength":
        # Use a colormap based on correlation strength (placeholder)
        cmap = cm.get_cmap('viridis')
        for i in range(num_qubits):
            color_val = cmap(i / max(1, num_qubits - 1))
            colors[f"q{i}"] = mcolors.to_hex(color_val)

    else:
        # Default quantum colors
        quantum_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        for i in range(num_qubits):
            colors[f"q{i}"] = quantum_colors[i % len(quantum_colors)]

    return colors


def plot_hypergraph(
    correlation_data: Union[Dict, List[Dict]],
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    save_path: Optional[str] = None,
    time_steps: Optional[List[float]] = None,
    config: Optional[Dict] = None,
    show_plot_nonblocking: Optional[Callable] = None,
) -> bool:
    """
    Plots a hypergraph of quantum state correlations with enhanced scientific visualization.

    This function orchestrates the visualization by calling analysis modules
    for computations, keeping the visualization layer clean and focused.

    Args:
        correlation_data: The data to plot (counts or density matrix).
        state_type: The type of quantum state.
        noise_type: The type of noise applied.
        save_path: Path to save the plot, if any.
        time_steps: Timesteps for dynamic visualization.
        config: Visualization configuration.
        show_plot_nonblocking: Function to show plots non-blockingly.

    Returns:
        bool: True if all plots were closed with Enter, False if any were closed with Ctrl+C.
    """
    config = config or {}
    config.setdefault("max_order", 2)
    config.setdefault("threshold", None)
    config.setdefault("adaptive_threshold", True)
    config.setdefault("target_edge_count", None)
    config.setdefault("threshold_percentile", 75.0)
    config.setdefault("symmetry_analysis", False)
    config.setdefault("plot_transitions", False)
    config.setdefault("plot_bloch", False)
    config.setdefault("node_color", "blue")
    config.setdefault("edge_color", "red")
    config.setdefault("layout", "entanglement_tree")
    config.setdefault("use_quantum_layout", True)
    config.setdefault("layout_algorithm", "spring")
    config.setdefault("color_scheme", "entanglement")
    config.setdefault("use_quantum_colors", True)
    config.setdefault("node_size", 800)
    config.setdefault("node_alpha", 0.8)
    config.setdefault("label_font_size", 12)

    plot_closed_with_ctrl_c = False

    # Handle time-stepped visualization
    if time_steps is not None and isinstance(correlation_data, list):
        # Compute Fubini-Study distances using analysis module
        fs_distances = []
        for i in range(len(correlation_data) - 1):
            if (
                "density" in correlation_data[i]
                and "density" in correlation_data[i + 1]
            ):
                rho1 = np.array(correlation_data[i]["density"])
                rho2 = np.array(correlation_data[i + 1]["density"])
                distance = compute_fubini_study_distance(rho1, rho2)
                fs_distances.append(distance)
            else:
                fs_distances.append(0.0)

        # Plot Bloch vectors if requested
        if config.get("plot_bloch") and time_steps is not None and show_plot_nonblocking is not None:
            plot_closed_with_ctrl_c |= plot_bloch_sphere_vectors(
                correlation_data, time_steps, save_path, show_plot_nonblocking
            )

        # Plot Fubini-Study distance over time
        if time_steps is not None and fs_distances and show_plot_nonblocking is not None:
            plot_closed_with_ctrl_c |= plot_fubini_study_distance(
                time_steps, fs_distances, save_path, show_plot_nonblocking
            )

        # Plot hypergraphs for each timestep
        for step, data in enumerate(correlation_data):
            fs_distance = fs_distances[step - 1] if step > 0 else None
            plot_closed_with_ctrl_c |= plot_single_hypergraph(
                data,
                state_type,
                noise_type,
                f"{save_path}_step_{step}.png" if save_path else None,
                time_steps[step],
                config,
                fs_distance=fs_distance,
                show_plot_nonblocking=show_plot_nonblocking,
            )

        # Plot error transitions if requested
        if config.get("plot_transitions"):
            if isinstance(correlation_data, list) and all(
                isinstance(item, dict) and "density" not in item
                for item in correlation_data
            ):
                plot_closed_with_ctrl_c |= plot_error_transition_graph(
                    correlation_data, time_steps, save_path, show_plot_nonblocking
                )
            else:
                logger.warning(
                    "Skipping error transition graph in density mode as it requires QASM counts."
                )
    else:
        # Single hypergraph plot
        plot_closed_with_ctrl_c = plot_single_hypergraph(
            correlation_data,
            state_type,
            noise_type,
            save_path,
            None,
            config,
            fs_distance=None,
            show_plot_nonblocking=show_plot_nonblocking,
        )

    return plot_closed_with_ctrl_c


def plot_single_hypergraph(
    correlation_data: Dict,
    state_type: Optional[str],
    noise_type: Optional[str],
    save_path: Optional[str],
    time_step: Optional[float],
    config: Dict,
    fs_distance: Optional[float] = None,
    show_plot_nonblocking: Optional[Callable] = None,
) -> bool:
    """
    Plots a single hypergraph with analysis results.

    Args:
        correlation_data: The data to plot (counts or density matrix).
        state_type: The type of quantum state.
        noise_type: The type of noise applied.
        save_path: Path to save the plot, if any.
        time_step: The current timestep (if time-stepped).
        config: Visualization configuration.
        fs_distance: Fubini-Study distance for this timestep.
        show_plot_nonblocking: Function to show plots non-blockingly.

    Returns:
        bool: True if the plot was closed with Enter, False if closed with Ctrl+C.
    """
    if not correlation_data:
        logger.warning("No valid correlation data for hypergraph plotting.")
        return False

    # Determine mode and extract basic info
    mode = "density" if "density" in correlation_data else "qasm"
    if mode == "density":
        density_matrix = np.array(correlation_data["density"])
        num_qubits = int(np.log2(density_matrix.shape[0]))
        shots = 1.0
    else:
        first_key = next(iter(correlation_data.keys()))
        num_qubits = len(first_key)
        if hasattr(correlation_data, 'shots'):
            shots = correlation_data.shots()
        else:
            shots = sum(int(count) for count in correlation_data.values())

    # Use analysis modules for computations
    edges = compute_correlations_for_hypergraph(
        correlation_data, num_qubits, mode, config
    )
    if not edges:
        logger.warning("No significant correlations found for hypergraph plotting.")
        return False

    # Get analysis results using analysis modules
    pairwise_corrs = compute_pairwise_correlations(
        correlation_data, num_qubits, mode, shots
    )
    clusters = (
        cluster_qubits(pairwise_corrs, num_qubits, num_clusters=2)
        if num_qubits > 1
        else [[0]]
    )

    # Collect correlation values for color scaling
    all_corrs = [props["weight"] for (_, props) in edges.values()]
    min_corr_val = min(all_corrs)
    max_corr_val = max(all_corrs)
    mean_corr_val = np.mean(all_corrs)
    abs_max_corr = max(abs(c) for c in all_corrs)

    def plot_func():
        # Set up figure with two subplots
        fig = plt.figure(figsize=(10, 8))
        gs = fig.add_gridspec(2, 1, height_ratios=[4, 1])
        ax_graph = fig.add_subplot(gs[0, 0])
        ax_analysis = fig.add_subplot(gs[1, 0])
        ax_analysis.set_axis_off()

        # Create hypergraph
        Hedges = {
            frozenset(edge_nodes): frozenset(edge_nodes)
            for edge_key, (edge_nodes, _) in edges.items()
        }
        H = hnx.Hypergraph(Hedges)

        # Enhanced quantum-specific node positioning
        layout_type = config.get("layout", "quantum_circuit")
        use_quantum_layout = config.get("use_quantum_layout", True)

        if use_quantum_layout and state_type:
            # Use quantum-specific layouts
            pos = compute_quantum_layout(num_qubits, state_type, layout_type)
            logger.info(f"Using quantum layout: {layout_type} for {state_type} state")
        else:
            # Fallback to traditional layout algorithms
            layout_algorithm = config.get("layout_algorithm", "spring")
            if layout_algorithm == "spring":
                pos = nx.spring_layout(H, seed=42)
            elif layout_algorithm == "circular":
                pos = nx.circular_layout(H)
            elif layout_algorithm == "spectral":
                pos = nx.spectral_layout(H)
            else:
                pos = nx.spring_layout(H, seed=42)
            logger.info(f"Using traditional layout: {layout_algorithm}")

        # Get quantum-aware node colors
        color_scheme = config.get("color_scheme", "entanglement")
        use_quantum_colors = config.get("use_quantum_colors", True)

        if use_quantum_colors and state_type:
            node_colors = get_quantum_color_scheme(num_qubits, state_type, color_scheme)
            node_color_list = [node_colors.get(node, config.get("node_color", "blue")) for node in H.nodes]
            logger.info(f"Using quantum color scheme: {color_scheme}")
        else:
            node_color_list = config.get("node_color", "blue")
            logger.info("Using traditional node coloring")

        # Build style info for edges
        cmap = cm.RdYlGn
        norm = mcolors.Normalize(vmin=-abs_max_corr, vmax=abs_max_corr)
        scale_factor = 4.0

        edge_styles = {}
        edge_labels = {}

        for edge_key, (edge_nodes, props) in edges.items():
            corr_val = props["weight"]
            color = cmap(norm(corr_val))
            linewidth = 1 + scale_factor * (abs(corr_val) / abs_max_corr)
            edge_styles[frozenset(edge_nodes)] = {
                "color": color,
                "linewidth": linewidth,
            }
            label_text = f"{corr_val:.2f}"
            if abs(corr_val) == abs_max_corr:
                label_text += " *"
            edge_labels[frozenset(edge_nodes)] = label_text

        # Draw the graph with quantum-aware styling
        nx.draw_networkx_nodes(
            H, pos,
            node_color=node_color_list,
            node_size=config.get("node_size", 800),
            alpha=config.get("node_alpha", 0.8),
            ax=ax_graph
        )
        nx.draw_networkx_labels(
            H, pos,
            font_size=config.get("label_font_size", 12),
            font_weight="bold",
            ax=ax_graph
        )

        # Draw hyperedges as polygons
        for ekey, style_dict in edge_styles.items():
            pts = np.array([pos[node] for node in ekey])
            if len(pts) >= 3:
                try:
                    hull = ConvexHull(pts)
                    poly = pts[hull.vertices]
                except:
                    poly = pts
            else:
                poly = pts

            patch = plt.Polygon(
                poly,
                closed=True,
                fill=False,
                edgecolor=style_dict["color"],
                linewidth=style_dict["linewidth"],
            )
            ax_graph.add_patch(patch)

            # Place label at centroid
            centroid = poly.mean(axis=0)
            ax_graph.text(
                centroid[0],
                centroid[1],
                edge_labels[ekey],
                fontsize=10,
                ha="center",
                va="center",
                color="black",
            )

        # Enhanced title with layout and threshold information
        title_str = f"{state_type or 'Quantum'} State Hypergraph"
        if noise_type:
            title_str += f" with {noise_type} Noise"
        if time_step is not None:
            title_str += f" (t={time_step:.2f})"

        # Add layout and threshold info as subtitle
        layout_info = f"Layout: {layout_type}" if use_quantum_layout else "Layout: Traditional"
        threshold_used = config.get("threshold")
        if config.get("adaptive_threshold", True):
            threshold_info = f"Adaptive Threshold: {threshold_used:.4f}" if threshold_used else "Adaptive Threshold"
        else:
            threshold_info = f"Manual Threshold: {threshold_used:.4f}" if threshold_used else "Default Threshold"

        ax_graph.set_title(title_str, fontsize=14, fontweight='bold')
        ax_graph.text(0.5, 0.95, f"{layout_info} | {threshold_info}",
                     transform=ax_graph.transAxes, ha='center', va='top',
                     fontsize=10, style='italic', alpha=0.8)

        # Add colorbar
        sm = cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cb = fig.colorbar(
            sm, ax=ax_graph, orientation="vertical", label="Correlation Value"
        )

        # Build analysis text using analysis modules
        analysis_lines = build_analysis_text(
            correlation_data, num_qubits, mode, shots, clusters, fs_distance, config
        )

        # Display analysis text
        analysis_text = "\n".join(analysis_lines)
        ax_analysis.text(
            0.01,
            0.5,
            analysis_text,
            fontsize=10,
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9),
            transform=ax_analysis.transAxes,
        )

        ax_analysis.set_xlim(0, 1)
        ax_analysis.set_ylim(0, 1)

    # Save or show the plot
    if save_path:
        plot_func()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved hypergraph to {save_path}")
        plt.close()
        return False
    elif state_type:  # Auto-generate organized save path
        from .save_manager import get_organized_save_path
        experiment_config = {
            'state_type': state_type,
            'noise_type': noise_type,
            'num_qubits': num_qubits
        }
        auto_save_path = get_organized_save_path(
            viz_type='hypergraph',
            experiment_config=experiment_config
        )
        plot_func()
        plt.savefig(auto_save_path, dpi=300, bbox_inches="tight")
        logger.info(f"Hypergraph auto-saved to {auto_save_path}")
        plt.close()
        return False
    else:
        print(
            f"Displaying hypergraph for timestep {time_step if time_step is not None else 'single'}..."
        )
        if show_plot_nonblocking is not None:
            return not show_plot_nonblocking(plot_func)
        else:
            # Fallback to standard plt.show() if no custom show function
            plot_func()
            plt.show()
            return False


def build_analysis_text(
    correlation_data: Dict,
    num_qubits: int,
    mode: str,
    shots: float,
    clusters: List[List[int]],
    fs_distance: Optional[float],
    config: Dict,
) -> List[str]:
    """
    Builds analysis text using analysis modules.

    Args:
        correlation_data: The correlation data.
        num_qubits: Number of qubits.
        mode: Analysis mode ('qasm' or 'density').
        shots: Number of shots.
        clusters: Qubit clusters.
        fs_distance: Fubini-Study distance.
        config: Configuration.

    Returns:
        List[str]: Analysis text lines.
    """
    analysis_lines = []
    analysis_lines.append(r"**Basic Correlation Stats**:")
    if mode == "qasm":
        analysis_lines.append(f"- Shots Used: {shots}")

    # Get correlation statistics
    edges = compute_correlations_for_hypergraph(
        correlation_data, num_qubits, mode, config
    )
    if edges:
        all_corrs = [props["weight"] for (_, props) in edges.values()]
        analysis_lines.append(f"- Min Corr: {min(all_corrs):.2f}")
        analysis_lines.append(f"- Max Corr: {max(all_corrs):.2f}")
        analysis_lines.append(f"- Mean Corr: {np.mean(all_corrs):.2f}")

    # Add Fubini-Study distance if available
    if fs_distance is not None:
        analysis_lines.append("")
        analysis_lines.append(r"**Decoherence Metric**:")
        analysis_lines.append(f"- Fubini-Study Dist.: {fs_distance:.3f} rad")

    # Add clustering results
    if num_qubits > 1:
        analysis_lines.append("")
        analysis_lines.append(r"**Qubit Clustering**:")
        for idx, cluster in enumerate(clusters):
            cluster_str = ", ".join([f"q{i}" for i in cluster])
            analysis_lines.append(f"- Cluster {idx + 1}: {cluster_str}")

    # Add symmetry analysis if enabled
    if config.get("symmetry_analysis"):
        if mode == "qasm":
            parity = compute_parity_distribution(correlation_data, num_qubits)
            su2_sym = compute_su2_symmetry(correlation_data, num_qubits, shots)
            analysis_lines.append("")
            analysis_lines.append(r"**Symmetry Analysis (QASM)**:")
            analysis_lines.append(
                f"- Parity (Even/Odd): {parity['even']:.2f}/{parity['odd']:.2f}"
            )
            analysis_lines.append(
                f"- SU(2) Symmetry (var): {su2_sym['su2_symmetry']:.2f}"
            )
        else:
            density_matrix = np.array(correlation_data["density"])
            su3_val = compute_su3_symmetry(density_matrix, num_qubits)
            analysis_lines.append("")
            analysis_lines.append(r"**Symmetry Analysis (Density)**:")
            analysis_lines.append(f"- Z-Symmetry Variance: {su3_val:.2f}")

    return analysis_lines


def plot_bloch_sphere_vectors(
    bloch_vectors: List[Dict[int, tuple]],
    time_steps: List[float],
    save_path: Optional[str],
    show_plot_nonblocking: Optional[Callable],
) -> bool:
    """Plot Bloch sphere trajectories."""
    from mpl_toolkits.mplot3d import Axes3D

    plot_closed_with_ctrl_c = False
    num_qubits = len(bloch_vectors[0])

    for qubit in range(num_qubits):

        def plot_func():
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection="3d")
            ax.set_title(f"Bloch Sphere Trajectory - Qubit {qubit}")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

            # Draw Bloch sphere
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            x = np.outer(np.cos(u), np.sin(v))
            y = np.outer(np.sin(u), np.sin(v))
            z = np.outer(np.ones(np.size(u)), np.cos(v))
            ax.plot_wireframe(x, y, z, color="gray", alpha=0.2)

            # Plot trajectory
            xs = [bv[qubit][0] for bv in bloch_vectors]
            ys = [bv[qubit][1] for bv in bloch_vectors]
            zs = [bv[qubit][2] for bv in bloch_vectors]
            ax.plot(xs, ys, zs, marker="o", label=f"Qubit {qubit}")

            # Add arrows
            for i in range(len(xs) - 1):
                ax.quiver(
                    xs[i],
                    ys[i],
                    zs[i],
                    xs[i + 1] - xs[i],
                    ys[i + 1] - ys[i],
                    zs[i + 1] - zs[i],
                    color="blue",
                    alpha=0.5,
                    arrow_length_ratio=0.1,
                )
            ax.legend()

        if save_path:
            plot_func()
            plt.savefig(
                f"{save_path}_bloch_qubit_{qubit}.png", bbox_inches="tight", dpi=300
            )
            logger.info(
                f"Saved Bloch sphere plot to {save_path}_bloch_qubit_{qubit}.png"
            )
            plt.close()
        else:
            print(f"Displaying Bloch sphere plot for qubit {qubit}...")
            if show_plot_nonblocking is not None:
                plot_closed_with_ctrl_c |= not show_plot_nonblocking(plot_func)
            else:
                plot_func()
                plt.show()

    return plot_closed_with_ctrl_c


def plot_fubini_study_distance(
    time_steps: List[float],
    fs_distances: List[float],
    save_path: Optional[str],
    show_plot_nonblocking: Optional[Callable],
) -> bool:
    """Plot Fubini-Study distance over time."""

    def plot_func():
        plt.figure(figsize=(8, 6))
        plt.plot(
            time_steps[1:],
            fs_distances,
            marker="o",
            label="Fubini-Study Distance",
            color="purple",
        )
        plt.xlabel("Time Step")
        plt.ylabel("Fubini-Study Distance (rad)")
        plt.title("Fubini-Study Distance Over Time")
        plt.legend()

    if save_path:
        plot_func()
        plt.savefig(f"{save_path}_fs_distance.png", dpi=300, bbox_inches="tight")
        logger.info(f"Saved Fubini-Study distance plot to {save_path}_fs_distance.png")
        plt.close()
        return False
    else:
        print("Displaying Fubini-Study distance plot...")
        if show_plot_nonblocking is not None:
            return not show_plot_nonblocking(plot_func)
        else:
            plot_func()
            plt.show()
            return False


def plot_error_transition_graph(
    counts_list: List[Dict],
    time_steps: List[float],
    save_path: str,
    show_plot_nonblocking: Optional[Callable],
) -> bool:
    """Plot error transition graph."""
    # Use analysis module for transition computation
    transition_analysis = compute_error_transitions(counts_list, time_steps)

    if "error" in transition_analysis:
        logger.warning(f"Error in transition analysis: {transition_analysis['error']}")
        return False

    G = transition_analysis["graph"]
    pos = nx.spring_layout(G)
    plot_closed_with_ctrl_c = False

    for t in time_steps[:-1]:

        def plot_transition():
            plt.figure(figsize=(10, 6))
            edges = [(u, v) for u, v, d in G.edges(data=True) if d["t"] == t]
            if not edges:
                plt.close()
                return
            weights = [G[u][v]["weight"] * 5 for u, v in edges]
            nx.draw_networkx_nodes(G, pos)
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=weights)
            nx.draw_networkx_labels(G, pos)
            plt.title(f"Error Transitions at t={t:.2f}")

        if save_path:
            plot_transition()
            plt.savefig(
                f"{save_path}_transition_t{t:.2f}.png", bbox_inches="tight", dpi=300
            )
            logger.info(
                f"Saved transition graph to {save_path}_transition_t{t:.2f}.png"
            )
            plt.close()
        else:
            print(f"Displaying error transition graph for t={t:.2f}...")
            if show_plot_nonblocking is not None:
                plot_closed_with_ctrl_c |= not show_plot_nonblocking(plot_transition)
            else:
                plot_transition()
                plt.show()

    return plot_closed_with_ctrl_c
