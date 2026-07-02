---
name: project-plan-dot-plan
description: "Структура .plan/ директории: файлы, форматы, обновление, связь с оркестрацией."
requires: none
---

> **Reference doc** — loaded on-demand from `references/skills/`. Not a separate ZCode skill; use when the master `multi-agent-ecosystem` skill or an agent brief points here.


## ЦЕЛЬ

Фиксировать план работ, прогресс и контекст сессии в стандартной `.plan/` структуре.

## КОГДА ИСПОЛЬЗОВАТЬ

- Старт нового проекта или PBI
- Передача контекста между сессиями
- Долгосрочная задача с несколькими итерациями

## СТРУКТУРА .plan/

```
.plan/
  README.md           # Цель проекта, статус, ссылки
  todos.md            # Краткий список задач (сводка)
  todos_full.md       # Детализированный список с контекстом
  napravlenie-*.md    # По одному файлу на направление работ
```

**Обязательные файлы**: `README.md`, `todos.md`, `todos_full.md`.
**По необходимости**: `napravlenie-*.md` при двух и более направлениях.

## ФОРМАТЫ

| Поле | Формат |
|------|--------|
| Время / дата | ISO 8601: `2025-01-15T14:30:00` |
| Статус задачи | `TODO` / `IN_PROGRESS` / `DONE` / `BLOCKED` |
| Прогресс в README | `## PROGRESS [YYYY-MM-DD]` секция с кратким логом |

## ПРАВИЛА ОБНОВЛЕНИЯ

При каждой правке в `.plan/`:
1. Обновить `todos.md` — зачеркнуть выполненное.
2. Добавить запись в `README.md` в секцию `## PROGRESS`.
3. Если задача завершена — переместить её из `todos.md` в `todos_full.md` с датой.

**Никогда не удалять** строки из `todos_full.md` — это история прогресса.

## ШАБЛОНЫ

**README.md:**
```markdown
# [Название проекта]

## Цель
[Один абзац]

## Статус
[ACTIVE / PAUSED / DONE]

## Ключевые файлы
- `.plan/todos.md` — задачи
- [другие]

## PROGRESS
### [YYYY-MM-DD]
- [что сделано]
```

**todos.md:**
```markdown
## Активные задачи
- [ ] [задача 1]
- [x] [выполненная задача]

## Заблокированные
- [ ] [задача] — reason: [причина]
```

## СВЯЗЬ С ОРКЕСТРАЦИЕЙ

- `start` агент читает `.plan/todos.md` для восстановления контекста
- Orchestrator не пишет `.plan/napravlenie-*.md` сам; если нужен update `.plan/**`, он делегируется отдельной writer-ветке с OWNERSHIP только на `.plan/**`
- При `session continuity` — прочитать последние 3 записи из `README.md ## PROGRESS`

## НЕПРЕРЫВНЫЕ ВОЛНЫ (CONTINUOUS MODE)

Для циклов вида `CONTINUOUS_MODE=until_user_stop`:

1. После каждой волны добавить запись в `.plan/README.md` (`## PROGRESS`) с:
   - номером волны;
   - кратким итогом (`approval/pause/blocked`);
   - списком изменённых файлов или причиной отсутствия изменений.
2. Если волна завершилась `blocked`, зафиксировать:
   - `blocker_type` (`BLOCKED_RUNTIME`, `BLOCKED_POLICY`, `BLOCKED_INPUT`, `BLOCKED_EXTERNAL`, `BLOCKED_INTEGRATION`);
   - `resume_packet` (конкретное действие для следующей волны, если работа паузится, а не завершается).
3. Синхронизировать `.plan/todos.md` и `.plan/todos_full.md`:
   - активные задачи остаются в `todos.md`;
   - завершённые и заблокированные шаги переносятся в `todos_full.md` с датой.

Минимальный evidence-пакет на волну:
- изменённые пути файлов;
- проверка(и), запущенные в рамках волны;
- статус AC (`met/not_met`) и остаточные риски.

## ЧЕКЛИСТ

- [ ] README.md создан с Целью и Статусом
- [ ] todos.md актуален
- [ ] todos_full.md содержит историю
- [ ] PROGRESS обновлён в README.md
- [ ] ISO 8601 для всех дат
