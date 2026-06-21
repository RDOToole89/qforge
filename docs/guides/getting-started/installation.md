# Installation

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages the Python interpreter and dependencies)
- Python 3.11 or later (uv installs the pinned 3.12 automatically)

All other dependencies (Qiskit, NumPy, SciPy, etc.) are declared in `pyproject.toml`
and pinned in `uv.lock` — you do not install them by hand.

## Installation Methods

### Development Installation

For development and testing:

```bash
# Clone the repository
git clone https://github.com/RDOToole89/qiskit-experiment-framework.git
cd qiskit-experiment-framework

# Create the .venv and install runtime + dev + test deps from uv.lock.
# uv reads .python-version and installs Python 3.12 if needed.
uv sync
```

That's it — `uv sync` creates `.venv/`, resolves the pinned interpreter, and installs
everything. Run commands inside the environment with `uv run <command>`.

To include the documentation or security tool groups as well:

```bash
uv sync --all-groups        # everything
uv sync --group docs        # add the docs group
```

### Production Installation

For production use:

```bash
pip install qforge
```

## Verification

Verify the installation by running the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/core/analysis --cov-report=html

# Run specific test modules
uv run pytest tests/core/test_metrics.py -v
```

## Optional Dependencies

### Documentation

To build documentation locally:

```bash
uv run --group docs mkdocs serve
```

### Development Tools

The `dev` group (ruff, mypy, pre-commit, ipython, jupyter) is installed by default
with `uv sync`. Just install the pre-commit hooks:

```bash
uv run pre-commit install
```

## Environment Setup

### Jupyter Notebooks

For interactive analysis (jupyter and ipython ship in the `dev` group):

```bash
uv run jupyter notebook
```

### IDE Integration

The framework includes type hints and docstrings for optimal IDE support:

- **VS Code**: Install Python extension for full IntelliSense
- **PyCharm**: Automatic detection of type hints and documentation
- **Vim/Neovim**: Use language server protocol (LSP) plugins

## Configuration

### Environment Variables

Optional environment variables:

```bash
# Copy the template and fill in your values
cp .env.example .env

# Or set directly
export QEF_LOG_LEVEL=INFO
export QEF_RESULTS_DIR=./results
export IBM_QUANTUM_TOKEN=your_token_here  # For hardware experiments
```

### Project Structure

After installation, your project structure should look like:

```
qiskit-experiment-framework/
├── src/
│   ├── engine/              # Engine API: run(), sweep()
│   ├── core/                # Pure physics: circuits, noise, metrics
│   └── experiments/         # Experiment programs
├── apps/
│   ├── api/                 # FastAPI server
│   └── client/              # Expo/React Native web UI
├── tests/                   # Test suite (~1,100 tests)
├── docs/                    # Documentation
├── pyproject.toml           # Dependencies, tool config (single source of truth)
├── uv.lock                  # Pinned, reproducible dependency lockfile
└── .python-version          # Pinned Python interpreter (3.12)
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'qiskit'** / **No module named 'src'**

```bash
# Re-sync the environment from the lockfile, then prefix commands with `uv run`
uv sync
uv run python -c "import qiskit; from src.engine.api import run"
```

**Lockfile out of date after editing pyproject.toml**

```bash
uv lock   # regenerate uv.lock, then `uv sync`
```

### Platform-Specific Notes

#### macOS

```bash
# May need to install Xcode command line tools
xcode-select --install
```

#### Windows

```bash
# Use Windows Subsystem for Linux (WSL) for best compatibility
# Or ensure Microsoft Visual C++ Build Tools are installed
```

#### Linux

```bash
# Install development headers if needed
sudo apt-get install python3-dev
```

## Next Steps

After successful installation:

1. Continue to the [Quick Start](quickstart.md) for immediate usage
2. Explore the [Metrics Reference](../api/metrics.md) for the analysis API
3. Set up [Hardware Access](../hardware-setup.md) for IBM Quantum experiments
