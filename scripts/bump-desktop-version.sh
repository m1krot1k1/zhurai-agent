#!/usr/bin/env bash
# bump-desktop-version.sh minor|major
# Синхронно поднимает version в apps/desktop/package.json, pyproject.toml, hermes_cli/__init__.py
set -euo pipefail

KIND="${1:-}"
if [[ "${KIND}" != "minor" && "${KIND}" != "major" ]]; then
  echo "Использование: $0 minor|major" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="${ROOT}/apps/desktop/package.json"
PYPROJECT="${ROOT}/pyproject.toml"
INIT_PY="${ROOT}/hermes_cli/__init__.py"

NEW_VERSION="$(python3 - "${KIND}" "${PKG}" "${PYPROJECT}" "${INIT_PY}" <<'PY'
import json, re, sys
from pathlib import Path

kind, pkg_path, pyproject_path, init_path = sys.argv[1:5]

with open(pkg_path, encoding="utf-8") as f:
    data = json.load(f)
parts = [int(x) for x in data["version"].split(".")]
major, minor, patch = (parts + [0, 0, 0])[:3]
if kind == "minor":
    major, minor, patch = major, minor + 1, 0
else:
    major, minor, patch = major + 1, 0, 0
new_v = f"{major}.{minor}.{patch}"

data["version"] = new_v
with open(pkg_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

pyproject = Path(pyproject_path)
text = pyproject.read_text(encoding="utf-8")
text, n = re.subn(r'(?m)^version = "[^"]+"', f'version = "{new_v}"', text, count=1)
if n != 1:
    raise SystemExit(f"failed to bump version in {pyproject_path}")
pyproject.write_text(text, encoding="utf-8")

init_py = Path(init_path)
itext = init_py.read_text(encoding="utf-8")
itext, n2 = re.subn(
    r'__version__\s*=\s*"[^"]+"',
    f'__version__ = "{new_v}"',
    itext,
    count=1,
)
if n2 != 1:
    raise SystemExit(f"failed to bump __version__ in {init_path}")
init_py.write_text(itext, encoding="utf-8")

print(new_v)
PY
)"

echo "${NEW_VERSION}"
