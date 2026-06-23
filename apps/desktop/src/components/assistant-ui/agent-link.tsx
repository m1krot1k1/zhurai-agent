'use client'

import { type ComponentProps, type ReactNode, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

import { AGENTS_ROUTE } from '@/app/routes'
import { Sparkles } from '@/lib/icons'
import { cn } from '@/lib/utils'
import { setFocusSubagentId } from '@/store/subagents'

const URL_SCHEME_RE = /^[a-z][a-z0-9+.-]*:/i

/**
 * Returns a subagent id when `href` is a Cursor-style agent reference
 * `[label](agent-id)` rather than an external URL or Hermes media/preview link.
 */
export function agentIdFromMarkdownHref(href?: string): string | null {
  if (!href) {
    return null
  }

  const raw = href.trim()

  if (!raw || /^https?:\/\//i.test(raw)) {
    return null
  }

  if (raw.startsWith('#media:') || raw.startsWith('#preview:') || raw.startsWith('#preview/')) {
    return null
  }

  if (URL_SCHEME_RE.test(raw)) {
    return null
  }

  // Absolute filesystem-style paths are not agent ids.
  if (raw.startsWith('/') && !raw.startsWith('//')) {
    return null
  }

  if (raw.startsWith('#agent:')) {
    try {
      return decodeURIComponent(raw.slice('#agent:'.length))
    } catch {
      return raw.slice('#agent:'.length)
    }
  }

  if (raw.startsWith('agent:')) {
    try {
      return decodeURIComponent(raw.slice('agent:'.length))
    } catch {
      return raw.slice('agent:'.length)
    }
  }

  try {
    return decodeURIComponent(raw)
  } catch {
    return raw
  }
}

export const AGENT_LINK_CHIP_CLASS =
  'mx-0.5 inline-flex max-w-56 cursor-pointer items-center gap-1 rounded px-1.5 py-0.5 align-middle text-[0.86em] font-medium leading-none bg-[color-mix(in_srgb,var(--ui-accent)_14%,transparent)] text-[color-mix(in_srgb,var(--ui-accent)_82%,var(--foreground))] underline-offset-2 hover:bg-[color-mix(in_srgb,var(--ui-accent)_22%,transparent)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/60'

interface AgentLinkProps extends Omit<ComponentProps<'button'>, 'children' | 'onClick' | 'type'> {
  agentId: string
  children: ReactNode
}

export function AgentLink({ agentId, children, className, ...props }: AgentLinkProps) {
  const navigate = useNavigate()

  const openAgent = useCallback(() => {
    setFocusSubagentId(agentId)
    navigate(AGENTS_ROUTE)
  }, [agentId, navigate])

  return (
    <button
      className={cn(AGENT_LINK_CHIP_CLASS, className)}
      data-agent-id={agentId}
      data-slot="aui_agent-link"
      onClick={openAgent}
      title={agentId}
      type="button"
      {...props}
    >
      <Sparkles aria-hidden className="size-3 shrink-0 opacity-80" />
      <span className="truncate">{children}</span>
    </button>
  )
}
