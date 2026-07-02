# State Map Wave 1

## overview

- Scan scope covered: `rules/*.mdc`, `agents/*.md`, `skills/**/SKILL.md`, `docs/**`, `scripts/**`, `.plan/**`, `docs/delivery/**`, `profiles/**`.
- Repository is an agent-system config mono-repo focused on orchestration policy, specialist registry, skills, documentation, and validation tooling.
- Canonical paths are explicitly defined as `agents/`, `rules/`, `skills/`, `docs/`; `.cursor/` is treated as a runtime mirror, not primary source.
- Current observed top-level functional areas:
  - Policy and routing rules: `rules/`
  - Agent catalog and role definitions: `agents/`
  - Operational skills and playbooks: `skills/`
  - Process and architecture docs: `docs/`
  - Validation and benchmark automation: `scripts/`
  - Wave planning artifacts: `.plan/`
  - Optional profile extensions: `profiles/`

## core

### `rules/` (core governance)
- `rules/specialists.mdc`: canonical routing matrix, specialization boundaries, and canonical-path policy.
- `rules/orchestrator.mdc`: orchestration constraints, delegation envelope requirements, branch budgeting, quality gates.
- `rules/aleksander.mdc`: DUA, execution standards, security invariants, and task workflow expectations.
- Core function: defines behavior contracts and decision policy for all agents.

### `agents/` (core capability registry)
- Contains base coordination agents (`start`, `orchestrator`, `meta-agent-architect`, `subagent-factory`) and domain specialists.
- `agents/README.md` documents architecture, routing patterns, and specialist domains.
- Core function: source of role responsibilities and operational entry points.

### `skills/` (core execution methods)
- `skills/**/SKILL.md` provides reusable operational procedures (autonomy, quality pipeline, orchestration, proof loop, planning).
- Core function: prescriptive execution practices used by agents during task delivery.

### `docs/` (core operating knowledge)
- `docs/README.md` is the index for process docs and system operation references.
- Includes canonical-path policy, orchestration chain docs, maintenance runbook, glossary, quality process, and `.plan` convention.
- `docs/delivery/backlog.md` is present and used as the queue intake source for wave planning.
- Core function: stable human-readable source of process, governance, and maintenance guidance.

### `.plan/` (living wave control plane)
- `.plan/todos.md` stores active queue, completed/pending ledger, and next packet pointer.
- `.plan/todos_full.md` stores append-only wave history snapshots.
- `.plan/session-context.md` stores resume context (branch, wave state, next action).
- `.plan/README.md` defines update rules and evidence conventions.
- Core function: operational continuity for scan->plan->execute->verify->rescan cadence.

## peripheral

### `scripts/` (automation/verification support)
- Cross-platform script suite (`.py`, `.sh`, `.ps1`) for registry validation, repo consistency checks, behavior benchmarks, transcript evaluation, and delegation export.
- `scripts/README.md` defines execution intent and run order (including full benchmark pipeline).
- Peripheral classification: supports quality enforcement but does not define base policy itself.

### `profiles/` (optional extensions)
- Example profile present: `profiles/msnmp/` with profile-specific agent/rule additions.
- Peripheral classification: opt-in domain expansion; not universal core.

### Missing/empty target zones in requested scan
- `src/**`: not present in current repository snapshot.

## ownership hints

- Prefer policy changes in `rules/` when updating behavior contracts, routing gates, or safety constraints.
- Prefer role/scope changes in `agents/*.md` and keep `agents/README.md` aligned.
- Prefer method/runbook updates in `skills/**/SKILL.md` for reusable execution improvements.
- Prefer procedural and explanatory updates in `docs/` for user/operator guidance.
- Keep automation changes in `scripts/` and validate with consistency/benchmark scripts after edits.
- Treat `profiles/**` as project-specific overlays; avoid using them as default canonical behavior.

## risk notes

- Coverage risk: `src/**` remains absent in the current repository snapshot, so application-module mapping is not applicable.
- Drift risk: mirror behavior for `.cursor/` is documented as non-canonical; if mirror checks are not enabled, root vs mirror drift can persist unnoticed.
- Rule density risk: multiple high-authority policy files can overlap; changes should be validated via consistency and behavior benchmark scripts to avoid contract conflicts.
- Operational risk: profile-specific artifacts (`profiles/msnmp/**`) may be mistaken for universal defaults unless explicitly scoped.
