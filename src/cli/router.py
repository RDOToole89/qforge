# src/cli/router.py

from __future__ import annotations

from typing import Dict, Any, Optional

from rich.table import Table

from .interactive.collectors import ParameterCollector
from .interactive.presets_browser import PresetsBrowser
from .interactive.viz import VisualizationOrchestrator
from .interactive.results import ResultsManager
from .interactive.settings import SettingsUI
from .common.context import CLIContext
from .common.constants import (
    MAIN_MENU_OPTIONS,
    SETTINGS_MENU_OPTIONS,
    FOOTER_HINTS,
    CURATED_PRESETS,
    PROMPT_IDS,
)
from src.config.params import apply_defaults, validate_parameters
from .actions.run import execute_run


class Router:
    """Interactive menu router that orchestrates the main CLI loop."""

    def __init__(self, console, input_handler, display_manager):
        self.ctx = CLIContext(console=console, input_handler=input_handler, display_manager=display_manager)
        # Components
        self.collector = ParameterCollector(self.ctx.input_handler, self.ctx.display_manager)
        self.browser = PresetsBrowser(self.ctx.input_handler, self.ctx.display_manager, self.ctx.console)
        self.results = ResultsManager(self.ctx.console, self.ctx.input_handler, self.ctx.display_manager)
        self.viz = VisualizationOrchestrator(self.ctx.display_manager)
        self.settings = SettingsUI(self.ctx.console, self.ctx.input_handler, self.ctx.display_manager)

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
        for key, name, family, desc in CURATED_PRESETS:
            table.add_row(key, name, family, desc)
        self.ctx.console.print(table)

    def run(self) -> None:
        from src.utils.messages import MESSAGES

        while True:
            self.ctx.console.print(MESSAGES.get(PROMPT_IDS["welcome"], "Welcome"))
            choice = self.ctx.input_handler.select_option(
                title="Main Menu",
                options=MAIN_MENU_OPTIONS,
                default_value="1",
                show_value_column=False,
            )
            try:
                self.ctx.display_manager.display_footer_hints(
                    FOOTER_HINTS
                )
            except Exception:
                pass

            if choice == "1":
                self.display_quick_options()
                try:
                    args = self.browser.browse(
                        include_keys=[k for k, *_ in CURATED_PRESETS]
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
                sub = self.ctx.input_handler.select_option(
                    title="Settings & Help",
                    options=SETTINGS_MENU_OPTIONS,
                    default_value="settings",
                    show_value_column=False,
                )
                if sub == "settings":
                    self.settings.show()
                elif sub == "help":
                    self._show_help_menu()
                continue
            elif choice == "q":
                self.ctx.console.print(MESSAGES.get(PROMPT_IDS["goodbye"], "Goodbye"))
                return
            else:
                self.ctx.console.print(MESSAGES.get(PROMPT_IDS["invalid_choice"], "Invalid choice"))
                continue

            # Normalize and display parameter summary
            normalized = validate_parameters(apply_defaults(args))
            self.ctx.display_manager.display_params_summary(normalized)

            # Confirm before running
            if self.ctx.input_handler.get_input(PROMPT_IDS["proceed_prompt"], "y", ["y", "n"]) != "y":
                try:
                    args = self.collector.collect_parameters(
                        interactive=True, base_args=normalized
                    )
                    normalized = validate_parameters(apply_defaults(args))
                    self.ctx.display_manager.display_params_summary(normalized)
                except Exception:
                    self.ctx.console.print(
                        MESSAGES.get("params_discarded", "Parameters discarded")
                    )
                    continue

            # Execute run using legacy ExperimentManager to avoid scope creep here
            try:
                research_file = execute_run(normalized, self.ctx.display_manager, self.viz)
                if research_file is not None:
                    self.results._last_research_analysis = research_file  # lightweight track
            except Exception as e:
                self.ctx.display_manager.display_error_message(
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
