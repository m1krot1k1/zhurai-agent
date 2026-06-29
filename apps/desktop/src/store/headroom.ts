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
