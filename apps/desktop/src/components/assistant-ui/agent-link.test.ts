import { describe, expect, it } from 'vitest'

import { agentIdFromMarkdownHref } from './agent-link'

describe('agentIdFromMarkdownHref', () => {
  it('returns subagent ids for non-url hrefs', () => {
    expect(agentIdFromMarkdownHref('sa-0-deadbeef')).toBe('sa-0-deadbeef')
    expect(agentIdFromMarkdownHref('delegate-tool:abc:0')).toBe('delegate-tool:abc:0')
  })

  it('rejects http(s) and hermes special links', () => {
    expect(agentIdFromMarkdownHref('https://example.com')).toBeNull()
    expect(agentIdFromMarkdownHref('http://localhost/x')).toBeNull()
    expect(agentIdFromMarkdownHref('#media:foo.png')).toBeNull()
    expect(agentIdFromMarkdownHref('#preview:file.txt')).toBeNull()
    expect(agentIdFromMarkdownHref('mailto:a@b.c')).toBeNull()
  })

  it('supports explicit agent: prefixes', () => {
    expect(agentIdFromMarkdownHref('#agent:sa-1-abc')).toBe('sa-1-abc')
    expect(agentIdFromMarkdownHref('agent:sa-1-abc')).toBe('sa-1-abc')
  })
})
