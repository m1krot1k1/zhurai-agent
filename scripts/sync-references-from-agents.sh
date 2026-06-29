#!/usr/bin/env bash
# Sync canonical references/agents/ (Hermes-oriented briefs) from runtime agents/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/agents"
DEST="${ROOT}/skills/multi-agent-ecosystem/references/agents"

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
