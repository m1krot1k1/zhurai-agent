---
name: repo-task-proof-loop
description: "7-фазный цикл выполнения задачи с доказательствами: spec → build → evidence → verify → fix → re-verify → learnings."
requires: none
---

## ЦЕЛЬ

Выполнять задачи с полной прослеживаемостью: каждое действие подтверждено артефактом.

## КОГДА ИСПОЛЬЗОВАТЬ

- Задача требует документированного доказательства выполнения
- PBI с acceptance criteria
- Multi-agent task с несколькими исполнителями

## РАСПОЛОЖЕНИЕ АРТЕФАКТОВ

```
agent-tasks/<TASK_ID>/
  spec.md           # Зафиксированные требования (не меняется после freeze)
  evidence.md       # Документальные доказательства выполнения
  verdict.md        # Финальный вердикт Verifier
  problems.md       # Найденные проблемы (опционально)
  learnings.md      # Уроки для следующих задач
  shared-context.md # Общий контекст для всех агентов задачи
```

## 7 ФАЗ

| Фаза | Агент | Действие |
|------|-------|----------|
| 1 Spec Freeze | architect/start | Написать spec.md; заморозить |
| 2 Build | code/specialist | Реализовать по spec |
| 3 Evidence | code | Создать evidence.md с артефактами |
| 4 Verify | code-reviewer | Проверить AC против evidence |
| 5 Fix | code | Исправить найденное |
| 6 Re-verify | code-reviewer | Повторная проверка после фикса |
| 7 Learnings | orchestrator | Написать learnings.md |

**Правило**: spec.md не меняется после Фазы 1. Изменения требований  новый TASK_ID.

## МАППИНГ НА CURSOR-АГЕНТОВ

| Фаза | Cursor агент |
|------|-------------|
| Spec | `@architect` или `@start` |
| Build | `@code`, `@frontend-specialist`, `@database-specialist` |
| Evidence | `@code` (запускает тесты, фиксирует вывод) |
| Verify | `@code-reviewer` |
| Fix | исходный исполнитель |
| Re-verify | `@code-reviewer` |
| Learnings | `@orchestrator` |

## ПРОМПТ-ШАБЛОН

```
Task(repo-task-proof-loop, "
  TASK_ID: {ID}
  PHASE: {1-7}
  SPEC: agent-tasks/{ID}/spec.md
  EVIDENCE_TARGET: agent-tasks/{ID}/evidence.md
  ACCEPTANCE_CRITERIA: [список]
  STOP_WHEN: все AC в evidence.md
")
```

## ОГРАНИЧЕНИЯ ПЛАТФОРМЫ

- Cursor не выполняет реальные bash команды вне одобренного shell
- Evidence = скриншоты / вывод тестов / диффы файлов, не только "выполнено"
- spec.md после freeze  read-only

## ЧЕКЛИСТ

- [ ] spec.md заморожен перед началом Build
- [ ] evidence.md содержит конкретные артефакты (не prose)
- [ ] Verifier проверял по AC из spec.md, не по памяти
- [ ] Fix  Re-verify цикл выполнен
- [ ] learnings.md написан
