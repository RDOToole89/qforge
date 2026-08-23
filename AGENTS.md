# AGENTS.md — QForge Repository-Wide AI Rules

Owner: Roibín O'Toole

## What This Is

QForge is a **general-purpose quantum experiment engine** built on Qiskit — for learning, experimentation, and real hardware. It hides Qiskit plumbing so you can set up experiments, learn quantum mechanics, and run real research — with an analysis layer configured for the question you are asking. The architecture is deliberately general: new experiment types (benchmarking, error correction, variational algorithms, etc.) are welcome. See `CLAUDE.md` for the full project overview, API examples, and the rules for working in this repo — this file summarizes the structural rules.

## Scientific Rigor

Physics laws are non-negotiable. Code that violates quantum mechanics will be rejected.

- **Reproducibility**: All experiments must support deterministic execution with seeds and provenance tracking
- **Validation**: Schema validation (Pydantic) and physics tests (`pytest tests/physics`) are gateways, not suggestions
- **Correctness over convenience**: If a metric doesn't match pen-and-paper physics, the code is wrong
- **Data integrity**: Results are immutable; never modify saved experiment data

## Architecture Layers (strict separation)

```
src/qforge/core/           Pure physics — metrics, noise models, state preparation, shared math primitives (src/qforge/core/math)
src/qforge/engine/          Orchestration — run(), sweep(), models, visualization, provenance
src/qforge/experiments/     Experiment programs — pluggable experiment definitions
apps/api/            FastAPI REST endpoints (thin consumer of the engine)
apps/client/         React Native / Expo visual lab (talks to apps/api only)
```

- `core` does NOT know about experiments or the engine
- `engine` does NOT know about specific experiment topics
- `experiments` calls into the engine, never the reverse
- `apps` are thin layers over the engine API — they do not own physics
- The documented public import is `qforge` (`from qforge import run`). `apps/` stays a consumer; HTTP JSON and codegen are the bridge, not Python import paths.

The engine runs without the visual lab. The 15-minute path is
`docs/guides/getting-started/first-run.md`. Keep visual-lab freeze (parked
FE-1…FE-6 in `apps/AGENTS.md`) until the owner unfreezes it.

## Experiments Structure

Experiments are organized into 4 folders, each with `steps/` and `deep_dives/`:

```
experiments/
├── basics/          11 steps + 10 deep dives    Learn quantum computing
├── advanced/         8 steps +  7 deep dives    Quantum algorithms
├── decoherence/      6 steps +  2 deep dives    Decoherence structure experiments
└── hardware/         5 steps +  3 deep dives    Real IBM Quantum processors
```

49 registered experiments total. See `src/qforge/experiments/AGENTS.md` for the full registry and how to add new ones.

## Visualization System

6 renderers (histogram, density_matrix, correlation, circuit, metrics_summary, bloch_sphere) plus sweep utilities. Plugin architecture in `src/qforge/engine/visualization/`. Config accepts `visualization_type: list[str] | str`. The circuit renderer is Qiskit's `circuit.draw(output='mpl')` plus unique-gate explainers; omit `"circuit"` or set `"none"` to skip.

## Local AGENTS.md Files

Each major directory has its own AGENTS.md with domain-specific rules:

- `src/qforge/core/AGENTS.md` — physics primitives and metric implementation rules
- `src/qforge/core/analysis/metrics/AGENTS.md` — metric registry, adding new metrics
- `src/qforge/core/state_preparation/AGENTS.md` — state types, CustomState source modes
- `src/qforge/engine/execution/AGENTS.md` — execution backends, hardware integration
- `src/qforge/experiments/AGENTS.md` — experiment registry, step/deep_dive pattern, docstring standards
- `apps/AGENTS.md` — engine↔API↔client contract, visual-lab freeze, parked frontend gaps
- `apps/client/src/features/bloch-sphere/AGENTS.md` — CPTP visualizer (frozen scope)
- `apps/client/src/features/circuit-builder/AGENTS.md` — circuit builder + Bloch playback (frozen scope)

These refine the rules above but may not contradict them.

## Never

- Mix experiment logic into `src/core` or physics primitives into `src/engine`
- Add chemistry, a Hamiltonian type, or an energy metric to core — engine estimates ⟨P⟩; programs interpret (VQE energy, QAOA MaxCut cost)
- Skip physics tests when modifying metrics or noise models
- Add visual-lab features, presets, or native-app work while the visual-lab freeze is in `apps/AGENTS.md`
- Add AI attribution (Co-Authored-By, Powered by, Generated with) to commits, code, or docs
- Introduce dependencies with uncontrolled network access (framework must stay deterministic)

## Always

- Follow the `steps/` + `deep_dives/` pattern when adding experiments
- Include WHAT YOU'LL LEARN, CIRCUIT diagram, and TRY IT in every experiment docstring
- Update the nearest `AGENTS.md` when adding structural concepts
- Register in-tree experiments in 4 places (folder init, root init, folder README, experiments AGENTS.md). Out-of-tree programs use `register_experiment()` — do not require a core or registry edit.
- Run `pytest` and verify via CLI before submitting changes
- Use `src/core` utilities instead of duplicating physics/math helpers — `src/qforge/core/math/` is the single source of truth for Pauli matrices, relaxation probabilities, TVD/Gini, and the canonical qubit/bit indexing convention
- When changing engine models, metric profiles, state preparation, or `bloch_math`, regenerate frontend catalogs and goldens (`scripts/gen_frontend_constants.py`, `scripts/gen_quantum_golden.py`) and keep `git diff` clean on `apps/client/src/generated` and the golden fixtures — see `apps/AGENTS.md`
