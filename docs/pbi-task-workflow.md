# PBI & Task Workflow Reference

> Extracted from `rules/aleksander.mdc` sections 3–5 to reduce token overhead in the always-loaded rule file.
> This document is the canonical source for PBI/task management workflow details.
> Paths like `docs/delivery/*`, `docs/technical/`, and `test/*` are **host-project conventions** for the application using this config. They are not expected to exist inside this configuration repository unless a host project adds them.

## Runtime state canon (applies to all branch contracts)

Workflow labels in this document (`Proposed`, `InReview`, etc.) are domain lifecycle labels, not runtime wire-status.

Every runtime handoff, completion contract, and telemetry payload must use the canonical pair:
- `approval_state`: `not_required|requested|approved|rejected`
- `execution_state`: `in_progress|paused|blocked|done|rework|aborted`

Backward compatibility policy:
- Allowed: keep legacy workflow labels in backlog/task tables for product process clarity.
- Required: provide explicit mapping from each workflow label to canonical runtime fields.
- Not allowed: emit workflow labels as runtime `status` in branch envelopes/contracts.

---

# 3. Product Backlog Item (PBI) Management

## 3.1 Overview
Rules for PBIs — clarity, consistency, effective management.

## 3.2 Backlog Document Rules
- **Location**: `docs/delivery/backlog.md`
- **Table**: `| ID | Actor | User Story | Status | Conditions of Satisfaction (CoS) |`
- PBIs ordered by priority (highest first).

## 3.3 PBI Workflow

### Status Definitions (workflow + canonical mapping)
| Workflow Status | Meaning | approval_state | execution_state |
|--------|---------|----------------|-----------------|
| Proposed | Suggested, not yet approved | not_required | paused |
| Agreed | Approved, ready for implementation | approved | paused |
| InProgress | Actively being worked on | approved | in_progress |
| InReview | Complete, awaiting review | requested | paused |
| Done | Completed and accepted | approved | done |
| Rejected | Requires rework or deprioritization | rejected | rework |

### Event Transitions
- **create_pbi → Proposed**: define user story + AC, unique ID
- **propose_for_backlog: Proposed → Agreed**: verify PRD alignment, log
- **start_implementation: Agreed → InProgress**: verify no other InProgress for same component, create tasks
- **submit_for_review: InProgress → InReview**: verify all tasks complete, all AC met
- **approve: InReview → Done**: verify AC, tests pass, archive, notify
- **reject: InReview → Rejected**: document reasons, identify rework
- **reopen: Rejected → InProgress**: address feedback, log
- **deprioritize: (Agreed|InProgress) → Proposed**: document reason, pause work

All transitions logged with timestamp + initiator.

## 3.4 PBI History Log
- Location: `backlog.md`
- Fields: Timestamp, PBI_ID, Event_Type, Details, User

## 3.5 PBI Detail Documents
- **Location**: `docs/delivery/<PBI-ID>/prd.md`
- **Required sections**: Overview, Problem Statement, User Stories, Technical Approach, UX/UI, Acceptance Criteria, Dependencies, Open Questions, Related Tasks
- Links back to backlog; backlog links to this doc
- Created when PBI moves Proposed → Agreed

---

# 4. Task Management

## 4.1 Task Documentation
- **Location**: `docs/delivery/<PBI-ID>/`
- **Task list**: `tasks.md`; **Task details**: `<PBI-ID>-<TASK-ID>.md`
- **Required sections**: Task-ID + Name, Description, Status History, Requirements, Implementation Plan, Verification, Files Modified

## 4.2 Principles
1. Each task = own markdown file
2. Follow naming convention
3. All required sections filled
4. Tasks index links to task files immediately on creation
5. Task files link back to index

## 4.3 Task Status Synchronisation
- Update both task file AND tasks index in same commit
- Verify status in both before starting
- Fix mismatches immediately

## 4.4 Status Definitions (workflow + canonical mapping)
| Workflow Status | Meaning | approval_state | execution_state |
|--------|---------|----------------|-----------------|
| Proposed | Newly defined | not_required | paused |
| Agreed | User approved | approved | paused |
| InProgress | AI Agent working | approved | in_progress |
| Review | Awaiting User validation | requested | paused |
| Done | User approved implementation | approved | done |
| Blocked | External dependency blocking | requested | blocked |

## 4.5 Event Transitions
- **user_approves: Proposed → Agreed**: verify, prioritize, create task file + link
- **start_work: Agreed → InProgress**: verify single InProgress per PBI, branch, log
- **submit_for_review: InProgress → Review**: requirements met, tests pass, PR/review ready
- **approve: Review → Done**: AC met, merge, archive. **Review Next Task Relevance** before marking Done.
- **reject: Review → InProgress**: document reason, feedback
- **significant_update: Review → InProgress**: document changes, resume
- **mark_blocked: InProgress → Blocked**: document reason
- **replan_after_blocker: Blocked → Agreed**: document resolution and create a replan/new branch for a fresh attempt
- **start_work (new attempt): Agreed → InProgress**: continue only in the new branch/attempt after replan

## 4.6 One In Progress Task Limit
One task per PBI 'InProgress' at a time (unless User approves concurrent).

## 4.7 Task History Log
- In task file under 'Status History'
- Fields: Timestamp, Event_Type, From_Status, To_Status, Details, User

## 4.8 Task Validation Rules
- All tasks associated with existing PBI; unique IDs; follow workflow; maintain history
- Pre-implementation: verify status, document task ID, list files, get approval
- Error prevention: stop on access issues, verify before starting
- Change management: reference task ID in commits, track deviations

## 4.9 Version Control
- Commit: `<task_id> <task_description>`
- PR title: `[<task_id>] <task_description>`
- On Done: `git acp "<task_id> <task_description>"`

## 4.10 Task Index File
- **Location**: `docs/delivery/<PBI-ID>/tasks.md`
- **Table**: `| Task ID | Name | Status | Description |`
- Name links to task file. Status per defined values. No extra content without User approval.

---

# 5. Testing Strategy and Documentation

## 5.1 Principles
1. Risk-based approach — prioritize by complexity/risk
2. Test pyramid — unit > integration > E2E
3. Clarity and maintainability
4. Automate wherever feasible

## 5.2 Test Scoping
- **Unit**: isolated functions/classes, mock external deps
- **Integration**: multi-component interaction. Mock external APIs, use real internal infra (DB, queues)
- **E2E**: full user-perspective flow, critical paths only

## 5.3 Test Plan Proportionality
| Task Complexity | Test Plan Scope |
|----------------|-----------------|
| Simple (constants, config) | 1–3 checks: compilation + basic integration |
| Basic (simple functions) | 5–15 cases: core functionality + error patterns |
| Complex (multi-service) | 15+ cases with coverage targets |

- Every implementation task MUST have `## Test Plan` section
- PBI-level: include dedicated "E2E CoS Test" task
- Avoid duplicating test plans across tasks — concentrate in E2E tasks

## 5.4 Test Implementation
- Unit tests: `test/unit/` mirroring source structure
- Integration tests: `test/integration/` or `test/<module>/`
- Clear, descriptive naming
