# Installation

## Requirements

- Python 3.9 or later
- Qiskit 0.45.0 or later
- NumPy 1.21.0 or later
- SciPy 1.7.0 or later

## Installation Methods

### Development Installation

For development and testing:

```bash
# Clone the repository
git clone https://github.com/your-org/qforge.git
cd qforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
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
pytest

# Run with coverage
pytest --cov=src/core/analysis --cov-report=html

# Run specific test modules
pytest tests/test_metrics.py -v
```

## Optional Dependencies

### Documentation

To build documentation locally:

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs serve
```

### Development Tools

Additional tools for development:

```bash
pip install black isort flake8 mypy pre-commit
```

## Environment Setup

### Jupyter Notebooks

For interactive analysis:

```bash
pip install jupyter ipython
jupyter notebook
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
export QISKIT_EXPERIMENTS_LOG_LEVEL=INFO
export QISKIT_EXPERIMENTS_CACHE_DIR=/path/to/cache
```

### Project Structure

After installation, your project structure should look like:

```
qforge/
├── src/
│   ├── engine/              # Engine API
│   └── core/
│       └── analysis/        # Analysis framework
├── tests/                   # Test suite
├── docs/                    # Documentation
├── requirements.txt         # Production dependencies
└── requirements-dev.txt     # Development dependencies
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'qiskit'**

```bash
pip install qiskit>=0.45.0
```

**ModuleNotFoundError: No module named 'src'**

```bash
# Ensure you're in the project root and installed in editable mode
pip install -e .
```

**Test failures related to coverage**

```bash
# Install coverage dependencies
pip install pytest-cov coverage
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

1. Continue to [Quick Start](quickstart.md) for immediate usage
2. Read the [Basic Usage](basic-usage.md) guide for detailed examples
3. Explore the [API Reference](../api/constants.md) for complete documentation
