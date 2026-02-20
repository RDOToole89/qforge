"""
Application-level runtime context for the engine.

Use `AppContext` to hold **process/session configuration** that should *not*
live in globals and does *not* belong inside per-experiment models
(`ExperimentConfig`). It centralizes paths, logging/viz preferences, and
optional infrastructure hooks (event bus, storage, viz factory) so the
orchestrator can remain clean and easily testable.

Why this exists
---------------
- Avoid hidden globals: pass a context object instead of reading module-level
  variables throughout the engine.
- Make orchestration testable: inject fakes/mocks for event bus, storage, or
  visualization without patching imports.
- Keep responsibilities separated: experiment *parameters* go in
  `ExperimentConfig`, while environment & infrastructure live here.

Nice extensions (what you get)
------------------------------
- **Dependency injection hooks**
  - `event_bus`: supply a preconfigured bus (e.g., `SimpleEventBus`) or
    let the caller provide a default factory via `resolve_event_bus(...)`.
  - `storage`: supply a storage backend (e.g., `LocalStorage`) or
    build one from `results_path` via `resolve_storage(...)`.
  - `make_viz_service`: a zero-arg factory returning a visualization
    service; used by `resolve_viz_service(...)`.
- **Environment labeling**
  - `engine_label`: short tag like `"dev"`, `"ci"`, `"prod"` that can be
    recorded in provenance or logs.
- **File-system hygiene**
  - `ensure_dirs=True` creates `base_results_dir` (and `profiles_root` if set)
    during initialization, eliminating “directory not found” errors.
  - `results_path` / `profiles_path` expose normalized absolute paths.

Attributes
----------
base_results_dir : str
    Root directory for results/artifacts. Auto-created when `ensure_dirs=True`.
profiles_root : Optional[str]
    Optional root for user/device profiles, calibrations, presets.
viz_backend : {'matplotlib', 'none'}
    Preferred visualization backend; renderers may honor this.
logging_mode : {'human', 'json'}
    Hint for the app’s logging formatter (not enforced here).
engine_label : str
    Free-form label (e.g., 'dev', 'ci', 'prod') recorded in provenance/logs.
ensure_dirs : bool
    Create `base_results_dir` and `profiles_root` (if present) on init.
event_bus : Optional[Any]
    Optional preconfigured event bus (should at least support `.publish(...)`).
storage : Optional[Any]
    Optional preconfigured storage backend (e.g., with `.save_analysis(...)`).
make_viz_service : Optional[Callable[[], Any]]
    Optional factory producing a visualization service instance.
results_path : pathlib.Path (property)
    Absolute, normalized path for results.
profiles_path : Optional[pathlib.Path] (property)
    Absolute, normalized path for profiles (or `None`).

Methods
-------
resolve_event_bus(default_factory)
    Returns the injected `event_bus` if present; otherwise calls the provided
    `default_factory()` to construct one.
resolve_storage(default_factory)
    Returns the injected `storage` if present; otherwise calls
    `default_factory(str(results_path))` to construct one bound to the
    results directory.
resolve_viz_service(default_factory)
    Uses the injected `make_viz_service()` factory if present; otherwise
    calls `default_factory()`.

Design notes
------------
- This class is intentionally **stdlib-only** and avoids importing engine
  internals to prevent dependency cycles.
- Keep per-run variability (e.g., number of shots) in `ExperimentConfig`.
  Keep longer-lived, process-level concerns (paths, backends) in `AppContext`.

Examples
--------
Basic usage with automatic directory creation:
    >>> ctx = AppContext(base_results_dir="~/lab-runs", engine_label="ci")
    >>> ctx.results_path.is_dir()
    True

Resolving dependencies with defaults:
    >>> bus = ctx.resolve_event_bus(lambda: SimpleEventBus())
    >>> storage = ctx.resolve_storage(lambda base: LocalStorage(base_dir=base))
    >>> viz = ctx.resolve_viz_service(create_default_service)

Full injection for tests or production:
    >>> ctx = AppContext(
    ...     event_bus=SimpleEventBus(),
    ...     storage=LocalStorage(base_dir="~/secure-results"),
    ...     make_viz_service=create_default_service,
    ...     engine_label="prod",
    ... )
    >>> bus = ctx.resolve_event_bus(lambda: object())  # returns injected bus
    >>> storage = ctx.resolve_storage(lambda base: object())  # returns injected storage
    >>> viz = ctx.resolve_viz_service(lambda: object())  # returns injected viz service

"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

# ---- Minimal structural typing notes (no Protocols to keep stdlib-only) ----
# event_bus is expected to have: publish(event) and optionally subscribe(...)
# storage is expected to have: save_analysis(dict) -> str (path), plus any extras
# make_viz_service should be a zero-arg callable returning a viz service object.


@dataclass
class AppContext:
    # --------------------------- Paths & environment ---------------------------

    # Where results, artifacts, manifests are written by default.
    base_results_dir: str = "results"

    # Optional root for “profiles” (user/device presets, calibration, etc.)
    profiles_root: str | None = None

    # Preferred visualization stack for renderers (engine may ignore if unavailable).
    viz_backend: Literal["matplotlib", "none"] = "matplotlib"

    # Logging presentation mode that your app bootstrap can honor.
    logging_mode: Literal["human", "json"] = "human"

    # Log level for setup_logging() (DEBUG, INFO, WARNING, ERROR).
    log_level: str = "INFO"

    # Annotate run provenance with a short environment label.
    engine_label: str = "dev"

    # If True, create base_results_dir (and profiles_root, if provided) on init.
    ensure_dirs: bool = True

    # ------------------------ Dependency injection hooks -----------------------

    # Optional, preconfigured event bus for the run/sweep facade to use.
    event_bus: Any | None = None

    # Optional, preconfigured storage backend (e.g., LocalStorage).
    storage: Any | None = None

    # Optional factory that returns a visualization service instance.
    make_viz_service: Callable[[], Any] | None = None

    # ------------------------------ Internals ---------------------------------

    # Resolved absolute paths (populated in __post_init__).
    _results_path: Path = field(init=False, repr=False)
    _profiles_path: Path | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        """Normalize paths and optionally create directories."""
        self._results_path = self._normalize_path(self.base_results_dir)
        if self.profiles_root is not None:
            self._profiles_path = self._normalize_path(self.profiles_root)

        if self.ensure_dirs:
            self._safe_mkdir(self._results_path)
            if self._profiles_path is not None:
                self._safe_mkdir(self._profiles_path)

    # ------------------------------ Helpers -----------------------------------

    @property
    def results_path(self) -> Path:
        """Absolute, normalized results directory (guaranteed to exist if ensure_dirs=True)."""
        return self._results_path

    @property
    def profiles_path(self) -> Path | None:
        """Absolute, normalized profiles directory (or None if not set)."""
        return self._profiles_path

    def resolve_event_bus(self, default_factory: Callable[[], Any]) -> Any:
        """
        Return the configured event bus, or create a default if none provided.

        Example:
            bus = ctx.resolve_event_bus(lambda: SimpleEventBus())
        """
        if self.event_bus is not None:
            return self.event_bus
        return default_factory()

    def resolve_storage(self, default_factory: Callable[[str], Any]) -> Any:
        """
        Return the configured storage backend, or create a default bound to results_path.

        Example:
            storage = ctx.resolve_storage(lambda base: LocalStorage(base_dir=base))
        """
        if self.storage is not None:
            return self.storage
        return default_factory(str(self.results_path))

    def resolve_viz_service(self, default_factory: Callable[[], Any]) -> Any:
        """
        Return a visualization service from the injected factory if present,
        otherwise use the provided default_factory.

        Example:
            viz = ctx.resolve_viz_service(create_default_service)
        """
        if self.make_viz_service is not None:
            return self.make_viz_service()
        return default_factory()

    # ----------------------------- Utilities ----------------------------------

    @staticmethod
    def _normalize_path(p: str) -> Path:
        """Expand ~, environment vars, and resolve to an absolute Path."""
        expanded = os.path.expandvars(os.path.expanduser(p))
        return Path(expanded).resolve()

    @staticmethod
    def _safe_mkdir(path: Path) -> None:
        """Create a directory if it does not exist (no error if already present)."""
        path.mkdir(parents=True, exist_ok=True)
