# Completion contracts (ZCode)

YAML schema for branch close-out and orchestrator wave synthesis. Every specialist branch and orchestrator wave **must** return a structured completion contract with evidence.

## Branch completion schema

```yaml
branch_id: <id>                    # e.g. B0-7
parent_id: <id|null>               # e.g. B0
level: <int>                       # delegation depth
owner: <agent-name>                # e.g. docs-specialist

# Runtime status (canonical pair)
approval_state: not_required|requested|approved|rejected
execution_state: in_progress|paused|blocked|done|rework|aborted

# Legacy wire alias (optional, must align with pair above)
status: approval|pause|blocked|resume

# Work summary
summary: "<one paragraph: what was completed>"
files_changed:
  - "<path>"

checks:
  - name: "<command or check label>"
    result: pass|fail|not_run
    evidence: "<short output anchor or reason not run>"

acceptance_criteria:
  - criterion: "<exact AC text>"
    status: met|not_met|partial|blocked

claim_to_evidence_matrix:
  - claim: "<assertion>"
    acceptance_criterion: "<AC id or text>"
    evidence_type: file|diff|command_output|test_result|review_note
    evidence_ref: "<path or command + anchor>"
    status: met|partial|not_met|blocked

residual_risks:
  - none|"<risk description>"

unknowns:
  - none|"<open question>"

confidence: high|medium|low
```

## Delegation envelope (input — required before branch start)

Orchestrator must attach this to every sub-session prompt:

```yaml
envelope:
  objective: "<one measurable sentence>"
  scope: "<paths, components>"
  out_of_scope: "<explicit exclusions>"
  ownership: "<exclusive globs — disjoint across parallel writers>"
  dependencies: none|after:<branch-id>|blocked-by:<branch-id>
  acceptance_criteria:
    - "<observable check>"
  non_negotiable:
    - "You will be PENALIZED for skipping steps"
    - "NEVER say done without listing changes + evidence"
  critical_unknowns: none|["<question>"]
```

Keyword gate: `NON-NEGOTIABLE` must contain **`PENALIZED`** literally.

## Orchestrator wave synthesis

After all branches return, orchestrator emits:

```yaml
wave_id: <id>
wave_number: <int>
branches_completed:
  - branch_id: <id>
    owner: <agent>
    execution_state: done|rework|blocked
    files_changed: [<paths>]
branches_deferred:
  - branch_id: <id>
    reason: "<why>"
open_risks:
  - "<aggregated from branches>"
delivery_ledger:
  - requested_item: "<AC or deliverable>"
    status: done|blocked|not_done
    evidence_ref: "<path or check>"
next_action: complete|continue_wave|pause|escalate
resume_packet: null|<continuation payload for next wave>
```

## State transition rules

| From | To | Allowed when |
|------|-----|--------------|
| `in_progress` | `paused` | Awaiting approval, input, or dependency |
| `paused` | `in_progress` | `approval_granted`, `input_received`, `dependency_resolved` |
| `in_progress` | `blocked` | Hard blocker; escalate with `blocker_reason` |
| `in_progress` | `done` | All AC met with evidence |
| `blocked` | `in_progress` | **Forbidden** without new branch / replan |
| `blocked` | `done` | **Forbidden** without new branch / replan |

## Pre-flight checklist (orchestrator before spawn)

- [ ] `OBJECTIVE`: one sentence, measurable
- [ ] `SCOPE` / `OUT_OF_SCOPE`: explicit boundaries
- [ ] `OWNERSHIP`: exclusive; no overlap with sibling writers
- [ ] `DEPENDENCIES`: listed or `none`
- [ ] `ACCEPTANCE_CRITERIA`: observable checks only
- [ ] `NON-NEGOTIABLE`: contains `PENALIZED`
- [ ] Agent brief path exists: `references/agents/<name>.md`

## Post-flight checklist (orchestrator on receive)

- [ ] `files_changed` lists real paths
- [ ] Each AC has `status` + evidence in matrix
- [ ] `checks` run or `not_run` with reason
- [ ] No "done" without `evidence_ref`
- [ ] `confidence` matches evidence strength
- [ ] Writer overlap: none across parallel branches

## Blocker taxonomy (wave level)

Use when `execution_state=blocked`:

| Code | Meaning |
|------|---------|
| `BLOCKED_RUNTIME` | Sub-session spawn unavailable, tool failure |
| `BLOCKED_POLICY` | Chain violation, missing envelope |
| `BLOCKED_INPUT` | Missing secrets, ambiguous AC |
| `BLOCKED_EXTERNAL` | External API / network dependency |
| `BLOCKED_INTEGRATION` | Cross-branch conflict, OWNERSHIP clash |

## Lazy-agent rejection signals

Reject and send `rework` if:

- Zero files changed but claims implementation
- Empty `claim_to_evidence_matrix` on material work
- "Completed" with no `checks` and no `not_run` justification
- Report length >> actual diff

## Minimal example (specialist branch)

```yaml
branch_id: B0-7
parent_id: B0
level: 1
owner: docs-specialist
approval_state: not_required
execution_state: done
summary: "Created seven orchestration reference docs under references/orchestration/"
files_changed:
  - skills/multi-agent-ecosystem/references/orchestration/README.md
  - skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md
checks:
  - name: "ls references/orchestration"
    result: pass
    evidence: "7 .md files present"
acceptance_criteria:
  - criterion: "delegation-chain.md present and ZCode-adapted"
    status: met
  - criterion: "README.md index"
    status: met
claim_to_evidence_matrix:
  - claim: "Orchestration index links all reference files"
    acceptance_criterion: "README.md index"
    evidence_type: file
    evidence_ref: "references/orchestration/README.md"
    status: met
residual_risks:
  - none
unknowns:
  - none
confidence: high
```

## See also

- [evidence-first-acceptance.md](./evidence-first-acceptance.md) — matrix examples
- [delegation-chain.md](./delegation-chain.md) — when contracts are required
- `references/rules/orchestrator.mdc` — full orchestration policy
