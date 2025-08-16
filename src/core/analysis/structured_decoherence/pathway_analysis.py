"""
High-Level Structured Decoherence Analysis

This module provides comprehensive analysis functions that combine all 5 
structured decoherence metrics for complete pathway characterization.

Usage:
    from src.core.analysis.structured_decoherence import compute_all_pathway_metrics
    
    metrics = compute_all_pathway_metrics(
        counts=measurement_data,
        state_type="GHZ", 
        num_qubits=3
    )
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

from .pathway_metrics import (
    compute_asymmetry_index,
    compute_pathway_concentration_ratio,
    compute_entanglement_error_correlation,
    compute_temporal_pathway_stability,
    compute_complexity_emergence_score,
)

logger = logging.getLogger("QuantumExperiment.Analysis.StructuredDecoherence")


def compute_all_pathway_metrics(counts: Dict[str, int], 
                               state_type: str = "GHZ",
                               num_qubits: Optional[int] = None,
                               historical_data: Optional[List[Dict[str, int]]] = None,
                               multi_qubit_data: Optional[Dict[int, Dict[str, int]]] = None) -> Dict[str, Any]:
    """
    Compute all 5 structured decoherence pathway metrics.
    
    This is the main function for structured decoherence analysis, computing
    all metrics needed for detecting non-random decoherence patterns.
    
    Args:
        counts: Current measurement outcomes (bitstring -> count)
        state_type: Quantum state type ("GHZ", "W", "BELL", "CLUSTER")  
        num_qubits: Number of qubits (auto-detected if None)
        historical_data: Previous measurement data for TPS calculation
        multi_qubit_data: Data across different qubit counts for CES calculation
        
    Returns:
        Dictionary containing all 5 pathway metrics plus analysis summary
    """
    if not counts:
        logger.warning("Empty counts provided for pathway analysis")
        return {}
    
    # Auto-detect number of qubits
    if num_qubits is None:
        first_bitstring = next(iter(counts.keys()))
        num_qubits = len(first_bitstring)
    
    logger.info(f"Computing structured decoherence metrics for {num_qubits}-qubit {state_type} state")
    
    # Compute core metrics
    metrics = {
        "asymmetry_index": compute_asymmetry_index(counts),
        "pathway_concentration_ratio": compute_pathway_concentration_ratio(counts),
        "entanglement_error_correlation": compute_entanglement_error_correlation(counts, state_type),
    }
    
    # Compute temporal stability if historical data available
    if historical_data:
        pathway_rankings = _extract_pathway_rankings([counts] + historical_data)
        metrics["temporal_pathway_stability"] = compute_temporal_pathway_stability(pathway_rankings)
    else:
        metrics["temporal_pathway_stability"] = None
        logger.debug("No historical data provided - TPS not computed")
    
    # Compute complexity emergence if multi-qubit data available  
    if multi_qubit_data:
        metrics["complexity_emergence_score"] = compute_complexity_emergence_score(multi_qubit_data)
    else:
        metrics["complexity_emergence_score"] = None
        logger.debug("No multi-qubit data provided - CES not computed")
    
    # Add metadata
    metrics["metadata"] = {
        "state_type": state_type,
        "num_qubits": num_qubits,
        "total_shots": sum(counts.values()),
        "unique_outcomes": len(counts),
        "analysis_timestamp": _get_timestamp(),
    }
    
    # Generate pathway analysis summary
    metrics["pathway_analysis"] = _generate_pathway_summary(metrics, counts, state_type)
    
    logger.info(f"Completed pathway analysis: AI={metrics['asymmetry_index']:.3f}, "
                f"PCR={metrics['pathway_concentration_ratio']:.3f}, "
                f"EEC={metrics['entanglement_error_correlation']:.3f}")
    
    return metrics


def analyze_decoherence_structure(counts: Dict[str, int],
                                state_type: str = "GHZ", 
                                confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """
    High-level analysis of decoherence structure with interpretation.
    
    Provides structured analysis of whether the decoherence exhibits
    statistically significant structured patterns vs. random behavior.
    
    Args:
        counts: Measurement outcomes  
        state_type: Quantum state type
        confidence_threshold: Threshold for detecting structured behavior
        
    Returns:
        Analysis results with structured/random classification
    """
    # Compute pathway metrics
    metrics = compute_all_pathway_metrics(counts, state_type)
    
    # Extract key indicators
    ai = metrics.get("asymmetry_index", 0)
    pcr = metrics.get("pathway_concentration_ratio", 1) 
    eec = metrics.get("entanglement_error_correlation", 0)
    
    # Determine if decoherence appears structured
    structure_indicators = []
    
    # High asymmetry suggests non-uniform patterns
    if ai > 0.3:
        structure_indicators.append("high_asymmetry")
    
    # High concentration suggests pathway preferences  
    if pcr > 2.0:
        structure_indicators.append("pathway_concentration")
        
    # Strong correlation suggests topology influence
    if abs(eec) > 0.5:
        structure_indicators.append("topology_correlation")
    
    # Calculate overall structure score
    structure_score = 0.0
    if ai > 0.2: structure_score += 0.4 * min(ai, 1.0)  
    if pcr > 1.5: structure_score += 0.3 * min(pcr/5.0, 1.0)
    if abs(eec) > 0.3: structure_score += 0.3 * abs(eec)
    
    # Classification
    is_structured = structure_score > confidence_threshold
    confidence = structure_score
    
    analysis = {
        "classification": "structured" if is_structured else "random",
        "confidence": confidence,
        "structure_score": structure_score,
        "indicators": structure_indicators,
        "metrics": metrics,
        "interpretation": _generate_interpretation(metrics, is_structured, structure_indicators),
    }
    
    logger.info(f"Decoherence analysis: {analysis['classification']} "
                f"(confidence: {confidence:.3f})")
    
    return analysis


def _extract_pathway_rankings(data_sequence: List[Dict[str, int]]) -> List[List[str]]:
    """Extract pathway rankings from sequence of measurement data."""
    rankings = []
    
    for counts in data_sequence:
        # Sort bitstrings by frequency (most frequent first)
        sorted_outcomes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ranking = [bitstring for bitstring, _ in sorted_outcomes]
        rankings.append(ranking)
    
    return rankings


def _generate_pathway_summary(metrics: Dict[str, Any], 
                            counts: Dict[str, int],
                            state_type: str) -> Dict[str, Any]:
    """Generate human-readable pathway analysis summary."""
    total_shots = sum(counts.values())
    
    # Find most frequent pathways
    sorted_outcomes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_pathways = sorted_outcomes[:min(5, len(sorted_outcomes))]
    
    # Calculate pathway probabilities
    pathway_probs = [(bitstring, count/total_shots) for bitstring, count in top_pathways]
    
    summary = {
        "dominant_pathways": pathway_probs,
        "pathway_concentration": f"Top 25% pathways contain {metrics['pathway_concentration_ratio']:.1f}x more events than bottom 25%",
        "asymmetry_level": _classify_asymmetry(metrics["asymmetry_index"]),
        "entanglement_influence": _classify_correlation(metrics["entanglement_error_correlation"]),
        "total_outcomes": len(counts),
        "measurement_shots": total_shots,
    }
    
    return summary


def _classify_asymmetry(ai: float) -> str:
    """Classify asymmetry level."""
    if ai < 0.1:
        return "very_uniform"
    elif ai < 0.3:
        return "slight_asymmetry" 
    elif ai < 0.6:
        return "moderate_asymmetry"
    else:
        return "high_asymmetry"


def _classify_correlation(eec: float) -> str:
    """Classify entanglement-error correlation."""
    abs_eec = abs(eec)
    if abs_eec < 0.2:
        return "no_correlation"
    elif abs_eec < 0.5:
        return "weak_correlation"
    elif abs_eec < 0.8:
        return "moderate_correlation"
    else:
        return "strong_correlation"


def _generate_interpretation(metrics: Dict[str, Any], 
                           is_structured: bool,
                           indicators: List[str]) -> str:
    """Generate natural language interpretation of results."""
    if is_structured:
        interpretation = "Analysis indicates STRUCTURED decoherence patterns. "
        
        if "high_asymmetry" in indicators:
            interpretation += "Error distribution shows significant deviation from uniform randomness. "
            
        if "pathway_concentration" in indicators:
            interpretation += "Errors are concentrated in preferred pathways. "
            
        if "topology_correlation" in indicators:
            interpretation += "Error patterns correlate with entanglement topology. "
            
        interpretation += "This supports the hypothesis of non-random decoherence pathways."
        
    else:
        interpretation = "Analysis indicates RANDOM decoherence patterns. "
        interpretation += "Error distribution appears consistent with stochastic decoherence. "
        interpretation += "No clear evidence of structured pathway preferences detected."
    
    return interpretation


def _get_timestamp() -> str:
    """Get current timestamp for analysis metadata."""
    from datetime import datetime
    return datetime.now().isoformat()