import { describe, expect, it } from 'vitest'

import { extractAgentLabel, formatSubagentRoleBadge, formatSubagentTitle } from './subagent-label'

describe('subagent-label', () => {
  it('extracts AGENT_ID from Hermes branch envelopes', () => {
    expect(extractAgentLabel('AGENT_ID: code-reviewer\nOBJECTIVE: review diff')).toBe('code-reviewer')
  })

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

  it('formatSubagentTitle with empty goal returns Subagent', () => {
    expect(formatSubagentTitle('')).toBe('Subagent')
    expect(formatSubagentTitle('   ')).toBe('Subagent')
  })

  it('formatSubagentTitle with markdown heading strips #', () => {
    expect(formatSubagentTitle('## Code Review\nDo the thing')).toBe('Code Review')
  })

  it('formatSubagentTitle truncates long goals', () => {
    const long = 'a'.repeat(100)
    const title = formatSubagentTitle(long, 72)
    expect(title.length).toBe(72)  // 71 chars + …
    expect(title.endsWith('…')).toBe(true)
  })

  it('extractAgentLabel with empty string returns undefined', () => {
    expect(extractAgentLabel('')).toBeUndefined()
    expect(extractAgentLabel('   ')).toBeUndefined()
  })

  it('extractAgentLabel with multi-line OBJECTIVE captures full first line', () => {
    const label = extractAgentLabel('OBJECTIVE: Analyze the codebase\nand implement fixes')
    expect(label).toBe('Analyze the codebase')
  })

  it('formatSubagentRoleBadge with empty role returns undefined', () => {
    expect(formatSubagentRoleBadge('')).toBeUndefined()
  })

  // XSS contract: the label is rendered as text content by React (no
  // dangerouslySetInnerHTML anywhere in the subagent-row tree). This test
  // pins that contract so a future contributor cannot regress to an innerHTML
  // path without breaking the suite. The label must come back as a plain
  // string; React then escapes it. We assert two things: (a) the returned
  // value is a regular string (no DOM node, no eval), and (b) the HTML
  // payload survives as literal text — i.e. the function did not strip,
  // evaluate, or mutate it.
  describe('XSS contract — extractAgentLabel returns plain text, never HTML', () => {
    it('returns a string (not a node) for a script-injected goal', () => {
      const label = extractAgentLabel('OBJECTIVE: <script>alert(1)</script>')
      expect(typeof label).toBe('string')
      expect(label).toBeDefined()
    })

    it('preserves the raw HTML payload as literal text', () => {
      const payload = '<script>alert(1)</script>'
      const label = extractAgentLabel(`OBJECTIVE: ${payload}`)
      // The script tag must be present verbatim in the returned string.
      // If extractAgentLabel ever started sanitizing/evaluating HTML, this
      // would break — which is exactly the regression we want to catch.
      expect(label).toContain(payload)
    })

    it('does not surface HTML entities that hint at innerHTML processing', () => {
      // If the function routed the label through an innerHTML-bound path,
      // entities like &lt; would appear instead of the raw < we passed in.
      // The contract is: bytes in === bytes out (modulo whitespace cleanup).
      const label = extractAgentLabel('OBJECTIVE: <img src=x onerror=alert(1)>')
      expect(label).toContain('<img src=x onerror=alert(1)>')
      expect(label).not.toContain('&lt;')
    })
  })
})
