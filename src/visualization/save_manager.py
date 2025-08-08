"""
Centralized save path management for visualizations.

This module provides consistent, organized file saving across all visualization types.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class VisualizationSaveManager:
    """
    Manages save paths and file organization for quantum experiment visualizations.

    Creates organized directory structure:
    visualizations/
    ├── histograms/
    ├── density_matrices/
    ├── hypergraphs/
    ├── animations/
    └── research_outputs/
    """

    def __init__(self, base_dir: str = "results/visualizations"):
        """
        Initialize the save manager.

        Args:
            base_dir: Base directory for all visualizations
        """
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        subdirs = [
            "histograms",
            "density_matrices",
            "hypergraphs",
            "animations",
            "research_outputs",
            "bloch_spheres",
            "correlations"
        ]

        for subdir in subdirs:
            (self.base_dir / subdir).mkdir(parents=True, exist_ok=True)

    def get_save_path(self,
                     viz_type: str,
                     experiment_config: Optional[Dict[str, Any]] = None,
                     custom_name: Optional[str] = None,
                     extension: str = "png") -> str:
        """
        Generate an organized save path for a visualization.

        Args:
            viz_type: Type of visualization ('histogram', 'density_matrix', 'hypergraph', etc.)
            experiment_config: Experiment configuration for filename generation
            custom_name: Custom filename (overrides automatic generation)
            extension: File extension (default: 'png')

        Returns:
            Full path for saving the visualization
        """
        # Map visualization types to directories
        type_mapping = {
            'histogram': 'histograms',
            'density_matrix': 'density_matrices',
            'hypergraph': 'hypergraphs',
            'animation': 'animations',
            'bloch_sphere': 'bloch_spheres',
            'correlation': 'correlations',
            'research': 'research_outputs'
        }

        # Get the appropriate subdirectory
        subdir = type_mapping.get(viz_type, 'research_outputs')
        save_dir = self.base_dir / subdir

        # Generate filename
        if custom_name:
            filename = f"{custom_name}.{extension}"
        else:
            filename = self._generate_filename(viz_type, experiment_config, extension)

        return str(save_dir / filename)

    def _generate_filename(self,
                          viz_type: str,
                          config: Optional[Dict[str, Any]] = None,
                          extension: str = "png") -> str:
        """
        Generate a descriptive filename based on experiment configuration.

        Args:
            viz_type: Type of visualization
            config: Experiment configuration
            extension: File extension

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not config:
            return f"{viz_type}_{timestamp}.{extension}"

        # Extract key parameters for filename
        state_type = config.get('state_type', 'unknown')
        noise_type = config.get('noise_type', 'no_noise')
        num_qubits = config.get('num_qubits', 'N')
        noise_enabled = config.get('noise_enabled', False)

        # Build descriptive filename
        parts = [
            viz_type,
            f"{state_type}_{num_qubits}q",
        ]

        if noise_enabled and noise_type:
            error_rate = config.get('error_rate', '')
            if error_rate:
                parts.append(f"{noise_type}_{error_rate}")
            else:
                parts.append(noise_type)
        else:
            parts.append("ideal")

        parts.append(timestamp)

        filename = "_".join(str(part).lower().replace(' ', '_') for part in parts)
        return f"{filename}.{extension}"

    def get_directory_info(self) -> Dict[str, Any]:
        """
        Get information about the visualization directory structure.

        Returns:
            Dictionary with directory statistics
        """
        info = {
            'base_directory': str(self.base_dir),
            'subdirectories': {},
            'total_files': 0
        }

        for subdir in self.base_dir.iterdir():
            if subdir.is_dir():
                file_count = len(list(subdir.glob("*.*")))
                info['subdirectories'][subdir.name] = {
                    'path': str(subdir),
                    'file_count': file_count
                }
                info['total_files'] += file_count

        return info

    def clean_old_files(self, days_old: int = 30, viz_type: Optional[str] = None) -> int:
        """
        Clean up old visualization files.

        Args:
            days_old: Remove files older than this many days
            viz_type: Specific visualization type to clean (None for all)

        Returns:
            Number of files removed
        """
        import time

        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0

        # Determine which directories to clean
        if viz_type:
            type_mapping = {
                'histogram': 'histograms',
                'density_matrix': 'density_matrices',
                'hypergraph': 'hypergraphs',
                'animation': 'animations',
                'bloch_sphere': 'bloch_spheres',
                'correlation': 'correlations',
                'research': 'research_outputs'
            }
            dirs_to_clean = [self.base_dir / type_mapping.get(viz_type, viz_type)]
        else:
            dirs_to_clean = [d for d in self.base_dir.iterdir() if d.is_dir()]

        for directory in dirs_to_clean:
            if not directory.exists():
                continue

            for file_path in directory.glob("*.*"):
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        removed_count += 1
                    except OSError:
                        pass  # Skip files that can't be deleted

        return removed_count


# Global save manager instance
_save_manager = None


def get_save_manager() -> VisualizationSaveManager:
    """Get the global save manager instance (singleton pattern)."""
    global _save_manager
    if _save_manager is None:
        _save_manager = VisualizationSaveManager()
    return _save_manager


def get_organized_save_path(viz_type: str,
                           experiment_config: Optional[Dict[str, Any]] = None,
                           custom_name: Optional[str] = None,
                           extension: str = "png") -> str:
    """
    Convenience function to get an organized save path.

    Args:
        viz_type: Type of visualization
        experiment_config: Experiment configuration
        custom_name: Custom filename
        extension: File extension

    Returns:
        Organized save path
    """
    return get_save_manager().get_save_path(
        viz_type=viz_type,
        experiment_config=experiment_config,
        custom_name=custom_name,
        extension=extension
    )
