---
name: outsystems-tenant-architecture
description: Generate an interactive HTML graph visualization of an OutSystems Developer Cloud tenant's assets (web/mobile apps, AI agents, AI model connections, libraries, integrations) with filter-by-type controls and OutSystems-themed dark mode styling. ONE tenant-level pass per invocation — does NOT loop into per-app deep dives (use outsystems-app-architecture separately for that). First run takes 2-5 min on healthy upstream; subsequent runs are cached (~5s). For demos, warm the cache once beforehand and show the cached path live. Use when the user asks for a tenant overview, architecture diagram, asset inventory, "what's in my tenant", "show me my apps", or similar.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: AskUserQuestion Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__env_list mcp__outsystems__app_list
metadata:
  version: "1.5.0"
  author: outsystems-r-and-d
---

# OutSystems Tenant Architecture

Produces a self-contained HTML file with a force-directed graph of every
asset in the user's ODC tenant. OutSystems dark theme, filter-by-type
sidebar, click for asset details. Caches results across sessions; the
first run is nearly as cheap as a cached run.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. Shared rules:
CONVENTIONS §7b (API quirks), §8.1–§8.6 (token-efficiency including
the harness-disk auto-save pattern this skill is built around).

## Procedure

### Step 0 — Scope guard (NEW v1.4.2 — demo-perf field-test, Sezen + Sofia)

This skill produces **one tenant-level visualization** per invocation,
**not per-app deep dives**. Read the user's request and pick the
matching branch:

**Branch A — Tenant-only view** ("show me my tenant", "what's in my
tenant", "tenant architecture", "ECG", "show me my apps")
→ Continue the procedure as normal.

**Branch B — Tenant + per-app deep dives** ("show me everything in
detail", "architecture of every app", "deep dive on each app")
→ **Stop and ask the user for confirmation.** Chaining
`outsystems-app-architecture` over every app costs ~10K tokens per app —
100 apps = ~1M tokens = ~$3-5 + 30-60 min wall time. Surface the
trade-off:

```
Question: "Run tenant view first, then per-app deep dives?"
Header:   "Scope?"
Options:
  - "Tenant only (Recommended)"
    description: "Produces the tenant ECG in 2-5 min. Run
                  outsystems-app-architecture per-app afterward only
                  for apps you want to drill into."
  - "Tenant + per-app for ALL apps"
    description: "Will spawn outsystems-app-architecture for each app.
                  N apps × ~10K tokens = ~{N*10}K tokens, ~{N*0.5}-{N*1} min wall time."
  - "Cancel"
    description: "Aborts."
```

Default to Branch A on ambiguity ("show me the ECG" → tenant-only).

**Why Step 0 exists (field-test note, 2026-06-12 Demo Team thread):**
Sezen reported 20 min, Sofia reported 10 min — both significantly
longer than the documented 2-5 min for a typical tenant. The leading
suspect is unintentional skill chaining ("show me the ECG"
interpreted as "tenant + every app deeply"). Step 0 is the gate.

### Step 0.5 — Demo prep tip

If the user is **prepping for a demo**: run this skill once **before
the demo** to warm the cache. During the demo, the same invocation
hits Step 5 (cached re-render) in ~5 seconds — looks instant on
screen. **Don't run the first-time path live in a demo.** The 2-5
min wait will tank the demo's energy. This is documented in the
catalog README and worth saying out loud to demo-team SAs.

### Step 1 — Auth + resolve tenant

Call `mcp__outsystems__auth_status`. If `logged_in: false`, stop and
ask the user to authenticate, then read `claims.aid` as `TENANT_ID`.

```
CACHE = ~/.claude/cache/outsystems-tenant-architecture/<TENANT_ID>/
SKILL = <this skill's directory>
mkdir -p "$CACHE"
```

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

### Step 2 — Cache freshness (only if cache exists)

If `$CACHE/meta.json` is present:

1. Call `mcp__outsystems__app_list` with `limit: 1` (tiny — ~300 tokens).
2. Compute `AGE = now - meta.fetched_at`.
3. If `AGE < 3600` **and** `probe.total == meta.total` → **cache valid,
   jump to Step 5** (cached re-render).

If the user said "refresh" / "fresh data" / "rebuild", skip this step.

### Step 3 — Fetch (parallel)

Call **both** of these in a single message so they run concurrently:

- `mcp__outsystems__env_list` — small response, ~700 bytes
- `mcp__outsystems__app_list` with `limit: 1000` — deliberately oversized

Save the env response to `$CACHE/envs-raw.json`.

For the app_list response, **inspect the result text**:

- **If it contains** `"Output has been saved to <path>"` (Claude Code's
  harness auto-save for large results, typical for tenants above ~150
  assets): extract the file path. That is `RAW_APPS` for Step 4.
- **If it returned an inline JSON object** `{"results":[...], "total":N}`
  (small-tenant path on Claude Code — and always the case on harnesses
  without auto-save, e.g. Codex): save it to `$CACHE/apps-raw.json`.
  That is `RAW_APPS` for Step 4.

### Step 4 — Build (fresh mode)

One Python invocation does the entire pipeline: transform raw MCP
responses into compact cache files, then inject into the template.

```bash
OUT="${OUTPUT_PATH:-$PWD/tenant-architecture.html}"
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT" "$RAW_APPS" "$TENANT_ID"
```

That's it. No `jq`, no separate transform-then-inject step.

### Step 5 — Build (cached mode)

When the cache is valid (jumped from Step 2), `build.py` is called with
just the cache and output path — it uses the existing compact cache
files directly:

```bash
OUT="${OUTPUT_PATH:-$PWD/tenant-architecture.html}"
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT"
```

### Step 6 — Report (3–5 lines)

- Output file path
- Asset count + 3-bucket breakdown (apps / agents / libraries+integrations)
- Cache state — "used (Xs old)" or "refreshed"
- Self-contained, opens in any browser

## Token budget — honest by tenant size band (revised v1.4.2)

The first-run cost has **three distinct bands** depending on tenant size,
because of how Claude Code's harness disk-save threshold (~25 KB tool
result) interacts with `app_list` payload sizes. On harnesses without
that auto-save (Codex), every `app_list` response arrives inline
regardless of size — see Harness notes for the equivalent cost model.

| Tenant size | Mechanism | Tokens (first run) | Wall time |
|---|---|---|---|
| **Small** (<~150 assets, response ≤25 KB) | Inline response → model writes to disk | ~5-10K | ~2-3 min |
| **Mid** (~150-300 assets, response 15-50 KB) | Inline-write OR borderline Claude Code auto-save | ~10-20K | ~3-7 min |
| **Large** (>~300 assets, response >25 KB) | Claude Code auto-save → model never sees bytes → `cp` directly to cache | ~3-5K | ~2-5 min |
| **Cached re-run (any size)** | Probe + build.py only | ~2-3K | ~5 s |

**The trap:** mid-sized tenants (150-300 assets) cost MORE tokens than
larger ones, because they double-pay (data once in MCP result, once
in write content). This is the [§8c mid-sized payload trap](docs/CONVENTIONS.md).

**Field-test observation (2026-06-12):** SAs report 10-20 min wall
times on production tenants. Suspected root cause: model violating
the "don't read the harness-saved file" anti-pattern (see below) and
pulling 50-150 KB back into context. If the model reads the
auto-saved file, subsequent turns slow nonlinearly — every model
operation now has the full asset list in context. This can balloon
a 3-min skill to 15-25 min.

Compare to v1.0 (~29K first run on a typical tenant) and ad-hoc
regeneration without this skill (~95K).

## Data shape contract

The `assets/template.html` script expects exactly:

```js
ASSETS = [
  { k: "uuid", n: "name", t: "AssetType", r: number, d: "YYYY-MM-DD", x: boolean },
  ...
]
ENVIRONMENTS = [
  { key: "uuid", name: "...", purpose: "...", host: "..." },
  ...
]
TENANT = { id: "uuid", realm: "string", region: "string", hosting: "string" }
```

Known asset types (each colored distinctly): `WebApplication`,
`MobileApplication`, `Agent`, `AIModelConnection`, `Workflow`,
`LowCodeLibrary`, `ExtensionLibrary`, `MobileLibrary`, `ExternalLibrary`,
`WidgetLibrary`, `ExternalConnection`. Unknown types render gray.

## Cache rules

- Location: `~/.claude/cache/outsystems-tenant-architecture/<tenant-id>/`
- TTL: 1 hour
- Freshness check: compare `total` from `app_list?limit=1` against cached
  value. Cheap (~300 tokens).
- Known false-negative: if N assets were added AND N deleted between
  fetches, count is stable and we'd miss the delta. Acceptable for 1-hour
  TTL. Force refresh on user request.

## Harness notes

- **Claude Code**: MCP results above ~25 KB are auto-saved to disk by
  the harness ("Output has been saved to <path>") and never enter
  model context. This is what makes the Large-tenant band in the
  Token budget table so cheap, and it's also why the 🔴 HARD STOP
  below exists — don't undo the saving by reading the file back in.
- **Codex**: no auto-save equivalent — every `app_list` response
  arrives inline regardless of tenant size, and is compacted straight
  to the cache file via the skill's existing Step 3 inline-handling
  path. Expect roughly the Mid-band token cost (~10-20K) on Codex even
  for large tenants, since the free Large-tenant discount doesn't
  apply. Cached runs and re-renders (Step 5) cost the same on both
  harnesses — that path never touches `app_list` at all.
- Cache location `~/.claude/cache/` is shared across harnesses (see
  the Step 1 note).

## Troubleshooting

Common failures (MCP disconnect, auth expiry, missing `python3`) live in
CONVENTIONS §7c. Skill-specific:

- **`limit: 1000` returns inline (not auto-saved)** → tenant is small
  (<150 assets). Save the response to `$CACHE/apps-raw.json` and pass
  that path as `RAW_APPS`. Same `build.py` call works.
- **`total > 2000`** → response might exceed the harness file buffer.
  Fall back to paginated `limit: 500`, save each page, then concatenate
  the `results[]` arrays before passing to `build.py`:
  `python3 -c "import json,sys; pages=[json.load(open(p)) for p in sys.argv[1:]]; print(json.dumps({'results':sum((p['results'] for p in pages),[]),'total':pages[0]['total']}))" "$CACHE"/apps-page-*.json > "$CACHE/apps-raw.json"`
- **No envs returned** → `build.py` falls back to `region=us-east-1`,
  `hosting=oscloud`, `realm=<tenant-id prefix>`.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4). Skill-specific:

- 🔴 **HARD STOP (Claude Code): do NOT read the harness-saved file.**
  When Claude Code's harness emits *"Output has been saved to <path>"*,
  the path goes **directly to build.py** via the command-line arg. The
  model must **never** read that file into context. A 280-asset tenant's
  payload is ~50 KB ≈ 12-15K tokens; on a 1000-asset tenant it's ~150 KB
  ≈ 35-50K tokens. Once that's in context, every subsequent turn
  processes the bloat — turning a 3-min skill into a 15-25 min skill.
  **This is the leading suspect for the field-test slowness reports**
  (Sezen 20 min, Sofia 10 min, 2026-06-12 Demo Team thread). If you
  need to verify content for debugging, run `head -c 1000 <path>` in a
  shell, not a read into the model. The contract is: data goes through
  disk → build.py → output HTML, never re-entering the model's context.
- 🔴 **HARD STOP (Codex): don't dump the inline payload back into the
  conversation or re-read the compact cache file.** Codex has no harness
  auto-save, so the `app_list` response always arrives inline (see
  Step 3). Once it is compacted into `$CACHE/apps-raw.json`, pass that
  file path to `build.py` — never re-print or re-load the raw payload
  into context on a later turn. The failure mode and its 15-25 min cost
  are the same as the Claude Code case above.
- **Don't chain into `outsystems-app-architecture` per-app** without
  Step 0's explicit user confirmation. A "tenant + every app" request
  has 100× the cost; gate it.
- **Don't pre-fetch with `limit: 100`** for the asset list. The skill
  is designed around `limit: 1000` triggering the auto-save threshold;
  smaller limits force inline payloads that cost ~5K output tokens
  per page in write content.

## When NOT to use

- User wants per-app architecture (use the per-app skill if available).
- User wants raw data only → return JSON, skip the HTML.
- User wants a non-graph layout (treemap, sunburst) → fork the template.
- Unsure whether this works on Codex vs. Claude Code → it works on
  both; see Harness notes below for the cost and behavior differences
  instead of assuming either is unsupported.
