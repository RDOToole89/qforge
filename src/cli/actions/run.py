from __future__ import annotations

from typing import Dict, Any, Optional

from src.engine.api import run as engine_run
from src.visualization.service import VisualizationService
from src.visualization.report import save_report_from_json


def execute_run(
    normalized_params: Dict[str, Any], display_manager, viz
) -> Optional[str]:
    """Run an experiment via the engine and save artifacts consistently.

    Returns the path to the saved analysis JSON for this run.
    """
    display_manager.display_info_message("🚀 Running quantum experiment...")

    # Prepare config for engine (normalize noise_type casing if present)
    allowed_keys = {
        "num_qubits",
        "state_type",
        "sim_mode",
        "shots",
        "noise_enabled",
        "noise_type",
        "error_rate",
        "rng_seed",
        "custom_params",
    }
    experiment_params = {
        k: v for k, v in normalized_params.items() if k in allowed_keys
    }
    if experiment_params.get("noise_type"):
        try:
            experiment_params["noise_type"] = str(
                experiment_params["noise_type"]
            ).lower()
        except Exception:
            pass

    # Run through engine to get analysis + deterministic run directory
    try:
        eng_result = engine_run(experiment_params)
    except Exception as e:
        display_manager.display_error_message(f"Engine run failed: {e}")
        return None

    # Prefer analysis path from artifacts
    try:
        analysis_json = next(
            a.path for a in eng_result.artifacts if str(a.path).endswith(".json")
        )
    except StopIteration:
        display_manager.display_error_message("No analysis JSON artifact found")
        return None

    # Show insights in the console
    try:
        display_manager.display_research_report(eng_result.analysis)
        display_manager.display_research_details(eng_result.analysis)
    except Exception:
        pass

    # Render appropriate visualizations and reports into the run directory
    sim_mode = experiment_params.get("sim_mode", "qasm")
    try:
        svc = VisualizationService()
        if sim_mode == "qasm":
            art_hist = svc.render_from_json(analysis_json, viz_type="histogram")
            display_manager.display_success_message(f"Histogram saved: {art_hist.path}")
            # Hypergraph only when counts are available
            try:
                art_hg = svc.render_from_json(analysis_json, viz_type="hypergraph")
                display_manager.display_success_message(
                    f"Hypergraph saved: {art_hg.path}"
                )
            except Exception:
                # Non-fatal if hypergraph is not applicable
                pass
        elif sim_mode == "density":
            art_dm = svc.render_from_json(analysis_json, viz_type="density_matrix")
            display_manager.display_success_message(
                f"Density matrix saved: {art_dm.path}"
            )
    except Exception as e:
        display_manager.display_warning_message(f"Visualization step skipped: {e}")

    # Write reports (md + html) into run_dir/reports
    try:
        rep_md = save_report_from_json(analysis_json, fmt="md")
        rep_html = save_report_from_json(analysis_json, fmt="html")
        display_manager.display_success_message(f"Report (md): {rep_md}")
        display_manager.display_success_message(f"Report (html): {rep_html}")
    except Exception as e:
        display_manager.display_warning_message(f"Report generation skipped: {e}")

    display_manager.display_success_message("✅ Experiment completed successfully!")
    return str(analysis_json)
