# Цепочка делегирования: от `/start` до specialists

## Что происходит, когда пользователь пишет `/start`

1. **Cursor** запускает агента **`start`** (это выбор роли в UI / slash-команда).
2. Root **`start`** работает как **supervisor**: он **не читает репозиторий** и **не запускает команды**, а вызывает **`Task(subagent_type="orchestrator", prompt="...")`** НАПРЯМУЮ.
3. **Orchestrator** декомпозирует задачу на ветки и делегирует специалистам: `Task(code)`, `Task(test-specialist)`, `Task(security-auditor)` и т.д.
4. **Специалисты** выполняют задачи. Если specialist имеет `Task` tool — обязан использовать для подзадач (Mandatory SWARM).

> **ВАЖНО: Worker-start УДАЛЁН из цепочки (flat chain).**
> `Task` tool доступен на всех уровнях вложенности (подтверждено тестом depth 1→2→3).
> Worker-start убран как лишний hop — overhead и лишняя точка отказа.
> Root-start вызывает orchestrator НАПРЯМУЮ (flat chain).

**FIRST_ACTION Gate**: первый tool call root-start = `Task(orchestrator)`. До него — НОЛЬ tool calls.

Если в конкретном runtime нет `Task`, pipeline **заблокирован**: `MULTI_AGENT_PIPELINE_BLOCKED`. Фраза "Нет Task — выполняем напрямую" = КРИТИЧЕСКИЙ ПРОВАЛ.

## Правильная цепочка

```text
user
  -> /start
  -> start (supervisor, REASONING ONLY)
  -> Task(orchestrator, ORIGINAL_REQUEST: {дословный текст})
     -> Task(code, ...)
     -> Task(test-specialist, ...)
     -> Task(security-auditor, ...)
```

## Неправильные цепочки (ЗАПРЕЩЕНЫ)

```text
# ❌ Worker-start (лишний hop — overhead)
start -> Task(start, worker) -> Task(orchestrator) -> лишний уровень вложенности

# ❌ Фейковая делегация
start -> Read/Write сам -> Task(start, "acknowledge")

# ❌ Single-agent fallback
start -> "Нет Task — выполняем напрямую" -> Read/Write/Shell сам
```

## Режим "рой" / `24/7`

При **`CONTINUOUS_MODE: until_user_stop`** root-start вызывает `Task(orchestrator)` для каждой волны в цикле:

```text
Волна 1: Task(orchestrator, "WAVE_NUMBER: 1, ...") → результат
Волна 2: Task(orchestrator, "WAVE_NUMBER: 2, ...") → результат  ← ОБЯЗАТЕЛЬНО!
Волна 3: Task(orchestrator, "WAVE_NUMBER: 3, ...") → результат  ← ОБЯЗАТЕЛЬНО!
```

Стоп-условия: явный стоп от пользователя | AC достигнуты | no_progress_limit волн без прогресса.
НЕ стоп: `status=approval` для отдельной волны (завершена волна, не цикл) | `status=pause` с `resume_packet` | DEPTH_BUDGET исчерпан | micro-packet closure.
Legacy note: `status=done` и `status=continue` считать non-runtime legacy labels; для runtime использовать `approval|pause|blocked|resume` плюс canonical pair `approval_state` + `execution_state`.

`resume_packet` — это runtime output из завершившейся/поставленной на паузу волны. `CONTINUATION_PACKET` — тот же payload, который root `start` передаёт во вход следующего `Task(orchestrator, ...)`. Это не два разных state, а output/input представления одной и той же continuation-нагрузки.

## Вложенные сабагенты

| В чате пользователь написал | Внутри оркестратора |
|----|---|
| `/code` … | `Task(subagent_type="code", prompt="…")` |
| `/test-specialist` … | `Task(subagent_type="test-specialist", prompt="…")` |
| `/orchestrator` … | `Task(subagent_type="orchestrator", prompt="…")` |

## Allowed / Forbidden

| Сценарий | Статус | Комментарий |
|----------|--------|-------------|
| root `start` → `Task(orchestrator)` | **Allowed** | Канонический путь |
| root `start` → `Task(start, worker)` | **Forbidden** | Лишний hop — flat chain only |
| root `start` → `Task(code\|debug)` | **Forbidden** | Только через orchestrator |
| orchestrator → `Task(code\|debug\|...)` | **Allowed** | Основная модель |
| specialist → `Task(...)` для подзадач | **Allowed** | Mandatory SWARM |
| same-type с более узким scope | **Allowed** | Fingerprint отличается, depth <= 3 |
| same-type с тем же fingerprint | **Forbidden** | Loop |

## Приоритет решения внутри specialist branch

Для любого specialist (`code`, `test-specialist`, `frontend-specialist`, `docs-specialist`) порядок всегда такой:

1. **MUST delegate** — если есть **2+ независимые подзадачи**
2. **MAY execute directly** — только если задача маленькая, неделимая и без независимых частей
3. **MUST escalate** — если локальная координация выросла до **3+ parallel writer children**

| Ситуация | Решение |
|----------|---------|
| 2+ независимые подзадачи | Specialist **обязан** запускать `Task()` |
| 1 маленькая неделимая задача | Specialist **может** сделать сам |
| Нужен same-type child | **Можно**, но только при более узком scope |
| Нужен другой домен | **Можно** звать подходящего специалиста |
| 3+ writer children | **Обязательная** эскалация в `orchestrator` |
| Reader children | Без writer-лимита, если нет конфликта OWNERSHIP |

Формула:

```text
specialist
  -> MUST delegate if 2+ independent subtasks
  -> MAY execute directly only for tiny indivisible work
  -> MUST escalate to orchestrator at 3+ writer children
```

## Однотипная делегация (same-type delegation)

1. Дочерний scope **строго уже** родительского.
2. Branch fingerprint отличается (goal / target-files / AC).
3. Глубина однотипной цепочки ≤ 3.

## См. также

- `agents/start.md` — рабочая модель start agent.
- `agents/orchestrator.md` — orchestrator agent.
- `rules/orchestrator.mdc` — правила оркестрации.
