from __future__ import annotations

from typing import Optional

from src.cli.interactive.results import ResultsManager


def show_recent(console, input_handler, display_manager, max_items: int = 10) -> None:
    ResultsManager(console, input_handler, display_manager).show_recent_results(max_items)


def open_viz_from_json(console, input_handler, display_manager, path: str) -> None:
    ResultsManager(console, input_handler, display_manager).open_visualization_from_result_json(path)


def rerun_from_json(console, input_handler, display_manager, path: str) -> None:
    ResultsManager(console, input_handler, display_manager).rerun_from_result_json(path)