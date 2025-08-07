"""
Visualization module with smart matplotlib backend configuration.

This module provides lazy loading for visualization components and intelligent
backend selection based on the environment (CLI vs. server/backend).
"""

import os
import sys
from typing import Optional, Callable, Any

# Configure matplotlib backend before any imports
def configure_matplotlib_backend() -> None:
    """
    Configure matplotlib backend based on environment.

    - CLI mode: Use interactive backend (TkAgg) for plots
    - Server/backend mode: Use non-interactive backend (Agg) for reliability
    """
    # Check if we're in interactive mode
    interactive_mode = (
        os.environ.get('QUANTUM_INTERACTIVE', '').lower() in ('true', '1', 'yes') or
        (hasattr(sys, 'ps1') and sys.ps1) or  # Interactive Python shell
        (hasattr(sys, 'gettrace') and sys.gettrace()) or  # Debugger
        'ipython' in sys.modules or  # IPython
        'jupyter' in sys.modules  # Jupyter
    )

    # Check if we have a display
    has_display = (
        os.environ.get('DISPLAY') is not None or
        os.environ.get('WAYLAND_DISPLAY') is not None or
        sys.platform == 'darwin'  # macOS always has display
    )

    # Determine backend
    if interactive_mode and has_display:
        backend = 'TkAgg'  # Interactive backend
        # Note: Backend configured for interactive mode
    else:
        backend = 'Agg'  # Non-interactive backend
        # Note: Backend configured for non-interactive mode

    # Set the backend
    os.environ['MPLBACKEND'] = backend

# Configure backend immediately
configure_matplotlib_backend()

# Lazy loading functions for visualization components
def get_visualization_handler() -> Callable:
    """Get visualization handler (lazy import)."""
    from .visualization_handler import VisualizationHandler
    return VisualizationHandler

def get_visualizer() -> Callable:
    """Get main visualizer class (lazy import)."""
    from .visualizer import Visualizer
    return Visualizer

def get_hypergraph_visualizer() -> Callable:
    """Get hypergraph visualizer (lazy import)."""
    from .hypergraph import plot_hypergraph
    return plot_hypergraph

def get_histogram_visualizer() -> Callable:
    """Get histogram visualizer (lazy import)."""
    from .histogram import plot_histogram
    return plot_histogram

def get_density_matrix_visualizer() -> Callable:
    """Get density matrix visualizer (lazy import)."""
    from .density_matrix import plot_density_matrix
    return plot_density_matrix

# Convenience function to get all visualizers
def get_all_visualizers() -> dict:
    """Get all visualization functions (lazy import)."""
    return {
        'hypergraph': get_hypergraph_visualizer(),
        'histogram': get_histogram_visualizer(),
        'density_matrix': get_density_matrix_visualizer(),
    }

# Export main functions and classes
__all__ = [
    'configure_matplotlib_backend',
    'get_visualization_handler',
    'get_visualizer',
    'get_hypergraph_visualizer',
    'get_histogram_visualizer',
    'get_density_matrix_visualizer',
    'get_all_visualizers',
]
