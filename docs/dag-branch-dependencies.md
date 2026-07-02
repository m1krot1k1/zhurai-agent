# DAG for branch dependencies

This document explains how **branch identifiers** (`B0-n`), **`DEPENDENCIES`** between tasks, and **rework limits** form a **directed acyclic graph (DAG)** in practice—plus when cycles or stalls must stop work.

Orchestration handoffs are operationalized in [delegation chain](delegation-chain.md). Evidence for each branch should follow [evidence-first acceptance](evidence-first-acceptance.md); checklist-style gates are in [process and quality gates](process-and-quality-gates.md).

## Branch IDs

| Pattern | Role |
| --- | --- |
| `B0` | Root wave / supervisor scope |
| `B0-1`, `B0-2`, … | Child branches under `B0` |
| `B0-1-1`, … | Deeper levels when sub-orchestrators split work |

**Rule:** IDs are **stable labels** in prompts and completion contracts; they are not git branches unless a separate CAID / worktree policy says so.

## `DEPENDENCIES` field

Task packets SHOULD declare:

- `DEPENDENCIES: none` — runnable immediately in parallel with other `none` peers (subject to OWNERSHIP disjointness).
- `DEPENDENCIES: after:B0-1` — **must not start** until branch `B0-1` reports `status: done` (or policy-defined partial acceptable state).
- `DEPENDENCIES: blocked-by:B0-3` — **hard wait** on resolution of `B0-3`; treat as blocked edge in the DAG until unblocked.

**DAG interpretation:** edges run **`dependency → dependent`**. A valid wave schedule is a **topological order** of branches after expanding `after:` and removing completed nodes.

### Invalid patterns

- **Cycles** (`after:A` on B and `after:B` on A) — orchestrator MUST replan or escalate.
- **Missing branch** — reference to unknown id → treat as `blocked` until corrected.

## Parallel writers

Parallel **builder** branches require **disjoint `OWNERSHIP`** (no overlapping writable globs). Reader branches (review, security audit) may overlap read scope but should not violate writer exclusivity. See routing guidance in [model routing](model-routing.md).

## Rework limits

Each branch carries a **`rework_cycles`** counter (or equivalent).

| Policy knob | Typical meaning |
| --- | --- |
| `rework_limit` | Maximum replan/fix loops for **this** branch before forced escalation |
| Breach | Return `status: blocked`, `escalate_reason: rework_limit_exceeded`, **do not** silently continue |

**Interaction with DAG:** a rework on branch `B0-2` **does not** automatically invalidate completed `B0-1` unless the completion contract explicitly invalidates downstream assumptions. Prefer **targeted rework branches** with narrow OWNERSHIP.

## Completion contract hook

Downstream tasks SHOULD NOT trust parent “done” without a contract.

Minimum alignment with [evidence-first acceptance](evidence-first-acceptance.md):

```yaml
branch_id: B0-2
status: done|rework|blocked|aborted
dependencies_satisfied:
  - after: B0-1
    observed_status: done
rework_cycles: 0
rework_limit: 3
```

## Fan-out vs depth

Flat fan-out with **too many** L1 children increases coordination cost. Structural rules in orchestrator policy suggest **sub-orchestrators** when L1 exceeds a small budget (see [skills index](skills-index.md) → orchestrator skill). Depth and budget interact: prefer **batch parallel** sibling readers over deep sequential chains when AC allows.
