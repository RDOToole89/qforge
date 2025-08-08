from typing import Optional
from rich.console import Console
from rich.table import Table
from src.cli.common.glossary import search_terms


class HelpManager:
    def __init__(self, console: Console):
        self.console = console

    def show(self, default_query: str = "") -> None:
        self.console.print("[bold cyan]Help & Glossary[/bold cyan]")
        self.console.print("Type to search terms; Enter to list all; Ctrl+C to exit.")
        self.console.print("Search term (Enter to list all) []: ", end="")
        try:
            q = input().strip()
        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]Help closed[/bold yellow]")
            return
        rows = search_terms(q)
        table = Table(title="Glossary", show_header=True, header_style="bold magenta")
        table.add_column("Term", style="green", width=24)
        table.add_column("Definition", style="yellow")
        for term, desc in rows:
            table.add_row(term, desc)
        if not rows:
            self.console.print("[bold yellow]No matches[/bold yellow]")
        else:
            self.console.print(table)
