# Agent Workspace

> The scratchpad for AI agents working on QForge. Where observations accumulate, plans get
> drafted, and patterns emerge before they're committed to the docs.

**Structure is tracked. Content is gitignored.** The directory skeleton (this `README.md`,
`AGENTS.md`, and `.gitkeep` files) is committed so it survives clones. Everything agents
write into the subfolders is ephemeral and ignored by git.

See [`AGENTS.md`](AGENTS.md) for the philosophy (why this exists, how knowledge is promoted).

---

## Directory Structure

```
.agent-workspace/
├── README.md              # This file — structure + lifecycle
├── AGENTS.md              # Philosophy — self-reflection + growth framework
│
├── active/                # Currently being worked on (this session)
│   ├── observations/      # What I'm seeing right now (physics, metrics, behavior)
│   ├── plans/             # Implementation plans in progress
│   └── drafts/            # Docs being drafted before promotion
│
├── todo/                  # Identified but not yet started (flagged work, future ideas)
│
├── archive/               # Done but retained for reference
│   ├── observations/      # Past observations (promoted or superseded)
│   └── audits/            # Past analysis reports
│
└── completed/             # Promoted — kept briefly as proof, then deleted
```

---

## Lifecycle

```
                 ┌──────────┐
          new ──▶│  active/  │──── work done ────┐
                 └──────────┘                    │
                      │                          ├──── discard (default) ──▶ 🗑️ delete
                      │ not now                  │
                      ▼                          ├──── archive (sometimes) ──▶ archive/
                 ┌──────────┐                    │
                 │  todo/    │                   └──── promote (rare) ──▶ completed/ ──▶ committed docs
                 └──────────┘
                      │
                      │ started
                      └──────▶ active/
```

### Rules

1. **Start in `active/`.** Name files `YYYY-MM-DD-description.md`.
2. **If not now, move to `todo/`.** Include enough context to pick up later.
3. **When done, decide: discard, archive, or promote.**
   - **Discard** (default) → delete it. Most artifacts are intermediary; the fix is in the
     code, the decision is in the commit.
   - **Archive** → move to `archive/` only if it has reference value AND isn't derivable
     from the code or existing docs.
   - **Promote** (rare) → create the committed doc (relevant `AGENTS.md`, `docs/architecture/`,
     `docs/research/`, …), then delete the workspace file.
4. **The bar for promotion is high.** If the knowledge is derivable from `git log`, the
   code, or an existing doc — don't create a new doc.
5. **Never reference workspace files from committed docs.** Content here is ephemeral.

---

## Triage Quick Reference

| Artifact | Default | Promote only if… |
|----------|---------|------------------|
| Debugging / investigation notes | discard | — (the fix is in the code) |
| Plans for completed work | discard | — (the code is the plan) |
| One-off observations | discard | it recurs 3+ times → it's architecture |
| Comparison tables for a made decision | discard | the decision itself is worth a doc |
| Research finding | archive | it's a durable result → `docs/research/` |
| Recurring architectural pattern | — | it's undocumented architecture → `AGENTS.md` / `docs/architecture/` |

**The test before promoting:** would a future agent with `git log` and the code still need
this? If yes, promote and wire it into the doc network (see `AGENTS.md` §3). If they could
work it out from the code — discard.

---

## Naming Convention

```
YYYY-MM-DD-description.md            # date-prefixed for sorting
observation-{topic}-YYYY-MM-DD.md    # specific observations
plan-{feature}.md                    # implementation plans
audit-{topic}-YYYY-MM-DD.md          # analysis reports
draft-{doc-name}.md                  # drafts headed for docs/
```
