# src/visualization/backends/__init__.py

"""
Multi-backend visualization system.

Supports different visualization libraries through a unified interface.
Backends: matplotlib, plotly, bokeh, manim (for animations), mayavi (3D)
"""

from typing import Dict, Callable, Any, Optional
import logging

logger = logging.getLogger("QuantumExperiment.Visualization.Backends")


class BackendRegistry:
    """Registry for different visualization backends."""

    def __init__(self):
        self._backends: Dict[str, Dict[str, Callable]] = {}
        self._active_backend = "matplotlib"  # Default

    def register_backend(self, name: str, functions: Dict[str, Callable]):
        """Register a new visualization backend."""
        self._backends[name] = functions
        logger.info(f"Registered visualization backend: {name}")

    def set_active_backend(self, name: str):
        """Set the active visualization backend."""
        if name not in self._backends:
            raise ValueError(f"Backend '{name}' not registered. Available: {list(self._backends.keys())}")
        self._active_backend = name
        logger.info(f"Switched to visualization backend: {name}")

    def get_function(self, func_name: str, backend: Optional[str] = None) -> Callable:
        """Get a visualization function from specified or active backend."""
        backend = backend or self._active_backend

        if backend not in self._backends:
            raise ValueError(f"Backend '{backend}' not available")

        if func_name not in self._backends[backend]:
            # Fallback to matplotlib if function not available in current backend
            if backend != "matplotlib" and "matplotlib" in self._backends:
                logger.warning(f"Function '{func_name}' not available in '{backend}', falling back to matplotlib")
                return self._backends["matplotlib"].get(func_name)
            raise ValueError(f"Function '{func_name}' not available in backend '{backend}'")

        return self._backends[backend][func_name]

    def list_backends(self) -> Dict[str, list]:
        """List all available backends and their functions."""
        return {name: list(funcs.keys()) for name, funcs in self._backends.items()}


# Global registry instance
backend_registry = BackendRegistry()


def get_backend_registry() -> BackendRegistry:
    """Get the global backend registry."""
    return backend_registry


def set_visualization_backend(backend: str):
    """Convenience function to set visualization backend."""
    backend_registry.set_active_backend(backend)
