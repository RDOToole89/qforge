# src/visualization/density_matrix.py

import matplotlib.pyplot as plt
import numpy as np
import os
from qiskit.quantum_info import DensityMatrix
from typing import Optional, Dict
import logging

logger = logging.getLogger("QuantumExperiment.Visualization")


def get_quantum_colormap(state_type: str, show_real: bool, show_imag: bool) -> str:
    """
    Get quantum-optimized colormap based on state type and component.

    Args:
        state_type: Type of quantum state
        show_real: Whether showing real part
        show_imag: Whether showing imaginary part

    Returns:
        Colormap name optimized for quantum data
    """
    if show_imag:
        return 'hsv'  # Circular colormap for phases
    elif show_real:
        return 'RdBu_r'  # Diverging colormap for real parts (emphasizes coherence)
    else:
        # Absolute value colormaps based on state type
        if state_type and state_type.upper() == 'GHZ':
            return 'plasma'  # Good for entangled states with high contrast
        elif state_type and state_type.upper() == 'W':
            return 'viridis'  # Perceptually uniform for W states
        elif state_type and state_type.upper() == 'CLUSTER':
            return 'inferno'  # High contrast for cluster states
        else:
            return 'viridis'  # Default perceptually uniform


def compute_quantum_metrics(density_matrix: DensityMatrix) -> Dict[str, float]:
    """
    Compute quantum-specific metrics from density matrix.

    Args:
        density_matrix: Qiskit DensityMatrix object

    Returns:
        Dictionary of quantum metrics
    """
    dm = density_matrix.data

    # Purity: Tr(ρ²)
    purity = np.trace(dm @ dm).real

    # Trace: Tr(ρ) (should be 1 for valid density matrix)
    trace = np.trace(dm).real

    # Von Neumann entropy: -Tr(ρ log₂(ρ))
    eigenvalues = np.linalg.eigvals(dm)
    eigenvalues = eigenvalues[eigenvalues > 1e-12]  # Remove numerical zeros
    von_neumann_entropy = -np.sum(eigenvalues * np.log2(eigenvalues)).real

    # Linear entropy: 1 - Tr(ρ²)
    linear_entropy = 1 - purity

    # Participation ratio: 1 / Tr(ρ²)
    participation_ratio = 1 / purity if purity > 1e-12 else float('inf')

    return {
        'purity': purity,
        'trace': trace,
        'von_neumann_entropy': von_neumann_entropy,
        'linear_entropy': linear_entropy,
        'participation_ratio': participation_ratio
    }


def plot_density_matrix(
    density_matrix: DensityMatrix,
    cmap: str = "viridis",
    show_real: bool = False,
    show_imag: bool = False,
    save_path: Optional[str] = None,
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    research_metrics: Optional[Dict] = None,
    show_quantum_metrics: bool = True,
) -> None:
    """
    Plots a heatmap of the density matrix with basis state labels.

    Args:
        density_matrix (DensityMatrix): Density matrix to plot.
        cmap (str, optional): Colormap for visualization.
        show_real (bool, optional): Show real part.
        show_imag (bool, optional): Show imaginary part.
        save_path (str, optional): File path to save the plot.
        state_type (str, optional): Quantum state type (e.g., GHZ, W, CLUSTER).
        noise_type (str, optional): Noise applied (e.g., DEPOLARIZING).
    """
    if density_matrix is None or not isinstance(density_matrix, DensityMatrix):
        logger.warning("No valid density matrix available to plot.")
        return

    # Extract the density matrix data as a numpy array
    dm_array = (
        np.real(density_matrix.data)
        if show_real
        else (np.imag(density_matrix.data) if show_imag else np.abs(density_matrix.data))
    )

    # Use quantum-optimized colormap if not explicitly specified
    if cmap == "viridis":  # Default was not changed
        cmap = get_quantum_colormap(state_type, show_real, show_imag)

    # Determine the number of qubits from the matrix size (2^n x 2^n)
    num_qubits = int(np.log2(dm_array.shape[0]))
    basis_states = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
    basis_labels = [f"|{state}⟩" for state in basis_states]

    # Compute quantum metrics if requested
    quantum_metrics = compute_quantum_metrics(density_matrix) if show_quantum_metrics else {}

    # Plot the heatmap with enhanced layout
    plt.figure(figsize=(12, 10))
    im = plt.imshow(dm_array, cmap=cmap, interpolation="nearest")

    # Highlight entangled blocks for specific states
    if state_type and state_type.upper() == 'GHZ' and not show_real and not show_imag:
        # Add visual emphasis for GHZ coherence terms
        # Draw rectangles around expected non-zero blocks
        from matplotlib.patches import Rectangle
        ax = plt.gca()
        # Highlight |000⟩⟨111| and |111⟩⟨000| coherence terms
        if num_qubits == 3:  # For 3-qubit GHZ
            # |000⟩⟨111| term at (0, 7)
            rect1 = Rectangle((6.5, -0.5), 1, 1, linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect1)
            # |111⟩⟨000| term at (7, 0)
            rect2 = Rectangle((-0.5, 6.5), 1, 1, linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect2)

    # Add colorbar with appropriate label
    colorbar_label = (
        "Real Part" if show_real
        else "Imaginary Part" if show_imag
        else "Absolute Value"
    )
    plt.colorbar(im, label=colorbar_label)

    # Set enhanced title with quantum metrics
    component_type = (
        "Real Part" if show_real
        else "Imaginary Part" if show_imag
        else "Magnitude"
    )

    title = f"Density Matrix - {component_type}"
    if state_type:
        title += f" ({state_type} State)"
    if noise_type:
        title += f" with {noise_type} Noise"

    # Add quantum metrics to title
    if quantum_metrics:
        purity = quantum_metrics.get('purity', 0)
        von_neumann = quantum_metrics.get('von_neumann_entropy', 0)
        title += f"\nPurity = {purity:.4f}, S = {von_neumann:.3f}"

    plt.title(title, fontsize=14, pad=20)

    # Set enhanced axis labels and ticks
    plt.xlabel("Basis State ⟨j|", fontsize=12)
    plt.ylabel("Basis State |i⟩", fontsize=12)
    plt.xticks(ticks=range(len(basis_labels)), labels=basis_labels, rotation=45, ha="right", fontsize=10)
    plt.yticks(ticks=range(len(basis_labels)), labels=basis_labels, fontsize=10)

    # Add research metrics text box
    if quantum_metrics or research_metrics:
        metadata_text = ""

        # Quantum metrics from density matrix
        if quantum_metrics:
            metadata_text += f"Purity: {quantum_metrics['purity']:.5f}\n"
            metadata_text += f"Trace: {quantum_metrics['trace']:.5f}\n"
            metadata_text += f"Von Neumann Entropy: {quantum_metrics['von_neumann_entropy']:.4f}\n"
            metadata_text += f"Linear Entropy: {quantum_metrics['linear_entropy']:.5f}\n"
            if quantum_metrics['participation_ratio'] != float('inf'):
                metadata_text += f"Participation Ratio: {quantum_metrics['participation_ratio']:.3f}\n"

        # Research metrics if available
        if research_metrics:
            info_theory = research_metrics.get('information_theory', {})
            if 'shannon_entropy' in info_theory:
                metadata_text += f"\nMeasurement Shannon H: {info_theory['shannon_entropy']:.4f}"
            if 'kl_divergence' in research_metrics.get('distribution_comparison', {}):
                kl_div = research_metrics['distribution_comparison']['kl_divergence']
                metadata_text += f"\nKL Divergence: {kl_div:.4f}"

        if metadata_text:
            plt.text(0.98, 0.02, metadata_text.strip(), transform=plt.gca().transAxes,
                    ha='right', va='bottom', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray'))

    # Add interpretation text for quantum states
    if state_type and quantum_metrics:
        purity = quantum_metrics.get('purity', 0)
        interpretation = ""

        if purity > 0.99:
            interpretation = "Pure quantum state"
        elif purity > 0.8:
            interpretation = "Mostly coherent state"
        elif purity > 0.5:
            interpretation = "Partially mixed state"
        else:
            interpretation = "Highly mixed state"

        if state_type.upper() == 'GHZ' and purity > 0.9:
            interpretation += " (strong entanglement)"
        elif state_type.upper() == 'W' and purity > 0.9:
            interpretation += " (symmetric entanglement)"

        plt.text(0.02, 0.98, interpretation, transform=plt.gca().transAxes,
                ha='left', va='top', fontsize=10, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))

    # Add grid to separate basis states
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, color="gray")
    plt.minorticks_on()
    plt.tight_layout()

    # Save or display the plot
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        logger.info(f"Saved density matrix plot to {save_path} (dimensions: {dm_array.shape})")
        plt.close()
    elif state_type:  # Auto-generate organized save path
        from .save_manager import get_organized_save_path
        experiment_config = {
            'state_type': state_type,
            'noise_type': noise_type,
            'num_qubits': int(np.log2(dm_array.shape[0]))
        }
        auto_save_path = get_organized_save_path(
            viz_type='density_matrix',
            experiment_config=experiment_config
        )
        plt.savefig(auto_save_path, bbox_inches="tight", dpi=300)
        logger.info(f"Density matrix auto-saved to {auto_save_path} (dimensions: {dm_array.shape})")
        plt.close()
    else:
        plt.show()
