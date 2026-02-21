# Correlated Noise Hypothesis Test: Findings Report

## Date: 2026-02-20
## Status: Framework Validated, Key Methodological Insights

---

## 1. Hypothesis Under Test

**H_corr**: If decoherence follows entanglement topology, then noise correlated along topology edges (qubit pairs connected by CX gates) should produce measurably different error patterns than independent noise.

**Experimental Design**: Run GHZ state under three noise conditions:
1. **Aligned** (cs > 0): Correlated Pauli errors (XX, YY, ZZ) boosted on topology-connected pairs
2. **Independent** (cs = 0): Standard depolarizing noise (baseline)
3. **Anti-aligned** (cs < 0): Correlated errors suppressed on topology-connected pairs

**Expected outcome**: A valid topology-sensitive metric should show:
- Aligned > 0 (significant)
- Independent ~ 0
- Anti-aligned < 0

---

## 2. Correlated Noise Model

### Implementation: `src/core/noise_models/correlated_depolarizing.py`

The `CorrelatedDepolarizingNoise` model applies:
- **Single-qubit gates**: Standard depolarizing (same as baseline)
- **Two-qubit gates on topology-connected pairs**: Modified 2-qubit Pauli channel with correlation bias
- **Two-qubit gates on non-connected pairs**: Standard 2-qubit depolarizing

### Channel Construction (Mixing Formula)

The 15 non-identity 2-qubit Paulis are partitioned:
- **Correlated**: XX, YY, ZZ (3 Paulis) — same error on both qubits
- **Uncorrelated**: remaining 12 Paulis

For `correlation_strength` (cs) >= 0:
```
P(correlated Pauli)   = (1-cs) * p/15 + cs * p/3
P(uncorrelated Pauli) = (1-cs) * p/15
```

For cs < 0 (let t = |cs|):
```
P(correlated Pauli)   = (1-t) * p/15
P(uncorrelated Pauli) = (1-t) * p/15 + t * p/12
```

**Key property**: Total error probability is preserved at `p` for all values of cs.

At cs=0.3, p=0.05: correlated Paulis get 3.14x the probability of uncorrelated ones.

### Topology Matrices

| State Type | Topology | Connected Pairs (n=4) |
|---|---|---|
| GHZ | Linear chain | (0,1), (1,2), (2,3) |
| W | All-to-all | All pairs |
| Cluster | Linear chain | (0,1), (1,2), (2,3) |

---

## 3. Finding #1: MI-Based EEC Cannot Distinguish Noise Correlations from State Correlations

### The Standard EEC Metric

The Entanglement-Error Correlation (EEC) computes:
1. **Topology matrix W(i,j)**: Theoretical entanglement weights (distance-decay for GHZ)
2. **Error matrix E(i,j)**: Pairwise mutual information from measurement data
3. **EEC = Pearson(W_flat, E_flat)**

### Observed Failure

At all tested parameters (4-6 qubits, p=0.05-0.40, cs=0.0-0.8), EEC was **indistinguishable across noise conditions**:

| Condition | EEC (4q, p=0.3) | EEC (6q, p=0.3) |
|---|---|---|
| Aligned (cs=0.8) | 0.351 | 0.572 |
| Independent (cs=0) | 0.348 | 0.601 |
| Anti-aligned (cs=-0.8) | 0.354 | 0.598 |

### Root Cause

The mutual information matrix E(i,j) is **dominated by state-inherent correlations**, not noise-induced correlations. For a GHZ state (|0...0> + |1...1>):

1. All qubit pairs are maximally correlated through the superposition
2. At p=0.05, >85% of outcomes are ideal (|0000> or |1111>)
3. The MI between any pair of qubits is dominated by this state structure
4. Noise-induced MI perturbations are tiny compared to state MI

**Additionally**, the GHZ topology matrix W uses ring-distance decay which doesn't match the linear chain circuit connectivity, reducing sensitivity.

### Implication

**EEC is suitable for comparing different state topologies** (GHZ vs W vs Cluster) but **not for comparing noise models on the same state**. For the latter, a noise-specific metric is needed.

---

## 4. Finding #2: Bit Covariance Reveals the Signal (But Has a Confound)

### Raw Bit Covariance

A simpler metric: Cov(b_i, b_j) = E[b_i * b_j] - E[b_i] * E[b_j], where b_i is the measured bit value.

At p=0.3, cs=0.8 (6 qubits):
| | Adjacent Mean | Non-Adjacent Mean |
|---|---|---|
| Aligned | 0.162 | 0.073 |
| Independent | 0.133 | 0.073 |
| Anti-aligned | 0.116 | 0.063 |

Adjacent covariance clearly differentiates! But...

### The (0,1) Confound

Pair (0,1) always has the highest covariance regardless of noise condition. This is because the first CX gate in the GHZ circuit (CX(0,1)) accumulates the most downstream noise — errors on this gate propagate through ALL subsequent CX gates.

This means Pearson correlation between W (uniform adjacency) and Cov (dominated by pair (0,1)) produces similar values across conditions.

---

## 5. Finding #3: Excess Covariance Selectivity (NTC) Works Correctly

### The Noise Topology Correlation (NTC) Metric

NTC isolates the noise-correlation effect by computing:
1. **Baseline**: Run independent noise (cs=0), get covariance matrix `Cov_baseline`
2. **Test condition**: Run with correlated noise, get `Cov_test`
3. **Excess covariance**: `Delta = Cov_test - Cov_baseline`
4. **Topology selectivity**: `NTC = mean(Delta_adjacent) - mean(Delta_nonadjacent)`

A permutation test shuffles qubit labels on the adjacency matrix to generate a null distribution.

### Implementation: `src/experiments/topology_comparison.py`

```python
# In run_correlated_comparison(), the independent condition serves as baseline
baseline_counts = all_counts["independent"]

# For each condition:
ntc_result = _noise_topology_correlation(
    counts=counts,
    baseline_counts=baseline_counts,
    state_type="GHZ",
    n_qubits=num_qubits,
    n_permutations=1000,
)
```

### Results: Parameter Sweep

| Qubits | Error Rate | cs | NTC | p-value | Significant? | Effect Size |
|---|---|---|---|---|---|---|
| 4 | 0.10 | 0.5 | +0.0059 | 0.083 | No | +1.61 |
| 4 | 0.10 | 0.8 | +0.0084 | 0.083 | No | +1.57 |
| 4 | 0.20 | 0.5 | +0.0103 | 0.167 | No | +1.46 |
| 4 | 0.20 | 0.8 | +0.0160 | 0.167 | No | +1.45 |
| 4 | 0.30 | 0.5 | +0.0159 | 0.083 | No | +1.43 |
| 4 | 0.30 | 0.8 | +0.0253 | 0.083 | No | +1.41 |
| **6** | **0.10** | **0.5** | **+0.0088** | **0.003** | **Yes** | **+2.70** |
| **6** | **0.10** | **0.8** | **+0.0124** | **0.003** | **Yes** | **+2.73** |
| **6** | **0.20** | **0.5** | **+0.0130** | **0.006** | **Yes** | **+2.65** |
| **6** | **0.20** | **0.8** | **+0.0218** | **0.006** | **Yes** | **+2.66** |
| **6** | **0.30** | **0.5** | **+0.0184** | **0.003** | **Yes** | **+2.68** |
| **6** | **0.30** | **0.8** | **+0.0289** | **0.003** | **Yes** | **+2.67** |

### Three-Condition Comparison (6q, p=0.3, cs=0.8)

| Condition | NTC | p-value | Significant? | Adj Excess | Non-adj Excess |
|---|---|---|---|---|---|
| **Aligned** | **+0.029** | **0.003** | **Yes** | +0.029 | -0.000 |
| Independent | 0.000 | 1.000 | No | 0.000 | 0.000 |
| Anti-aligned | -0.007 | 1.000 | No | -0.017 | -0.010 |

### Interpretation

1. **Aligned noise**: Excess covariance concentrates **exclusively on adjacent pairs** (+0.029), with zero excess on non-adjacent pairs. The permutation test confirms this is significant (p=0.003, effect_size=2.67).

2. **Independent noise**: NTC = 0 exactly (it is the baseline by construction).

3. **Anti-aligned noise**: NTC is negative (-0.007), meaning adjacent pairs lose MORE covariance than non-adjacent pairs. However, ALL pairs show reduced covariance, consistent with the anti-correlated channel distributing error mass away from correlated Paulis.

---

## 6. Why 4 Qubits Are Insufficient

With 4 qubits there are only 6 qubit pairs (3 adjacent, 3 non-adjacent). The permutation test over 4! = 24 permutations gives a minimum achievable p-value of 1/24 = 0.042. The NTC effect is in the right direction (positive for aligned, zero for independent, negative for anti-aligned) but:

- Many permutations produce similar selectivity values
- The minimum p-value observed is 0.083 (2/24), just above the 0.05 threshold

**At 6 qubits** (15 pairs, 720 permutations), the test has sufficient resolution and all aligned conditions achieve p < 0.01.

---

## 7. Circuit Depth Balancing Verification

As a prerequisite for this experiment, circuit depth balancing was implemented:

```python
from src.core.state_preparation import prepare_state
c = prepare_state("GHZ", 3, balance="gate_count")
# Result: all qubits have 2 gates (q2 padded with 1 identity)
```

The state-aware null model confirms symmetry under balanced circuits:
```python
from src.core.analysis.core.null_models import state_aware_null_model
null = state_aware_null_model("GHZ", 3, error_rate=0.05)
# abs(null["001"] - null["100"]) < 1e-10  # Symmetric when balanced
```

---

## 8. Architecture: How the Pieces Fit

```
src/experiments/topology_comparison.py
  BalancedTopologyComparison
    run_correlated_comparison()
      |
      |--> src/engine/api.run() x3 (aligned, independent, anti-aligned)
      |      |
      |      |--> src/engine/execution/runner.py
      |      |      |
      |      |      |--> src/core/state_preparation/  (GHZ with gate_count balancing)
      |      |      |--> src/core/noise_models/
      |      |             |--> depolarizing.py           (cs=0 baseline)
      |      |             |--> correlated_depolarizing.py (cs != 0)
      |      |                    |
      |      |                    |--> _build_correlated_2q_channel()
      |      |                    |      Mixing formula: standard <-> correlated Paulis
      |      |                    |--> apply()
      |      |                           Per-pair noise: correlated on topology edges,
      |      |                           standard on non-edges
      |      |
      |      |--> src/engine/analysis/research_integration.py
      |             (computes standard research metrics)
      |
      |--> _compute_bit_covariance_matrix()
      |      Cov(b_i, b_j) from measurement counts
      |
      |--> _noise_topology_correlation()
             Delta = Cov_test - Cov_baseline
             NTC = mean(Delta_adj) - mean(Delta_nonadj)
             Permutation test on qubit-label shuffles
```

### Key Files

| File | Role |
|---|---|
| `src/core/noise_models/correlated_depolarizing.py` | Correlated noise channel with mixing formula |
| `src/experiments/topology_comparison.py` | Experiment + NTC metric + permutation test |
| `src/core/state_preparation/base_state.py` | Gate-count balancing |
| `src/core/analysis/core/null_models.py` | State-aware null model |
| `src/core/analysis/metrics/entanglement_error_correlation.py` | EEC + permutation test |

---

## 9. Conclusions

### What Works

1. **Correlated noise model** correctly creates topology-dependent pair correlations
2. **NTC metric** successfully detects correlated noise (significant at 6+ qubits)
3. **Circuit depth balancing** removes the asymmetric gate-depth artifact
4. **State-aware null model** correctly predicts symmetric error distribution for balanced circuits

### What Doesn't Work (and Why)

1. **MI-based EEC** cannot distinguish noise correlations from state correlations on GHZ states — the state's global entanglement dominates the mutual information matrix
2. **4-qubit tests** lack statistical power for permutation tests (only 24 permutations, minimum p = 0.042)

### Methodological Insights

1. **State structure dominates at low noise**: At p < 0.1, the GHZ state's inherent correlations overwhelm noise effects in most metrics
2. **Excess-over-baseline is essential**: Raw covariance includes both state and noise contributions; only the excess (relative to independent noise baseline) isolates the noise effect
3. **Qubit count matters for significance**: Need >= 6 qubits (>= 15 pairs) for the permutation test to reach significance at alpha=0.05
4. **The CX chain creates asymmetric noise propagation**: Even with gate-count balancing, the first CX gate's errors propagate further than later gates, creating non-uniform pair covariances

### Next Steps

1. Test on **cluster states** (local stabilizer structure may give sharper per-pair signals)
2. Test on **real hardware** to see if actual device noise shows topology-dependent correlations
3. Develop **multi-scale NTC** that accounts for different path lengths in the circuit graph
4. Investigate whether NTC can be computed WITHOUT a baseline run (e.g., using the state-aware null model prediction instead)
