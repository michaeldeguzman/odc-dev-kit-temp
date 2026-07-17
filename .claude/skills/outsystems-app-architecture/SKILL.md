---
name: outsystems-app-architecture
description: Generate an interactive HTML graph of a single OutSystems app's architecture — UI flows + screens, server actions + functions, business entities, static enums, structures, roles, AI model connections, and library dependencies — with OutSystems-themed dark mode styling. ONE app per invocation — do NOT iterate over multiple apps in a single call (run the skill explicitly per-app, gated by AskUserQuestion if N>3). For tenant-wide views, use outsystems-tenant-architecture instead. Use when the user asks for the architecture of a specific app, "show me the architecture of [app]", "explore [app]", "what's inside [app]", "give me an overview of [app]", or similar.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: AskUserQuestion Bash Read Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_info mcp__outsystems__app_refs mcp__outsystems__context_screens mcp__outsystems__context_actions mcp__outsystems__context_entities mcp__outsystems__context_structures mcp__outsystems__context_roles
metadata:
  version: "1.4.0"
  author: outsystems-r-and-d
---

# OutSystems App Architecture

Produces a self-contained HTML file with a force-directed graph of a
single app's internal structure: UI flows → screens, action groups →
server actions / functions, data layer (entities / enums / structures),
security (roles), and **dependencies** — AI model connections and
referenced libraries. OutSystems dark theme, filter-by-category
sidebar, click for detail.

**v1.2 change:** the graph now surfaces the agent → AIModelConnection
and app → library edges via `app_refs` data. Available via cross-skill
cache reuse from `outsystems-dependency-impact` (zero MCP cost) or a
fresh small-app `app_refs` call. Closes a v1.1 field-testing finding
(SA: *"there's no dependency between the agent and the AI model"*).

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. Shared rules: §7b
(`context_*` capped at `limit: 100`), §8.1–§8.6 (token-efficiency
including the harness disk auto-save pattern).

## Procedure

### Step 0 — Scope guard (NEW v1.3.2 — demo-perf field-test)

This skill produces **one app's architecture** per invocation. Read
the user's request and route:

**Branch A — One specific app** ("architecture of Banking Portal",
"show me TaskTracker")
→ Continue.

**Branch B — Multiple specific apps** ("architecture of Banking
Portal AND TaskTracker AND ...")
→ For N ≤ 3, run this skill once per app sequentially. For N > 3,
**ask the user** — it's ~10K tokens each, ~50K + ~5 min
for 5 apps. Confirm before chaining.

**Branch C — Whole tenant** ("architecture of everything", "all my
apps", "tenant ECG")
→ **Stop and route to `outsystems-tenant-architecture`.** That skill
is a single tenant-level pass at ~3-10K tokens, not 100× per-app calls.
Tell the user: *"For the tenant view, use `outsystems-tenant-architecture`
— it's one pass instead of N. After you have that, come back here for
specific apps you want to drill into."*

**Why Step 0 exists (field-test note, 2026-06-12 Demo Team thread):**
Sezen and Sofia reported 10-20 min wall times on the architecture
skills — likely caused by unintentional chaining ("show me all apps"
fanning out into 100+ per-app invocations).

### Step 1 — Auth + identify the app

Call `mcp__outsystems__auth_status`. If `logged_in: false`, stop.

Resolve the app from the user's prompt:

- If the user gave an asset key (UUID), use it directly.
- Otherwise call `mcp__outsystems__app_list` with `search: "<name from
  prompt>"`. If exactly one match → use it. If multiple → list the
  candidates and ask the user to pick. If zero → ask for a more
  specific name.

```
APP_KEY  = <asset key>
APP_NAME = <human-readable name>
CACHE    = ~/.claude/cache/outsystems-app-architecture/<APP_KEY>/
SKILL    = <this skill's directory>
mkdir -p "$CACHE"
```

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

### Step 2 — Cache freshness (only if cache exists)

If `$CACHE/meta.json` is present:

1. Call `mcp__outsystems__app_info` with `key: <APP_KEY>` (cheap, ~500
   tokens).
2. Compute `AGE = now - meta.fetched_at`.
3. If `AGE < 3600` AND `app_info.revision == meta.revision` → **cache
   valid, jump to Step 4** (cached re-render).

If the user said "refresh" / "fresh data" / "rebuild", skip this step.

### Step 3 — Fetch (parallel)

Call **all six** of these in a single message so they run concurrently.
Use `limit: 100` (the API max) on all `context_*` calls. Large apps
will trigger Claude Code's harness auto-save even at limit:100 — handle that the
same way as inline responses (see below).

- `mcp__outsystems__app_info` with `key: <APP_KEY>` (no limit field)
- `mcp__outsystems__context_screens` with `app: <APP_KEY>`, `limit: 100`,
  `owned_only: true`
- `mcp__outsystems__context_actions` with `app: <APP_KEY>`, `limit: 100`,
  `owned_only: true`
- `mcp__outsystems__context_entities` with `app: <APP_KEY>`, `limit: 100`,
  `owned_only: false` — **note: false, unlike the other context_* calls.**
  Many apps (especially "thin UI" patterns) define their data model in a
  separate library module. With `owned_only: true` we'd return empty for
  those apps and report "no entities" — which is materially misleading
  (field-test report: `rmad employee directory`). `owned_only: false`
  catches the inherited entities; `build.py` partitions them as
  `entities` (owned by this app) vs `inheritedEntities` (from referenced
  libraries) and renders both.
- `mcp__outsystems__context_structures` with `app: <APP_KEY>`, `limit: 100`,
  `owned_only: true`
- `mcp__outsystems__context_roles` with `app: <APP_KEY>`, `limit: 100`,
  `owned_only: true`

For **each** of the six responses, follow this rule:

- **If the response is the "Output has been saved to <path>" notice**
  (Claude Code's harness auto-save kicked in, typical for large apps):
  extract the path. `cp` it into the cache via Bash (no model tokens
  spent on content). **This is the cheapest path.**
- **If the response is inline JSON** (under the ~25 KB threshold on
  Claude Code — and always the case on harnesses without auto-save,
  e.g. Codex): **write a COMPACT form to
  `$CACHE/<section>-raw.json`** — only the fields `build.py` reads,
  per the whitelist below.

### Step 3.5 — Dependencies via `app_refs` (cross-skill cache or fresh)

The Dependencies layer (AI model connections + library refs) needs
`app_refs` data. Resolve it in this order:

1. **Cross-skill cache lookup (free).** Check if
   `~/.claude/cache/outsystems-dependency-impact/<TENANT_ID>/refs/<APP_KEY>.json`
   exists AND was written within 24h. If yes → that's `REFS_PATH`. No
   MCP call needed. The dependency-impact skill already scanned this
   app.

2. **Fresh `app_refs` call (for small apps only).** If no cache hit
   AND `app_info.assetType` is `Agent` or `Workflow`, OR
   `app_info.revision < 100`, call
   `mcp__outsystems__app_refs(key: <APP_KEY>)`. Most agents are small
   enough that the upstream `app_refs` timeout (CONVENTIONS §7b)
   doesn't bite. Save the response
   to `$CACHE/refs-raw.json` and use that as `REFS_PATH`.

3. **Skip the dependencies layer.** If `app_info.revision >= 100` AND
   no cache hit (likely a Banking-Portal-class large app where
   `app_refs` would time out), leave `REFS_PATH` unset. The graph
   renders without the Dependencies layer; add a note in the Step 5
   report: *"Dependencies layer skipped — run `outsystems-dependency-impact`
   first to populate the cache, then re-run."*

Tenant ID for the cross-skill cache path: get from
`mcp__outsystems__auth_status` claims (`claims.aid`) on the same call
as Step 1. Or read from `~/.claude/cache/outsystems-tenant-architecture/`
folder names (a previous skill run will have created
`outsystems-tenant-architecture/<TENANT_ID>/`).

### Compact-write field whitelist (mandatory for inline responses)

When writing an inline response, emit ONLY these fields. This roughly
halves the write content vs. the raw MCP shape and is the single
biggest token saver on first runs (saves ~4-5K tokens empirically).

| Section | Fields to keep |
|---|---|
| `screens-raw.json`    | `data[].(key, name, description, isPublic, timestamp, ownerAppKey, additionalData.{uiFlowKey, uiFlowName})` |
| `actions-raw.json`    | `data[].(key, name, description, isPublic, ownerAppKey, additionalData.actionType)` |
| `entities-raw.json`   | `data[].(key, name, description, isStatic, ownerAppKey, isReferenced, producerAssetName)` |
| `structures-raw.json` | `data[].(key, name, description, ownerAppKey)` |
| `roles-raw.json`      | `data[].(key, name, description, isPublic, ownerAppKey)` |
| `app-info-raw.json`   | full response (already small) |

Use compact JSON formatting (no whitespace inside objects). Wrap in
`{"data": [...]}` to match the MCP envelope — `build.py` then reads
inline-written files and harness-saved files interchangeably.

### Step 4 — Build (fresh or cached)

One Python invocation does everything: transforms raw responses into
the compact cache files, then injects into the template. Pass
`--refs $REFS_PATH` if Step 3.5 found a refs source; omit otherwise.

```bash
OUT="${OUTPUT_PATH:-$PWD/app-architecture.html}"

python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT" \
  --app-info       "$APP_INFO_PATH"     \
  --screens        "$SCREENS_PATH"      \
  --actions        "$ACTIONS_PATH"      \
  --entities       "$ENTITIES_PATH"     \
  --structures     "$STRUCTURES_PATH"   \
  --roles          "$ROLES_PATH"        \
  ${REFS_PATH:+--refs "$REFS_PATH"}
```

For cached mode, omit all the `--*-path` flags — `build.py` will reuse
the existing compact cache files (including any deps from a previous
fresh run).

### Step 5 — Report (3–5 lines)

- Output file path
- App name + revision + asset type
- Counts: UI flows, screens, server actions, functions, entities,
  enums, structures, roles
- Cache state — "used (Xs old)" or "refreshed"

## Data shape contract

`build.py` writes a single compact bundle to `$CACHE/app-data.json`
that the template expects:

```js
APP_DATA = {
  app: { key, name, type, revision, description, date },
  uiFlows: [{ key, name }],
  screens: [{ k, n, flow, desc, pub, date }],
  actions: [{ k, n, kind: "action"|"function", desc, pub }],
  entities: [{ k, n, desc }],                       // owned by this app
  inheritedEntities: [{ k, n, desc, fromModule }],   // inherited from libraries (v1.3+)
  enums: [{ k, n, desc }],
  structures: [{ k, n, desc }],
  roles: [{ k, n, desc, pub }],
  deps: [{ k, n, kind, cat: "AIModel"|"Library", rev }],  // [] if no refs source
  inheritedCount: number
}
```

`deps[]` is empty when no `--refs` was provided. The template
conditionally hides the Dependencies layer based on `deps.length`.
Built-in OutSystems modules (`(System)`, `OutSystemsUI`, etc.) are
filtered out of `deps` to reduce noise.

## Cache rules

- Location: `~/.claude/cache/outsystems-app-architecture/<app-key>/`
- TTL: 1 hour
- Freshness check: compare `app_info.revision` against `meta.revision`.
  This is more precise than the tenant skill's `total` check — a single
  revision number is the canonical "did anything change?" signal.

## Token budget (empirical estimate)

| Scenario | Mechanism | Total |
|---|---|---|
| Small app (Agent/Workflow), first run | 6 context_* + 1 app_refs (fresh) + build.py | **~10K** |
| Small app, first run + dep-impact cache hit | 6 context_* + build.py (no extra MCP call) | **~9K** |
| Typical app, first run (large, deps layer skipped) | 6 context_* + build.py | ~12K |
| Cached run | `app_info` probe + build.py | ~2K |
| Re-render only | build.py | ~1K |

Empirically measured on Banking Portal (18 screens / 42 actions /
30 entities / 6 structures / 19 enums / 1 role): **~17K without
compact-write, ~12-13K with**. Cached re-runs cost ~1K. v1.2's
deps-layer adds ~0 cost when the dep-impact cache is warm; ~500
tokens when a fresh small-app `app_refs` call is needed.

## Harness notes

- **Claude Code**: `context_*` MCP results above ~25 KB are auto-saved
  to disk by the harness ("Output has been saved to <path>") and never
  enter model context. On a large app this is what keeps the first-run
  cost down, and it's why the 🔴 HARD STOP below exists — don't undo
  the saving by reading the file back in.
- **Codex**: no auto-save equivalent — every `context_*` response
  arrives inline regardless of app size, and is compacted straight to
  the cache file via the skill's existing Step 3 inline-handling /
  compact-write path. Expect roughly the first-run token cost even on
  large apps, since the free Claude-Code auto-save discount doesn't
  apply. Cached runs and re-renders (Step 4 cached mode) cost the same
  on both harnesses — that path never touches `context_*` at all.
- Cache location `~/.claude/cache/` is shared across harnesses (see
  the Step 1 note).

## Troubleshooting

Common failures (MCP disconnect, auth expiry, missing `python3`) live
in CONVENTIONS §7c. Skill-specific:

- **App name matches multiple apps** → return the candidate list, ask
  the user to pick. Show `assetKey, name, revision, isExternal`.
- **`app_info` returns 404** → app may have been deleted. Clear cache
  for that key and tell the user.
- **`context_*` returns `{"data":[], "pagination":...}`** with empty
  data despite `owned_only: true` → try `owned_only: false`. Some
  context endpoints have ownership-resolution quirks; `build.py`
  filters non-owned items by `assetKey` match.
- **`app_refs` times out on a small app you expected to succeed** →
  this is rare (the timeout mostly hits large apps). Save a placeholder
  to `$CACHE/refs-raw.json` containing `{"assetKey": "<key>", "failed":
  true}`. The skill renders without the Dependencies layer.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4 no-jq, §8.1 don't pre-paginate).
Skill-specific:

- 🔴 **HARD STOP (Claude Code): do NOT read any `context_*`
  harness-saved file.** When a context call returns *"Output has been
  saved to <path>"*, `cp` that file into the cache via Bash and pass
  the path to `build.py`. **Never** read it into context. A large
  app's `context_screens` payload alone can be 20-40 KB ≈ 5-10K
  tokens; on a Banking-Portal-class app the total across all six
  context calls pulled into context = 50-150 KB = 12-35K tokens. This
  is the leading suspect for the 10-20 min slowness reports
  (2026-06-12 Demo Team thread, Sezen + Sofia). If you need to verify
  content for debugging, run `head -c 1000 <path>` in a shell, not a
  read into the model.
- 🔴 **HARD STOP (Codex): don't dump an inline `context_*` payload
  back into the conversation or re-read the compact cache file.** Codex
  has no harness auto-save, so each `context_*` response arrives inline
  (see Step 3) and is compacted straight to `$CACHE/<section>-raw.json`.
  Pass that file path to `build.py` — never re-print or re-load the raw
  payload into context on a later turn. The failure mode and its
  10-20 min cost are the same as the Claude Code case above.

- **Don't iterate this skill over many apps in one go** without
  Step 0's user-confirmation gate. A "give me all my apps" request
  scaled to 100 apps = ~1M tokens / 30-60 min wall time. Always
  prefer `outsystems-tenant-architecture` for tenant-wide views; this
  skill is per-app only.

- **Don't invent per-screen authorization or role assignments in any
  summary you generate.** The compact-write whitelist for
  `screens-raw.json` does NOT capture authorization (`Accessible by`)
  data, and the bundle's `screens[]` array has no `role` field. If you
  emit a "Roles" column per screen, you are confabulating from the
  app's primary role name — which is wrong. Field-test
  report (Rui M., rmad employee directory): the skill output stated
  every common-flow screen had role `RMadEmployeeDirectory`, but in
  Studio those screens were `Accessible by: Everyone` (anonymous).
  **Render the app's roles as a flat list once (from `D.roles`); never
  cross-product them with screens.** The only per-screen auth signal
  available is `isPublic` (anonymous-accessible boolean) — surface
  that if needed, but do not fabricate role memberships.

- **Don't fetch `context_themes`** — response can be >150 KB on a real
  app (Banking Portal). Out of scope; high cost, low signal.
- **Don't call `app_refs` on large apps** (`assetType=WebApplication`
  AND `revision >= 100`). The upstream `app_refs` queue saturates
  (see CONVENTIONS §7b) — times out, poisons the queue for ~10s.
  Step 3.5's conditional gate handles this; don't
  override it.
- **Don't re-fetch `app_refs` if the dependency-impact cache has a
  recent entry.** Cross-skill cache reuse is the whole point — saves
  one MCP call per run and avoids any timeout risk.

## When NOT to use

- User wants the whole tenant (use `outsystems-tenant-architecture`).
- User wants raw data only — return JSON.
- App is huge and the user wants a specific subsystem only — they're
  better served by a `context_search` follow-up.
