# CLI Reference

The `qxf` command-line tool provides quick access to the quantum experiment framework without writing Python code.

## Installation

After installing the package, the `qxf` command is available:

```bash
pip install -e .
qxf --help
```

## Commands

### `qxf list`

List all registered experiment programs.

```bash
$ qxf list
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Description                                              ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ sst_q1            │ Test whether entanglement topology influences            │
│                   │ decoherence pathways                                     │
│ sst_q1_structured │ SST Q1 with amplitude damping (structured) noise         │
│ bell_correlation  │ Bell state correlation test - quantum vs classical       │
│                   │ bounds                                                   │
└───────────────────┴──────────────────────────────────────────────────────────┘
```

### `qxf run <name>`

Run a registered experiment by name.

```bash
qxf run <experiment_name> [OPTIONS]
```

**Arguments:**
- `name` - Experiment name from registry (use `qxf list` to see available)

**Options:**
- `-s, --set KEY=VALUE` - Override config values (can be used multiple times)
- `-j, --json` - Output full result as JSON instead of summary

**Examples:**

```bash
# Run with defaults
qxf run sst_q1

# Override parameters
qxf run sst_q1 -s num_qubits=3 -s error_rate=0.1

# Multiple overrides
qxf run bell_correlation -s shots=8192 -s error_rate=0.05

# JSON output for scripting
qxf run sst_q1 --json > result.json

# Disable noise
qxf run sst_q1 -s noise_enabled=false
```

**Output:**

```
Running experiment: sst_q1
Overrides: {'num_qubits': 3, 'error_rate': 0.1}

Status: completed
Timestamp: 2025-12-02T17:51:18.395984

Structured Decoherence Metrics:
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

### `qxf run-config <path>`

Run an experiment from a JSON configuration file.

```bash
qxf run-config <config_path> [OPTIONS]
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
  "enable_research_metrics": true,
  "research_type": "structured_decoherence"
}
```

**Usage:**

```bash
qxf run-config my_experiment.json
qxf run-config my_experiment.json --json > results.json
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
| `enable_research_metrics` | bool | true | Compute structured decoherence metrics |
| `research_type` | str | "structured_decoherence" | Type of research metrics |

## Scripting Examples

### Batch experiments

```bash
#!/bin/bash
for rate in 0.01 0.05 0.1 0.2; do
  qxf run sst_q1 -s error_rate=$rate --json >> sweep_results.jsonl
done
```

### Process results with jq

```bash
# Extract asymmetry index from result
qxf run sst_q1 --json | jq '.structured_decoherence_metrics.asymmetry_index'

# Get measurement counts
qxf run bell_correlation --json | jq '.analysis.measurement_results.raw_counts'
```

### Compare experiments

```bash
# Run same config with different states
for state in GHZ W Cluster; do
  echo "=== $state ==="
  qxf run sst_q1 -s state_type=$state
done
```

## Exit Codes

- `0` - Success
- `1` - Error (unknown experiment, invalid config, execution failure)

## Help

Each command has built-in help:

```bash
qxf --help
qxf run --help
qxf run-config --help
qxf list --help
```
