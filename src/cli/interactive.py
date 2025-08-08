"""
Interactive CLI module for the Quantum Experiment Framework.

This module handles the interactive command-line interface for running
quantum experiments with user-friendly prompts and rich output.
"""

import uuid
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table

from src.config.quick_experiments import QUICK_EXPERIMENTS, get_experiment_info
from src.experiments.presets import load_preset_experiments
from src.config.params import apply_defaults, validate_parameters
from src.utils.input_handler import InputHandler
from src.utils.messages import MESSAGES
from src.utils import logger as logger_utils
from .display import DisplayManager


class InteractiveCLI:
    """
    Interactive command-line interface for quantum experiments.

    This class handles the interactive session, including parameter
    collection, experiment selection, and user interaction.
    """

    def __init__(self):
        """Initialize the interactive CLI."""
        self.console = Console()
        self.input_handler = InputHandler(self.console, MESSAGES)
        self.display_manager = DisplayManager(self.console)
        self.logger = logger_utils.setup_logger(
            log_level="INFO",
            log_to_file=True,
            log_to_console=True,
            structured_log_file="logs/structured_logs.json",
        )

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
        """
        Display the available quick experiment options with categories and difficulty levels.
        """
        table = Table(
            title="🚀 Quick Experiment Options",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Name", style="green", width=25)
        table.add_column("Category", style="blue", width=12)
        table.add_column("Difficulty", style="magenta", width=12)
        table.add_column("Description", style="yellow")

        for key, option in QUICK_EXPERIMENTS.items():
            category = option.get("category", "unknown")
            difficulty = option.get("difficulty", "unknown")
            table.add_row(
                key, option["name"], category, difficulty, option["description"]
            )

        self.console.print(table)
        self.console.print(
            "\n💡 Choose an option number or press 'c' for custom parameters"
        )
        self.console.print(
            "📚 Categories: entanglement, topological, analysis, scaling, dynamics"
        )
        self.console.print("🎯 Difficulty: beginner, intermediate, advanced")

    def collect_parameters(
        self, interactive: bool = True, base_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect experiment parameters either interactively or from command-line arguments.

        Args:
            interactive (bool): Whether to collect parameters interactively.

        Returns:
            Dict[str, Any]: Collected experiment parameters.
        """
        # Start with default parameters (allow overriding defaults via base_args)
        args = apply_defaults(base_args or {})

        if interactive:
            # Interactive parameter collection using InputHandler
            self.display_manager.display_info_message(
                "🔧 Let's configure your quantum experiment!"
            )

            # Number of qubits
            num_qubits = self.input_handler.get_numeric_input(
                "num_qubits_prompt", str(args["num_qubits"]), expected_type=int
            )
            args["num_qubits"] = int(num_qubits)

            # State type with numeric and hotkeys
            state_options = [
                ("GHZ", "GHZ State", "g"),
                ("W", "W State", "w"),
                ("CLUSTER", "Cluster State", "c"),
                ("BELL", "Bell State", "b"),
                ("SUPERPOSITION", "Superposition (|+>^n)", "u"),
                ("CUSTOM", "Custom State", "m"),
                ("RANDOM", "Random State", "r"),
            ]
            args["state_type"] = self.input_handler.select_option(
                title="State Type",
                options=state_options,
                default_value=args["state_type"],
            )

            # Collect custom state parameters if needed
            if args["state_type"] == "CUSTOM":
                args["custom_params"] = self._collect_custom_state_params(
                    args["num_qubits"]
                )  # may include its own num_qubits

            # Noise configuration
            noise_enabled = self.input_handler.prompt_yes_no("enable_noise_prompt", "y")
            args["noise_enabled"] = noise_enabled

            if noise_enabled:
                noise_options = [
                    ("DEPOLARIZING", "Depolarizing", "d"),
                    ("PHASE_FLIP", "Phase Flip", "p"),
                    ("BIT_FLIP", "Bit Flip", "b"),
                    ("THERMAL_RELAXATION", "Thermal Relaxation", "t"),
                ]
                args["noise_type"] = self.input_handler.select_option(
                    title="Noise Type",
                    options=noise_options,
                    default_value=args.get("noise_type", "DEPOLARIZING"),
                )

                # Error rate (Enter keeps default shown)
                error_rate = self.input_handler.get_numeric_input(
                    "error_rate_prompt",
                    str(args.get("error_rate", 0.1)),
                    expected_type=float,
                )
                try:
                    args["error_rate"] = float(error_rate)
                except Exception:
                    # Keep current default if input was empty
                    pass

            # Shots
            shots = self.input_handler.get_numeric_input(
                "shots_prompt", str(args["shots"]), expected_type=int
            )
            args["shots"] = int(shots)

            # Simulation mode
            sim_mode = self.input_handler.select_option(
                title="Simulation Mode",
                options=[
                    ("qasm", "QASM (shots)", "q"),
                    ("statevector", "Statevector", "s"),
                ],
                default_value=args["sim_mode"],
            )
            args["sim_mode"] = sim_mode

            # Visualization preferences
            enable_viz = self.input_handler.prompt_yes_no(
                "enable_visualization_prompt", "y"
            )
            if enable_viz:
                viz_type = self.input_handler.select_option(
                    title="Visualization Type",
                    options=[
                        ("histogram", "Histogram", "h"),
                        ("density_matrix", "Density Matrix", "d"),
                        ("hypergraph", "Hypergraph", "g"),
                    ],
                    default_value="histogram",
                )
                args["visualization_type"] = viz_type
            else:
                args["visualization_type"] = "none"

        return validate_parameters(args)

    def _collect_custom_state_params(self, default_num_qubits: int) -> Dict[str, Any]:
        """Collect parameters for CustomState (source: gates|builder|openqasm)."""
        custom_params: Dict[str, Any] = {}
        # Optional template quick-pick
        template_choice = self.input_handler.select_option(
            title="Custom Templates (optional)",
            options=[
                ("none", "None", "n"),
                ("bell_phi_plus", "Bell |Φ+> (2 qubits)", "1"),
                ("w3_gate", "W(3) gate-based", "2"),
                ("cluster_1d_3", "Cluster 1D (3)", "3"),
            ],
            default_value="none",
        )
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
        # Choose source
        source = self.input_handler.get_input(
            "custom_state_source_prompt",
            "gates",
            valid_options=["gates", "builder", "openqasm"],
            valid_options_display=["GATES", "BUILDER", "OPENQASM"],
        )
        custom_params["source"] = source

        # Common validate flag
        validate = self.input_handler.prompt_yes_no("custom_state_validate_prompt", "y")
        custom_params["validate"] = bool(validate)

        if source == "gates":
            # Require num_qubits and gates JSON
            custom_params["num_qubits"] = default_num_qubits
            gates_json = self.input_handler.get_input(
                "custom_state_gates_json_prompt", "[{'name':'h','qargs':[0]}]"
            )
            try:
                import json as _json

                gates = _json.loads(gates_json.replace("'", '"'))
            except Exception:
                gates = []
            custom_params["gates"] = gates
        elif source == "builder":
            builder = self.input_handler.get_input(
                "custom_state_builder_prompt", "mypkg.builders:make_qc"
            )
            custom_params["builder"] = builder
            custom_params["num_qubits"] = default_num_qubits
        else:  # openqasm
            qasm_path = self.input_handler.get_input(
                "custom_state_qasm_path_prompt", "path/to/circuit.qasm"
            )
            custom_params["openqasm"] = qasm_path
            # optional num_qubits; default to current selection
            custom_params["num_qubits"] = default_num_qubits

        return custom_params

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

        if choice not in QUICK_EXPERIMENTS:
            self.print_message("invalid_choice")
            return self.collect_parameters(interactive=True)

        # Use predefined configuration
        selected_option = QUICK_EXPERIMENTS[choice]
        self.console.print(f"\n✅ Selected: {selected_option['name']}")
        args = apply_defaults(selected_option["config"])
        args = validate_parameters(args)

        return args

    def browse_presets(self, include_keys: Optional[list] = None) -> Dict[str, Any]:
        """
        Browse presets via a numeric/hotkey menu and return selected configuration.

        Args:
            include_keys: Optional list of preset keys to show. If None, show all.

        Returns:
            Dict[str, Any]: Validated experiment parameters.
        """
        # Load unified presets from registry
        unified = load_preset_experiments()
        # Build keys
        keys = list(unified.keys())
        if include_keys is not None:
            keys = [k for k in keys if k in include_keys]
        if not keys:
            keys = list(unified.keys())

        # Optional search/filter step
        # Category filter
        categories = sorted({unified[k].get("category", "?") for k in keys})
        categories = [c for c in categories if c]
        categories.insert(0, "all")
        cat_choice = self.input_handler.select_option(
            title="Filter by Category",
            options=[(c, c.title(), c[0] if c != "all" else "a") for c in categories],
            default_value="all",
        )
        if cat_choice != "all":
            keys = [k for k in keys if unified[k].get("category") == cat_choice]

        # Difficulty filter
        diffs = sorted({unified[k].get("difficulty", "?") for k in keys})
        diffs = [d for d in diffs if d]
        diffs.insert(0, "all")
        diff_choice = self.input_handler.select_option(
            title="Filter by Difficulty",
            options=[(d, d.title(), d[0] if d != "all" else "a") for d in diffs],
            default_value="all",
        )
        if diff_choice != "all":
            keys = [k for k in keys if unified[k].get("difficulty") == diff_choice]

        # Free-text search
        search_text = self.input_handler.get_input("preset_search_prompt", "", None)
        if search_text:
            st = search_text.lower()

            def match(meta: dict) -> bool:
                blob = " ".join(
                    [
                        meta.get("name", ""),
                        meta.get("description", ""),
                        meta.get("category", ""),
                        meta.get("difficulty", ""),
                    ]
                ).lower()
                return st in blob

            keys = [k for k in keys if match(unified[k])]

        options = []
        for k in keys:
            meta = unified[k]
            label = f"{meta['name']} [{meta.get('category','?')}/{meta.get('difficulty','?')}]"
            options.append((k, label, k))
        options.append(("c", "Custom Parameters", "c"))
        options.append(("q", "Back", "q"))

        choice = self.input_handler.select_option(
            title="Presets Browser",
            options=options,
            default_value=keys[0],
        )
        if choice == "q":
            # Go back to main menu by raising to caller
            raise KeyboardInterrupt
        # Convert preset to args
        selected = unified.get(choice)
        if choice == "c" or selected is None:
            return self.collect_parameters(interactive=True)

        # Detail pane
        self.show_preset_details(choice, selected)
        proceed = self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) == "y"
        if not proceed:
            # Offer clone & edit
            clone_or_back = self.input_handler.select_option(
                title="Clone & Edit?",
                options=[("clone", "Clone and Edit", "c"), ("back", "Back", "b")],
                default_value="back",
            )
            if clone_or_back == "clone":
                return self.collect_parameters(
                    interactive=True, base_args=selected.get("config", {})
                )
            raise KeyboardInterrupt

        args = apply_defaults(selected.get("config", {}))
        return validate_parameters(args)

    def show_preset_details(self, key: str, meta: Dict[str, Any]) -> None:
        table = Table(title=f"Preset: {meta.get('name', key)}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        cfg = meta.get("config", {})
        table.add_row("Description", meta.get("description", "-"))
        table.add_row("Category", meta.get("category", "-"))
        table.add_row("Difficulty", meta.get("difficulty", "-"))
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
        self.console.print(table)

    def _show_visualization(
        self, results: Dict[str, Any], params: Dict[str, Any], viz_type: str
    ) -> None:
        """
        Display visualization based on user preference.

        Args:
            results: Experiment results containing counts and other data
            params: Experiment parameters
            viz_type: Type of visualization (histogram, density_matrix, hypergraph)
        """
        try:
            self.display_manager.display_info_message(
                f"🎨 Generating {viz_type} visualization..."
            )

            # Handle different result types
            if viz_type == "density_matrix":
                # For density matrix visualization, we don't need counts
                counts = {}
            else:
                # Extract counts from results for other visualization types
                if hasattr(results, "get"):
                    counts = results.get("counts", {})
                else:
                    # If results is not a dict (e.g., DensityMatrix object), we can't extract counts
                    self.display_manager.display_warning_message(
                        "⚠️ No measurement data available for visualization"
                    )
                    return

                if not counts:
                    self.display_manager.display_warning_message(
                        "⚠️ No measurement data available for visualization"
                    )
                    return

            # Get visualization parameters
            num_qubits = params.get("num_qubits", 3)
            state_type = params.get("state_type", "GHZ")
            noise_type = params.get("noise_type", "DEPOLARIZING")
            noise_enabled = params.get("noise_enabled", True)

            # Import visualization functions (lazy loading)
            if viz_type == "histogram":
                from src.visualization import get_histogram_visualizer

                plot_function = get_histogram_visualizer()

                # Get research metrics if available from the research handler
                research_metrics = None
                if hasattr(self, "_last_research_analysis"):
                    research_metrics = self._last_research_analysis.get(
                        "research_metrics"
                    )

                plot_function(
                    counts=counts,
                    state_type=state_type,
                    noise_type=noise_type,
                    noise_enabled=noise_enabled,
                    num_qubits=num_qubits,
                    research_metrics=research_metrics,
                    save_path=None,  # Display only, don't save
                )

            elif viz_type == "density_matrix":
                from src.visualization import get_density_matrix_visualizer

                # Check if we have density matrix data
                if params.get("sim_mode") != "density":
                    self.display_manager.display_warning_message(
                        "⚠️ Density matrix visualization requires density simulation mode"
                    )
                    return

                # For density mode, results may be the density matrix directly or in a dict
                if hasattr(results, "data") and hasattr(results, "draw"):
                    # Direct DensityMatrix object
                    density_matrix = results
                elif isinstance(results, dict) and "density_matrix" in results:
                    # Dictionary containing density matrix
                    density_matrix = results["density_matrix"]
                else:
                    self.display_manager.display_warning_message(
                        "⚠️ No density matrix data available"
                    )
                    return

                # Get research metrics if available
                research_metrics = None
                if hasattr(self, "_last_research_analysis"):
                    research_metrics = self._last_research_analysis.get(
                        "research_metrics"
                    )

                plot_function = get_density_matrix_visualizer()
                plot_function(
                    density_matrix,
                    state_type=state_type,
                    noise_type=noise_type,
                    research_metrics=research_metrics,
                )

            elif viz_type == "hypergraph":
                from src.visualization import get_hypergraph_visualizer

                plot_function = get_hypergraph_visualizer()
                plot_function(
                    correlation_data=counts,
                    state_type=state_type,
                    noise_type=noise_type,
                    config={},  # Provide empty config to avoid None comparison issues
                )

            self.display_manager.display_success_message(
                f"✅ {viz_type.title()} visualization displayed!"
            )

        except Exception as e:
            self.display_manager.display_error_message(
                f"❌ Visualization error: {str(e)}"
            )

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
        for idx, f in enumerate(files, start=1):
            try:
                mtime = f.stat().st_mtime
                from datetime import datetime

                ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                ts = "-"
            table.add_row(str(idx), str(f), ts)
        self.console.print(table)
        # Actions: re-open viz or re-run (stubs)
        action = self.input_handler.select_option(
            title=MESSAGES.get("recent_action_title", "Result Actions"),
            options=[
                ("back", "Back", "b"),
                ("open", "Open Visualization", "o"),
                ("rerun", "Re-run", "r"),
            ],
            default_value="back",
        )
        if action == "back":
            return
        # Pick item
        idx_map = [(str(i), str(i), str(i)) for i in range(1, len(files) + 1)]
        pick = self.input_handler.select_option(
            title="Select Result",
            options=idx_map,
            default_value="1",
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
                self.display_manager.display_error_message(f"Failed to open visualization: {e}")
        elif action == "rerun":
            self.console.print(f"Re-running from: {chosen}")
            try:
                self._rerun_from_result_json(str(chosen))
            except Exception as e:
                self.display_manager.display_error_message(f"Failed to re-run: {e}")

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
                    self._show_visualization(raw_results, experiment_params, viz_type)
                self.display_manager.display_success_message(
                    f"📊 Research-grade analysis saved: {research_file}"
                )
        else:
            self.display_manager.display_experiment_results(result)
            self.display_manager.display_info_message("🔬 Density Matrix Mode: Displaying quantum state analysis")
            viz_type = experiment_params.get("visualization_type", "none")
            if viz_type and viz_type != "none":
                if isinstance(result, tuple) and len(result) >= 2:
                    _c, raw_results = result
                    self._show_visualization(raw_results, experiment_params, viz_type)
                else:
                    self._show_visualization(result, experiment_params, viz_type)

    def show_settings_stub(self) -> None:
        # Display current defaults; editing will be added later
        from src.config.settings import settings

        table = Table(title="Settings (read-only)")
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
            )

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
                # Force CUSTOM path
                args = self.collect_parameters(interactive=True)
                args["state_type"] = "CUSTOM"
                args["custom_params"] = self._collect_custom_state_params(
                    args["num_qubits"]
                )
            elif choice == "4":
                self.show_recent_results()
                continue
            elif choice == "5":
                self.show_settings_stub()
                continue
            elif choice == "q":
                self.print_message("goodbye")
                return
            else:
                self.print_message("invalid_choice")
                continue

            # Display parameter summary
            self.display_manager.display_params_summary(args)

            # Confirm before running
            if self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) != "y":
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
                    for k, v in args.items()
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

                            # Show research insights
                            if "research_insights" in research_analysis:
                                insights = research_analysis["research_insights"]
                                if insights.get("key_findings"):
                                    self.display_manager.display_info_message(
                                        "🔬 Research Insights:"
                                    )
                                    for finding in insights["key_findings"]:
                                        self.display_manager.display_info_message(
                                            f"  • {finding}"
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
