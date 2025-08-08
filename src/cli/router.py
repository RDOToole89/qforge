# src/cli/router.py

from __future__ import annotations

from typing import Dict, Any, Optional

from rich.table import Table

from .interactive.collectors import ParameterCollector
from .interactive.presets_browser import PresetsBrowser
from .interactive.viz import VisualizationOrchestrator
from .interactive.results import ResultsManager
from .interactive.settings import SettingsUI
from src.config.params import apply_defaults, validate_parameters


class Router:
    """Interactive menu router that orchestrates the main CLI loop."""

    def __init__(self, console, input_handler, display_manager):
        self.console = console
        self.input_handler = input_handler
        self.display_manager = display_manager
        # Components
        self.collector = ParameterCollector(input_handler, display_manager)
        self.browser = PresetsBrowser(input_handler, display_manager, console)
        self.results = ResultsManager(console, input_handler, display_manager)
        self.viz = VisualizationOrchestrator(display_manager)
        self.settings = SettingsUI(console, input_handler, display_manager)

    def display_quick_options(self) -> None:
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

    def run(self) -> None:
        from src.utils.messages import MESSAGES

        while True:
            self.console.print(MESSAGES.get("welcome", "Welcome"))
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
                self.display_quick_options()
                try:
                    args = self.browser.browse(
                        include_keys=[
                            "ghz_basic",
                            "ghz_noise",
                            "density_analysis",
                            "ghz_structured_decoherence_ref",
                        ]
                    )
                except KeyboardInterrupt:
                    continue
            elif choice == "2":
                try:
                    args = self.browser.browse()
                except KeyboardInterrupt:
                    continue
            elif choice == "3":
                try:
                    args = self.collector.collect_parameters(
                        interactive=True, force_state_type="CUSTOM"
                    )
                except KeyboardInterrupt:
                    continue
            elif choice == "4":
                self.results.show_recent_results()
                continue
            elif choice == "5":
                sub = self.input_handler.select_option(
                    title="Settings & Help",
                    options=[
                        ("settings", "Settings", "s"),
                        ("help", "Help & Glossary", "h"),
                        ("back", "Back", "b"),
                    ],
                    default_value="settings",
                    show_value_column=False,
                )
                if sub == "settings":
                    self.settings.show()
                elif sub == "help":
                    self._show_help_menu()
                continue
            elif choice == "q":
                self.console.print(MESSAGES.get("goodbye", "Goodbye"))
                return
            else:
                self.console.print(MESSAGES.get("invalid_choice", "Invalid choice"))
                continue

            # Normalize and display parameter summary
            normalized = validate_parameters(apply_defaults(args))
            self.display_manager.display_params_summary(normalized)

            # Confirm before running
            if self.input_handler.get_input("proceed_prompt", "y", ["y", "n"]) != "y":
                try:
                    args = self.collector.collect_parameters(
                        interactive=True, base_args=normalized
                    )
                    normalized = validate_parameters(apply_defaults(args))
                    self.display_manager.display_params_summary(normalized)
                except Exception:
                    self.console.print(
                        MESSAGES.get("params_discarded", "Parameters discarded")
                    )
                    continue

            # Execute run using legacy ExperimentManager to avoid scope creep here
            try:
                from src.experiments.manager import get_experiment_manager
                from src.core.research_handler import ResearchExperimentHandler

                self.display_manager.display_info_message(
                    "🚀 Running quantum experiment..."
                )
                em = get_experiment_manager()
                experiment_params = {
                    k: v
                    for k, v in normalized.items()
                    if k not in ["name", "description", "category", "difficulty"]
                }
                result = em.run_experiment("ghz_basic", custom_params=experiment_params)
                if result:
                    is_density = experiment_params.get("sim_mode") == "density"
                    if not is_density:
                        research_handler = ResearchExperimentHandler()
                        if isinstance(result, tuple) and len(result) >= 2:
                            circuit, raw_results = result
                            research_analysis = (
                                research_handler.process_experiment_result(
                                    circuit=circuit,
                                    result=raw_results,
                                    experiment_config=experiment_params,
                                    experiment_id="cli_experiment",
                                )
                            )
                            self.results._last_research_analysis = research_analysis
                            research_file = research_handler.save_research_result(
                                research_analysis
                            )
                            self.display_manager.display_experiment_results(result)
                            viz_type = experiment_params.get(
                                "visualization_type", "none"
                            )
                            if viz_type and viz_type != "none":
                                self.viz.show(raw_results, experiment_params, viz_type)
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
                                self.viz.show(raw_results, experiment_params, viz_type)
                            else:
                                self.viz.show(result, experiment_params, viz_type)
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

    def _show_help_menu(self) -> None:
        glossary = {
            "depolarizing": "Noise channel replacing the state with the maximally mixed state with probability p.",
            "phase_flip": "Z errors with some probability (dephasing)",
            "density matrix": "Matrix representation supporting mixed states.",
            "counts": "Measurement outcome frequencies from shot-based simulations/experiments.",
            "fubini-study": "Distance measure on quantum states in projective Hilbert space.",
        }
        term = self.input_handler.get_input("help_search_prompt", "")
        table = Table(title="Help & Glossary")
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