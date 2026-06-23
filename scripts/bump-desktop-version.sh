#!/usr/bin/env bash
# bump-desktop-version.sh minor|major
# Обновляет version в apps/desktop/package.json
set -euo pipefail

KIND="${1:-}"
if [[ "${KIND}" != "minor" && "${KIND}" != "major" ]]; then
  echo "Использование: $0 minor|major" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="${ROOT}/apps/desktop/package.json"

NEW_VERSION="$(python3 - "${KIND}" "${PKG}" <<'PY'
import json, sys
kind, path = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
parts = [int(x) for x in data["version"].split(".")]
major, minor, patch = (parts + [0, 0, 0])[:3]
if kind == "minor":
    major, minor, patch = major, minor + 1, 0
else:
    major, minor, patch = major + 1, 0, 0
new_v = f"{major}.{minor}.{patch}"
data["version"] = new_v
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(new_v)
PY
)"

echo "${NEW_VERSION}"
