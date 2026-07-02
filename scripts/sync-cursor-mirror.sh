#!/usr/bin/env bash
# Синхронизация runtime-зеркала .cursor/ из канонических директорий репозитория.
#
# Канон: agents/, rules/, skills/, docs/, scripts/ (корень репо)
# Зеркало: .cursor/agents/, .cursor/rules/, .cursor/skills/, .cursor/docs/, .cursor/scripts/
#
# Список директорий совпадает с MIRROR_SYNC_DIRS в scripts/validate-repo-consistency.py
# (когда скрипт появится в репозитории).
#
# Использование:
#   ./scripts/sync-cursor-mirror.sh           # синхронизация
#   ./scripts/sync-cursor-mirror.sh --dry-run # только показать rsync-команды
#
# После синхронизации (опционально):
#   CHECK_CURSOR_MIRROR=1 python3 scripts/validate-repo-consistency.py

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIRROR_ROOT="${ROOT}/.cursor"
DRY_RUN=0

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--dry-run]" >&2
  exit 1
fi

# Должен совпадать с MIRROR_SYNC_DIRS в validate-repo-consistency.py
MIRROR_SYNC_DIRS=(rules agents skills docs scripts)

mkdir -p "${MIRROR_ROOT}"

RSYNC_FLAGS=(-a --delete)
if [[ "${DRY_RUN}" -eq 1 ]]; then
  RSYNC_FLAGS+=(--dry-run --itemize-changes)
fi

synced=0
skipped=0

for dir in "${MIRROR_SYNC_DIRS[@]}"; do
  src="${ROOT}/${dir}"
  dest="${MIRROR_ROOT}/${dir}"

  if [[ ! -d "${src}" ]]; then
    echo "[skip] ${dir}/ — canonical directory missing" >&2
    skipped=$((skipped + 1))
    continue
  fi

  mkdir -p "${dest}"
  echo "[sync] ${dir}/ -> .cursor/${dir}/"
  rsync "${RSYNC_FLAGS[@]}" "${src}/" "${dest}/"
  synced=$((synced + 1))
done

echo "done: synced=${synced} skipped=${skipped} mirror=${MIRROR_ROOT}"
