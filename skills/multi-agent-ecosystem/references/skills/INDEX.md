# Skills reference index

On-demand reference docs for the `multi-agent-ecosystem` skill. Flat layout: `references/skills/<name>.md` (not nested skill directories).

Canonical agent briefs: `references/agents/`. Rules: `references/rules/`. Orchestration runbooks: `references/orchestration/`.

## Catalog

| Name | Path | Description | Requires | Load when |
| --- | --- | --- | --- | --- |
| agent-evals | [agent-evals.md](agent-evals.md) | Измерения оценки агентов, golden tasks, регрессионные наборы, рубрики; когда гонять до merge core rules. | structured-agent-logging, orchestrator | Before merging core rules; benchmark/eval work |
| agent-manager | [agent-manager.md](agent-manager.md) | Agent lifecycle management — creation, updates, deactivation, registry validation. | — | Creating, updating, deactivating agents |
| agent-prompt-quality | [agent-prompt-quality.md](agent-prompt-quality.md) | Обязательные поля конверта делегирования, AC, Voice/Stop when  минимум двусмысленности, максимум исполнимости. | — | Before any delegation envelope |
| agent-quality-pipeline | [agent-quality-pipeline.md](agent-quality-pipeline.md) | Пайплайн качества многоагентных задач: граф работ, метрики, отладка, рубрика оценки оркестрации, Agent Council для multi-variant решений. | web-research-fact-pack, caid-worktrees | Multi-agent quality pipeline design |
| agent-system-navigation | [agent-system-navigation.md](agent-system-navigation.md) | Быстрая навигация по агентам, паттернам делегирования, маршрутизация задач. | — | Routing, finding agents/skills |
| caid-worktrees | [caid-worktrees.md](caid-worktrees.md) | Concurrent Agent Isolation via git worktrees per delegation branch | — | Parallel writer branches, OWNERSHIP isolation |
| circuit-breaker | [circuit-breaker.md](circuit-breaker.md) | Circuit breaker pattern for preventing cascading failures in agent delegation | — | Delegation failure cascades |
| context-propagation | [context-propagation.md](context-propagation.md) | Structured context envelope for reliable state propagation between agents | — | Cross-branch state envelopes |
| dag-validation | [dag-validation.md](dag-validation.md) | DAG (Directed Acyclic Graph) validation for agent delegation dependencies | — | Branch dependency graphs |
| mcp-governance | [mcp-governance.md](mcp-governance.md) | Управление доверием к MCP — allowlisting, схемы инструментов, уровни серверов, аудит, секреты; для Cursor/мультиагент контекста. | tool-output-sanitization | MCP servers, tool trust |
| model-routing | [model-routing.md](model-routing.md) | Multi-model routing for cost optimization based on task complexity and ambiguity | — | Cost-aware model selection |
| multi-pass-autonomy | [multi-pass-autonomy.md](multi-pass-autonomy.md) | Паттерн многопроходной автономии: Advocate → Critic → Arbiter, бюджет автономности, контракт сходимости. | — | Advocate/Critic/Arbiter loops |
| orchestrator | [orchestrator.md](orchestrator.md) | Use when: сложная задача с 2+ доменами, нужен параллельный мульти-voice pipeline | agent-prompt-quality, structured-policy-yaml | 2+ domains, parallel pipeline |
| project-plan-dot-plan | [project-plan-dot-plan.md](project-plan-dot-plan.md) | Структура .plan/ директории: файлы, форматы, обновление, связь с оркестрацией. | — | .plan/ structure and updates |
| repo-task-proof-loop | [repo-task-proof-loop.md](repo-task-proof-loop.md) | 7-фазный цикл выполнения задачи с доказательствами: spec → build → evidence → verify → fix → re-verify → learnings. | — | Evidence-first task execution |
| session-memory-tiers | [session-memory-tiers.md](session-memory-tiers.md) | Уровни памяти сессии — ephemeral/session/project/persistent policy; .plan/session-context; вытеснение; PII и секреты. | project-plan-dot-plan, tool-output-sanitization | Session context, memory eviction |
| specialist-discovery | [specialist-discovery.md](specialist-discovery.md) | Таблица субагентов и условия их выбора, включая динамическое обнаружение на основе индекса возможностей и исторической производительности. | — | Choosing which agent to delegate to |
| start-workflow | [start-workflow.md](start-workflow.md) | Когда и как использовать /start: архитектура, паттерны, интеграция с orchestrator. Также содержит протокол автономного выполнения (DUA tiers, execution steps, footer) и human-in-the-loop gates. | structured-agent-logging | /start routing, DUA, HITL gates |
| structured-agent-logging | [structured-agent-logging.md](structured-agent-logging.md) | Structured logs for multi-branch agent runs—JSONL records with branch_id, correlation IDs, and completion-contract friendly fields for audit and replay. | caid-worktrees, start-workflow | JSONL audit trails |
| structured-policy-yaml | [structured-policy-yaml.md](structured-policy-yaml.md) | Политика как YAML/структурированные блоки в задачах, валидация, version fields, совместимость с ../rules/*.mdc. | orchestrator, agent-prompt-quality, agent-evals | YAML policy fragments in tasks |
| subagent-factory | [subagent-factory.md](subagent-factory.md) | Creates or updates specialized subagents with matching rules and optional skills. Use when existing agents cannot cover a recurring task pattern or when orchestrator detects a capability gap. | — | Packaged agent+rules+skill creation |
| telemetry-pipeline | [telemetry-pipeline.md](telemetry-pipeline.md) | Agent telemetry collection and analysis pipeline | — | Agent metrics collection |
| thinking-checkpoints | [thinking-checkpoints.md](thinking-checkpoints.md) | Mandatory STOP-and-think gates at key decision points. Prevents dumb-model drift by forcing explicit reasoning before decomposition, delegation, mid-execution, synthesis, and response. | — | CP-1..CP-5 stop-and-think gates |
| tool-output-sanitization | [tool-output-sanitization.md](tool-output-sanitization.md) | UNTRUSTED_EXTERNAL из выводов инструментов — редакция, indirect injection, безопасная суммаризация для агентов. | mcp-governance, session-memory-tiers | UNTRUSTED_EXTERNAL tool output |
| web-research-fact-pack | [web-research-fact-pack.md](web-research-fact-pack.md) | Pre-implementation web research as gate §18—build a cited fact-pack envelope, treat web as UNTRUSTED_EXTERNAL, and satisfy allowed web_research statuses for non-trivial work. | — | Pre-implementation web research |

## Merged aliases

Former standalone skills merged into canonical references (from source skills index):

| Alias (merged) | Canonical reference | Notes |
| --- | --- | --- |
| autonomous-execution | [start-workflow.md](start-workflow.md) | Merged into start-workflow |
| behavior-benchmarks-transcript | [agent-evals.md](agent-evals.md) | Merged into agent-evals |
| budget-orchestration | [orchestrator.md](orchestrator.md) | Merged into orchestrator |
| caid-ownership-matrix | [caid-worktrees.md](caid-worktrees.md) | Merged into caid-worktrees |
| delegation-contracts | [orchestrator.md](orchestrator.md) | Merged into orchestrator |
| human-in-the-loop-gates | [start-workflow.md](start-workflow.md) | Merged into start-workflow |
| progressive-mcp-discovery | [mcp-governance.md](mcp-governance.md) | Merged into mcp-governance |


## Specialist routing

Which agent briefs typically load which reference:

| Reference skill | Specialist agent(s) |
| --- | --- |
| agent-evals | benchmark-specialist, meta-agent-architect |
| agent-manager | agent-manager, meta-agent-architect |
| agent-prompt-quality | orchestrator, all specialists |
| agent-quality-pipeline | orchestrator, meta-agent-architect |
| agent-system-navigation | start, orchestrator, repo-explorer |
| caid-worktrees | orchestrator, devops-specialist |
| circuit-breaker | orchestrator |
| context-propagation | orchestrator |
| dag-validation | orchestrator |
| mcp-governance | orchestrator, security-auditor |
| model-routing | orchestrator |
| multi-pass-autonomy | orchestrator, code-skeptic |
| orchestrator | orchestrator (primary) |
| project-plan-dot-plan | orchestrator, start |
| repo-task-proof-loop | all builder specialists |
| session-memory-tiers | orchestrator, start |
| specialist-discovery | orchestrator, start |
| start-workflow | start (primary) |
| structured-agent-logging | orchestrator, monitoring-specialist |
| structured-policy-yaml | rules-specialist, orchestrator |
| subagent-factory | subagent-factory, meta-agent-architect |
| telemetry-pipeline | monitoring-specialist, orchestrator |
| thinking-checkpoints | all agents |
| tool-output-sanitization | all agents handling external data |
| web-research-fact-pack | orchestrator, repo-explorer, security-auditor |

## ZCode delegation pattern

In Cursor, agents used `Task(subagent_type="...", prompt="...")`. In ZCode:

1. Load the target agent brief from `references/agents/<name>.md`
2. Spawn a ZCode sub-session (or run `/orchestrator` for coordination) with the full delegation envelope
3. Launch **independent** branches in parallel when ZCode supports concurrent agents
4. Apply MUST/MAY rules from `../rules/orchestrator.mdc` — specialists with 2+ independent subtasks must delegate

## Related

- [delegation-chain.md](../orchestration/delegation-chain.md)
- [evidence-first-acceptance.md](../orchestration/evidence-first-acceptance.md)
- [process-and-quality-gates.md](../orchestration/process-and-quality-gates.md)
