# src/visualization/histogram.py

import matplotlib.pyplot as plt
import os
import numpy as np
from typing import Optional, Dict, List
import logging
from natsort import natsorted  # For natural sorting of basis states

logger = logging.getLogger("QuantumExperiment.Visualization")


def get_quantum_color_scheme(states: List[str], state_type: str, num_qubits: int, noise_enabled: bool) -> List[str]:
    """
    Generate quantum-aware color scheme highlighting expected quantum states.

    Args:
        states: List of basis states (e.g., ['000', '001', '010', ...])
        state_type: Type of quantum state ('GHZ', 'W', 'CLUSTER', etc.)
        num_qubits: Number of qubits in the system
        noise_enabled: Whether noise is applied

    Returns:
        List of colors for each state
    """
    if not state_type:
        # Default coloring for unknown states
        return ['red' if noise_enabled else 'blue'] * len(states)

    state_type = state_type.upper()
    colors = []

    for state in states:
        if state_type == "GHZ":
            # Highlight GHZ expected states |000⟩ and |111⟩
            if state in ['000', '111'][:num_qubits]:  # Handle different qubit counts
                colors.append('#1f77b4' if not noise_enabled else '#d62728')  # Deep blue/red for expected
            else:
                colors.append('#ff7f0e' if noise_enabled else '#aec7e8')  # Orange/light blue for errors

        elif state_type == "W":
            # Highlight W state components (single excitations: |001⟩, |010⟩, |100⟩)
            w_states = [format(1 << i, f'0{num_qubits}b') for i in range(num_qubits)]
            if state in w_states:
                colors.append('#2ca02c' if not noise_enabled else '#d62728')  # Green for W components
            else:
                colors.append('#ff7f0e' if noise_enabled else '#98df8a')  # Orange/light green for errors

        elif state_type == "CLUSTER":
            # For cluster states, all computational basis states should have equal probability
            colors.append('#9467bd' if not noise_enabled else '#ff7f0e')  # Purple for uniform, orange for noise

        elif state_type == "BELL":
            # Bell states: |00⟩ and |11⟩ for Φ+, or |01⟩ and |10⟩ for Ψ+
            if state in ['00', '11']:
                colors.append('#17becf' if not noise_enabled else '#d62728')  # Cyan for Bell components
            else:
                colors.append('#ff7f0e' if noise_enabled else '#9edae5')  # Orange/light cyan for errors

        else:
            # Default quantum coloring
            colors.append('#1f77b4' if not noise_enabled else '#d62728')

    return colors


def get_ideal_quantum_distribution(state_type: str, num_qubits: int) -> Dict[str, float]:
    """
    Get the ideal probability distribution for a given quantum state type.

    Args:
        state_type: Type of quantum state
        num_qubits: Number of qubits

    Returns:
        Dictionary of state -> probability
    """
    if not state_type:
        return {}

    state_type = state_type.upper()
    total_states = 2 ** num_qubits

    if state_type == "GHZ":
        # GHZ state: equal superposition of |000...0⟩ and |111...1⟩
        ideal = {}
        all_zero = '0' * num_qubits
        all_one = '1' * num_qubits
        for i in range(total_states):
            state = format(i, f'0{num_qubits}b')
            if state == all_zero or state == all_one:
                ideal[state] = 0.5
            else:
                ideal[state] = 0.0
        return ideal

    elif state_type == "W":
        # W state: equal superposition of all single-excitation states
        ideal = {}
        w_states = [format(1 << i, f'0{num_qubits}b') for i in range(num_qubits)]
        prob_per_state = 1.0 / num_qubits
        for i in range(total_states):
            state = format(i, f'0{num_qubits}b')
            if state in w_states:
                ideal[state] = prob_per_state
            else:
                ideal[state] = 0.0
        return ideal

    elif state_type == "CLUSTER":
        # Cluster state: equal superposition of all computational basis states
        prob_per_state = 1.0 / total_states
        return {format(i, f'0{num_qubits}b'): prob_per_state for i in range(total_states)}

    elif state_type == "BELL":
        # Bell state: equal superposition of |00⟩ and |11⟩ (for Φ+)
        ideal = {}
        for i in range(total_states):
            state = format(i, f'0{num_qubits}b')
            if state in ['00', '11'] and num_qubits == 2:
                ideal[state] = 0.5
            else:
                ideal[state] = 0.0
        return ideal

    return {}


def plot_histogram(
    counts: Dict[str, int],
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    noise_enabled: Optional[bool] = None,
    save_path: Optional[str] = None,
    min_occurrences: int = 0,
    num_qubits: Optional[int] = None,
    research_metrics: Optional[Dict] = None,  # Add research metrics
    show_ideal: bool = True,  # Show ideal distribution comparison
) -> None:
    """
    Plots a histogram of quantum measurement results.

    Args:
        counts (Dict[str, int]): Dictionary of measurement outcomes.
        state_type (str, optional): Quantum state type (e.g., GHZ, W, CLUSTER).
        noise_type (str, optional): Noise model used (e.g., DEPOLARIZING).
        noise_enabled (bool, optional): Whether noise was applied.
        save_path (str, optional): File path to save the plot.
        min_occurrences (int): Minimum occurrences to display.
        num_qubits (int, optional): Number of qubits in the system.
    """
    if counts is None:
        logger.warning("Counts object is None. No data to plot.")
        return

    # Ensure counts is a dictionary of numeric values
    try:
        counts = dict(counts)
    except TypeError:
        logger.error("Counts object could not be converted to a dictionary.")
        return

    # Filter counts based on min_occurrences
    filtered_counts = {
        k: int(v)
        for k, v in counts.items()
        if isinstance(v, (int, float)) and v >= min_occurrences
    }

    if not filtered_counts:
        logger.warning("No outcomes meet the minimum occurrences threshold.")
        return

    # Sort the basis states in natural order (e.g., 000, 001, ..., 111)
    states = natsorted(filtered_counts.keys())
    occurrences = [filtered_counts[state] for state in states]

    # Compute total shots for probability calculation
    total_shots = sum(occurrences)
    probabilities = [count / total_shots for count in occurrences]

    # Determine number of qubits if not provided
    if num_qubits is None:
        num_qubits = len(states[0]) if states else 1

    # Get quantum-aware colors
    colors = get_quantum_color_scheme(states, state_type, num_qubits, noise_enabled or False)

    # Create the histogram with enhanced layout
    plt.figure(figsize=(12, 8))

    # Create main histogram
    bars = plt.bar(
        states,
        probabilities,
        color=colors,
        alpha=0.8,
        edgecolor='black',
        linewidth=0.5
    )

    # Add ideal distribution comparison if requested and available
    if show_ideal and state_type and not (noise_enabled and noise_type):
        ideal_dist = get_ideal_quantum_distribution(state_type, num_qubits)
        if ideal_dist:
            ideal_probs = [ideal_dist.get(state, 0) for state in states]
            plt.plot(states, ideal_probs, 'k--', linewidth=2, alpha=0.7,
                    label=f'Ideal {state_type}', marker='o', markersize=4)

    # Add counts as labels above the bars
    for bar, count in zip(bars, occurrences):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{count}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # Set labels and enhanced title with research metrics
    plt.xlabel("Basis State", fontsize=12)
    plt.ylabel("Probability", fontsize=12)

    # Enhanced title with research metrics
    title = f"{state_type or 'Quantum'} State Distribution ({num_qubits} qubits, {total_shots} shots)"
    if noise_enabled and noise_type:
        title += f"\nwith {noise_type} Noise"
    else:
        title += "\n(Ideal, No Noise)"

    # Add research metrics to title if available
    if research_metrics:
        info_theory = research_metrics.get('information_theory', {})
        shannon_entropy = info_theory.get('shannon_entropy', 0)
        normalized_entropy = info_theory.get('normalized_entropy', 0)
        title += f" | H = {shannon_entropy:.3f} (norm: {normalized_entropy:.3f})"

    plt.title(title, fontsize=14, pad=20)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True, which="both", linestyle="--", alpha=0.3)

    # Add legend if ideal distribution is shown
    if show_ideal and state_type and not (noise_enabled and noise_type):
        plt.legend(loc='upper right')

    # Add research metadata text box
    if research_metrics:
        info_theory = research_metrics.get('information_theory', {})
        qubit_analysis = research_metrics.get('qubit_analysis', {})
        distribution_comparison = research_metrics.get('distribution_comparison', {})

        metadata_text = ""
        if 'shannon_entropy' in info_theory:
            metadata_text += f"Shannon Entropy: {info_theory['shannon_entropy']:.4f}\n"
        if 'normalized_entropy' in info_theory:
            metadata_text += f"Normalized H: {info_theory['normalized_entropy']:.4f}\n"
        if 'kl_divergence' in distribution_comparison:
            metadata_text += f"KL Divergence: {distribution_comparison['kl_divergence']:.4f}\n"
        if 'total_variation_distance' in distribution_comparison:
            metadata_text += f"TV Distance: {distribution_comparison['total_variation_distance']:.4f}"

        if metadata_text:
            plt.text(0.98, 0.98, metadata_text.strip(), transform=plt.gca().transAxes,
                    ha='right', va='top', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))

    # Adjust layout for better spacing
    plt.tight_layout()

    # Save or display the plot
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        logger.info(
            f"Saved histogram to {save_path} (states: {len(states)}, total shots: {total_shots})"
        )
        plt.close()
    else:
        plt.show()
