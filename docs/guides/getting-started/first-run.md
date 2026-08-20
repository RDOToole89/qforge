# First 15 minutes

Three experiments. The metric that matches each question. No visual lab — the
engine is enough.

By the end you will have measured a qubit, seen two-qubit entanglement, and used
**Structure Score** to tell a noisy GHZ state apart from a product state that
looks similarly messy.

## 0. Install (~2 min)

You need [uv](https://docs.astral.sh/uv/) once. Then:

```bash
git clone https://github.com/RDOToole89/qforge.git
cd qforge
uv sync
```

`uv sync` creates `.venv/` and installs the pinned Python 3.12 environment from
`uv.lock`. Prefix commands with `uv run` so they use that environment.

## 1. A qubit (~3 min)

A classical bit is 0 or 1. A qubit can be in superposition: the state
\(|+\rangle = (|0\rangle + |1\rangle)/\sqrt{2}\) has no definite value until you
measure it. The Hadamard gate \(H\) prepares \(|+\rangle\) from \(|0\rangle\).

```bash
uv run qforge run 01_superposition
```

You should see roughly half `0` and half `1`. The CLI also prints where it
saved the histogram — open that PNG:

```text
Measurements: 1024 shots
Top outcomes:
  1: 526 (51.4%)
  0: 498 (48.6%)

Metrics
  asymmetry_index   0.0273
Asymmetry Index near 0 means the histogram looks like a fair coin. |0⟩ or |1⟩ would be near 1.

Saved:
  histogram: results/2026-08-20/SUPERPOSITION_1q_clean_1024shots_00000000/histogram.png
  analysis: results/2026-08-20/SUPERPOSITION_1q_clean_1024shots_00000000/analysis.json
```

That 50/50 split is not measurement error. The qubit did not have a hidden bit
value waiting to be read. Asymmetry Index near **0** is the same statement in
one number: the histogram looks like a fair coin. For contrast: `|0⟩` always
measures `0` (Asymmetry Index near 1), and `|1⟩` always measures `1`.

The CLI run above is only \(|+\rangle\). To see all three, open a REPL with
`uv run python` and:

```python
from qforge import get_experiment

exp = get_experiment("01_superposition")
for result in exp.run_all_states():
    print(sorted(result.analysis.measurement_results.raw_counts.items()))
```

## 2. Entanglement (~3 min)

Two qubits can be correlated more strongly than any pair of independent coins.
The Bell state \(|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}\) always
agrees: both 0, or both 1 — never `01` or `10`. `qforge run 05_bell_states`
prepares this one state (not all four Bell states).

```bash
uv run qforge run 05_bell_states -s rng_seed=42
```

```text
Outcomes  4096 shots
11 ███████████░░░░░░░░░░░  51.0%
00 ███████████░░░░░░░░░░░  49.0%

Metrics
structure_score    0.3097
total_correlation  0.9965
High Structure Score / Total Correlation: only 00 and 11. Independent 50/50 coins would be ~0.
```

If each qubit were an independent 50/50 coin, `01` and `10` would appear about
as often as `00` and `11`. They do not. Structure Score is high for the same
reason.

A GHZ state is the same idea for \(N\) qubits:
\(|\mathrm{GHZ}\rangle = (|00\ldots0\rangle + |11\ldots1\rangle)/\sqrt{2}\).
`qforge run 06_ghz_states` prepares the **3-qubit** default. Only the two
all-agree outcomes should appear. To scale qubit count:

```bash
uv run qforge sweep 06_ghz_states -p num_qubits=2,3,4 -s shots=1024
```

## 3. Noise, and Structure Score (~7 min)

Turn on a little depolarizing noise. The histogram is no longer two perfect
peaks — stray bitstrings appear. The question is whether those strays are
*independent per qubit* or still *structured*.

```bash
uv run qforge run 06_ghz_states \
  -s noise_enabled=true \
  -s noise_type=depolarizing \
  -s error_rate=0.05 \
  -s rng_seed=42
```

On Windows PowerShell, put the overrides on one line (no `\`):

```bash
uv run qforge run 06_ghz_states -s noise_enabled=true -s noise_type=depolarizing -s error_rate=0.05 -s rng_seed=42
```

The experiment already asks for Structure Score, Total Correlation, and
Concentration Index. With that seed you should see something like:

```text
Outcomes  4096 shots
111 ██████████░░░░░░░░░░░░  47.1%
000 ██████████░░░░░░░░░░░░  46.2%
110 █░░░░░░░░░░░░░░░░░░░░░   2.4%
001 ░░░░░░░░░░░░░░░░░░░░░░   1.9%

Metrics
concentration_index  86.8636
structure_score       0.4010
total_correlation     1.5563
Two peaks (000/111) score high. A product of |+⟩ states stays near 0 on Structure Score.
```

The two GHZ peaks still dominate. Structure Score is about **0.40**.

### What Structure Score is saying

If each qubit failed on its own, the histogram would look like a product of
single-qubit probabilities — a *factorized* distribution. Structure Score
measures how far the **real** histogram is from that independent-qubits story.

- Near **0**: the bits could have been separate coins. A product of
  \(|+\rangle\) states looks like this even after noise.
- Higher (here ~**0.4**): the outcomes still hang together. Noisy GHZ stays
  structured — you mostly still see all-zeros or all-ones.

Formally, \(\mathrm{SS} = \mathrm{JSD}(P_\text{observed} \,\|\, Q_\text{factorized})\),
in bits, bounded to \([0, 1]\). \(Q_\text{factorized}\) is the product of the
per-qubit marginals. Implementation:
`qforge.core.analysis.metrics.structure_score`.

### The contrast that makes the number mean something

Same noise, same shots, two different states. Paste into `uv run python`:

```python
from qforge import run, ExperimentConfig

def score(state: str) -> None:
    result = run(ExperimentConfig(
        num_qubits=3,
        state_type=state,
        shots=2048,
        rng_seed=42,
        noise_enabled=True,
        noise_type="depolarizing",
        error_rate=0.05,
        metrics=["structure_score"],
    ))
    counts = result.analysis.measurement_results.raw_counts
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:4]
    ss = result.metrics_bundle.metrics["structure_score"].value
    print(f"{state:14}  Structure Score = {ss:.4f}  top = {top}")

score("GHZ")
score("SUPERPOSITION")
```

With this seed:

| State | What it is | Structure Score | Histogram |
| --- | --- | --- | --- |
| `GHZ` | all 0 or all 1 | ~0.41 | peaks at `000` and `111` |
| `SUPERPOSITION` | three independent \(\|+\rangle\) qubits | ~0.0004 | spread across all 8 outcomes |

Noise made both histograms messy. Only GHZ stayed correlated. That is the
metric's job: it is not "how noisy was the run", it is "how far is this
distribution from independent qubits".

`06_ghz_states` already computes those three. `metrics=["structure_score"]`
computes only this one; `metrics="quick"` is Structure Score plus
Concentration Index.

## What to do next

- Continue the basics path: `uv run qforge list`, then steps `02`–`11`.
- Sweep a parameter: `uv run qforge sweep 06_ghz_states -p error_rate=0.01,0.05,0.1 -s noise_enabled=true -s noise_type=depolarizing`
- Use the engine directly: [Quick Start](quickstart.md).
- Read the rest of the metrics: [Metrics](../api/metrics.md).

The Expo / React Native app is optional. Everything above is the installable
`qforge` package.
