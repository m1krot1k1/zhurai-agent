/** Extract a human agent label from a delegate goal / Task() prompt. */
export function extractAgentLabel(goal: string, agentId?: string): string | undefined {
  const explicit = agentId?.trim()
  if (explicit) {
    return explicit
  }

  const text = goal.trim()

  if (!text) {
    return undefined
  }

  const fromBrief = text.match(/AGENT_BRIEF_PATH:\s*.*?\/agents\/([\w-]+)\.md/i)?.[1]
  if (fromBrief) {
    return fromBrief
  }

  const agentIdLine = text.match(/^AGENT_ID:\s*(\S+)/im)?.[1] ?? text.match(/\bAGENT_ID:\s*(\S+)/i)?.[1]
  if (agentIdLine) {
    return agentIdLine
  }

  const subagentType = text.match(/subagent_type\s*[=:]\s*["']?([\w-]+)/i)?.[1]
  if (subagentType) {
    return subagentType
  }

  const taskType = text.match(/Task\s*\(\s*subagent_type\s*=\s*["']([\w-]+)["']/i)?.[1]
  if (taskType) {
    return taskType
  }

  const role = text.match(/\brole\s*[=:]\s*["']?(orchestrator|leaf)/i)?.[1]
  if (role && role.toLowerCase() !== 'leaf') {
    return role.toLowerCase()
  }

  const objective = extractObjectiveSnippet(goal)
  if (objective && objective.length <= 48) {
    return objective
  }

  return undefined
}

/** One-line OBJECTIVE (or first non-meta line) for row subtitle. */
export function extractObjectiveSnippet(goal: string, maxLen = 120): string | undefined {
  const text = goal.trim()
  if (!text) {
    return undefined
  }

  const objective = text.match(/OBJECTIVE:\s*([^\n]+)/i)?.[1]?.trim()
  const line = (objective ??
    text
      .split('\n')
      .map(l => l.trim())
      .find(l => l && !/^AGENT_ID:/i.test(l) && !/^role\s*[=:]\s*leaf\b/i.test(l)) ??
    '')
    .replace(/^#+\s*/, '')
    .replace(/\s+/g, ' ')
    .trim()

  if (!line) {
    return undefined
  }

  return line.length > maxLen ? `${line.slice(0, maxLen - 1)}…` : line
}

export interface SubagentDisplay {
  badge?: string
  title: string
}

/** Badge = agent id; title = objective or truncated goal (never duplicate badge text). */
export function formatSubagentDisplay(goal: string, agentId?: string, maxTitle = 72): SubagentDisplay {
  const badge = extractAgentLabel(goal, agentId)
  const objective = extractObjectiveSnippet(goal, maxTitle)
  const fallback = formatSubagentTitle(goal, maxTitle, agentId)

  if (badge && objective && objective.toLowerCase() !== badge.toLowerCase()) {
    return { badge, title: objective }
  }

  if (badge && fallback.toLowerCase() !== badge.toLowerCase()) {
    return { badge, title: fallback }
  }

  return { title: fallback, badge: badge && !objective ? badge : undefined }
}

/** Short title for subagent rows — label when present, else first line of goal. */
export function formatSubagentTitle(goal: string, maxLen = 72, agentId?: string): string {
  const label = extractAgentLabel(goal, agentId)
  const objective = extractObjectiveSnippet(goal, maxLen)

  if (label && objective && objective.toLowerCase() !== label.toLowerCase()) {
    return objective
  }

  if (label && !objective) {
    return label
  }

  const firstLine =
    goal
      .split('\n')
      .map(line => line.trim())
      .find(line => line && !/^AGENT_ID:/i.test(line) && !/^role\s*[=:]\s*leaf\b/i.test(line)) ?? goal

  const cleaned = firstLine.replace(/^#+\s*/, '').replace(/\s+/g, ' ').trim()

  if (!cleaned) {
    return 'Subagent'
  }

  return cleaned.length > maxLen ? `${cleaned.slice(0, maxLen - 1)}…` : cleaned
}

export function formatSubagentRoleBadge(role: string | undefined): string | undefined {
  if (!role) {
    return undefined
  }

  const normalized = role.trim().toLowerCase()
  if (!normalized || normalized === 'leaf') {
    return undefined
  }

  return normalized
}
