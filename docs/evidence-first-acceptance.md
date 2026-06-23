# Evidence-First Acceptance Template

Use this template when reporting task completion so each "done" claim has verifiable proof.

## Claim-to-Evidence Matrix (Copy/Paste)

```yaml
claim_to_evidence_matrix:
  - claim: "<what is asserted>"
    acceptance_criterion: "<AC id or exact AC text>"
    evidence_type: file|diff|command_output|test_result|review_note
    evidence_ref: "<path or command + short output anchor>"
    status: met|partial|not_met|blocked
```

## Reviewer Acceptance Checklist

Reject the output if any required check fails.

- [ ] Every material claim is present in the matrix.
- [ ] Each claim links to concrete evidence (`evidence_ref` is specific and inspectable).
- [ ] `acceptance_criterion` is mapped for each claim (no unmapped "done" statements).
- [ ] `status` is explicit (`met|partial|not_met|blocked`) and consistent with evidence.
- [ ] For command/test claims, output is included or summarized with a reproducible command.
- [ ] Residual risks or blockers are listed when status is not `met`.

## Evidence Quality Examples

### Scenario A: Code change verification

Insufficient evidence:

```yaml
- claim: "Feature works"
  acceptance_criterion: "AC-1"
  evidence_type: test_result
  evidence_ref: "tests passed"
  status: met
```

Why insufficient:

- `evidence_ref` is not verifiable (no command, no file, no output anchor).
- Claim is vague and cannot be audited.

Sufficient evidence:

```yaml
- claim: "User can submit form without validation error for valid input"
  acceptance_criterion: "AC-1: valid form submission succeeds"
  evidence_type: command_output
  evidence_ref: "npm test -- form-submit.spec.ts -> PASS (3 tests), plus src/features/form/submit.ts updated"
  status: met
```

### Scenario B: Rule/doc governance change verification

Insufficient evidence:

```yaml
- claim: "Policy updated and consistent"
  acceptance_criterion: "AC-2"
  evidence_type: review_note
  evidence_ref: "checked manually"
  status: met
```

Why insufficient:

- No changed paths, no check command, no explicit consistency signal.

Sufficient evidence:

```yaml
- claim: "Policy wording updated without introducing rule conflicts"
  acceptance_criterion: "AC-2: no contradictions in updated policy set"
  evidence_type: command_output
  evidence_ref: "rules/orchestrator.mdc edited; scripts/validate-repo-consistency.ps1 -> PASS"
  status: met
```

## Minimal Completion Block (Optional Companion)

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
  residual_risks:
    - none|"<risk>"
  confidence: high|medium|low
```
