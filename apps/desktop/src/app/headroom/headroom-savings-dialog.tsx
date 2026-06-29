import { useStore } from '@nanostores/react'
import { useCallback, useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { useI18n } from '@/i18n'
import { openExternalLink } from '@/lib/external-link'
import { BarChart3, ExternalLink, RefreshCw } from '@/lib/icons'
import { cn } from '@/lib/utils'
import {
  $headroomDashboardUrl,
  $headroomDialogOpen,
  closeHeadroomDialog,
  DEFAULT_HEADROOM_DASHBOARD_URL,
  headroomDashboardUrl,
  headroomStatsUrl,
  normalizeHeadroomBaseUrl,
  refreshHeadroomDashboardUrl
} from '@/store/headroom'

type HeadroomStatsSnapshot = {
  requests?: number
  tokensSaved?: number
  costSaved?: number
  cacheHits?: number
  lifetimeTokensSaved?: number
}

function formatCount(value: number | undefined): string {
  if (value === undefined || Number.isNaN(value)) {
    return '—'
  }

  return value.toLocaleString()
}

function formatUsd(value: number | undefined): string {
  if (value === undefined || Number.isNaN(value)) {
    return '—'
  }

  return `$${value.toFixed(4)}`
}

function parseStatsPayload(payload: unknown): HeadroomStatsSnapshot | null {
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

function StatCard({ className, label, value }: { className?: string; label: string; value: string }) {
  return (
    <div
      className={cn(
        'rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-sidebar-surface-background)/60 px-3 py-2.5',
        className
      )}
    >
      <p className="text-[0.68rem] font-medium uppercase tracking-wide text-(--ui-text-quaternary)">{label}</p>
      <p className="mt-1 font-mono text-[0.9375rem] tabular-nums text-foreground">{value}</p>
    </div>
  )
}

export function HeadroomSavingsDialog({ baseUrl }: { baseUrl?: string }) {
  const { t } = useI18n()
  const h = t.headroom
  const open = useStore($headroomDialogOpen)
  const configBaseUrl = useStore($headroomDashboardUrl)
  const [stats, setStats] = useState<HeadroomStatsSnapshot | null>(null)
  const [stale, setStale] = useState(false)
  const [loading, setLoading] = useState(false)

  const normalizedBase = normalizeHeadroomBaseUrl(baseUrl ?? configBaseUrl ?? DEFAULT_HEADROOM_DASHBOARD_URL)
  const dashboardHref = headroomDashboardUrl(normalizedBase)

  const refreshStats = useCallback(async () => {
    setLoading(true)

    try {
      const response = await fetch(headroomStatsUrl(normalizedBase), {
        cache: 'no-store',
        signal: AbortSignal.timeout(4_000)
      })

      if (!response.ok) {
        throw new Error(`stats ${response.status}`)
      }

      const parsed = parseStatsPayload(await response.json())
      setStats(parsed)
      setStale(false)
    } catch {
      setStale(true)
    } finally {
      setLoading(false)
    }
  }, [normalizedBase])

  useEffect(() => {
    void refreshHeadroomDashboardUrl()
  }, [])

  useEffect(() => {
    if (!open) {
      return
    }

    void refreshHeadroomDashboardUrl()
    void refreshStats()
    const timer = window.setInterval(() => void refreshStats(), 15_000)

    return () => window.clearInterval(timer)
  }, [open, refreshStats])

  const openDashboard = () => {
    openExternalLink(dashboardHref)
  }

  return (
    <Dialog
      onOpenChange={next => {
        if (!next) {
          closeHeadroomDialog()
        }
      }}
      open={open}
    >
      <DialogContent className="max-w-md gap-4">
        <DialogHeader>
          <DialogTitle icon={BarChart3}>{h.title}</DialogTitle>
          <DialogDescription>{h.description}</DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-2.5">
          <StatCard label={h.stats.requests} value={formatCount(stats?.requests)} />
          <StatCard label={h.stats.tokensSaved} value={formatCount(stats?.tokensSaved)} />
          <StatCard label={h.stats.costSaved} value={formatUsd(stats?.costSaved)} />
          <StatCard label={h.stats.cacheHits} value={formatCount(stats?.cacheHits)} />
          <StatCard
            className="col-span-2"
            label={h.stats.lifetimeTokensSaved}
            value={formatCount(stats?.lifetimeTokensSaved)}
          />
        </div>

        {stale && (
          <p className="text-[0.72rem] text-muted-foreground/90">{h.proxyUnavailable(normalizedBase)}</p>
        )}

        <DialogFooter className="gap-2 sm:justify-between">
          <Button
            className="gap-1.5"
            disabled={loading}
            onClick={() => void refreshStats()}
            type="button"
            variant="ghost"
          >
            <RefreshCw className={cn('size-3.5', loading && 'animate-spin')} />
            {h.refresh}
          </Button>
          <Button className="gap-1.5" onClick={openDashboard} type="button">
            <ExternalLink className="size-3.5" />
            {h.openInBrowser}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
