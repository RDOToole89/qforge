# Qiskit Experiment Framework

A research-grade quantum experiment framework built on Qiskit for investigating structured decoherence pathways in quantum systems. The framework implements the **Spring Network Model** hypothesis -- that quantum decoherence follows structured pathways determined by entanglement network topology rather than random patterns. It sits between a learning tool and a research instrument: educational enough to teach quantum mechanics concepts, rigorous enough to produce publishable results.

## Features

- **8 Research Metrics** for structured decoherence analysis (Asymmetry Index, Pathway Concentration Ratio, Entanglement-Error Correlation, Temporal Pathway Stability, Complexity Emergence Score, Structure Score, Concentration Index, Total Correlation) with bootstrap confidence intervals and v1.0 schema compliance.
- **Engine-First Architecture** with a clean `run()` / `sweep()` API, Pydantic models for type-safe configuration, and deterministic reproducibility via RNG plumbing.
- **Multiple Simulation Modes**: shot-based sampling, statevector (exact noiseless), and density matrix (full mixed state with noise).
- **Physics-Compliant Noise Models**: depolarizing, amplitude damping, phase damping, and custom noise channels through a factory pattern.
- **Bloch Sphere Visualizer**: a React Native (Expo) frontend for interactive visualization of CPTP maps and quantum states.
- **Pluggable Experiment Programs**: protocol-based abstraction for adding new experiments beyond the flagship structured decoherence studies.

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/qiskit-experiment-framework.git
cd qiskit-experiment-framework
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=4,
    state_type="GHZ",
    enable_research_metrics=True,
    research_type="structured_decoherence",
    shots=4096,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
)

result = run(config)

metrics = result.structured_decoherence_metrics
print(f"Asymmetry Index:      {metrics.asymmetry_index:.4f}")
print(f"Pathway Concentration: {metrics.pathway_concentration_ratio:.4f}")
print(f"Topology Correlation:  {metrics.entanglement_error_correlation:.4f}")
```

You can also run the analysis pipeline directly on measurement data:

```python
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

counts = {"000": 400, "111": 400, "001": 100, "110": 100}
results = run_all_to_schema(counts)

print(f"Schema version: {results['schema_version']}")
print(f"Structure Score: {results['structure_score']['value']:.4f}")
```

## Architecture

The framework follows a strict layered architecture:

```
experiments/          Experiment programs (SST hypotheses, benchmarks, ...)
    |
    v
engine/               Orchestration layer: run(), sweep(), Pydantic models
    |
    v
core/                 Pure physics: circuits, noise models, state prep, metrics
    |-- analysis/         Research metrics, pipelines, schema bridge
    |-- noise_models/     Physics-compliant noise channels
    |-- state_preparation/ Quantum state factories (GHZ, Bell, W, Cluster, ...)
```

- **`src/core/`** contains no experiment-specific logic -- it is pure quantum mechanics, information theory, and statistics.
- **`src/engine/`** orchestrates experiments without knowing what "structured decoherence" means.
- **`src/experiments/`** carries research-specific semantics and uses the engine API.

## Running the Frontend

The Bloch sphere visualizer is a React Native (Expo) app:

```bash
cd apps/client
npm install
npm run web
```

This starts the Expo development server. The app connects to the Python backend for experiment data and renders interactive CPTP map visualizations.

## Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

## Documentation

Research documentation and study guides are in the `docs/` directory:

- `docs/research-docs/` -- Research hypotheses, experiment suggestions, and findings
- `CLAUDE.md` -- Detailed project architecture and development context

## Contributing

We welcome contributions. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

Apache-2.0. See [LICENSE](LICENSE) for details.
