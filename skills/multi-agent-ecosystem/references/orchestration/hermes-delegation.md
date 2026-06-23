# Hermes delegation (`delegate_task`)

Runtime mapping for **zhur.ai-agent** (Desktop / TUI / gateway). Cursor `Task()` is **not** available here.

## Tool

| Pattern | Hermes |
|---------|--------|
| `Task(orchestrator, …)` | `delegate_task(role="orchestrator", goal=…, context=…)` **or** slash `/orchestrator` |
| `Task(code, …)` | `delegate_task(role="leaf", goal=…, context=…)` with `AGENT_BRIEF_PATH: agents/code.md` |
| Parallel branches | `delegate_task(tasks=[{goal, context}, …])` |
| Specialist with 2+ subtasks | Child uses `role="orchestrator"` or batches `tasks=[…]` |

Paths resolve via `ZHUR_AI_AGENT_ROOT` or install root (`agent/ecosystem_paths.py`).

## Start router (`/start`)

1. Capture **ORIGINAL_REQUEST** verbatim.
2. **No** Read/Write/Shell before handoff.
3. First delegation:

```text
delegate_task(
  role="orchestrator",
  goal="Decompose and execute ORIGINAL_REQUEST",
  context="ORIGINAL_REQUEST: <verbatim user text>
Load agents/orchestrator.md
Load skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md"
)
```

Or invoke **`/orchestrator`** with the same text.

## Orchestrator branch template

For each specialist branch:

```text
delegate_task(
  role="leaf",
  goal="<branch OBJECTIVE>",
  context="OBJECTIVE: ...
ORIGINAL_REQUEST: <verbatim>
OWNERSHIP: <exclusive globs>
AGENT_BRIEF_PATH: agents/<specialist>.md
NON-NEGOTIABLE: Read AGENT_BRIEF_PATH and follow that role."
)
```

Parallel writers (independent OWNERSHIP):

```text
delegate_task(tasks=[
  {goal: "...", context: "... AGENT_BRIEF_PATH: agents/code.md ..."},
  {goal: "...", context: "... AGENT_BRIEF_PATH: agents/test-specialist.md ..."},
])
```

## Limits

Default `delegation.max_concurrent_children` may be **3**. For orchestrator waves with 4–6 writers, raise in config or split into sequential batches.

## Blocked

If `delegate_task` is unavailable → return `DELEGATION_BLOCKED`. **Do not** fall back to inline multi-branch work on `/start` tasks.

## Helper (Python)

`agent.ecosystem_delegate.build_delegate_branch_context(agent_id, objective=…)` builds the `context` string with `AGENT_BRIEF_PATH`.
