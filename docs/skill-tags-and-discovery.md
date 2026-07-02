# Skill tags and discovery

Skills in this repo live under `skills/*/SKILL.md`. **Discovery** means finding the *right* skill quickly without pasting every `SKILL.md` into context.

## Tags and “when to use”

Prefer **machine- and human-facing** hints in each skill’s YAML frontmatter:

- **`name`** — stable identifier; often matches directory name.
- **`description`** — one line; appears in agent picker and [skills index](skills-index.md).
- **When-to-use bullets** (in body or frontmatter, per skill convention) — **triggers**: task shape, risk class, or artifact type.

Tags might include domains (`orchestration`, `security`, `mcp`) or task shapes (`delegation`, `evals`). Keep tags **low-cardinality** so the index stays scannable.

## Finding skills without context bloat

1. **Start at the index** — [skills-index.md](skills-index.md) lists every path and a one-line summary.
2. **Route by task shape** — [specialist-discovery](../skills/specialist-discovery/SKILL.md) maps *problems* to agents; skills document *how* those agents should work.
3. **Progressive loading** — read **only** the skill you need; use [agent-system-navigation](../skills/agent-system-navigation/SKILL.md) for cross-links.
4. **MCP and tools** — for server/tool discovery specifically, use [mcp-governance](../skills/mcp-governance/SKILL.md) so schemas do not flood context.

## Practices map

For “where did we encode practice X,” see [cursor-ai-practices-map](cursor-ai-practices-map.md) — it points to skills **and** docs without duplicating full rules.

## Operational note

Regenerate or extend the **skills index** when adding directories under `skills/` so names and paths stay aligned (`skills-index.md` intro describes the glob rule).

## Related artifacts

| Topic | Where |
| --- | --- |
| Full skill table | [skills-index](skills-index.md) |
| Practices → artifacts | [cursor-ai-practices-map](cursor-ai-practices-map.md) |
| Repo root conventions | [canonical-paths-and-cursor-mirror](canonical-paths-and-cursor-mirror.md) |
