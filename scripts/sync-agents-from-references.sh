#!/usr/bin/env bash
# Sync runtime agents/ from canonical references/agents/ (Hermes-oriented briefs).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/skills/multi-agent-ecosystem/references/agents"
DEST="${ROOT}/agents"

if [[ ! -d "${SRC}" ]]; then
  echo "missing source: ${SRC}" >&2
  exit 1
fi

mkdir -p "${DEST}"

count=0
for f in "${SRC}"/*.md; do
  base="$(basename "${f}")"
  if [[ "${base}" == "README.md" ]]; then
    continue
  fi
  cp "${f}" "${DEST}/${base}"
  count=$((count + 1))
done

echo "synced ${count} agent briefs: ${SRC} -> ${DEST}"
