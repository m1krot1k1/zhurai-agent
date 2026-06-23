#!/usr/bin/env python3
"""Aggregate full-repo checks: validators, behavior/transcript benchmarks, exporter smoke (CI parity)."""

from __future__ import annotations

import json
import os
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent


def run_step(name: str, argv: list[str], extra_env: dict[str, str] | None = None) -> None:
    print(f"\n=== {name} ===\n", flush=True)
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    subprocess.run(argv, cwd=str(ROOT), check=True, env=env)


def exporter_smoke() -> None:
    print("\n=== Delegation exporter smoke (sample fixture) ===\n", flush=True)
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "export-delegation-tree.py"),
            "--composer-data",
            str(ROOT / "benchmarks" / "exporter-fixtures" / "sample-composer-data.json"),
            "--format",
            "json",
            "--all-roots",
        ],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert data["summary"]["selectedComposers"] == 5
    assert data["summary"]["agentCounts"]["orchestrator"] == 1
    assert data["roots"][0]["children"][0]["agent"] == "start"
    print("Delegation exporter smoke assertions passed.", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-mirror",
        action="store_true",
        help="Enable .cursor mirror drift warnings during validate-repo-consistency step.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print("run-full-repo-benchmark: repo root =", ROOT, flush=True)
    mirror_env = {"CHECK_CURSOR_MIRROR": "1"} if args.check_mirror else {"CHECK_CURSOR_MIRROR": "0"}
    if args.check_mirror:
        print("run-full-repo-benchmark: mirror drift check ENABLED", flush=True)
    else:
        print("run-full-repo-benchmark: mirror drift check skipped by default", flush=True)

    steps: list[tuple[str, list[str], dict[str, str] | None]] = [
        ("check-policy-encoding", [sys.executable, str(SCRIPT_DIR / "check-policy-encoding.py")], None),
        ("validate-agent-registry", [sys.executable, str(SCRIPT_DIR / "validate-agent-registry.py")], None),
        (
            "validate-repo-consistency",
            [sys.executable, str(SCRIPT_DIR / "validate-repo-consistency.py")],
            mirror_env,
        ),
        ("run-behavior-benchmarks", [sys.executable, str(SCRIPT_DIR / "run-behavior-benchmarks.py")], None),
        ("evaluate-transcript-runs", [sys.executable, str(SCRIPT_DIR / "evaluate-transcript-runs.py")], None),
    ]
    for name, argv, extra_env in steps:
        run_step(name, argv, extra_env=extra_env)
    exporter_smoke()
    print("\n=== run-full-repo-benchmark: OK ===\n", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
