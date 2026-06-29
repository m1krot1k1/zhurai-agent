import { atom } from 'nanostores'

import { getHermesConfigRecord } from '@/hermes'
import type { HermesConfigRecord } from '@/types/hermes'

/** Default Headroom proxy base URL (see optional-mcps/headroom/README.md). */
export const DEFAULT_HEADROOM_DASHBOARD_URL = 'http://127.0.0.1:8787'

export const $headroomDashboardUrl = atom(DEFAULT_HEADROOM_DASHBOARD_URL)

export const $headroomDialogOpen = atom(false)

export function headroomDashboardUrlFromConfig(config: HermesConfigRecord): string {
  const headroom = config.headroom

  if (headroom && typeof headroom === 'object') {
    const url = (headroom as Record<string, unknown>).dashboard_url

    if (typeof url === 'string' && url.trim()) {
      return normalizeHeadroomBaseUrl(url)
    }
  }

  return DEFAULT_HEADROOM_DASHBOARD_URL
}

export async function refreshHeadroomDashboardUrl(): Promise<void> {
  try {
    const config = await getHermesConfigRecord()
    $headroomDashboardUrl.set(headroomDashboardUrlFromConfig(config))
  } catch {
    $headroomDashboardUrl.set(DEFAULT_HEADROOM_DASHBOARD_URL)
  }
}

export function openHeadroomDialog(): void {
  $headroomDialogOpen.set(true)
}

export function closeHeadroomDialog(): void {
  $headroomDialogOpen.set(false)
}

export function toggleHeadroomDialog(): void {
  $headroomDialogOpen.set(!$headroomDialogOpen.get())
}

export function normalizeHeadroomBaseUrl(raw: string): string {
  return raw.trim().replace(/\/+$/, '')
}

export function headroomDashboardUrl(baseUrl = DEFAULT_HEADROOM_DASHBOARD_URL): string {
  return `${normalizeHeadroomBaseUrl(baseUrl)}/dashboard`
}

export function headroomStatsUrl(baseUrl = DEFAULT_HEADROOM_DASHBOARD_URL): string {
  return `${normalizeHeadroomBaseUrl(baseUrl)}/stats`
}

export type HeadroomStatsSnapshot = {
  requests?: number
  tokensSaved?: number
  costSaved?: number
  cacheHits?: number
  lifetimeTokensSaved?: number
}

export function parseStatsPayload(payload: unknown): HeadroomStatsSnapshot | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  const root = payload as Record<string, unknown>
  const requestsBlock = root.requests as Record<string, unknown> | undefined
  const tokensBlock = root.tokens as Record<string, unknown> | undefined
  const costBlock = root.cost as Record<string, unknown> | undefined
  const cacheBlock = root.cache as Record<string, unknown> | undefined
  const persistent = root.persistent_savings as Record<string, unknown> | undefined

  const readNumber = (...values: unknown[]): number | undefined => {
    for (const value of values) {
      if (typeof value === 'number' && Number.isFinite(value)) {
        return value
      }
    }

    return undefined
  }

  return {
    cacheHits: readNumber(cacheBlock?.hits, cacheBlock?.hit_count),
    costSaved: readNumber(costBlock?.saved_usd, costBlock?.saved, costBlock?.savings_usd),
    lifetimeTokensSaved: readNumber(
      persistent?.tokens_saved,
      persistent?.total_tokens_saved,
      persistent?.lifetime_tokens_saved
    ),
    requests: readNumber(requestsBlock?.total, requestsBlock?.count),
    tokensSaved: readNumber(tokensBlock?.saved, tokensBlock?.saved_total, tokensBlock?.savings)
  }
}

/** True only for absolute http:// or https:// URLs (rejects javascript:, file:, data:, etc.). */
export function isHttpHttpsUrl(raw: string): boolean {
  const trimmed = raw.trim()

  if (!trimmed) {
    return false
  }

  const lower = trimmed.toLowerCase()
  if (!lower.startsWith('http://') && !lower.startsWith('https://')) {
    return false
  }

  try {
    const parsed = new URL(trimmed)

    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

/** Open a URL in the system browser; no-op unless the URL is http(s). */
export function openHeadroomExternalUrl(url: string): void {
  if (!isHttpHttpsUrl(url)) {
    return
  }

  void window.hermesDesktop?.openExternal?.(url)
}

export function openHeadroomDashboardInBrowser(baseUrl = $headroomDashboardUrl.get()): void {
  openHeadroomExternalUrl(headroomDashboardUrl(baseUrl))
}
