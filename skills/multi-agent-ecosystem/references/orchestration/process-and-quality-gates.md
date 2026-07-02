# Process and quality gates (ZCode)

Routing, verification, and completion rules for waves in the **multi-agent-ecosystem** plugin.

## Routing summary

- **`/start`** → orchestrator pattern only; specialists come from orchestrator. User-facing wave summary via start router after orchestrator returns.
- **Direct `/code`, `/debug`, …** → named specialist without `/start`.
- **Imperative request (DUA)** → execute without blocking on PBI/task files in the user repo.
- **Explanation only** → `ask` or single read-only specialist branch.
- **Multi-artifact / multi-domain** → orchestrator with explicit branches and `OWNERSHIP`.

Full table: [routing-table.md](./routing-table.md).

## Minimal verification

| Change type | Expected check |
|-------------|----------------|
| Code | Compile / test when possible; else state `not_run` + reason |
| UI | Smoke test in browser when tools exist; else document skip |
| Branch close | [Completion contract](./completion-contracts.md) with evidence |
| Agent briefs (`references/agents/*.md`) | Registry / link validation when scripts exist |

## Final verification checklist

Before marking a wave or branch `done`:

- [ ] All acceptance criteria covered explicitly — no "implied" passes.
- [ ] Changed paths listed in `files_changed`.
- [ ] Checks actually ran, or `not_run` with reason.
- [ ] Residual risks documented.
- [ ] Single completion contract format per [completion-contracts.md](./completion-contracts.md).
- [ ] [Claim-to-evidence matrix](./evidence-first-acceptance.md) filled for material claims.

## Large tasks

Use **repo-task-proof-loop** pattern when the project adopts it:

- Artifacts under `agent-tasks/<TASK_ID>/` or project-local `.plan/`
- Minimum: `spec.md`, independent `verdict.md`

## Autonomy and user response

- Default: act with reasonable assumptions; ask only on blocking risk or missing secrets.
- Mandatory footer per [start-workflow.md](./start-workflow.md):
  - **Краткая сводка**
  - **Векторы улучшения**

## Orchestrator-specific gates

| Gate | Rule |
|------|------|
| Writer fan-out (L1) | ≤6 parallel writer branches per orchestrator wave |
| Specialist writer fan-out | 3+ parallel writers → escalate to orchestrator |
| Reader fan-out | Unlimited (code-reviewer, security-auditor, ask, repo-explorer, …) |
| Core policy changes | `references/rules/` changes → code-reviewer + security-auditor branches |
| Evidence | No `done` without matrix + checks |

## See also

- [start-workflow.md](./start-workflow.md) — operator checklist
- [evidence-first-acceptance.md](./evidence-first-acceptance.md) — reviewer rejection rules
- `references/rules/orchestrator.mdc` — full policy
