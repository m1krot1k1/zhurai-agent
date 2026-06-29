import { describe, expect, it, vi } from 'vitest'

import {
  DEFAULT_HEADROOM_DASHBOARD_URL,
  headroomDashboardUrl,
  headroomDashboardUrlFromConfig,
  headroomStatsUrl,
  isHttpHttpsUrl,
  normalizeHeadroomBaseUrl,
  openHeadroomExternalUrl,
  parseStatsPayload
} from './headroom'

describe('normalizeHeadroomBaseUrl', () => {
  it('trims whitespace and trailing slashes', () => {
    expect(normalizeHeadroomBaseUrl('  http://127.0.0.1:8787/  ')).toBe('http://127.0.0.1:8787')
    expect(normalizeHeadroomBaseUrl('http://host///')).toBe('http://host')
  })
})

describe('headroomDashboardUrlFromConfig', () => {
  it('reads dashboard_url from headroom config', () => {
    expect(
      headroomDashboardUrlFromConfig({
        headroom: { dashboard_url: 'http://custom:9999/' }
      })
    ).toBe('http://custom:9999')
  })

  it('falls back to default when config is missing or invalid', () => {
    expect(headroomDashboardUrlFromConfig({})).toBe(DEFAULT_HEADROOM_DASHBOARD_URL)
    expect(headroomDashboardUrlFromConfig({ headroom: { dashboard_url: '   ' } })).toBe(
      DEFAULT_HEADROOM_DASHBOARD_URL
    )
  })
})

describe('headroomStatsUrl', () => {
  it('appends /stats to the normalized base', () => {
    expect(headroomStatsUrl('http://127.0.0.1:8787/')).toBe('http://127.0.0.1:8787/stats')
    expect(headroomDashboardUrl()).toBe('http://127.0.0.1:8787/dashboard')
  })
})

describe('parseStatsPayload', () => {
  it('returns null for non-object payloads', () => {
    expect(parseStatsPayload(null)).toBeNull()
    expect(parseStatsPayload(undefined)).toBeNull()
    expect(parseStatsPayload('stats')).toBeNull()
    expect(parseStatsPayload(42)).toBeNull()
  })

  it('parses canonical Headroom stats blocks', () => {
    expect(
      parseStatsPayload({
        cache: { hits: 12 },
        cost: { saved_usd: 0.0042 },
        persistent_savings: { tokens_saved: 50_000 },
        requests: { total: 100 },
        tokens: { saved: 25_000 }
      })
    ).toEqual({
      cacheHits: 12,
      costSaved: 0.0042,
      lifetimeTokensSaved: 50_000,
      requests: 100,
      tokensSaved: 25_000
    })
  })

  it('accepts alternate field names within each block', () => {
    expect(
      parseStatsPayload({
        cache: { hit_count: 3 },
        cost: { savings_usd: 1.5 },
        persistent_savings: { lifetime_tokens_saved: 900 },
        requests: { count: 7 },
        tokens: { saved_total: 400 }
      })
    ).toEqual({
      cacheHits: 3,
      costSaved: 1.5,
      lifetimeTokensSaved: 900,
      requests: 7,
      tokensSaved: 400
    })
  })

  it('prefers the first finite number when multiple aliases are present', () => {
    expect(
      parseStatsPayload({
        cache: { hit_count: 99, hits: 1 },
        cost: { saved: 0.5, saved_usd: 0.1 },
        requests: { count: 5, total: 50 },
        tokens: { saved: 10, saved_total: 20 }
      })
    ).toEqual({
      cacheHits: 1,
      costSaved: 0.1,
      lifetimeTokensSaved: undefined,
      requests: 50,
      tokensSaved: 10
    })
  })

  it('ignores non-finite numbers and string numerics', () => {
    expect(
      parseStatsPayload({
        cache: { hits: NaN },
        cost: { saved_usd: Infinity },
        requests: { total: '100' },
        tokens: { saved: null }
      })
    ).toEqual({
      cacheHits: undefined,
      costSaved: undefined,
      lifetimeTokensSaved: undefined,
      requests: undefined,
      tokensSaved: undefined
    })
  })

  it('returns an empty snapshot shape for an empty object', () => {
    expect(parseStatsPayload({})).toEqual({
      cacheHits: undefined,
      costSaved: undefined,
      lifetimeTokensSaved: undefined,
      requests: undefined,
      tokensSaved: undefined
    })
  })
})

describe('isHttpHttpsUrl', () => {
  it('accepts http and https URLs', () => {
    expect(isHttpHttpsUrl('http://127.0.0.1:8787/dashboard')).toBe(true)
    expect(isHttpHttpsUrl('https://headroom.example/stats')).toBe(true)
    expect(isHttpHttpsUrl('  https://example.com  ')).toBe(true)
  })

  it('rejects non-http(s) schemes and invalid URLs', () => {
    expect(isHttpHttpsUrl('javascript:alert(1)')).toBe(false)
    expect(isHttpHttpsUrl('file:///etc/passwd')).toBe(false)
    expect(isHttpHttpsUrl('data:text/plain,hi')).toBe(false)
    expect(isHttpHttpsUrl('not-a-url')).toBe(false)
    expect(isHttpHttpsUrl('')).toBe(false)
    expect(isHttpHttpsUrl('   ')).toBe(false)
  })
})

describe('openHeadroomExternalUrl', () => {
  it('calls openExternal only for http(s) URLs', () => {
    const openExternal = vi.fn()
    vi.stubGlobal('window', { hermesDesktop: { openExternal } })

    openHeadroomExternalUrl('https://example.com/dashboard')
    expect(openExternal).toHaveBeenCalledWith('https://example.com/dashboard')

    openHeadroomExternalUrl('javascript:alert(1)')
    expect(openExternal).toHaveBeenCalledTimes(1)

    vi.unstubAllGlobals()
  })
})
