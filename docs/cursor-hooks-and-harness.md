# Cursor hooks and harness (best-effort)

**Scope:** General guidance for using **editor / IDE hooks** with Cursor-class agents and a **testing harness** sketch. Repo-specific wiring lives in project config; this doc stays **agnostic** so teams can map it to their CI.

Related process docs: [delegation chain](delegation-chain.md), [process and quality gates](process-and-quality-gates.md), [eval pipeline vision](eval-pipeline-vision.md).

## Hooks concept (Cursor)

**Hooks** are lifecycle callbacks around developer actions—for example file save, pre-commit, session start, or custom slash commands. For agent ecosystems they help with:

| Hook idea | Intent |
| --- | --- |
| Pre-run gate | Block destructive commands unless environment flag confirms dry-run or approval |
| Post-edit lint | Run formatter/linter after agent writes files; surface diff-sized signal |
| Policy bundle load | Ensure `rules/*.mdc` + `agents/*.md` snapshot used by the run matches git HEAD or a pinned revision |
| Secret scan | Fail fast on patterns matching API keys before commit |

Cursor may expose hooks through **workspace settings**, **tasks**, **extensions**, or future first-class hook APIs depending on product version. Treat the table above as **logical** integration points; implement with whatever mechanism your workspace supports (VS Code `tasks.json`, git hooks, CI job, etc.).

## Testing harness (sketch)

Goal: reproducible **golden-path** and **adversarial** runs without touching production.

1. **Fixture workspace** — copy or clone a **minimal repo snapshot** with synthetic secrets (invalid keys only).
2. **Driver** — script or benchmark runner invokes the agent stack with:
   - fixed **model tier** (see [model routing](model-routing.md)),
   - frozen **policy bundle** path,
   - recorded **user prompt** or transcript replay (see [replay fixtures vision](replay-fixtures-vision.md)).
3. **Assertions** — not only exit code:
   - files touched ⊆ `OWNERSHIP`,
   - completion contract present for builder branches ([evidence-first acceptance](evidence-first-acceptance.md)),
   - benchmarks from repo scripts if applicable (`scripts/run-full-repo-benchmark.sh` pattern).
4. **Teardown** — reset worktree or use ephemeral container so runs do not contaminate each other.

## Safety defaults

- Default harness to **read-only** remotes and **no** credential mounts.
- Log **hashed** prompts + redacted tool I/O; align with [agent telemetry contract](agent-telemetry-contract.md).
- For injection testing, load cases from [prompt injection probes](security/prompt-injection-probes.md) categories only inside the isolated harness.

## When hooks are insufficient

Hooks cannot replace **orchestrator-level** gates (parallel writer safety, rework limits, relay semantics). Use this document for **local ergonomics and CI**; use [DAG and branch dependencies](dag-branch-dependencies.md) for planning correctness.
