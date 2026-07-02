# Glossary — Cursor Agent System

Канонический глоссарий терминов, используемых в репозитории. При расхождениях в разных файлах — этот документ авторитетен.

---

## Агенты и роли

| Термин | Определение |
|--------|-------------|
| **agent** | Файл `agents/<name>.md` с YAML-frontmatter и инструкциями для Cursor. Вызывается как `/<name>` в UI или `Task(subagent_type="<name>")` программно. |
| **coordination agent** | Агент-координатор: не выполняет предметную работу сам, только маршрутизирует и синтезирует. Четыре таких агента: `start`, `orchestrator`, `meta-agent-architect`, `subagent-factory`. |
| **domain specialist** | Агент-специалист: выполняет конкретную предметную работу (code, debug, test-specialist, …). Сейчас 28 специалистов. |
| **orchestrator** | Рекурсивный координатор: получает задачу от `start`, декомпозирует на ветки, делегирует специалистам или под-оркестраторам, синтезирует результат. |
| **start** | Тонкий супервизорный роутер: получает запрос пользователя, формирует envelope, **один раз** вызывает `Task(orchestrator)`, синтезирует ответ пользователю. Сам не вызывает специалистов. |
| **worker-start** | **Устаревший термин.** Ранее — второй экземпляр `start` с `ENTRY_MODE: supervised_worker`. Удалён из активной цепочки в пользу flat-chain: root `start` вызывает `Task(orchestrator)` напрямую. Вложенные subagent-ветки по-прежнему могут использовать `Task()` по своим правилам. |
| **sub-orchestrator** | Экземпляр оркестратора, запущенный как ветка другого оркестратора. Применяется при fan-out > 6 или для явно обособленного под-домена. |
| **swarm / рой** | Набор параллельно работающих агентов-специалистов внутри одной волны оркестрации. |
| **B0, B-tree** | Phase-tree нотация: B0 — корневой оркестратор волны, B0-1/B0-2/… — его дочерние ветки. |

---

## Режимы и конверты

| Термин | Определение |
|--------|-------------|
| **envelope** | Структурированный заголовок, который `start` формирует и передаёт в `Task(orchestrator)`. Содержит: `USER_MESSAGE`, `ENTRY_MODE`, `OWNERSHIP`, `CONTINUOUS_MODE`, `OPEN_ENDED_IMPROVEMENT`, etc. |
| **DUA** (Direct User Authorization) | Наличие явного пользовательского разрешения на действие. Сигналы: императивные глаголы («реализуй», «implement», «fix»), slash-команды, явные просьбы действовать. При DUA агент не ждёт подтверждения. Канонически определён в `rules/aleksander.mdc §1`. |
| **ENTRY_MODE** | Поле конверта, определяющее роль текущего вызова `start`. Значения: `supervised_worker` (**устарело** — исторически worker-start), `analyzer_only` / analyzer (start как верификатор в Execute→Verify→Analyze loop). Корневой handoff на волну — через `Task(orchestrator)`, не через worker-start. |
| **CONTINUOUS_MODE: until_user_stop** | Пользователь явно просит 24/7-режим: каждая волна завершается `recommended_action: continue` + `next_packet`, пока пользователь не остановит. |
| **OPEN_ENDED_IMPROVEMENT: yes** | Режим открытого самоулучшения: цикл завершается только при `steady_state` (исчерпан backlog) или явной остановке пользователем. |
| **FULL_FORCE_START_PROFILE** | Внутренний profiling-const: режим автопилота по умолчанию при `/start` без явного «лёгкий проход». См. `rules/orchestrator.mdc §1.1`. |
| **autopilot** | Пользовательский ярлык для `CONTINUOUS_MODE: until_user_stop` + `OPEN_ENDED_IMPROVEMENT: yes`. Внутреннее название — `FULL_FORCE_START_PROFILE`. |
| **SINGLE_AGENT_DEGRADED_MODE** | Исключительный fallback-лейбл при недоступном `Task` и явном разрешении политики/пользователя. Запрещён для `/start`, swarm, 24/7, open-ended; при нарушении ветка должна вернуться в `blocked`, без продолжения в degraded-режиме. |
| **PAUSED_FOR_RUNTIME_BUDGET** | Честный статус: работа прервана лимитами runtime, не завершена. |
| **approval_state** | Канонический approval-контур ветки: `not_required | requested | approved | rejected`. Используется совместно с `execution_state` в completion contracts. |
| **execution_state** | Канонический execution-контур ветки: `in_progress | paused | blocked | done | rework | aborted`. `paused` возобновляем через явный resume-event; `blocked` terminal для текущей попытки. |

---

## Artifact paths

| Термин | Определение |
|--------|-------------|
| **canonical path** | Пути `agents/`, `rules/`, `skills/`, `docs/`, `benchmarks/`, `scripts/`, `tg_bot/`, `profiles/` — root-level в этом репозитории конфигурации. |
| **mirror path** | `.cursor/` внутри host-проекта: IDE подхватывает агентов из `.cursor/agents/` и правила из `.cursor/rules/`. Это зеркало canonical. |
| **CHECK_CURSOR_MIRROR** | Команда проверки дрейфа между canonical и mirror. Документирована в `docs/canonical-paths-and-cursor-mirror.md`. |
| **profile** | Project-specific расширение в `profiles/<name>/`: содержит `agents/`, `rules/`, опционально `skills/`. Не входит в core. Активируется явным копированием в `.cursor/`. |
| **`.plan/`** | Директория в корне host-проекта: `todos.md`, `todos_full.md`, файлы `napravlenie-*.md`. Ведётся оркестратором после каждой волны. Спека: `skills/project-plan-dot-plan/SKILL.md`. |
| **`agent-tasks/<TASK_ID>/`** | Proof-loop артефакты: `spec.md`, `evidence.md`, `verdict.md`. Спека: `skills/repo-task-proof-loop/SKILL.md`. |

---

## Механизмы оркестрации

| Термин | Определение |
|--------|-------------|
| **Task(...)** | Программный вызов сабагента: `Task(subagent_type="code", prompt="…")`. Эквивалент `/code` для пользователя. |
| **fan-out** | Количество параллельных веток B0. При > 6 — обязательно сгруппировать в под-оркестраторы. |
| **quality gate** | Проверочный барьер перед синтезом результатов: все ветки вернули артефакты? AC выполнены? Доказательства присутствуют? |
| **RELAY_MODE** | Транспортный механизм: если `Task` недоступен внутри orchestrator runtime, но разрешён `PARENT_TASK_RELAY_ALLOWED`, оркестратор возвращает `ORCHESTRATOR_RELAY_REQUEST` родителю. |
| **behavior contract** | Статическая regex/path-проверка в `benchmarks/behavior-contracts.json`. Не требует LLM. Проверяет, что ключевые контракты присутствуют в файлах агентов/правил. |
| **transcript case** | Fixture-based проверка живого транскрипта в `benchmarks/transcript-cases.json`. |

---

## Смотрите также

- `rules/aleksander.mdc` — DUA и пользовательские предпочтения (канон)
- `rules/orchestrator.mdc` — контракты оркестрации (канон)
- `rules/specialists.mdc` — маршрутизация и реестр агентов (канон)
- `docs/delegation-chain.md` — single source of truth по цепочке делегации
- `docs/autonomous-self-improvement-loop.md` — спираль самоулучшения
