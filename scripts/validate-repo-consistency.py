#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR_ROOT = ROOT / ".cursor"
TEXT_EXTENSIONS = {
    ".md",
    ".mdc",
    ".py",
    ".sh",
    ".ps1",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
}

errors: list[str] = []
warnings: list[str] = []
CONFLICT_START = "<" * 7
CONFLICT_MID = "=" * 7
CONFLICT_END = ">" * 7
MIRROR_SYNC_DIRS = ("rules", "agents", "skills", "docs", "scripts")
MIRROR_CHECK_ENV = "CHECK_CURSOR_MIRROR"


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def read_text_robust(
    path: Path,
    encodings: Iterable[str] = (
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
    """Read text files with legacy encoding fallback.

    This keeps repository validators/benchmarks resilient to files not saved as UTF-8.
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


def read(rel_path: str) -> str:
    return read_text_robust(ROOT / rel_path)


def walk(rel_path: str) -> list[Path]:
    path = ROOT / rel_path
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    return [child for child in path.rglob("*") if child.is_file()]


for required_file in (
    "scripts/validate-agent-registry.py",
    "scripts/validate-agent-registry.sh",
    "scripts/validate-agent-registry.ps1",
    "scripts/validate-repo-consistency.py",
    "scripts/validate-repo-consistency.sh",
    "scripts/validate-repo-consistency.ps1",
    "scripts/iteration-vcs-preflight.sh",
    "scripts/run-behavior-benchmarks.py",
    "scripts/run-behavior-benchmarks.sh",
    "scripts/run-behavior-benchmarks.ps1",
    "scripts/evaluate-transcript-runs.py",
    "scripts/evaluate-transcript-runs.sh",
    "scripts/evaluate-transcript-runs.ps1",
    "scripts/export-delegation-tree.py",
    "scripts/export-delegation-tree.sh",
    "scripts/export-delegation-tree.ps1",
    "scripts/check-policy-encoding.py",
    "scripts/check-policy-encoding.sh",
    "scripts/check-policy-encoding.ps1",
    ".github/workflows/repo-validation.yml",
    "agent-tasks/README.md",
    "benchmarks/README.md",
    "benchmarks/behavior-contracts.json",
    "benchmarks/transcript-cases.json",
    "benchmarks/exporter-fixtures/sample-composer-data.json",
    "docs/delegation-exporter.md",
):
    if not (ROOT / required_file).exists():
        fail(f"[required] Missing required file {required_file}")

files_to_scan = (
    walk("README.md")
    + walk("agents")
    + walk("benchmarks")
    # Messenger/chat exports under chat/ can accidentally keep Git conflict markers after merges.
    + walk("chat")
    + walk("docs")
    + walk("profiles")
    + walk("rules")
    + walk("skills")
    + walk("scripts")
    + walk(".github")
    + walk("agent-tasks")
)

for path in files_to_scan:
    if path.suffix not in TEXT_EXTENSIONS:
        continue
    text = read_text_robust(path)
    rel_path = path.relative_to(ROOT).as_posix()
    for line in text.splitlines():
        if line.startswith((CONFLICT_START, CONFLICT_MID, CONFLICT_END)):
            fail(f"[conflict] Merge conflict markers found in {rel_path}")
            break


def first_non_empty_line(path: Path) -> str:
    text = read_text_robust(path)
    for line in text.splitlines():
        if line.strip():
            # Some UTF-8 BOM scenarios may appear as a literal U+FEFF at line start.
            return line.strip().lstrip("\ufeff")
    return ""


for path in walk("agents"):
    if path.suffix == ".md" and path.name != "README.md":
        if first_non_empty_line(path) != "---":
            fail(
                f'[frontmatter] {path.relative_to(ROOT).as_posix()} must start with frontmatter delimiter "---"',
            )

for path in walk("rules"):
    if path.suffix == ".mdc" and first_non_empty_line(path) != "---":
        fail(
            f'[frontmatter] {path.relative_to(ROOT).as_posix()} must start with frontmatter delimiter "---"',
        )

for path in walk("skills"):
    if path.name == "SKILL.md" and first_non_empty_line(path) != "---":
        fail(
            f'[frontmatter] {path.relative_to(ROOT).as_posix()} must start with frontmatter delimiter "---"',
        )


def mirror_check_enabled() -> bool:
    value = os.getenv(MIRROR_CHECK_ENV, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def check_root_mirror_drift() -> None:
    """Detect drift between canonical root paths and optional .cursor mirrors."""
    if not mirror_check_enabled():
        return
    if not MIRROR_ROOT.exists():
        return

    for directory in MIRROR_SYNC_DIRS:
        root_dir = ROOT / directory
        mirror_dir = MIRROR_ROOT / directory
        if not root_dir.exists() or not mirror_dir.exists():
            continue

        root_files = [path for path in root_dir.rglob("*") if path.is_file()]
        for root_file in root_files:
            rel = root_file.relative_to(ROOT)
            mirror_file = MIRROR_ROOT / rel
            if not mirror_file.exists():
                warn(f"[mirror] Missing mirrored file .cursor/{rel.as_posix()}")
                continue
            if root_file.read_bytes() != mirror_file.read_bytes():
                warn(f"[mirror] Drift detected between {rel.as_posix()} and .cursor/{rel.as_posix()}")


check_root_mirror_drift()

markdown_files = [
    path
    for path in (
        walk("README.md")
        + walk("agents")
        + walk("benchmarks")
        + walk("docs")
        + walk("profiles")
        + walk("skills")
        + walk("agent-tasks")
        + walk("rules")
    )
    if path.suffix in {".md", ".mdc"}
]

for path in markdown_files:
    text = read_text_robust(path)
    rel_path = path.relative_to(ROOT).as_posix()
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        sanitized_target = target.split("#", 1)[0].split("?", 1)[0]
        resolved = (path.parent / sanitized_target).resolve()
        if not resolved.exists():
            fail(f"[links] Broken markdown link in {rel_path}: {target}")

gitignore = read(".gitignore")
for forbidden_pattern in (r"^/?scripts/$", r"^/?agent-tasks/$"):
    if re.search(forbidden_pattern, gitignore, re.MULTILINE):
        fail(f"[gitignore] Forbidden ignore pattern /{forbidden_pattern}/ found in .gitignore")

workflow_text = read(".github/workflows/repo-validation.yml")
if "setup-python" not in workflow_text:
    fail("[workflow] CI workflow must install Python explicitly")
uses_full_benchmark = "run-full-repo-benchmark" in workflow_text
if uses_full_benchmark:
    # scripts/run-full-repo-benchmark.py runs validators + behavior + transcript + exporter smoke (CI parity).
    pass
else:
    if "run-behavior-benchmarks" not in workflow_text:
        fail("[workflow] CI workflow must run behavior benchmarks explicitly")
    if "evaluate-transcript-runs" not in workflow_text:
        fail("[workflow] CI workflow must run transcript benchmarks explicitly")
    if "export-delegation-tree" not in workflow_text:
        fail("[workflow] CI workflow must smoke-test delegation exporter explicitly")

if errors:
    print("Repository consistency validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    sys.exit(1)

print("Repository consistency validation passed.")
print(f"- Checked files: {len(files_to_scan)}")
if warnings:
    print(f"- Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"  * {warning}")
elif not mirror_check_enabled():
    print(f"- Mirror drift check: skipped (set {MIRROR_CHECK_ENV}=1 to enable)")
