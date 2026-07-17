---
name: outsystems-app-documentation
description: Auto-generate clean Markdown documentation for a single OutSystems app — overview, UI flows + screens, server actions + functions, data model (entities, enums, structures), security (roles), and dependencies. Render-only — reads from the shared arch-cache populated by outsystems-app-architecture (auto-fills it if missing). Use when the user asks to "generate docs for [app]", "document [app]", "create documentation for [app]", "write up [app]", "auto-document [app]", "make docs for [app]", "compliance docs for [app]", or similar.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_info mcp__outsystems__context_screens mcp__outsystems__context_actions mcp__outsystems__context_entities mcp__outsystems__context_structures mcp__outsystems__context_roles
metadata:
  version: "1.4.0"
  author: outsystems-r-and-d
---

# OutSystems App Documentation

Produces a clean Markdown file documenting a single app's structure.
Drop-in for Confluence, wiki pages, README files, compliance docs, or
onboarding.

**v1.1 architecture (changed from v1.0):** this skill is **render-only**.
It reads from the shared `outsystems-app-architecture` cache rather
than maintaining its own fetch. If the arch-cache is missing or stale,
the skill auto-populates it (running the same 6-call fetch the arch
skill uses), so **both skills end up cached together** after this
runs. Future invocations of either skill on this app cost ~1.5K.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. This skill is a
renderer; most rules apply via the arch-cache it reads from, not
direct MCP calls. Shared rules: §7b (API quirks), §8
(token-efficiency).

## The contract — shared arch-cache as the data layer

Documentation is a **rendering** of architecture, not its own fetcher.
Any skill that needs structured app data should read from the
arch-cache at:

```
~/.claude/cache/outsystems-app-architecture/<APP_KEY>/app-data.json
```

This shape is documented in `outsystems-app-architecture`'s SKILL.md
and is stable. As the catalog grows, expect more skills to chain off
this same cache (test-coverage report, security audit, etc.) — the
arch fetch happens once, every downstream skill renders cheap.

## Procedure

### Step 1 — Auth + identify the app

Call `mcp__outsystems__auth_status`. If `logged_in: false`, stop.

Resolve the app from the user's prompt — same way as
`outsystems-app-architecture`:
- Asset key (UUID) → use directly.
- Otherwise `mcp__outsystems__app_list` with `search: "<name>"`. 1 match
  → use; multiple → ask; 0 → ask for more specific name.

```
APP_KEY    = <asset key>
ARCH_CACHE = ~/.claude/cache/outsystems-app-architecture/<APP_KEY>/
DOC_CACHE  = ~/.claude/cache/outsystems-app-documentation/<APP_KEY>/
SKILL      = <this skill's directory>
mkdir -p "$ARCH_CACHE" "$DOC_CACHE"
```

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

### Step 2 — Check arch-cache

If `$ARCH_CACHE/app-data.json` exists:
1. Call `mcp__outsystems__app_info` with `key: <APP_KEY>` (cheap probe).
2. Load `$ARCH_CACHE/meta.json`. If
   `app_info.revision == meta.revision` AND
   `now - meta.fetched_at < 3600` → **arch-cache is current. Jump to
   Step 4.**

### Step 3 — Populate arch-cache (when missing or stale)

Follow `outsystems-app-architecture`'s **Step 3 — Fetch (parallel)**
procedure verbatim:

- All 6 calls (`app_info` + 5 `context_*`) in a single message,
  `limit: 100, owned_only: true`
- For each response, handle it exactly as the arch skill's Step 3 does:
  on Claude Code a large result is auto-saved to disk by the harness
  ("Output has been saved to <path>") and `cp`'d into the cache; on Codex
  (and any harness without auto-save) the response arrives inline and is
  compact-written to `$ARCH_CACHE/<section>-raw.json` per the field
  whitelist in the arch-skill's SKILL.md

Then run the arch-skill's build.py to produce the bundle:

```bash
ARCH_SKILL="$HOME/.claude/skills/outsystems-app-architecture"
python3 "$ARCH_SKILL/scripts/build.py" "$ARCH_CACHE" "$ARCH_CACHE/.tmp.html" \
  --app-info       "$ARCH_CACHE/app-info-raw.json"      \
  --screens        "$ARCH_CACHE/screens-raw.json"       \
  --actions        "$ARCH_CACHE/actions-raw.json"       \
  --entities       "$ARCH_CACHE/entities-raw.json"      \
  --structures     "$ARCH_CACHE/structures-raw.json"    \
  --roles          "$ARCH_CACHE/roles-raw.json"
rm -f "$ARCH_CACHE/.tmp.html"   # don't need the arch HTML, just app-data.json
```

This populates `$ARCH_CACHE/app-data.json` AND
`$ARCH_CACHE/meta.json`. Both skills now benefit on subsequent runs.

### Step 4 — Render markdown

```bash
OUT="${OUTPUT_PATH:-$PWD/<APP_SLUG>.md}"
python3 "$SKILL/scripts/build.py" "$DOC_CACHE" "$OUT" \
  --app-data "$ARCH_CACHE/app-data.json"
```

### Step 5 — Report (3–5 lines)

- Output file path
- App + revision
- Counts (`X screens · Y actions · Z entities · …`)
- Cache state — "arch-cache reused" / "arch-cache populated by this run"
- Note: markdown is paste-ready for Confluence / wiki / pandoc → PDF

## Data shape contract

`build.py` reads `app-data.json` (produced by
`outsystems-app-architecture`'s build.py) in this shape:

```js
{
  app:        { key, name, type, revision, description, date },
  uiFlows:    [{ key, name }],
  screens:    [{ k, n, flow, desc, pub, date }],
  actions:    [{ k, n, kind: "action"|"function", desc, pub }],
  entities:   [{ k, n, desc }],
  enums:      [{ k, n, desc }],
  structures: [{ k, n, desc }],
  roles:      [{ k, n, desc, pub }],
  inheritedCount: number
}
```

build.py still supports a slow-path (--app-info + 5 --context-* args)
for direct CLI use, but the SKILL procedure does not invoke it.

## Output format

Single Markdown file. Standard headings, tables, bullet lists. No
HTML, no images, no Mermaid. Compatible with GitHub/GitLab, Confluence
"paste from Markdown", and pandoc → PDF/DOCX conversion.

## Cache rules

- **Reads from:** `~/.claude/cache/outsystems-app-architecture/<app-key>/app-data.json`
- **Writes its own cache to:** `~/.claude/cache/outsystems-app-documentation/<app-key>/`
  (the rendered bundle gets persisted so subsequent re-renders work
  even if arch-cache is later cleared).
- TTL on arch-cache freshness: 1 hour
- Freshness check: `app_info.revision` vs `arch_cache/meta.json.revision`

## Token budget (estimate)

| Scenario | Mechanism | Total |
|---|---|---|
| Arch-cache reused (typical workflow) | app_info probe + build.py | **~1.5K** |
| Arch-cache missing → auto-populate + render | Same as arch skill's first run + render | ~13K |
| Doc-cache re-render (arch later cleared) | build.py only | ~1K |

The typical case is **fast** because the natural workflow is
explore-then-document. The arch-cache-missing case costs the same as
just running the arch skill — no extra penalty for using docs.

## Harness notes

- This skill is **render-only** and normally reads the shared arch-cache,
  so the typical path (Step 4) makes no `context_*` calls and costs the
  same on Claude Code and Codex.
- The only harness-sensitive path is Step 3 (auto-populating a missing or
  stale arch-cache), which runs `outsystems-app-architecture`'s fetch: on
  Claude Code, `context_*` results above ~25 KB are auto-saved to disk by
  the harness and `cp`'d into the cache; on Codex there is no auto-save, so
  each response arrives inline and is compact-written to the cache. That
  skill's Harness notes and its 🔴 HARD STOP (don't read a harness-saved
  file back into context) both apply here whenever Step 3 runs.
- Cache location `~/.claude/cache/` is shared across harnesses (see the
  Step 1 note), so an arch-cache populated by either skill on either
  harness is reused by this one.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4). Skill-specific:

- **Don't write your own fetch logic.** The arch skill owns the fetch
  contract; docs is a renderer. If you need fields the arch bundle
  doesn't have, extend the arch skill instead.
- **Don't generate HTML here** — that's
  `outsystems-app-architecture`'s output. This skill produces Markdown
  specifically because customers want to paste it elsewhere.
- **Don't invent per-screen authorization or role assignments.** The
  arch bundle's `screens[]` array has no `role` field — only
  `isPublic`. If you emit a per-screen Roles column, you are
  confabulating from the app's primary role name (field-test report,
  Rui M., rmad employee directory). The build.py renderer follows this
  rule by design; if you produce output via a different code path
  (e.g. summarizing context_* responses directly), enforce it manually
  — render the app's roles as a flat list once, never cross-product
  with screens.

## When NOT to use

- Visual graph of the app → use `outsystems-app-architecture`.
- Tenant-wide docs across many apps → out of scope; document one app
  at a time, or wait for a future "tenant report" skill.
- Detailed behavioral docs (what each action returns, error paths) →
  requires reading the OML, beyond `context_*` data. Out of scope.
