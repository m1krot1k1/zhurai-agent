# Пример промпта для оркестратора: три голоса (Builder / Skeptic / Verifier)

Скопируйте и подставьте свою фичу. Запускайте из **`/orchestrator`** или это содержимое уйдёт в оркестратор через **`/start`** (start оборачивает в свой конверт).

Каждая реальная дочерняя **`Task(...)`** должна содержать все обязательные секции из **`rules/orchestrator.mdc` §3** (completeness gate). Ниже — **один** связный пример: общий конверт волны + три ветки с полным каркасом (значения в угловых скобках замените).

```text
=== ВОЛНА (родитель оркестратора; один конверт на сообщение) ===

OBJECTIVE: Реализовать <КРАТКО: фича> с проверкой и оспариванием дизайна; после волны — синтез и при зазорах rework только по списку.

SCOPE: Координация трёх веток B1–B3; согласование общего fact-pack; синтез результатов; обновление `.plan/todos.md` и `.plan/todos_full.md` при существенном прогрессе.

OUT_OF_SCOPE: Правки вне согласованных путей веток; расширение AC без явного согласования; коммит/пуш без успешной верификации, если это запрещено конвертом.

OWNERSHIP: Только файлы направления `.plan/**` и оркестрационный синтез ответа (ветки B1–B3 владеют своими целевыми путями кода/тестов согласно ниже).

DEPENDENCIES: none (B2/B3 могут быть after:B1, если Skeptic/Verifier должны видеть артефакт Builder — укажите явно).

STEPS:
1. Запустить §18 fact-ветку (или использовать уже готовый cited fact-pack) и раздать **одинаковый** fact-pack всем голосам.
2. В одном сообщении запустить три `Task(...)` (B1–B3), каждый с полным конвертом §3 (шаблоны ниже).
3. Синтезировать; при расхождении с AC — целевой rework.
4. При необходимости вызвать `start` как analyzer по `docs/autonomous-task-with-verification.md`.

DELIVERABLES:
- Сводка волны + статус AC1–AC2.
- Обновлённые `.plan/todos.md`, `.plan/todos_full.md` (если применимо).
- Ссылки/цитаты Evidence из веток.

ACCEPTANCE_CRITERIA:
- [ ] B1 закрыл AC1–AC2 артефактами в согласованных путях.
- [ ] B2 дал проверяемый список утверждений/рисков по границам AC (без «зелёных» тестов ценой порчи прод-логики).
- [ ] B3 дал PASS/FAIL по каждому AC с командами и фрагментом вывода или явным `not_run` + причина.

CRITICAL_UNKNOWNS: none

NON-NEGOTIABLE:
- Вы будете **PENALIZED** за запуск `Task(...)` без полного набора секций §3 в **каждой** дочерней ветке.
- Вы будете **PENALIZED** за заявление «готово» без evidence (пути, вывод команд, артефакты).
- Один и тот же §18 fact-pack для всех голосов; не делайте live web внутри раундов debate/council.

COMPLETION_CONTRACT:
- Вернуть: branch_id/statус, файлы, checks (pass/fail/not_run), AC met/not_met, confidence, unknowns, риски (схема `rules/orchestrator.mdc` §5).

BUDGET (из multi-pass-autonomy):
- MAX_PARALLEL_BRANCHES: 3
- MAX_DEBATE_ROUNDS: 2
- MAX_REWORK_AFTER_VERIFY: 2

PRE-IMPLEMENTATION FACT PASS:
- Перед Builder/Skeptic/Verifier запусти отдельную §18 fact-ветку и собери короткий cited fact-pack:
  - актуальные framework/library docs
  - version-specific caveats
  - security/best-practice notes, если релевантно
- Один и тот же fact-pack передай всем голосам; не делай live web внутри самих раундов debate/council.

=== B1 — Task(subagent_type="code", ...) ===
Branch ID: B0-1 | Level: 1 | DEPTH_BUDGET: 9

OBJECTIVE: Минимальный рабочий дифф по AC1–AC2 в согласованных путях.

SCOPE: <файлы реализации>

OUT_OF_SCOPE: <чужие модули / секреты / согласованные запреты>

OWNERSHIP: <точные glob/пути, только B1>

DEPENDENCIES: none

STEPS:
1. Прочитать согласованные файлы; реализовать по AC.
2. Запустить согласованные проверки (тесты/сборка); зафиксировать вывод.

DELIVERABLES: Изменённые файлы + краткий список команд и результатов.

ACCEPTANCE_CRITERIA:
- [ ] AC1 выполнен (измеримо: …)
- [ ] AC2 выполнен (измеримо: …)

CRITICAL_UNKNOWNS: none

NON-NEGOTIABLE:
- Вы будете **PENALIZED** за scope creep вне OWNERSHIP и за «done» без вывода проверок.

COMPLETION_CONTRACT: summary, files_changed, checks, AC status, evidence (§5).

Voice: Builder
Stop when: минимальный рабочий дифф по AC1–AC2 в согласованных путях файлов

=== B2 — Task(subagent_type="code-skeptic", ...) ===
Branch ID: B0-2 | Level: 1 | DEPTH_BUDGET: 9

OBJECTIVE: Оспорить допущения Builder, проверить границы AC и сценарии поломки.

SCOPE: Анализ артефактов B1 и/или спеки из конверта (если B2 параллельно B1 — только спека/план).

OUT_OF_SCOPE: Правки прод-кода «чтобы закрыть глаза»; подмена AC.

OWNERSHIP: Нет записи в репозиторий (read-only критика), если иное не согласовано.

DEPENDENCIES: after:B1 (если нужен дифф B1; иначе `none` + явно указать, что опора только на спеку).

STEPS:
1. Выписать проверяемые утверждения и риски.
2. Сопоставить с AC; отметить пробелы.

DELIVERABLES: Структурированный отчёт: утверждение → риск → что проверить.

ACCEPTANCE_CRITERIA:
- [ ] Есть список проверяемых утверждений и «что может сломаться».
- [ ] Нет правок прод-кода ради «зелёных» тестов без явного согласования.

CRITICAL_UNKNOWNS: none

NON-NEGOTIABLE:
- Вы будете **PENALIZED** за общие фразы без привязки к AC и артефактам.

COMPLETION_CONTRACT: summary, evidence (ссылки на файлы/фрагменты), AC coverage skeptical pass.

Voice: Skeptic
Stop when: список проверяемых утверждений + риски + «что может сломаться»; БЕЗ правок прод-кода ради «зелёных» тестов

=== B3 — Task(subagent_type="test-specialist"|"review", ...) ===
Branch ID: B0-3 | Level: 1 | DEPTH_BUDGET: 9

OBJECTIVE: Независимая верификация выполнения AC1–AC2.

SCOPE: Запуск согласованных команд / проверок на артефактах B1; учёт выводов B2 при необходимости.

OUT_OF_SCOPE: Переписывание фичи под результат; изменение AC.

OWNERSHIP: Только тестовые/вспомогательные файлы, если это явно разрешено конвертом; иначе read-only.

DEPENDENCIES: after:B1; после B2, если верификация должна учитывать риски.

STEPS:
1. Воспроизвести шаги проверки из AC.
2. Зафиксировать PASS/FAIL на каждый AC с выводом.

DELIVERABLES: Таблица AC × статус × команда × фрагмент вывода.

ACCEPTANCE_CRITERIA:
- [ ] PASS/FAIL по каждому AC с командами и выводом или `not_run` + причина.

CRITICAL_UNKNOWNS: none

NON-NEGOTIABLE:
- Вы будете **PENALIZED** за выставление PASS без воспроизводимого evidence.

COMPLETION_CONTRACT: summary, checks, AC table, evidence (§5).

Voice: Verifier
Stop when: отчёт PASS/FAIL по каждому AC с командами и выводом

После волны: синтез; при зазорах — rework только по списку; затем при необходимости вызов start как analyzer по docs/autonomous-task-with-verification.md.

Обнови .plan/todos.md и .plan/todos_full.md (таймстемп, ✅).
```

См. также: [multi-pass-autonomy SKILL](../skills/multi-pass-autonomy/SKILL.md), [autonomy-multi-voice.md](./autonomy-multi-voice.md), [agent-prompt-quality SKILL](../skills/agent-prompt-quality/SKILL.md) (обязательные секции §3).
