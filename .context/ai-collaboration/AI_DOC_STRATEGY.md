# AI Documentation Strategy

> **Status:** Draft for Team Review
> **Audience:** Engineering Team
> **Purpose:** Define a clear, maintainable, tool-agnostic approach for AI-readable documentation in the Qiskit Experiment Framework

## Table of Contents

1. [Summary: Why AI-Aware Docs Matter](#1-summary-why-ai-aware-docs-matter)
2. [Core Principles](#2-core-principles)
3. [Documentation Hierarchy](#3-documentation-hierarchy)
4. [Placement Rules](#4-placement-rules)
5. [What Goes in AI Docs vs Human Docs](#5-what-goes-in-ai-docs-vs-human-docs)
6. [What AI.md Should Not Contain](#6-what-aimd-should-not-contain)
7. [Templates](#7-templates)
   - [7.1 Root AGENTS.md](#71-root-agentsmd-template)
   - [7.2 Module AGENTS.md](#72-module-agentsmd-template-eg-srccore)
   - [7.3 Root AI.md](#73-root-aimd-template)
   - [7.4 Module AI.md](#74-module-aimd-template)
8. [Maintenance Model](#8-maintenance-model)
9. [When to Create or Skip Module-Level AI.md](#9-when-to-create-or-skip-module-level-aimd)
10. [FAQ and Anti-Patterns](#10-faq-and-anti-patterns)
11. [Quickstart Checklist](#11-quickstart-checklist)

---

## 1. Summary: Why AI-Aware Docs Matter

AI-assisted development tools are now embedded in everyday engineering. They produce high-quality code only when the surrounding context is accurate, structured, and consistent.

In a scientific framework like this, precision is paramount. AI does not infer physical laws or experimental constraints. It follows:

- Folder structure
- Examples
- Patterns
- Constraints
- Explicit rules

When these are missing or unclear, AI will improvise — and often incorrectly (e.g., creating unphysical quantum states or bypassing schema validation).

**Typical AI Failure Modes:**

- Inventing unphysical parameters (e.g., T1 > T2).
- Bypassing Pydantic validation layers.
- Placing orchestration logic in physics primitives.
- Ignoring established noise models.

These are not model shortcomings. They are context engineering failures.

## 2. Core Principles

- **Tool-agnostic**: Compatible with Copilot, Cursor, Claude, ChatGPT and future AI tooling.
- **High-signal, low-noise**: Short, structured, and free of narrative or explanation.
- **Layered documentation hierarchy**: `AGENTS.md` (global) → `AGENTS.md` (local) → `AI.md` (root) → `AI.md` (module).
- **Close to the code**: Each file must live inside the directory it governs to ensure correct AI context.
- **Explicit boundaries**: AI must understand domain rules (Core vs Engine vs Experiments), allowed imports, and architectural constraints without guesswork.

## 3. Documentation Hierarchy

### AGENTS.md (Repository-Level)

- **Location**: Repository root (`/`)
- **Purpose**: Defines high-level architectural guardrails for the entire repository. Explains the "Physics-First" philosophy, schema enforcement, and strict layer separation.
- **Applies to**: Every folder and module inside this repo.

### Root AI.md

- **Location**: Repository root (`/AI.md`)
- **Purpose**: Provides a structural overview of the repository. Describes `src/core`, `src/engine`, `src/experiments`. Explains patterns for Pydantic usage, Qiskit integration, and testing.

### Module-Level AGENTS.md / AI.md

- **Location**: Inside specific module folders (e.g., `src/core/AGENTS.md`, `src/experiments/AGENTS.md`).
- **Purpose**: Defines responsibilities and constraints for that specific domain.
  - `src/core`: Physics primitives, pure functions, no side effects.
  - `src/engine`: IO, orchestration, side effects allowed.
  - `src/experiments`: Concrete implementations, notebook constraints.

## 4. Placement Rules

```text
qiskit-experiment-framework/
├── AGENTS.md          # Global physics rules, schema enforcement, layer boundaries
├── AI.md              # Repo architecture overview
├── docs/              # Human documentation (SST, Research Notes)
│   └── AGENTS.md      # Rules for writing documentation (style, structure)
└── src/
    ├── core/
    │   └── AGENTS.md  # Physics primitives only. No IO. Strict typing.
    ├── engine/
    │   └── AGENTS.md  # Orchestration rules. Database/File access patterns.
    └── experiments/
        └── AGENTS.md  # Experiment design rules. Notebook constraints.
```

## 5. What Goes in AI Docs vs Human Docs

| Content Type                   | AI Docs (AGENTS.md / AI.md) | Human Docs (docs/*.md) |
| :----------------------------- | :-------------------------- | :--------------------- |
| Rules, constraints, invariants | Yes                         | No                     |
| Architecture overview          | Summary                     | Detailed               |
| Folder structure               | Yes                         | Yes                    |
| Golden-path examples           | Yes                         | No                     |
| Explanations, reasoning        | No                          | Yes                    |
| Physics theory & SST           | No                          | Yes                    |
| Historical decisions           | No                          | Yes                    |

AI docs are not explanatory; they are instructional.

## 6. What AI.md Should Not Contain

AI.md files must remain short, structural, and constraint-focused. They should not include narrative, explanation, or business context.

**Do not include:**

- Detailed physics derivations (link to `docs/research-docs/`).
- Long-form SST philosophy (link to `docs/research-docs/sst-ext.md`).
- Payload schemas (link to Pydantic models).
- Explanations of *why* we use a specific noise model (just say *use* it).

## 7. Templates

### 7.1 Root AGENTS.md Template

```markdown
# AGENTS.md — Repository-Wide AI Rules

Owner: Research Engineering
Last updated: YYYY-MM-DD
Token budget: 350

## Global Principles

1. This repository encodes physics-first quantum experimentation.
2. Schema-hardened data contracts (Pydantic, JSON Schema) are mandatory.
3. Architectural layers are strict: `src/core` (physics), `src/engine` (orchestration), `src/experiments` (impl).

## Never

- Invent new top-level directories.
- Mix experiment orchestration logic into `src/core`.
- Skip schema validation or physics tests.
- Introduce non-deterministic dependencies.

## Always

- Follow existing folder patterns.
- Reuse shared utilities in `src/core`.
- Run `pytest tests/physics` after core changes.
```

### 7.2 Module AGENTS.md Template (e.g., src/core)

```markdown
# AGENTS.md — Core Physics Primitives

Owner: Research Engineering
Last updated: YYYY-MM-DD
Token budget: 300

## Purpose

- Pure physics calculations, metrics, and data schemas.
- No side effects (IO, Network).

## Local Boundaries

- Allowed imports: `numpy`, `scipy`, `qiskit` (core only), `pydantic`.
- Forbidden imports: `src.engine`, `matplotlib` (visualization belongs in analysis, not core logic).

## Do Not

- Perform file IO.
- Define experiment execution logic.

## Always

- Use Pydantic v2 for all data structures.
- Ensure functions are pure and deterministic.
```

### 7.3 Root AI.md Template

```markdown
# AI.md — Repository Architecture Overview

Owner: Research Engineering
Last updated: YYYY-MM-DD
Token budget: 500

## 1. Overview

A framework for Structured Quantum Mechanics (SQM) experiments using Qiskit.

## 2. Architectural Components

- `src/core`: Domain entities, physics logic, metrics.
- `src/engine`: Runners, data persistence, analysis pipelines.
- `src/experiments`: Experiment definitions and configurations.

## 3. Boundaries

`experiments` -> `engine` -> `core`.
`core` never imports `engine` or `experiments`.

## 4. Patterns

- **Config**: All experiments defined by Pydantic models in `src/core/config`.
- **Results**: All outputs validated against schemas in `src/core/results`.
```

## 8. Maintenance Model

AI documentation must be updated whenever:

- Folder structures change.
- New physics modules are added.
- Schema patterns change.

**Rule:** AI documentation must be updated in the same PR as any structural change.

## 9. When to Create or Skip Module-Level AI.md

**Create when:**

- A specific experiment has complex custom logic.
- A new engine backend is added.

**Skip when:**

- Adding a standard experiment that follows existing patterns.
- Adding simple utility functions.

## 10. FAQ and Anti-Patterns

**Should physics theory be in AI.md?**
No. Link to `docs/research-docs/`.

**Do we need an AI.md for every experiment?**
No. Only if it deviates from the standard `BaseExperiment` pattern.

## 11. Quickstart Checklist

- [ ] Choose the correct file type (Root AGENTS, Module AGENTS).
- [ ] Keep it concise and structural.
- [ ] Include metadata (Owner, Last updated).
- [ ] Focus on rules, boundaries, and allowed imports.
- [ ] Place inside the directory it governs.
