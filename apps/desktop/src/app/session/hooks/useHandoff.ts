import type { MutableRefObject } from 'react'

import { delay, inlineErrorMessage } from './use-prompt-actions'

interface HandoffResult {
  ok: boolean
  error?: string
}

interface HandoffOptions {
  activeSessionIdRef: MutableRefObject<string | null>
  appendSessionTextMessage: (sessionId: string, role: 'system', text: string) => void
  copy: any
  requestGateway: <T>(method: string, params?: Record<string, unknown>) => Promise<T>
}

export function useHandoff({ activeSessionIdRef, appendSessionTextMessage, copy, requestGateway }: HandoffOptions) {
  const handoffSession = async (
    platform: string,
    options?: { onProgress?: (state: string) => void; sessionId?: string }
  ): Promise<HandoffResult> => {
    const sid = options?.sessionId || activeSessionIdRef.current

    if (!sid) {
      return { error: copy.sessionUnavailable, ok: false }
    }

    const target = platform.trim().toLowerCase()

    if (!target) {
      return { error: copy.handoff.failed(''), ok: false }
    }

    try {
      options?.onProgress?.('pending')
      await requestGateway('handoff.request', {
        platform: target,
        session_id: sid
      })
    } catch (err) {
      return { error: inlineErrorMessage(err, copy.handoff.failed(target)), ok: false }
    }

    const deadline = Date.now() + 60_000
    let lastState = 'pending'

    while (Date.now() < deadline) {
      await delay(800)

      let record: any

      try {
        record = await requestGateway('handoff.state', { session_id: sid })
      } catch {
        continue
      }

      const state = record.state || 'pending'

      if (state !== lastState) {
        options?.onProgress?.(state)
        lastState = state
      }

      if (state === 'completed') {
        appendSessionTextMessage(sid, 'system', copy.handoff.systemNote(target))
        return { ok: true }
      }

      if (state === 'failed') {
        return { error: record.error || copy.handoff.failed(target), ok: false }
      }
    }

    const cleanup = await requestGateway('handoff.fail', {
      error: copy.handoff.timedOut,
      session_id: sid
    }).catch(() => null)

    if ((cleanup as any)?.state === 'completed') {
      appendSessionTextMessage(sid, 'system', copy.handoff.systemNote(target))
      return { ok: true }
    }

    return { error: copy.handoff.timedOut, ok: false }
  }

  return { handoffSession }
}
