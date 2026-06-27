import { describe, expect, it } from 'vitest'

import { extractAgentLabel, formatSubagentRoleBadge, formatSubagentTitle } from './subagent-label'

describe('subagent-label', () => {
  it('extracts subagent_type from Task() prompts', () => {
    expect(extractAgentLabel('Task(subagent_type="orchestrator", prompt="...")')).toBe('orchestrator')
    expect(extractAgentLabel('OBJECTIVE: run analysis\nsubagent_type: code')).toBe('code')
  })

  it('extracts orchestrator role', () => {
    expect(extractAgentLabel('role="orchestrator"\nOBJECTIVE: plan')).toBe('orchestrator')
    expect(extractAgentLabel('role: leaf')).toBeUndefined()
  })

  it('shortens long goals', () => {
    const title = formatSubagentTitle('ФУЛЛ АНАЛИЗ репозитория /Users/foo/bar\n## КОНТЕКСТ')
    expect(title).toBe('ФУЛЛ АНАЛИЗ репозитория /Users/foo/bar')
  })

  it('formats role badge', () => {
    expect(formatSubagentRoleBadge('orchestrator')).toBe('orchestrator')
    expect(formatSubagentRoleBadge('leaf')).toBeUndefined()
  })
})
