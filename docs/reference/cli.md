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
01_superposition
1 qubit  ·  SUPERPOSITION

Outcomes  1024 shots
1 ████████████░░░░░░░░░░  51.4%
0 ███████████░░░░░░░░░░░  48.6%

Metrics
asymmetry_index  0.0273
Asymmetry Index near 0 means the histogram looks like a fair coin. |0⟩ or |1⟩ would be near 1.

Saved
  histogram  results/2026-08-20/SUPERPOSITION_1q_clean_1024shots_00000000/histogram.png
  analysis   results/2026-08-20/SUPERPOSITION_1q_clean_1024shots_00000000/analysis.json
```

`qforge run` executes the experiment's **default config**, not every variant in the docstring. Registered experiments already pick the metrics that match the question they ask, and the CLI prints a one-line hint under the numbers. Extra methods (`run_all_states`, `run_scaling`) and `qforge sweep` cover the rest.

### `qforge sweep <name>`

Sweep a registered experiment over one or more parameter ranges. The base is the experiment's default config; `-s` overrides apply to every point; `-p` ranges take a cartesian product.

```bash
qforge sweep <experiment_name> -p KEY=v1,v2,v3 [OPTIONS]
```

**Arguments:**
- `name` - Experiment name from registry

**Options:**
- `-p, --param KEY=v1,v2,v3` - Sweep range (repeatable). JSON lists also work: `-p 'num_qubits=[2,3,4]'`
- `-s, --set KEY=VALUE` - Base-config override applied to every sweep point
- `-j, --json` - Output the list of results as JSON

**Examples:**

```bash
# Scale GHZ from 2 to 4 qubits
qforge sweep 06_ghz_states -p num_qubits=2,3,4 -s shots=1024

# Noise strength on a 3-qubit GHZ
qforge sweep 06_ghz_states \
  -p error_rate=0.01,0.05,0.1 \
  -s noise_enabled=true \
  -s noise_type=depolarizing

# Two-parameter grid
qforge sweep 06_ghz_states -p num_qubits=2,3 -p error_rate=0.01,0.05 \
  -s noise_enabled=true -s noise_type=depolarizing
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
  "metrics": "structure"
}
```

**Usage:**

```bash
qforge run-config my_experiment.json
qforge run-config my_experiment.json --json > results.json
```

### `qforge sweep-config <path>`

Same as `sweep`, but the spec is a JSON [SweepManifest](../guides/getting-started/quickstart.md): `base_config` plus `parameter_ranges`.

```bash
qforge sweep-config my_sweep.json
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
| `metrics` | str \| list | experiment default | Metric profile (`"structure"`, `"quick"`, `"information_theory"`) or an explicit list. Registered experiments already set a teaching list. |
| `experiment_type` | str | None | Optional free-string label for grouping and storage |

## Scripting Examples

### Batch experiments

Prefer `qforge sweep` over a shell loop — one command, one table:

```bash
qforge sweep 06_ghz_states -p error_rate=0.01,0.05,0.1,0.2 \
  -s noise_enabled=true -s noise_type=depolarizing
```

A loop still works when you want separate CLI invocations:

```bash
#!/bin/bash
for rate in 0.01 0.05 0.1 0.2; do
  qforge run 06_ghz_states -s noise_enabled=true -s noise_type=depolarizing \
    -s error_rate=$rate --json >> sweep_results.jsonl
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
qforge sweep --help
qforge run-config --help
qforge sweep-config --help
qforge list --help
```
