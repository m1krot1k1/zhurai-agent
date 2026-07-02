---
name: structured-agent-logging
description: Structured logs for multi-branch agent runs—JSONL records with branch_id, correlation IDs, and completion-contract friendly fields for audit and replay.
requires: [caid-worktrees, start-workflow]
---

## OVERVIEW

Plain prose “I did X” does not scale across parallel branches. Use **JSON Lines (JSONL)** so orchestrators can **grep, aggregate, and prove** delegation. Align field names with completion contracts in **`rules/orchestrator.mdc` §5** (Evidence schema) and phase-tree IDs in **§16**—this skill defines a minimal interchange shape; it does not replace those sections.

## КОГДА ИСПОЛЬЗОВАТЬ

- Multiple `Task` / Task branches in one session
- Need audit trail for CAID commits—pair with **`skills/caid-worktrees/SKILL.md`**
- Parent synthesis must merge child status + checks + evidence

## WORKFLOW

### Шаг 1: Choose correlation identifiers

1. **`branch_id`**: use **§16** format (`B0`, `B0-1`, …); never reuse IDs across concurrent writers.
2. **`correlation_id` / `parent_branch_id`**: tie child spawn to parent packet (UUID or deterministic hash of Task envelope—pick one scheme per repo and stay consistent).
3. **`run_id` / `session_id`**: optional top-level key for file rotation across waves.

### Шаг 2: JSONL record shape (minimal)

Emit **one JSON object per line** after material events (spawn, tool batch, completion). Recommended keys:

| Field | Purpose |
|-------|---------|
| `ts` | ISO-8601 timestamp |
| `level` | `info` / `warn` / `error` |
| `branch_id` | Phase-tree id |
| `agent` | Specialist name |
| `event` | `spawn` / `tool` / `complete` / `blocker` |
| `correlation_id` | End-to-end trace |
| `tool` | Tool name when `event=tool` |
| `status` | `done` / `rework` / `blocked` / `aborted` for completions |
| `files_changed` | string array |
| `checks` | array of `{name, result, evidence}` per §5 |
| `message` | Short human line; long blobs → external path |

Extend only when a parent **COMPLETION_CONTRACT** requires more; avoid duplicating full prompts in JSONL.

### Шаг 3: Privacy, size, and handoff

1. **No secrets** in logs; redact tokens—see **`skills/start-workflow/SKILL.md`**.
2. Truncate large tool outputs; store **path + SHA256** if evidence must be large—anti-hallucination norms in workspace rules.
3. On synthesis, parent aggregates child JSONL summaries into the YAML completion block expected by **§5**, not raw log dumps.

## CHECKLIST

- [ ] Every writer event includes `branch_id` + `correlation_id`
- [ ] Completions include `status`, `files_changed`, `checks` stub
- [ ] JSONL valid (one parseable object per line)
- [ ] Secrets and oversized payloads excluded or externalized

**Example: JSONL log stream for a multi-branch wave**

```jsonl
{"ts":"2026-06-09T10:15:00Z","level":"info","branch_id":"B0","agent":"orchestrator","event":"spawn","correlation_id":"c00-01","message":"spawning 3 writer branches"}
{"ts":"2026-06-09T10:15:02Z","level":"info","branch_id":"B0-1","agent":"code","event":"spawn","correlation_id":"c00-01","parent_branch_id":"B0","tool":null,"message":"starting rate-limit implementation"}
{"ts":"2026-06-09T10:15:02Z","level":"info","branch_id":"B0-2","agent":"code","event":"spawn","correlation_id":"c00-01","parent_branch_id":"B0","tool":null,"message":"starting auth-refresh implementation"}
{"ts":"2026-06-09T10:15:45Z","level":"info","branch_id":"B0-1","agent":"code","event":"tool","correlation_id":"c00-01","tool":"Write","message":"wrote src/middleware/rateLimit.ts"}
{"ts":"2026-06-09T10:16:10Z","level":"info","branch_id":"B0-1","agent":"code","event":"complete","correlation_id":"c00-01","status":"done","files_changed":["src/middleware/rateLimit.ts","tests/rateLimit.test.ts"],"checks":[{"name":"npm test","result":"pass","evidence":"exit 0, 5/5 tests"},{"name":"npm run lint","result":"pass","evidence":"exit 0, 0 warnings"}]}
{"ts":"2026-06-09T10:16:30Z","level":"warn","branch_id":"B0-2","agent":"code","event":"blocker","correlation_id":"c00-01","message":"Redis connection refused in CI","status":"blocked"}
```
