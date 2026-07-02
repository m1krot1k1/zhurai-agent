---
name: headroom
description: "Headroom proxy stats, MCP compression, savings dashboard."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, compression, headroom, observability, tokens]
    category: mcp
    related_skills: [mcp-governance]
    config:
      - headroom.dashboard_url
---

# Headroom Skill

Headroom compresses LLM context and exposes `headroom_compress`, `headroom_retrieve`, and `headroom_stats` over MCP. With the proxy running, Hermes can call those tools and poll HTTP stats for savings dashboards.

## When to Use

- User asks about token savings, compression stats, or Headroom dashboard
- Installing or troubleshooting the Headroom MCP catalog entry
- Building dialog/UI that shows live or historical compression metrics
- On-demand compression of large tool output before reasoning (`headroom_compress`)

Do not use for Hermes built-in context compression (`compression` in config.yaml) — that is a separate subsystem.

## Prerequisites

- Headroom installed: `pip install "headroom-ai[proxy,mcp]"`
- Proxy listening (default `http://127.0.0.1:8787`): `headroom proxy`
- MCP catalog entry installed: `hermes mcp install official/headroom`
- Config base URL (optional override):

```yaml
headroom:
  dashboard_url: http://127.0.0.1:8787
```

## How to Run

1. Start proxy: `terminal` → `headroom proxy`
2. Install MCP: `hermes mcp install official/headroom` (once per profile)
3. New Hermes session so MCP tools probe against live `/mcp`
4. Check stats via MCP `headroom_stats` or HTTP (see Quick Reference)

## Quick Reference

| Surface | URL / command |
|---------|----------------|
| MCP endpoint | `{dashboard_url}/mcp` |
| Web dashboard | `{dashboard_url}/dashboard` |
| Live stats | `GET {dashboard_url}/stats` |
| History / charts | `GET {dashboard_url}/stats-history` |
| Config key | `headroom.dashboard_url` |

Default `dashboard_url`: `http://127.0.0.1:8787` (proxy base, no path suffix).

## Procedure

### Install and verify MCP

1. Confirm proxy health: `curl -sf http://127.0.0.1:8787/stats`
2. Run `hermes mcp install official/headroom` if not already configured
3. Restart session; confirm tools `headroom_compress`, `headroom_retrieve`, `headroom_stats` appear
4. Optional: `hermes mcp configure headroom` to adjust enabled tools

### Poll stats for dialog integration

1. Read `headroom.dashboard_url` from config (fallback `http://127.0.0.1:8787`)
2. **Headline counters:** `GET {base}/stats` every 5–30s while active; 60s when idle
3. **Trend charts:** `GET {base}/stats-history` every 60–300s or on user refresh
4. On HTTP failure: keep last payload, mark stale, do not block chat

### On-demand compression workflow

1. Large blob (logs, grep, JSON) exceeds useful context → call `headroom_compress` with `content`
2. Reason over returned `compressed` text; store `hash` from response
3. If full original needed → `headroom_retrieve` with `hash` (optional `query` filter)

## Pitfalls

- **Proxy not running** — MCP probe fails; start `headroom proxy` before install/session
- **Wrong port** — update `headroom.dashboard_url` and `mcp_servers.headroom.url` together
- **Expired retrieve** — local originals TTL ~1h; proxy store ~5min for retrieve fallback
- **Double compression** — proxy compresses HTTP traffic; MCP tools are on-demand and separate
- **Remote agents** — point transport URL at `http://<host>:8787/mcp` on the proxy machine

## Verification

- [ ] `curl -sf "$(hermes config get headroom.dashboard_url 2>/dev/null || echo http://127.0.0.1:8787)/stats"` returns JSON with `tokens` or `requests`
- [ ] `hermes mcp configure headroom` lists three Headroom tools when proxy is up
- [ ] `headroom_stats` MCP call returns `compressions` / `tokens_saved` fields
