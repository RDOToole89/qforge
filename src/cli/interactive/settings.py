# src/cli/interactive/settings.py

from __future__ import annotations

from typing import Any
from rich.table import Table


class SettingsUI:
    """Settings and profiles UI for interactive CLI."""

    def __init__(self, console, input_handler, display_manager):
        self.console = console
        self.input_handler = input_handler
        self.display_manager = display_manager

    def show(self) -> None:
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
            self._edit_settings()
            return
        if action in {"profiles_save", "profiles_load"}:
            self._profiles_action(action)

    def _edit_settings(self) -> None:
        from src.config.settings import settings

        try:
            new_shots = self.input_handler.get_numeric_input(
                "shots_prompt", str(settings.DEFAULT_SHOTS), int
            )
            new_err = self.input_handler.get_numeric_input(
                "error_rate_prompt", str(settings.DEFAULT_ERROR_RATE), float
            )
            settings.DEFAULT_SHOTS = int(new_shots)
            settings.DEFAULT_ERROR_RATE = float(new_err)
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
            save_base = self.input_handler.get_input(
                "custom_state_qasm_path_prompt", "results/visualizations"
            )
            try:
                from src.visualization.save_manager import set_save_manager_base_dir

                set_save_manager_base_dir(save_base)
            except Exception:
                pass
            self.display_manager.display_success_message(
                "✅ Updated settings (shots, error_rate, viz backend, save dir)"
            )
        except Exception as e:
            self.display_manager.display_error_message(f"Failed to edit settings: {e}")

    def _profiles_action(self, action: str) -> None:
        from src.config.settings import settings

        try:
            from src.config import profiles as _profiles

            if action == "profiles_save":
                name = self.input_handler.get_input("custom_template_prompt", "default")
                path = _profiles.save_profile(name)
                self.display_manager.display_success_message(
                    f"✅ Saved profile to {path}"
                )
            else:
                existing = _profiles.list_profiles()
                if not existing:
                    self.display_manager.display_info_message("No profiles found.")
                    return
                options = [(n, n, n[0]) for n in existing]
                pick = self.input_handler.select_option(
                    "Select Profile", options, existing[0], show_value_column=False
                )
                prof = _profiles.load_profile(pick)
                _profiles.apply_profile(prof)
                self.display_manager.display_success_message(
                    f"✅ Loaded profile '{pick}'"
                )
            try:
                from src.visualization.save_manager import set_save_manager_base_dir

                set_save_manager_base_dir(
                    settings.DEFAULT_RESULTS_DIR + "/visualizations"
                )
            except Exception:
                pass
        except Exception as e:
            self.display_manager.display_error_message(f"Profile operation failed: {e}")
