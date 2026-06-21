# AGENTS.md — QForge Repository-Wide AI Rules

Owner: Roibín O'Toole
Last updated: 2026-04-05

## What This Is

QForge is a **general-purpose quantum experiment engine** built on Qiskit — for learning, research, and real hardware. The current research focus is structured decoherence, but the architecture is deliberately general. New experiment types (benchmarking, error correction, variational algorithms, etc.) are welcome.

## Scientific Rigor

Physics laws are non-negotiable. Code that violates quantum mechanics will be rejected.

- **Reproducibility**: All experiments must support deterministic execution with seeds and provenance tracking
- **Validation**: Schema validation (Pydantic) and physics tests (`pytest tests/physics`) are gateways, not suggestions
- **Correctness over convenience**: If a metric doesn't match pen-and-paper physics, the code is wrong
- **Data integrity**: Results are immutable; never modify saved experiment data

## Architecture Layers (strict separation)

```
src/core/           Pure physics — metrics, noise models, state preparation, shared math primitives (src/core/math)
src/engine/          Orchestration — run(), sweep(), models, visualization, provenance
src/experiments/     Research programs — pluggable experiment definitions
apps/api/            FastAPI REST endpoints
apps/client/         React Native / Expo frontend (Bloch sphere, circuit builder, glossary)
```

- `core` does NOT know about experiments or the engine
- `engine` does NOT know about specific research questions
- `experiments` calls into the engine, never the reverse
- `apps` are thin layers over the engine API

## Experiments Structure

Experiments are organized into 4 folders, each with `steps/` and `deep_dives/`:

```
experiments/
├── basics/          11 steps + 10 deep dives    Learn quantum computing
├── advanced/         8 steps +  7 deep dives    Quantum algorithms
├── decoherence/      6 steps +  2 deep dives    Structured decoherence research
└── hardware/         5 steps +  3 deep dives    Real IBM Quantum processors
```

49 registered experiments total. See `src/experiments/AGENTS.md` for the full registry and how to add new ones.

## Visualization System

6 renderers (histogram, density_matrix, correlation, circuit, metrics_summary, bloch_sphere) plus sweep utilities. Plugin architecture in `src/engine/visualization/`. Config accepts `visualization_type: list[str] | str`.

## Local AGENTS.md Files

Each major directory has its own AGENTS.md with domain-specific rules:

- `src/core/AGENTS.md` — physics primitives and metric implementation rules
- `src/core/analysis/metrics/AGENTS.md` — metric registry, adding new metrics
- `src/core/state_preparation/AGENTS.md` — state types, CustomState source modes
- `src/engine/execution/AGENTS.md` — execution backends, hardware integration
- `src/experiments/AGENTS.md` — experiment registry, step/deep_dive pattern, docstring standards

These refine the rules above but may not contradict them.

## Never

- Mix experiment logic into `src/core` or physics primitives into `src/engine`
- Reference SST, SQM, or personal theory branding — use "structured decoherence"
- Skip physics tests when modifying metrics or noise models
- Add AI attribution (Co-Authored-By, Powered by, Generated with) to commits, code, or docs
- Introduce dependencies with uncontrolled network access (framework must stay deterministic)

## Always

- Follow the `steps/` + `deep_dives/` pattern when adding experiments
- Include WHAT YOU'LL LEARN, CIRCUIT diagram, and TRY IT in every experiment docstring
- Update the nearest `AGENTS.md` when adding structural concepts
- Register new experiments in 4 places (folder init, root init, folder README, experiments AGENTS.md)
- Run `pytest` and verify via CLI before submitting changes
- Use `src/core` utilities instead of duplicating physics/math helpers — `src/core/math/` is the single source of truth for Pauli matrices, relaxation probabilities, TVD/Gini, and the canonical qubit/bit indexing convention
