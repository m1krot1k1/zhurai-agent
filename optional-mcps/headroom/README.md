# Headroom (optional MCP catalog entry)

[Headroom](https://headroom-docs.vercel.app/docs/mcp) compresses LLM context and exposes compression, retrieval, and stats as MCP tools. When the proxy runs locally, Hermes connects via the catalog entry at `http://127.0.0.1:8787/mcp`.

## Prerequisites

```bash
pip install "headroom-ai[proxy,mcp]"
headroom proxy   # binds http://127.0.0.1:8787 by default
```

Install into Hermes:

```bash
hermes mcp install official/headroom
```

## Config

Non-secret settings live in `config.yaml` (not `.env`):

```yaml
headroom:
  dashboard_url: http://127.0.0.1:8787
```

`headroom.dashboard_url` is the **proxy base URL** (scheme + host + port, no trailing slash). UI and dialog integrations derive paths from it:

| Path | Purpose |
|------|---------|
| `/dashboard` | Built-in web dashboard (historical charts) |
| `/stats` | Live session stats + `persistent_savings` lifetime totals |
| `/stats-history` | Durable hourly/daily/weekly/monthly rollups (powers dashboard charts) |
| `/mcp` | Streamable HTTP MCP endpoint (Hermes catalog transport) |

Override the default port in config when the proxy binds elsewhere.

## Stats endpoints (dialog / polling)

### Live stats — `GET {dashboard_url}/stats`

Poll for current request counts, token savings, cache hits, and budget status.

```bash
curl -s http://127.0.0.1:8787/stats | jq .
```

Typical JSON blocks: `requests`, `tokens`, `cost`, `cache`, `persistent_savings`.

Example response (fields may vary by Headroom version):

```json
{
  "requests": { "total": 42, "cached": 5, "failed": 0 },
  "tokens": { "input": 50000, "output": 8000, "saved": 12500, "savings_percent": 25.0 },
  "cost": { "total_cost_usd": 0.15, "total_savings_usd": 0.04 },
  "persistent_savings": {
    "lifetime": { "tokens_saved": 12500, "compression_savings_usd": 0.04 }
  }
}
```

**Polling pattern for dialog UI:** poll every 5–30s while a session is active; back off to 60s when idle. Treat connection errors as proxy-down (show last-known stats + stale badge). Read `headroom.dashboard_url` from Hermes config (default `http://127.0.0.1:8787`); derive `{base}/stats` and `{base}/dashboard` from that value.

### Historical stats — `GET {dashboard_url}/stats-history`

Durable compression history survives proxy restarts. Used for charts and export.

```bash
curl -s http://127.0.0.1:8787/stats-history | jq .
curl -s "http://127.0.0.1:8787/stats-history?format=csv&series=weekly"
```

Query params (optional): `format=csv`, `series=daily|weekly|monthly`, `history_mode=full`.

**Polling pattern for dialog UI:** poll every 60–300s for chart refresh; fetch on explicit user “refresh savings” action. Prefer `/stats-history` for trend lines; use `/stats` for headline counters.

### MCP alternative — `headroom_stats` tool

When MCP is connected, call `headroom_stats` instead of raw HTTP for session compression metrics (includes sub-agent aggregation via `~/.headroom/session_stats.jsonl`).

## Security

The default proxy has **no authentication**. Bind to localhost only; do not expose port 8787 on untrusted networks without a separate gate.
