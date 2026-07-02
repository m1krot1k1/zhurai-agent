# Evidence-first acceptance (ZCode)

Use this template when reporting task completion so every "done" claim has verifiable proof. Required for orchestrator synthesis and specialist branch close-out.

## Claim-to-evidence matrix

Copy into the completion contract or wave report:

```yaml
claim_to_evidence_matrix:
  - claim: "<what is asserted>"
    acceptance_criterion: "<AC id or exact AC text>"
    evidence_type: file|diff|command_output|test_result|review_note
    evidence_ref: "<path or command + short output anchor>"
    status: met|partial|not_met|blocked
```

## Reviewer acceptance checklist

Reject output if any check fails.

- [ ] Every material claim appears in the matrix.
- [ ] Each claim links to concrete evidence (`evidence_ref` is specific and inspectable).
- [ ] `acceptance_criterion` is mapped for each claim (no unmapped "done" statements).
- [ ] `status` is explicit and consistent with evidence.
- [ ] Command/test claims include reproducible command or output anchor.
- [ ] Residual risks listed when status is not `met`.

## Evidence quality examples

### Scenario A: Code change

**Insufficient:**

```yaml
- claim: "Feature works"
  acceptance_criterion: "AC-1"
  evidence_type: test_result
  evidence_ref: "tests passed"
  status: met
```

**Sufficient:**

```yaml
- claim: "User can submit form without validation error for valid input"
  acceptance_criterion: "AC-1: valid form submission succeeds"
  evidence_type: command_output
  evidence_ref: "npm test -- form-submit.spec.ts -> PASS (3 tests); src/features/form/submit.ts updated"
  status: met
```

### Scenario B: Plugin / rules change

**Insufficient:**

```yaml
- claim: "Policy updated and consistent"
  acceptance_criterion: "AC-2"
  evidence_type: review_note
  evidence_ref: "checked manually"
  status: met
```

**Sufficient:**

```yaml
- claim: "Orchestration references present and cross-linked"
  acceptance_criterion: "AC-2: README index lists all orchestration files"
  evidence_type: file
  evidence_ref: "skills/multi-agent-ecosystem/references/orchestration/README.md links delegation-chain.md, routing-table.md, completion-contracts.md"
  status: met
```

## Minimal completion block

Companion to the matrix — full schema in [completion-contracts.md](./completion-contracts.md):

```yaml
completion_contract:
  summary: "<what was completed>"
  files_changed:
    - "<path>"
  checks_run:
    - name: "<check name>"
      result: pass|fail|not_run
      evidence: "<short proof>"
  acceptance_criteria:
    - criterion: "<AC text>"
      status: met|not_met
  claim_to_evidence_matrix:
    - claim: "<text>"
      acceptance_criterion: "<AC>"
      evidence_type: file|diff|command_output|test_result|review_note
      evidence_ref: "<path or command>"
      status: met|partial|not_met|blocked
  residual_risks:
    - none|"<risk>"
  confidence: high|medium|low
```

## Integration with ZCode waves

| Role | Responsibility |
|------|----------------|
| Specialist | Fill matrix for branch AC before returning to orchestrator |
| Orchestrator | Aggregate branch matrices; reject thin "done" without `evidence_ref` |
| Start router | Surface wave-level summary in footer with AC status |

## Anti-patterns (reject)

- "Verified" / "checked" without path or command
- Long narrative report + zero file paths
- `status: met` with `evidence_type: review_note` and no reviewer branch id
- Claiming tests ran without command output when tests were required

## See also

- [completion-contracts.md](./completion-contracts.md) — full YAML schema
- [start-workflow.md](./start-workflow.md) — footer and operator checklist
- `references/rules/aleksander.mdc` — anti-hallucination rules
