# Delegation Exporter

Безопасный способ вытащить **delegation tree** из Cursor/Codex без локально-захардкоженных путей, workspace hash и UUID.

Инструмент:
- читает `state.vscdb` как **SQLite**, а не как сырые байты;
- берёт только нужные ключи (`composer.composerData`, `workbench.backgroundComposer.workspacePersistentData`);
- умеет работать либо с live Cursor workspace storage, либо с экспортированным `composer.composerData` JSON;
- по умолчанию **не печатает абсолютные пути проекта**; для этого нужен явный флаг `--show-paths`.

Основной CLI:
- `scripts/export-delegation-tree.sh`
- `scripts/export-delegation-tree.ps1`
- `scripts/export-delegation-tree.py`

## Основные режимы

Показать доступные Cursor workspaces:

```bash
scripts/export-delegation-tree.sh --list-workspaces
```

Построить дерево для наиболее подходящего workspace:

```bash
scripts/export-delegation-tree.sh --format text
```

Явно выбрать workspace:

```bash
scripts/export-delegation-tree.sh --workspace-id 49e4d06b31559bc099fc4f14667d1229 --format markdown
```

Показать полные пути проекта:

```bash
scripts/export-delegation-tree.sh --workspace-id 49e4d06b31559bc099fc4f14667d1229 --show-paths
```

Выгрузить machine-readable JSON:

```bash
scripts/export-delegation-tree.sh --workspace-id 49e4d06b31559bc099fc4f14667d1229 --format json > delegation-tree.json
```

Построить дерево из экспортированного fixture/JSON без доступа к Cursor DB:

```bash
scripts/export-delegation-tree.sh --composer-data benchmarks/exporter-fixtures/sample-composer-data.json --format json --all-roots
```

## Что экспортируется

Для каждой вершины exporter показывает:
- `composerId`
- имя ветки/задачи
- agent type (`start`, `orchestrator`, `code`, ...)
- parent/root request IDs, если они есть
- `contextUsagePercent`
- `totalLinesAdded`, `totalLinesRemoved`, `filesChangedCount`
- branch metadata
- краткий `subtitle`

По умолчанию exporter:
- исключает `archived` вершины;
- показывает только `unifiedMode=agent`, чтобы не засоряться обычными chat-root записями;
- если root явно не указан, выбирает **самый свежий root tree**.

## Почему это безопаснее старых extract-скриптов

Старые ad-hoc `extract-*.js` были рискованны, потому что:
- читали `state.vscdb` как текстовый blob;
- были привязаны к конкретному `workspaceStorage/<id>/state.vscdb`;
- содержали зашитые request/root IDs;
- могли случайно вытекать в локальные артефакты с приватными путями.

Новый exporter:
- параметризован;
- воспроизводим;
- пригоден для CI smoke-check через committed fixture;
- не зависит от одного компьютера или одного конкретного запуска.
