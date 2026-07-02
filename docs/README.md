# Документация конфигурации агентов

Короткий индекс файлов в `docs/` для этого репозитория.

| Документ | Назначение | Когда читать |
|----------|------------|--------------|
| [autonomous-task-with-verification.md](./autonomous-task-with-verification.md) | Цикл Execute → Verify → Analyze → Rework; роль **start** только как **analyzer** при вызове из orchestrator. | Когда нужна итеративная доводка до AC |
| [autonomous-self-improvement-loop.md](./autonomous-self-improvement-loop.md) | **Закрытая спираль** самоулучшения этого репо: root `start` ведёт outer-loop и запускает orchestrator wave напрямую, затем `START_REPORT` решает continue/stop. | Задача «улучши систему агентов» без микроучастия пользователя |
| [quick-start-orchestration.md](./quick-start-orchestration.md) | Быстрый сценарий: один запрос → root `start` → `Task(orchestrator)` → специалисты. | Первый запуск и онбординг |
| [start-workflow.md](./start-workflow.md) | Стабильный `/start` handoff и каноничный контур `approval_state`/`execution_state` с переходами pause/resume/blocked. | Операционное ведение wave-циклов и контроль статусов |
| [process-and-quality-gates.md](./process-and-quality-gates.md) | Когда какой агент и минимальные проверки качества. | Перед выдачей финального ответа |
| [comparison-multi-agent-setups.md](./comparison-multi-agent-setups.md) | Наша схема координации в контексте других подходов. | Когда сравниваете подходы/trade-offs |
| [project-plan-convention.md](./project-plan-convention.md) | Каталог **`.plan/`** в корне проекта: `todos.md`, журнал, файлы по направлениям. | Для длинных и многоэтапных задач |
| [autonomy-multi-voice.md](./autonomy-multi-voice.md) | Многоходовая автономность: несколько «голосов», лимиты; не AGI. | Для сложных спорных решений |
| [orchestrator-three-voice-prompt-example.md](./orchestrator-three-voice-prompt-example.md) | Готовый шаблон промпта: Builder / Skeptic / Verifier + бюджеты. | Когда нужно быстро запустить multi-voice |
| [delegation-chain.md](./delegation-chain.md) | От `/start` до вложенных сабагентов; эквивалент `Task(X)` и `/X`. | Единый источник правды по маршрутизации |
| [delegation-exporter.md](./delegation-exporter.md) | Безопасный экспортер дерева делегирования из Cursor/Codex `state.vscdb` или `composer.composerData`. | Когда нужно проверить, кто кого запускал и как выглядело дерево оркестрации |
| [pbi-task-workflow.md](./pbi-task-workflow.md) | Управление PBI/Task: workflow-статусы, их явный mapping в `approval_state`/`execution_state`, переходы и тестирование (извлечено из `aleksander.mdc`). | Когда включен task-driven режим |
| [canonical-paths-and-cursor-mirror.md](./canonical-paths-and-cursor-mirror.md) | Канон vs зеркало `.cursor/`, `CHECK_CURSOR_MIRROR`, команды проверки drift. | Копирование в IDE, CI, рассинхрон деревьев |
| [external-parity-oh-my-claudecode.md](./external-parity-oh-my-claudecode.md) | Сравнение с oh-my-claudecode: концептуальные параллели (условные метки, без гарантий 1:1). | Контекст для терминологии экосистемы |
| [GLOSSARY.md](./GLOSSARY.md) | Канонический глоссарий: agent, DUA, envelope, ENTRY_MODE, B-tree, autopilot и др. | Когда нужно уточнить значение термина |
| [MAINTENANCE_RUNBOOK.md](./MAINTENANCE_RUNBOOK.md) | Пошаговые инструкции: добавить/переименовать/удалить агент, создать skill, обновить profile. | При любых изменениях реестра или структуры |
| [skills-index.md](./skills-index.md) | Полный перечень `skills/*/SKILL.md` с однострочными описаниями. | При добавлении skill, онбординге |
| [cursor-ai-practices-map.md](./cursor-ai-practices-map.md) | Карта практик ИИ (MCP, evals, память, телеметрия…) → пути в репо. | Быстрый обзор интеграции под Cursor |
| [dag-branch-dependencies.md](./dag-branch-dependencies.md) | DAG веток, `DEPENDENCIES`, антициклы в multi-agent. | Параллельные writer-ветки |
| [model-routing.md](./model-routing.md) | Выбор tier модели по роли (оркестратор / builder / reviewer). | Оптимизация стоимости и качества |
| [agent-telemetry-contract.md](./agent-telemetry-contract.md) | Поля телеметрии по веткам, rework, инструменты. | Наблюдаемость, разбор прогонов |
| [cursor-hooks-and-harness.md](./cursor-hooks-and-harness.md) | Hooks и harness Cursor в связке с правилами проекта. | Локальная дисциплина команды |
| [rag-over-core-policy.md](./rag-over-core-policy.md) | Когда RAG/индекс по `rules/agents/skills` уместен, риски дрейфа. | Расширенный поиск по core |
| [eval-pipeline-vision.md](./eval-pipeline-vision.md) | Видение CI/evals для правил и агентов. | Долгосрочная автоматизация проверок |
| [replay-fixtures-vision.md](./replay-fixtures-vision.md) | Фикстуры ответов инструментов для регрессий. | Детерминированные тесты политик |
| [open-telemetry-future.md](./open-telemetry-future.md) | OpenTelemetry spans для agent/MCP (перспектива). | Платформенная observability |
| [security/prompt-injection-probes.md](./security/prompt-injection-probes.md) | Набор проб и чеклист challenge-pass. | Безопасность, adversarial входы |
| [multimodal-injection-class.md](./multimodal-injection-class.md) | Мультимодальные и unicode-инъекции (OCR, вложения, canvas). | Угрозы вне текста задачи |
| [supervisor-routing-criteria.md](./supervisor-routing-criteria.md) | Явный supervisor и критерии маршрутизации vs неявный выбор модели. | Стабильная оркестрация |
| [llm-as-judge-playbook.md](./llm-as-judge-playbook.md) | LLM-as-judge: рубрики, human-held gold, дисперсия прогонов. | Evals и приёмка |
| [skill-tags-and-discovery.md](./skill-tags-and-discovery.md) | Теги, «When to use», поиск skill без раздува контекста Cursor. | Навигация по skills |

## Единый источник правды

- Маршрутизация и допустимые вызовы: `docs/delegation-chain.md`.
- Цикл верификации и analyzer-роль `start`: `docs/autonomous-task-with-verification.md`.
- Автономная спираль улучшения конфиг-репо: `docs/autonomous-self-improvement-loop.md`.
- Минимальные quality gates и финальный чеклист: `docs/process-and-quality-gates.md`.
- Глоссарий терминов системы: `docs/GLOSSARY.md`.
- Обслуживание реестра (добавить/удалить/переименовать агент): `docs/MAINTENANCE_RUNBOOK.md`.
- Описание скриптов валидации: `scripts/README.md`.

См. также каталог агентов: [agents/README.md](../agents/README.md) и [корневой README](../README.md).
