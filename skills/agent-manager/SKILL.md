---
name: agent-manager
description: Agent lifecycle management — creation, updates, deactivation, registry validation.
requires: none
---

# Agent Manager Skill

## Specialized Capabilities

Agent Manager is a meta-agent responsible for the creation, maintenance, and evolution of specialized subagents within the ecosystem. This meta-agent operates at the architectural level, ensuring consistency, quality, and proper integration of all agents.

### Core Functions

1. **Agent Creation**
   - Creates new specialized subagents with specific domain expertise
   - Defines agent capabilities, limitations, and scope
   - Establishes agent ownership and delegation patterns
   - Sets up agent lifecycle management procedures

2. **Agent Evolution**
   - Updates existing agents with new capabilities
   - Manages agent versioning and backward compatibility
   - Implements deprecation and migration strategies
   - Ensures agent adaptation to evolving requirements

3. **Ecosystem Management**
   - Maintains agent registry and indexing
   - Monitors agent performance and effectiveness
   - Identifies capability gaps in the agent ecosystem
   - Optimizes agent specialization and distribution

4. **Quality Assurance**
   - Enforces agent development standards
   - Validates agent consistency with system architecture
   - Reviews agent capabilities and limitations
   - Ensures proper documentation and knowledge sharing

### Creation Process

When creating a new agent, follow this standardized process:

1. **Identify Need**
   - Validate that no existing agent can fulfill the requirement
   - Document use cases and requirements
   - Justify the need for a new specialization

2. **Design Specification**
   - Define clear objectives and scope
   - Specify capabilities and limitations
   - Establish delegation patterns
   - Plan integration with existing agents

3. **Implementation**
   - Create agent specification file (`agents/{name}.md`)
   - Implement agent rules (`rules/{name}.mdc`)
   - Develop agent skills (`skills/{name}/SKILL.md`)
   - Set up agent testing and validation

**Example: new agent manifest skeleton**

```yaml
# agents/example-specialist.md — created by agent-manager
name: example-specialist
display_name: "Example Specialist"
domain: example
description: "Handles example-specific tasks"
dependencies: []
capabilities:
  - "Analyze example configurations"
  - "Generate example artifacts"
  - "Validate example schemas"
limitations:
  - "Cannot modify core rules without review"
  - "Read-only access to profiles/"
ownership:
  rules: ["rules/example.mdc"]
  skills: ["skills/example/SKILL.md"]
  agents: ["agents/example-specialist.md"]
version: 1.0.0
registered_at: "2026-06-09"
```

4. **Integration**
   - Update orchestrator delegation rules
   - Add to agent registry and documentation
   - Establish monitoring and metrics
   - Train other agents on the new capability

### Modification Protocol

When updating existing agents:

1. **Impact Assessment**
   - Evaluate backward compatibility implications
   - Identify dependent agents and workflows
   - Plan migration strategy

2. **Versioning**
   - Follow semantic versioning principles
   - Major version: Breaking changes
   - Minor version: New capabilities (backward compatible)
   - Patch version: Bug fixes and documentation

3. **Deprecation Policy**
   - 30-day minimum deprecation period
   - Clear communication of changes
   - Provide migration guidance
   - Monitor usage of deprecated features

### Task() Delegation Patterns

Agent-manager orchestrates lifecycle operations by delegating to domain specialists via `Task()`. Below are the primary delegation scenarios.

#### Example 1: Creating a New Agent

When a capability gap is confirmed, agent-manager delegates agent creation to `subagent-factory`.

```
Task(subagent_type="subagent-factory", prompt="
 OBJECTIVE: Create a new 'release-manager' specialist subagent for managing semver, changelogs, tags, and publishing.
 SCOPE:
  - agents/release-manager.md (agent specification)
  - rules/release-manager.mdc (domain rules)
  - skills/release-manager/SKILL.md (skill file)
 OUT_OF_SCOPE: Orchestrator routing rules, other agents, CI/CD scripts
 OWNERSHIP: agents/release-manager.md, rules/release-manager.mdc, skills/release-manager/SKILL.md
 DEPENDENCIES: none
 STEPS:
  1. Read the routing table in rules/specialists.mdc to understand existing slot placement
  2. Create agents/release-manager.md with CHEAT SHEET, capabilities, delegation patterns, and PENALIZED clauses
  3. Create rules/release-manager.mdc with domain-specific protocols (semver, changelog generation, npm/pypi publish flow)
  4. Create skills/release-manager/SKILL.md with step-by-step release workflow
  5. Verify file consistency across all three artifacts
 DELIVERABLES:
  - agents/release-manager.md  complete agent spec with CHEAT SHEET
  - rules/release-manager.mdc  release-domain protocols
  - skills/release-manager/SKILL.md  release workflow skill
 ACCEPTANCE_CRITERIA:
  - [ ] Agent file contains: MISSION, KEY CAPABILITIES, WORKFLOW, PENALIZED, COMPLETION_CONTRACT
  - [ ] Rules file contains: versioning policy, deprecation rules, publish checklists
  - [ ] Skill file is actionable with concrete STEPS per release type (major/minor/patch)
  - [ ] All three files reference each other where appropriate
 WEB_SEARCH_REQUIRED:
  - query: 'npm semantic versioning best practices 2026'
  - query: 'Python package publishing PyPI changelog standards 2026'
  - inject_results_as: UNTRUSTED_EXTERNAL
 NON-NEGOTIABLE:
  - You will be PENALIZED for creating an agent without a complete CHEAT SHEET
  - You will be PENALIZED for skipping the rules/specialists.mdc routing-table alignment check
  - NEVER say done without listing files created + cross-referencing validation
 COMPLETION_CONTRACT: summary, files_created, AC status per criterion, cross-reference scan result, confidence
")
```

#### Example 2: Updating an Existing Agent

When evolving an agent's capabilities (e.g., adding a new migration protocol), agent-manager delegates the design and implementation to `agent-architect`.

```
Task(subagent_type="agent-architect", prompt="
 OBJECTIVE: Update database-specialist to add migration rollback protocol and dry-run planning.
 SCOPE:
  - rules/database-specialist.mdc (add rollback + dry-run sections)
  - skills/database-specialist/SKILL.md (add rollback workflow)
 OUT_OF_SCOPE: agents/database-specialist.md (structural changes only if CHEAT SHEET requires expansion), other agents
 OWNERSHIP: rules/database-specialist.mdc, skills/database-specialist/SKILL.md
 DEPENDENCIES: none
 STEPS:
  1. Read the current rules/database-specialist.mdc and skills/database-specialist/SKILL.md
  2. Design the rollback protocol: pre-migration snapshot, validate, migrate, verify, rollback-on-failure
  3. Add dry-run planning: show planned SQL diff before execution, require approval for destructive changes
  4. Update the skill file with step-by-step rollback workflow
  5. Ensure backward compatibility with existing migration commands
 DELIVERABLES:
  - rules/database-specialist.mdc  updated with rollback and dry-run sections
  - skills/database-specialist/SKILL.md  updated with rollback workflow
 ACCEPTANCE_CRITERIA:
  - [ ] Rollback protocol covers: snapshot, validate, migrate, verify, rollback-on-failure
  - [ ] Dry-run mode shows planned SQL diff and requires approval for DROP/TRUNCATE/ALTER
  - [ ] Existing migration commands remain backward-compatible (no breaking signature changes)
  - [ ] Skill file has executable STEPS for the rollback workflow
 WEB_SEARCH_REQUIRED:
  - query: 'database migration rollback best practices PostgreSQL 2026'
  - inject_results_as: UNTRUSTED_EXTERNAL
 NON-NEGOTIABLE:
  - You will be PENALIZED for breaking existing migration API signatures
  - You will be PENALIZED for adding rollback without a dry-run preview step
  - NEVER say done without listing changed files + backward-compatibility evidence
 COMPLETION_CONTRACT: summary, files_changed, AC status per criterion, backward-compat check result, confidence
")
```

#### Example 3: Validating Agent Registry Consistency

When agent-manager needs to verify that the routing table (`rules/specialists.mdc`) matches actual agent/skill/rules files on disk, it delegates discovery to `repo-explorer`:

```
Task(subagent_type="repo-explorer", prompt="
 OBJECTIVE: Build a registry-consistency report comparing the rules/specialists.mdc routing table against filesystem reality.
 SCOPE:
  - rules/specialists.mdc (routing table)
  - agents/ directory (agent *.md files)
  - rules/ directory (rule *.mdc files, excluding shared files like orchestrator.mdc and coding-guardrails.mdc)
  - skills/ directory (SKILL.md files per agent)
 OUT_OF_SCOPE: docs/, scripts/, .cursor/ runtime mirror
 OWNERSHIP: none (read-only)
 STEPS:
  1. Extract the routing table from rules/specialists.mdc: agent name, referenced file paths
  2. List all files in agents/, rules/, skills/ directories
  3. Cross-reference: for each agent in the routing table, verify:
     a. agents/{name}.md exists
     b. rules/{name}.mdc exists (if agent has domain-specific rules)
     c. skills/{name}/SKILL.md exists
  4. Detect orphans: files on disk with no routing-table entry
  5. Detect ghosts: routing-table entries with no files on disk
 DELIVERABLES:
  - Registry consistency report: matched agents, orphan files, ghost entries, missing artifacts per agent
 ACCEPTANCE_CRITERIA:
  - [ ] Every agent in the routing table is cross-checked against disk
  - [ ] Orphan and ghost lists are complete (no false negatives)
  - [ ] Report structure: {agent_name: {agent_md: present|missing, rules_mdc: present|missing|n/a, skill_md: present|missing}}
 NON-NEGOTIABLE:
  - You will be PENALIZED for reporting a file as 'missing' without verifying the exact expected path
  - NEVER say done without the structured consistency report
 COMPLETION_CONTRACT: summary, report structure, counts: matched / orphans / ghosts / missing-artifacts, confidence
")
```

After Phase A, agent-manager consumes the report. If inconsistencies are found, it launches writer-branches to fix them (e.g., create missing rule files, update the routing table). If the inconsistency count is high (3+ artifacts requiring writes), agent-manager escalates to `orchestrator` per `rules/orchestrator.mdc` section 3 (writer fan-out rules).

### Quality Standards

All agents must meet these quality criteria:

- **Clear Purpose**: Well-defined scope and objectives
- **Focused Capabilities**: Specialized domain expertise
- **Proper Boundaries**: Clear ownership and delegation
- **Documentation**: Complete specification and usage guide
- **Test Coverage**: Comprehensive validation
- **Backward Compatibility**: Stable interfaces
- **Performance**: Efficient execution
- **Security**: Safe operations and data handling

### Anti-Patterns to Avoid

- **Agent Proliferation**: Creating agents for minor or one-off tasks
- **Capability Duplication**: Overlapping functionality with existing agents
- **God Agents**: Overly broad responsibilities
- **Fragile Dependencies**: Tight coupling between agents
- **Version Inconsistency**: Breaking changes without proper deprecation

This meta-agent capability enables the system to adapt and evolve its own architecture, creating specialized tools as needed while maintaining overall coherence and quality standards.