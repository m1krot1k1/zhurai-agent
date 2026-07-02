#!/usr/bin/env python3
"""Validate UTF-8 encoding hygiene for core policy text files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = ("rules", "agents", "skills")
TEXT_SUFFIXES = {".md", ".mdc"}
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# Common mojibake fragments from UTF-8 text decoded/stored through the wrong codec.
MOJIBAKE_TOKENS = (
    "\ufffd",  # replacement character
    "\u00c2",  # Â
    "\u00c3",  # Ã
    "\u00d0",  # Ð
    "\u00d1",  # Ñ
    "\u00e2\u20ac\u201c",  # â€œ
    "\u00e2\u20ac\u201d",  # â€�
    "\u00e2\u20ac\u02dc",  # â€˜
    "\u00e2\u20ac\u2122",  # â€™
    "\u00e2\u20ac\u00a6",  # â€¦
    "\u0420\u045f",  # Рџ
    "\u0420\u0451",  # Рё
    "\u0420\u00b0",  # Р°
    "\u0421\u201a",  # С‚
    "\u0421\u2039",  # С‹
    "\u0421\u0451",  # Сё
)


def iter_policy_files() -> list[Path]:
    files: list[Path] = []
    for rel_dir in TARGET_DIRS:
        root = ROOT / rel_dir
        if not root.exists():
            continue
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix in TEXT_SUFFIXES
        )
    return sorted(files)


def decode_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_encoding_issues(text: str) -> list[str]:
    hits = [token for token in MOJIBAKE_TOKENS if token in text]
    if CONTROL_CHAR_RE.search(text):
        hits.append("CONTROL_CHAR")
    return hits


def main() -> int:
    files = iter_policy_files()
    if not files:
        print("Policy encoding check failed:", file=sys.stderr)
        print("- No core policy files found under rules/, agents/, skills/.", file=sys.stderr)
        return 1

    failures: list[str] = []
    checked = 0

    for path in files:
        rel_path = path.relative_to(ROOT).as_posix()
        try:
            text = decode_utf8(path).lstrip("\ufeff")
        except UnicodeDecodeError as exc:
            failures.append(
                f"[decode] {rel_path}: file is not valid UTF-8 ({exc.reason} at byte {exc.start})",
            )
            continue

        checked += 1
        hits = find_encoding_issues(text)
        if hits:
            failures.append(f"[mojibake] {rel_path}: suspicious tokens {', '.join(hits)}")

    if failures:
        print("Policy encoding check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Policy encoding check passed.")
    print(f"- Checked files: {checked}")
    print("- Roots: rules/, agents/, skills/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
