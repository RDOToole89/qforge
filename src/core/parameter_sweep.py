"""
Parameter sweep automation for systematic quantum experiment exploration.

This module provides automated parameter sweeps for research-grade quantum
experiments, enabling systematic exploration of parameter spaces and
statistical aggregation of results.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import itertools

from .research_handler import ResearchExperimentHandler
from ..experiments.manager import get_experiment_manager

logger = logging.getLogger("QuantumExperiment.ParameterSweep")


class ParameterSweepEngine:
    """
    Automated parameter sweep engine for quantum experiments.

    Enables systematic exploration of parameter spaces with automatic
    result aggregation, statistical analysis, and research-grade output.
    """

    def __init__(self, results_dir: str = "results"):
        """
        Initialize the parameter sweep engine.

        Args:
            results_dir: Directory to save sweep results
        """
        self.results_dir = Path(results_dir)
        self.sweep_results_dir = self.results_dir / "parameter_sweeps"
        self.sweep_results_dir.mkdir(parents=True, exist_ok=True)

        self.research_handler = ResearchExperimentHandler(results_dir)

        logger.info(f"Parameter sweep engine initialized with results directory: {self.results_dir}")

    def run_parameter_sweep(self,
                           base_experiment_id: str,
                           parameter_ranges: Dict[str, List[Any]],
                           runs_per_config: int = 3,
                           sweep_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a systematic parameter sweep on a base experiment.

        Args:
            base_experiment_id: ID of the base experiment to sweep
            parameter_ranges: Dictionary mapping parameter names to lists of values
            runs_per_config: Number of runs per parameter configuration
            sweep_name: Optional name for the sweep (auto-generated if None)

        Returns:
            Comprehensive sweep results with aggregated statistics

        Example:
            sweep_results = engine.run_parameter_sweep(
                base_experiment_id="ghz_structured_decoherence_ref",
                parameter_ranges={
                    "error_rate": [0.01, 0.05, 0.10, 0.20],
                    "shots": [1024, 4096]
                },
                runs_per_config=3
            )
        """
        if sweep_name is None:
            sweep_name = f"{base_experiment_id}_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        sweep_id = str(uuid.uuid4())[:8]
        logger.info(f"🚀 Starting parameter sweep: {sweep_name} (ID: {sweep_id})")

        # Generate all parameter combinations
        param_combinations = self._generate_parameter_combinations(parameter_ranges)
        total_experiments = len(param_combinations) * runs_per_config

        logger.info(f"📊 Sweep overview:")
        logger.info(f"   - Base experiment: {base_experiment_id}")
        logger.info(f"   - Parameter combinations: {len(param_combinations)}")
        logger.info(f"   - Runs per configuration: {runs_per_config}")
        logger.info(f"   - Total experiments: {total_experiments}")

        # Initialize experiment manager
        em = get_experiment_manager()

        # Run all experiments
        sweep_results = {
            "sweep_metadata": {
                "sweep_id": sweep_id,
                "sweep_name": sweep_name,
                "base_experiment_id": base_experiment_id,
                "timestamp": datetime.now().isoformat(),
                "total_experiments": total_experiments,
                "parameter_ranges": parameter_ranges,
                "runs_per_config": runs_per_config
            },
            "experiment_results": [],
            "aggregated_analysis": {}
        }

        experiment_count = 0

        # Run experiments for each parameter combination
        for param_combo in param_combinations:
            logger.info(f"🧪 Running parameter combination: {param_combo}")

            combo_results = {
                "parameter_combination": param_combo,
                "runs": []
            }

            # Run multiple times for statistical robustness
            for run_num in range(runs_per_config):
                experiment_count += 1
                logger.info(f"   Run {run_num + 1}/{runs_per_config} ({experiment_count}/{total_experiments})")

                try:
                    # Run the experiment with custom parameters
                    experiment_id = f"{base_experiment_id}_sweep_{sweep_id}_{experiment_count}"
                    result = em.run_experiment(base_experiment_id, custom_params=param_combo)

                    if result and isinstance(result, dict) and 'research_analysis' in result:
                        run_result = {
                            "run_number": run_num + 1,
                            "experiment_id": experiment_id,
                            "success": True,
                            "research_analysis": result['research_analysis'],
                            "research_file": result.get('research_file', '')
                        }
                        combo_results["runs"].append(run_result)
                        logger.info(f"   ✅ Run {run_num + 1} completed successfully")
                    else:
                        logger.error(f"   ❌ Run {run_num + 1} failed - no research analysis returned")
                        combo_results["runs"].append({
                            "run_number": run_num + 1,
                            "experiment_id": experiment_id,
                            "success": False,
                            "error": "No research analysis returned"
                        })

                except Exception as e:
                    logger.error(f"   ❌ Run {run_num + 1} failed with error: {e}")
                    combo_results["runs"].append({
                        "run_number": run_num + 1,
                        "experiment_id": f"{base_experiment_id}_sweep_{sweep_id}_{experiment_count}",
                        "success": False,
                        "error": str(e)
                    })

            sweep_results["experiment_results"].append(combo_results)

        # Aggregate results
        logger.info("📈 Aggregating sweep results...")
        sweep_results["aggregated_analysis"] = self._aggregate_sweep_results(sweep_results["experiment_results"])

        # Save comprehensive sweep results
        sweep_file = self._save_sweep_results(sweep_results, sweep_name)
        logger.info(f"💾 Sweep results saved to: {sweep_file}")

        logger.info(f"🎉 Parameter sweep '{sweep_name}' completed successfully!")
        return sweep_results

    def run_noise_level_sweep(self,
                             base_experiment_id: str,
                             noise_levels: List[float] = None,
                             runs_per_level: int = 3) -> Dict[str, Any]:
        """
        Convenience method for noise level sweeps (common research pattern).

        Args:
            base_experiment_id: ID of the base experiment
            noise_levels: List of noise levels to test (default: [0.01, 0.05, 0.10, 0.20])
            runs_per_level: Number of runs per noise level

        Returns:
            Sweep results focused on noise level analysis
        """
        if noise_levels is None:
            noise_levels = [0.01, 0.05, 0.10, 0.20]

        return self.run_parameter_sweep(
            base_experiment_id=base_experiment_id,
            parameter_ranges={"error_rate": noise_levels},
            runs_per_config=runs_per_level,
            sweep_name=f"{base_experiment_id}_noise_sweep"
        )

    def run_shot_convergence_test(self,
                                 base_experiment_id: str,
                                 shot_counts: List[int] = None,
                                 runs_per_count: int = 3) -> Dict[str, Any]:
        """
        Test convergence behavior across different shot counts.

        Args:
            base_experiment_id: ID of the base experiment
            shot_counts: List of shot counts to test (default: [1024, 2048, 4096, 8192])
            runs_per_count: Number of runs per shot count

        Returns:
            Convergence analysis results
        """
        if shot_counts is None:
            shot_counts = [1024, 2048, 4096, 8192]

        return self.run_parameter_sweep(
            base_experiment_id=base_experiment_id,
            parameter_ranges={"shots": shot_counts},
            runs_per_config=runs_per_count,
            sweep_name=f"{base_experiment_id}_convergence_test"
        )

    def _generate_parameter_combinations(self, parameter_ranges: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """Generate all combinations of parameters."""
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())

        combinations = []
        for combo in itertools.product(*param_values):
            combinations.append(dict(zip(param_names, combo)))

        return combinations

    def _aggregate_sweep_results(self, experiment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate statistics across all sweep experiments."""

        aggregated = {
            "parameter_analysis": {},
            "statistical_summary": {},
            "trends": {},
            "key_findings": []
        }

        # Collect all successful runs
        all_successful_runs = []
        for combo_result in experiment_results:
            param_combo = combo_result["parameter_combination"]
            successful_runs = [run for run in combo_result["runs"] if run.get("success", False)]

            for run in successful_runs:
                run_data = run["research_analysis"]
                run_data["parameters"] = param_combo
                all_successful_runs.append(run_data)

        if not all_successful_runs:
            logger.warning("No successful runs to aggregate")
            return aggregated

        # Analyze trends for each parameter
        for combo_result in experiment_results:
            param_combo = combo_result["parameter_combination"]
            successful_runs = [run for run in combo_result["runs"] if run.get("success", False)]

            if successful_runs:
                # Average metrics across runs for this parameter combination
                avg_entropy = sum(run["research_analysis"]["research_metrics"]["information_theory"]["normalized_entropy"]
                                for run in successful_runs) / len(successful_runs)

                avg_kl_div = sum(run["research_analysis"]["research_metrics"]["distribution_comparison"]["kl_divergence"]
                               for run in successful_runs) / len(successful_runs) if "distribution_comparison" in successful_runs[0]["research_analysis"]["research_metrics"] else 0

                param_key = "_".join(f"{k}={v}" for k, v in param_combo.items())
                aggregated["parameter_analysis"][param_key] = {
                    "parameters": param_combo,
                    "successful_runs": len(successful_runs),
                    "average_normalized_entropy": avg_entropy,
                    "average_kl_divergence": avg_kl_div,
                    "entropy_std": self._calculate_std([run["research_analysis"]["research_metrics"]["information_theory"]["normalized_entropy"]
                                                      for run in successful_runs]),
                }

        # Generate key findings
        if len(all_successful_runs) > 1:
            entropies = [run["research_metrics"]["information_theory"]["normalized_entropy"] for run in all_successful_runs]
            min_entropy = min(entropies)
            max_entropy = max(entropies)

            aggregated["key_findings"].append(f"Entropy range: {min_entropy:.3f} - {max_entropy:.3f}")

            if max_entropy - min_entropy > 0.1:
                aggregated["key_findings"].append("Significant entropy variation detected across parameters")

        aggregated["statistical_summary"] = {
            "total_successful_runs": len(all_successful_runs),
            "total_parameter_combinations": len(experiment_results),
            "success_rate": len(all_successful_runs) / sum(len(combo["runs"]) for combo in experiment_results) if experiment_results else 0
        }

        return aggregated

    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    def _save_sweep_results(self, sweep_results: Dict[str, Any], sweep_name: str) -> str:
        """Save comprehensive sweep results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sweep_{sweep_name}_{timestamp}.json"
        filepath = self.sweep_results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(sweep_results, f, indent=2, default=str)

        return str(filepath)


# Convenience functions for quick access
def run_noise_sweep(experiment_id: str, noise_levels: List[float] = None, runs_per_level: int = 3) -> Dict[str, Any]:
    """Quick noise level sweep."""
    engine = ParameterSweepEngine()
    return engine.run_noise_level_sweep(experiment_id, noise_levels, runs_per_level)


def run_convergence_test(experiment_id: str, shot_counts: List[int] = None, runs_per_count: int = 3) -> Dict[str, Any]:
    """Quick convergence test."""
    engine = ParameterSweepEngine()
    return engine.run_shot_convergence_test(experiment_id, shot_counts, runs_per_count)


def run_custom_sweep(experiment_id: str, parameter_ranges: Dict[str, List[Any]], runs_per_config: int = 3) -> Dict[str, Any]:
    """Quick custom parameter sweep."""
    engine = ParameterSweepEngine()
    return engine.run_parameter_sweep(experiment_id, parameter_ranges, runs_per_config)
