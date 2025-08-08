"""
Interactive CLI module for the Quantum Experiment Framework.

This module handles the interactive command-line interface for running
quantum experiments with user-friendly prompts and rich output.
"""

import uuid
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table

from src.config.params import apply_defaults, validate_parameters
from src.utils.input_handler import InputHandler
from .help import HelpManager
from src.utils.messages import MESSAGES
from src.utils import logger as logger_utils
from .display import DisplayManager
from .interactive.collectors import ParameterCollector
from .interactive.presets_browser import PresetsBrowser
from .interactive.viz import VisualizationOrchestrator


class InteractiveCLI:
    """
    Interactive command-line interface for quantum experiments.

    This class handles the interactive session, including parameter
    collection, experiment selection, and user interaction.
    """

    def __init__(self):
        """Initialize the interactive CLI."""
        self.console = Console()
        self.help_manager = HelpManager(self.console)
        self.input_handler = InputHandler(
            self.console, MESSAGES, help_manager=self.help_manager
        )
        self.display_manager = DisplayManager(self.console)
        # Initialize logger once for interactive mode, suppress duplicate handlers
        self.logger = logger_utils.setup_logger(
            log_level="INFO",
            log_to_file=True,
            log_to_console=True,
            structured_log_file="logs/structured_logs.json",
        )
        # Tame noisy third-party loggers
        try:
            import logging as _logging

            _logging.getLogger("qiskit").setLevel(_logging.WARNING)
            _logging.getLogger("qiskit_aer").setLevel(_logging.WARNING)
            # Prevent propagation to root to avoid duplicates
            self.logger.propagate = False
        except Exception:
            pass

    def print_message(self, key: str, **kwargs) -> None:
        """
        Print a console message from the MESSAGES lookup table.

        Args:
            key (str): The key to look up the message in MESSAGES.
            **kwargs: Values to format the message with.
        """
        message = MESSAGES.get(
            key, f"[bold red]Missing prompt for key: {key}[/bold red]"
        )
        self.console.print(message.format(**kwargs))

    def display_quick_options(self) -> None:
        # Minimal curated preset overview only (difficulty removed in Phase 8)
        table = Table(
            title="🚀 Quick Start Presets",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Key", style="cyan", width=14)
        table.add_column("Name", style="green", width=28)
        table.add_column("Family", style="blue", width=12)
        table.add_column("Description", style="yellow")
        curated = [
            ("ghz_basic", "GHZ State Basics", "GHZ", "3-qubit GHZ state baseline"),
            ("ghz_noise", "GHZ with Noise", "GHZ", "GHZ with depolarizing noise"),
            (
                "density_analysis",
                "Density Matrix Analysis",
                "GHZ",
                "Statevector analysis for GHZ",
            ),
            (
                "ghz_structured_decoherence_ref",
                "Structured Decoherence (Ref)",
                "GHZ",
                "Research preset",
            ),
        ]
        for key, name, family, desc in curated:
            table.add_row(key, name, family, desc)
        self.console.print(table)

    def collect_parameters(
        self,
        interactive: bool = True,
        base_args: Optional[Dict[str, Any]] = None,
        force_state_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        collector = ParameterCollector(self.input_handler, self.display_manager)
        return collector.collect_parameters(
            interactive=interactive,
            base_args=base_args,
            force_state_type=force_state_type,
        )

    def _collect_custom_state_params(
        self, default_num_qubits: int
    ) -> Optional[Dict[str, Any]]:
        """Collect parameters for CustomState (source: gates|builder|openqasm).

        Returns None if the user cancels.
        """
        custom_params: Dict[str, Any] = {}
        # Optional template quick-pick
        # Show only templates relevant to the current qubit count for a smoother UX
        relevant_templates = [
            ("none", "None", "n"),
            ("bell_phi_plus", "Bell |Φ+> (2 qubits)", "1"),
            ("w3_gate", "W(3) gate-based", "2"),
            ("cluster_1d_3", "Cluster 1D (3)", "3"),
            ("ghz_3", "GHZ (3) via gates", "4"),
            ("cancel", "Cancel and go back", "q"),
        ]
        # Filter by target qubits
        filtered_templates = [
            (v, l, h)
            for (v, l, h) in relevant_templates
            if (
                v in {"none", "cancel"}
                or (v == "bell_phi_plus" and default_num_qubits == 2)
                or (
                    v in {"w3_gate", "cluster_1d_3", "ghz_3"}
                    and default_num_qubits == 3
                )
            )
        ]
        template_choice = self.input_handler.select_option(
            title="Custom Templates (optional)",
            options=filtered_templates or [("cancel", "Cancel and go back", "q")],
            default_value="none",
            show_value_column=False,
        )
        if template_choice == "cancel":
            return None
        if template_choice == "bell_phi_plus":
            return {
                "source": "gates",
                "num_qubits": 2,
                "gates": [
                    {"name": "h", "qargs": [0]},
                    {"name": "cx", "qargs": [0, 1]},
                ],
            }
        if template_choice == "w3_gate":
            return {
                "source": "gates",
                "num_qubits": 3,
                "gates": [
                    {"name": "u3", "params": [1.910633, 0, 0], "qargs": [0]},
                    {"name": "cx", "qargs": [0, 1]},
                    {"name": "u3", "params": [-1.910633, 0, 0], "qargs": [0]},
                    {"name": "u3", "params": [1.230959, 0, 0], "qargs": [0]},
                    {"name": "cx", "qargs": [0, 2]},
                    {"name": "u3", "params": [-1.230959, 0, 0], "qargs": [0]},
                ],
            }
        if template_choice == "cluster_1d_3":
            return {
                "source": "gates",
                "num_qubits": 3,
                "gates": [
                    {"name": "h", "qargs": [0]},
                    {"name": "h", "qargs": [1]},
                    {"name": "h", "qargs": [2]},
                    {"name": "cz", "qargs": [0, 1]},
                    {"name": "cz", "qargs": [1, 2]},
                ],
            }
        if template_choice == "ghz_3":
            return {
                "source": "gates",
                "num_qubits": 3,
                "gates": [
                    {"name": "h", "qargs": [0]},
                    {"name": "cx", "qargs": [0, 1]},
                    {"name": "cx", "qargs": [1, 2]},
                ],
            }
        # Choose source with Advanced toggle (default simple)
        self.display_manager.display_info_message(
            "Simple: Gates JSON (recommended). Advanced: Python builder/OpenQASM (experts)."
        )
        advanced_enabled = False
        source: Optional[str] = None
        while True:
            source_options = [("gates", "Gates JSON", "g")]
            if not advanced_enabled:
                source_options.append(
                    ("advanced", "Show advanced (builder/OpenQASM)", "a")
                )
            else:
                source_options.extend(
                    [
                        ("builder", "Python builder (module:function)", "b"),
                        ("openqasm", "OpenQASM file", "o"),
                    ]
                )
            source_options.append(("cancel", "Cancel and go back", "q"))

            choice = self.input_handler.select_option(
                title="Custom Circuit Source",
                options=source_options,
                default_value="gates",
                show_value_column=False,
            )
            if choice == "advanced":
                advanced_enabled = True
                continue
            if choice == "cancel":
                return None
            source = choice
            break
        custom_params["source"] = source

        # Common validate flag
        validate = self.input_handler.prompt_yes_no("custom_state_validate_prompt", "y")
        custom_params["validate"] = bool(validate)

        if source == "gates":
            # Require num_qubits and gates JSON
            custom_params["num_qubits"] = default_num_qubits
            self.display_manager.display_info_message(
                'Example: [{"name":"h","qargs":[0]},{"name":"cx","qargs":[0,1}]'
            )
            import json as _json

            while True:
                gates_json = self.input_handler.get_input(
                    "custom_state_gates_json_prompt", '[{"name":"h","qargs":[0]}]'
                )
                try:
                    gates = _json.loads(gates_json.replace("'", '"'))
                except Exception as e:
                    self.display_manager.display_error_message(f"Invalid JSON: {e}")
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                ok, reason = self._validate_gates_list(gates)
                if not ok:
                    self.display_manager.display_error_message(
                        f"Invalid gates specification: {reason}"
                    )
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                custom_params["gates"] = gates
                break
        elif source == "builder":
            self.display_manager.display_info_message(
                "Provide a dotted path to a callable that builds and returns a QuantumCircuit."
            )
            while True:
                builder = self.input_handler.get_input(
                    "custom_state_builder_prompt", "mypkg.builders:make_qc"
                )
                if ":" not in builder or builder.count(":") != 1:
                    self.display_manager.display_error_message(
                        "Builder must be in the form 'module.sub:func'"
                    )
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                custom_params["builder"] = builder
                break
            custom_params["num_qubits"] = default_num_qubits
        else:  # openqasm
            self.display_manager.display_info_message(
                "Enter a local path to a .qasm file compatible with Qiskit parser."
            )
            from pathlib import Path as _Path

            while True:
                qasm_path = self.input_handler.get_input(
                    "custom_state_qasm_path_prompt", "path/to/circuit.qasm"
                )
                if not _Path(qasm_path).exists():
                    self.display_manager.display_warning_message(
                        "Path not found. Ensure the file exists."
                    )
                    if not self.input_handler.prompt_yes_no(
                        "custom_state_validate_prompt", "y"
                    ):
                        return None
                    continue
                custom_params["openqasm"] = qasm_path
                break
            # optional num_qubits; default to current selection
            custom_params["num_qubits"] = default_num_qubits

        return custom_params

    @staticmethod
    def _validate_gates_list(gates_obj: Any) -> tuple[bool, str]:
        """Validate a gates JSON structure for CustomState.

        Expect a list of {name: str, qargs: list[int], params?: list[number]}.
        """
        if not isinstance(gates_obj, list):
            return False, "Expected a list of gate objects"
        for idx, item in enumerate(gates_obj):
            if not isinstance(item, dict):
                return False, f"Item {idx} must be an object"
            if "name" not in item or "qargs" not in item:
                return False, f"Item {idx} missing 'name' or 'qargs'"
            if not isinstance(item["name"], str):
                return False, f"Item {idx} 'name' must be string"
            if not isinstance(item["qargs"], list) or not all(
                isinstance(q, int) for q in item["qargs"]
            ):
                return False, f"Item {idx} 'qargs' must be list of integers"
            if "params" in item and not isinstance(item["params"], list):
                return False, f"Item {idx} 'params' must be a list if provided"
        return True, ""

    def _preview_custom_circuit(
        self, num_qubits: int, custom_params: Dict[str, Any]
    ) -> None:
        """Validate and preview a CustomState circuit (basic summary)."""
        from src.core.state_preparation.custom_state import CustomState

        try:
            cs = CustomState(num_qubits=num_qubits, custom_params=custom_params)
            qc = cs.create(add_barrier=False)
        except Exception as e:
            self.console.print(
                MESSAGES.get(
                    "custom_invalid_params", "Invalid custom parameters: {reason}"
                ).format(reason=str(e))
            )
            return
        # Show brief summary
        table = Table(title="Custom Circuit Preview")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Qubits", str(qc.num_qubits))
        try:
            table.add_row("Depth", str(qc.depth()))
            table.add_row("Gates", str(len(qc.data)))
        except Exception:
            pass
        self.console.print(table)

    def run_quick_experiment(self, choice: str) -> Dict[str, Any]:
        """
        Run a quick experiment based on user choice.

        Args:
            choice (str): The experiment choice from the user.

        Returns:
            Dict[str, Any]: The experiment configuration.
        """
        if choice == "c":
            return self.collect_parameters(interactive=True)

        # This part of the logic needs to be refactored to use the new PresetsBrowser
        # For now, we'll just return a default or raise an error if the choice is not handled
        # This will be addressed in a subsequent edit.
        self.print_message("invalid_choice")
        return self.collect_parameters(interactive=True)

    def browse_presets(self, include_keys: Optional[list] = None) -> Dict[str, Any]:
        browser = PresetsBrowser(self.input_handler, self.display_manager, self.console)
        args = browser.browse(include_keys=include_keys)
        return validate_parameters(apply_defaults(args))

    def show_preset_details(self, key: str, meta: Dict[str, Any]) -> None:
        table = Table(title=f"Preset: {meta.get('name', key)}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        cfg = meta.get("config", {})
        table.add_row("Description", meta.get("description", "-"))
        table.add_row("Category", meta.get("category", "-"))
        # Prefer experiment family over difficulty in the UI
        fam = meta.get("family", cfg.get("state_type", "-"))
        table.add_row("Family", str(fam))
        table.add_row("State", str(cfg.get("state_type", "-")))
        table.add_row("Qubits", str(cfg.get("num_qubits", "-")))
        table.add_row("Noise", str(cfg.get("noise_type", "-")))
        table.add_row("Noise Enabled", str(cfg.get("noise_enabled", False)))
        table.add_row("Error Rate", str(cfg.get("error_rate", "-")))
        table.add_row("Shots", str(cfg.get("shots", "-")))
        table.add_row("Sim Mode", str(cfg.get("sim_mode", "-")))
        table.add_row("Viz Type", str(cfg.get("visualization_type", "-")))
        if "research_type" in meta:
            table.add_row("Research Type", str(meta.get("research_type")))
        # Expected outputs (if provided)
        exp = meta.get("expected_outcomes")
        if exp:
            table.add_row("Expected Outcomes", str(exp))
        # Estimated runtime (heuristic)
        try:
            nq = int(cfg.get("num_qubits", 3))
            shots = int(cfg.get("shots", 1024))
            sim = str(cfg.get("sim_mode", "qasm")).lower()
            noise = bool(cfg.get("noise_enabled", False))
            # Heuristic coefficients
            base = 0.02 + 0.005 * max(0, nq - 2)
            per_shot = 0.000002 if sim == "qasm" else 0.0000005
            if noise:
                per_shot *= 1.5
                base += 0.01
            est = base + shots * per_shot
            table.add_row("Est. Runtime (s)", f"~{est:.2f}")
        except Exception:
            pass
        self.console.print(table)

    def _preview_preset_circuit(self, config: Dict[str, Any]) -> None:
        """Render a fast ASCII preview of the circuit from a preset config without running.

        Args:
            config: Preset configuration dict.
        """
        from src.core.state_preparation import prepare_state
        from qiskit import QuantumCircuit

        state_type = config.get("state_type", "GHZ")
        num_qubits = int(config.get("num_qubits", 3))
        custom_params = config.get("custom_params")
        qc = prepare_state(
            state_type=state_type,
            num_qubits=num_qubits,
            custom_params=custom_params,
            add_barrier=False,
            experiment_id="preview",
        )
        if hasattr(qc, "draw"):
            self.console.print("[bold]ASCII Circuit Preview:[/bold]")
            self.console.print(str(qc.draw(output="text", fold=-1)))

    def _show_visualization(self, results: Dict[str, Any], params: Dict[str, Any], viz_type: str) -> None:
        VisualizationOrchestrator(self.display_manager).show(results, params, viz_type)

    def show_recent_results(self, max_items: int = 10) -> None:
        from pathlib import Path

        base = Path("results")
        if not base.exists():
            self.print_message("no_results_found")
            return
        files = sorted(
            base.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        files = files[:max_items]
        if not files:
            self.print_message("no_results_found")
            return
        table = Table(title=MESSAGES.get("recent_results_title", "Recent Results"))
        table.add_column("#", style="cyan", width=4)
        table.add_column("Filename", style="green")
        table.add_column("Modified", style="yellow", width=20)
        table.add_column("Metric", style="magenta", width=12)
        for idx, f in enumerate(files, start=1):
            try:
                mtime = f.stat().st_mtime
                from datetime import datetime
                import json as _json

                ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                # Try to extract a key metric (normalized entropy)
                metric = "-"
                try:
                    with open(f, "r") as jf:
                        data = _json.load(jf)
                    info = data.get("research_metrics", {}).get(
                        "information_theory", {}
                    )
                    if "normalized_entropy" in info and isinstance(
                        info["normalized_entropy"], (int, float)
                    ):
                        metric = f"H_norm={info['normalized_entropy']:.3f}"
                except Exception:
                    metric = "-"
            except Exception:
                ts = "-"
                metric = "-"
            table.add_row(str(idx), str(f), ts, metric)
        self.console.print(table)
        # Actions: re-open viz or re-run (stubs)
        action = self.input_handler.select_option(
            title=MESSAGES.get("recent_action_title", "Result Actions"),
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
        # Pick item
        idx_map = [(str(i), str(i), str(i)) for i in range(1, len(files) + 1)]
        pick = self.input_handler.select_option(
            title="Select Result",
            options=idx_map,
            default_value="1",
            show_value_column=False,
        )
        try:
            sel = int(pick)
            chosen = files[sel - 1]
        except Exception:
            return
        if action == "open":
            self.console.print(f"Opening: {chosen}")
            try:
                self._open_visualization_from_result_json(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(
                    f"Failed to open visualization: {e}"
                )
        elif action == "rerun":
            self.console.print(f"Re-running from: {chosen}")
            try:
                self._rerun_from_result_json(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(f"Failed to re-run: {e}")
        elif action == "compare":
            # pick second file
            pick2 = self.input_handler.select_option(
                title=MESSAGES.get("recent_compare_title", "Compare Results"),
                options=idx_map,
                default_value="2" if len(files) > 1 else "1",
                show_value_column=False,
            )
            try:
                sel2 = int(pick2)
                chosen2 = files[sel2 - 1]
            except Exception:
                return
            try:
                self._compare_results(str(chosen), str(chosen2))
                # Offer ideal deltas if same state/qubits
                if self.input_handler.prompt_yes_no("insights_details_prompt", "n"):
                    self._compare_vs_ideal(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(f"Failed to compare: {e}")

    def _open_visualization_from_result_json(self, file_path: str) -> None:
        import json as _json

        with open(file_path, "r") as f:
            analysis = _json.load(f)
        self._last_research_analysis = analysis
        params = analysis.get("experiment_parameters", {})
        counts = analysis.get("measurement_results", {}).get("raw_counts", {})
        # pick viz type
        viz = self.input_handler.select_option(
            title="Visualization Type",
            options=[
                ("histogram", "Histogram", "h"),
                ("density_matrix", "Density Matrix", "d"),
                ("hypergraph", "Hypergraph", "g"),
            ],
            default_value="histogram",
            show_value_column=False,
        )
        # Display params summary then viz
        args = apply_defaults(params)
        args["visualization_type"] = viz
        self.display_manager.display_params_summary(args)
        # For histogram/hypergraph we pass counts; for density we cannot reconstruct DM here
        self._show_visualization({"counts": counts}, args, viz)

    def _rerun_from_result_json(self, file_path: str) -> None:
        import json as _json
        from src.experiments.manager import get_experiment_manager
        from src.core.research_handler import ResearchExperimentHandler

        with open(file_path, "r") as f:
            analysis = _json.load(f)
        params = analysis.get("experiment_parameters", {})
        args = apply_defaults(params)
        self.display_manager.display_params_summary(args)
        if self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) != "y":
            return
        self.display_manager.display_info_message("🚀 Running quantum experiment...")
        em = get_experiment_manager()
        experiment_params = {
            k: v
            for k, v in args.items()
            if k not in ["name", "description", "category", "difficulty"]
        }
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
                    self._show_visualization(raw_results, experiment_params, viz_type)
                self.display_manager.display_success_message(
                    f"📊 Research-grade analysis saved: {research_file}"
                )
        else:
            self.display_manager.display_experiment_results(result)
            self.display_manager.display_info_message(
                "🔬 Density Matrix Mode: Displaying quantum state analysis"
            )
            viz_type = experiment_params.get("visualization_type", "none")
            if viz_type and viz_type != "none":
                if isinstance(result, tuple) and len(result) >= 2:
                    _c, raw_results = result
                    self._show_visualization(raw_results, experiment_params, viz_type)
                else:
                    self._show_visualization(result, experiment_params, viz_type)

    def _compare_results(self, file_a: str, file_b: str) -> None:
        import json as _json
        from math import isclose
        import matplotlib.pyplot as _plt

        with open(file_a, "r") as fa, open(file_b, "r") as fb:
            a = _json.load(fa)
            b = _json.load(fb)
        a_metrics = a.get("research_metrics", {})
        b_metrics = b.get("research_metrics", {})
        a_info = a_metrics.get("information_theory", {})
        b_info = b_metrics.get("information_theory", {})
        table = Table(title="Result Comparison (Information Theory)")
        table.add_column("Metric", style="cyan")
        table.add_column("A", style="green")
        table.add_column("B", style="yellow")
        table.add_column("Δ (B-A)", style="magenta")
        for key in sorted(set(a_info.keys()) | set(b_info.keys())):
            av = a_info.get(key, None)
            bv = b_info.get(key, None)
            if isinstance(av, (int, float)) or isinstance(bv, (int, float)):
                try:
                    delta = (bv or 0) - (av or 0)
                    table.add_row(key, f"{av}", f"{bv}", f"{delta:+.6f}")
                except Exception:
                    table.add_row(key, str(av), str(bv), "-")
            else:
                table.add_row(key, str(av), str(bv), "-")
        self.console.print(table)

        # Mini chart: bar of normalized entropy for A vs B if available
        try:
            a_h = a_info.get("normalized_entropy")
            b_h = b_info.get("normalized_entropy")
            if isinstance(a_h, (int, float)) and isinstance(b_h, (int, float)):
                _plt.figure(figsize=(4, 3))
                _plt.bar(["A", "B"], [a_h, b_h], color=["#1f77b4", "#ff7f0e"])
                _plt.title("Normalized Entropy")
                _plt.ylim(0, 1)
                _plt.tight_layout()
                _plt.show()
        except Exception:
            pass

    def _compare_vs_ideal(self, file_path: str) -> None:
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
        # Align keys
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

    def show_settings_stub(self) -> None:
        # Display current defaults; editing will be added later
        from src.config.settings import settings

        table = Table(title="Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("DEFAULT_NUM_QUBITS", str(settings.DEFAULT_NUM_QUBITS))
        table.add_row("DEFAULT_STATE_TYPE", str(settings.DEFAULT_STATE_TYPE))
        table.add_row("DEFAULT_NOISE_TYPE", str(settings.DEFAULT_NOISE_TYPE))
        table.add_row("DEFAULT_NOISE_ENABLED", str(settings.DEFAULT_NOISE_ENABLED))
        table.add_row("DEFAULT_SHOTS", str(settings.DEFAULT_SHOTS))
        table.add_row("DEFAULT_SIM_MODE", str(settings.DEFAULT_SIM_MODE))
        table.add_row("DEFAULT_ERROR_RATE", str(settings.DEFAULT_ERROR_RATE))
        table.add_row("RESULTS_DIR", str(settings.DEFAULT_RESULTS_DIR))
        table.add_row("LOGS_DIR", str(settings.DEFAULT_LOGS_DIR))
        self.console.print(table)

        # Actions stub (Profiles/Editing soon)
        try:
            self.display_manager.display_footer_hints(["p=profiles", "b=back"])
        except Exception:
            pass
        action = self.input_handler.select_option(
            title="Settings Actions",
            options=[
                ("back", "Back", "b"),
                ("edit", "Edit Settings", "e"),
                ("profiles_save", "Save Profile", "s"),
                ("profiles_load", "Load Profile", "l"),
            ],
            default_value="back",
            show_value_column=False,
        )
        if action == "edit":
            # Simple inline editor for common fields
            try:
                new_shots = self.input_handler.get_numeric_input(
                    "shots_prompt", str(settings.DEFAULT_SHOTS), int
                )
                new_err = self.input_handler.get_numeric_input(
                    "error_rate_prompt", str(settings.DEFAULT_ERROR_RATE), float
                )
                settings.DEFAULT_SHOTS = int(new_shots)
                settings.DEFAULT_ERROR_RATE = float(new_err)
                # Optional: visualization backend
                backend_choice = self.input_handler.get_input(
                    "visualization_type_prompt",
                    "histogram",
                    ["matplotlib", "plotly"],
                    ["matplotlib", "plotly"],
                ).lower()
                try:
                    from src.visualization.backends import set_visualization_backend

                    set_visualization_backend(
                        "plotly" if backend_choice == "plotly" else "matplotlib"
                    )
                except Exception:
                    pass
                # Optional: save base dir
                save_base = self.input_handler.get_input(
                    "custom_state_qasm_path_prompt", "results/visualizations"
                )
                try:
                    from src.visualization.save_manager import (
                        set_save_manager_base_dir,
                    )

                    set_save_manager_base_dir(save_base)
                except Exception:
                    pass
                self.display_manager.display_success_message(
                    "✅ Updated settings (shots, error_rate, viz backend, save dir)"
                )
            except Exception as e:
                self.display_manager.display_error_message(
                    f"Failed to edit settings: {e}"
                )
            return
        if action in {"profiles_save", "profiles_load"}:
            try:
                from src.config import profiles as _profiles

                if action == "profiles_save":
                    name = self.input_handler.get_input(
                        "custom_template_prompt", "default"
                    )
                    path = _profiles.save_profile(name)
                    self.display_manager.display_success_message(
                        f"✅ Saved profile to {path}"
                    )
                else:
                    existing = _profiles.list_profiles()
                    if not existing:
                        self.display_manager.display_info_message("No profiles found.")
                    else:
                        # Simple selector by number
                        options = [(n, n, n[0]) for n in existing]
                        pick = self.input_handler.select_option(
                            "Select Profile",
                            options,
                            existing[0],
                            show_value_column=False,
                        )
                        prof = _profiles.load_profile(pick)
                        _profiles.apply_profile(prof)
                self.display_manager.display_success_message(
                    f"✅ Loaded profile '{pick}'"
                )
                # After applying a profile, refresh save manager and optionally backend
                try:
                    from src.visualization.save_manager import set_save_manager_base_dir

                    set_save_manager_base_dir(
                        settings.DEFAULT_RESULTS_DIR + "/visualizations"
                    )
                except Exception:
                    pass
            except Exception as e:
                self.display_manager.display_error_message(
                    f"Profile operation failed: {e}"
                )

    def _show_help_menu(self) -> None:
        # Minimal glossary stub
        glossary = {
            "depolarizing": "A noise channel that replaces the state with the maximally mixed state with probability p.",
            "phase_flip": "A noise channel that flips the phase (Z error) with some probability.",
            "density matrix": "Matrix representation of a quantum state supporting mixed states.",
            "counts": "Measurement outcome frequencies from shot-based simulations/experiments.",
            "fubini-study": "A distance measure on quantum states based on their projective Hilbert space geometry.",
        }
        term = self.input_handler.get_input("help_search_prompt", "")
        table = Table(title=MESSAGES.get("help_title", "Help & Glossary"))
        table.add_column("Term", style="cyan")
        table.add_column("Definition", style="green")
        items = (
            glossary.items()
            if not term
            else [
                (k, v)
                for k, v in glossary.items()
                if term.lower() in k.lower() or term.lower() in v.lower()
            ]
        )
        if not items:
            self.console.print("[yellow]No entries found.[/yellow]")
            return
        for k, v in items:
            table.add_row(k, v)
        self.console.print(table)

    def run_interactive_session(self) -> None:
        """
        Run the main interactive session loop.
        """
        while True:
            self.print_message("welcome")
            choice = self.input_handler.select_option(
                title="Main Menu",
                options=[
                    ("1", "Quick Start (curated presets)", "1"),
                    ("2", "Browse Presets", "2"),
                    ("3", "Build Custom State", "3"),
                    ("4", "Recent Results", "4"),
                    ("5", "Settings", "5"),
                    ("q", "Quit", "q"),
                ],
                default_value="1",
                show_value_column=False,
            )
            try:
                self.display_manager.display_footer_hints(
                    ["numbers=select", "enter=default", "?=help", "q=quit"]
                )
            except Exception:
                pass

            if choice == "1":
                # Quick Start: curated subset of unified presets (beginner + research anchor)
                curated = [
                    "ghz_basic",
                    "ghz_noise",
                    "density_analysis",
                    "ghz_structured_decoherence_ref",
                ]
                try:
                    args = self.browse_presets(include_keys=curated)
                except KeyboardInterrupt:
                    continue
            elif choice == "2":
                # Browse presets
                try:
                    args = self.browse_presets()
                except KeyboardInterrupt:
                    continue
            elif choice == "3":
                # Build Custom State: go directly into wizard with forced CUSTOM state
                try:
                    args = self.collect_parameters(
                        interactive=True, force_state_type="CUSTOM"
                    )
                except KeyboardInterrupt:
                    # User cancelled within the custom wizard; return to main menu
                    continue
            elif choice == "4":
                self.show_recent_results()
                continue
            elif choice == "5":
                # Settings or Help menu stub selection
                sub = self.input_handler.select_option(
                    title="Settings & Help",
                    options=[
                        ("settings", "Settings", "s"),
                        ("noise_help", "Noise Types (help)", "n"),
                        ("help", "Help & Glossary", "h"),
                        ("back", "Back", "b"),
                    ],
                    default_value="settings",
                    show_value_column=False,
                )
                if sub == "settings":
                    self.show_settings_stub()
                elif sub == "noise_help":
                    from src.config.constants import VALID_NOISE_TYPES

                    t = Table(title="Available Noise Types")
                    t.add_column("Type", style="cyan")
                    t.add_column("Summary", style="green")
                    summaries = {
                        "DEPOLARIZING": "Uniform Pauli errors; mixes state with prob p",
                        "PHASE_FLIP": "Z errors with prob p (dephasing)",
                        "BIT_FLIP": "X errors with prob p (bit flips)",
                        "THERMAL_RELAXATION": "T1/T2 hardware-like relaxation",
                        "AMPLITUDE_DAMPING": "Energy loss (|1>→|0>)",
                        "PHASE_DAMPING": "Pure dephasing without energy loss",
                    }
                    for nt in VALID_NOISE_TYPES:
                        t.add_row(nt, summaries.get(nt, "-"))
                    self.console.print(t)
                elif sub == "help":
                    self._show_help_menu()
                continue
            elif choice == "q":
                self.print_message("goodbye")
                return
            else:
                self.print_message("invalid_choice")
                continue

            # Normalize and display parameter summary
            normalized = validate_parameters(apply_defaults(args))
            self.display_manager.display_params_summary(normalized)

            # Confirm before running
            if self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) != "y":
                # Open Edit with current values instead of exiting
                try:
                    args = self.collect_parameters(
                        interactive=True, base_args=normalized
                    )
                    normalized = validate_parameters(apply_defaults(args))
                    self.display_manager.display_params_summary(normalized)
                except Exception:
                    self.print_message("params_discarded")
                    continue

                # Run the experiment with research-grade analysis
            try:
                from src.experiments.manager import get_experiment_manager
                from src.core.research_handler import ResearchExperimentHandler

                self.display_manager.display_info_message(
                    "🚀 Running quantum experiment..."
                )

                # Get experiment manager and run experiment
                em = get_experiment_manager()

                # Run experiment using user parameters as custom params
                # Filter out metadata that shouldn't go to the experiment runner
                experiment_params = {
                    k: v
                    for k, v in normalized.items()
                    if k not in ["name", "description", "category", "difficulty"]
                }

                result = em.run_experiment("ghz_basic", custom_params=experiment_params)

                if result:
                    # Check if this is a density matrix experiment
                    is_density_experiment = (
                        experiment_params.get("sim_mode") == "density"
                    )

                    if not is_density_experiment:
                        # Process with research handler for advanced analysis (only for count-based experiments)
                        research_handler = ResearchExperimentHandler()

                        if isinstance(result, tuple) and len(result) >= 2:
                            circuit, raw_results = result

                            # Generate research-grade analysis
                            research_analysis = (
                                research_handler.process_experiment_result(
                                    circuit=circuit,
                                    result=raw_results,
                                    experiment_config=experiment_params,
                                    experiment_id="cli_experiment",
                                )
                            )

                            # Store research analysis for visualization access
                            self._last_research_analysis = research_analysis

                            # Save research results
                            research_file = research_handler.save_research_result(
                                research_analysis
                            )

                            # Display comprehensive results including circuit diagram
                            self.display_manager.display_experiment_results(result)

                            # Show visualization if requested
                            viz_type = experiment_params.get(
                                "visualization_type", "none"
                            )
                            if viz_type and viz_type != "none":
                                self._show_visualization(
                                    raw_results, experiment_params, viz_type
                                )

                            # Show research report and optional details
                            self.display_manager.display_research_report(
                                research_analysis
                            )
                            if self.input_handler.prompt_yes_no(
                                "insights_details_prompt", "n"
                            ):
                                self.display_manager.display_research_details(
                                    research_analysis
                                )

                            # Show research file saved
                            self.display_manager.display_success_message(
                                f"📊 Research-grade analysis saved: {research_file}"
                            )

                        else:
                            # Fallback to basic display for research mode
                            self.display_manager.display_experiment_results(result)

                    else:
                        # For density matrix experiments, skip research processing and go straight to visualization
                        self.display_manager.display_experiment_results(result)
                        self.display_manager.display_info_message(
                            "🔬 Density Matrix Mode: Displaying quantum state analysis"
                        )

                        # Show visualization if requested
                        viz_type = experiment_params.get("visualization_type", "none")
                        if viz_type and viz_type != "none":
                            if isinstance(result, tuple) and len(result) >= 2:
                                circuit, raw_results = result
                                self._show_visualization(
                                    raw_results, experiment_params, viz_type
                                )
                            else:
                                self._show_visualization(
                                    result, experiment_params, viz_type
                                )

                    self.display_manager.display_success_message(
                        "✅ Experiment completed successfully!"
                    )
                else:
                    self.display_manager.display_error_message("❌ Experiment failed")

            except Exception as e:
                self.display_manager.display_error_message(
                    f"❌ Error running experiment: {str(e)}"
                )
                continue


def run_interactive() -> None:
    """
    Run the interactive CLI session.

    This is the main entry point for the interactive mode.
    """
    cli = InteractiveCLI()
    cli.run_interactive_session()
