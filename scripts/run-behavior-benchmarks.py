#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIO_FILE = ROOT / "benchmarks" / "behavior-contracts.json"


def read_text_robust(
    path: Path,
    encodings: tuple[str, ...] = (
        "utf-8",
        "utf-8-sig",
        # Cyrillic legacy encodings
        "cp866",
        "koi8-r",
        "koi8-u",
        "mac-cyrillic",
        "iso-8859-5",
        # Windows-125x fallbacks
        "cp1251",
        "cp1252",
    ),
) -> str:
    """
    Robust text reader for validators/benchmarks.

    Some markdown files may be saved in legacy encodings; benchmark must not crash
    due to UnicodeDecodeError.
    """
    last_exc: UnicodeDecodeError | None = None
    for enc in encodings:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError as e:
            last_exc = e
            continue
    if last_exc is not None:
        return path.read_text(encoding="utf-8", errors="replace")
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path) -> dict:
    return json.loads(read_text_robust(path))


def read(path: Path) -> str:
    return read_text_robust(path)


def main() -> int:
    data = load_json(SCENARIO_FILE)
    scenarios = data.get("scenarios", [])
    failures: list[str] = []
    passed = 0

    for scenario in scenarios:
        scenario_failures: list[str] = []
        scenario_id = scenario["id"]

        for rel_path in scenario.get("required_paths", []):
            if not (ROOT / rel_path).exists():
                scenario_failures.append(f'missing required path "{rel_path}"')

        for rel_path in scenario.get("missing_paths", []):
            if (ROOT / rel_path).exists():
                scenario_failures.append(f'path should be absent in core "{rel_path}"')

        for check in scenario.get("required_regex", []):
            rel_path = check["file"]
            pattern = check["pattern"]
            path = ROOT / rel_path
            if not path.exists():
                scenario_failures.append(f'missing file for regex check "{rel_path}"')
                continue
            if not re.search(pattern, read(path), re.DOTALL):
                scenario_failures.append(f'pattern not found in {rel_path}: /{pattern}/')

        for check in scenario.get("forbidden_regex", []):
            rel_path = check["file"]
            pattern = check["pattern"]
            path = ROOT / rel_path
            if not path.exists():
                continue
            if re.search(pattern, read(path), re.DOTALL):
                scenario_failures.append(f'forbidden pattern found in {rel_path}: /{pattern}/')

        if scenario_failures:
            failures.append(f'[{scenario_id}] ' + "; ".join(scenario_failures))
        else:
            passed += 1

    if failures:
        print("Behavior benchmarks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Behavior benchmarks passed.")
    print(f"- Scenarios: {passed}")
    print(f"- Spec: {SCENARIO_FILE.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
