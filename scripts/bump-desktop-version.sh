#!/usr/bin/env bash
# bump-desktop-version.sh minor|major
# Синхронно поднимает version в apps/desktop/package.json, pyproject.toml, hermes_cli/__init__.py, acp_registry/agent.json
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
AGENT_JSON="${ROOT}/acp_registry/agent.json"

NEW_VERSION="$(python3 - "${KIND}" "${PKG}" "${PYPROJECT}" "${INIT_PY}" "${AGENT_JSON}" <<'PY'
import json, re, sys
from pathlib import Path

kind, pkg_path, pyproject_path, init_path, agent_json_path = sys.argv[1:6]

SEMVER_RE = re.compile(r"\A\d+\.\d+\.\d+\Z")


def read_version_from_pkg(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return json.load(f)["version"]


def read_version_from_pyproject(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r'(?m)^version = "([^"]+)"', text)
    if not m:
        raise SystemExit(f"ERROR: no `version = ...` found in {path}")
    return m.group(1)


def read_version_from_init(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not m:
        raise SystemExit(f"ERROR: no __version__ found in {path}")
    return m.group(1)


def assert_semver(v: str, source: str) -> None:
    if not SEMVER_RE.match(v):
        raise SystemExit(
            f"ERROR: version in {source} must be MAJOR.MINOR.PATCH, got {v!r}"
        )


# Pre-flight: all 4 files must agree AND be valid semver before any mutation.
pkg_v = read_version_from_pkg(pkg_path)
pyproject_v = read_version_from_pyproject(pyproject_path)
init_v = read_version_from_init(init_path)
agent_v = read_version_from_pkg(agent_json_path)

for v, src in (
    (pkg_v, pkg_path),
    (pyproject_v, pyproject_path),
    (init_v, init_path),
    (agent_v, agent_json_path),
):
    assert_semver(v, src)

if not (pkg_v == pyproject_v == init_v == agent_v):
    raise SystemExit(
        "ERROR: version mismatch — sync manually first:\n"
        f"  package.json   = {pkg_v}\n"
        f"  pyproject.toml = {pyproject_v}\n"
        f"  __init__.py    = {init_v}\n"
        f"  agent.json     = {agent_v}"
    )

with open(pkg_path, encoding="utf-8") as f:
    data = json.load(f)
major, minor, patch = map(int, pkg_v.split("."))
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

agent_json = Path(agent_json_path)
adata = json.loads(agent_json.read_text(encoding="utf-8"))
adata["version"] = new_v
adata["distribution"]["uvx"]["package"] = f"hermes-agent[acp]=={new_v}"
with open(agent_json, "w", encoding="utf-8") as f:
    json.dump(adata, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(new_v)
PY
)"

echo "${NEW_VERSION}"
