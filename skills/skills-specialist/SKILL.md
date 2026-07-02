---
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
