from __future__ import annotations

from typing import Optional


def render_from_json(
    path: str,
    viz_type: Optional[str] = None,
    backend: Optional[str] = None,
    outdir: Optional[str] = None,
) -> None:
    import os
    import json as _json

    with open(path, "r") as f:
        analysis = _json.load(f)

    use_engine = os.environ.get("QEXP_USE_ENGINE_API", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    vtype = viz_type or "histogram"
    if use_engine and vtype in {"histogram", "density_matrix", "hypergraph"}:
        try:
            from src.engine.viz_service import (
                VisualizationService,
                VisualizationRequest,
            )

            svc = VisualizationService(default_backend=(backend or "matplotlib"))
            req = VisualizationRequest(
                viz_type=vtype,
                backend=(backend or "matplotlib"),
                output_base_dir=outdir,
            )
            svc.render_from_json(path, req)
            return
        except Exception:
            pass

    # Legacy fallback
    params = analysis.get("experiment_parameters", {})
    counts = analysis.get("measurement_results", {}).get("raw_counts", {})
    if vtype == "histogram":
        from src.visualization import get_histogram_visualizer

        plot_fn = get_histogram_visualizer()
        plot_fn(
            counts=counts,
            state_type=params.get("state_type", "GHZ"),
            noise_type=params.get("noise_type", "DEPOLARIZING"),
            noise_enabled=params.get("noise_enabled", True),
            num_qubits=int(params.get("num_qubits", 3)),
            research_metrics=analysis.get("research_metrics"),
            save_path=None,
        )
    elif vtype == "hypergraph":
        from src.visualization import get_hypergraph_visualizer

        get_hypergraph_visualizer()(
            correlation_data=counts,
            state_type=params.get("state_type", "GHZ"),
            noise_type=params.get("noise_type", "DEPOLARIZING"),
            config={},
        )
    elif vtype == "density_matrix":
        # Cannot reconstruct density matrix from counts
        raise SystemExit(2)
