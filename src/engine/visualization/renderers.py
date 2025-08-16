"""
Research-focused visualization renderers.

Each renderer is a plugin that can create specific types of visualizations
from quantum experiment data.
"""

import logging
from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import numpy as np

from .service import VisualizationRenderer
from src.engine.models import ArtifactRef

logger = logging.getLogger(__name__)


class HistogramRenderer(VisualizationRenderer):
    """
    Renders measurement count histograms optimized for research analysis.
    
    Features:
    - Clean, publication-ready styling
    - Research metrics annotations (when available)
    - Pathway analysis highlighting
    """
    
    def can_render(self, viz_type: str, data: Dict[str, Any]) -> bool:
        """Check if this is a histogram request with measurement counts."""
        if viz_type != "histogram":
            return False
            
        # Check for measurement counts in various possible locations
        analysis = data.get("analysis", {})
        measurement_results = analysis.get("measurement_results", {})
        
        counts = (
            measurement_results.get("raw_counts") or
            measurement_results.get("outcome_probabilities") or
            data.get("counts")  # Direct counts
        )
        
        return counts is not None and len(counts) > 0
    
    def render(self, data: Dict[str, Any], output_path: str) -> ArtifactRef:
        """Render research-focused histogram."""
        # Extract data
        analysis = data.get("analysis", {})
        measurement_results = analysis.get("measurement_results", {})
        experiment_params = analysis.get("experiment_parameters", {})
        
        # Get counts (try multiple locations for flexibility)
        counts = (
            measurement_results.get("raw_counts") or
            measurement_results.get("outcome_probabilities") or  
            data.get("counts")
        )
        
        if not counts:
            raise ValueError("No measurement counts found in data")
            
        # Extract research metrics if available
        research_metrics = data.get("structured_decoherence_metrics")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data for plotting
        bitstrings = list(counts.keys())
        values = list(counts.values())
        
        # Sort by bitstring for consistent ordering
        sorted_data = sorted(zip(bitstrings, values))
        bitstrings, values = zip(*sorted_data)
        
        # Create bar plot
        bars = ax.bar(range(len(bitstrings)), values, 
                     alpha=0.8, color='steelblue', edgecolor='navy', linewidth=0.5)
        
        # Customize appearance
        ax.set_xlabel('Measurement Outcomes', fontsize=12, fontweight='bold')
        ax.set_ylabel('Counts', fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(bitstrings)))
        ax.set_xticklabels(bitstrings, rotation=45 if len(bitstrings) > 8 else 0)
        
        # Create title with experiment info
        title_parts = []
        if experiment_params.get("state_type"):
            title_parts.append(f"{experiment_params['state_type']} State")
        if experiment_params.get("num_qubits"):
            title_parts.append(f"({experiment_params['num_qubits']} qubits)")
        if experiment_params.get("noise_enabled"):
            noise_type = experiment_params.get("noise_type", "Unknown")
            error_rate = experiment_params.get("error_rate", 0)
            title_parts.append(f"{noise_type} noise (p={error_rate:.3f})")
            
        title = " - ".join(title_parts) if title_parts else "Measurement Results"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Add research metrics annotation if available
        if research_metrics:
            metrics_text = []
            if research_metrics.get("asymmetry_index") is not None:
                ai = research_metrics["asymmetry_index"]
                metrics_text.append(f"AI: {ai:.3f}")
            if research_metrics.get("pathway_concentration_ratio") is not None:
                pcr = research_metrics["pathway_concentration_ratio"]  
                metrics_text.append(f"PCR: {pcr:.3f}")
            if research_metrics.get("entanglement_error_correlation") is not None:
                eec = research_metrics["entanglement_error_correlation"]
                metrics_text.append(f"EEC: {eec:.3f}")
                
            if metrics_text:
                metrics_str = " | ".join(metrics_text)
                ax.text(0.02, 0.98, f"Research Metrics: {metrics_str}", 
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                       facecolor='lightgray', alpha=0.8))
        
        # Highlight dominant pathways if this looks like structured decoherence
        if research_metrics and research_metrics.get("pathway_concentration_ratio", 1) > 2:
            # Highlight top pathways
            sorted_by_value = sorted(enumerate(values), key=lambda x: x[1], reverse=True)
            top_indices = [idx for idx, _ in sorted_by_value[:2]]  # Top 2 pathways
            
            for idx in top_indices:
                bars[idx].set_color('orange')
                bars[idx].set_alpha(1.0)
                bars[idx].set_edgecolor('darkorange')
                bars[idx].set_linewidth(2.0)
        
        # Improve layout
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # Save figure
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        logger.info(f"Saved research histogram to {output_path}")
        
        # Create artifact reference
        return ArtifactRef(
            kind="histogram",
            path=str(output_path),
            metadata={
                "renderer": "HistogramRenderer",
                "experiment_type": experiment_params.get("state_type"),
                "num_outcomes": len(counts),
                "total_shots": sum(counts.values()) if isinstance(list(counts.values())[0], (int, float)) else None,
                "has_research_metrics": research_metrics is not None
            }
        )