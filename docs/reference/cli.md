# CLI Reference

The `qforge` command-line tool provides quick access to the quantum experiment framework without writing Python code.

## Installation

After installing the package, the `qforge` command is available:

```bash
uv sync
uv run qforge --help
```

The examples below use the bare `qforge` command; prefix with `uv run` if you have not activated the project virtual environment.

## Commands

### `qforge list`

List all registered experiment programs.

```bash
$ qforge list
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Description                                              ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 01_superposition            │ What IS a qubit? Superposition and measurement           │
│ 11_noise_and_entanglement   │ How entanglement changes error patterns                  │
│ bell_correlation  │ Bell state correlation test - quantum vs classical       │
│                   │ bounds                                                   │
└───────────────────┴──────────────────────────────────────────────────────────┘
```

### `qforge run <name>`

Run a registered experiment by name.

```bash
qforge run <experiment_name> [OPTIONS]
```

**Arguments:**
- `name` - Experiment name from registry (use `qforge list` to see available)

**Options:**
- `-s, --set KEY=VALUE` - Override config values (can be used multiple times)
- `-j, --json` - Output full result as JSON instead of summary

**Examples:**

```bash
# Run with defaults
qforge run 01_superposition

# Override parameters
qforge run 01_superposition -s num_qubits=3 -s error_rate=0.1

# Multiple overrides
qforge run bell_correlation -s shots=8192 -s error_rate=0.05

# JSON output for scripting
qforge run 01_superposition --json > result.json

# Disable noise
qforge run 01_superposition -s noise_enabled=false
```

**Output:**

```
Running experiment: 01_superposition
Overrides: {'num_qubits': 3, 'error_rate': 0.1}

Status: completed
Timestamp: 2025-12-02T17:51:18.395984

Analysis Metrics:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric                               ┃   Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Asymmetry Index (AI)                 │  0.6761 │
│ Pathway Concentration (PCR)          │ 95.1000 │
│ Entanglement-Error Correlation (EEC) │  0.0000 │
│ Structure Score (SS)                 │  0.6761 │
│ Concentration Index (CI)             │ 95.1000 │
│ Total Correlation (TC)               │  1.5197 │
└──────────────────────────────────────┴─────────┘

Measurements: 1024 shots
Top outcomes:
  111: 496 (48.4%)
  000: 455 (44.4%)
  001: 23 (2.2%)
```

### `qforge run-config <path>`

Run an experiment from a JSON configuration file.

```bash
qforge run-config <config_path> [OPTIONS]
```

**Arguments:**
- `config_path` - Path to JSON config file

**Options:**
- `-j, --json` - Output full result as JSON

**Example config file** (`my_experiment.json`):

```json
{
  "num_qubits": 4,
  "state_type": "GHZ",
  "noise_enabled": true,
  "noise_type": "depolarizing",
  "error_rate": 0.05,
  "shots": 4096,
  "metrics": "decoherence"
}
```

**Usage:**

```bash
qforge run-config my_experiment.json
qforge run-config my_experiment.json --json > results.json
```

## Configuration Options

When using `-s` overrides or JSON config files, these parameters are available:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_qubits` | int | 4 | Number of qubits in the system |
| `state_type` | str | "GHZ" | Quantum state: "GHZ", "W", "Bell", "Cluster" |
| `noise_enabled` | bool | true | Whether to apply noise |
| `noise_type` | str | "depolarizing" | Noise model: "depolarizing", "amplitude_damping" |
| `error_rate` | float | 0.05 | Noise strength (0.0 to 1.0) |
| `shots` | int | 4096 | Number of measurement shots |
| `metrics` | str \| list | None | Metric profile name ("decoherence", "quick", "information_theory") or explicit list of metric names |
| `experiment_type` | str | "decoherence" | Experiment category tag ("decoherence", "parameter_sweep", "noise_comparison", "control", "scaling", "convergence", "batch_sweep") |

## Scripting Examples

### Batch experiments

```bash
#!/bin/bash
for rate in 0.01 0.05 0.1 0.2; do
  qforge run 01_superposition -s error_rate=$rate --json >> sweep_results.jsonl
done
```

### Process results with jq

```bash
# Extract asymmetry index from result
qforge run 01_superposition --json | jq '.metrics_bundle.metrics.asymmetry_index.value'

# Get measurement counts
qforge run bell_correlation --json | jq '.analysis.measurement_results.raw_counts'
```

### Compare experiments

```bash
# Run same config with different states
for state in GHZ W Cluster; do
  echo "=== $state ==="
  qforge run 01_superposition -s state_type=$state
done
```

## Exit Codes

- `0` - Success
- `1` - Error (unknown experiment, invalid config, execution failure)

## Help

Each command has built-in help:

```bash
qforge --help
qforge run --help
qforge run-config --help
qforge list --help
```
