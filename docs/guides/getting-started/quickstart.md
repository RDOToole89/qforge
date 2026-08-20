# Quick Start

This is the engine API tour. If you have not run an experiment yet, start with
the [First 15 minutes](first-run.md) path (superposition → Bell → noisy GHZ)
instead — you do not need the visual lab.

This page assumes you have already completed the [Installation](installation.md).

## 1. Run a Preset Experiment (CLI)

The fastest way to see the framework in action:

```bash
# See what's available
qforge list

# Run a basic experiment
qforge run 01_superposition

# Customize parameters
qforge run 01_superposition -s num_qubits=4 -s error_rate=0.05

# Sweep a parameter (cartesian product of -p ranges)
qforge sweep 06_ghz_states -p num_qubits=2,3,4 -s shots=1024
```

Each run prints a histogram path under `results/` (plus `analysis.json`).

## 2. Run an Experiment (Python)

For more control, use the engine API directly:

```python
from qforge import run, ExperimentConfig

result = run(ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    shots=1024,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
))

# Results are typed Pydantic models
meas = result.analysis.measurement_results
print(f"Fidelity: {meas.fidelity:.4f}")
print(f"Top outcomes: {dict(list(meas.outcome_probabilities.items())[:3])}")
```

## 3. Analysis Metrics

Request a metric profile (or an explicit list of metric names) via `metrics=` to compute information-theoretic analysis metrics with bootstrap confidence intervals. Registered experiments already pick a default list — `qforge run 05_bell_states` prints Structure Score without extra flags.

```python
result = run(ExperimentConfig(
    num_qubits=4,
    state_type="GHZ",
    shots=4096,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    metrics="structure",  # profile name, or a list like ["asymmetry_index"]
))

bundle = result.metrics_bundle
print(f"Structure Score: {bundle.metrics['structure_score'].value:.4f}")
for name, entry in bundle.metrics.items():
    print(f"  {name}: {entry.value:.4f} (CI95: {entry.ci95})")
```

Available profiles: `"structure"` (distribution-structure suite), `"quick"`, and `"information_theory"`. Register more with `register_profile()`.

## 4. Direct Analysis Pipeline

You can also run the analysis pipeline on raw measurement data without the engine:

```python
from qforge.core.analysis.pipelines.pathway_analysis import run_all_to_schema

counts = {"000": 400, "111": 400, "001": 100, "110": 100}
results = run_all_to_schema(counts)

print(f"Schema version: {results['schema_version']}")
print(f"Structure Score: {results['structure_score']['value']:.4f}")
```

## 5. Parameter Sweeps

Explore how a parameter affects your experiment across a range of values.

**CLI** (uses the experiment's default config as the base):

```bash
qforge sweep 06_ghz_states \
  -p error_rate=0.01,0.05,0.1 \
  -s noise_enabled=true \
  -s noise_type=depolarizing
```

**Python:**

```python
from qforge import ExperimentConfig, SweepManifest, sweep

manifest = SweepManifest(
    base_config=ExperimentConfig(
        num_qubits=3,
        state_type="GHZ",
        shots=1024,
        noise_enabled=True,
        noise_type="depolarizing",
    ),
    parameter_ranges={"error_rate": [0.01, 0.05, 0.1, 0.2]},
)

results = sweep(manifest)
for r in results:
    cfg = r.analysis.experiment_parameters
    fid = r.analysis.measurement_results.fidelity
    print(f"  error_rate={cfg['error_rate']:.2f} -> fidelity={fid:.4f}")
```

## 6. Launch the Web UI

To explore experiments visually with the Bloch sphere, circuit builder, and glossary:

```bash
# Terminal 1: Start the API server (fastapi/uvicorn are installed by `uv sync`)
uv run uvicorn apps.api.main:app --reload --port 8000

# Terminal 2: Start the web client
cd apps/client
pnpm install
pnpm web
```

Open [http://localhost:8081](http://localhost:8081) in your browser.

## What's Next

- **[First 15 minutes](first-run.md)** — superposition → Bell → noisy GHZ, Structure Score in plain language
- **[CLI Reference](../../reference/cli.md)** — Full command documentation
- **[Metrics Guide](../api/metrics.md)** — Deep dive into the 8 analysis metrics
- **[Hardware Setup](../hardware-setup.md)** — Run experiments on IBM Quantum hardware
- **[Architecture](../../architecture/architecture.md)** — Understand the three-layer design
