# Contributing

Thank you for your interest in contributing to the QForge. This guide covers the development workflow, code quality standards, and how to add new components.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management.
Install uv once, then everything else is a single command.

```bash
# Clone the repository
git clone https://github.com/RDOToole89/qforge.git
cd qforge

# Create the .venv and install all runtime + dev + test dependencies from uv.lock.
# uv also installs the pinned Python interpreter (3.12) automatically.
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

The pre-commit hooks run `ruff` for linting and formatting on every commit. Make sure they are installed before you start writing code.

Run any command inside the environment with `uv run <command>` (no manual activation
needed). The lockfile (`uv.lock`) is committed, so every contributor gets the exact
same dependency set.

### Full-Stack Setup (API + Web Client)

If you want to run both the Python API and the web frontend:

```bash
# Terminal 1: Start the API server (fastapi/uvicorn are part of the default sync)
uv run uvicorn apps.api.main:app --reload --port 8000

# Terminal 2: Start the web client
cd apps/client
pnpm install
pnpm web
```

The client runs on `http://localhost:8081` and expects the API at `http://localhost:8000`.

Copy `.env.example` to `.env` and fill in your IBM Quantum token if you want to use hardware features.

## Code Quality

We use three tools to enforce code quality:

| Tool   | Purpose              | Config Location    |
|--------|----------------------|--------------------|
| ruff   | Linting + formatting | `pyproject.toml`   |
| mypy   | Static type checking | `pyproject.toml`   |
| pytest | Testing              | `pyproject.toml`   |

Run them individually:

```bash
# Lint (check for issues)
uv run ruff check src/ tests/

# Format (auto-fix style)
uv run ruff format src/ tests/

# Type checking
uv run mypy src/

# Tests
uv run pytest
```

All three must pass before a PR can be merged.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src/core/analysis --cov-report=term-missing

# Run a specific test file
uv run pytest tests/core/test_metrics.py

# Run tests in parallel
uv run pytest -n auto
```

Coverage is tracked for `src/core/analysis/`. When adding new metrics or analysis code, include tests that cover the core computation paths.

## Architecture

The framework follows a strict three-layer architecture:

```
src/experiments/    Opinionated experiment programs
       |
       v
src/engine/         Orchestration: run(), sweep(), Pydantic models, storage
       |
       v
src/core/           Pure physics: circuits, noise, state prep, metrics
```

**Rules:**

- `core/` must not import from `engine/` or `experiments/`.
- `engine/` must not import from `experiments/`.
- `experiments/` can import from both `engine/` and `core/`.

For the full architectural description, see [CLAUDE.md](CLAUDE.md).

## Adding a New Metric

All analysis metrics live in `src/core/analysis/metrics/`. To add a new one:

1. **Create the metric module** in `src/core/analysis/metrics/your_metric.py`. Implement a function that takes measurement counts (a `dict[str, int]`) and returns a `float`.

2. **Register it** using `MetricSpec` in `src/core/analysis/metrics/registry.py`:

```python
from src.core.analysis.metrics.registry import MetricSpec

# In the METRIC_SPECS list or equivalent registration block:
MetricSpec(
    name="your_metric_name",
    module="src.core.analysis.metrics.your_metric",
    function="compute_your_metric",
    description="Brief description of what this metric measures.",
)
```

3. **Add schema support** in `src/core/analysis/metrics/schema_bridge.py` so the metric appears in the v1.0 schema output.

4. **Write tests** covering at minimum:
   - A known-answer test with a simple distribution.
   - Edge cases (uniform distribution, single-outcome distribution, empty counts).
   - Value range validation (e.g., metric is in [0, 1]).

5. **Add a docstring** with a clear description of the metric's mathematical definition and physical interpretation.

## Code Style

- **Docstrings**: Google-style convention, enforced by `ruff` (pydocstyle).
- **Line length**: 100 characters maximum.
- **Formatting**: `ruff format` handles all style decisions (double quotes, space indentation).
- **Type annotations**: Required on all public functions. `mypy --strict`-adjacent settings are enabled in `pyproject.toml`.
- **Imports**: Sorted by `ruff` using isort rules. First-party imports use `src.*` paths.

Avoid abbreviations in variable names except for well-established conventions (e.g., `rng`, `ci`, `ai` for Asymmetry Index).

## Pull Request Process

1. **Branch from `main`**. Use a descriptive branch name (e.g., `feat/new-metric-name`, `fix/bootstrap-edge-case`).

2. **Keep PRs focused**. One logical change per PR. If you are adding a metric and fixing an unrelated bug, submit them separately.

3. **All checks must pass**:
   - `ruff check` -- no lint errors
   - `ruff format --check` -- no formatting drift
   - `mypy src/` -- no type errors
   - `pytest` -- all tests pass

4. **Write a clear PR description** summarizing what changed and why. Link to any related issues.

5. **Request review**. A maintainer will review and may request changes before merging.

## Breaking Changes

This project is at beta (v0.2). We prefer clean breaks over backward-compatibility shims. If your change removes or renames a public API:

- Remove the old code entirely (do not wrap or deprecate).
- Update all internal callers and tests.
- Note the breaking change in your PR description.

## Questions

If you are unsure about anything, open an issue or start a discussion before writing code. We are happy to help you find the right approach.
