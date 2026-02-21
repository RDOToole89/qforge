# Where I Left Off

**Date:** February 2026
**Branch:** `refactor/simplify-codebase` (PR #3 → main)
**State:** Everything committed, tests passing (252/252), results reproduced.

---

## What exists and works

### The framework
- Full experiment engine: `run()` and `sweep()` in `src/engine/api.py`
- 6 quantum states: GHZ, Bell, W, Cluster, Superposition, Custom
- Noise models: depolarizing + correlated depolarizing (with topology)
- Gate-count circuit balancing to remove preparation-depth confounds
- Deterministic seeds throughout — every result is reproducible
- 252 tests, all green

### The completed study: State Probe Sensitivity
- **47 NTC experiments** across 3 phases (see `docs/research-docs/STATE_PROBE_FINDINGS.md`)
- **42 fingerprint analysis conditions** (Direction 2)
- Key results:
  - GHZ is the only effective Z-basis probe (9/9 significant)
  - Cluster and |+>^n produce exactly zero signal (Pauli invariance — a real theorem, not a bug)
  - W states are genuinely insensitive, confirmed across 10 seeds
  - **Star noise finding:** NTC says "no star noise detected" but the fingerprint shows equal-magnitude signal in a different direction. The metric was blind, not the probe.
  - Noise fingerprints **scale** (same direction, growing magnitude) rather than shift — mean cosine similarity 0.874

### Key files to re-read when you come back
- `docs/research-docs/STATE_PROBE_FINDINGS.md` — the full report with Appendix B walkthrough
- `docs/research-docs/further_research.md` — three proposed next directions
- `docs/research-docs/research_direction.md` — the original experimental protocol
- `src/experiments/state_probe_sensitivity.py` — all experiment code
- `src/core/analysis/core/correlations.py` — fingerprint utilities
- `results/fingerprint_analysis/summary.json` — Direction 2 summary

---

## Where the physics stopped

You hit the boundary between "intuition + simulation" and "formalism." Specifically:

1. **You understand** what the Bloch sphere is, what Pauli operators do, what covariance measures, why uniform distributions are noise-invariant, and how cosine similarity captures topology differences.

2. **You don't yet have** the linear algebra to derive things like: why CZ gates preserve measurement probabilities (hint: diagonal unitaries commute with Z-basis projectors), how to construct optimal measurement bases for a given state, or how error correction codes relate to noise structure.

3. **The ceiling you hit:** The next physics questions (measurement basis adaptation, coherent errors, entanglement witnesses) all require comfort with matrix multiplication, tensor products, and eigenvalue decomposition. Not PhD-level math, but undergraduate linear algebra applied to quantum mechanics.

---

## Three ways to continue (pick one when you have time)

### Option A: Textbook mode (learning-focused)
Use the framework to work through a QM/QC textbook chapter by chapter. Implement each concept as an experiment.

Good books for your level:
- **"Quantum Computing: An Applied Approach" by Hidary** — practical, code-heavy, builds intuition
- **"Quantum Computation and Quantum Information" by Nielsen & Chuang** — the bible, but dense. Chapters 1-4 cover the linear algebra you need
- **3Blue1Brown's "Essence of Linear Algebra"** YouTube series — visual, exactly your style, and the prerequisite for everything else

Concrete first steps:
1. Watch 3B1B linear algebra series (3-4 hours total)
2. Implement single-qubit gate visualisation on the Bloch sphere using your framework
3. Work through tensor products by building 2-qubit states from scratch
4. Re-derive the Pauli invariance theorem yourself with actual matrix math

### Option B: Measurement basis experiment (research-focused)
The single highest-value next experiment from the study:

> If you measure Cluster states in the X-basis instead of Z-basis, does the NTC signal become non-zero?

This tests whether the Pauli invariance blindness is a fundamental limit or just a basis choice. The code changes are small (add a basis rotation before measurement in the runner). The physics is genuinely interesting — nobody has tested this in simulation as far as I know.

Implementation sketch:
1. Add `measurement_basis` param to `ExperimentConfig` (values: "Z", "X", "Y", "stabilizer")
2. In the runner, insert H gates before measurement for X-basis (or S†H for Y-basis)
3. Re-run Phase 1 with Cluster state in X-basis
4. If NTC > 0 → the state was always sensitive, just measured wrong. Paper-worthy finding.

### Option C: Topology classifier (engineering-focused)
Build a simple classifier that identifies noise topology from raw fingerprint vectors, without requiring a matched template. The data already exists.

Steps:
1. Add ring and grid noise topologies (extend `topology.py`)
2. Run fingerprint analysis for all 4-5 topologies
3. Train a nearest-centroid or small neural net on the fingerprint vectors
4. Test: given a blind fingerprint, can you identify the noise topology?

This is more ML/engineering than physics, but it's a natural extension of the star noise finding and plays to your strengths.

---

## Don't forget

- All results are simulation-only (Qiskit Aer). Hardware validation would be the ultimate test but requires access to a real quantum computer (IBM Quantum has free tiers).
- The `CLAUDE.md` has full architecture docs. Read it first when coming back.
- Python venv is at `venv/bin/python`. All deps are in `requirements.txt`.
- No AI attribution in commits or docs — that's a standing preference.

---

Good luck with Sommi. This project will be here when you're ready.
