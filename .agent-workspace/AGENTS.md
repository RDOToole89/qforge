# AGENTS.md — Agent Workspace

> How AI agents use this scratchpad: a place for in-progress thinking that lives *outside* the committed docs until it has proven durable.

**Parent:** Root [`AGENTS.md`](../AGENTS.md) and [`CLAUDE.md`](../CLAUDE.md) · **Last reviewed:** 2026-06-21

---

## 1. What This Is

This is the **scratchpad** for AI agents working on QForge. It is the boundary of the
codebase — where an agent records what it's seeing, planning, or unsure about *before*
that understanding is solid enough to commit.

- **Committed docs** (`CLAUDE.md`, root + leaf `AGENTS.md`, `docs/`) are **crystallized
  knowledge** — things that survived verification and proved useful across sessions.
- **This workspace** is the **growth medium** — ephemeral, speculative, sometimes wrong,
  but where the next durable insight starts.

The relationship is conjecture → criticism → knowledge: workspace notes become committed
docs only after they prove correct and reusable. Until then, they stay separate.

---

## 2. The Growth Model

Knowledge grows at the boundary (Deutsch's evolutionary view: conjectures are created,
criticised, and either survive as knowledge or are replaced). QForge documentation
follows the same one-directional pattern:

```
Observation (workspace)  →  Pattern recognition  →  Promotion (committed docs)  →  New boundary
       ↑                                                                              │
       └──────────────────── new observations at the new boundary ────────────────────┘
```

- **The workspace is the conjecture space.** Agents write observations, plans, and drafts.
- **Committed docs are the surviving knowledge.** Promoted only after it is verified
  against the code and found useful beyond one session.
- **The promotion protocol is the criticism mechanism.** Most notes never survive — that
  is healthy. Only durable insight is promoted.

### When the framework can't express something

If you hit something the documented architecture can't describe — a metric whose behavior
isn't captured by the analysis docs, an execution path that doesn't fit the engine/core
split, an experiment shape that breaks the `steps/` + `deep_dives/` pattern — **that's a
growth signal, not a failure.**

1. **Record it** in `active/observations/`.
2. **Don't force it** into an existing category — that creates false structure.
3. **Let it recur** — if the same thing shows up 2–3 times, the boundary is real.
4. **Step outside** — extend the relevant `AGENTS.md`, add a `docs/architecture/` note, or
   raise it with the maintainer.

---

## 3. How Agents Use This Workspace

### Starting a session
1. **Check `active/`** — unfinished work from a previous session?
2. **Check `todo/`** — flagged work relevant to today's task?
3. **Check `archive/`** — past observations relevant to what you're about to do?

### During work
- **Investigating physics/metrics behavior?** → note it in `active/observations/`
- **Building something non-trivial?** → draft a plan in `active/plans/`
- **Writing or restructuring docs?** → draft in `active/drafts/` before committing
- **Noticed something you can't act on now?** → drop it in `todo/`

### Ending a session — the reflection moment
Ask: *did I produce workspace artifacts, and for each, is it intermediary or architectural?*

**Most workspace knowledge is intermediary.** It served its purpose during the session.
The default is **discard or archive**, not promote.

- Debugging notes → **discard** (the fix is in the code + commit message)
- Session context ("tried X, failed because Y") → **discard** (the commit has it)
- Plans for completed work → **discard** (the code IS the plan now)
- One-off observations that don't recur → **discard** (noise, not signal)

**Architectural knowledge (promote — rare):**
- Describes *how the system works* in a way the code can't → promote to the relevant
  `AGENTS.md` or `docs/architecture/`
- Captures *why* a non-obvious choice was made → promote to `docs/architecture/`
- Same observation has appeared 3+ times → the pattern IS architecture; codify it
- A research finding worth keeping → `docs/research/`

**The bar for promotion is high.** Every committed doc is maintenance burden. If the
knowledge is derivable from the code, `git log`, or an existing doc, it doesn't need a new
doc. Only promote what would be *lost* otherwise and *needed* by a future session.

### After promoting — wire it into the network
A new committed doc that nothing links to is an orphan. Check:
1. **Entry point:** does root `CLAUDE.md` / `AGENTS.md` need a reference? (loaded every session)
2. **Navigation:** can an agent *find* it by walking `CLAUDE.md` → leaf `AGENTS.md` → `docs/`?
3. **Locality:** does the nearest leaf `AGENTS.md` (e.g. `src/core/analysis/metrics/AGENTS.md`)
   reference it?
4. **Consistency:** does it overlap or contradict an existing doc? Merge or cross-reference.

---

## 4. Self-Consistency Check (a mirror, not a gate)

Periodically the workspace reflects on the codebase it serves:

- **Do the `AGENTS.md` / `CLAUDE.md` descriptions still match the code?** (layers, registry
  counts, metric list, visualization renderers)
- **Are there stale observations** in `archive/` pointing at things now changed or fixed?
- **Did organic growth leave noise?** When a rule or path changes, old references become
  stale — they're negative signal agents will follow into dead ends. Rewire or remove them.
- **Is there dead code or orphaned docs?** Both degrade the network's signal-to-noise ratio.

---

## 5. Anti-Patterns

| Anti-Pattern | Why It's Wrong | Instead |
|-------------|---------------|---------|
| Promoting everything interesting | Inflates committed docs, creates maintenance burden | Discard is the healthy default |
| Workspace as permanent storage | Defeats the ephemeral design | Discard, archive briefly, or promote — don't hoard |
| Forcing observations into existing categories | Creates false structure | Let patterns emerge naturally |
| Skipping the reflection moment | Loses boundary signals | 60 seconds at session end is enough |
| Promoting without recurrence | Single observations may be noise | Wait for 3+ instances |
| Referencing workspace files from committed docs | Creates broken references | Workspace is ephemeral; committed docs are self-contained |
| Documenting what the code already says | Redundant docs drift and mislead | Only promote what would be *lost* without a doc |

---

## 6. The Recursive Nature

This file is itself subject to the growth protocol. If agents hit situations it doesn't
cover — a new kind of workspace artifact, a new lifecycle stage — that's the boundary.
Record the observation; if it recurs, update this file. The system that describes how the
system grows must itself be able to grow.
