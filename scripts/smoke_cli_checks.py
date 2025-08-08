import sys
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from src.cli.interactive_app import InteractiveCLI
from src.cli.help import HelpManager


def latest_two_json() -> list[Path]:
    files = sorted(
        Path("results").rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    return files[:2]


def test_compare_results():
    cli = InteractiveCLI()
    files = latest_two_json()
    if len(files) < 2:
        print("[skip] Not enough results to compare")
        return
    print(f"[run] Comparing: {files[0].name} vs {files[1].name}")
    cli._compare_results(str(files[0]), str(files[1]))


def test_help_show():
    console = Console()
    help_mgr = HelpManager(console)
    print("[run] HelpManager.show with query 'ghz'")
    with patch("builtins.input", side_effect=["ghz"]):
        help_mgr.show()


def main():
    print("[start] CLI smoke checks")
    # 1) Recent Results compare
    test_compare_results()
    # 2) Help search
    test_help_show()
    print("[done] CLI smoke checks complete")


if __name__ == "__main__":
    sys.exit(main())
