# Agent Registry

## Core Agents

### Agent Manager
- **Role**: Creates, updates, and manages specialized subagents
- **Capabilities**: Agent lifecycle management, capability evolution, ecosystem optimization
- **Use Cases**: When existing agents cannot cover a recurring task pattern, when orchestrator detects a capability gap
- **Documentation**: `agents/agent-manager.md`

### Orchestrator
- **Role**: Coordinates complex tasks across multiple agents
- **Capabilities**: Task decomposition, agent delegation, workflow management
- **Use Cases**: Multi-step tasks, complex workflows, parallel processing
- **Documentation**: `agents/orchestrator.md`

### Start
- **Role**: Primary entry point for user requests
- **Capabilities**: Initial request handling, worker initialization, task routing
- **Use Cases**: User initiates `/start`, task delegation
- **Documentation**: `agents/start.md`

### Code
- **Role**: Implements code changes and modifications
- **Capabilities**: Code generation, refactoring, bug fixes
- **Use Cases**: Feature implementation, code improvements, bug resolution
- **Documentation**: `agents/code.md`