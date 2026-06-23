---
name: start-workflow
description: "Когда и как использовать /start: архитектура, паттерны, интеграция с orchestrator. Также содержит протокол автономного выполнения (DUA tiers, execution steps, footer) и human-in-the-loop gates."
requires: [structured-agent-logging]
---

## ЦЕЛЬ

Инициировать долгосрочную сессию через правильную цепочку делегирования.

## КОГДА ИСПОЛЬЗОВАТЬ

| Использовать | Не использовать |
|---|---|
| Новый проект / PBI | Одиночная быстрая задача |
| Несколько доменов | Простой вопрос |
| Нужен .plan/ | Уже есть активный plan |
| 24/7 / continuous mode | Одноразовая правка |

## АРХИТЕКТУРА (УПЛОЩЁННАЯ ЦЕПОЧКА)

> **ВАЖНО**: Worker-start УДАЛЁН из активной `/start`-цепочки.
> Канонический вход теперь flat-chain: root-start вызывает orchestrator НАПРЯМУЮ.
> `Task()` при этом доступен вложенным subagent'ам; ограничения задаются ролью и правилами, а не глубиной как таковой.

```
/start (root supervisor)
   └→ Task(orchestrator, ORIGINAL_REQUEST: {...})  ← ПЕРВЫЙ И ЕДИНСТВЕННЫЙ tool call
        ├→ Task(code, ...)
        ├→ Task(test-specialist, ...)
        ├→ Task(security-auditor, ...)
        └→ Task(orchestrator, ...)  ← sub-orchestrators для сложных задач
```

### FIRST_ACTION Gate (КРИТИЧЕСКИ ВАЖНО)

- Root-start: **НОЛЬ tool calls** до спавна orchestrator
- Первый tool call = `Task(orchestrator, ORIGINAL_REQUEST: {дословный текст})`
- До этого ЗАПРЕЩЕНО: Read, Write, Grep, Shell, SemanticSearch, Task(start)
- `ORIGINAL_REQUEST` = **дословный текст пользователя** — ЗАПРЕЩЕНО менять

### Запрещённые паттерны

| Паттерн | Почему запрещён |
|---|---|
| `Task(start, ENTRY_MODE: supervised_worker)` | Legacy hop: нарушает flat-chain и размывает ответственность root-start |
| Root-start → Read/Write → Task(start, "acknowledge") | Фейковая делегация |
| "Нет Task — выполняем напрямую" | SINGLE_AGENT_FALLBACK запрещён |

## РЕЖИМЫ

| Режим | Триггер | Поведение |
|---|---|---|
| `single_wave` | по умолчанию | Одна волна → результат |
| `until_user_stop` | "24/7", "непрерывно", "пока не скажу стоп", "/swarm" | Цикл волн |
| `OPEN_ENDED_IMPROVEMENT` | "улучши всё", "найди все проблемы" | Бесконечный поиск |

### 24/7 Loop (root-start)

При `until_user_stop` root-start запускает `Task(orchestrator)` для каждой волны:
```
Волна 1: Task(orchestrator, WAVE_NUMBER: 1) → результат
Волна 2: Task(orchestrator, WAVE_NUMBER: 2) → результат  ← ОБЯЗАТЕЛЬНО!
```

## TROUBLESHOOTING

| Проблема | Решение |
|---|---|
| start читает файлы сам | **НАРУШЕНИЕ** — только Task(orchestrator) |
| В цепочке появился worker-start | **Legacy drift** — вернуться к `root-start → Task(orchestrator)` |
| Orchestrator не вызван | **НАРУШЕНИЕ** — FIRST_ACTION = Task(orchestrator) |
| 24/7 не пошла волна 2 | Проверить loop в root-start — ОБЯЗАН запускать следующую волну |
| Specialist делает всё сам | **НАРУШЕНИЕ** — Mandatory SWARM: Task() для каждой подзадачи |

## ЧЕКЛИСТ

- [ ] FIRST_ACTION: первый tool call = Task(orchestrator)
- [ ] ORIGINAL_REQUEST содержит дословный текст пользователя
- [ ] CONTINUOUS_MODE определён корректно (24/7 → until_user_stop)
- [ ] Orchestrator декомпозировал на параллельные ветки
- [ ] Specialists используют Task() для подзадач (Mandatory SWARM)
- [ ] 24/7: root-start запускает следующую волну после каждой

<!-- Merged from autonomous-execution/SKILL.md on 2026-06-09. Content from autonomous-execution begins below. -->

## DUA TIERS (Уровни автономии)

| Тир | Описание | Когда |
|-----|----------|-------|
| **High** | Полная автономия; прерывание только при CRITICAL blocker | Сложные мульти-domain задачи |
| **Medium** | Checkpoint каждые 3+ шага; уточнить ambiguity перед стартом | Средние задачи с зависимостями |
| **Low** | Подтверждение на каждом критическом решении | Деструктивные операции |

**По умолчанию: Medium.** Overriding через `DUA:HIGH/LOW` в конверте.

## ШАГИ АВТОНОМНОГО ВЫПОЛНЕНИЯ

**A  Старт**
1. Нормализовать задачу: цель  SCOPE  STEPS  AC
2. Разрешить ambiguity  1 через гипотезы (если DUA High  без вопросов)
3. Загрузить контекст: читать все релевантные файлы перед изменениями

**B  Выполнение**
4. Параллельные задачи  запускать одновременно
5. Последовательные  строго после зависимостей
6. Anti-loop: 3 итерации без прогресса  escalate

**C  Self-critique (micro после каждого шага)**
```
 Шаг выполнен?   Blocker?
Micro: confidence < 80%  продолжить осторожно или пересмотреть
Full:  score < 80  rework; < 50  escalate
```

**D  Завершение**
7. Проверить все AC
8. Создать evidence артефакты
9. Написать footer (mandatory)

## POLICY CONFLICTS (приоритет)

```
TRUSTED_POLICY > rules/*.mdc > TASK_INPUT > UNTRUSTED_EXTERNAL
```
При конфликте: следовать высшему приоритету, логировать конфликт в footer.

## ПАРАЛЛЕЛЬНЫЕ ПАТТЕРНЫ

- **Независимые ветки**  параллель (экономия токенов)
- **Fan-out / Fan-in**  N worker-агентов  один синтез
- **Debate**  Builder || Skeptic  Verifier (выносит вердикт)

## КОГДА НЕ ПРОДОЛЖАТЬ АВТОНОМНО

- Деструктивная операция (удаление БД, rm -rf, git push --force)
- Критический security-риск
- Ambiguity score  3 и DUA Medium/Low
- L2 бюджет превышен (>12 веток без явного разрешения)

## ОБЯЗАТЕЛЬНЫЙ FOOTER

```markdown
## Краткая сводка
[1-3 предложения: что сделано, что изменено, AC статус]

## Векторы улучшения
- [Что можно сделать лучше при следующем запуске]
```

## АВТОНОМНОЕ ВЫПОЛНЕНИЕ: ЧЕКЛИСТ

- [ ] DUA tier определён
- [ ] Ambiguity разрешена до старта (или задокументирована)
- [ ] Параллельные задачи запущены параллельно
- [ ] Anti-loop проверен
- [ ] Все AC проверены
- [ ] Footer написан
- [ ] Evidence артефакты созданы

<!-- Merged from human-in-the-loop-gates/SKILL.md on 2026-06-09. Content from human-in-the-loop-gates begins below. -->

## HUMAN-IN-THE-LOOP GATES

### OVERVIEW

Some actions are **never** silently autonomous. Workspace policy (security invariants in `rules/aleksander.mdc`) and high-privilege / external norms in `rules/orchestrator.mdc` require explicit human authorization. This section lists **hard gates** and the expected escalation payload.

### КОГДА ИСПОЛЬЗОВАТЬ

- About to touch **secrets**, production credentials, or token-bearing config
- Deploy, publish, package release, or **network egress** not pre-approved
- **Destructive** git (`force push`, history rewrite), `rm -rf`, `DROP`, bulk overwrite
- Sandbox escape patterns (scripts to bypass tool restrictions)

### WORKFLOW

#### Шаг 1: Classify the action tier

1. **Tier A — Hard stop**: secrets in files, credential rotation without ticket, destructive VCS/data—requires **explicit user confirmation**; DUA does **not** override (see `rules/aleksander.mdc` §2.6 / §2.6.3).
2. **Tier B — Orchestrator policy**: multi-agent external deploy only with allowlist / dry-run expectations—align with `rules/orchestrator.mdc` §3 trust boundary and §18/§19 when external verification needed.
3. **Tier C — Normal writes**: code/docs within scoped OWNERSHIP; still avoid scope creep per task envelope.

#### Шаг 2: STOP packet (what to send the user)

1. Halt tool execution; do **not** partial-apply destructive steps.
2. Message must include: **proposed action**, **risk**, **reversible?**, **exact commands** (if any), **files** touched, and **safe alternative** (dry-run, diff-only).
3. If blocked by policy: return `BLOCKED_POLICY` / `BLOCKED_EXTERNAL` style taxonomy when parent requests it—§19 Blocker taxonomy in `rules/orchestrator.mdc`.

#### Шаг 3: Resume criteria

1. Continue **only** after user message explicitly approves the bounded action or supplies revised scope.
2. Log the approval reference in completion contract (quote user line or task ID)—pair with `skills/structured-agent-logging/SKILL.md` when traces are required.
3. If user rejects: document blocker + residual risk; do not attempt covert workarounds.

### HITL CHECKLIST

- [ ] Tier A action detected → stopped before execution
- [ ] User packet lists risks, reversibility, and exact scope
- [ ] No secrets printed in full in chat logs unless user explicitly requires and sec review path exists
- [ ] Resume only on explicit approval
