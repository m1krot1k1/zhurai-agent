# Delegation chain: `/start` to specialists

> **Hermes (Desktop/TUI/gateway):** use `delegate_task` — see [hermes-delegation.md](./hermes-delegation.md). Cursor `Task()` is not available in this runtime.

## What happens when the user runs `/start`

1. **ZCode** runs the **`/start`** command (`commands/start.md`), which activates the **multi-agent-ecosystem** skill in **start router** mode.
2. The start router acts as **supervisor**: it does **not** read the repo, run shell, or edit files before handoff. It passes `ORIGINAL_REQUEST` (verbatim user text) to the **orchestrator** pattern.
3. The **orchestrator** decomposes work into branches and delegates to specialists by loading `references/agents/<name>.md` and spawning **ZCode sub-sessions** (or running sequentially when parallel spawn is unavailable).
4. **Specialists** execute branch work. When a specialist has 2+ independent subtasks, it **must** delegate (Mandatory SWARM) — same rules as orchestrator, scoped to the branch.

> **Flat chain only.** There is no intermediate worker-start hop. Root `/start` hands off directly to orchestrator semantics.

**FIRST_ACTION gate (start router):** the first substantive action is orchestrator handoff — not repo exploration. Reading files or running tools before that is a policy violation unless the user invoked a direct specialist command instead of `/start`.

If the runtime cannot spawn sub-sessions or parallel agents, record `MULTI_AGENT_PIPELINE_BLOCKED` and escalate. Phrases like "no sub-agent — doing it inline" on a multi-branch `/start` task are a **critical failure** unless the user explicitly requested single-agent mode.

## Canonical chain

```text
user
  -> /start  (commands/start.md, start router mode)
  -> orchestrator pattern  (commands/orchestrator.md)
     -> branch: load references/agents/code.md + sub-session
     -> branch: load references/agents/test-specialist.md + sub-session
     -> branch: load references/agents/security-auditor.md + sub-session
  -> orchestrator synthesizes completion contracts
  -> start router returns wave result to user
```

### ZCode handoff equivalents

| Cursor-era pattern | ZCode pattern |
|--------------------|---------------|
| `Task(subagent_type="orchestrator", …)` | `/orchestrator` or orchestrator mode with full branch envelope |
| `Task(subagent_type="code", …)` | Load `references/agents/code.md` + spawn sub-session with branch prompt |
| `Task(subagent_type="orchestrator", …)` (nested) | Sub-orchestrator wave with narrower `OWNERSHIP` |

Each branch prompt must include the full envelope: `OBJECTIVE`, `SCOPE`, `OUT_OF_SCOPE`, `OWNERSHIP`, `DEPENDENCIES`, `ACCEPTANCE_CRITERIA`, `NON-NEGOTIABLE`, `COMPLETION_CONTRACT`. See [completion-contracts.md](./completion-contracts.md).

## Forbidden chains

```text
# Worker-start (removed — extra hop)
/start -> secondary start worker -> orchestrator

# Fake delegation
/start -> Read/Write/Shell locally -> "acknowledge" only

# Single-agent fallback on multi-branch /start
/start -> "cannot spawn sub-sessions" -> do all work inline without escalation
```

## Swarm / continuous mode (`until_user_stop`)

When the user requests 24/7, swarm, or "until I say stop", the start router runs **one orchestrator wave per iteration**:

```text
Wave 1: orchestrator(WAVE_NUMBER: 1) -> result
Wave 2: orchestrator(WAVE_NUMBER: 2) -> result   <- required
Wave 3: orchestrator(WAVE_NUMBER: 3) -> result   <- required
```

**Stop when:** user says stop | acceptance criteria met | `no_progress_limit` waves without progress.

**Do not stop when:** a single wave completes but AC are open | pause with `resume_packet` | micro-packet closed in open-ended improvement.

`resume_packet` is the payload emitted when a wave pauses. The next orchestrator wave receives it as `CONTINUATION_PACKET` — same data, output vs input view.

## Slash commands vs internal delegation

| User types | Orchestrator action |
|------------|---------------------|
| `/code …` | Branch with `references/agents/code.md` |
| `/test-specialist …` | Branch with `references/agents/test-specialist.md` |
| `/orchestrator …` | Orchestrator mode directly (skip start router if already in orchestrator context) |

Direct specialist commands bypass start router when the user explicitly chose a single domain.

## Allowed / forbidden

| Scenario | Status | Notes |
|----------|--------|-------|
| `/start` → orchestrator pattern | **Allowed** | Canonical path |
| `/start` → direct specialist without orchestrator | **Forbidden** | Unless user used `/code`, `/debug`, etc. directly |
| orchestrator → specialist branches | **Allowed** | Core model |
| specialist → sub-branches for subtasks | **Allowed** | Mandatory SWARM when 2+ independent subtasks |
| same-type child with narrower scope | **Allowed** | Fingerprint must differ; depth ≤ 3 |
| same-type child with same fingerprint | **Forbidden** | Loop |
| 3+ parallel **writer** children under one specialist | **Escalate** | Return coordination to orchestrator |

## Specialist decision order

For any specialist (`code`, `test-specialist`, `frontend-specialist`, `docs-specialist`, …):

1. **MUST delegate** — 2+ independent subtasks
2. **MAY execute directly** — one tiny indivisible task (one file, one action)
3. **MUST escalate** — 3+ parallel writer children locally

| Situation | Action |
|-----------|--------|
| 2+ independent subtasks | Spawn sub-sessions (or sequential branches with full envelopes) |
| 1 small indivisible task | May execute in current session |
| Same-type child | Allowed only with **strictly narrower** scope |
| Cross-domain need | Load the matching `references/agents/<name>.md` |
| 3+ writer children | Escalate to orchestrator |
| Reader branches (review, security audit, ask, repo-explorer) | No writer fan-out limit |

## Same-type delegation

1. Child scope must be **strictly narrower** than parent.
2. Branch fingerprint differs (goal / target-files / AC).
3. Same-type chain depth ≤ 3.

## See also

- [start-workflow.md](./start-workflow.md) — operator checklist and runtime states
- [routing-table.md](./routing-table.md) — which agent brief to load
- `commands/start.md`, `commands/orchestrator.md`
- `references/rules/orchestrator.mdc`
