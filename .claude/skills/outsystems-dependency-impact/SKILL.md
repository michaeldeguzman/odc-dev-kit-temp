---
name: outsystems-dependency-impact
description: Build an interactive HTML REVERSE-dependency explorer for the tenant — answers "who depends on this library/agent?" for every library, agent, and connection. A one-time scan whose duration is proportional to consumer asset count (typical: 1-3 min for a 20-asset tenant, 9-25 min for a 150-asset tenant, bounded by an upstream MCP `app_refs` 2-parallel cap — see "Why is this slow?" in SKILL.md). Queries against the cached index are free thereafter (~1-2K). Use ONLY for reverse questions like "who depends on [library/agent]", "if I publish [library] who breaks", "blast radius of [library/agent]", "reverse dependency map", "library impact audit", "agent impact audit". For forward questions about a specific app ("what does App X depend on", "deps of App X"), use outsystems-app-architecture or call mcp__outsystems__app_refs directly — they're ~10x cheaper.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: AskUserQuestion Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_refs
metadata:
  version: "1.3.0"
  author: outsystems-r-and-d
---

# OutSystems Dependency Impact

Produces a self-contained HTML reverse-dependency explorer. Pick any
library/agent/connection in the tenant — the page shows every app
that references it, the specific revision they're built against, and
how stale that reference is vs. the current revision.

**Key insight:** the scan is the expensive part. Once cached, the user
can search and explore freely in the browser at zero ongoing cost.
That's why this skill exists as a one-time scan rather than a
per-target query.

## Why is this slow? (added v1.2.1 — field-test, João L.)

The first-run scan is **fundamentally O(N) over consumer assets** and
**capped at 2 parallel calls by the upstream `app_refs` endpoint**
(CONVENTIONS §7b). The skill can't speed this up — it's a platform
constraint filed for engineering as S3 in our upstream-work backlog.

For a typical 150-asset tenant:

| Upstream health | Wall time |
|---|---|
| Healthy (2-parallel + 5s cooldown holds) | ~9 minutes |
| Realistic (occasional timeout-driven downshifts) | ~12-15 minutes |
| Degraded (sustained timeouts, sequential fallback) | ~18-25 minutes |

For SMALLER tenants the time scales down linearly — a 20-asset tenant
is ~1-3 min, a 50-asset tenant is ~3-10 min. The Step 4.5 pre-flight
gate computes the per-tenant ETA from the actual scan-list count.

The cache (24h TTL) makes subsequent queries free — the slowness is a
one-time tax per tenant per day. If you'll be away anyway, fire the
scan, walk away, come back to the cached browser.

**What this skill does NOT promise:**
- It does not promise <5 min scans. The math doesn't allow it under
  current upstream caps.
- It does not promise complete data — Banking-Portal-class large apps
  time out individually and are recorded as "unable to analyze."
- It does not promise the scan won't degrade further if upstream is
  overloaded — see the abort condition in Step 5.

**What unlocks better:** S3 fix on the MCP server side (lift the
2-parallel cap on `app_refs`). When that lands, a 150-asset scan
should drop to ~2-3 minutes.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. Shared rules: §7b
(`app_refs` 2-parallel cap), §8 (token-efficiency).

## The two reality checks

**`app_refs` is timeout-prone for large apps.** Banking Portal
(574 revisions, huge OML) consistently fails to return. The skill
expects this — failed calls are recorded as "unable to analyze" and
the scan continues. v1.0 *will* have blind spots on large apps.
Customers are told this in the report.

**Scan is bounded to "consumer" asset types.** Libraries depending
on other libraries is rare and lower-value. v1.0 scans only the
4 consumer types: `WebApplication`, `MobileApplication`, `Agent`,
`Workflow`. This roughly halves the call volume and concentrates the
budget on the high-signal calls.

## Procedure

### Step 0 — Scope detection + pre-flight confirmation (NEW in v1.2.0)

**This skill is expensive** — a fresh full-tenant scan is 80-100K tokens
and 9-15 minutes of wall time. Step 0 makes sure the user actually
wants that before burning the budget. Read the user's request and pick
the matching branch:

**Branch A — Forward-deps for ONE specific app** ("what does App X use",
"show me the deps of App X", "what's in App X")
→ **Stop. Tell the user this skill is the wrong tool** and route to
`outsystems-app-architecture` (which shows the same forward-dep info
plus screens/entities/actions for ~10K tokens). Do NOT continue the
procedure.

**Branch B — Forward-deps for 2-3 specific apps** ("what do App X and
App Y depend on")
→ **Stop. Skip this skill entirely.** Call
`mcp__outsystems__app_refs` directly on each named app (N calls,
~3-5K tokens total). Report the deps inline.

**Branch C — Reverse-deps / blast radius / library impact** ("who
depends on lib X", "if I publish X who breaks", "audit my deps")
→ **Continue through Steps 1-4 without asking** (those steps are cheap,
~3-5K tokens). The confirmation gate fires in **Step 4.5** with an
ETA computed from the actual consumer asset count for THIS tenant,
not a hardcoded "~150" estimate.

**Why Step 0 exists (field-test note, João L. 2026-06-01):** the v1.1.x
trigger phrases ("dependency tree", "dependency audit") attracted
"analyze these 2 apps" requests that routed through the full scan and
spent 20+ minutes with timeouts. The v1.2.0 description is tighter,
but Step 0 is the safety net.

**Why the gate moved to Step 4.5 (v1.2.2 — live-test 2026-06-05):**
the v1.2.1 Step 0 gate hardcoded "~150 consumer assets, 9-25 min" in
the question text. For a 20-asset tenant that's misleading — real
scan takes ~1-3 min, not ~9-25 min. The gate now fires AFTER the
filter step so the ETA reflects this tenant's actual scope.

### Step 1 — Auth + resolve tenant

Call `mcp__outsystems__auth_status`, then read `claims.aid` as
`TENANT_ID`.

```
CACHE = ~/.claude/cache/outsystems-dependency-impact/<TENANT_ID>/
SKILL = <this skill's directory>
mkdir -p "$CACHE"
```

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

### Step 2 — Cache freshness (24h TTL)

If `$CACHE/meta.json` exists AND `now - meta.scanned_at < 86400` (24h):

→ **cache valid, jump to Step 6** (render from cache).

If the user said "refresh" / "rescan" / "fresh data", skip this check.

### Step 3 — Asset list (cross-skill reuse)

We need the full tenant asset list to know what to scan AND to look
up current revisions.

**Preferred (fast):** read
`~/.claude/cache/outsystems-tenant-architecture/<TENANT_ID>/assets.json`
if it exists and was written within 24h. That's the same compact
shape we'd produce, courtesy of the tenant-architecture skill.

**Fallback (slow):** call `mcp__outsystems__app_list` with
`limit: 1000`. On Claude Code the harness auto-saves the response to disk
("Output has been saved to <path>") — `cp` it to
`$CACHE/assets-raw.json`. On harnesses without auto-save (Codex) the
response arrives inline instead — save it to `$CACHE/assets-raw.json`
the same way and continue identically.

### Step 4 — Filter to scan list

From the asset list, select assets where `assetType` is one of:
`WebApplication`, `MobileApplication`, `Agent`, `Workflow`.

**ALSO exclude system-template apps by name pattern** (added v1.2.2,
live-test 2026-06-05). These deterministically fail `app_refs` via
the OML-fallback with *"System modules cannot be loaded with the Model
API"* — the same error documented in `outsystems-spec-driven-build`.
Pre-filtering saves a wasted MCP call + ~300ms-3s per asset:

```python
SYSTEM_TEMPLATE_PATTERNS = (
    "Template ", "Template_", "template_",
    "Screen Templates ",
)
SYSTEM_TEMPLATE_EXACT = {"OutSystems Sample Data"}

def is_system_template(name: str) -> bool:
    return (name in SYSTEM_TEMPLATE_EXACT
            or name.startswith(SYSTEM_TEMPLATE_PATTERNS))
```

Save the filtered list of `assetKey`s to `$CACHE/scan-list.json`
(compact JSON, one key per line is fine).

Typical tenant: ~150 consumer assets out of ~280 total. Small stage
tenants: 10-30 consumer assets. The pre-flight gate in Step 4.5
adapts to the actual count.

### Step 4.5 — Pre-flight confirmation with actual count (NEW v1.2.2)

Now that we know the exact scan-list size, compute the ETA and ask
the user to confirm BEFORE Step 5 burns the scan budget.

**ETA formula** (derived from CONVENTIONS §7b — 2-parallel cap, ~5s/call):

```
count       = len(scan_list)
healthy_s   = count * 3.5    # 2-parallel × ~7s/batch ÷ 2
realistic_s = count * 5.0    # accounting for some downshift batches
degraded_s  = count * 12.0   # full sequential fallback
healthy_m   = round(healthy_s / 60, 1)
degraded_m  = round(degraded_s / 60, 1)
tokens_k    = round(count * 0.55, 0)   # ~550 tokens/asset empirical
```

Then ask the user:

```
Question: "Scan {count} consumer assets to build the reverse-dependency
           map? Estimated {healthy_m}-{degraded_m} min wall time
           (bounded by upstream MCP 2-parallel cap), ~{tokens_k}K tokens.
           Cache lives 24h; subsequent queries are free."
Header:   "Scan?"
Options:
  - "Yes — start the scan"
    description: "Scans {count} assets. ETA: ~{healthy_m} min healthy,
                  up to ~{degraded_m} min on degraded upstream. ~{tokens_k}K tokens."
  - "No — cancel"
    description: "Aborts. The asset list + tenant cache are kept
                  (cheap), but no app_refs calls fire."
```

On "No" → stop. The asset list + tenant-assets cache stay (they're
cheap and useful for other skills). No app_refs calls fire.

**Example numbers** for common tenant sizes:

| Consumer count | Healthy | Degraded | Tokens |
|---:|---:|---:|---:|
| 12 | ~0.7 min | ~2.4 min | ~7K |
| 20 | ~1.2 min | ~4.0 min | ~11K |
| 50 | ~2.9 min | ~10.0 min | ~28K |
| 150 | ~8.8 min | ~30.0 min | ~83K |

(Last row matches the v1.2.1 hardcoded "9-25 min" range that this
gate replaces.)

### Step 5 — Scan `app_refs` for every asset in scan-list

Call `mcp__outsystems__app_refs` for each asset. **Throttle contract
(HARD — do not improvise):**

**Start state — batched mode:** batches of 2 calls in parallel, 5-second
cool-down between batches (see CONVENTIONS §7b for the empirical
detail on upstream `app_refs` saturation).

**Downshift trigger:** if 3 consecutive batches see ≥1 timeout each,
**switch to sequential single calls** with 3-second pauses between
them. Stay in sequential mode for the rest of this scan; do NOT retry
batches of 2. The upstream queue is unhealthy at this point and
parallel calls poison the pipeline.

**Abort trigger:** if 10 consecutive single calls time out, **stop the
scan**. Report to the user:
- "Upstream `app_refs` appears overloaded — saw N consecutive timeouts."
- "Partial scan is cached at `$CACHE/refs/` ({completed}/{total} assets)."
- "Re-running this skill resumes from where it stopped (see Step 5b)."
Do NOT keep trying. Do NOT escalate to higher parallelism.

**Forbidden — never escalate above batches of 2.** Empirically, 3+
parallel saturates the upstream and poisons subsequent calls
(CONVENTIONS §7b). The model is NOT permitted to "try 10 at once"
even if a few succeed — the failure mode is silent timeout and the
partial successes get followed by widespread failure ~10 seconds
later (field-test, João L., 2026-06-01).

**Periodic progress reports (added v1.2.1 — field-test, João L.).**
Every **10 batches** during the scan, emit a one-liner to the user
showing forward progress. Without this, multi-minute scans look
silently stuck and users lose confidence. Format:

```
Progress: 42/150 consumers scanned · 18 unique targets found ·
2 timeouts so far · est. 6 min remaining
```

Recompute the ETA from current throughput, not the initial estimate —
if the scan downshifted to sequential, the remaining time scales
accordingly. The model is responsible for emitting these between
batches, NOT every batch (would be too chatty).

**Per-response handling — dual-schema support (added v1.2.2).**
Live-test 2026-06-05 discovered `app_refs` now returns
`schemaVersion: 2` shape with `{producerAssetKey, producerAssetName,
importedKind}` instead of the legacy `{moduleKey, name, kind, revision}`
(see CHANGELOG + upstream-work S14). `build.py` reads BOTH shapes
seamlessly; the model can save whichever it received without
field-mapping. Concretely:

- **Successful** (v2 shape, typical now)
  → save to `$CACHE/refs/<assetKey>.json` keeping
  `{assetKey, references: [{producerAssetKey, producerAssetName, importedKind}, ...]}`.
- **Successful** (v1 shape, if encountered — e.g. older cached files)
  → save keeping
  `{assetKey, revision, references: [{moduleKey, name, kind, revision}, ...]}`.
- In either case, drop `description`, `version`, and other unused
  fields. `build.py` ignores them.
- **Timed-out / errored** → save a placeholder
  `$CACHE/refs/<assetKey>.json` containing
  `{assetKey: "<key>", failed: true, reason: "<short-tag>"}` where
  reason is one of: `system-module`, `timeout-large-oml`, `timeout`,
  `error`. The scan continues (subject to the abort trigger above).

**Why dual-schema:** the schema drift was breaking but the fix is
forward-compatible. If the API reverts or a third shape appears,
extend `build.py` rather than scrambling to re-map at write time.

For a typical 150-asset scan with 2-parallel + 5s cool-down on a
healthy upstream: ~75 batches × ~7s = ~9 minutes wall clock. Degraded
upstream (sequential fallback): up to ~15 minutes. Token cost: ~150
compact writes × ~80 tok each = ~12K output tokens. **Empirical
full-scan budget: ~80–100K** (revised up from v1.0's ~20K after a
partial 25-asset run). The dominant cost is *per-batch* overhead
(cool-down turn + progress recompute + dispatch round-trip ≈ 1K tok
per pair), not content — app_refs responses for small agents are ~300
bytes and roundtrip inline rather than auto-saving to disk. Net: don't
budget this skill at <50K for a fresh full-tenant scan. The cache
makes subsequent renders ~1–2K, so this is genuinely a one-time tax.

Do **not** use `jq` to inspect the responses inline. Trust `build.py`
to handle parsing.

### Step 5b — Resume from partial scan (NEW in v1.2.0)

**Before each `app_refs` call**, check whether
`$CACHE/refs/<assetKey>.json` already exists. If yes, **skip the
call** — that asset was either scanned in a prior run or failed in a
way that we've already recorded.

This makes the scan resumable across SKILL invocations:

- A prior scan killed mid-flight (Step 5's abort trigger, ctrl-C, MCP
  reconnect, lost network) leaves a partial cache at `$CACHE/refs/`.
- Re-running this skill picks up from the missing assets only — no
  duplicate cost for already-scanned ones.
- Failed assets stay marked as failed unless the user passes "rescan
  failures" — in which case delete `$CACHE/refs/<key>.json` files
  where `failed: true` before resuming.

### Step 6 — Build the index

```bash
OUT="${OUTPUT_PATH:-$PWD/dependency-impact.html}"
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT" \
  --assets   "$CACHE/scan-list.json"  \
  --refs-dir "$CACHE/refs/"           \
  --tenant-assets "$CACHE/tenant-assets.json"
```

Where `tenant-assets.json` is either the tenant-architecture skill's
`assets.json` (copied or symlinked into `$CACHE`) or a fresh fetch.

`build.py` produces:
- `$CACHE/impact-data.json` — the unified data bundle
- `$CACHE/meta.json` — scan timestamp + stats
- `$OUT` — the final HTML

### Step 7 — Cached re-render

```bash
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT"
```

### Step 8 — Report (3–5 lines)

- Output file path
- Stats: X assets scanned, Y failed (likely Banking Portal-class)
- Catalogued: Z unique targets, W total dependency edges
- Cache state — "scanned now" / "from cache (Xh old)"
- "Open the HTML and use the search box to pick a target"

## Data shape contract

`build.py` writes `$CACHE/impact-data.json`:

```js
{
  tenant: { id, scannedAt },
  stats: {
    consumerAssetCount, scannedCount, failedCount,
    targetCount,       // unique referenced moduleKeys
    edgeCount,         // total ref edges across all apps
  },
  // Forward index: per-asset list of its deps (compact)
  assets: [
    { k, n, t, r, d, scanned, deps?: [{k, n, kind, r}] }
  ],
  // Reverse index: per-target list of dependent assets (the hot path)
  byTarget: {
    "<moduleKey>": {
      n, kind, currentRev,            // looked up from tenant-assets
      users: [{ k, n, t, usedRev, gap }]   // gap = currentRev - usedRev
    }
  }
}
```

## Cache rules

- Location: `~/.claude/cache/outsystems-dependency-impact/<tenant-id>/`
- TTL: **24 hours** (deps change slowly; this is intentionally long
  vs the per-app skills' 1h TTL).
- Force refresh: "refresh" / "rescan" / "fresh data".
- Cross-skill reuse: prefers `outsystems-tenant-architecture` cache
  for the asset list (CONVENTIONS §8a — cross-skill data sharing).

## Token budget (estimate)

| Scenario | Mechanism | Total |
|---|---|---|
| First scan, ~150 consumer assets (empirical) | batch-of-2 × 75 + build | **~80–100K** |
| Cached run within 24h | meta check + build.py | ~2K |
| Re-render only | build.py | ~1K |

The scan is genuinely the expensive part. The original v1.0 estimate
of ~15K was optimistic: it assumed `app_refs` responses would trigger
Claude Code's harness disk auto-save (>25 KB threshold). In practice
most responses are ~300 bytes and roundtrip inline on every harness.
Combined with the batch-of-2 concurrency limit
(the 2-parallel concurrency cap), per-batch overhead dominates. Still cheaper than a naive
"scan everything" (would be ~200K+) — the consumer-type filter
and compact-write discipline are doing real work.

## Harness notes

- **Claude Code**: the one large response in this skill is the Step 3
  fallback `app_list` with `limit: 1000`, which the harness auto-saves to
  disk ("Output has been saved to <path>") so it never enters model
  context — `cp` it straight to the cache. The per-asset `app_refs`
  responses are tiny (~300 bytes) and always arrive inline.
- **Codex**: no auto-save equivalent — the Step 3 `app_list` response
  arrives inline regardless of size and is saved to the cache file the
  same way. Only that one response differs: the per-asset `app_refs` scan
  that dominates the first-scan cost (~80-100K) is inline on both
  harnesses, so the scan costs the same on Codex as on Claude Code.
  Cached runs (24h TTL) and re-renders cost the same on both — they never
  call `app_list` or `app_refs` at all.
- Cache location `~/.claude/cache/` is shared across harnesses (see the
  Step 1 note), including the cross-skill
  `outsystems-tenant-architecture` asset-list cache reused in Step 3.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4). Skill-specific:

- **Don't scan libraries / connections / external libraries.** They
  rarely have meaningful deps and inflate scan cost. Filtered out in
  Step 4.
- **Don't run `app_refs` on Banking Portal-class apps without
  expecting failure.** Treat as best-effort; the report shows what
  couldn't be analyzed.
- **Don't try to fetch transitive deps** (deps-of-deps). The browser
  can compute that from `byTarget` if needed. v1.x ships direct only.
- **Don't paginate `app_refs`** — it's a single-shot call per asset.

## When NOT to use

- User wants the architecture of one app → use
  `outsystems-app-architecture` (it shows that app's deps via its own
  data, more focused).
- User wants to check ONE specific app's deps (forward) → call
  `app_refs` directly; this skill's scan is overkill.
- User wants real-time deps (e.g., right before a deploy) → the
  cache might be 24h stale; pass "refresh" to force a fresh scan.
- Tenant has many large/timeout-prone apps → coverage will be low.
  Wait for the underlying MCP perf fix on `app_refs`.
