# Multi-Agent Ecosystem — Agent Index

*33 agent definitions (4 coordination + 29 domain specialists) for ZCode `multi-agent-ecosystem` skill.*

## Canonical Paths (ZCode)

| Layer | Path (from skill root) |
|-------|------------------------|
| Agents | `references/agents/<name>.md` |
| Rules | `../rules/` |
| Skills | `../skills/` |
| Orchestration | `../orchestration/` |
| Docs | `../docs/` |

Load agents via `/start`, `/orchestrator`, or `multi-agent-ecosystem` skill → `references/agents/<name>.md`.

## Quick Start

| Scenario | Route |
|----------|-------|
| Complex / multi-domain | `/start` → orchestrator → specialists |
| Single domain, clear scope | Load specialist brief directly |
| New capability needed | `meta-agent-architect` or `subagent-factory` |

## Coordination Agents

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [start](start.md) | Entry router | Complex requests, 24/7 loops, multi-domain work |
| [orchestrator](orchestrator.md) | Multi-branch coordination | Cross-domain projects, parallel specialist branches |
| [meta-agent-architect](meta-agent-architect.md) | Ecosystem design | Agent family redesign, standards, merge/split |
| [subagent-factory](subagent-factory.md) | Package builder | Create agent + rules + skill packages |

## Planning & Architecture

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [architect](architect.md) | System design | Planning, specs, architecture before coding |
| [api-designer](api-designer.md) | API design | Endpoints, contracts, developer experience |
| [agent-architect](agent-architect.md) | Agent workflows | Roles, guardrails, runbooks |

## Development & Implementation

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [code](code.md) | General implementation | Features, bugs, refactors |
| [debug](debug.md) | Root cause | Diagnose errors, then fix |
| [database-specialist](database-specialist.md) | Data layer | Schema, migrations, query tuning |
| [frontend-specialist](frontend-specialist.md) | UI/UX | React/TS/CSS, accessibility |
| [mobile-specialist](mobile-specialist.md) | Mobile | React Native, iOS/Android |
| [provider-integrator](provider-integrator.md) | AI providers | `src/api/providers/**` integration |

## Data & Analytics

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [data-analyst](data-analyst.md) | Analytics | ETL, visualization, data science |

## Operations & Infrastructure

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [devops-specialist](devops-specialist.md) | CI/CD & deploy | Docker, pipelines, Kubernetes |
| [monitoring-specialist](monitoring-specialist.md) | Observability | Logging, metrics, tracing, APM |

## Quality Assurance

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [test-specialist](test-specialist.md) | Testing | Jest, coverage, failure debugging |
| [code-reviewer](code-reviewer.md) | Code quality | Standards, mentoring |
| [code-simplifier](code-simplifier.md) | Refactoring | Simplify without behavior change |
| [code-skeptic](code-skeptic.md) | Verification | Challenge claims, enforce rules |
| [security-auditor](security-auditor.md) | Security | Vulnerability assessment |
| [performance-optimizer](performance-optimizer.md) | Performance | Profiling, latency, memory |
| [review](review.md) | Formal review | Git-diff review, approval verdicts |
| [benchmark-specialist](benchmark-specialist.md) | Behavior contracts | Transcript evals, regressions |

## Documentation & Support

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [docs-specialist](docs-specialist.md) | Technical writing | READMEs, API docs, changelogs |
| [bug-triage](bug-triage.md) | Bug analysis | Repro steps, root cause, fix plan |
| [repo-explorer](repo-explorer.md) | Navigation | Find files, trace flows |
| [ask](ask.md) | Q&A only | Explanations without code changes |
| [release-manager](release-manager.md) | Releases | Versioning, changesets |

## Ecosystem Management

| Agent | Domain | When to Use |
|-------|--------|-------------|
| [rules-specialist](rules-specialist.md) | Policy rules | Create/update `.mdc` rules |
| [skills-specialist](skills-specialist.md) | Skills library | Create/update `SKILL.md` files |
| [profile-manager](profile-manager.md) | Project profiles | Custom agent profiles |
| [agent-manager](agent-manager.md) | Agent lifecycle | Create, update, deactivate agents |

## Delegation Pattern (ZCode)

```
User → /start → orchestrator brief → parallel specialist branches
                                      ↓
                         references/agents/<specialist>.md
```

- **start**: hand off verbatim `ORIGINAL_REQUEST` to orchestrator; no direct repo work.
- **orchestrator**: decompose, assign OWNERSHIP, delegate per `../orchestration/delegation-chain.md`.
- **specialists**: execute in scope; delegate when 2+ independent subtasks exist.

## Full Agent List (33)

`agent-architect`, `agent-manager`, `api-designer`, `architect`, `ask`, `benchmark-specialist`, `bug-triage`, `code`, `code-reviewer`, `code-simplifier`, `code-skeptic`, `data-analyst`, `database-specialist`, `debug`, `devops-specialist`, `docs-specialist`, `frontend-specialist`, `meta-agent-architect`, `mobile-specialist`, `monitoring-specialist`, `orchestrator`, `performance-optimizer`, `profile-manager`, `provider-integrator`, `release-manager`, `repo-explorer`, `review`, `rules-specialist`, `security-auditor`, `skills-specialist`, `start`, `subagent-factory`, `test-specialist`
