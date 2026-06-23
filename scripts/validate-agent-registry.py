#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / "agents"
COORDINATION_AGENTS = {
    "start",
    "orchestrator",
    "agent-architect",
    "subagent-factory",
}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read_text_robust(
    path: Path,
    encodings: Iterable[str] = (
        "utf-8",
        "utf-8-sig",
        # Cyrillic legacy encodings (these repo markdowns appear saved in one of them)
        "cp866",
        "koi8-r",
        "koi8-u",
        "mac-cyrillic",
        "iso-8859-5",
        # Windows-125x fallbacks (last resort)
        "cp1251",
        "cp1252",
    ),
) -> str:
    """
    Read text files that may be saved in legacy encodings.

    Goal: avoid hard failures in validators/benchmarks due to UnicodeDecodeError.
    """
    last_exc: UnicodeDecodeError | None = None
    for enc in encodings:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError as e:
            last_exc = e
            continue
    # Final fallback: never crash validators; preserve content as best as possible.
    if last_exc is not None:
        return path.read_text(encoding="utf-8", errors="replace")
    return path.read_text(encoding="utf-8", errors="replace")


def read(rel_path: str) -> str:
    return read_text_robust(ROOT / rel_path)


def parse_frontmatter(rel_path: str, text: str) -> tuple[str, str]:
    # Some agent markdown files start with UTF-8 BOM. Allow optional BOM and
    # trailing whitespace around frontmatter delimiters.
    match = re.match(
        r"^\ufeff?---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?",
        text,
        re.DOTALL,
    )
    if not match:
        fail(f'[frontmatter] Missing or malformed frontmatter in {rel_path}')
        return "", ""

    block = match.group(1)
    name_match = re.search(r"^name:\s*(.+)$", block, re.MULTILINE)
    description_match = re.search(r"^description:\s*(.+)$", block, re.MULTILINE)

    if not name_match:
        fail(f'[frontmatter] Missing "name" field in {rel_path}')
    if not description_match:
        fail(f'[frontmatter] Missing "description" field in {rel_path}')

    return (
        name_match.group(1).strip() if name_match else "",
        description_match.group(1).strip() if description_match else "",
    )


def expect_includes(rel_path: str, needle: str, label: str) -> None:
    text = read(rel_path)
    if needle not in text:
        fail(f'[{label}] Expected {rel_path} to include "{needle}"')


def expect_regex(rel_path: str, pattern: str, label: str) -> None:
    text = read(rel_path)
    if not re.search(pattern, text, re.DOTALL):
        fail(f"[{label}] Expected {rel_path} to match /{pattern}/")


agent_files = sorted(
    path for path in AGENT_DIR.glob("*.md") if path.name != "README.md"
)

if not agent_files:
    fail("[registry] No agent definitions found in agents/")

seen_names: dict[str, str] = {}
agent_names: list[str] = []

for path in agent_files:
    rel_path = path.relative_to(ROOT).as_posix()
    basename = path.stem
    text = read_text_robust(path)
    name, _description = parse_frontmatter(rel_path, text)

    if name and name != basename:
        fail(
            f'[registry] Frontmatter name "{name}" does not match filename "{basename}" in {rel_path}'
        )

    if name:
        if name in seen_names:
            fail(
                f'[registry] Duplicate agent name "{name}" in {rel_path} and {seen_names[name]}'
            )
        else:
            seen_names[name] = rel_path
            agent_names.append(name)

for required_agent in sorted(COORDINATION_AGENTS):
    if required_agent not in seen_names:
        fail(f'[registry] Missing required coordination agent "{required_agent}"')

agent_count = len(agent_names)
domain_count = len([name for name in agent_names if name not in COORDINATION_AGENTS])

expect_includes("README.md", f"{agent_count} agent definitions", "docs")
expect_includes("agents/README.md", f"{agent_count} agent definitions", "registry")
expect_includes("agents/README.md", f"{domain_count} domain specialists", "registry")
expect_regex(
    "rules/specialists.mdc",
    rf"(?:\*\*{agent_count}\s+agent definitions\*\*|\*\*{agent_count}\s+агента\*\*)",
    "registry",
)
expect_regex(
    "rules/specialists.mdc",
    rf"\*\*{domain_count}\*\*[\s\S]{{0,64}}(?:domain specialists|специалист)",
    "registry",
)

for registry_file in ("agents/README.md", "rules/specialists.mdc"):
    text = read(registry_file)
    for agent_name in agent_names:
        if agent_name not in text:
            fail(f'[registry] {registry_file} does not mention agent "{agent_name}"')

if errors:
    print("Agent registry validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    sys.exit(1)

print("Agent registry validation passed.")
print(f"- Agents: {agent_count}")
print(f"- Coordination agents: {len(COORDINATION_AGENTS)}")
print(f"- Domain specialists: {domain_count}")
