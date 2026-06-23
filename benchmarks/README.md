# Benchmarks

Этот каталог хранит два слоя проверок для agent-system repository:

- **behavioral contract benchmarks**: проверяют, что критичные контракты явно зафиксированы в prompts/rules;
- **transcript benchmarks**: проверяют живые или fixture-транскрипты на anti-loop, root start routing, ownership safety, fan-out policy и честность runtime-degradation.

Идея:
- валидировать не только структуру файлов, но и наличие ключевых поведенческих контрактов в prompts/rules;
- ловить регрессии маршрутизации, same-type delegation, parallel ownership, transcript safety, fake-orchestration without `Task` и optional profiles;
- запускаться локально и в CI без внешнего LLM runtime.

Слои:
- `behavior-contracts.json` — статические контракты ядра.
- `transcript-cases.json` — fixture-suite для evaluator'а живых прогонов.
- `transcript-fixtures/` — минимальные pass/fail транскрипты для CI.

Локальный запуск:
- `scripts/run-behavior-benchmarks.sh`
- `scripts/evaluate-transcript-runs.sh`
- `scripts/evaluate-transcript-runs.sh chat/result.json`
- `scripts/evaluate-transcript-runs.sh chat/`
- `scripts/run-full-repo-benchmark.sh` (канонический полный цикл)
- `scripts/run-full-repo-benchmark.sh --check-mirror` (добавляет проверку drift для `.cursor/**` при необходимости)

Ограничение:
- transcript evaluator опирается на явные orchestration-сигналы (`Task(...)`, `OWNERSHIP`, `/start`, `analyzer`) и поэтому не заменяет полноценный runtime scoring качества модели;
- если в export нет agent-сигналов, evaluator помечает файл как `skipped`, а не придумывает выводы из шумного чата.

## Сценарии behavior-contracts.json

| ID | Что проверяет |
|----|---------------|
| `start_single_hop` | Root start делегирует **напрямую** в orchestrator. Worker-start убран из активной цепочки как legacy hop; forbidden: прямые вызовы специалистов из root start |
| `start_relay_mode_documented` | RELAY_MODE задокументирован в start.md для случая, когда Task недоступен |
| `orchestrator_child_relay_documented` | ORCHESTRATOR_RELAY_REQUEST задокументирован в orchestrator.md |
| `orchestrator_never_self_executes` | Orchestrator остаётся coordinator-only: self-exec запрещён, `.plan/**` и merge идут через delegated writer/git path |
| `same_type_delegation_enabled` | Явное разрешение same-type delegation с narrower scope в правилах |
| `parallel_writer_safety` | Контракты параллельной записи в разные файлы задокументированы |
| `large_same_type_fanout_escalates` | Fan-out >6 веток → обязателен суб-оркестратор |
| `ownership_and_dependencies_in_contracts` | OWNERSHIP и DEPENDENCIES поля задокументированы в envelope-контрактах |
| `optional_profile_isolated` | Profile-специфичные агенты изолированы от core |
| `council_for_core_rule_changes` | Изменения core-правил требуют council-process |
| `task_unavailable_blocks_or_marks_degraded` | Отсутствие Task → HARD FAIL или явный SINGLE_AGENT_DEGRADED_MODE |
| `degraded_mode_forbidden_for_start_swarm_open_ended` | DEGRADED_MODE запрещён при /start, swarm, 24/7, open-ended |
| `autonomous_self_improvement_loop_documented` | Спираль самоулучшения задокументирована |
| `swarm_supervisor_mode_documented` | Supervisor B0-mode задокументирован |
| `open_ended_until_stop_cannot_stop_on_micro_packet` | open-ended режим: нельзя останавливаться на micro-packet без steady_state |
| `canonical_runtime_contour_documented` | Новый contour `approval|pause|blocked|resume`, pair `approval_state/execution_state` и перевод `resume_packet -> CONTINUATION_PACKET` зафиксированы статически |
| `coding_guardrails_documented` | Coding-layer фиксирует anti-overengineering guardrails: явные assumptions, simplest diff, surgical changes и goal-driven verification |
| `mandatory_web_before_implementation_and_council` | Обязательный web-поиск перед имплементацией задокументирован |
| `start_full_force_completion_hardening` | FULL_FORCE_START_PROFILE completion-hardening задокументирован |
| `agent_registry_completeness` | Реестровые и управляющие агенты упомянуты в specialists.mdc и agents/README.md |
| `branch_count_cap_before_suborchestrator` | Правило cap ограничения веток до 6 закреплено |
| `vcs_preflight_cross_platform` | Скрипты preflight существуют для всех трёх платформ (.sh/.py/.ps1) |
| `profile_isolation_enforced` | Profile-агенты НЕ присутствуют в core agents/ и rules/ |

