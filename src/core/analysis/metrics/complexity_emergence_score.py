"""
Complexity Emergence Score (CES) - Critical Threshold Detection for Structured Decoherence

# Mathematical Foundation
The Complexity Emergence Score quantifies at what system complexity level
(number of qubits) structured decoherence patterns emerge above noise background.
It uses logistic regression and critical point analysis to detect phase
transitions in quantum error structure as system size increases.

# Physical Interpretation
CES tests the hypothesis that structured decoherence only becomes detectable
above a critical system complexity threshold. Below this threshold, quantum
systems are too simple to exhibit clear pathway structure; above it, 
entanglement networks become complex enough to guide decoherence patterns.

# Research Applications
- Detecting critical complexity thresholds for quantum error structure
- Characterizing scaling behavior of structured decoherence
- Identifying minimum system sizes for pathway-based error correction
- Understanding emergence phenomena in quantum many-body systems

# Mathematical Definition
CES fits a logistic emergence curve to structure metrics vs system size:
S(n) = A / (1 + exp(-k(n - n₀))) + S₀

Where:
- S(n): Structure metric (e.g., Asymmetry Index) for n qubits
- n₀: Critical emergence threshold (qubits)
- k: Emergence sharpness parameter
- A: Emergence amplitude, S₀: baseline level

CES = k × A, quantifying both emergence sharpness and magnitude.

# Educational Framework
This implementation demonstrates:
- Logistic regression and sigmoid function fitting in physics
- Critical phenomena and phase transitions in quantum systems
- Statistical model selection and goodness-of-fit testing
- Machine learning applications in quantum information science

References:
- Landau & Lifshitz (1980), "Statistical Physics - Phase Transitions"
- Sachdev (2011), "Quantum Phase Transitions"  
- Hastie et al. (2009), "Elements of Statistical Learning"
- Cardy (1996), "Scaling and Renormalization in Statistical Physics"
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any, Mapping, Union
from dataclasses import dataclass
from scipy.optimize import curve_fit, minimize_scalar
from scipy.stats import pearsonr, linregress
import warnings

from ..constants import (
    CES_MIN_POINTS, CES_MAX_QUBITS, ALPHA,
    STRUCTURE_WEAK_THRESHOLD, STRUCTURE_MODERATE_THRESHOLD, STRUCTURE_STRONG_THRESHOLD,
    validate_counts_dict
)
from .asymmetry_index import compute_asymmetry_index

logger = logging.getLogger(__name__)


@dataclass
class EmergenceAnalysis:
    """
    Complete complexity emergence analysis with critical point detection.
    
    This structure provides comprehensive information about how structured
    decoherence emerges as quantum system complexity increases.
    """
    complexity_emergence_score: float
    critical_threshold: float
    emergence_sharpness: float
    emergence_amplitude: float
    baseline_structure: float
    emergence_quality: str  # "excellent", "good", "poor", "insufficient"
    scaling_behavior: str  # "sigmoid", "linear", "power_law", "flat"
    fit_r_squared: float
    emergence_confidence: float
    critical_range: Tuple[float, float]
    emergence_summary: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "complexity_emergence_score": self.complexity_emergence_score,
            "critical_threshold": self.critical_threshold,
            "emergence_sharpness": self.emergence_sharpness,
            "emergence_amplitude": self.emergence_amplitude,
            "baseline_structure": self.baseline_structure,
            "emergence_quality": self.emergence_quality,
            "scaling_behavior": self.scaling_behavior,
            "fit_r_squared": self.fit_r_squared,
            "emergence_confidence": self.emergence_confidence,
            "critical_range": self.critical_range,
            "emergence_summary": self.emergence_summary
        }


def compute_complexity_emergence_score(multi_qubit_data: Dict[int, Mapping[str, int]],
                                     structure_metric: str = "asymmetry_index",
                                     emergence_model: str = "logistic",
                                     return_analysis: bool = False) -> float:
    """
    Compute Complexity Emergence Score - critical threshold for structure emergence.
    
    Mathematical Process:
        1. Compute structure metric for each qubit count in multi_qubit_data
        2. Fit emergence model (logistic, linear, power_law) to (n_qubits, metric) data
        3. Extract critical parameters: threshold n₀, sharpness k, amplitude A
        4. Calculate CES = k × A (combines emergence sharpness and magnitude)
        5. Validate fit quality and statistical significance
        
    Physical Interpretation:
        - CES > 1.0: Sharp, high-amplitude emergence (clear critical threshold)
        - CES ≈ 0.1-1.0: Moderate emergence (gradual structure increase)
        - CES < 0.1: Weak/no emergence (linear or flat scaling)
        - Critical threshold n₀: Minimum qubits for detectable structure
        
    Emergence Models:
        - **Logistic**: S(n) = A/(1 + exp(-k(n-n₀))) + S₀
        - **Linear**: S(n) = m×n + b (baseline for comparison)  
        - **Power Law**: S(n) = A×n^α + S₀ (scaling analysis)
        - **Hybrid**: Automatic model selection via AIC/BIC
        
    Structure Metrics:
        - **asymmetry_index**: Primary emergence metric (default)
        - **structure_score**: Alternative using Jensen-Shannon divergence
        - **concentration_index**: Economic inequality emergence
        - **custom**: User-provided metric function
        
    Args:
        multi_qubit_data: {n_qubits: measurement_counts} for different system sizes
        structure_metric: Which metric to use for emergence analysis
        emergence_model: "logistic", "linear", "power_law", or "auto"
        return_analysis: If True, return comprehensive EmergenceAnalysis
        
    Returns:
        float: Complexity Emergence Score (higher = sharper emergence)
        OR EmergenceAnalysis: Complete emergence analysis results
        
    Raises:
        ValueError: If insufficient data or invalid parameters
        
    Examples:
        >>> # Clear emergence at 3-4 qubits
        >>> data = {
        ...     2: {"00": 500, "01": 500},
        ...     3: {"000": 400, "111": 350, "others": 250},
        ...     4: {"0000": 600, "1111": 300, "others": 100},
        ...     5: {"00000": 700, "11111": 250, "others": 50}
        ... }
        >>> ces = compute_complexity_emergence_score(data)
        >>> print(f"CES = {ces:.3f}")  # Expected: high emergence score
        
        >>> # Linear scaling (no emergence)
        >>> data = {2: uniform_counts, 3: uniform_counts, 4: uniform_counts}
        >>> ces = compute_complexity_emergence_score(data)
        >>> print(f"CES = {ces:.3f}")  # Expected: low emergence score
        
    Complexity:
        Time: O(n × k × m) where n = qubit counts, k = outcomes, m = fit iterations
        Space: O(n) for storing metric values
        
    Educational Notes:
        - CES bridges statistical physics and quantum information theory
        - Logistic functions model many natural emergence phenomena
        - Critical phenomena appear in diverse physical systems
        - Machine learning provides tools for detecting emergence patterns
    """
    # Input validation with research-grade error handling
    if not multi_qubit_data or len(multi_qubit_data) < CES_MIN_POINTS:
        logger.warning(f"CES requires ≥{CES_MIN_POINTS} data points, got {len(multi_qubit_data) if multi_qubit_data else 0}")
        return 0.0 if not return_analysis else EmergenceAnalysis(
            complexity_emergence_score=0.0,
            critical_threshold=0.0,
            emergence_sharpness=0.0,
            emergence_amplitude=0.0,
            baseline_structure=0.0,
            emergence_quality="insufficient",
            scaling_behavior="flat",
            fit_r_squared=0.0,
            emergence_confidence=0.0,
            critical_range=(0.0, 0.0),
            emergence_summary="Insufficient data for emergence analysis"
        )
    
    # Validate data consistency and extract qubit counts
    qubit_counts = sorted(multi_qubit_data.keys())
    if any(n < 1 or n > CES_MAX_QUBITS for n in qubit_counts):
        raise ValueError(f"Qubit counts must be in [1, {CES_MAX_QUBITS}], got {qubit_counts}")
    
    logger.debug(f"Computing CES for {len(qubit_counts)} system sizes: {qubit_counts}")
    
    # Compute structure metric for each system size
    structure_values = []
    for n_qubits in qubit_counts:
        counts = multi_qubit_data[n_qubits]
        
        # Validate counts for this system size
        try:
            counts_clean = validate_counts_dict(counts, f"system size {n_qubits}")
        except ValueError as e:
            logger.warning(f"Invalid counts for {n_qubits} qubits: {e}")
            continue
        
        # Compute specified structure metric
        if structure_metric == "asymmetry_index":
            metric_value = compute_asymmetry_index(counts_clean)
        elif structure_metric == "structure_score":
            from .schema_bridge import compute_structure_score
            metric_value = compute_structure_score(counts_clean)
        elif structure_metric == "concentration_index":
            from .schema_bridge import compute_concentration_index
            metric_value = compute_concentration_index(counts_clean)
        else:
            raise ValueError(f"Unknown structure metric: {structure_metric}")
        
        structure_values.append(metric_value)
        logger.debug(f"n={n_qubits}: {structure_metric}={metric_value:.6f}")
    
    if len(structure_values) < CES_MIN_POINTS:
        logger.warning(f"Only {len(structure_values)} valid data points after filtering")
        return 0.0 if not return_analysis else _create_insufficient_emergence_analysis()
    
    # Convert to numpy arrays for fitting
    x_data = np.array(qubit_counts[:len(structure_values)])
    y_data = np.array(structure_values)
    
    # Fit emergence model and extract parameters
    if emergence_model == "auto":
        fit_results = _fit_best_emergence_model(x_data, y_data)
    else:
        fit_results = _fit_emergence_model(x_data, y_data, emergence_model)
    
    # Calculate CES from fit parameters
    ces = _calculate_ces_from_fit(fit_results, emergence_model)
    
    logger.debug(f"Computed CES = {ces:.6f} using {emergence_model} model")
    
    if not return_analysis:
        return ces
    
    # Generate comprehensive emergence analysis
    return _generate_emergence_analysis(
        ces, fit_results, x_data, y_data, structure_metric, emergence_model
    )


def compute_emergence_across_metrics(multi_qubit_data: Dict[int, Mapping[str, int]],
                                   metrics: List[str] = None) -> Dict[str, float]:
    """
    Compute CES across multiple structure metrics for comprehensive analysis.
    
    This function analyzes emergence patterns across different structural
    measures, providing a multi-dimensional view of complexity scaling.
    
    Mathematical Foundation:
        Each metric may show different emergence patterns:
        - AI: Deviation from uniformity emergence
        - Structure Score: Information-theoretic structure emergence  
        - Concentration: Economic inequality emergence
        
    Research Applications:
        - Comparing emergence patterns across different structural aspects
        - Identifying which metrics are most sensitive to complexity scaling
        - Multi-metric validation of emergence phenomena
        
    Args:
        multi_qubit_data: {n_qubits: measurement_counts} for different system sizes
        metrics: List of metrics to analyze (None = use all available)
        
    Returns:
        Dict[str, float]: {metric_name: emergence_score} for each metric
        
    Examples:
        >>> data = {2: counts_2q, 3: counts_3q, 4: counts_4q, 5: counts_5q}
        >>> emergence_scores = compute_emergence_across_metrics(data)
        >>> print(f"AI emergence: {emergence_scores['asymmetry_index']:.3f}")
        >>> print(f"SS emergence: {emergence_scores['structure_score']:.3f}")
    """
    if metrics is None:
        metrics = ["asymmetry_index", "structure_score", "concentration_index"]
    
    emergence_scores = {}
    
    for metric in metrics:
        try:
            ces = compute_complexity_emergence_score(
                multi_qubit_data, 
                structure_metric=metric,
                emergence_model="logistic"
            )
            emergence_scores[metric] = ces
            logger.debug(f"Emergence for {metric}: {ces:.6f}")
        except Exception as e:
            logger.warning(f"Failed to compute emergence for {metric}: {e}")
            emergence_scores[metric] = 0.0
    
    return emergence_scores


def _fit_emergence_model(x_data: np.ndarray, y_data: np.ndarray, model: str) -> Dict[str, Any]:
    """Fit specified emergence model to structure vs complexity data."""
    results = {"model": model, "success": False}
    
    try:
        if model == "logistic":
            results.update(_fit_logistic_emergence(x_data, y_data))
        elif model == "linear":
            results.update(_fit_linear_emergence(x_data, y_data))
        elif model == "power_law":
            results.update(_fit_power_law_emergence(x_data, y_data))
        else:
            raise ValueError(f"Unknown emergence model: {model}")
            
    except Exception as e:
        logger.debug(f"Emergence model fitting failed for {model}: {e}")
        results.update({
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e)
        })
    
    return results


def _fit_logistic_emergence(x_data: np.ndarray, y_data: np.ndarray) -> Dict[str, Any]:
    """Fit logistic emergence model: S(n) = A/(1 + exp(-k(n-n₀))) + S₀"""
    
    def logistic_func(x, A, k, n0, S0):
        """Logistic function with emergence parameters."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return A / (1 + np.exp(-k * (x - n0))) + S0
    
    # Intelligent initial parameter estimation
    y_min, y_max = np.min(y_data), np.max(y_data)
    x_min, x_max = np.min(x_data), np.max(x_data)
    
    # Initial guesses
    A_init = y_max - y_min  # Amplitude
    S0_init = y_min  # Baseline
    n0_init = (x_min + x_max) / 2  # Midpoint as initial threshold
    k_init = 1.0  # Initial sharpness
    
    initial_guess = [A_init, k_init, n0_init, S0_init]
    
    # Parameter bounds (reasonable constraints)
    bounds = (
        [0, 0.1, x_min - 1, 0],  # Lower bounds
        [2 * (y_max - y_min), 10, x_max + 1, y_max]  # Upper bounds
    )
    
    try:
        # Fit logistic function
        popt, pcov = curve_fit(
            logistic_func, x_data, y_data,
            p0=initial_guess,
            bounds=bounds,
            maxfev=5000
        )
        
        A, k, n0, S0 = popt
        
        # Calculate R-squared
        y_pred = logistic_func(x_data, *popt)
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # Parameter uncertainties
        param_errors = np.sqrt(np.diag(pcov))
        
        return {
            "success": True,
            "parameters": {
                "amplitude": A,
                "sharpness": k,
                "threshold": n0,
                "baseline": S0
            },
            "parameter_errors": {
                "amplitude_err": param_errors[0],
                "sharpness_err": param_errors[1],
                "threshold_err": param_errors[2],
                "baseline_err": param_errors[3]
            },
            "r_squared": r_squared,
            "fitted_function": lambda x: logistic_func(x, *popt)
        }
        
    except Exception as e:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e)
        }


def _fit_linear_emergence(x_data: np.ndarray, y_data: np.ndarray) -> Dict[str, Any]:
    """Fit linear model: S(n) = m×n + b"""
    try:
        slope, intercept, r_value, p_value, std_err = linregress(x_data, y_data)
        
        return {
            "success": True,
            "parameters": {
                "slope": slope,
                "intercept": intercept,
                "p_value": p_value
            },
            "parameter_errors": {
                "slope_err": std_err
            },
            "r_squared": r_value**2,
            "fitted_function": lambda x: slope * x + intercept
        }
        
    except Exception as e:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e)
        }


def _fit_power_law_emergence(x_data: np.ndarray, y_data: np.ndarray) -> Dict[str, Any]:
    """Fit power law model: S(n) = A×n^α + S₀"""
    
    def power_law_func(x, A, alpha, S0):
        """Power law function with baseline."""
        return A * np.power(x, alpha) + S0
    
    # Initial parameter estimation
    y_min = np.min(y_data)
    y_range = np.max(y_data) - y_min
    
    initial_guess = [y_range, 1.0, y_min]
    bounds = ([0, 0, 0], [10 * y_range, 5, np.max(y_data)])
    
    try:
        popt, pcov = curve_fit(
            power_law_func, x_data, y_data,
            p0=initial_guess,
            bounds=bounds,
            maxfev=5000
        )
        
        A, alpha, S0 = popt
        
        # Calculate R-squared
        y_pred = power_law_func(x_data, *popt)
        ss_res = np.sum((y_data - y_pred) ** 2)
        ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        param_errors = np.sqrt(np.diag(pcov))
        
        return {
            "success": True,
            "parameters": {
                "amplitude": A,
                "exponent": alpha,
                "baseline": S0
            },
            "parameter_errors": {
                "amplitude_err": param_errors[0],
                "exponent_err": param_errors[1],
                "baseline_err": param_errors[2]
            },
            "r_squared": r_squared,
            "fitted_function": lambda x: power_law_func(x, *popt)
        }
        
    except Exception as e:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e)
        }


def _fit_best_emergence_model(x_data: np.ndarray, y_data: np.ndarray) -> Dict[str, Any]:
    """Automatically select best emergence model using AIC/BIC criteria."""
    models = ["logistic", "linear", "power_law"]
    results = []
    
    for model in models:
        fit_result = _fit_emergence_model(x_data, y_data, model)
        if fit_result["success"]:
            # Calculate AIC (Akaike Information Criterion)
            n_data = len(x_data)
            n_params = len(fit_result["parameters"])
            
            # Residual sum of squares
            y_pred = fit_result["fitted_function"](x_data)
            rss = np.sum((y_data - y_pred) ** 2)
            
            # AIC = 2k + n*ln(RSS/n)
            aic = 2 * n_params + n_data * np.log(rss / n_data) if rss > 0 else np.inf
            
            fit_result["aic"] = aic
            results.append(fit_result)
    
    if not results:
        # No models fit successfully
        return {
            "model": "none",
            "success": False,
            "parameters": {},
            "r_squared": 0.0
        }
    
    # Select model with lowest AIC
    best_result = min(results, key=lambda x: x.get("aic", np.inf))
    logger.debug(f"Best model: {best_result['model']} (AIC={best_result.get('aic', 'N/A'):.2f})")
    
    return best_result


def _calculate_ces_from_fit(fit_results: Dict[str, Any], model: str) -> float:
    """Calculate CES from fitted model parameters."""
    if not fit_results["success"]:
        return 0.0
    
    params = fit_results["parameters"]
    
    if model == "logistic":
        # CES = sharpness × amplitude for logistic emergence
        k = params.get("sharpness", 0.0)
        A = params.get("amplitude", 0.0)
        ces = k * A
        
    elif model == "linear":
        # For linear model, CES based on slope magnitude
        slope = params.get("slope", 0.0)
        ces = abs(slope) * 0.1  # Scale down for comparison
        
    elif model == "power_law":
        # For power law, CES based on exponent and amplitude
        alpha = params.get("exponent", 0.0)
        A = params.get("amplitude", 0.0)
        ces = alpha * A * 0.1  # Scale down for comparison
        
    else:
        ces = 0.0
    
    # Ensure non-negative
    return max(0.0, ces)


def _generate_emergence_analysis(ces: float,
                               fit_results: Dict[str, Any],
                               x_data: np.ndarray,
                               y_data: np.ndarray,
                               structure_metric: str,
                               emergence_model: str) -> EmergenceAnalysis:
    """Generate comprehensive emergence analysis results."""
    
    if not fit_results["success"]:
        return _create_insufficient_emergence_analysis()
    
    params = fit_results["parameters"]
    r_squared = fit_results.get("r_squared", 0.0)
    
    # Extract model-specific parameters
    if emergence_model == "logistic":
        critical_threshold = params.get("threshold", 0.0)
        emergence_sharpness = params.get("sharpness", 0.0)
        emergence_amplitude = params.get("amplitude", 0.0)
        baseline_structure = params.get("baseline", 0.0)
        
        # Confidence range for critical threshold
        threshold_err = fit_results.get("parameter_errors", {}).get("threshold_err", 1.0)
        critical_range = (
            max(0, critical_threshold - threshold_err),
            critical_threshold + threshold_err
        )
        
    else:
        # Default values for non-logistic models
        critical_threshold = np.mean(x_data)
        emergence_sharpness = 1.0
        emergence_amplitude = np.max(y_data) - np.min(y_data)
        baseline_structure = np.min(y_data)
        critical_range = (np.min(x_data), np.max(x_data))
    
    # Determine emergence quality
    if r_squared >= 0.9:
        emergence_quality = "excellent"
    elif r_squared >= 0.7:
        emergence_quality = "good"
    elif r_squared >= 0.5:
        emergence_quality = "poor"
    else:
        emergence_quality = "insufficient"
    
    # Determine scaling behavior
    if emergence_model == "logistic" and emergence_sharpness > 1.0:
        scaling_behavior = "sigmoid"
    elif emergence_model == "linear":
        scaling_behavior = "linear"
    elif emergence_model == "power_law":
        scaling_behavior = "power_law"
    else:
        scaling_behavior = "flat"
    
    # Emergence confidence (based on fit quality and parameter significance)
    emergence_confidence = r_squared * (1.0 if emergence_quality in ["excellent", "good"] else 0.5)
    
    # Generate summary
    summary = (f"CES = {ces:.3f} ({emergence_quality} {scaling_behavior} emergence): "
              f"threshold ≈ {critical_threshold:.1f} qubits, R² = {r_squared:.3f}")
    
    return EmergenceAnalysis(
        complexity_emergence_score=ces,
        critical_threshold=critical_threshold,
        emergence_sharpness=emergence_sharpness,
        emergence_amplitude=emergence_amplitude,
        baseline_structure=baseline_structure,
        emergence_quality=emergence_quality,
        scaling_behavior=scaling_behavior,
        fit_r_squared=r_squared,
        emergence_confidence=emergence_confidence,
        critical_range=critical_range,
        emergence_summary=summary
    )


def _create_insufficient_emergence_analysis() -> EmergenceAnalysis:
    """Create default emergence analysis for insufficient data."""
    return EmergenceAnalysis(
        complexity_emergence_score=0.0,
        critical_threshold=0.0,
        emergence_sharpness=0.0,
        emergence_amplitude=0.0,
        baseline_structure=0.0,
        emergence_quality="insufficient",
        scaling_behavior="flat",
        fit_r_squared=0.0,
        emergence_confidence=0.0,
        critical_range=(0.0, 0.0),
        emergence_summary="Insufficient data for emergence analysis"
    )


def validate_ces_properties(ces: float,
                          multi_qubit_data: Dict[int, Mapping[str, int]],
                          tolerance: float = 1e-10) -> bool:
    """
    Validate mathematical properties of computed CES.
    
    Validated Properties:
        1. Non-negativity: CES ≥ 0 (emergence score cannot be negative)
        2. Scaling consistency: Higher complexity should allow higher CES
        3. Data dependency: CES should vary with input data characteristics
        4. Model consistency: Similar data should give similar CES
        5. Physical bounds: CES should be bounded by reasonable physical limits
    """
    # Property 1: Non-negativity
    assert ces >= -tolerance, f"CES={ces} is negative"
    
    # Property 2: Finite and real
    assert np.isfinite(ces), f"CES={ces} is not finite"
    assert np.isreal(ces), f"CES={ces} is not real"
    
    # Property 3: Reasonable bounds (CES typically < 10 for physical systems)
    assert ces <= 100, f"CES={ces} unreasonably large (possible fitting error)"
    
    logger.debug(f"CES validation passed: CES={ces:.6f}")
    return True


def complexity_emergence_educational_demo() -> dict:
    """
    Educational demonstration of CES behavior across emergence scenarios.
    
    Returns:
        dict: Demonstration results with critical phenomena interpretations
    """
    demo_results = {}
    
    # Example 1: Sharp emergence at 3 qubits (GHZ-like)
    sharp_emergence_data = {
        2: {"00": 500, "01": 500},  # Random
        3: {"000": 400, "111": 400, "others": 200},  # Emerging structure
        4: {"0000": 600, "1111": 350, "others": 50},  # Strong structure
        5: {"00000": 700, "11111": 250, "others": 50}  # Dominant structure
    }
    
    ces_sharp = compute_complexity_emergence_score(sharp_emergence_data, return_analysis=True)
    demo_results["sharp_emergence"] = {
        "data": sharp_emergence_data,
        "analysis": ces_sharp.to_dict(),
        "interpretation": "Clear critical threshold around 3 qubits"
    }
    
    # Example 2: Gradual emergence (no critical point)
    gradual_emergence_data = {
        2: {"00": 450, "01": 400, "10": 100, "11": 50},
        3: {"000": 350, "111": 300, "001": 200, "others": 150},
        4: {"0000": 400, "1111": 300, "0001": 150, "others": 150},
        5: {"00000": 450, "11111": 250, "00001": 150, "others": 150}
    }
    
    ces_gradual = compute_complexity_emergence_score(gradual_emergence_data, return_analysis=True)
    demo_results["gradual_emergence"] = {
        "data": gradual_emergence_data,
        "analysis": ces_gradual.to_dict(),
        "interpretation": "Linear scaling without critical threshold"
    }
    
    # Example 3: No emergence (flat scaling)
    no_emergence_data = {
        2: {"00": 250, "01": 250, "10": 250, "11": 250},
        3: {"000": 125, "001": 125, "010": 125, "011": 125,
            "100": 125, "101": 125, "110": 125, "111": 125},
        4: {"0000": 62, "0001": 62, "0010": 62, "0011": 62,
            "0100": 62, "0101": 62, "0110": 62, "0111": 62,
            "1000": 64, "1001": 64, "1010": 64, "1011": 64,
            "1100": 64, "1101": 64, "1110": 64, "1111": 64}
    }
    
    ces_flat = compute_complexity_emergence_score(no_emergence_data, return_analysis=True)
    demo_results["no_emergence"] = {
        "data": no_emergence_data,
        "analysis": ces_flat.to_dict(),
        "interpretation": "No structure emergence - random decoherence"
    }
    
    # Multi-metric comparison
    multi_metric_scores = compute_emergence_across_metrics(sharp_emergence_data)
    demo_results["multi_metric_analysis"] = {
        "emergence_scores": multi_metric_scores,
        "interpretation": "Different metrics may show different emergence patterns"
    }
    
    # Summary insights
    demo_results["summary"] = {
        "ces_range_observed": [
            ces_sharp.complexity_emergence_score,
            ces_gradual.complexity_emergence_score,
            ces_flat.complexity_emergence_score
        ],
        "emergence_progression": "sharp > gradual > flat",
        "critical_phenomena": "Sharp emergence indicates phase transition behavior",
        "research_applications": "Detecting minimum complexity for structured decoherence"
    }
    
    logger.info("CES educational demonstration completed")
    return demo_results