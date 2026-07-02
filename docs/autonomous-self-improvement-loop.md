# Автономная спираль самоулучшения (agent-system repo)

Документ задаёт **канонический** способ «крутить по кругу» улучшение **этого** репозитория (конфигурация агентов), **без** участия пользователя на каждом микрошаге и **без** запрещённой конструкции **`start → start`**.

## Что вы хотите получить

| Желание | Как это реализовано в системе |
|--------|--------------------------------|
| Система сама анализирует, всё ли отработало | После **Verify** оркестратор вызывает **`start` только как analyzer** (текстовый вердикт по AC + артефактам). См. [autonomous-task-with-verification.md](./autonomous-task-with-verification.md). |
| Пока не дотянем качество — правки и снова тесты | Цикл **Execute → Verify → Analyze → Rework** с **`rework_limit`** и anti-loop (`rules/orchestrator.mdc` §4, §8). |
| Не дергать человека в процессе | Исполнение ведёт **orchestrator**; пользователь дал задачу один раз. Ограничения **безопасности** (дестрой, секреты, high-privilege) из `rules/aleksander.mdc` остаются. |
| «Максимально лучше без предела» | **Не является** гарантией политики: сходимость только к **измеримым AC** и **бюджетам**; иначе эскалация или остановка с отчётом. |

## Что запрещено (и почему так лучше)

- **`Task(subagent_type="start")` от корневого `start`** **без** узко разрешённого режима — запрещён (второй «корневой» вход ломает thin-router и бенчмарки). **Устарело:** канонический supervisor→worker handoff `Task(start, ENTRY_MODE: supervised_worker)` — снят с цепочки; **текущий** путь: корневой `start` → **`Task(orchestrator)` напрямую**. Причина теперь архитектурная: flat-chain даёт меньше hop'ов, меньше drift и более прозрачную маршрутизацию, при этом вложенные subagent'ы всё ещё могут использовать `Task()` по своим правилам. См. [delegation-chain.md](./delegation-chain.md).
- **Полноценный второй `start` внутри дерева** вместо оркестратора — запрещён; маршрутизация поддерева = **`Task(orchestrator, …)`**.
- **Analyzer-вызов** `Task(subagent_type="start", …)` **из оркестратора** — **разрешён** и **единственный** поддерживаемый способ «start смотрит на результат» без нового `/start` в UI.

## Закрытая спираль (алгоритм для оркестратора)

Выполняйте **последовательно**; на каждой итерации должен быть **новый артефакт** (дифф, лог прогона, явный отчёт), иначе срабатывает anti-loop.

### 0. Конверт (один раз)

Зафиксируйте в execution envelope:

- **OBJECTIVE**: что улучшаем (например: «усилить автономный цикл и проверки»).
- **AC** (измеримые): например  
  - `python3 scripts/run-full-repo-benchmark.py` → exit 0  
  - нет регрессий в transcript/behavior benchmarks  
  - изменения только в согласованных путях (см. ниже).
- **`rework_limit`**: например **3** полных цикла Verify→Analyze→Rework на один и тот же класс зазоров.
- **NON-GOALS**: не трогать вложенное зеркало `**/.cursor/**` как канон, если пользователь запретил; не ослаблять security-инварианты.

### 0.5. VCS pre-flight на КАЖДУЮ итерацию

Перед любым новым циклом правок выполните:

```bash
BASE_BRANCH="${BASE_BRANCH:-dev}"
git fetch --all --prune
git rev-list --left-right --count "origin/${BASE_BRANCH}...HEAD"
git status --short --branch
```

Или используйте готовый helper:

```bash
./scripts/iteration-vcs-preflight.sh
./scripts/iteration-vcs-preflight.sh --sync
```

Дальше:

1. Если дерево **чистое** и `origin/${BASE_BRANCH}...HEAD = 0 0`, допускается синхронизация через:
   - `git pull --rebase origin ${BASE_BRANCH}`
   - если команда падает из-за локальной multi-merge конфигурации, fallback: `git rebase origin/${BASE_BRANCH}`
2. Если дерево **чистое**, но есть расхождение:
   - `0 N` (локальная ветка ahead) → pull/rebase не нужен, продолжайте итерацию;
   - `N 0` (локальная ветка behind) → обязательно `git rebase origin/${BASE_BRANCH}` до любых правок;
   - `N M` (diverged) → остановка автоматической итерации и эскалация пользователю (или отдельный согласованный merge/rebase plan).
3. Если дерево **грязное**, pull/rebase не выполнять до завершения текущей итерации.
4. Запрещены destructive-операции (`reset --hard`, `push --force`, удаление истории).

### 1. Baseline (перед правками)

Запустите агрегатор (или отдельные шаги):

```bash
./scripts/run-full-repo-benchmark.sh
```

Сохраните вывод как **доказательство** baseline (в completion contract ветки).
Если `.sh` недоступен в текущей среде, используйте fallback:

```bash
python3 scripts/run-full-repo-benchmark.py
```

### 2. Execute

Ветки с явным **OWNERSHIP** (правила / агенты / skills / docs / scripts — по домену). Для правок `rules/*.mdc` при необходимости **Council §17** (`rules/orchestrator.mdc`).

### 3. Verify

- `code-reviewer` / `security-auditor` по диффу ядра (где уместно).
- Повторный прогон benchmark: сначала `./scripts/run-full-repo-benchmark.sh`, при недоступности `.sh` — `python3 scripts/run-full-repo-benchmark.py`.

### 3.5. Web research evidence (обязательно для внешних фактов)

Если в итерации использовались внешние API/версии/безопасностные паттерны, в отчёт итерации добавляется блок `web_research`.

```yaml
web_research:
  status: used|not_needed|not_available|not_run
  ...  # canonical schema defined in rules/orchestrator.mdc §18 (Web evidence contract)
```

Каноническая схема и обязательные поля — только в `rules/orchestrator.mdc` §18, чтобы избежать drift между документами.
Если web research не требовался, это фиксируется явно: `status: not_needed` + причина.

### 4. Analyze (только так вызывается «второй start»)

Один вызов:

```text
Task(subagent_type="start", prompt="
ENTRY_MODE: analyzer_only
TRUSTED_POLICY: (вставить релевантные выдержки правил)
TASK_INPUT:
  DELIVERABLES: (список файлов / сценариев)
  ACCEPTANCE_CRITERIA: (как в конверте §0)
  EVIDENCE: (вывод команд, кратко)
ОЖИДАЕМЫЙ ВЫХОД: ровно «Выполнено» ИЛИ «Продолжить:» + нумерованные зазоры
")
```

**Запрещено** в этом вызове: новые `Task`, чтение репозитория, команды — см. `agents/start.md` ANALYZER MODE.

### 5. Rework

Если «Продолжить:» — только **таргетные** ветки на перечисленные зазоры → снова §3–§4.

### 6. Выход из спирали

- Analyzer вернул **«Выполнено»** с учётом evidence **или**
- Достигнут **`rework_limit`** **или**
- Требуется решение человека (продукт/безопасность/неоднозначный форк).

### 6.5. Commit / Push gate на итерацию

После успешного Verify:

1. `git status --short` — коммитить только при реальных изменениях.
2. Коммит-сообщение формулировать в языке, который задан контрактом итерации (например, RU при явном требовании пользователя).
3. Пуш только после успешного Verify:
   - `git push origin HEAD`
   - только при явном разрешении пользователя в текущей сессии (DUA) или при наличии заранее подтверждённого allowlist-правила в контракте.
4. После push — сразу следующая итерация, начиная снова с **§0.5 VCS pre-flight**.

## Связь с `.plan/`

Для длинных прогонов ведите `.plan/todos.md` / `session-context.md` по skill `project-plan-dot-plan`: итерация спирали, что поменялось, что ещё открыто.

## Шаблон AC для задачи «улучшить систему агентов»

Минимум:

1. `run-full-repo-benchmark.py` — **pass**.
2. Нет нарушений **core vs peripheral** для задач улучшения ядра (`rules/orchestrator.mdc` §13).
3. Делегирование: корневой путь **`/start` → `Task(orchestrator)`** сохранён; **нет** сценариев «fake orchestration» при отсутствии `Task`.

## См. также

- [autonomous-task-with-verification.md](./autonomous-task-with-verification.md) — роли Execute/Verify/Analyze/Rework.
- [delegation-chain.md](./delegation-chain.md) — допустимые и запрещённые вызовы `start`.
- `agents/orchestrator.md` — Phase 4b и практика цикла.
- `scripts/run-full-repo-benchmark.py` — единый прогон проверок.
