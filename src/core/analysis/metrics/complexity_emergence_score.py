"""Complexity Emergence Score (CES) - Threshold detection in metric-vs-size data.

# Mathematical Foundation
The Complexity Emergence Score quantifies at what system size (number of
qubits) a structure metric rises sharply above its background level. It uses
logistic curve fitting and critical point analysis to detect threshold-like
behavior in a metric as system size increases.

# Physical Interpretation
CES detects whether a metric grows gradually with system size or exhibits a
sharp, threshold-like rise around a critical size n₀. A sharp rise resembles
phase-transition-like behavior; a flat or gradual trend does not.

# Applications
- Detecting thresholds where a metric rises sharply with system size
- Characterizing the scaling behavior of distribution-structure metrics
- Comparing emergence behavior across state types and noise conditions

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

from __future__ import annotations

import logging
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, overload

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress

from ..constants import CES_MAX_QUBITS, CES_MIN_POINTS, validate_counts_dict
from .asymmetry_index import compute_asymmetry_index

logger = logging.getLogger(__name__)


@dataclass
class EmergenceAnalysis:
    """Complete complexity emergence analysis with critical point detection.

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
    critical_range: tuple[float, float]
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
            "emergence_summary": self.emergence_summary,
        }


@overload
def compute_complexity_emergence_score(
    multi_qubit_data: Mapping[int, Mapping[str, int]],
    structure_metric: str = ...,
    emergence_model: str = ...,
    return_analysis: Literal[False] = ...,
) -> float: ...


@overload
def compute_complexity_emergence_score(
    multi_qubit_data: Mapping[int, Mapping[str, int]],
    structure_metric: str = ...,
    emergence_model: str = ...,
    *,
    return_analysis: Literal[True],
) -> EmergenceAnalysis: ...


def compute_complexity_emergence_score(
    multi_qubit_data: Mapping[int, Mapping[str, int]],
    structure_metric: str = "asymmetry_index",
    emergence_model: str = "logistic",
    return_analysis: bool = False,
) -> float | EmergenceAnalysis:
    """Compute Complexity Emergence Score - critical threshold for structure emergence.

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
        - **Auto**: Automatic model selection via AIC

    Structure Metrics:
        - **asymmetry_index**: Primary emergence metric (default)
        - **structure_score**: Alternative using Jensen-Shannon divergence
        - **concentration_index**: Economic inequality emergence

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
    """
    # Input validation with strict error handling
    if not multi_qubit_data or len(multi_qubit_data) < CES_MIN_POINTS:
        logger.warning(
            "CES requires ≥%d data points, got %d",
            CES_MIN_POINTS,
            len(multi_qubit_data) if multi_qubit_data else 0,
        )
        return (
            0.0
            if not return_analysis
            else EmergenceAnalysis(
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
                emergence_summary="Insufficient data for emergence analysis",
            )
        )

    # Validate data consistency and extract qubit counts
    qubit_counts = sorted(multi_qubit_data.keys())
    if any(n < 1 or n > CES_MAX_QUBITS for n in qubit_counts):
        raise ValueError(f"Qubit counts must be in [1, {CES_MAX_QUBITS}], got {qubit_counts}")

    logger.debug("Computing CES for %d system sizes: %s", len(qubit_counts), qubit_counts)

    # Compute structure metric for each system size, keeping (x,y) aligned
    x_vals: list[float] = []
    y_vals: list[float] = []
    for n_qubits in qubit_counts:
        counts = multi_qubit_data[n_qubits]
        try:
            counts_clean = validate_counts_dict(counts, f"system size {n_qubits}")
        except ValueError as e:
            logger.warning("Invalid counts for %d qubits: %s", n_qubits, e)
            continue

        # Compute specified structure metric
        if structure_metric == "asymmetry_index":
            metric_value = float(compute_asymmetry_index(counts_clean))
        elif structure_metric == "structure_score":
            from .structure_score import compute_structure_score

            metric_value = float(compute_structure_score(counts=counts_clean).get("value", 0.0))
        elif structure_metric == "concentration_index":
            from .concentration_index import compute_concentration_index

            metric_value = float(compute_concentration_index(counts_clean))
        else:
            raise ValueError(f"Unknown structure metric: {structure_metric}")

        x_vals.append(float(n_qubits))
        y_vals.append(metric_value)
        logger.debug("n=%d: %s=%.6f", n_qubits, structure_metric, metric_value)

    if len(y_vals) < CES_MIN_POINTS:
        logger.warning("Only %d valid data points after filtering", len(y_vals))
        return 0.0 if not return_analysis else _create_insufficient_emergence_analysis()

    # Convert to numpy arrays for fitting
    x_data = np.asarray(x_vals, dtype=float)
    y_data = np.asarray(y_vals, dtype=float)

    # Fit emergence model and extract parameters
    if emergence_model == "auto":
        fit_results = _fit_best_emergence_model(x_data, y_data)
    else:
        fit_results = _fit_emergence_model(x_data, y_data, emergence_model)

    # Use the actually selected model for CES calculation
    model_for_ces = fit_results.get("model", emergence_model)
    ces = _calculate_ces_from_fit(fit_results, model_for_ces)

    logger.debug("Computed CES = %.6f using %s model", ces, model_for_ces)

    if not return_analysis:
        return ces

    # Generate comprehensive emergence analysis
    return _generate_emergence_analysis(
        ces, fit_results, x_data, y_data, structure_metric, model_for_ces
    )


def compute_emergence_across_metrics(
    multi_qubit_data: Mapping[int, Mapping[str, int]], metrics: list[str] | None = None
) -> dict[str, float]:
    """Compute CES across multiple structure metrics for comprehensive analysis.

    This function analyzes emergence patterns across different structural
    measures, providing a multi-dimensional view of complexity scaling.

    Args:
        multi_qubit_data: {n_qubits: measurement_counts} for different system sizes
        metrics: List of metrics to analyze (None = use defaults)

    Returns:
        Dict[str, float]: {metric_name: emergence_score} for each metric
    """
    if metrics is None:
        metrics = ["asymmetry_index", "structure_score", "concentration_index"]

    emergence_scores: dict[str, float] = {}
    for metric in metrics:
        try:
            ces = compute_complexity_emergence_score(
                multi_qubit_data, structure_metric=metric, emergence_model="logistic"
            )
            emergence_scores[metric] = float(ces)
            logger.debug("Emergence for %s: %.6f", metric, ces)
        except Exception as e:
            logger.warning("Failed to compute emergence for %s: %s", metric, e)
            emergence_scores[metric] = 0.0

    return emergence_scores


def _fit_emergence_model(x_data: np.ndarray, y_data: np.ndarray, model: str) -> dict[str, Any]:
    """Fit specified emergence model to structure vs complexity data."""
    results: dict[str, Any] = {"model": model, "success": False}
    try:
        if model == "logistic":
            fitted = _fit_logistic_emergence(x_data, y_data)
        elif model == "linear":
            fitted = _fit_linear_emergence(x_data, y_data)
        elif model == "power_law":
            fitted = _fit_power_law_emergence(x_data, y_data)
        else:
            raise ValueError(f"Unknown emergence model: {model}")
        results.update(fitted)
        results["model"] = model
    except Exception as e:
        logger.debug("Emergence model fitting failed for %s: %s", model, e)
        results.update({"parameters": {}, "r_squared": 0.0, "fit_error": str(e)})
    return results


def _fit_logistic_emergence(x_data: np.ndarray, y_data: np.ndarray) -> dict[str, Any]:
    """Fit logistic emergence model: S(n) = A/(1 + exp(-k(n-n₀))) + S₀."""

    def logistic_func(x: Any, A: float, k: float, n0: float, S0: float) -> Any:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return A / (1 + np.exp(-k * (x - n0))) + S0

    # Intelligent initial parameter estimation
    y_min, y_max = float(np.min(y_data)), float(np.max(y_data))
    x_min, x_max = float(np.min(x_data)), float(np.max(x_data))

    A_init = max(y_max - y_min, 1e-8)  # Amplitude
    S0_init = y_min  # Baseline
    n0_init = 0.5 * (x_min + x_max)  # Midpoint as initial threshold
    k_init = 1.0  # Initial sharpness

    initial_guess = [A_init, k_init, n0_init, S0_init]
    bounds = (
        [0.0, 0.1, x_min - 1.0, 0.0],
        [2.0 * (y_max - y_min + 1e-8), 10.0, x_max + 1.0, y_max],
    )

    try:
        popt, pcov = curve_fit(
            logistic_func, x_data, y_data, p0=initial_guess, bounds=bounds, maxfev=5000
        )
        A, k, n0, S0 = [float(v) for v in popt]
        y_pred = logistic_func(x_data, *popt)
        ss_res = float(np.sum((y_data - y_pred) ** 2))
        ss_tot = float(np.sum((y_data - np.mean(y_data)) ** 2))
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        param_errors = np.sqrt(np.diag(pcov)) if pcov is not None else np.array([np.nan] * 4)
        return {
            "success": True,
            "parameters": {
                "amplitude": A,
                "sharpness": k,
                "threshold": n0,
                "baseline": S0,
            },
            "parameter_errors": {
                "amplitude_err": float(param_errors[0]),
                "sharpness_err": float(param_errors[1]),
                "threshold_err": float(param_errors[2]),
                "baseline_err": float(param_errors[3]),
            },
            "r_squared": float(r_squared),
            "fitted_function": lambda x: logistic_func(x, *popt),
        }
    except Exception as e:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e),
        }


def _fit_linear_emergence(x_data: np.ndarray, y_data: np.ndarray) -> dict[str, Any]:
    """Fit linear model: S(n) = m×n + b."""
    try:
        slope, intercept, r_value, p_value, std_err = linregress(x_data, y_data)
        return {
            "success": True,
            "parameters": {
                "slope": float(slope),
                "intercept": float(intercept),
                "p_value": float(p_value),
            },
            "parameter_errors": {"slope_err": float(std_err)},
            "r_squared": float(r_value**2),
            "fitted_function": lambda x: slope * x + intercept,
        }
    except Exception as e:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e),
        }


def _fit_power_law_emergence(x_data: np.ndarray, y_data: np.ndarray) -> dict[str, Any]:
    """Fit power law model: S(n) = A×n^α + S₀."""

    def power_law_func(x: Any, A: float, alpha: float, S0: float) -> Any:
        return A * np.power(x, alpha) + S0

    y_min = float(np.min(y_data))
    y_max = float(np.max(y_data))
    y_range = y_max - y_min
    if y_range <= 1e-12:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": "Degenerate data (flat response)",
        }

    initial_guess = [y_range, 1.0, y_min]
    bounds = ([0.0, 0.0, 0.0], [10.0 * y_range, 5.0, y_max])

    try:
        popt, pcov = curve_fit(
            power_law_func, x_data, y_data, p0=initial_guess, bounds=bounds, maxfev=5000
        )
        A, alpha, S0 = [float(v) for v in popt]
        y_pred = power_law_func(x_data, *popt)
        ss_res = float(np.sum((y_data - y_pred) ** 2))
        ss_tot = float(np.sum((y_data - np.mean(y_data)) ** 2))
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        param_errors = np.sqrt(np.diag(pcov)) if pcov is not None else np.array([np.nan] * 3)
        return {
            "success": True,
            "parameters": {"amplitude": A, "exponent": alpha, "baseline": S0},
            "parameter_errors": {
                "amplitude_err": float(param_errors[0]),
                "exponent_err": float(param_errors[1]),
                "baseline_err": float(param_errors[2]),
            },
            "r_squared": float(r_squared),
            "fitted_function": lambda x: power_law_func(x, *popt),
        }
    except Exception as e:
        return {
            "success": False,
            "parameters": {},
            "r_squared": 0.0,
            "fit_error": str(e),
        }


def _fit_best_emergence_model(x_data: np.ndarray, y_data: np.ndarray) -> dict[str, Any]:
    """Automatically select best emergence model using AIC."""
    models = ["logistic", "linear", "power_law"]
    results: list[dict[str, Any]] = []

    for model in models:
        fit_result = _fit_emergence_model(x_data, y_data, model)
        if fit_result.get("success"):
            n_data = int(len(x_data))
            # parameter counts by model (consistent with our parameterization)
            param_count_by_model = {"logistic": 4, "linear": 2, "power_law": 3}
            n_params = param_count_by_model.get(
                fit_result.get("model", model), len(fit_result.get("parameters", {}))
            )
            y_pred = fit_result["fitted_function"](x_data)
            rss = float(np.sum((y_data - y_pred) ** 2))
            # AIC = 2k + n*ln(RSS/n); handle perfect fit (rss=0)
            # as -inf to favor simplest perfect-fit model
            aic = 2.0 * n_params + n_data * np.log(rss / n_data) if rss > 0 else -np.inf
            fit_result["aic"] = aic
            results.append(fit_result)

    if not results:
        return {"model": "none", "success": False, "parameters": {}, "r_squared": 0.0}

    best_result = min(results, key=lambda x: x.get("aic", np.inf))
    logger.debug(
        "Best model: %s (AIC=%s)",
        best_result.get("model"),
        (f"{best_result.get('aic'):.2f}" if np.isfinite(best_result.get("aic", np.inf)) else "−∞"),
    )
    return best_result


def _calculate_ces_from_fit(fit_results: dict[str, Any], model: str) -> float:
    """Calculate CES from fitted model parameters."""
    if not fit_results.get("success"):
        return 0.0

    params = fit_results.get("parameters", {})
    if model == "logistic":
        k = float(params.get("sharpness", 0.0))
        A = float(params.get("amplitude", 0.0))
        ces = k * A
    elif model == "linear":
        slope = float(params.get("slope", 0.0))
        ces = abs(slope) * 0.1  # scaled for comparability
    elif model == "power_law":
        alpha = float(params.get("exponent", 0.0))
        A = float(params.get("amplitude", 0.0))
        ces = alpha * A * 0.1  # scaled for comparability
    else:
        ces = 0.0

    return max(0.0, float(ces))


def _generate_emergence_analysis(
    ces: float,
    fit_results: dict[str, Any],
    x_data: np.ndarray,
    y_data: np.ndarray,
    structure_metric: str,
    emergence_model: str,
) -> EmergenceAnalysis:
    """Generate comprehensive emergence analysis results."""
    if not fit_results.get("success"):
        return _create_insufficient_emergence_analysis()

    params = fit_results.get("parameters", {})
    r_squared = float(fit_results.get("r_squared", 0.0))

    if emergence_model == "logistic":
        critical_threshold = float(params.get("threshold", 0.0))
        emergence_sharpness = float(params.get("sharpness", 0.0))
        emergence_amplitude = float(params.get("amplitude", 0.0))
        baseline_structure = float(params.get("baseline", 0.0))
        # Confidence range for critical threshold
        threshold_err = float(fit_results.get("parameter_errors", {}).get("threshold_err", 1.0))
        critical_range = (
            max(0.0, critical_threshold - threshold_err),
            critical_threshold + threshold_err,
        )
    else:
        # Defaults for non-logistic models
        critical_threshold = float(np.mean(x_data))
        emergence_sharpness = 1.0
        emergence_amplitude = float(np.max(y_data) - np.min(y_data))
        baseline_structure = float(np.min(y_data))
        critical_range = (float(np.min(x_data)), float(np.max(x_data)))

    # Emergence quality
    if r_squared >= 0.9:
        emergence_quality = "excellent"
    elif r_squared >= 0.7:
        emergence_quality = "good"
    elif r_squared >= 0.5:
        emergence_quality = "poor"
    else:
        emergence_quality = "insufficient"

    # Scaling behavior
    if emergence_model == "logistic" and emergence_sharpness > 1.0:
        scaling_behavior = "sigmoid"
    elif emergence_model == "linear":
        scaling_behavior = "linear"
    elif emergence_model == "power_law":
        scaling_behavior = "power_law"
    else:
        scaling_behavior = "flat"

    emergence_confidence = r_squared * (1.0 if emergence_quality in ("excellent", "good") else 0.5)
    summary = (
        f"CES = {ces:.3f} ({emergence_quality} {scaling_behavior} "
        f"emergence): threshold ≈ {critical_threshold:.1f} qubits, "
        f"R² = {r_squared:.3f}"
    )

    return EmergenceAnalysis(
        complexity_emergence_score=float(ces),
        critical_threshold=critical_threshold,
        emergence_sharpness=emergence_sharpness,
        emergence_amplitude=emergence_amplitude,
        baseline_structure=baseline_structure,
        emergence_quality=emergence_quality,
        scaling_behavior=scaling_behavior,
        fit_r_squared=r_squared,
        emergence_confidence=float(emergence_confidence),
        critical_range=critical_range,
        emergence_summary=summary,
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
        emergence_summary="Insufficient data for emergence analysis",
    )


def validate_ces_properties(
    ces: float, multi_qubit_data: dict[int, Mapping[str, int]], tolerance: float = 1e-10
) -> bool:
    """Validate mathematical properties of computed CES.

    Validated Properties:
        1. Non-negativity: CES ≥ 0 (emergence score cannot be negative)
        2. Finite and real
        3. Reasonable bounds (guard against runaway fits)
    """
    assert ces >= -tolerance, f"CES={ces} is negative"
    assert np.isfinite(ces), f"CES={ces} is not finite"
    assert np.isreal(ces), f"CES={ces} is not real"
    assert ces <= 100, f"CES={ces} unreasonably large (possible fitting error)"
    logger.debug("CES validation passed: CES=%.6f", ces)
    return True


def complexity_emergence_educational_demo() -> dict:
    """Educational demonstration of CES behavior across emergence scenarios.

    Returns:
        dict: Demonstration results with critical phenomena interpretations
    """
    demo_results: dict[str, Any] = {}

    # Example 1: Sharp emergence at ~3 qubits (GHZ-like)
    sharp_emergence_data = {
        2: {"00": 500, "01": 500},  # Random
        3: {"000": 400, "111": 400, "001": 200},  # Emerging structure
        4: {"0000": 600, "1111": 350, "0001": 50},  # Strong structure
        5: {"00000": 700, "11111": 250, "00001": 50},  # Dominant structure
    }
    ces_sharp = compute_complexity_emergence_score(sharp_emergence_data, return_analysis=True)
    demo_results["sharp_emergence"] = {
        "data": sharp_emergence_data,
        "analysis": ces_sharp.to_dict(),
        "interpretation": "Clear critical threshold around 3 qubits",
    }

    # Example 2: Gradual emergence (no sharp critical point)
    gradual_emergence_data = {
        2: {"00": 450, "01": 400, "10": 100, "11": 50},
        3: {"000": 350, "111": 300, "001": 200, "010": 150},
        4: {"0000": 400, "1111": 300, "0001": 150, "0010": 150},
        5: {"00000": 450, "11111": 250, "00001": 150, "00010": 150},
    }
    ces_gradual = compute_complexity_emergence_score(gradual_emergence_data, return_analysis=True)
    demo_results["gradual_emergence"] = {
        "data": gradual_emergence_data,
        "analysis": ces_gradual.to_dict(),
        "interpretation": "Linear/gradual scaling without a sharp threshold",
    }

    # Example 3: No emergence (flat scaling)
    no_emergence_data = {
        2: {"00": 250, "01": 250, "10": 250, "11": 250},
        3: {
            "000": 125,
            "001": 125,
            "010": 125,
            "011": 125,
            "100": 125,
            "101": 125,
            "110": 125,
            "111": 125,
        },
        4: {
            "0000": 62,
            "0001": 62,
            "0010": 62,
            "0011": 62,
            "0100": 62,
            "0101": 62,
            "0110": 62,
            "0111": 62,
            "1000": 64,
            "1001": 64,
            "1010": 64,
            "1011": 64,
            "1100": 64,
            "1101": 64,
            "1110": 64,
            "1111": 64,
        },
    }
    ces_flat = compute_complexity_emergence_score(no_emergence_data, return_analysis=True)
    demo_results["no_emergence"] = {
        "data": no_emergence_data,
        "analysis": ces_flat.to_dict(),
        "interpretation": "No structure emergence — random-like decoherence",
    }

    # Multi-metric comparison
    multi_metric_scores = compute_emergence_across_metrics(sharp_emergence_data)
    demo_results["multi_metric_analysis"] = {
        "emergence_scores": multi_metric_scores,
        "interpretation": "Different metrics may show differing emergence sensitivity",
    }

    # Summary insights
    demo_results["summary"] = {
        "ces_range_observed": [
            ces_sharp.complexity_emergence_score,
            ces_gradual.complexity_emergence_score,
            ces_flat.complexity_emergence_score,
        ],
        "emergence_progression": "sharp > gradual > flat",
        "critical_phenomena": "Sharp emergence indicates phase-transition-like behavior",
        "applications": "Detecting thresholds where a metric rises sharply with system size",
    }

    logger.info("CES educational demonstration completed")
    return demo_results
