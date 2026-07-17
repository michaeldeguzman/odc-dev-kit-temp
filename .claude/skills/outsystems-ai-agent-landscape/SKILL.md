---
name: outsystems-ai-agent-landscape
description: Generate an interactive HTML inventory + governance view of every AI agent and AI model connection in an OutSystems tenant. Shows provider breakdown (Amazon Bedrock / Azure OpenAI / Custom), Trial vs Customer entitlement audit, agent freshness, and "test/demo" name heuristics. Use when the user asks for an AI inventory, AI agents audit, AI governance view, "what AI is in my tenant", "show me my agents", "which models are we using", "AI compliance check", "audit my AI", or similar.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__context_agents mcp__outsystems__context_connections
metadata:
  version: "1.2.0"
  author: outsystems-r-and-d
---

# OutSystems AI Agent Landscape

Produces a self-contained HTML dashboard showing every AI agent and
every AI model connection in the tenant. Cards for the model
connections (provider, entitlement, description). A filterable,
sortable table for the agents (name, owner, last update, public flag,
description). Plus governance heuristics (Trial vs Customer count,
test/demo agent count, stale agents).

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. Shared rules: §7b
(`context_*` capped at `limit: 100`), §8 (token-efficiency).
`context_agents` typically trips auto-save at ~100 agents;
`context_connections` is small enough to come back inline.

## Procedure

### Step 1 — Auth + resolve tenant

Call `mcp__outsystems__auth_status`. If `logged_in: false`, stop.
Read `claims.aid` as `TENANT_ID`.

```
CACHE = ~/.claude/cache/outsystems-ai-agent-landscape/<TENANT_ID>/
SKILL = <this skill's directory>
mkdir -p "$CACHE"
```

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

### Step 2 — Cache freshness (only if cache exists)

If `$CACHE/meta.json` is present:
1. Call `mcp__outsystems__context_agents` with `limit: 1` (cheap probe,
   returns one agent + total via pagination).
2. Compute `AGE = now - meta.fetched_at`.
3. If `AGE < 3600` AND the response's `pagination.limit + offset`
   suggests the same total count as cached → **cache valid, jump to
   Step 4**.

If the user said "refresh" / "fresh data", skip this step.

### Step 3 — Fetch (parallel)

Call **both** of these in a single message so they run concurrently.
**Both with `limit: 100`** (the API max per CONVENTIONS §7b):

- `mcp__outsystems__context_agents` with `limit: 100`,
  `owned_only: false` (tenant-wide view)
- `mcp__outsystems__context_connections` with `limit: 100`,
  `owned_only: false`

For each response:

- **If the response is "Output has been saved to <path>"** (Claude Code
  harness auto-save for large results, typical for `context_agents`):
  note the path, `cp` it into `$CACHE/agents-raw.json`.
- **If inline JSON** (typical for `context_connections` — and for ALL
  responses on harnesses without auto-save, e.g. Codex): write a COMPACT
  form to the cache file per the whitelist below.

### Compact-write field whitelist (mandatory for inline responses)

| Section | Fields to keep |
|---|---|
| `agents-raw.json`      | data[].(key, name, description, ownerAppKey, isPublic, timestamp, additionalData.{revision, revisionDateTime}) |
| `connections-raw.json` | data[].(key, name, description, ownerAppKey, isPublic, timestamp, providerName, additionalData.{providerId, entitlement, revisionDateTime}) |

Compact JSON formatting (no whitespace inside objects). Wrap in
`{"data": [...]}` envelope.

### Step 4 — Build

```bash
OUT="${OUTPUT_PATH:-$PWD/ai-agent-landscape.html}"
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT" \
  --agents      "$CACHE/agents-raw.json" \
  --connections "$CACHE/connections-raw.json" \
  --tenant-id   "$TENANT_ID"
```

`build.py` computes:
- Provider breakdown (Amazon Bedrock / Azure OpenAI / Custom / etc.)
- Trial-vs-Customer entitlement counts
- "Test/demo" agent count (name heuristic: contains `test`, `tmp`,
  `demo`, `123`, `xxx`, or `untitled`)
- Stale agent count (no revision update in >180 days)
- Public-vs-internal split

### Step 5 — Cached re-render

```bash
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT"
```

### Step 6 — Report (3–5 lines)

- Output file path
- Counts: N agents · M connections (X Trial / Y Customer)
- Risk highlights: # test/demo agents, # stale agents, providers in use
- Cache state — "used (Xs old)" or "refreshed"

## Data shape contract

`build.py` writes `$CACHE/landscape-data.json` matching this shape:

```js
LANDSCAPE_DATA = {
  tenant: { id },
  agents: [ { k, n, desc, owner, pub, date, isTestDemo: bool, isStale: bool } ],
  connections: [ { k, n, desc, provider, providerId, entitlement, date } ],
  stats: {
    totalAgents, totalConnections,
    trialConns, customerConns,
    publicAgents, internalAgents,
    testDemoAgents, staleAgents,
    providers: [ { name, count } ]
  }
}
```

## Cache rules

- Location: `~/.claude/cache/outsystems-ai-agent-landscape/<tenant-id>/`
- TTL: 1 hour
- Freshness check: agent count from `context_agents?limit:1`
- Force refresh: "refresh" / "fresh data" / "rebuild"

## Token budget (estimate, ~100 agents)

| Scenario | Mechanism | Total |
|---|---|---|
| First run | Connections inline (compact) + agents harness-saved | **~3-4K** |
| Cached run | Probe + build.py | ~2K |
| Re-render only | build.py | ~1K |

The agents auto-save is what keeps this cheap — without it (i.e. for
tenants with very few agents that come back inline) the cost would
roughly double on the agents Write.

## Harness notes

- **Claude Code**: large MCP results (>~25 KB) are auto-saved to disk by
  the harness ("Output has been saved to <path>") and never enter model
  context. This is the cheapest path (see Token budget).
- **Codex**: no auto-save equivalent — large `context_agents` responses
  arrive inline and are counted into context once (~50–150 KB for ~100
  agents) before being compacted to the cache file. The skill works
  unchanged; expect roughly 2x the first-run token cost. Cached runs and
  re-renders cost the same as on Claude Code.
- Cache location `~/.claude/cache/` is shared across harnesses (see
  Step 1 note).

## Troubleshooting

- **`context_agents` returns inline (no harness save)** → small tenant,
  fewer than ~50 agents. Use the compact-Write path normally.
- **Tenant has >100 agents** → paginate: call `context_agents` with
  `limit:100, offset:0`, then `offset:100`, etc. Concatenate the
  `data` arrays before passing to `build.py`.
- **Provider grouping looks wrong** → providers come from
  `additionalData.providerId` (`amazonbedrock`, `azureopenai`,
  `customconnection`). `build.py` has a hardcoded map; extend it if
  new provider IDs appear.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.1, §8.4, don't `Read` the
harness-saved file). Skill-specific:

- **Don't fetch with `owned_only: true`** when no `app` is set — that's
  the app-scoped path. Tenant-wide view requires `owned_only: false`.

## When NOT to use

- User wants a deep view of one specific agent → use
  `outsystems-app-architecture` with that agent's key (agents are apps).
- User wants the full tenant inventory across all asset types → use
  `outsystems-tenant-architecture`.
- User wants per-customer / per-team breakdown of AI usage → that's a
  reporting tier this v1.0 doesn't cover. Future skill.
