---
name: outsystems-deploy-preview
description: Generate an HTML preview of what would happen when promoting an OutSystems app from one environment to another (e.g. Dev → Test or Test → Prod). Shows source vs target revision, fresh-deploy vs update classification, revision gap, and risk indicators. Use when the user asks for a deploy preview, "what would change if I deploy [app] to [env]", "is it safe to promote [app]", "preview the deploy of [app]", "show me the deploy plan for [app]", "what happens if I push [app] to [env]", or similar.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_info mcp__outsystems__env_list mcp__outsystems__env_apps
metadata:
  version: "1.2.0"
  author: outsystems-r-and-d
---

# OutSystems Deploy Preview

Produces a self-contained HTML report comparing an OutSystems app's
state in a source environment against a target environment. Classifies
the promotion as **fresh deploy / update / no-op / concerning** and
assigns a **risk level (none / low / medium / high / concerning)**.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. Shared rules: §7b
(deploy_impact known-null — documented below), §8 (token-efficiency).

## Design decision — no `deploy_impact` in v1.0

The naïve approach is to wrap `mcp__outsystems__deploy_impact` +
`deploy_impact_status` (the async impact analyzer). **Don't.** As of
v1.0 of this skill, the `deploy_impact` MCP tool returns
`{impacts:null, status:null}` consistently across apps and
environments — likely a MCP/tenant configuration issue documented in
CONVENTIONS §7b. The skill is designed to work without it.

Instead, v1.0 computes the preview client-side from:
- `app_info` — source app metadata (latest revision)
- `env_apps(target_env, search=app_name)` — target env's deployed revision
- `env_list` — environment context (names, purposes, hosts)

This synchronous design works **for both fresh deploys and updates**,
costs ~3K tokens first-run, and doesn't depend on the broken API.

If `deploy_impact` becomes reliable later, v1.1 can layer it on as an
optional "authoritative" data source.

## Procedure

### Step 1 — Auth + identify app + identify target env

Call `mcp__outsystems__auth_status`. If `logged_in: false`, stop.

Resolve the app from the user's prompt:
- If user gave an asset key (UUID), use it directly.
- Otherwise call `mcp__outsystems__app_list` with `search: "<name>"`.
  - 1 match → use it.
  - Multiple → list candidates, ask user to pick.
  - 0 matches → ask for a more specific name.

Resolve the target environment from the user's prompt:
- If user named an env ("Test", "Production"), match against `env_list`.
- If user said "promote/push" without target → ask user to pick from the
  available environments.

```
APP_KEY        = <asset key>
APP_NAME       = <human name>
TARGET_ENV_KEY = <env key>
TARGET_ENV_NAME = <e.g. "Test">
CACHE          = ~/.claude/cache/outsystems-deploy-preview/<APP_KEY>_<TARGET_ENV_KEY>/
SKILL          = <this skill's directory>
mkdir -p "$CACHE"
```

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

### Step 2 — Cache freshness (only if cache exists)

If `$CACHE/meta.json` is present:
1. Call `mcp__outsystems__app_info` with `key: <APP_KEY>` (cheap).
2. Compute `AGE = now - meta.fetched_at`.
3. If `AGE < 600` (10 minutes — shorter TTL than other skills because
   deploys can happen rapidly) AND `app_info.revision == meta.source_revision`
   → **cache valid, jump to Step 5**.

Use a shorter TTL here because the whole point is to see fresh state.
Stale cache could hide a just-completed deploy.

If the user said "refresh" / "fresh data", skip this step.

### Step 3 — Fetch (parallel)

Call these in a single message so they run concurrently:

- `mcp__outsystems__app_info` with `key: <APP_KEY>`
- `mcp__outsystems__env_apps` with `env_key: <TARGET_ENV_KEY>`,
  `search: <APP_NAME>` — filtered to keep response small
- `mcp__outsystems__env_list` — **only if the shared env cache is missing or stale**
  (see env-list shared cache below)

All responses fit in-context comfortably (`app_info` is one record,
`env_apps` is filtered to ~1 app, `env_list` is 3 records). **Save
each to cache in compact form per the whitelist below.**

#### env-list shared cache (cross-skill)

Environment data is stable. Check
`~/.claude/cache/outsystems-tenant-envs/<TENANT_ID>.json` before
calling `env_list`:

- **Exists AND <24 h old** → read it; skip the `env_list` call.
- **Missing or stale** → call `env_list`, save the compact form to the
  shared cache path *and* to `$CACHE/env-list-raw.json`. Subsequent
  skill invocations (this one or others) reuse it.

Saves ~165 tokens + one parallel MCP call per warm-session invocation.

### Compact-write field whitelist (mandatory for inline responses)

| Section | Fields to keep |
|---|---|
| `app-info-raw.json`        | full response (already small — one record with `assetKey, name, assetType, revision, revisionDateTime, description`) |
| `target-env-apps-raw.json` | `results[].(applicationKey, name, revision, deploymentDateTime, buildKey, url)` |
| `env-list-raw.json`        | `results[].(key, name, purpose, hostname, region)` |

Wrap each in the same envelope shape the MCP returns (e.g.
`{"results":[...]}` for env-list / env-apps, raw object for app-info).

### Step 4 — Build (fresh)

```bash
OUT="${OUTPUT_PATH:-$PWD/deploy-preview.html}"
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT" \
  --app-info       "$CACHE/app-info-raw.json"       \
  --target-env-apps "$CACHE/target-env-apps-raw.json" \
  --env-list       "$CACHE/env-list-raw.json"        \
  --target-env-key "$TARGET_ENV_KEY"                 \
  --source-env-name "Development"
```

`build.py` does the diff math, classifies risk, and injects into the
template.

### Step 5 — Build (cached re-render)

```bash
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT"
```

### Step 6 — Report (3–5 lines)

- Output file path
- App + revision (source) → target env
- Classification: fresh deploy / update (gap N revisions) / no-op
- Risk level + 1-line reason
- Cache state — "used (Xs old)" or "refreshed"

## Data shape contract

`build.py` writes a single compact bundle to `$CACHE/preview-data.json`:

```js
PREVIEW_DATA = {
  app: { key, name, type, description, sourceRev, sourceDate },
  sourceEnv: { name },          // "Development" by default
  targetEnv: { key, name, purpose, host },
  target: { deployed: bool, rev?, date?, buildKey?, url? },
  classification: "fresh" | "update" | "noop" | "concerning",
  risk: { level: "none"|"low"|"medium"|"high"|"concerning", label, note },
  revGap: number,               // source - target (0, positive, or negative)
  recommendations: [ string, ... ]
}
```

Risk classification rules (in `build.py`):

| Condition | Classification | Risk |
|---|---|---|
| `target.deployed == false` | fresh | medium |
| `revGap == 0` | noop | none |
| `revGap == 1` | update | low |
| `2 <= revGap <= 5` | update | low |
| `6 <= revGap <= 50` | update | medium |
| `revGap > 50` | update | high |
| `revGap < 0` (target ahead) | concerning | concerning |

### Post-publish failure modes to mention in recommendations

When risk is **high / concerning**, the rendered preview's
`recommendations[]` should include a one-liner pointing the user at the
publish-validator-rejection taxonomy in case the publish itself fails
post-promotion:

> *"If the publish fails with OS-APPS-40028 ('Input binary does not
> contain a valid OML'), see
> `outsystems-design-to-app/references/gotchas/publish-validator-rejections.md`
> for the rejection-cause taxonomy (missing Entities chunk, stale
> ReferersData.xml, RadioGroup auto-create children duplicated, etc.).
> Round-trip through `LoadESpace`/`SaveESpace` is NOT a sufficient
> quality bar — the server-side validator is stricter."*

This is documentation only — `build.py` doesn't need to know the
taxonomy. The recommendation just routes the user to the right
diagnostic doc if they hit this failure mode after the deploy.

## Cache rules

- Location: `~/.claude/cache/outsystems-deploy-preview/<app-key>_<target-env-key>/`
- TTL: **10 minutes** (shorter than other skills — deploy state changes fast)
- Freshness check: compare `app_info.revision` to cached
  `source_revision`. Cheap (~500 tokens).
- Force refresh: user says "refresh" / "fresh data" / "rebuild" /
  "actually deploy" (the last one because the user wants to see
  the latest state right before deploying).

## Token budget (estimate)

| Scenario | Mechanism | Total |
|---|---|---|
| First run, typical app | 3 small inline responses + build.py | **~5K** |
| Cached run | app_info probe + build.py | ~2K |
| Re-render only | build.py | ~1K |

Lower than tenant (~3K) and app-architecture (~12K) because there's
much less data to move — three small queries vs. dozens.

## Harness notes

- This skill's three queries are tiny (`app_info` is one record, filtered
  `env_apps` is ~1 app, `env_list` is 3 records), so every response arrives
  inline on both Claude Code and Codex — none is large enough to hit Claude
  Code's ~25 KB harness disk auto-save. First-run cost (~5K) and
  cached/re-render costs are therefore the same on both harnesses; the
  compact-write-to-cache path in Step 3 is the single handling path on either.
- Cache location `~/.claude/cache/` is shared across harnesses (see the
  Step 1 note), including the cross-skill `outsystems-tenant-envs` env-list
  cache.

## Troubleshooting

Common failures (MCP disconnect, auth expiry, missing `python3`) live
in CONVENTIONS §7c. Skill-specific:

- **`env_apps` returns empty results** for the searched app → app
  isn't deployed in target env. Classification: "fresh deploy".
  Render normally; this is a valid case, not a failure.
- **App name matches multiple apps** → list candidates and ask user.
- **Target env key not in `env_list`** → user named an invalid env.
  Re-prompt with the list of available envs.
- **`deploy_impact` API becomes reliable later** → wire in as optional
  authoritative source in a future version; do not block on it.

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4 no-jq). Skill-specific:

- **Don't call `deploy_impact` / `deploy_impact_status`.** Known
  broken (see CONVENTIONS §7b for the `deploy_impact` null-response
  issue). Synchronous comparison via the Step-3 fetch is the reliable
  path.
- **Don't fetch `env_apps` without the `search` filter.** Production
  environments can have hundreds of apps; the filter keeps responses
  small — on Claude Code that avoids an unnecessary harness disk
  auto-save, and on harnesses without auto-save (Codex) it avoids a
  large inline payload that would cost extra tokens.
- **Don't paginate `app_revisions`** to compute a richer "what's in
  the gap" view. v1.x stops at `rev_gap` as a number; pagination
  doubles MCP calls for marginal info gain.

## When NOT to use

- User wants to **actually deploy**, not preview → use
  `mcp__outsystems__deploy_start` directly (not yet wrapped as a skill).
- User wants to see what's deployed across **all** envs → that's a
  different skill (env-status overview).
- User wants the architecture of the app (entities/screens/actions) →
  use `outsystems-app-architecture`.
