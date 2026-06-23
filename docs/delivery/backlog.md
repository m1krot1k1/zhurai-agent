# Product Backlog Index (PBI Tracking)

> **Source**: Per `rules/aleksander.mdc:99` — primary source of truth for PBI tracking  
> **Workflow**: Follows `docs/pbi-task-workflow.md` structure  
> **Evidence-first**: Uses `docs/evidence-first-acceptance.md` acceptance format  
> **Last updated**: 2026-03-31  
> **Version**: v1.0  
> **Branch ID**: B0-1 (initial creation)

---

## PBI Index Table

| PBI-ID | Title | Status | Last Updated | Linked Tasks |
|--------|-------|--------|--------------|--------------|
| PBI-002 | `/start` operator sync | Agreed | 2026-03-31 | [PRD](PBI-002/prd.md) |
| PBI-006 | Evidence-first acceptance | Agreed | 2026-03-31 | [PRD](PBI-006/prd.md) |
| PBI-xxx | [New Item] | Proposed | - | - |

> **Legend**:  
> - **Agreed**: Approved, ready for implementation  
> - **Proposed**: Suggested, not yet approved  
> - **InProgress**: Actively being worked on  
> - **Review**: Complete, awaiting review  
> - **Done**: Completed and accepted  
> - **Rejected**: Requires rework or deprioritization  
> - **Blocked**: External dependency blocking

---

## PBI Details Summary

### PBI-002: `/start` operator sync

- **Status**: Agreed
- **Description**: Align `/start` chain terminology and relay semantics with `docs/start-workflow.md` and `docs/delegation-chain.md`
- **Evidence-first reference**: Requires claim-to-evidence matrix with traceable refs
- **Supporting docs**: 
  - `docs/start-workflow.md` (primary runbook)
  - `docs/delegation-chain.md` (detailed relay chain)
  - `agents/start.md` (canonical agent definition)

### PBI-006: Evidence-first acceptance

- **Status**: Agreed
- **Description**: Implement evidence-first acceptance format with `docs/evidence-first-acceptance.md` (claim-to-evidence matrix + reviewer checklist) and `docs/process-and-quality-gates.md` ("Final Verification Checklist")
- **Evidence schema**: Completion contract with `branch_id`, `files_changed`, `checks`, `acceptance_criteria`, `confidence`, `unknowns`, `risks`
- **Applicable to**: reviewer branches (`code-reviewer`, `security-auditor`, `review`)

---

## Backlog Item Template

Use this template for new PBI proposals:

```markdown
### PBI-XXX: [Title]

- **Status**: Proposed
- **Description**: [Clear one-sentence summary]
- **User Story**: As a [role], I want [goal] so that [benefit]
- **Priority**: [High/Medium/Low]
- **Dependencies**: [List of blocking items]
- **Target Date**: [Optional]
- **Linked Tasks**: [tasks.md links when InProgress]
```

---

## Task Status Definitions

| Status | Meaning |
|--------|---------|
| **Proposed** | Newly defined, awaiting user approval |
| **Agreed** | User approved, ready for implementation |
| **InProgress** | AI Agent actively working |
| **Review** | Awaiting user validation |
| **Done** | User approved implementation |
| **Blocked** | External dependency blocking progress |

---

## Evidence-First Acceptance Reference

All "done" claims must include verifiable proof using the **Claim-to-Evidence Matrix**:

```yaml
claim_to_evidence_matrix:
  - claim: "<what is asserted>"
    acceptance_criterion: "<AC id or exact AC text>"
    evidence_type: file|diff|command_output|test_result|review_note
    evidence_ref: "<path or command + short output anchor>"
    status: met|partial|not_met|blocked
```

See `docs/evidence-first-acceptance.md` for complete template and examples.

---

## Quality Gates Reference

Before marking PBI as "Done", verify:

- [ ] All Acceptance Criteria covered explicitly, without "implied"
- [ ] List of changed paths provided
- [ ] Checks were actually run (or explicitly noted why not run)
- [ ] Residual risks/limitations documented
- [ ] Completion contract filled in standardized format

See `docs/process-and-quality-gates.md` for "Final Verification Checklist".

---

## Cross-References

### Related Documentation

| Document | Purpose |
|----------|---------|
| `docs/pbi-task-workflow.md` | Full PBI & Task workflow reference |
| `docs/evidence-first-acceptance.md` | Evidence-first acceptance template |
| `docs/process-and-quality-gates.md` | Process and quality gates documentation |
| `docs/start-workflow.md` | `/start` operator runbook |
| `docs/delegation-chain.md` | Delegation chain detailed reference |

### Rule References

| Rule | Section | Description |
|------|---------|-------------|
| `aleksander.mdc` | 3–5 | PBI management and task workflow |
| `orchestrator.mdc` | 3, 5, 8 | Delegation completeness and quality gates |
| `specialists.mdc` | - | Specialist routing and delegation rules |

---

## Creation Metadata

- **Created**: 2026-03-31
- **Created by**: docs-specialist (Branch B0-1)
- **Generated via**: `Task(docs-specialist, "Create missing backlog.md")`
- **Validation**: Cross-references verified ✅

---

*This document serves as the primary backlog interface. Individual PBI PRDs are stored in `docs/delivery/<PBI-ID>/prd.md`.*
