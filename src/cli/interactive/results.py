# src/cli/interactive/results.py

from __future__ import annotations

from typing import Any, Dict, List
from rich.table import Table


class ResultsManager:
    """Handles recent results listing, opening visualizations, re-runs, and comparisons."""

    def __init__(self, console, input_handler, display_manager):
        self.console = console
        self.input_handler = input_handler
        self.display_manager = display_manager
        # last analysis cache for viz metrics
        self._last_research_analysis: Dict[str, Any] | None = None

    def show_recent_results(self, max_items: int = 10) -> None:
        from pathlib import Path
        base = Path("results")
        if not base.exists():
            self.display_manager.console.print("[yellow]No results found.[/yellow]")
            return
        files = sorted(base.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:max_items]
        if not files:
            self.display_manager.console.print("[yellow]No results found.[/yellow]")
            return
        table = Table(title="Recent Results")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Filename", style="green")
        table.add_column("Modified", style="yellow", width=20)
        table.add_column("Metric", style="magenta", width=12)
        from datetime import datetime
        import json as _json
        for idx, f in enumerate(files, start=1):
            try:
                ts = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                metric = "-"
                try:
                    with open(f, "r") as jf:
                        data = _json.load(jf)
                    info = data.get("research_metrics", {}).get("information_theory", {})
                    if isinstance(info.get("normalized_entropy"), (int, float)):
                        metric = f"H_norm={info['normalized_entropy']:.3f}"
                except Exception:
                    metric = "-"
            except Exception:
                ts, metric = "-", "-"
            table.add_row(str(idx), str(f), ts, metric)
        self.console.print(table)
        action = self.input_handler.select_option(
            title="Result Actions",
            options=[
                ("back", "Back", "b"),
                ("open", "Open Visualization", "o"),
                ("rerun", "Re-run", "r"),
                ("compare", "Compare Two Results", "c"),
            ],
            default_value="back",
            show_value_column=False,
        )
        if action == "back":
            return
        idx_map = [(str(i), str(i), str(i)) for i in range(1, len(files) + 1)]
        pick = self.input_handler.select_option(
            title="Select Result", options=idx_map, default_value="1", show_value_column=False
        )
        try:
            chosen = files[int(pick) - 1]
        except Exception:
            return
        if action == "open":
            self.console.print(f"Opening: {chosen}")
            try:
                self.open_visualization_from_result_json(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(f"Failed to open visualization: {e}")
        elif action == "rerun":
            self.console.print(f"Re-running from: {chosen}")
            try:
                self.rerun_from_result_json(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(f"Failed to re-run: {e}")
        elif action == "compare":
            pick2 = self.input_handler.select_option(
                title="Compare Results", options=idx_map, default_value="2" if len(files) > 1 else "1", show_value_column=False
            )
            try:
                chosen2 = files[int(pick2) - 1]
            except Exception:
                return
            try:
                self.compare_results(str(chosen), str(chosen2))
                if self.input_handler.prompt_yes_no("insights_details_prompt", "n"):
                    self.compare_vs_ideal(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(f"Failed to compare: {e}")

    def open_visualization_from_result_json(self, file_path: str) -> None:
        import json as _json
        with open(file_path, "r") as f:
            analysis = _json.load(f)
        self._last_research_analysis = analysis
        params = analysis.get("experiment_parameters", {})
        counts = analysis.get("measurement_results", {}).get("raw_counts", {})
        viz = self.input_handler.select_option(
            title="Visualization Type",
            options=[("histogram", "Histogram", "h"), ("density_matrix", "Density Matrix", "d"), ("hypergraph", "Hypergraph", "g")],
            default_value="histogram",
            show_value_column=False,
        )
        args = {**params, "visualization_type": viz}
        self.display_manager.display_params_summary(args)
        from .viz import VisualizationOrchestrator
        VisualizationOrchestrator(self.display_manager).show({"counts": counts}, args, viz)

    def rerun_from_result_json(self, file_path: str) -> None:
        import json as _json
        from src.experiments.manager import get_experiment_manager
        from src.core.research_handler import ResearchExperimentHandler

        with open(file_path, "r") as f:
            analysis = _json.load(f)
        params = analysis.get("experiment_parameters", {})
        args = dict(params)
        self.display_manager.display_params_summary(args)
        if self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) != "y":
            return
        self.display_manager.display_info_message("🚀 Running quantum experiment...")
        em = get_experiment_manager()
        experiment_params = {k: v for k, v in args.items() if k not in ["name", "description", "category", "difficulty"]}
        result = em.run_experiment("ghz_basic", custom_params=experiment_params)
        if not result:
            self.display_manager.display_error_message("❌ Experiment failed")
            return
        is_density_experiment = experiment_params.get("sim_mode") == "density"
        if not is_density_experiment:
            research_handler = ResearchExperimentHandler()
            if isinstance(result, tuple) and len(result) >= 2:
                circuit, raw_results = result
                research_analysis = research_handler.process_experiment_result(
                    circuit=circuit,
                    result=raw_results,
                    experiment_config=experiment_params,
                    experiment_id="cli_experiment",
                )
                self._last_research_analysis = research_analysis
                research_file = research_handler.save_research_result(research_analysis)
                self.display_manager.display_experiment_results(result)
                viz_type = experiment_params.get("visualization_type", "none")
                if viz_type and viz_type != "none":
                    from .viz import VisualizationOrchestrator
                    VisualizationOrchestrator(self.display_manager).show(raw_results, experiment_params, viz_type)
                self.display_manager.display_success_message(f"📊 Research-grade analysis saved: {research_file}")
        else:
            self.display_manager.display_experiment_results(result)
            self.display_manager.display_info_message("🔬 Density Matrix Mode: Displaying quantum state analysis")
            viz_type = experiment_params.get("visualization_type", "none")
            if viz_type and viz_type != "none":
                if isinstance(result, tuple) and len(result) >= 2:
                    _c, raw_results = result
                    from .viz import VisualizationOrchestrator
                    VisualizationOrchestrator(self.display_manager).show(raw_results, experiment_params, viz_type)
                else:
                    from .viz import VisualizationOrchestrator
                    VisualizationOrchestrator(self.display_manager).show(result, experiment_params, viz_type)

    def compare_results(self, file_a: str, file_b: str) -> None:
        import json as _json
        a, b = None, None
        with open(file_a, "r") as fa, open(file_b, "r") as fb:
            a = _json.load(fa)
            b = _json.load(fb)
        a_info = a.get("research_metrics", {}).get("information_theory", {})
        b_info = b.get("research_metrics", {}).get("information_theory", {})
        table = Table(title="Result Comparison (Information Theory)")
        table.add_column("Metric", style="cyan")
        table.add_column("A", style="green")
        table.add_column("B", style="yellow")
        table.add_column("Δ (B-A)", style="magenta")
        for key in sorted(set(a_info.keys()) | set(b_info.keys())):
            av, bv = a_info.get(key, None), b_info.get(key, None)
            if isinstance(av, (int, float)) or isinstance(bv, (int, float)):
                try:
                    delta = (bv or 0) - (av or 0)
                    table.add_row(key, f"{av}", f"{bv}", f"{delta:+.6f}")
                except Exception:
                    table.add_row(key, str(av), str(bv), "-")
            else:
                table.add_row(key, str(av), str(bv), "-")
        self.console.print(table)

    def compare_vs_ideal(self, file_path: str) -> None:
        import json as _json
        from src.visualization.histogram import get_ideal_quantum_distribution

        with open(file_path, "r") as f:
            data = _json.load(f)
        params = data.get("experiment_parameters", {})
        state_type = params.get("state_type")
        num_qubits = int(params.get("num_qubits", 0))
        counts = data.get("measurement_results", {}).get("raw_counts", {})
        shots = max(1, int(sum(int(v) for v in counts.values())))
        probs = {k: int(v) / shots for k, v in counts.items()}
        ideal = get_ideal_quantum_distribution(state_type, num_qubits)
        keys = sorted(set(list(probs.keys()) + list(ideal.keys())))
        tvd = 0.5 * sum(abs(probs.get(k, 0) - ideal.get(k, 0)) for k in keys)
        try:
            import math

            kl = sum(
                probs[k] * math.log((probs[k] + 1e-12) / (ideal.get(k, 1e-12)))
                for k in keys
                if probs.get(k, 0) > 0
            )
        except Exception:
            kl = float("nan")
        t = Table(title="Delta vs Ideal", show_header=True, header_style="bold magenta")
        t.add_column("Metric", style="cyan")
        t.add_column("Value", style="green")
        t.add_row("Total Variation Distance", f"{tvd:.6f}")
        t.add_row("KL Divergence", f"{kl:.6f}")
        self.console.print(t)