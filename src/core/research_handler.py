"""
Research-grade experiment handler with comprehensive analysis and JSON output.

This module provides enterprise-level experiment handling specifically designed
for structured decoherence research, including full metric computation,
statistical validation, and publication-ready JSON output.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

import numpy as np
from qiskit.result import Counts

from .analysis.information_theory import compute_research_metrics
from .analysis.decoherence import compute_fubini_study_distance
from .analysis.correlations import compute_pairwise_correlations
from ..experiments.presets.ghz_structured_decoherence import get_ideal_ghz_distribution

logger = logging.getLogger("QuantumExperiment.ResearchHandler")


class ResearchExperimentHandler:
    """
    Research-grade experiment handler for structured decoherence studies.

    This class provides comprehensive analysis capabilities including:
    - Information-theoretic metrics (entropy, KL divergence, mutual information)
    - Decoherence analysis (Fubini-Study distance, bias detection)
    - Statistical validation (convergence testing, reproducibility)
    - Publication-ready JSON output with full metadata
    """

    def __init__(self, results_dir: str = "results"):
        """
        Initialize the research experiment handler.

        Args:
            results_dir: Directory to save research results
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

        # Create subdirectories for organized results
        (self.results_dir / "structured_decoherence").mkdir(exist_ok=True)
        (self.results_dir / "parameter_sweeps").mkdir(exist_ok=True)
        (self.results_dir / "convergence_tests").mkdir(exist_ok=True)

        logger.info(f"Research handler initialized with results directory: {self.results_dir}")

    def process_experiment_result(self,
                                circuit: Any,
                                result: Any,
                                experiment_config: Dict[str, Any],
                                experiment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a quantum experiment result with comprehensive research analysis.

        Args:
            circuit: Qiskit quantum circuit
            result: Qiskit experiment result
            experiment_config: Experiment configuration parameters
            experiment_id: Unique experiment identifier

        Returns:
            Comprehensive research analysis dictionary
        """
        if experiment_id is None:
            experiment_id = str(uuid.uuid4())

        logger.info(f"Processing research experiment: {experiment_id}")

        # Extract experiment parameters first
        num_qubits = experiment_config.get('num_qubits', 3)

        # Extract counts from result with better debugging
        logger.debug(f"Result type: {type(result)}")
        logger.debug(f"Result has get_counts: {hasattr(result, 'get_counts')}")

        try:
            if hasattr(result, 'get_counts'):
                counts_raw = result.get_counts()
                logger.debug(f"Counts from get_counts(): {type(counts_raw)}")
            elif isinstance(result, dict) and 'counts' in result:
                # The result is a dict with a 'counts' key containing the actual Counts object
                counts_obj = result['counts']
                counts_raw = dict(counts_obj)  # Convert Counts to dict
                logger.debug(f"Extracted counts from result dict: {type(counts_raw)}")
            elif isinstance(result, dict):
                counts_raw = result
                logger.debug(f"Using result as dict directly")
            else:
                # Try direct conversion of Counts object
                counts_raw = dict(result)
                logger.debug(f"Converted Counts to dict: {type(counts_raw)}")
        except Exception as e:
            logger.error(f"Failed to extract counts: {e}")
            return {}

        # Convert to string keys for consistency
        logger.debug(f"Raw counts type: {type(counts_raw)}")
        logger.debug(f"Raw counts sample: {list(counts_raw.items())[:3] if hasattr(counts_raw, 'items') else 'not iterable'}")

        # Handle different count formats
        counts = {}
        try:
            for key, value in counts_raw.items():
                logger.debug(f"Processing key={key} (type: {type(key)}), value={value} (type: {type(value)})")

                # Ensure key is a proper bitstring
                if isinstance(key, int):
                    # Convert integer to bitstring
                    key_str = format(key, f'0{num_qubits}b')
                else:
                    key_str = str(key)

                # Ensure value is an integer - handle Counts objects as values
                try:
                    if hasattr(value, 'item'):  # numpy scalar
                        value_int = int(value.item())
                    elif isinstance(value, (int, float)):
                        value_int = int(value)
                    elif hasattr(value, '__int__'):
                        value_int = int(value)
                    else:
                        # If it's a Counts object or similar, skip this problematic entry
                        logger.warning(f"Skipping problematic value type: {type(value)} for key {key}")
                        continue

                    counts[key_str] = value_int

                except (ValueError, TypeError) as ve:
                    logger.warning(f"Could not convert value {value} (type: {type(value)}) to int for key {key}: {ve}")
                    continue

        except Exception as e:
            logger.error(f"Failed to process counts: {e}")
            # Try alternative approach - maybe the result itself is the counts
            try:
                if hasattr(counts_raw, 'binary_probabilities'):
                    # Alternative Qiskit counts format
                    for bitstring, count in counts_raw.binary_probabilities().items():
                        counts[bitstring] = int(count * sum(counts_raw.values()))
                elif hasattr(counts_raw, 'most_frequent'):
                    # Another alternative - just get the most frequent outcome for now
                    most_frequent = counts_raw.most_frequent(1)[0]
                    counts[most_frequent[0]] = most_frequent[1]
                else:
                    logger.error(f"Could not extract counts from {type(counts_raw)}")
                    return {}
            except Exception as e2:
                logger.error(f"Alternative count extraction failed: {e2}")
                return {}

        state_type = experiment_config.get('state_type', 'GHZ')
        noise_type = experiment_config.get('noise_type', 'DEPOLARIZING')
        error_rate = experiment_config.get('error_rate', 0.05)
        shots = experiment_config.get('shots', 1024)

        # Create comprehensive analysis
        analysis = {
            "experiment_metadata": {
                "experiment_id": experiment_id,
                "timestamp": datetime.now().isoformat(),
                "framework_version": "2.0.0",
                "research_type": experiment_config.get('research_type', 'structured_decoherence')
            },

            "experiment_parameters": {
                "num_qubits": num_qubits,
                "state_type": state_type,
                "noise_type": noise_type,
                "noise_enabled": experiment_config.get('noise_enabled', True),
                "error_rate": error_rate,
                "shots": shots,
                "sim_mode": experiment_config.get('sim_mode', 'qasm'),
                "multiple_runs": experiment_config.get('multiple_runs', 1),
            },

            "circuit_statistics": {
                "depth": circuit.depth() if hasattr(circuit, 'depth') else 0,
                "num_gates": len(circuit.data) if hasattr(circuit, 'data') else 0,
                "num_qubits": circuit.num_qubits if hasattr(circuit, 'num_qubits') else num_qubits,
                "gate_types": self._count_gate_types(circuit) if hasattr(circuit, 'data') else {}
            },

            "measurement_results": {
                "raw_counts": counts,
                "total_shots": sum(counts.values()),
                "unique_outcomes": len(counts),
                "outcome_probabilities": self._compute_probabilities(counts)
            }
        }

        # Add comprehensive research metrics
        ideal_counts = None
        if state_type.upper() == 'GHZ':
            ideal_dist = get_ideal_ghz_distribution(num_qubits)
            total_shots = sum(counts.values())
            ideal_counts = {k: int(v * total_shots) for k, v in ideal_dist.items()}

        research_metrics = compute_research_metrics(
            counts=counts,
            ideal_counts=ideal_counts,
            num_qubits=num_qubits
        )

        analysis["research_metrics"] = research_metrics

        # Add decoherence-specific analysis
        if ideal_counts:
            analysis["decoherence_analysis"] = self._compute_decoherence_metrics(
                counts, ideal_counts, experiment_config
            )

        # Add statistical validation
        analysis["statistical_validation"] = self._compute_statistical_validation(
            counts, experiment_config
        )

        # Add research insights
        analysis["research_insights"] = self._generate_research_insights(
            analysis, experiment_config
        )

        logger.info(f"Research analysis completed for experiment: {experiment_id}")
        return analysis

    def save_research_result(self, analysis: Dict[str, Any],
                           filename: Optional[str] = None) -> str:
        """
        Save research analysis to a JSON file with organized directory structure.

        Args:
            analysis: Complete research analysis dictionary
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if filename is None:
            exp_id = analysis["experiment_metadata"]["experiment_id"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            research_type = analysis["experiment_metadata"].get("research_type", "experiment")
            filename = f"{research_type}_{exp_id[:8]}_{timestamp}.json"

        # Determine subdirectory based on research type
        research_type = analysis["experiment_metadata"].get("research_type", "experiment")
        if "sweep" in research_type or "batch" in research_type:
            subdir = "parameter_sweeps"
        elif "convergence" in research_type:
            subdir = "convergence_tests"
        else:
            subdir = "structured_decoherence"

        filepath = self.results_dir / subdir / filename

        # Save with pretty formatting for readability
        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"Research results saved to: {filepath}")
        return str(filepath)

    def _compute_probabilities(self, counts: Dict[str, int]) -> Dict[str, float]:
        """Compute normalized probability distribution from counts."""
        total = sum(counts.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in counts.items()}

    def _count_gate_types(self, circuit) -> Dict[str, int]:
        """Count the types of gates in the circuit."""
        gate_counts = {}
        if hasattr(circuit, 'data'):
            for instruction, _, _ in circuit.data:
                gate_name = instruction.name
                gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
        return gate_counts

    def _compute_decoherence_metrics(self,
                                   observed_counts: Dict[str, int],
                                   ideal_counts: Dict[str, int],
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Compute decoherence-specific metrics for structured decoherence research."""

        # Compute deviation from ideal distribution
        deviations = {}
        total_observed = sum(observed_counts.values())
        total_ideal = sum(ideal_counts.values())

        all_outcomes = set(observed_counts.keys()) | set(ideal_counts.keys())

        for outcome in all_outcomes:
            obs_prob = observed_counts.get(outcome, 0) / total_observed
            ideal_prob = ideal_counts.get(outcome, 0) / total_ideal
            deviations[outcome] = obs_prob - ideal_prob

        # Identify patterns in deviations
        error_bitstrings = {k: v for k, v in deviations.items()
                           if k not in ['000', '111'] and abs(v) > 0.001}

        return {
            "probability_deviations": deviations,
            "error_bitstring_frequencies": error_bitstrings,
            "max_deviation": max(abs(v) for v in deviations.values()),
            "total_error_probability": sum(observed_counts.get(k, 0) for k in error_bitstrings.keys()) / total_observed,
            "structured_vs_random": self._assess_structure_vs_randomness(error_bitstrings)
        }

    def _compute_statistical_validation(self,
                                      counts: Dict[str, int],
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Compute statistical validation metrics."""
        total_shots = sum(counts.values())
        num_outcomes = len(counts)

        # Basic statistical measures
        validation = {
            "shot_count_adequacy": {
                "total_shots": total_shots,
                "recommended_min_shots": num_outcomes * 100,  # Rule of thumb
                "adequacy_ratio": total_shots / (num_outcomes * 100),
                "adequate": total_shots >= num_outcomes * 100
            },
            "sampling_quality": {
                "outcome_coverage": num_outcomes / (2 ** config.get('num_qubits', 3)),
                "min_count_per_outcome": min(counts.values()) if counts else 0,
                "max_count_per_outcome": max(counts.values()) if counts else 0,
            }
        }

        # Confidence intervals for main outcomes (simplified)
        if 'num_qubits' in config and config['num_qubits'] == 3:
            for outcome in ['000', '111']:
                if outcome in counts:
                    p = counts[outcome] / total_shots
                    # Simple binomial confidence interval
                    std_err = np.sqrt(p * (1 - p) / total_shots)
                    validation[f"{outcome}_confidence_interval"] = {
                        "point_estimate": p,
                        "standard_error": std_err,
                        "ci_95_lower": max(0, p - 1.96 * std_err),
                        "ci_95_upper": min(1, p + 1.96 * std_err)
                    }

        return validation

    def _assess_structure_vs_randomness(self, error_bitstrings: Dict[str, float]) -> Dict[str, Any]:
        """Assess whether error patterns show structure vs pure randomness."""
        if not error_bitstrings:
            return {"assessment": "insufficient_data", "confidence": 0.0}

        # Simple heuristics for structure detection
        error_probs = list(error_bitstrings.values())

        # Check for uniform distribution (random-like)
        mean_error = np.mean(error_probs)
        std_error = np.std(error_probs)
        cv = std_error / mean_error if mean_error > 0 else 0

        # Structure indicators
        structure_indicators = {
            "coefficient_of_variation": cv,
            "uniformity_score": 1 - cv,  # High uniformity suggests randomness
            "pattern_concentration": max(error_probs) / sum(error_probs) if sum(error_probs) > 0 else 0,
        }

        # Simple classification
        if cv < 0.3:
            assessment = "uniform_random_like"
            confidence = 0.7
        elif structure_indicators["pattern_concentration"] > 0.4:
            assessment = "structured_patterns_detected"
            confidence = 0.8
        else:
            assessment = "mixed_patterns"
            confidence = 0.5

        return {
            "assessment": assessment,
            "confidence": confidence,
            "indicators": structure_indicators
        }

    def _generate_research_insights(self,
                                  analysis: Dict[str, Any],
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research insights and interpretations."""
        insights = {
            "key_findings": [],
            "research_questions_addressed": [],
            "recommendations": []
        }

        # Extract key metrics for insight generation
        metrics = analysis.get("research_metrics", {})
        info_theory = metrics.get("information_theory", {})
        qubit_analysis = metrics.get("qubit_analysis", {})

        # Shannon entropy insights
        entropy = info_theory.get("shannon_entropy", 0)
        normalized_entropy = info_theory.get("normalized_entropy", 0)

        if normalized_entropy < 0.8:
            insights["key_findings"].append(
                f"Low normalized entropy ({normalized_entropy:.3f}) suggests structured outcomes rather than random decoherence"
            )
        elif normalized_entropy > 0.95:
            insights["key_findings"].append(
                f"High normalized entropy ({normalized_entropy:.3f}) indicates near-random decoherence patterns"
            )

        # Qubit bias insights
        qubit_biases = qubit_analysis.get("qubit_wise_bias", {})
        if qubit_biases:
            max_bias = max(abs(v) for v in qubit_biases.values())
            if max_bias > 0.1:
                insights["key_findings"].append(
                    f"Significant qubit bias detected (max: {max_bias:.3f}), suggesting asymmetric decoherence"
                )

        # Decoherence pattern insights
        decoherence = analysis.get("decoherence_analysis", {})
        structure_assessment = decoherence.get("structured_vs_random", {})

        if structure_assessment.get("assessment") == "structured_patterns_detected":
            insights["key_findings"].append(
                "Structured decoherence patterns detected - supports hypothesis of non-random quantum noise"
            )
            insights["research_questions_addressed"].append(
                "Evidence found for structured rather than purely stochastic decoherence"
            )

        # Generate recommendations
        total_shots = analysis["measurement_results"]["total_shots"]
        if total_shots < 4096:
            insights["recommendations"].append(
                "Increase shot count to ≥4096 for improved statistical significance"
            )

        error_rate = config.get("error_rate", 0.05)
        if error_rate > 0.15:
            insights["recommendations"].append(
                "Consider lower noise levels for better structure detection"
            )

        return insights


# Convenience function for quick research analysis
def analyze_research_experiment(circuit, result, config, experiment_id=None) -> Dict[str, Any]:
    """
    Quick function to analyze a research experiment with full metrics.

    Args:
        circuit: Qiskit quantum circuit
        result: Experiment result
        config: Experiment configuration
        experiment_id: Optional experiment ID

    Returns:
        Complete research analysis dictionary
    """
    handler = ResearchExperimentHandler()
    return handler.process_experiment_result(circuit, result, config, experiment_id)
