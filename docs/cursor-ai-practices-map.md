# Карта практик ИИ → артефакты репозитория (Cursor / multi-agent)

Единый указатель: что из «набора практик под Cursor» куда легло в этом репо. Дубли осознанные: часть уже в `rules/orchestrator.mdc` и смежных правилах; здесь — ссылки на skills и docs, добавленные для операционализации.

| Практика | Куда смотреть |
| --- | --- |
| MCP schema-first, allowlist, progressive discovery | [skills/mcp-governance/SKILL.md](../skills/mcp-governance/SKILL.md) |
| Конверты делегирования, DEPENDENCIES, fingerprint, relay | [skills/orchestrator/SKILL.md](../skills/orchestrator/SKILL.md) (delegation-contracts merged), [docs/dag-branch-dependencies.md](./dag-branch-dependencies.md) |
| Evals, golden tasks, рубрики | [skills/agent-evals/SKILL.md](../skills/agent-evals/SKILL.md), [docs/eval-pipeline-vision.md](./eval-pipeline-vision.md), [docs/llm-as-judge-playbook.md](./llm-as-judge-playbook.md) |
| LLM-as-judge, стабильность скоринга | [docs/llm-as-judge-playbook.md](./llm-as-judge-playbook.md) |
| Agent Council, judge voice | [skills/agent-council-judge/SKILL.md](../skills/agent-council-judge/SKILL.md) |
| Память уровнями, session context | [skills/session-memory-tiers/SKILL.md](../skills/session-memory-tiers/SKILL.md), [project-plan-convention.md](./project-plan-convention.md) (`.plan/`) |
| Policy as structured blocks (YAML) | [skills/structured-policy-yaml/SKILL.md](../skills/structured-policy-yaml/SKILL.md) |
| Санитизация вывода инструментов, indirect injection | [skills/tool-output-sanitization/SKILL.md](../skills/tool-output-sanitization/SKILL.md), [docs/security/prompt-injection-probes.md](./security/prompt-injection-probes.md) |
| Мультимодальные инъекции (OCR, unicode, canvas) | [docs/multimodal-injection-class.md](./multimodal-injection-class.md) |
| Red team / injection suite (пробы) | [docs/security/prompt-injection-probes.md](./security/prompt-injection-probes.md) |
| Маршрутизация моделей по роли | [docs/model-routing.md](./model-routing.md) |
| Явный supervisor routing vs неявный выбор модели | [docs/supervisor-routing-criteria.md](./supervisor-routing-criteria.md) |
| Теги skills, поиск без раздувания контекста | [docs/skill-tags-and-discovery.md](./skill-tags-and-discovery.md) |
| Телеметрия и cost per branch | [docs/agent-telemetry-contract.md](./agent-telemetry-contract.md) |
| Структурированные логи агентов | [skills/structured-agent-logging/SKILL.md](../skills/structured-agent-logging/SKILL.md), [docs/agent-telemetry-contract.md](./agent-telemetry-contract.md) |
| Replay fixtures (видение + CI) | [docs/replay-fixtures-vision.md](./replay-fixtures-vision.md) |
| RAG только по core (осторожно) | [docs/rag-over-core-policy.md](./rag-over-core-policy.md) |
| Cursor hooks / harness | [docs/cursor-hooks-and-harness.md](./cursor-hooks-and-harness.md) |
| OpenTelemetry (будущее) | [docs/open-telemetry-future.md](./open-telemetry-future.md) |
| Полный список skills | [docs/skills-index.md](./skills-index.md) |
| Evidence-first, completion debt | [evidence-first-acceptance.md](./evidence-first-acceptance.md), [process-and-quality-gates.md](./process-and-quality-gates.md) |
| Web-research fact-pack (цитаты, UNTRUSTED_EXTERNAL) | [skills/web-research-fact-pack/SKILL.md](../skills/web-research-fact-pack/SKILL.md), [skills/orchestrator/SKILL.md](../skills/orchestrator/SKILL.md) |
| Budget / depth / fan-out | [skills/orchestrator/SKILL.md](../skills/orchestrator/SKILL.md) (budget-orchestration merged) |
| CAID, disjoint OWNERSHIP, атрибуция веток | [skills/caid-worktrees/SKILL.md](../skills/caid-worktrees/SKILL.md) (caid-ownership-matrix merged), [docs/dag-branch-dependencies.md](./dag-branch-dependencies.md) |
| Human-in-the-loop, approve перед опасными операциями | [skills/start-workflow/SKILL.md](../skills/start-workflow/SKILL.md) (human-in-the-loop-gates merged) |
| Behavior benchmarks / transcript contracts | [skills/agent-evals/SKILL.md](../skills/agent-evals/SKILL.md) (behavior-benchmarks-transcript merged), [skills/repo-task-proof-loop/SKILL.md](../skills/repo-task-proof-loop/SKILL.md), скрипты в `scripts/` |

Обновляйте эту таблицу при добавлении новых практик или переименовании путей.
