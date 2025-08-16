"""
Research Integration Module

Bridge between engine API and core structured decoherence analysis.
Provides clean integration for computing research metrics.
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

from src.engine.models.config import ExperimentConfig
from src.engine.models.research import StructuredDecoherenceMetrics, AnalysisMetadata, PathwayAnalysis
from src.core.analysis.structured_decoherence.pathway_metrics import (
    compute_asymmetry_index,
    compute_pathway_concentration_ratio,
    compute_entanglement_error_correlation,
)

logger = logging.getLogger(__name__)


def extract_counts_from_result(raw_result: Any) -> Dict[str, int]:
    """
    Extract measurement counts from various Qiskit result formats.
    
    Args:
        raw_result: Raw result from quantum experiment
        
    Returns:
        Dictionary of {bitstring: count} pairs
    """
    try:
        if hasattr(raw_result, "get_counts"):
            counts_raw = raw_result.get_counts()
            return dict(counts_raw)
        elif isinstance(raw_result, dict) and "counts" in raw_result:
            counts_obj = raw_result["counts"]
            return dict(counts_obj)
        elif isinstance(raw_result, dict) and "density_matrix" in raw_result:
            # For density matrix results, we cannot directly extract counts
            # This would require a different analysis approach
            logger.warning("Density matrix results not supported for structured decoherence metrics")
            return {}
        else:
            logger.error(f"Unsupported result format: {type(raw_result)}")
            return {}
    except Exception as e:
        logger.error(f"Failed to extract counts from result: {e}")
        return {}


def compute_research_metrics(
    counts: Dict[str, int],
    config: ExperimentConfig
) -> Optional[StructuredDecoherenceMetrics]:
    """
    Compute structured decoherence metrics if enabled.
    
    Args:
        counts: Measurement counts as {bitstring: count} pairs
        config: Experiment configuration
        
    Returns:
        StructuredDecoherenceMetrics if research enabled, None otherwise
    """
    if not config.enable_research_metrics:
        return None
        
    if config.research_type != "structured_decoherence":
        logger.warning(f"Research type '{config.research_type}' not supported for structured decoherence metrics")
        return None
        
    if not counts:
        logger.warning("No measurement counts available for research metrics")
        return None
        
    try:
        logger.info("Computing structured decoherence metrics")
        
        # Compute the 5 core metrics
        ai = compute_asymmetry_index(counts)
        pcr = compute_pathway_concentration_ratio(counts)
        eec = compute_entanglement_error_correlation(counts, config.state_type)
        
        # TPS and CES require multiple experiments or time series data
        # For single experiments, these are set to None
        tps = None  # Would need multiple noise levels
        ces = None  # Would need multiple system sizes or complexity levels
        
        # Create analysis metadata
        total_shots = sum(counts.values())
        unique_outcomes = len(counts)
        
        metadata = AnalysisMetadata(
            state_type=config.state_type,
            num_qubits=config.num_qubits,
            total_shots=total_shots,
            unique_outcomes=unique_outcomes,
            analysis_timestamp=datetime.now().isoformat(),
            noise_conditions=_extract_noise_conditions(config)
        )
        
        # Create pathway analysis
        pathway_analysis = _create_pathway_analysis(counts, ai, pcr, eec)
        
        # Create structured decoherence metrics
        metrics = StructuredDecoherenceMetrics(
            asymmetry_index=ai,
            pathway_concentration_ratio=pcr,
            entanglement_error_correlation=eec,
            temporal_pathway_stability=tps,
            complexity_emergence_score=ces,
            metadata=metadata,
            pathway_analysis=pathway_analysis
        )
        
        logger.info(f"Research metrics computed: AI={ai:.4f}, PCR={pcr:.4f}, EEC={eec:.4f}")
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to compute research metrics: {e}")
        return None


def _extract_noise_conditions(config: ExperimentConfig) -> Optional[Dict[str, Any]]:
    """Extract noise conditions from config for metadata."""
    if not config.noise_enabled:
        return None
        
    conditions = {
        "noise_type": config.noise_type,
        "error_rate": config.error_rate,
    }
    
    # Add additional noise parameters if present
    if config.z_prob is not None:
        conditions["z_prob"] = config.z_prob
    if config.i_prob is not None:
        conditions["i_prob"] = config.i_prob
    if config.t1 is not None:
        conditions["t1"] = config.t1
    if config.t2 is not None:
        conditions["t2"] = config.t2
        
    return conditions


def _create_pathway_analysis(
    counts: Dict[str, int], 
    ai: float, 
    pcr: float, 
    eec: float
) -> PathwayAnalysis:
    """Create human-readable pathway analysis."""
    total_shots = sum(counts.values())
    
    # Get dominant pathways (sorted by frequency)
    sorted_outcomes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    dominant_pathways = [
        [bitstring, count / total_shots] 
        for bitstring, count in sorted_outcomes[:5]  # Top 5 pathways
    ]
    
    # Qualitative assessments based on metrics (using enum values)
    if pcr > 5.0:
        pathway_concentration = "very_high"
    elif pcr > 2.0:
        pathway_concentration = "high"
    elif pcr > 1.5:
        pathway_concentration = "moderate"
    elif pcr > 1.1:
        pathway_concentration = "low"
    else:
        pathway_concentration = "very_low"
        
    if ai > 1.0:
        asymmetry_level = "high_asymmetry"
    elif ai > 0.5:
        asymmetry_level = "moderate_asymmetry"
    elif ai > 0.2:
        asymmetry_level = "slight_asymmetry"
    else:
        asymmetry_level = "very_uniform"
        
    if eec > 0.5:
        entanglement_influence = "strong_correlation"
    elif eec > 0.2:
        entanglement_influence = "moderate_correlation"
    elif eec > 0.05:
        entanglement_influence = "weak_correlation"
    else:
        entanglement_influence = "no_correlation"
    
    return PathwayAnalysis(
        dominant_pathways=dominant_pathways,
        pathway_concentration=pathway_concentration,
        asymmetry_level=asymmetry_level,
        entanglement_influence=entanglement_influence,
        total_outcomes=len(counts),
        measurement_shots=total_shots
    )