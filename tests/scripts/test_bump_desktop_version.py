"""Tests for scripts/bump-desktop-version.sh — the single mutator of 4 version
files (apps/desktop/package.json, pyproject.toml, hermes_cli/__init__.py,
acp_registry/agent.json).

A drift between any of those four is the classic release bug: the ACP
registry manifest pins ``hermes-agent[acp]==X`` while pyproject ships
``X+1``, and the upstream registry CI rejects the build. The bump script
is the only place that keeps them in lockstep, so this test exercises it
end-to-end against a temp tree seeded at a known version and asserts that
all four files land on the same new version and that the resulting
agent.json is a valid manifest whose ``uvx.package`` pin matches.

Note: the script computes ``ROOT`` from its own path (``$(dirname
"$0")/..``), so running it against a temp tree requires chdir-ing into a
copy of the repo with the script in place. We make a minimal fake repo
root and invoke the script via its absolute path so ``$0`` resolves
correctly to the real script file under the source tree.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "bump-desktop-version.sh"


def _make_fake_repo(tmp_path: Path, version: str) -> Path:
    """Build a minimal mirror of the four files the script touches, rooted
    at ``tmp_path``. The script computes paths as ``$ROOT/apps/desktop/...``
    etc., so it operates on whatever tree we point it at — as long as the
    four files exist with the shape it expects.
    """
    root = tmp_path

    # apps/desktop/package.json — version field, JSON-shaped.
    desktop_dir = root / "apps" / "desktop"
    desktop_dir.mkdir(parents=True)
    (desktop_dir / "package.json").write_text(
        json.dumps(
            {"name": "hermes-desktop", "version": version, "private": True},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # pyproject.toml — single ``version = "X"`` line.
    (root / "pyproject.toml").write_text(
        '[project]\nname = "hermes-agent"\nversion = "'
        + version
        + '"\n',
        encoding="utf-8",
    )

    # hermes_cli/__init__.py — ``__version__ = "X"``.
    init_dir = root / "hermes_cli"
    init_dir.mkdir()
    (init_dir / "__init__.py").write_text(
        f'__version__ = "{version}"\n__release_date__ = "2026-01-01"\n',
        encoding="utf-8",
    )

    # acp_registry/agent.json — version + uvx package pin.
    agent_dir = root / "acp_registry"
    agent_dir.mkdir()
    (agent_dir / "agent.json").write_text(
        json.dumps(
            {
                "id": "hermes-agent",
                "name": "Hermes Agent",
                "version": version,
                "description": "test fixture",
                "distribution": {
                    "uvx": {
                        "package": f"hermes-agent[acp]=={version}",
                        "args": ["hermes-acp"],
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def _run_bump(root: Path, kind: str) -> subprocess.CompletedProcess:
    """Invoke the real bump-desktop-version.sh with ROOT pointed at ``root``.

    The script hard-codes ``ROOT="$(cd "$(dirname "$0")/.." && pwd)"``, so
    to operate on our fake tree we drop a symlink to the real script at
    ``<root>/scripts/bump-desktop-version.sh``. Then ``$(dirname "$0")/..``
    resolves to ``root`` and the script's fixed paths land on our fixture.
    This exercises the real script text, not a re-implementation.
    """
    scripts_dir = root / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    link = scripts_dir / "bump-desktop-version.sh"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(SCRIPT)

    env = dict(os.environ)
    # Make sure the same python3 the test runner uses is on PATH; the
    # script invokes ``python3`` directly to do the JSON/TOML mutation.
    env["PATH"] = os.path.dirname(sys.executable) + ":" + env.get("PATH", "")

    proc = subprocess.run(
        ["bash", str(link), kind],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc


def _assert_all_at(root: Path, version: str) -> None:
    pkg = json.loads((root / "apps" / "desktop" / "package.json").read_text("utf-8"))
    assert pkg["version"] == version, f"package.json version != {version!r}"

    pyproject = (root / "pyproject.toml").read_text("utf-8")
    assert f'version = "{version}"' in pyproject, (
        f"pyproject.toml missing 'version = \"{version}\"'"
    )

    init_py = (root / "hermes_cli" / "__init__.py").read_text("utf-8")
    assert f'__version__ = "{version}"' in init_py, (
        f"__init__.py missing '__version__ = \"{version}\"'"
    )

    agent = json.loads((root / "acp_registry" / "agent.json").read_text("utf-8"))
    assert agent["version"] == version, f"agent.json version != {version!r}"
    expected_pin = f"hermes-agent[acp]=={version}"
    assert agent["distribution"]["uvx"]["package"] == expected_pin, (
        f"agent.json uvx.package != {expected_pin!r}; "
        f"got {agent['distribution']['uvx']['package']!r}"
    )


def test_minor_bump(tmp_path):
    """minor: 0.37.0 → 0.38.0 across all 4 files; agent.json stays valid JSON
    and the uvx pin matches the new version.
    """
    if shutil.which("bash") is None:
        pytest.skip("bash not available")

    root = _make_fake_repo(tmp_path, "0.37.0")
    proc = _run_bump(root, "minor")

    assert proc.returncode == 0, (
        f"bump-desktop-version.sh minor failed:\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    new_v = proc.stdout.strip().splitlines()[-1]
    assert new_v == "0.38.0", f"expected 0.38.0, got {new_v!r}"
    _assert_all_at(root, "0.38.0")


def test_major_bump(tmp_path):
    """major: 0.38.0 → 1.0.0 across all 4 files."""
    if shutil.which("bash") is None:
        pytest.skip("bash not available")

    root = _make_fake_repo(tmp_path, "0.38.0")
    proc = _run_bump(root, "major")

    assert proc.returncode == 0, (
        f"bump-desktop-version.sh major failed:\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    new_v = proc.stdout.strip().splitlines()[-1]
    assert new_v == "1.0.0", f"expected 1.0.0, got {new_v!r}"
    _assert_all_at(root, "1.0.0")


def test_invalid_kind_rejects(tmp_path):
    """A kind other than minor|major must exit non-zero and print usage.
    Protects the script from silently bumping to a bogus version when
    someone fat-fingers the argument (e.g. ``bump-desktop-version.sh patch``).
    """
    if shutil.which("bash") is None:
        pytest.skip("bash not available")

    root = _make_fake_repo(tmp_path, "0.37.0")
    proc = _run_bump(root, "patch")

    assert proc.returncode != 0, (
        f"expected non-zero exit for invalid kind 'patch', got 0.\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    # None of the files should have moved.
    _assert_all_at(root, "0.37.0")


def test_lockstep_across_minor_then_major(tmp_path):
    """Idempotency-ish: bump minor then major and assert the final state is
    consistent. Catches a regression where the second invocation picks up
    a stale version from one of the four files (e.g. the script forgets
    to re-read agent.json).
    """
    if shutil.which("bash") is None:
        pytest.skip("bash not available")

    root = _make_fake_repo(tmp_path, "0.37.0")
    p1 = _run_bump(root, "minor")
    assert p1.returncode == 0, p1.stderr
    _assert_all_at(root, "0.38.0")
    p2 = _run_bump(root, "major")
    assert p2.returncode == 0, p2.stderr
    _assert_all_at(root, "1.0.0")
