# Optimized Agent System
*33 agent definitions (4 coordination + 29 domain specialists in core) + intelligent orchestration*

## Canonical Repository Paths

Use root-first canonical paths for all navigation and edits:
- `agents/` (agent definitions)
- `rules/` (behavioral policy)
- `skills/` (operational skills)
- `docs/` (project documentation)

If `.cursor/` mirror paths exist in runtime context, treat them as mirrors. Canonical edits should target root paths first unless a task explicitly requires mirror-only maintenance.

## 🎯 Quick Start

**For complex or multi-domain requests**: Start with the **start** agent (`/start`)
**For simple, single-domain tasks**: Use the appropriate specialist directly (`/[agent-name]`)
**Need new capabilities?**: Use **Meta-Agent-Architect** (`/meta-agent-architect`) or **Subagent-Factory** (`/subagent-factory`)

## 🏗️ System Architecture

The agent system supports recursive coordination for complex work:
```
User → start → Orchestrator → Auto-Orchestrating Specialists
     ↘ Meta-Agent-Architect + Subagent-Factory → New Capability Packages
     
Typical coordination levels:
Level 1: Simple task execution or complexity analysis
Level 2: Specialist coordination for complex tasks  
Level 3: Multi-domain orchestration with quality gates
Level 4+: Additional recursion only when it improves convergence
```

### 🎯 Central Intelligence
| Agent | Role | When to Use |
|-------|------|-------------|
| **start** | Pure router / main entry; one direct handoff to orchestrator | Complex requests, multi-domain tasks, optimization needs |
| **orchestrator** | Multi-step workflow coordination | Cross-domain projects, parallel specialist coordination |
| **meta-agent-architect** | Ecosystem design and governance | Agent family redesign, standards, merge/split decisions |
| **subagent-factory** | Builds specialist packages (agent + rules + skill) | Fast creation/update of focused capabilities |

## 🚀 Auto-Orchestration System

**Core coordination goals:**
- Route tasks to the smallest effective owner.
- Delegate recursively only when needed.
- Enforce quality gates before synthesis.
- Keep branch contracts explicit and verifiable.
- Stop unproductive recursion via anti-loop controls.

### 🧠 Complexity Detection Examples

**Simple Tasks (Direct Execution):**
- Single file modifications within expertise domain
- Standard pattern applications with clear requirements
- Component-level changes with no external dependencies

**Complex Tasks (Auto-Orchestration):**
- Multi-system architectural decisions → **architect** orchestrates with **api-designer**, **database-specialist**, **security-auditor**
- Performance optimization across full stack → **performance-optimizer** coordinates with **database-specialist**, **frontend-specialist**, **monitoring-specialist**
- Security audit for compliance → **security-auditor** orchestrates with **devops-specialist**, **database-specialist**, **performance-optimizer**

## 🔧 Core Specialists

### **Planning & Architecture**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| architect | Planning, specs, architecture before coding | "Design microservices architecture" |
| api-designer | API design, endpoints, developer experience | "Design REST API for user management" |
| agent-architect | Agent workflows, roles, guardrails, runbooks | "Create code review workflow" |

### **Development & Implementation**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| code | Implement features, fix bugs, refactor | "Add user authentication system" |
| debug | Diagnose errors, root cause, then fix | "Investigate JWT token expiration" |
| database-specialist | Database design, optimization, migrations, query tuning | "Optimize slow queries, design schema" |
| frontend-specialist | React/TS/CSS, UX, accessibility | "Create responsive dashboard" |
| mobile-specialist | React Native, iOS/Android optimization, mobile patterns | "Build cross-platform mobile app" |
| provider-integrator | AI providers in `src/api/providers/**` | "Add new AI model support" |

### **Data & Analytics**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| data-analyst | Data processing, ETL, analytics, data science, visualization | "Build sales analytics dashboard" |

### **Operations & Infrastructure**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| devops-specialist | CI/CD, Docker, deployment, containerization, Kubernetes | "Set up production deployment pipeline" |
| monitoring-specialist | Logging, metrics, tracing, APM, observability | "Implement comprehensive monitoring" |

### **Quality Assurance**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| test-specialist | Comprehensive testing, Jest, coverage, debugging failures | "Create full test suite" |
| code-reviewer | General code quality, standards, mentoring | "Review for best practices" |
| code-simplifier | Refactor without changing behavior | "Simplify complex components" |
| code-skeptic | Verify claims, enforce project rules | "Validate architecture decisions" |
| security-auditor | Security review, vulnerability assessment | "Audit authentication flow" |
| performance-optimizer | Profiling, latency, memory optimization | "Fix performance bottlenecks" |
| review | Formal git-diff review, runtime verdicts `approval/blocked/pause/resume` | "Review pull request" |

### **Documentation & Support**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| docs-specialist | Technical writing, READMEs, changelogs | "Write API documentation" |
| bug-triage | Reproduction steps, root cause analysis, fix planning | "Analyze bug reports" |
| repo-explorer | Navigate codebase, find files, trace flows | "Find where feature is implemented" |
| ask | Questions and explanations (no code changes) | "How does authentication work?" |
| release-manager | Complete release lifecycle, changesets, versioning | "Prepare release v2.1.0" |

### **Orchestration & Registry**
| Agent | Purpose | Example Use |
|-------|---------|-------------|
| benchmark-specialist | Run behavior contracts, evaluate transcripts, add scenarios | "Run full repo benchmarks and report regressions" |
| rules-specialist | Create/update .mdc rules, register agents in routing table | "Add a routing rule to specialists.mdc" |
| skills-specialist | Create/update SKILL.md, curate skills library | "Create a deployment skill for CI workflow" |
| profile-manager | Create/manage project-specific profiles in profiles/ | "Create profile for myproject with custom agents" |
| agent-manager | Create, update, manage specialized subagents lifecycle | "Add new agent to the ecosystem" |

## 🚀 Usage Patterns

### 🔥 Simple Tasks (Direct Specialist)
```bash
/database-specialist Optimize this slow query and add indexes
/frontend-specialist Fix accessibility issues in LoginForm
/test-specialist Create tests for AuthService
/devops-specialist Set up Docker containerization and CI/CD pipeline
/mobile-specialist Create React Native login screen with biometric auth
/data-analyst Build user engagement analytics dashboard
/monitoring-specialist Implement logging and alerting for API endpoints
```

### 🎼 Complex Tasks (start → Orchestrator → Specialists)
```bash
/start Implement complete user authentication system with database, API, UI, and tests

/start Investigate performance issues across frontend and database
```

### 🤖 Capability Expansion
```bash
/subagent-factory Create mobile-specialist package for React Native

/meta-agent-architect Analyze overlap and redesign across operations specialists

/subagent-factory Create qa-automation-specialist with rules and skill package
```

## 📊 System Benefits

- Lower routing ambiguity for complex requests.
- Clear escalation path for capability gaps.
- Better separation between direct specialist work and orchestrated work.
- Consistent delegation contracts and synthesis format.
- More predictable quality through explicit verification steps.

## 📖 Documentation

- **[Docs index](../docs/README.md)** — оглавление `docs/` и порядок чтения.
- **[Быстрый старт оркестрации](../docs/quick-start-orchestration.md)** — один запрос → root `start` → `Task(orchestrator)` → специалисты.
- **[Процесс и quality gates](../docs/process-and-quality-gates.md)** — когда какой агент, минимальные проверки.
- **[Сравнение с другими системами](../docs/comparison-multi-agent-setups.md)** — контекст многоагентных схем.
- **[Цикл verify / analyzer](../docs/autonomous-task-with-verification.md)** — роль **start** только как analyzer из orchestrator.
- **[Цепочка `/start` → root `start` → `Task(orchestrator)` → сабагенты](../docs/delegation-chain.md)** — как работает flat-chain и почему `Task(X)` = `/X`.
- **[План проекта `.plan/`](../docs/project-plan-convention.md)** — `todos.md`, журнал, направления; обновление с волнами оркестрации.
- **[Автономность и много «голосов»](../docs/autonomy-multi-voice.md)** — skill `multi-pass-autonomy`; не AGI, лимиты и артефакты.
- **[Пример промпта: 3 голоса](../docs/orchestrator-three-voice-prompt-example.md)** — Builder / Skeptic / Verifier.
- **Качество промптов:** [agent-prompt-quality SKILL](../skills/agent-prompt-quality/SKILL.md).

## 💡 Best Practices

1. **Start with purpose, not agent**: What are you trying to accomplish?
2. **Use `/start` for entry**: **start** только собирает конверт и вызывает **`Task(orchestrator, …)`**, затем кратко отвечает пользователю. **Не** вызывает специалистов напрямую. Прямая работа одним доменом — **`/code`**, **`/debug`** и т.д. без start.
3. **Be specific with specialists**: Provide clear context and requirements.
4. **Let orchestrator coordinate**: For tasks spanning multiple domains; orchestrator splits branches and assigns domain specialists by fit (see `rules/specialists.mdc`).
5. **Request new capabilities**: Use Meta-Agent-Architect for ecosystem design and Subagent-Factory for fast package creation.
6. **Validate registry consistency**: After adding/removing agent files, run validators from the repo root:
   - bash: **`scripts/validate-agent-registry.sh`**
   - PowerShell: **`scripts/validate-agent-registry.ps1`**
   - bash: **`scripts/validate-repo-consistency.sh`**
   - PowerShell: **`scripts/validate-repo-consistency.ps1`**
   - bash: **`scripts/run-behavior-benchmarks.sh`**
   - PowerShell: **`scripts/run-behavior-benchmarks.ps1`**
   Update the registry docs (`README.md`, `agents/README.md`, `rules/specialists.mdc`) when the registry changes intentionally.

## Optional Profiles

Project-specific specialists are kept outside the universal core:
- `profiles/msnmp/agents/pentest-pipeline.md`
- `profiles/msnmp/rules/pentest-pipeline.mdc`

Enable them only when a host project explicitly merges that profile into runtime `.cursor/`.

---

**Need help choosing?** Use `/start` and let the system optimize your workflow!