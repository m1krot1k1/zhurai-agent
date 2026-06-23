# ZCode canonical paths

Layout and path policy for the **multi-agent-ecosystem** ZCode plugin. This plugin is self-contained: there is no `.cursor/` mirror tree — edit sources here directly.

## Plugin root

Installed layout (relative to plugin root):

```text
.zcode-plugin/
  plugin.json          # name, version, skills/commands dirs
commands/
  start.md             # /start slash command
  orchestrator.md      # /orchestrator slash command
  …                    # other slash commands (per agent)
skills/
  multi-agent-ecosystem/
    SKILL.md           # master skill entry (loaded by commands)
    references/
      orchestration/   # this folder — on-demand orchestration docs
      agents/          # per-specialist briefs (*.md)
      rules/           # policy adaptations (*.md / *.mdc)
      skills/          # optional nested skill copies
```

`plugin.json` declares:

```json
{
  "skills": "skills",
  "commands": "commands"
}
```

Paths in commands and references are **relative to the plugin root**, not the user's project repo.

## Canonical source-of-truth tiers

| Tier | Paths | Edit policy |
|------|-------|-------------|
| **Commands** | `commands/*.md` | Slash entry points; front-matter links to skill |
| **Master skill** | `skills/multi-agent-ecosystem/SKILL.md` | Routing, DUA, delegation summary |
| **Orchestration refs** | `skills/multi-agent-ecosystem/references/orchestration/` | Chain, workflow, routing, contracts |
| **Agent briefs** | `skills/multi-agent-ecosystem/references/agents/` | One file per specialist |
| **Rules** | `skills/multi-agent-ecosystem/references/rules/` | orchestrator, specialists, aleksander, etc. |
| **Nested skills** | `skills/multi-agent-ecosystem/references/skills/*/SKILL.md` | Deep dives (start-workflow, orchestrator, …) |

**Primary rule:** state maps, gap analysis, and branch `OWNERSHIP` target plugin paths above — not the user's unrelated project tree unless the task explicitly scopes there.

## User project vs plugin

| Context | Where agents work |
|---------|-------------------|
| Plugin development | `skills/multi-agent-ecosystem/**`, `commands/**` |
| User codebase task | User repo paths declared in branch `SCOPE` / `OWNERSHIP` |
| Planning (optional) | User repo `.plan/` if the project uses it |

The plugin does not sync into a hidden IDE mirror. After editing plugin files, reinstall or reload the plugin in ZCode per your environment's workflow.

## Skill discovery (required for `/start`)

ZCode **commands** load from `~/.zcode/commands/commands/`. **Skills** load separately from:

- `~/.zcode/skills/<name>/SKILL.md` (user-global, highest priority for personal skills)
- Enabled official plugins under `~/.zcode/cli/plugins/cache/`

If `/start` fails with `Skill not found: multi-agent-ecosystem`, register the skill once:

```bash
bash ~/.zcode/commands/scripts/install-skill-discovery.sh
```

Then start a **new ZCode chat** (skills are resolved at session bootstrap).

**Fallback (no install):** `commands/start.md` instructs the agent to Read
`skills/multi-agent-ecosystem/SKILL.md` directly when the Skill tool is unavailable (or `ZHUR_AI_AGENT_ROOT/skills/multi-agent-ecosystem/SKILL.md`).

## Path resolution for agents

1. Command sets `skills: multi-agent-ecosystem`.
2. Agent resolves `references/...` from `skills/multi-agent-ecosystem/references/...`.
3. Orchestrator loads `references/orchestration/delegation-chain.md` before decomposition.
4. Specialist branch loads `references/agents/<name>.md` for role behavior.
5. Policy conflicts: `references/rules/` wins over orchestration summaries.

Example resolutions:

| Reference in command | Resolved path |
|---------------------|---------------|
| `references/orchestration/delegation-chain.md` | `skills/multi-agent-ecosystem/references/orchestration/delegation-chain.md` |
| `references/agents/code.md` | `skills/multi-agent-ecosystem/references/agents/code.md` |
| `references/rules/orchestrator.mdc` | `skills/multi-agent-ecosystem/references/rules/orchestrator.mdc` |

## What not to scan as canonical

- Nested duplicate plugin installs inside user projects (unless task scopes there)
- Generated or vendor trees (`node_modules`, build output)
- User's global `~/.cursor/` config (runtime only; not this plugin's source)

## Validation (when scripts exist)

If the plugin ships validators under `scripts/`:

| Check | Purpose |
|-------|---------|
| Agent registry count | Every `references/agents/*.md` has a matching command or registry entry |
| Reference link check | Internal `references/` links resolve |
| Skill front-matter | Each `commands/*.md` points at `multi-agent-ecosystem` |

Run whatever validate script the plugin documents; if none exist yet, manual checklist: every path in [routing-table.md](./routing-table.md) should exist under `references/agents/`.

## Comparison with Cursor-era layout

| Cursor repo | ZCode plugin equivalent |
|-------------|-------------------------|
| `agents/*.md` | `references/agents/*.md` |
| `rules/*.mdc` | `references/rules/*` |
| `skills/*/SKILL.md` | `references/skills/*/SKILL.md` + master `SKILL.md` |
| `docs/delegation-chain.md` | `references/orchestration/delegation-chain.md` |
| `.cursor/` mirror | **None** — single canonical tree |

## See also

- [README.md](./README.md) — orchestration index and on-demand loading
- [routing-table.md](./routing-table.md) — agent brief paths
- `.zcode-plugin/plugin.json` — plugin metadata
