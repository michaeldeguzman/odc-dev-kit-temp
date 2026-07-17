# Skills Catalog Conventions

The standard every skill in this bundle follows. Applying these makes
all skills look, behave, and cost roughly the same — and lets a
reviewer audit a new skill in 60 seconds.

Validated against:
- [Agent Skills spec](https://agentskills.io/specification)
- The existing `outsystems` plugin (LICENSE, plugin.json conventions)
- Empirical token-budget measurements from the two skills shipped

---

## 1. File layout (mandatory)

```
skills/<skill-name>/
├── SKILL.md
├── scripts/
│   └── build.py
└── assets/
    └── template.html
```

- **`scripts/` and `assets/` are the spec-recommended subdirs.** Don't
  put `build.py` or `template.html` at the skill root.
- **Don't add extra top-level dirs** unless you genuinely need
  `references/` (per the spec). Most skills won't.

## 2. Naming conventions

- **Skill dir name = `name` in frontmatter** (per spec).
- **All skill names prefixed `outsystems-`** so they cluster in any
  auto-discovery list.
- **Lowercase, hyphens only, no consecutive hyphens, no leading/trailing
  hyphen, ≤64 chars.**
- Examples: `outsystems-tenant-architecture`, `outsystems-app-architecture`,
  `outsystems-deploy-preview`, `outsystems-ai-agent-landscape`.

## 3. SKILL.md frontmatter (required fields)

| Field | Required | Constraint | Example |
|---|---|---|---|
| `name` | ✅ | Spec rules above | `outsystems-app-architecture` |
| `description` | ✅ | ≤1024 chars; describes **what + when**; includes natural-language triggers customers actually say | `Generate an interactive HTML graph of a single OutSystems app's architecture […]. Use when the user asks for the architecture of a specific app, "show me the architecture of [app]", […]` |
| `license` | ✅ | `MIT` (matches the plugin's LICENSE) | `MIT` |
| `compatibility` | ✅ | ≤500 chars; declares runtime requirements explicitly | `Designed for Claude Code. Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.` |
| `allowed-tools` | ✅ | Space-separated list of every tool the skill calls (Bash, Write, Edit, plus each `mcp__outsystems__*` tool) | `Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list` |
| `metadata.version` | ✅ | Semver string (quoted) | `"1.0.0"` |
| `metadata.author` | ✅ | `outsystems-r-and-d` | `outsystems-r-and-d` |

## 4. SKILL.md body — required sections (in this order)

1. **Title** — `# OutSystems <Skill Name>` (human-readable, not the slug)
2. **(One-paragraph summary)** — what it produces, in one sentence
3. **`## Prerequisites`** — MCP connection requirement, Python 3, any
   other preconditions. Tell the user explicitly to authenticate if not.
4. **`## The core trick — keep large data off the model's tokens`** —
   names the harness-disk auto-save pattern, shows the "saved to file"
   notice text, explains how the skill uses it.
5. **`## Procedure`** — numbered steps. Each step calls out which MCP
   tools are invoked and whether they should run in parallel.
6. **`## Data shape contract`** — what JSON shape `template.html`
   expects (`APP_DATA`, `ASSETS`, etc.). Shows the literal JS object.
7. **`## Cache rules`** — path, TTL, freshness check pattern, known
   false-negatives.
8. **`## Token budget`** — empirical measurements in a table (first run,
   cached, re-render).
9. **`## Troubleshooting`** — bulleted failure modes + remedies. Cover
   MCP disconnect, auth expiry, edge cases the procedure can hit.
10. **`## Anti-patterns — do NOT do these`** — encodes the lessons from
    other skills (`Don't use jq`, `Don't paginate prophylactically`,
    `Don't Read the harness-saved file into your context`).
11. **`## When NOT to use`** — points to sibling skills + cases that
    don't fit.

**Body length limits**: <500 lines / ~5K tokens (per spec). Both shipped
skills are <200 lines / <2K tokens.

## 4b. Standard Prerequisites (referenced by every skill)

Every skill in the catalog assumes the same three things. Skills SHOULD
reference this appendix from their Prerequisites section rather than
restating it.

- **`outsystems` MCP server connected** and authenticated. Verify via
  `mcp__outsystems__auth_status` if needed.
- **Running inside Claude Code** — the harness disk auto-save behavior
  (§8.1) is Claude-Code-specific.
- **Python 3.7+** available as `python3`. Stdlib only — no `pip
  install`, no `jq`, no external deps.

Skill-specific extras (e.g. "Mentor enabled on the tenant" for
`outsystems-mentor-copilot`) belong in the skill's own Prereq section
on top of this baseline.

## 5. `template.html` conventions

- **First-line HTML comment** with `template-version: <X.Y.Z>` — bump
  on breaking template changes (independent of skill `metadata.version`).
- **Placeholder pattern**: `/*__<NAMESPACE>__*/null` (e.g.
  `/*__APP_DATA__*/null`). Use:
  - **One placeholder** per logical bundle when the data is consumed
    together (app skill: `APP_DATA`).
  - **Multiple placeholders** when the data sections are independently
    cached (tenant skill: `ASSETS`, `ENVS`, `TENANT`).
- **Empty-state required**: opening the un-injected template directly
  must render a friendly "not yet populated" screen, not crash. Wire
  this via a `<template id="tpl-empty">` block that renders if the
  data const is `null`.
- **Two `<template>` blocks**: `tpl-app` (the real UI) and `tpl-empty`
  (the not-populated state). `boot()` chooses based on data.
- **Single `<script>` tag at the bottom** for the boot + render logic.
- **OutSystems dark theme variables** (from the tenant template's
  `:root { --os-bg, --os-red, --os-text… }`) — reuse for visual
  consistency.

## 6. `scripts/build.py` conventions

- **Pure Python stdlib only.** No `pip install` ever. (No `jq`, no
  `requests`, no `yaml` libraries.) `json`, `pathlib`, `sys`, `re`,
  `time`, `argparse` is the typical set.
- **Shebang + `chmod +x`** so customers can run it manually for
  debugging: `#!/usr/bin/env python3`.
- **Top docstring** explaining usage, inputs (read), outputs (write),
  and **why a script** (the token-efficiency rationale).
- **Exit codes**:
  - `0` success
  - `1` runtime failure (missing file, bad JSON, etc.)
  - `2` usage error (wrong args)
- **Error output goes to `stderr`**, never `stdout`.
- **Argument style**:
  - **Positional only** for ≤2 args (the common case is
    `<cache-dir> <output-path>`).
  - **`argparse` with named flags** when the script takes optional
    sources (e.g. the app skill's `--app-info`, `--screens`, etc.).
- **JSON validation**: parse with `json.loads()` before substituting,
  to fail loudly on bad data.
- **Idempotent**: running `build.py` twice on the same cache produces
  byte-identical output.

## 7. Cache convention

- **Path**: `~/.claude/cache/outsystems-<skill-name>/<identifier>/`
  - tenant: `outsystems-tenant-architecture/<tenant-id>/`
  - app: `outsystems-app-architecture/<app-key>/`
- **TTL**: 1 hour (default). Override with env var if a skill needs
  longer / shorter.
- **Freshness check pattern**: a single tiny MCP call (`limit:1` or
  `app_info`) returns a fingerprint (count, revision, hash). Compare to
  `meta.json`. If equal, reuse cache.
- **`meta.json` schema**: `{ "<fingerprint-field>": <value>,
  "fetched_at": <unix-timestamp> }`. Field name is whatever the skill
  uses to detect change (`total`, `revision`, etc.).
- **User can force refresh**: respect "refresh" / "fresh data" /
  "rebuild" in the prompt.

## 7b. Known OutSystems MCP API quirks (apply to all skills)

These were discovered by live testing — keep them in mind when writing
the procedure for any new skill that touches the same tools.

- **`mcp__outsystems__context_*` caps `limit` at 100.** Values above 100
  return HTTP 400 Bad Request. Use `limit: 100` as the ceiling for
  every `context_*` call (`context_screens`, `context_actions`,
  `context_entities`, `context_structures`, `context_roles`,
  `context_themes`, `context_agents`, `context_connections`,
  `context_search`).
- **`mcp__outsystems__app_list` accepts `limit: 1000` cleanly.** The
  tenant skill exploits this to trigger harness auto-save in a single
  call.
- **`mcp__outsystems__app_list` with no `limit`/`offset` returns only
  the first 100 results**, despite the docstring claiming "fetches
  every page". Don't rely on that auto-paginate behavior.
- **`mcp__outsystems__app_refs` times out on apps with large OML**
  (e.g. Banking Portal at rev 574). Either skip it or wrap with a
  short timeout + cached-on-success pattern.
- **`mcp__outsystems__context_themes` returns very large payloads**
  (>150K chars for typical apps). If your skill doesn't need theme
  inventory, skip it; otherwise expect harness disk save every time.
- **Auth tokens expire mid-session.** Procedures must handle
  "requires re-authorization" errors gracefully — tell the user to
  reconnect, not loop.
- **`mcp__outsystems__deploy_impact` returns `{impacts:null, status:null}`**
  consistently in this stage tenant (~5+ minute waits across 3 apps, no
  change). Either the analysis worker isn't running, or the MCP tool has
  a bug. Skills should not depend on this tool until it's validated to
  return real data. Use the synchronous-comparison pattern from
  `outsystems-deploy-preview` as a workaround.
- **`mcp__outsystems__app_revisions` is paginated** with the same shape
  as `app_list` (`page:{...}, results:[...]`). Default 100/page,
  6 pages for Banking Portal (574 revisions). Avoid full enumeration
  unless really needed.
- **`mcp__outsystems__app_refs` cannot handle >2 parallel calls.**
  Empirically: 3+ in parallel saturates an upstream queue; all
  in-flight calls (and ~10s of subsequent calls) time out. Tools that
  do bulk dependency analysis MUST throttle to 1–2 parallel max with
  ~5s cool-downs between batches. Sequential is safest. This makes
  full-tenant dependency scans inherently slow (10–15 min for ~150
  consumer assets).
- **`mcp__outsystems__context_screens` does NOT return per-screen
  authorization / role-assignment data.** It returns `isPublic` (bool
  — anonymous-accessible) but no list of roles allowed to access the
  screen. Skills MUST NOT confabulate role assignments per screen
  (field-test report: Rui M., rmad employee directory — the skill
  output stated every common-flow screen had role
  `RMadEmployeeDirectory` when in Studio they were all
  `Accessible by: Everyone`). If a future MCP server version surfaces
  authorization metadata, capture it via compact-write whitelist
  changes; until then, never cross-product `roles[]` with `screens[]`
  in any output. This is enforced in the v1.3.1+ anti-patterns of
  both `outsystems-app-architecture` and `outsystems-app-documentation`.

## 7c. Common troubleshooting (referenced by every skill)

These failure modes apply across the catalog. Skills SHOULD reference
this section rather than restating them.

- **MCP server disconnected** → tell the user to reconnect the
  `outsystems` MCP server (`/mcp` then `outsystems` → Reconnect).
- **Auth token expired mid-session** → the deferred
  `mcp__outsystems__authenticate` tool surfaces an authorization URL
  the user opens in their browser. On remote / SSH sessions the
  callback page fails to load; have the user paste the full
  `localhost:7890/callback?…` URL and call
  `mcp__outsystems__complete_authentication { callback_url: "<that URL>" }`.
- **`python3` not on PATH** → very rare on modern dev machines. Ask
  the user to install (`brew install python3` on macOS; preinstalled
  on most Linux distros).
- **HTTP 400 on a `context_*` call** → check `limit` is ≤ 100
  (§7b — context service caps at 100).

Skill-specific failures (`app_info` 404, `env_apps` empty for fresh
deploys, etc.) belong in the skill's own Troubleshooting section.

## 8. Token-efficiency rules (in priority order)

1. **Deliberately oversize the heavy MCP request** so Claude Code's
   harness auto-saves the response to disk (use the API's max
   accepted limit — see §7b for caps). The skill passes that path to
   `build.py`. Asset data never enters the model.
2. **Compact-Write inline responses.** When a tool returns its
   payload in-context (under the ~25 KB harness threshold) and the
   procedure needs that payload on disk, the model must emit ONLY
   the fields `build.py` reads — never the full MCP shape. Each
   skill's SKILL.md must include a per-section field whitelist for
   this purpose. **This is the single biggest first-run token-saver
   after the harness-disk pattern.** Empirically saved ~4-5K tokens
   on the app-architecture skill (17K → 12-13K).
3. **No Bash transforms in the model's output.** `build.py` does it all.
4. **No jq.** It's not guaranteed to be installed.
5. **Cache aggressively.** Cached re-runs should land under ~3K tokens.
6. **Minimize model turns.** Run independent tool calls in parallel
   (a single message containing N MCP fetches + N Writes + 1 Bash).
   Each extra turn adds ~30s wall-clock latency.

### 8a. Optimizations from empirical testing

Status legend:
- ✅ Applied in catalog v0.4 polish pass (May 2026)
- 🟡 Deferred to v2.0 (changes runtime behavior — needs more testing)

These were discovered while measuring real skill runs.

🟡 **Defer `auth_status` until first MCP fetch fails.** The freshness
probe (typically `app_info` or `app_list?limit=1`) will itself return
"requires re-authorization" on expired tokens. Use that error as the
trigger for the auth flow, rather than pre-flighting with `auth_status`.
Saves ~230 tokens per cached invocation, applies to every skill in the
catalog. Trade-off: one extra retry on the rare expired-token case.
**Held for v2.0** — changes runtime behavior, needs the harness
auth-error path validated in a separate test pass.

✅ **Cache `env_list` at tenant scope.** Stable data — environments
change rarely. Cache at
`~/.claude/cache/outsystems-tenant-envs/<tenant-id>.json` with a
24-hour TTL, share across all skills in a session. Saves ~165 tokens
+ one parallel MCP call per skill invocation on warm sessions.
**Applied in v0.4** to `outsystems-deploy-preview` (the only catalog
skill currently using `env_list`). Documented as a cross-skill cache
that any future env-aware skill should also consume.

✅ **Tighten SKILL.md bodies.** Empirical finding (catalog v0.3): each
SKILL.md body costs ~1.5–2K tokens to load, every invocation. On a
warm/cached run where MCP fetches + Writes drop to ~0, the procedure
markdown becomes the *majority* of the spend. **Applied in v0.4** via
two reductions:

- ✅ **Stripped explanatory prose** — the duplicated "core trick"
  /  harness-disk explanation that appeared in 4 skills' SKILL.md is
  now a single line pointing to CONVENTIONS §8.1.
- ✅ **Hoisted shared anti-patterns** — `Don't use jq`, `Don't
  paginate prophylactically`, `Don't Read the harness-saved file`
  are all in CONVENTIONS §8.4 / §8.1 and §8 generally. Each skill's
  anti-pattern list now contains only the skill-specific items, with
  a one-line "Shared rules apply (CONVENTIONS §X)" preamble.

Result: ~15–20% size reduction per SKILL.md across the catalog. The
trade-off (less self-contained skill files, reviewers need both docs)
is acceptable for the per-customer-session token math at scale.

### 8c. Empirical observation — the "mid-sized payload trap"

Token cost is **non-linear** with app/tenant size. Tiny responses
(<5 KB) and large responses (>25 KB) are both cheap; mid-sized
responses (10–24 KB) are the expensive case.

- **Tiny responses (<5 KB)**: come back inline, Write is cheap.
- **Mid-sized (10–24 KB)**: come back inline → must be round-tripped
  through the model to be Written to disk → **double-pays** for the
  payload (once as MCP result entering context, once as Write content
  leaving context).
- **Large (>25 KB)**: harness auto-saves → model never sees the bytes,
  payload cost ≈ 0 regardless of size.

**Counter-intuitive consequence:** a bigger app/tenant can cost
*fewer* model tokens than a mid-sized one, because more of its
responses cross the auto-save threshold.

**Implication for skill design:** the v0.4 "deliberate overfetch"
trick (§8b) directly addresses this — push borderline payloads over
the threshold by fetching more than you need, then filter in
`build.py`. The harness-disk-save is a step function, not a gradient;
ride it intentionally.

### 8b. Future technique — "deliberate overfetch" to force auto-save

Once §8.1–§8.6 are exhausted, a further lever exists: **deliberately
ask for more data than you need** so the response crosses Claude
Code's auto-save threshold (~25 KB tool result) and lands on disk
with zero model-token cost.

Concrete pattern: a `context_*` call with `owned_only:false` returns
both owned items AND inherited-library items. The inherited items
are usually dead weight for the skill, but they pad the response
above the auto-save threshold. The transform script (`build.py`)
filters them out at `ownerAppKey == app_key` — final output is
identical, but the model never saw the payload.

Empirically, this can save another ~5K tokens per first run on
skills that have borderline-sized inline responses (e.g. the
app-architecture skill's screens ~19 KB and structures ~11 KB).

**Caveats — why this is filed as a future technique, not a default:**

- Risks tripping the API's per-call `limit` cap (see §7b — context
  service caps at 100). Some apps' inherited counts exceed 100.
- Couples the procedure tightly to the harness threshold value
  (~25 KB), which is a Claude Code implementation detail that could
  change.
- Adds confusing "we ask for more than we use" semantics to the
  procedure, which is harder for skill reviewers to validate.

Use only after a skill has been stable in production for a release
cycle and the gain is empirically measured worthwhile.

## 9. Versioning

- **`metadata.version`** is the skill's semver. Bump it when the
  procedure or contract changes.
- **Template version** (in the HTML comment) is independent. Bump it
  on UI/structure changes that would break previously-saved caches.
- **Don't increment for typo fixes** in the SKILL.md body.

## 10. Testing checklist (before shipping)

Run this checklist on every new skill before adding it to the bundle:

- [ ] **Frontmatter manual audit**: run the validation Bash block from
  the v1.2 audit (it's saved in this conversation's transcript). All
  fields present, name matches dir, lengths within bounds.
- [ ] **Synthetic fixture test**: feed `build.py` 3–5 hand-crafted
  records in the expected MCP shape; output renders, placeholders
  resolve to 0, asset counts match.
- [ ] **Cached re-render test**: run `build.py` again with no `--*`
  flags; output is byte-identical to the fresh run (`diff -q`).
- [ ] **Auto-discovery confirmation**: copy to `~/.claude/skills/`,
  start a fresh Claude Code session, confirm the skill appears in the
  available-skills list with its description.
- [ ] **Live MCP test**: trigger the skill via natural language (use
  one of the trigger phrases from the description). Watch token cost
  in the status bar; should match the SKILL.md token budget within
  ~30%.
- [ ] **Live MCP error-path test**: confirm every MCP call in the
  procedure uses a `limit` value the API actually accepts. The
  synthetic fixture won't catch HTTP 400 from bad limit values —
  only the live test will. See §7b for known caps.
- [ ] **Compact-Write verification**: inspect the cache files written
  during a fresh run. Each `<section>-raw.json` should be ≤50% the
  size of the raw MCP response (rough rule of thumb). If they're
  closer to the raw size, the procedure isn't enforcing the per-section
  field whitelist — fix SKILL.md.
- [ ] **Anti-patterns enforced**: grep the SKILL.md for `jq` —
  must only appear in `Don't use jq` warnings.
- [ ] **Bundle tarball test**: extract the tarball into a clean dir,
  run the synthetic fixture from there. Confirms relative-path
  references in build.py are correct.

## 11. Distribution checklist (before handing to engineering)

- [ ] All testing checklist items above are green.
- [ ] `README.md` table at the root is updated with the new skill row.
- [ ] Tarball is refreshed (`tar -czf outsystems-mcp-skill.tar.gz outsystems-mcp-skill/`).
- [ ] Tarball is small (<100 KB for a typical 1–3 skill bundle).
- [ ] No skill-specific stale files in `~/.claude/cache/` from your
  testing (or note them in the handoff so testers don't get confused).

## Appendix: minimal starter SKILL.md

Copy this template and fill in `<placeholders>` when starting a new
skill:

```markdown
---
name: outsystems-<short-skill-name>
description: <One-sentence what + "Use when the user asks for…" + 3-5 trigger phrases customers would actually say>.
license: MIT
compatibility: Designed for Claude Code. Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: Bash Write Edit mcp__outsystems__auth_status <other mcp tools used>
metadata:
  version: "1.0.0"
  author: outsystems-r-and-d
---

# OutSystems <Skill Name>

<One paragraph summary.>

## Prerequisites

- The `outsystems` MCP server is connected. Verify with
  `mcp__outsystems__auth_status`.
- Running inside Claude Code (the harness disk-save feature is
  Claude-Code-specific).
- Python 3.7+ as `python3`.

## The core trick — keep large data off the model's tokens

<Explain how the skill triggers the harness disk-save path. Reference
the "Output has been saved to <path>" notice.>

## Procedure

### Step 1 — Auth + identify
…

### Step 2 — Cache freshness
…

### Step 3 — Fetch (parallel)
…

### Step 4 — Build
```bash
python3 "$SKILL/scripts/build.py" "$CACHE" "$OUT" <flags...>
```

### Step 5 — Report
…

## Data shape contract
…

## Cache rules
…

## Token budget
…

## Troubleshooting
…

## Anti-patterns — do NOT do these
- **Don't use `jq`.** Not guaranteed to be installed. Use `build.py`.
- **Don't paginate prophylactically.** Oversize the request; let the
  harness handle it.
- **Don't `Read` the harness-saved file into your context.**

## When NOT to use
…
```
