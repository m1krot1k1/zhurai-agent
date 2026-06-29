# Цепочка делегирования: от `/start` до specialists

> **PBI-002 operator sync:** терминология и relay-семантика этого документа должны совпадать с `docs/start-workflow.md`, `skills/start-workflow/SKILL.md` и `agents/start.md` (STEP 0.5).

## Что происходит, когда пользователь пишет `/start`

1. **Cursor** запускает агента **`start`** (это выбор роли в UI / slash-команда).
2. Root **`start`** выполняет **STEP 0** (reasoning only): фиксирует запрос, определяет `CONTINUOUS_MODE`, `OPEN_ENDED_IMPROVEMENT`, trust boundary — **без tool calls**.
3. Root **`start`** выполняет **STEP 0.5**: выводит **inline brief** (understanding-first) в **том же turn** — objective restatement, режим, hint плана волны. Это user-facing текст/reasoning, **не** tool call, **не** блокирующая пауза.
4. Root **`start`** вызывает **`Task(subagent_type="orchestrator", prompt="...")`** НАПРЯМУЮ — **первый и единственный** tool call в этом turn. Поле **`ORIGINAL_REQUEST`** в prompt — **дословный** текст пользователя (brief может перефразировать только для пользователя).
5. **Orchestrator** декомпозирует задачу на ветки и делегирует специалистам: `Task(code)`, `Task(test-specialist)`, `Task(security-auditor)` и т.д.
6. **Специалисты** выполняют задачи. Если specialist имеет `Task` tool — обязан использовать для подзадач (Mandatory SWARM).

> **ВАЖНО: Worker-start УДАЛЁН из цепочки (flat chain).**
> `Task` tool доступен на всех уровнях вложенности (подтверждено тестом depth 1→2→3).
> Worker-start убран как лишний hop — overhead и лишняя точка отказа.
> Root-start вызывает orchestrator НАПРЯМУЮ (flat chain).

**FIRST_ACTION Gate**: первый tool call root-start = `Task(orchestrator)`. До него — НОЛЬ tool calls (STEP 0.5 brief **не считается** tool call).

Если в конкретном runtime нет `Task`, pipeline **заблокирован**: `MULTI_AGENT_PIPELINE_BLOCKED`. Фраза "Нет Task — выполняем напрямую" = КРИТИЧЕСКИЙ ПРОВАЛ.

## STEP 0.5 — Understanding-first inline brief (DUA-safe)

**Цель:** показать понимание задачи пользователю **в том же turn**, до делегирования — без блокирующей паузы и без нарушения FIRST_ACTION.

**Порядок в одном turn:**

```text
1. STEP 0 (reasoning): CONTINUOUS_MODE, OPEN_ENDED, trust-boundary
2. STEP 0.5 (текст): краткий brief пользователю
3. FIRST tool call: Task(orchestrator) с ORIGINAL_REQUEST дословно
```

**Шаблон brief** (3–6 строк):

```markdown
**Понял задачу:** {restate objective}
**Режим:** {single_wave|until_user_stop} · OPEN_ENDED: {yes|no} · волна: {N}
**План волны:** {orchestrator → specialists hint}
**Дальше:** делегирую orchestrator с ORIGINAL_REQUEST дословно.
```

> **Терминология:** `Task(orchestrator)` (Cursor) и `delegate to orchestrator` (Hermes `delegate_task`) — эквивалентны для FIRST_ACTION и STEP 0.5.

| При активном DUA (`/start`, императив) | Запрещено |
|---|---|
| Brief + `Task(orchestrator)` в **одном** turn | Turn только с brief, ожидание «ок?» |
| Немедленное делегирование после brief | Ambiguity gate с паузой перед Task |
| Brief = текст/reasoning | Любой tool call до Task(orchestrator) |
| Restate objective в brief | Подмена или сокращение `ORIGINAL_REQUEST` в prompt orchestrator |

**Invariant:** STEP 0.5 не ослабляет FIRST_ACTION — это не extra hop, не pre-flight Read, не approval gate. При DUA Medium-tier «уточнить перед стартом» **не блокирует** STEP 0.5 + `Task(orchestrator)`: зафиксировать допущения в inline brief и делегировать в том же turn.

## ORIGINAL_REQUEST supremacy

`ORIGINAL_REQUEST` в контракте для orchestrator — **дословный текст** запроса пользователя.

| Разрешено | Запрещено |
|---|---|
| Brief перефразирует цель **для пользователя** | Переписывать `ORIGINAL_REQUEST` своими словами |
| `OBJECTIVE` сформулировать из запроса | Сокращать, summarize или менять intent в `ORIGINAL_REQUEST` |
| Дословная передача в prompt orchestrator | Подмена objective в поле `ORIGINAL_REQUEST` |

Brief и `ORIGINAL_REQUEST` — **разные поля**: brief = user-facing restatement; `ORIGINAL_REQUEST` = verbatim payload для orchestrator.

## Правильная цепочка

```text
user
  -> /start
  -> start (supervisor)
     -> STEP 0 (reasoning, no tools)
     -> STEP 0.5 (inline brief, same turn)
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

### Relay-семантика (continuation между волнами)

| Термин | Роль |
|--------|------|
| `resume_packet` | Runtime output: payload, который волна эмитит при паузе и ожидании продолжения |
| `CONTINUATION_PACKET` | Input view того же payload — root `start` передаёт его во вход следующего `Task(orchestrator, ...)` |
| `relay_resume` envelope | Формат handoff для продолжения после предыдущей волны (альтернативная обёртка для `CONTINUATION_PACKET`) |

`resume_packet` и `CONTINUATION_PACKET` — **не два разных state**, а output/input представления одной continuation-нагрузки (см. `docs/start-workflow.md`).

**Relay при паузе (не стоп для 24/7):**

- `status: pause` с `pause_reason: RELAY_REQUIRED` — **не** hard stop; root-start проксирует payload и продолжает цикл.
- Deprecated aliases (`done`, `continue`, `relay_required`) допустимы только на входе для совместимости и нормализуются в канон до следующей волны.

**Relay при недоступном nested `Task()` (orchestrator runtime):**

- Если orchestrator не может вызвать `Task()` → возвращает `ORCHESTRATOR_RELAY_REQUEST` родителю (`rules/orchestrator.mdc` §0.1.3).
- **Запрещён** fallback на Read/Shell вместо relay — это `MULTI_AGENT_PIPELINE_BLOCKED` semantics, не single-agent execution.

## Вложенные сабагенты

| В чате пользователь написал | Внутри оркестратора |
|----|---|
| `/code` … | `Task(subagent_type="code", prompt="…")` |
| `/test-specialist` … | `Task(subagent_type="test-specialist", prompt="…")` |
| `/orchestrator` … | `Task(subagent_type="orchestrator", prompt="…")` |

## Allowed / Forbidden

| Сценарий | Статус | Комментарий |
|----------|--------|-------------|
| root `start` → STEP 0.5 brief + `Task(orchestrator)` в одном turn | **Allowed** | DUA-safe: brief не tool call |
| root `start` → `Task(orchestrator)` | **Allowed** | Канонический путь |
| root `start` → brief-only turn, ожидание подтверждения | **Forbidden** | Блокирующая пауза при DUA `/start` |
| root `start` → `Task(start, worker)` | **Forbidden** | Лишний hop — flat chain only |
| root `start` → `Task(code\|debug)` | **Forbidden** | Только через orchestrator |
| orchestrator → `Task(code\|debug\|...)` | **Allowed** | Основная модель |
| specialist → `Task(...)` для подзадач | **Allowed** | Mandatory SWARM |
| same-type с более узким scope | **Allowed** | Fingerprint отличается, depth <= 3 |
| same-type с тем же fingerprint | **Forbidden** | Loop |
| Изменение `ORIGINAL_REQUEST` в prompt orchestrator | **Forbidden** | ORIGINAL_REQUEST supremacy |

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

- `agents/start.md` — STEP 0 / STEP 0.5, ORIGINAL_REQUEST, relay pause handling.
- `docs/start-workflow.md` — operator runbook (PBI-002 canonical sequence).
- `skills/start-workflow/SKILL.md` — архитектура flat chain и DUA carve-out.
- `agents/orchestrator.md` — orchestrator agent.
- `rules/orchestrator.mdc` — правила оркестрации (§0.1.3 relay, §0.6.1 STEP 0.5 / FIRST_ACTION).
