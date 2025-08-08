from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from rich.console import Console


@dataclass
class CLIContext:
    console: Console
    input_handler: object
    display_manager: object
    settings: Optional[object] = None
