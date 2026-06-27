/** Extract a human agent label from a delegate goal / Task() prompt. */
export function extractAgentLabel(goal: string): string | undefined {
  const text = goal.trim()

  if (!text) {
    return undefined
  }

  const subagentType = text.match(/subagent_type\s*[=:]\s*["']?([\w-]+)/i)?.[1]
  if (subagentType) {
    return subagentType
  }

  const role = text.match(/\brole\s*[=:]\s*["']?(orchestrator|leaf)/i)?.[1]
  if (role && role.toLowerCase() !== 'leaf') {
    return role.toLowerCase()
  }

  const objective = text.match(/OBJECTIVE:\s*([\s\S]+?)(?:\n\S|$)/i)?.[1]?.trim()
  if (objective) {
    const short = objective.replace(/\s+/g, ' ')
    return short.length <= 48 ? short : undefined
  }

  return undefined
}

/** Short title for subagent rows — label when present, else first line of goal. */
export function formatSubagentTitle(goal: string, maxLen = 72): string {
  const label = extractAgentLabel(goal)
  if (label) {
    return label
  }

  const firstLine =
    goal
      .split('\n')
      .map(line => line.trim())
      .find(Boolean) ?? goal

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
