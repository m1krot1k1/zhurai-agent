# Task → agent routing (ZCode)

Consolidated routing for the **multi-agent-ecosystem** plugin (33 agents). Load the matching brief from `references/agents/<name>.md` when spawning a branch.

## Quick routing checklist

1. **Question only, no file changes** → `ask`
2. **One domain, clear scope, one artifact** → matching specialist (not orchestrator)
3. **Multiple domains or artifacts** → orchestrator (`/orchestrator` or orchestrator mode)
4. **Agent ecosystem changes** → `meta-agent-architect`, `subagent-factory`, or `agent-manager`
5. **Completion / review** → apply [evidence-first-acceptance.md](./evidence-first-acceptance.md)

## Entry routing

| User intent | Route |
|-------------|-------|
| Complex / multi-domain / unclear decomposition | `/start` → orchestrator |
| Multi-branch coordination | `/orchestrator` |
| Direct imperative + single domain | `/code`, `/debug`, `/docs-specialist`, … |
| Explain only | `/ask` or orchestrator → `ask` branch |

## Process gates (from quality workflow)

| Pattern | Route |
|---------|-------|
| `/start` | Orchestrator only for decomposition; user-facing synthesis via start router |
| Direct `/code`, `/debug`, … | Named specialist without `/start` |
| Imperative request (DUA) | Execute without blocking on PBI/task file |
| Explanation only | `ask` or single specialist read-only branch |
| Multi-artifact / multi-domain | Orchestrator with explicit branches and `OWNERSHIP` |

## Full specialist table

| Task | Agent | Brief path |
|------|-------|------------|
| Complex / non-obvious coordination | **start** (router) | `commands/start.md` |
| Multi-step delegation, parallel branches | **orchestrator** | `commands/orchestrator.md` + `references/agents/orchestrator.md` |
| Agent workflows / runbooks | **agent-architect** | `references/agents/agent-architect.md` |
| Planning / system architecture | **architect** | `references/agents/architect.md` |
| API design | **api-designer** | `references/agents/api-designer.md` |
| Bug triage / reproduction | **bug-triage** | `references/agents/bug-triage.md` |
| Plan stress-test / claim verification | **code-skeptic** | `references/agents/code-skeptic.md` |
| Code review / mentoring | **code-reviewer** | `references/agents/code-reviewer.md` |
| Formal git-diff review | **review** | `references/agents/review.md` |
| Refactor without behavior change | **code-simplifier** | `references/agents/code-simplifier.md` |
| Database schema / migrations / optimization | **database-specialist** | `references/agents/database-specialist.md` |
| Debugging / root cause | **debug** | `references/agents/debug.md` |
| Documentation | **docs-specialist** | `references/agents/docs-specialist.md` |
| React / UI / frontend | **frontend-specialist** | `references/agents/frontend-specialist.md` |
| Mobile / React Native / iOS / Android | **mobile-specialist** | `references/agents/mobile-specialist.md` |
| ETL / analytics / visualization | **data-analyst** | `references/agents/data-analyst.md` |
| CI/CD / Docker / deploy / containers | **devops-specialist** | `references/agents/devops-specialist.md` |
| Logs / metrics / tracing / observability | **monitoring-specialist** | `references/agents/monitoring-specialist.md` |
| Create / manage agent ecosystem | **meta-agent-architect** | `references/agents/meta-agent-architect.md` |
| Agent + rules + skill package | **subagent-factory** | `references/agents/subagent-factory.md` |
| Performance | **performance-optimizer** | `references/agents/performance-optimizer.md` |
| Providers `src/api/providers/**` | **provider-integrator** | `references/agents/provider-integrator.md` |
| Releases / changesets | **release-manager** | `references/agents/release-manager.md` |
| Codebase navigation / where to edit | **repo-explorer** | `references/agents/repo-explorer.md` |
| Security review | **security-auditor** | `references/agents/security-auditor.md` |
| Testing (Jest / TDD / coverage) | **test-specialist** | `references/agents/test-specialist.md` |
| Questions only, no changes | **ask** | `references/agents/ask.md` |
| Code implementation | **code** | `references/agents/code.md` |
| Behavior benchmarks / contracts | **benchmark-specialist** | `references/agents/benchmark-specialist.md` |
| Create / update `.mdc` rules | **rules-specialist** | `references/agents/rules-specialist.md` |
| Create / update `SKILL.md` | **skills-specialist** | `references/agents/skills-specialist.md` |
| Project profiles (`profiles/`) | **profile-manager** | `references/agents/profile-manager.md` |
| Agent lifecycle management | **agent-manager** | `references/agents/agent-manager.md` |

## Mandatory SWARM (specialist branches)

| Condition | Decision | Status |
|-----------|----------|--------|
| 2+ independent subtasks | Delegate to sub-sessions / sub-branches | **MUST** |
| 1 file, 1 action, no independent parts | Execute in current session | **MAY** |
| Same-type child (`code` → `code`) | Only if child scope is strictly narrower | **MAY** |
| Cross-domain (`code` → `test-specialist`) | Load matching agent brief | **MAY** |
| 3+ parallel **writer** children | Escalate to orchestrator | **MUST** |
| Reader branches (review, security, ask, explorer) | Parallelize without writer limit | **MAY** |

## Writer vs reader

| Class | Examples | Parallelism |
|-------|----------|-------------|
| **Writer** (changes files) | code, frontend-specialist, docs-specialist, rules-specialist, database-specialist | 3+ parallel writers under one specialist → escalate to orchestrator |
| **Reader** (analysis only) | code-reviewer, security-auditor, ask, repo-explorer, code-skeptic, review, benchmark-specialist | No fan-out limit |

## Cost-aware routing

1. One domain + one file + one artifact → **one specialist**
2. Multi-artifact / multi-domain → **orchestrator**
3. Read-only state mapping → **repo-explorer** once, cache `state_map`
4. Independent branches → launch in parallel when ZCode supports it
5. Source >3000 items or >5MB → sub-orchestrator + chunking

## See also

- [delegation-chain.md](./delegation-chain.md) — handoff chain
- [zcode-paths.md](./zcode-paths.md) — where briefs and rules live
- `references/rules/specialists.mdc` — canonical policy source
