# AGENTS.md — Repository-Wide AI Rules

Owner: Research Engineering (Roibín O'Toole)
Last updated: 2025-12-02
Token budget: 400

## ⚠️ SCIENTIFIC RIGOR IS PARAMOUNT

**This is a research framework, not a general-purpose tool.** Every change must uphold scientific validity:

- **Physics laws are non-negotiable** — Code that violates quantum mechanics or thermodynamics will be rejected.
- **Reproducibility is mandatory** — All experiments must be deterministic with explicit seeds and provenance tracking.
- **Validation precedes execution** — Schema validation and physics tests (`pytest tests/physics`) are gateways, not suggestions.
- **Data integrity is sacred** — Results are immutable; never modify saved experiment data without versioning.
- **Analytical correctness over convenience** — If a metric doesn't match pen-and-paper physics, the code is wrong.

**If you break scientific rigor, you break the entire framework's purpose.**

## Global Principles

1. This repository encodes physics-first quantum experimentation; any change must preserve structured entanglement/decoherence analysis.
2. Schema-hardened data contracts (Pydantic, JSON Schema) are mandatory for configs and results—never bypass validation layers.
3. Architectural layers are strict: `src/core` (metrics + physics primitives), `src/engine` (orchestration, pipelines, IO), `src/experiments` (concrete experiment definitions and notebooks).
4. Shared knowledge lives in `docs/` (see `docs/ai-context/AI_COLLABORATOR_NOTES.md`); code must reflect the documented boundaries.
5. Every domain with bespoke rules will have its own local `AGENTS.md`; consult them in addition to this global file.

## Never
- Invent new top-level directories or rename `src/core|engine|experiments`, `schemas`, or `docs` without a design RFC.
- Mix experiment orchestration logic into `src/core` or physics primitives into `src/engine`.
- Skip schema validation, physics tests (`pytest tests/physics`), or noise guardrails when introducing new experiment flows.
- Introduce dependencies that allow uncontrolled network or hardware access; this framework must stay deterministic and reproducible.
- Delete or overwrite data schemas/results without updating the corresponding specs under `schemas/` and `docs/`.

## Always
- Follow existing folder patterns when adding experiments (`src/experiments/<domain>/...`) or engine components (`src/engine/<service>`).
- Reuse shared utilities in `src/core` and `src/engine` instead of duplicating physics/math helpers.
- Update or create the nearest local `AGENTS.md` / `AI.md` when you add new structural concepts.
- Reference `docs/ai-context/AI_COLLABORATOR_NOTES.md`, `docs/architecture/ARCHITECTURE.md`, and any domain ADRs before modifying core behavior.
- Run formatting (Prettier/markdownlint for docs, Ruff/pytest as configured) before submitting changes.

## Scope
Local `AGENTS.md` files will live in:
- `src/core` — physics primitives, metrics, and schema utilities.
- `src/engine` — orchestration, runners, execution backends.
- `src/experiments` — domain-specific experiment suites and pipelines.
- `docs/` — AI-facing documentation strategy and research narratives.

These local profiles refine the boundaries above but may not contradict them. Always treat this root file as the source of truth for repository-wide intent.
