import os
import sys


def pytest_sessionstart(session):
    # Ensure repository root is on sys.path so imports like `from src...` work
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
