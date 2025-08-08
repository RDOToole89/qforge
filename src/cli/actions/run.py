from __future__ import annotations

from typing import Dict, Any, Optional

from src.core.research_handler import ResearchExperimentHandler
from src.experiments.manager import get_experiment_manager


def execute_run(
    normalized_params: Dict[str, Any], display_manager, viz
) -> Optional[str]:
    """Run an experiment using legacy ExperimentManager and return research file if saved."""
    display_manager.display_info_message("🚀 Running quantum experiment...")
    em = get_experiment_manager()
    experiment_params = {
        k: v
        for k, v in normalized_params.items()
        if k not in ["name", "description", "category", "difficulty"]
    }
    result = em.run_experiment("ghz_basic", custom_params=experiment_params)
    if not result:
        display_manager.display_error_message("❌ Experiment failed")
        return None

    is_density = experiment_params.get("sim_mode") == "density"
    if not is_density:
        research_handler = ResearchExperimentHandler()
        if isinstance(result, tuple) and len(result) >= 2:
            circuit, raw_results = result
            research_analysis = research_handler.process_experiment_result(
                circuit=circuit,
                result=raw_results,
                experiment_config=experiment_params,
                experiment_id="cli_experiment",
            )
            research_file = research_handler.save_research_result(research_analysis)
            display_manager.display_experiment_results(result)
            viz_type = experiment_params.get("visualization_type", "none")
            if viz_type and viz_type != "none":
                viz.show(raw_results, experiment_params, viz_type)
            display_manager.display_success_message(
                f"📊 Research-grade analysis saved: {research_file}"
            )
            display_manager.display_success_message(
                "✅ Experiment completed successfully!"
            )
            return str(research_file)
    else:
        display_manager.display_experiment_results(result)
        display_manager.display_info_message(
            "🔬 Density Matrix Mode: Displaying quantum state analysis"
        )
        viz_type = experiment_params.get("visualization_type", "none")
        if viz_type and viz_type != "none":
            if isinstance(result, tuple) and len(result) >= 2:
                _c, raw_results = result
                viz.show(raw_results, experiment_params, viz_type)
            else:
                viz.show(result, experiment_params, viz_type)
        display_manager.display_success_message("✅ Experiment completed successfully!")
        return None
