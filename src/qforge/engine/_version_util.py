"""Centralized version string for provenance and metadata."""


def get_version() -> str:
    """Return the installed package version, or 'dev' if not installed."""
    try:
        from importlib.metadata import version

        return version("qforge")
    except Exception:
        return "dev"
