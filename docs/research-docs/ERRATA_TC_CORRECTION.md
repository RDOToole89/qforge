# Errata: Total Correlation Values Corrected

**Date:** 2026-04-04
**Affects:** HARDWARE_SCALING_RESULTS.md, STRUCTURED_DECOHERENCE_PAPER_DRAFT.md

## What happened

During the live hardware experiment session, Total Correlation (TC) values for W states were extracted from `result.metrics_bundle` in inline scripts. These values were inflated — likely due to the engine's metrics computation receiving incomplete counts during the live session (not all outcomes were included in the counts dict passed to the metric function).

When TC is recomputed from the full saved counts data, the values are significantly lower.

## Corrected values

### W Scaling (Experiment 5)

| N | TC (reported) | TC (corrected from saved data) |
|---|--------------|-------------------------------|
| 2 | 0.548 | 0.534 |
| 3 | 0.878 | 0.623 |
| 4 | 1.250 | 0.545 |
| 5 | 1.871 | 0.640 |
| 6 | 2.312 | 0.427 |

### W-6 Topology Comparison (Experiment 2)

| Metric | Reported | Corrected |
|--------|----------|-----------|
| TC | 0.836 | ~0.4-0.6 (cannot verify exactly — full counts not saved) |
| CI | 711 | ~313 (from full counts of later run) |

### Impact on findings

| Claim | Status |
|-------|--------|
| "6x TC gap between hardware and simulation" | **RETRACTED** — the gap was a reporting artifact |
| "Open modeling gap" (Experiments 9, 10) | **RETRACTED** — hardware TC matches simulation within 1.1x |
| W shows "less globally correlated" structure than GHZ | **STILL VALID** — GHZ TC ~4.4 vs W TC ~0.5 |
| SS-based findings (scaling, topology, backend) | **UNAFFECTED** — SS values are consistent across all paths |
| Amplification vs redistribution (entropy analysis) | **UNAFFECTED** — computed directly from raw counts |

### What was NOT affected

- All Structure Score (SS) values — consistent across computation paths
- All entropy and KL divergence values — computed from raw counts
- The core River vs Fog distinction (12x SS separation)
- The GHZ scaling trend
- The W scaling trend (SS)
- The backend comparison (SS CV = 5.7%)
- The Cluster negative result

### Root cause

The TC inflation occurred because the live hardware session's metrics bundle received a subset of outcomes. TC = Σ H(Xi) - H(joint). When the joint distribution has fewer outcomes, joint entropy decreases while marginal entropies stay roughly the same, inflating TC.

### Lesson

Always recompute metrics from saved full counts rather than relying on values extracted during live sessions. The framework now saves complete count dictionaries, making post-hoc verification possible.
