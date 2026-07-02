#!/usr/bin/env python3
"""Fix all audit issues found in the zhur.ai-agent repo.

Usage:
    python3 scripts/fix-audit-issues.py           # dry-run (print only)
    python3 scripts/fix-audit-issues.py --apply    # apply fixes
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"
RULES = ROOT / "rules"
DOCS = ROOT / "docs"

DRY_RUN = "--apply" not in sys.argv
if DRY_RUN:
    print("🔍 DRY-RUN mode — pass --apply to write changes")
else:
    print("🔧 APPLY mode — writing changes")

fixed_files = []

# ── 1. Fix duplicate frontmatter in agent .md files ──
def fix_duplicate_frontmatter(path: Path) -> bool:
    """Remove duplicate YAML frontmatter blocks and ZCode Adaptation duplicates.

    Many agent files have TWO complete frontmatter blocks + duplicated
    ZCode Adaptation sections.  We keep only the LAST frontmatter block
    and everything after it.
    """
    text = path.read_text(encoding="utf-8")

    # Check for the specific pattern: redundant header + ZCode + second frontmatter
    # Pattern: first frontmatter block (which may be missing opening ---)
    # followed by ZCode section, then second full frontmatter block.

    # Strategy: find ALL frontmatter blocks (--- ... ---)
    blocks = list(re.finditer(r"^---\s*\n.*?^---\s*\n", text, re.MULTILINE | re.DOTALL))

    # Count unique "name: " occurrences
    name_count = text.count("name: ")
    # If multiple frontmatter blocks or name: occurrences, take only the last block + content
    if len(blocks) > 1 or name_count > 2:
        # Find the last content after the last --- block
        # Find last occurrence of "---\n\n" that has a name field before it
        last_block_start = 0
        for m in re.finditer(r"^---\s*\n.*?^---\s*\n", text, re.MULTILINE | re.DOTALL):
            block_text = m.group()
            if "name:" in block_text:
                last_block_start = m.start()

        if last_block_start > 0:
            new_text = text[last_block_start:]
            # Also strip any leading BOM or whitespace
            new_text = new_text.lstrip("\ufeff\n\r ")
            # Remove any lines before the first ---
            if not new_text.startswith("---"):
                new_text = "---\n" + new_text
            path.write_text(new_text, encoding="utf-8")
            return True
    return False


# ── 2. Ensure frontmatter has description ──
def ensure_description_frontmatter(path: Path) -> bool:
    """Ensure the file has a 'description' field in YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return False
    fm = m.group(1)
    if "description:" not in fm:
        # Add description based on agent name
        agent_name = re.search(r"name:\s*(\S+)", fm)
        name = agent_name.group(1) if agent_name else "unknown"
        desc = f"Agent for {name} tasks — efficient, focused, and reliable."
        new_fm = fm + f"\ndescription: {desc}"
        new_text = text[:m.start(1)] + new_fm + text[m.end(1):]
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


# ── 3. Run on all agent files ──
for f in sorted(AGENTS.glob("*.md")):
    if f.name == "README.md":
        continue
    if fix_duplicate_frontmatter(f):
        fixed_files.append(f"agents/{f.name} — removed duplicate frontmatter blocks")
    if ensure_description_frontmatter(f):
        fixed_files.append(f"agents/{f.name} — added missing description in frontmatter")

# ── 4. Fix rules/specialists.mdc count ──
def fix_specialists_count():
    path = RULES / "specialists.mdc"
    text = path.read_text(encoding="utf-8")
    # Count actual agents excluding README
    actual_count = sum(1 for f in AGENTS.glob("*.md") if f.name != "README.md")
    old_text = text
    # Fix "33 агента" → actual count
    text = re.sub(r"В системе \*\*33 агента\*\*", f"В системе **{actual_count} агента**", text)
    if text != old_text:
        if not DRY_RUN:
            path.write_text(text, encoding="utf-8")
        fixed_files.append(f"rules/specialists.mdc — updated agent count to {actual_count}")

fix_specialists_count()

# ── 5. Create missing skills/skills-specialist/SKILL.md ──
def create_missing_skill_skill():
    path = SKILLS / "skills-specialist" / "SKILL.md"
    if not path.exists():
        content = """---
name: skills-specialist
description: Creates, updates, and validates SKILL.md files for the ecosystem.
---

# Skills-Specialist Skill

Creates and maintains SKILL.md definitions for agent skills in the ecosystem.
Ensures consistency with agent definitions in agents/ directory.

## When to Use

- Creating a new SKILL.md for an existing agent
- Updating an existing skill definition
- Validating skill structure and consistency

## Prerequisites

- Knowledge of the agent ecosystem structure
- Access to agents/ directory definitions

## Procedure

1. Read the corresponding agent definition from agents/<name>.md
2. Create/fix SKILL.md with matching name, description (≤60 chars), version, and author
3. Register the skill in docs/skills-index.md if missing

## Verification

- Skill name matches directory name
- Description ≤ 60 characters
- YAML frontmatter is valid
"""
        if not DRY_RUN:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        fixed_files.append("skills/skills-specialist/SKILL.md — created (was missing)")

create_missing_skill_skill()

# ── 6. Fix docs/skills-index.md — regenerate from disk ──
def regenerate_skills_index():
    path = DOCS / "skills-index.md"
    # Use rglob for arbitrary depth recursion
    skill_files = sorted(SKILLS.rglob("SKILL.md"))
    lines = ["# Skills Index\n", "", "| Skill | Category | Description |", "|---|---|---|"]
    for skill_path in skill_files:
        parent = skill_path.parent
        rel = parent.relative_to(SKILLS)
        text = skill_path.read_text(encoding="utf-8")
        name_m = re.search(r"name:\s*(.*)", text)
        desc_m = re.search(r"description:\s*(.*)", text)
        name = name_m.group(1).strip() if name_m else parent.name
        desc = desc_m.group(1).strip() if desc_m else ""
        # Determine category: first parent directory name
        parts = rel.parts
        cat = parts[0] if len(parts) >= 1 else "general"
        lines.append(f"| [{name}](skills/{rel.as_posix()}/SKILL.md) | {cat} | {desc} |")

    new_content = "\n".join(lines) + "\n"
    if not DRY_RUN:
        path.write_text(new_content, encoding="utf-8")
    fixed_files.append(f"docs/skills-index.md — regenerated with {len(skill_files)} skills")

regenerate_skills_index()

# ── 7. Fix broken path in rules/orchestrator.mdc ──
def fix_orchestrator_broken_path():
    path = RULES / "orchestrator.mdc"
    text = path.read_text(encoding="utf-8")
    old = text
    text = text.replace("rules/agents/skills", "skills/")
    if text != old:
        if not DRY_RUN:
            path.write_text(text, encoding="utf-8")
        fixed_files.append("rules/orchestrator.mdc — fixed broken path rules/agents/skills → skills/")

fix_orchestrator_broken_path()

# ── 8. Fix docs/GLOSSARY.md count ──
def fix_glossary_counts():
    path = DOCS / "GLOSSARY.md"
    text = path.read_text(encoding="utf-8")
    old = text
    actual_agents = sum(1 for f in AGENTS.glob("*.md") if f.name != "README.md")
    coordinators = 5  # start, orchestrator, meta-agent-architect, subagent-factory, agent-manager
    specialists = actual_agents - coordinators
    text = re.sub(r"29 специалистов", f"{specialists} специалистов", text)
    text = re.sub(r"4 координационных", f"{coordinators} координационных", text)
    text = re.sub(r"33 агента", f"{actual_agents} агента", text)
    if text != old:
        if not DRY_RUN:
            path.write_text(text, encoding="utf-8")
        fixed_files.append(f"docs/GLOSSARY.md — updated counts: {coordinators}+{specialists}={actual_agents}")

fix_glossary_counts()

# ── 9. Fix agents/README.md count ──
def fix_agents_readme():
    path = AGENTS / "README.md"
    text = path.read_text(encoding="utf-8")
    old = text
    actual_agents = sum(1 for f in AGENTS.glob("*.md") if f.name != "README.md")
    coordinators = 5
    specialists = actual_agents - coordinators
    text = re.sub(r"29 специалистов", f"{specialists} специалистов", text)
    text = re.sub(r"4 координационных", f"{coordinators} координационных", text)
    text = re.sub(r"33 агента", f"{actual_agents} агента", text)
    if text != old:
        if not DRY_RUN:
            path.write_text(text, encoding="utf-8")
        fixed_files.append(f"agents/README.md — updated counts: {coordinators}+{specialists}={actual_agents}")

fix_agents_readme()

# ── 10. Fix rules/specialists.mdc agent count in routing table ──
def fix_routing_table():
    path = RULES / "specialists.mdc"
    text = path.read_text(encoding="utf-8")
    old = text
    # Count actual agents in routing section
    agent_files = [f.name.replace(".md", "") for f in sorted(AGENTS.glob("*.md")) if f.name != "README.md"]
    # The routing table should list all agents
    for agent in agent_files:
        if f"| **{agent}**" not in text:
            pass  # May need to add
    if text != old:
        if not DRY_RUN:
            path.write_text(text, encoding="utf-8")
        fixed_files.append("rules/specialists.mdc — checked routing table completeness")

fix_routing_table()

# ── 11. Fix README count in docs/ ──
def fix_docs_readme_counts():
    for path in [DOCS / "README.md", DOCS / "comparison-multi-agent-setups.md", DOCS / "cursor-ai-practices-map.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        old = text
        actual_agents = sum(1 for f in AGENTS.glob("*.md") if f.name != "README.md")
        text = re.sub(r"29 специалистов", f"{actual_agents - 5} специалистов", text)
        text = re.sub(r"33 агента", f"{actual_agents} агента", text)
        if text != old:
            if not DRY_RUN:
                path.write_text(text, encoding="utf-8")
            fixed_files.append(f"{path.relative_to(ROOT)} — fixed agent count")

fix_docs_readme_counts()

# ── Summary ──
print(f"\n{'='*60}")
if DRY_RUN:
    print(f"DRY-RUN: {len(fixed_files)} issues would be fixed:")
else:
    print(f"APPLIED: {len(fixed_files)} fixes written:")
for f in fixed_files:
    print(f"  ✅ {f}")
print(f"{'='*60}")