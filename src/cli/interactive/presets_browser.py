# src/cli/interactive/presets_browser.py

from __future__ import annotations

from typing import Dict, Any, List, Optional, Tuple

from rich.table import Table
from src.experiments.presets import load_preset_experiments


class PresetsBrowser:
    """Encapsulates the presets browsing and filtering UI logic."""

    def __init__(self, input_handler, display_manager, console):
        self.input_handler = input_handler
        self.display_manager = display_manager
        self.console = console

    def browse(self, include_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        unified = load_preset_experiments()
        keys = list(unified.keys())
        if include_keys is not None:
            keys = [k for k in keys if k in include_keys]
        if not keys:
            keys = list(unified.keys())

        # Category filter
        categories = sorted({unified[k].get("category", "?") for k in keys})
        categories = [c for c in categories if c]
        categories.insert(0, "all")
        cat_choice = self.input_handler.select_option(
            title="Filter by Category",
            options=[(c, c.title(), c[0] if c != "all" else "a") for c in categories],
            default_value="all",
            show_value_column=False,
        )
        if cat_choice != "all":
            keys = [k for k in keys if unified[k].get("category") == cat_choice]

        # Family filter (replaces difficulty)
        families = sorted(
            {unified[k].get("family", "?") for k in keys}
            | {
                unified[k].get(
                    "state", unified[k].get("config", {}).get("state_type", "?")
                )
                for k in keys
            }
        )
        families = [f for f in families if f and f != "?"]
        families.insert(0, "all")
        fam_choice = self.input_handler.select_option(
            title="Filter by Experiment Family",
            options=[
                (f, str(f).title(), str(f)[0] if f != "all" else "a") for f in families
            ],
            default_value="all",
            show_value_column=False,
        )
        if fam_choice != "all":
            keys = [
                k
                for k in keys
                if unified[k].get("family") == fam_choice
                or unified[k].get("state") == fam_choice
                or unified[k].get("config", {}).get("state_type") == fam_choice
            ]

        # Search text
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

        # Options table
        options: List[Tuple[str, str, str]] = []
        for k in keys:
            meta = unified[k]
            cfg = meta.get("config", {})
            name = meta.get("name", k)
            state = cfg.get("state_type", "-")
            q = cfg.get("num_qubits", "-")
            noise = cfg.get("noise_type", "-")
            sim = cfg.get("sim_mode", "-")
            shots = cfg.get("shots", "-")
            fam = meta.get("family", state)
            label = f"{name}  |  Family={fam}  State={state}  Q={q}  Noise={noise}  Sim={sim}  Shots={shots}"
            options.append((k, label, k))
        options.append(("show_all", "Show all options/help", "?"))
        options.append(("c", "Custom Parameters", "c"))
        options.append(("q", "Back", "q"))

        choice = self.input_handler.select_option(
            title="Presets Browser",
            options=options,
            default_value=keys[0],
            show_value_column=False,
        )
        if choice == "show_all":
            self._show_overview(unified)
            return self.browse(include_keys)
        if choice == "q":
            raise KeyboardInterrupt
        selected = unified.get(choice)
        if choice == "c" or selected is None:
            from .collectors import ParameterCollector  # lazy import to avoid cycle

            return ParameterCollector(
                self.input_handler, self.display_manager
            ).collect_parameters(interactive=True)
        return selected.get("config", {})

    def _show_overview(self, unified: Dict[str, Any]) -> None:
        table = Table(title="Options Overview")
        table.add_column("Category", style="cyan")
        table.add_column("Values", style="green")
        categories = ", ".join(
            sorted({unified[k].get("category", "-") for k in unified})
        )
        difficulties = ", ".join(
            sorted({unified[k].get("difficulty", "-") for k in unified})
        )
        table.add_row("Categories", categories)
        table.add_row("Difficulties", difficulties)
        self.console.print(table)
