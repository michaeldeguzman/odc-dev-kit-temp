# Changelog

All notable changes to the catalog. Each skill is versioned independently
(see `metadata.version` in each `SKILL.md`); this file collects them.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

Nothing pending. Submit issues / ideas to inform the next batch.

---

## 2026-07-13 — Codex install path in Installation docs

### Changed

- `README.md` — Installation section now shows both `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex CLI) paths, with agent-invoked (Path A) and manual (Path B) variants for each. Added a skills-directory table at the top and a note that Codex's `~/.codex/skills/` is deprecated (per Paulo's own `install_skill_pack.py`).
- `docs/INTRO.md` — 5-step first-time path now mentions both skills directories; fixed the "Claude Code only, doesn't work on Codex" line (was wrong post-portability-wave); "How to install" section now covers both agents with an agent-invoked shortcut.

Closes a docs gap left by the portability wave: individual skills were declared agent-neutral, but the Installation instructions were still 100% Claude-Code-only, blocking Codex users from onboarding.

---

## 2026-07-13 — Catalog is agent-neutral (Codex + Claude Code)

### Milestone

Every skill in the catalog is now validated on both Claude Code and Codex CLI. This closes the "agentic-coding-for-OutSystems" track: developers can use whichever harness matches their workflow (Claude Code for lowest first-pass cost on large-MCP flows; Codex CLI for parity of procedure + guardrails).

The per-skill portability work was contributed by **Paulo Ribeiro** (OutSystems R&D) across the 2026-07-08 → 2026-07-11 wave — see the individual `## <skill> v1.X.0: works on Codex + Claude Code` entries below for the exact prose changes made to each skill.

### Changed

- `skills/outsystems-plan-to-mentor/SKILL.md` — normalized the `compatibility:` line to the pattern Paulo established across the portability wave (`Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — …)`). Bumped v1.0.0 → v1.1.0.
- `docs/SKILL-INDEX.md` — rewrote the *Compatibility note* section to reflect dual-agent support; fixed a stale "10 core skills" count (it's 11 since `outsystems-plan-to-mentor` was vendored on 2026-06-29).
- `README.md` — flipped the harness-compatibility table's *Codex CLI* row from ❌ Not supported to ✅ Supported, preserving the token-cost caveat. Introduced Codex directly under Claude Code in the table.

### Not changed

- No skill procedure or contract logic. This is docs + one compatibility-string normalization only.
- Existing per-skill portability CHANGELOG entries (below) are the authoritative record of what changed in each skill.

---

## 2026-07-11 — `outsystems-custom-code` v1.1.0: works on Codex + Claude Code

Compatibility update — no behavior change. The build, test, packaging, upload,
and publish workflow is unchanged.

- Compatibility metadata now names both agents.
- The title no longer names one agent.
- The MCP setup paragraph keeps the Claude Code flow as a concrete example and
  adds a neutral fallback for other agents.

---

## 2026-07-10 — `outsystems-design-to-app` v1.1.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- Prose that named Claude-only tools now reads neutrally — same instructions,
  and agents without a given built-in tool are told the equivalent inline step
  (e.g. the one confirmation before firing Mentor is asked inline on Codex).
- The shared cache note clarifies the cache path is the same on every agent.
- New "Harness notes" section at the end covers the one practical difference:
  a first pass costs more on Codex because it receives large MCP payloads
  inline, where Claude Code's harness saves them to disk.

Every step that touches the tenant — app creation, the Mentor calls, publish —
and every confirmation gate is byte-for-byte identical to v1.0.0. Verified by
running the skill on both agents against the same tenant.

---

## 2026-07-10 — `outsystems-mentor-copilot` v1.2.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- Behaviors specific to Claude Code's harness (the >25 KB disk auto-save, the
  max-tokens spill on the terminal poll, the sandbox limit on long sleeps, the
  background-run flag) are now attributed to it, each with the equivalent step
  for agents without them.
- New "Harness notes" section covers the one practical difference: a first run
  costs more on Codex because Mentor's large scan events arrive inline;
  re-rendering a past run costs the same on both.
- The shared cache note clarifies the cache path is the same on every agent.

The publish safety gate is unchanged: the report surfaces a Publish handoff and
never auto-publishes — the human confirms. Verified by running the skill on both
agents against the same tenant.

---


## 2026-07-10 — `outsystems-mentor-polling-behavior` v1.4.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- Slash-command examples reworded to name-invocation phrasing, and the config
  note says "your agent's skills directory" with the Claude Code path kept as
  the concrete example.
- Prose that named Claude-only tools now reads neutrally; where a built-in tool
  doesn't exist on an agent, the text says what to do instead (e.g. on Codex the
  one confirmation before firing Mentor is asked inline — same question, same
  wait for an explicit answer).
- The HARD STOP blocks attribute the interactive permission prompt to Claude
  Code while keeping the same command discipline on agents without it.
- The shared cache note clarifies the cache path is the same on every agent.
- New "Harness notes" section covers the one practical difference: Mentor's
  10–50 KB per-poll events arrive inline on Codex, so a run costs more there —
  which is exactly what this skill's 30s polling cadence helps contain. The
  render and summary modes make no MCP calls and cost the same on both.

Every safety gate — the login stop, the single confirmation before
`mentor_start`, the no-auto-publish rule, cancel-on-abort, and the
findings-display rules — is byte-for-byte identical to v1.3.0. Verified by
running the skill on both agents against the same tenant.

---


## 2026-07-10 — `outsystems-spec-driven-build` v1.1.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- Prose that named Claude-only tools now reads neutrally; where a built-in tool
  doesn't exist on an agent, the text says what to do instead (e.g. on Codex the
  one confirmation before firing Mentor — and the interview questions — are
  asked inline; same questions, same wait for explicit answers).
- The shared cache note clarifies the cache path is the same on every agent.
- New "Harness notes" section covers the one practical difference: a greenfield
  build's Mentor polling costs more on Codex because large MCP payloads arrive
  inline, where Claude Code's harness saves them to disk. Re-rendering a past
  build makes no MCP calls and costs the same on both.

Every step that touches the tenant — app creation and the Mentor call — and
every safety gate (the single confirmation before `mentor_start`, the
never-auto-publish handoff with `publish_start` not even granted, the
System-module-template refusal, the spec-validation rules) is byte-for-byte
identical to v1.0.0. Verified by running the skill on both agents against the
same tenant.

---


## 2026-07-09 — `outsystems-app-architecture` v1.4.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- The response-handling step attributes the auto-save-to-disk behavior to
  Claude Code and gives agents without it (Codex) the same compact-write path.
- The 🔴 HARD STOP anti-pattern gains a Codex counterpart (don't re-dump an
  inline `context_*` payload or re-read the compact cache file); the existing
  Claude Code guardrail is unchanged.
- New "Harness notes" section: first-run cost is higher on Codex because the
  auto-save discount doesn't apply. The cache path is the same on every agent.
- Capitalized tool names in prose reworded neutrally.

Verified by running the skill on both agents against the same tenant.

---


## 2026-07-09 — `outsystems-app-documentation` v1.4.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- The arch-cache auto-populate step attributes the auto-save-to-disk behavior
  to Claude Code and gives agents without it (Codex) the same compact-write
  path, delegating to `outsystems-app-architecture` (whose guardrails apply
  when it runs).
- New "Harness notes" section: this render-only skill costs the same on both
  agents in its typical path; only the auto-populate path differs. The cache
  path is the same on every agent.
- Capitalized tool names in prose reworded neutrally.

Verified by running the skill on both agents against the same tenant.

---


## 2026-07-09 — `outsystems-dependency-impact` v1.3.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before. The skill is read-only.

- `compatibility` frontmatter now names both agents.
- The `app_list` fallback attributes the auto-save-to-disk behavior to Claude
  Code and gives agents without it (Codex) the same save-to-cache path.
- New "Harness notes" section: only that one `app_list` response differs by
  agent — the per-asset scan that dominates first-scan cost arrives inline on
  both, so scanning costs the same, and cached runs are identical. The cache
  path is the same on every agent.
- Capitalized tool names in prose reworded neutrally.

Verified by running the skill on both agents against the same tenant.

---


## 2026-07-09 — `outsystems-deploy-preview` v1.2.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before. The skill is read-only — it previews a
promotion and never calls a tenant-changing tool.

- `compatibility` frontmatter now names both agents.
- New "Harness notes" section: the three queries it makes are tiny and always
  arrive inline, so it costs the same on Claude Code and Codex.
- The `env_apps` anti-pattern names what an unfiltered response does on each
  agent.
- Capitalized tool names in prose reworded neutrally.

Verified by running the skill on both agents against the same tenant.

---


## 2026-07-09 — `outsystems-tenant-architecture` v1.5.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- The response-handling step attributes the auto-save-to-disk behavior to
  Claude Code and gives agents without it (Codex) the same compact-write path.
- The 🔴 HARD STOP anti-pattern gains a Codex counterpart (don't re-dump the
  inline `app_list` payload or re-read the compact cache file); the existing
  Claude Code guardrail is unchanged.
- New "Harness notes" section: large tenants cost more on Codex because the
  auto-save discount doesn't apply. The cache path is the same on every agent.
- Capitalized tool names in prose reworded neutrally.

Verified by running the skill on both agents against the same tenant.

---


## 2026-07-09 — `outsystems-app-architecture` v1.3.3 + `outsystems-dependency-impact` v1.2.3 (app_refs deps parser fix)

### Driver

The PR 3 portability-wave live smoke (2026-07-09) surfaced a pre-existing bug:
`app_refs` returns references as `{producerAssetName, producerAssetKey, kinds: [...]}`
(schemaVersion 2, source `context-service`; verified live against
professionalservices.outsystems.dev), but both skills' parsers predated that
shape. The smoke only looked clean because its test app's references were all
built-ins (dropped either way).

### Fixed — live `app_refs` reference shape

- **`outsystems-app-architecture`** (`scripts/build.py`, `_build_deps`) read
  `name` / `kind` / `moduleKey`, so `name` was always `""` and **every**
  reference was dropped before the built-in filter — the Dependencies layer
  (AI model connections + library refs, the v1.2 headline feature) rendered
  empty for any app with a real non-built-in dependency. Now reads
  `producerAssetName` / `producerAssetKey` with legacy fallbacks and derives the
  kind via a new shape-tolerant `_ref_kind()` helper.
- **`outsystems-dependency-impact`** (`scripts/build.py`, `_build_bundle`)
  already keyed on `producerAssetKey` so it never dropped refs, but rendered
  `kind: "?"` against the `kinds` list. Now maps `kinds` via the same helper and
  falls back to `producerAssetName` in the reverse index.

`_ref_kind()` accepts every observed shape — legacy scalar `kind`,
oml-fallback `importedKind`, and the context-service `kinds` list (joined).
`_categorize_dep` behavior is unchanged: `AIModelConnection` → AIModel via the
legacy scalar; context-service entity-imports default to Library (AI model
connections do not flow through `app_refs` on the current platform — they surface
via `context_connections`). `outsystems-app-documentation` is unaffected — its
Dependencies section reads `inheritedCount`, never `deps`.

### Verified

- New unit tests with real 2026-07-09 live fixtures (`scripts/tests/`):
  app-architecture 5/5, dependency-impact 2/2 — all fail pre-fix, pass after.
- Deps-present live end-to-end smoke on `WBG_PoC` (rev 135): fixed build.py
  renders `deps:3` (UltimatePDF, WorldBankTheme, OutSystemsDataGrid); the
  unfixed parser on the identical live section files renders `deps:0`.

---

## 2026-07-08 — `outsystems-ai-agent-landscape` v1.2.0: works on Codex + Claude Code

Compatibility update — no behavior change. Anyone using the skill on Claude Code
(or Kiro) sees it work exactly as before.

- `compatibility` frontmatter now names both agents.
- The response-handling step attributes the auto-save-to-disk behavior to
  Claude Code and gives agents without it (Codex) the same compact-write path.
- New "Harness notes" section: a first run costs about 2x on Codex because
  large responses arrive inline; cached runs cost the same. The cache path is
  the same on every agent.

Verified by running the skill on both agents against the same tenant.

---


## 2026-06-29 — `outsystems-plan-to-mentor` v1.0.0 (vendored from Paulo's repo) + trigger-map audit

### Driver

Paulo Ribeiro (OutSystems R&D) submitted two skills via [`PauloACRibeiro/portable-agent-skills`](https://github.com/PauloACRibeiro/portable-agent-skills) targeting the "agentic-coding-for-OutSystems" track — a different developer persona than Mentor's "vibe-coding" angle. PRD → plan → pseudo-code → Mentor flow, mirroring how senior devs work in Claude/Codex on Python or C#.

Before vendoring, ran a catalog-wide **trigger-map audit** (commit `81adb9d`) to ensure the additions land on a clean, non-overlapping taxonomy. Without this, adding two more Mentor-adjacent skills risked the agent picking the wrong skill (research suggests triggering accuracy degrades past ~10-15 skills in one harness, and we'd cross that line).

### Added — `docs/TRIGGER-MAP.md` (new shared artifact, commit `81adb9d`)

- Canonical "input → skill" map for both the agent (auto-routing reference) and human reviewers (catalog cohesion gate).
- "When ambiguous" disambiguation rules covering "Build me an app" / "Generate Mentor prompt for X" / "Show me my [thing]" / "Document this" / "Run Mentor on my app to do X".
- Catalog hygiene rules + pre-vendor checklist for new skill candidates.

### Changed — three description tightenings (commit `81adb9d`)

- `outsystems-design-to-app`: narrowed scope to VISUAL sources only (Figma / image / HTML). Removed "written description" trigger that overlapped with spec-driven-build's territory. Added explicit "For prose-only specs, use spec-driven-build" line.
- `outsystems-spec-driven-build`: claimed the TEXT-ONLY territory. Added "For Figma/image/HTML, use design-to-app" line up front. Mentions "build an app from this written description" as a trigger phrase now that design-to-app released it.
- `outsystems-mentor-copilot`: added two "When NOT to use" rows pointing at Paulo's companion skills — mentor-implementation (Studio-native pseudocode) and plan-to-mentor (now vendored).

### Added — `outsystems-plan-to-mentor` v1.0.0

- Coverage-reviews and patches an EXISTING saved OutSystems plan file against its source PRD before Mentor conversion. Required coverage matrix, versioned review artifacts, two-pass coverage loop.
- Plan generator is interchangeable — accepts `superpowers:writing-plans` output, `outsystems-spec-driven-build` output, or hand-written plans.
- Two delivery modes: paste-safe prompts (default, no MCP needed) or OutSystems MCP delivery via the companion `outsystems-mentor-implementation` skill.
- Vendored from `PauloACRibeiro/portable-agent-skills` (Paulo's repo remains the upstream source-of-truth). Frontmatter adapted to CONVENTIONS §3 (license, compatibility, allowed-tools, metadata.version + author). Routing Boundary expanded to align with `docs/TRIGGER-MAP.md`. Skipped: `agents/openai.yaml` (Codex-specific config) and `tests/` (Paulo-specific test framework).
- Files included: `SKILL.md`, `README.md`, 4 reference docs (coverage-review-prompt, delivery-modes, mentor-implementation-invocation, mentor-spec-guardrails), `scripts/check_plan_handoff.py`. Total: ~40 KB.

### Added — `outsystems-mentor-implementation` as a Complementary Tool (NOT vendored)

- Paulo's larger skill (~1 MB across ~80 reference files) is referenced in README's "Complementary tools" section pointing at his repo, NOT vendored into ours. Reasoning: (1) Paulo's repo is source-of-truth and he's actively maintaining it; vendoring would fork; (2) substantial knowledge artifact (229 KB pseudocode manifest, 81 KB UI pattern catalog, 75 KB Studio language elements, etc.) doesn't belong inline in our catalog; (3) it has prerequisites (`outsystems-tech-content` MCP server + `workspace-knowledge-cc`) that not every tester has.
- README's Complementary tools table documents the prerequisite gap.

### Catalog count

`10 core + 1 optional companion` → `11 core + 1 optional companion + 1 separate-repo companion`. README/SKILL-INDEX updated accordingly.

---

## 2026-06-19 — Gotcha-baking pass (Tier 2 deep integration)

Following the gotchas/ knowledge harvest from `claude-oml-tool` (earlier today), wired selected universal-engine-level traps into the actual Mentor prompts + risk classifications + identity discipline across four skills. Goal: turn passive "reference doc" knowledge into active "Mentor sees this rule at build time" enforcement.

### Changed — `outsystems-design-to-app/references/workflow.md`

The spec preamble that gets prepended to every Mentor batch now includes six engine-level HARD RULES with explicit cross-references to the corresponding gotcha docs:

- **R1** — Theme class collisions (5 reserved names + 6 collision patterns)
- **R2** — SVG icon color baking + `<i class="ph">` doesn't render in ODC SPA runtime
- **R3** — TableRecords need a seeded Source
- **R4** — Interactive widgets need `<div data-widget-slot>` slots, NOT `<a>` slots
- **R5** — Reconcile duplicate primary actions (chunk button + authored Button)
- **R6** — SPA section visibility — strip `display:none / .active` for per-screen chunks (except transient overlays)

Mentor now sees these rules verbatim on every batch (entities + screens + chrome). Each rule includes a "See gotchas/X.md" pointer for full context if Mentor needs deeper detail.

### Changed — `outsystems-spec-driven-build/scripts/build.py` (MENTOR_GUARDRAILS)

Extended the anti-failure guardrails block prepended to every Mentor prompt with three new universal-UI rules (the ones that apply to any Mentor-driven build, not just design-source):

- **Rule 8** — Reserved theme class names (the 5)
- **Rule 9** — SVG icon color baking + font-icon-doesn't-render
- **Rule 10** — TableRecords seeded Source requirement

(Existing rule 8 renumbered to 11.) Verified via `build-prompt` smoke test: rules 8/9/10 appear in the generated Mentor prompt.

### Changed — `outsystems-deploy-preview` SKILL.md

Added a "Post-publish failure modes" section under the risk classification table. When risk is `high` or `concerning`, the rendered preview should include a recommendations line pointing the user at the OS-APPS-40028 publish-validator-rejection taxonomy (in case the publish itself fails after promotion). Documentation-only; `build.py` doesn't need to know the taxonomy — it just routes the user to the right diagnostic doc if they hit the failure mode.

### Changed — `outsystems-change-planner` (local-only skill, NOT in this repo)

Added a Phase 2 Step 0 pre-flight: "identity continuity" check. Before opening a mentor session, confirm `APP_KEY` is the SAME asset key referenced in Phase 1's brief — i.e. we're modifying the existing app, not minting a new one via `app_create`. Spawning new shells per iteration is the anti-pattern documented in `gotchas/iterative-deployments.md` (cluttering tenant with abandoned revisions of `<AppName>_v1`, `<AppName>_v2`, …).

### Why this matters

Tier 1 (the gotchas/ import yesterday) was the passive layer — knowledge available if you go looking for it. Tier 2 (today) is the active layer — Mentor sees the rules at build time, the user sees the publish-validator taxonomy when their deploy gets risky, and the iteration skill enforces app-key continuity. The combined effect: traps that bit `claude-oml-tool`'s direct-OML approach no longer bite our Mentor-driven flow either.

### Attribution

All rules cite the corresponding gotcha doc (which in turn cites the `claude-oml-tool` `validated/` source with date + APP evidence).

---

## 2026-06-19 — `outsystems-design-to-app` — gotchas/ knowledge harvest

Imported 12 field-tested gotchas from `OutSystems/claude-oml-tool`'s `validated/` corpus (Hasan Derawan's team) into `outsystems-design-to-app/references/gotchas/`. With attribution to the source repo + APP-cited evidence.

These are engine-level traps that bite regardless of the build approach — Mentor-driven or direct OML mutation — so the knowledge transfers cleanly even though `claude-oml-tool` uses a different architecture (Model API DLLs vs. our Mentor-driven flow).

### Added — `outsystems-design-to-app/references/gotchas/` (12 new files)

**Theme + styling:**
- `theme-collisions.md` — Five reserved class names (main-content, sidebar, header, content, footer) that collide with OutSystemsUI's LayoutBlank theme, plus 6 other theme-collision anti-patterns (`<aside>` for sidebar, link colors without `!important`, ThemeGrid_ misuse, etc.)

**Icons:**
- `svg-icon-baking.md` — Why SVG icons go BLACK on dark backgrounds (`currentColor` resolves to black inside base64 background-image), plus the hard rule that `<i class="ph ph-X">` font-icons DON'T render in ODC's SPA runtime — use inline `<svg>` with baked colors
- `icon-coverage-checklist.md` — Per-build location checklist (sidebar nav, KPI corners, agenda markers, action chips, search shortcuts, buttons). Skipping any leaves the published surface feeling unfinished
- `icon-translation-figma.md` — Lucide → Phosphor translation table (30+ common icons) for Figma React sources

**SPA structure:**
- `spa-shell-fallback-fidelity.md` — Four shell-fidelity patterns the auto-transpiler doesn't handle: per-screen header title, source-matched table header colour, styled upload drop-zone (widget INSIDE, not adjacent), white icons on coloured tiles
- `spa-section-visibility.md` — Source HTML's `display:none / .active → display:block` JS toggle pattern doesn't run in ODC — sections render chrome-only with content invisible. Strip the visibility CSS when each section becomes its own screen (EXCEPT for transient overlays)

**Widgets — anti-patterns:**
- `widget-link-slot.md` — Grafting an interactive widget (Upload / Input / Form / Button) into an `<a>` anchor slot makes the rendered Link wrap the widget — clicks intercepted, file picker never opens. Use `<div data-widget-slot="slot">` instead
- `duplicate-buttons.md` — Source chunk's `<button>Sign In</button>` AND a separately-authored Button widget both target the same screen → two overlapping primary actions. Reconcile to one
- `tablerecords-seeding.md` — TableRecords with an unset Source renders "no records" even when structurally correct. Seed via Local Variable `List<Entity>` populated in OnInitialize, one ListAppend per source `<tr>` row

**Publish + iteration:**
- `publish-validator-rejections.md` — Constructs that pass model API Save() but fail ODC's publish validator (OS-APPS-40028). Missing Entities chunk, stale ReferersData.xml / VerifyCaches.xml, RadioGroup auto-create children, etc.
- `iterative-deployments.md` — Pinning `eSpace.Key` for stable URLs across iterations (vs spawning new apps every run). Maps to our chained spec-driven-build / change-planner workflow

**Index:**
- `INDEX.md` — table of contents grouped by theme / icons / SPA structure / widgets / publish

### Changed — `outsystems-design-to-app` SKILL.md

- Step 2 (knowledge load) — gotchas/ added to the "load on demand" list with reference to INDEX.md
- Anti-patterns section — new bullet pointing at the gotchas/ checklist for visual-source builds, framing it as the difference between "mostly works" and a polished published surface

### Attribution

All 12 gotcha files cite their source `validated/<file>.md` in `OutSystems/claude-oml-tool` with the validation date and APP-cited evidence where available. Patterns extracted in our voice (driving Mentor); verbatim C# / `plan.json` recipes intentionally omitted (those are OmlTool-specific).

---

## 2026-06-17 — `outsystems-mentor-polling-behavior` v1.3.0 (new skill — optional companion)

**Driver:** The default `pollAfterMs` hint (500ms) from the OutSystems MCP
server is designed for real-time UI progress bars, not LLM agents where
every poll response has a token cost. `mentor_get_run` emits verbose
intermediate event batches (10–50KB each) on every poll; at 500ms cadence
a typical 6-minute Mentor run produces 700+ responses flooding the model's
context before completion. A 30s cadence reduces this to ~12 polls with no
change to completion time.

### Added — `outsystems-mentor-polling-behavior` v1.3.0

**Three-mode skill:**

- **Mode 1 — Mentor invocation:** Enforces Tier 1/2/3 polling discipline,
  records per-poll telemetry silently. HTML dashboard is NOT auto-generated
  — telemetry accumulates and dashboard is rendered on demand only.
- **Mode 2 — Generate dashboard:** On-demand HTML render of all session data.
- **Mode 3 — Summary + recommendations:** Cross-session digest (Option A) and
  trend analysis with recommendations (Option B) — `run.py summary` outputs
  structured JSON, model interprets it.

**Operation tier model:**
- Tier 1 — Synchronous (`app_list`, `context_*`, `env_list` etc.): call once, no sleep.
- Tier 2 — Fast async (`publish_start`, `deploy_start`, `extlib_upload`,
  `test_setup_start`): 30s inline poll until terminal.
- Tier 3 — Long async / verbose (`mentor_get_run` only): 30s cadence, cursor
  discipline, terminal result only.

**Telemetry and dashboard:**
- Per-poll telemetry recorded to `poll-log.jsonl` (poll index, timestamp,
  status, event count, payload bytes) — no prompt content stored (privacy by design)
- Session path communicated via `.current-session` pointer file — eliminates
  all `$(...)` command substitutions from the polling loop
- `run.py finalize` writes only `endTime` + `status` — findings displayed
  inline in conversation, never stored
- HTML dashboard: `index.html` (Session List) + `sessions/<runId>/detail.html`
  (Detail Page), both self-contained, OutSystems dark theme, Inter + JetBrains
  Mono fonts matching tenant-architecture style
- Stat cards show poll reduction as % with raw numbers as subtitle:
  *"99% fewer polls — 12 vs 720 at 500ms"*
- Tier classification rendered as a proper table with Tool / Tier / Polling rule
- Collapsible "What is this skill?" panel on the dashboard with plain-English
  explanation

**`scripts/run.py` subcommands** (pure stdlib, Python 3.7+):
`init`, `update-run-id`, `show-session`, `show-config`, `record-poll`,
`finalize`, `summarize`, `summary`, `render`

**SFTDD test suite** (76 tests via `uv run pytest`):
9 use cases covering all subcommands, HTML rendering, feedback signal,
stats computation, and cross-session summary.

**Config** (`config.json`):
- `polling.tier3CadenceSecs` (default 30)
- `polling.tier2CadenceSecs` (default 30)
- `tierOverrides` — reclassify any tool without editing SKILL.md
- `feedback.thresholds.avgMentorDurationSecs` — single threshold for Tier
  Review Signal (avgPollCount removed as noisy proxy)
- `dashboard.staleSessionDays` — dims old sessions in the dashboard

### Honest framing

- Does NOT solve Mentor's context-verbosity problem — verbose events still
  land in context per poll. Reduces poll *count*, not event *verbosity*.
- Token count is a proxy (payload bytes ÷ 4), not a real billing figure.
- Byte savings are extrapolated (avg bytes per poll × polls saved), not measured.
- Optional skill — not a prerequisite for any other skill in the catalog.

---

## 2026-06-16 — Docs sync + `outsystems-custom-code` frontmatter polish

After `outsystems-design-to-app` (Swamy) and `outsystems-custom-code`
(Diogo) merged, swept the catalog docs to reflect the new 10-skill
state and brought custom-code's frontmatter up to CONVENTIONS §3
compliance.

### Changed — `outsystems-custom-code` (frontmatter polish, no version bump)

- Added full frontmatter per CONVENTIONS §3: `license: MIT`,
  `compatibility` (.NET 8 SDK / Docker / OutSystems MCP), `allowed-tools`
  (Bash, Read/Write/Edit, the `mcp__outsystems__extlib_*` toolset for
  deploy), `metadata.version: "1.0.0"`, `metadata.author: outsystems-r-and-d`.
- Expanded description from one sentence to a discoverable trigger
  block: covers what the skill is + 5 natural-language phrases users
  would actually say ("build a C# library for OutSystems", "create
  ODC external logic", "write custom code for ODC", etc.).
- No content changes — the body (SDK attributes, runtime constraints,
  testing, deploy) is Diogo's verbatim.

### Changed — `README.md`

- Skill count `8` → `10` everywhere.
- Skill table regrouped by primary use case (Explore / Build /
  Operate) matching `docs/SKILL-INDEX.md` taxonomy.
- New rows: `outsystems-design-to-app`, `outsystems-custom-code`.
- Repo-layout tree alphabetized and updated with both new directories.
- "Skill size" claim loosened — design-to-app ships ~30 reference
  files, custom-code is reference-only (no scripts/assets).
- "Some skills cost real money" callout updated to include
  `outsystems-design-to-app` as Mentor-driven (~$1–15 per build).

### Changed — `docs/SKILL-INDEX.md`

- Added `outsystems-custom-code` row to the Build section with
  framing that calls out its distinct shape ("extends ODC with native
  code, not Mentor-generated app surface").
- Quick-reference ASCII diagram extended with the custom-code Build row.
- Skill-count line `9 skills` → `10 skills`.
- Version list updated to current versions after this session's patches:
  `outsystems-tenant-architecture` v1.4.2, `outsystems-app-architecture`
  v1.3.2, `outsystems-dependency-impact` v1.2.2, `outsystems-spec-driven-build`
  v1.0.1 (post-T1-revert), `outsystems-custom-code` v1.0.0 (new).

---

## 2026-06-16 — `outsystems-design-to-app` v1.0.0 (new skill)

### Added — `outsystems-design-to-app` v1.0.0

Turns a design source (Figma URL, screenshot, HTML mockup, or written
brief) into a working OutSystems app via the OutSystems MCP / Mentor.
The skill bridges three things a vanilla LLM does poorly on its own:
**design extraction**, **OutSystems UI domain knowledge**, and
**Mentor invocation discipline**.

**Pipeline:**
- Extract design tokens + structure (Figma MCP / HTML / image / written
  brief)
- Compose a structured `spec.json` that maps every visual element to a
  real OutSystems UI block (no fake CSS-styled containers)
- Drive `mentor_start` in batches (entities → screens) with field-tested
  preambles and cursor poll discipline
- Publish the result

**OutSystems UI knowledge bundled:**
- `references/outsystems-ui/ui-reference.md` — cross-cutting reference
  (semantic widget hierarchy, anti-patterns, Quick lookup by requirement,
  Entities enums, Form widgets, Critical rules)
- `references/outsystems-ui/patterns/*` — per-category block reference
  (content, interaction, navigation, numbers, adaptive, utilities)
- `references/outsystems-ui/{layouts,styles-and-utilities,design-tokens,
  charts,maps}.md` — layout, styling, tokens, charts, maps
- `references/screen-guides/*` — 13 screen-archetype recipes + 5
  cross-cutting design-system / component-selection guides

**Assets:**
- `assets/enriched-blueprint.json` — canonical spec.json schema

## 2026-06-16 — UI quality prelude T1 — REVERTED on 2026-06-16

Initially shipped as `b847101` (`docs/UI-PRELUDE.md` + bundled prelude in
`outsystems-spec-driven-build` v1.0.2 / `outsystems-mentor-copilot` v1.1.2)
then reverted same day after `outsystems-design-to-app` (Swamy) merged.
The new skill provides a more comprehensive treatment of the same problem
(block-mapping gate + per-archetype guides + structured `spec.json`) —
T1's prose-style prelude was redundant once that was in place. Catalog
stays lean: 10 skills, no overlapping UI-quality layers.

Skill versions restored: `outsystems-spec-driven-build` v1.0.1,
`outsystems-mentor-copilot` v1.1.1. CHANGELOG entry preserved as
historical record.

---

## 2026-06-12 — Architecture skills perf-defense bundle

**Driver:** Demo Team Slack thread (2026-06-11/12). Sezen De Bruijn
reported `outsystems-tenant-architecture` taking ~20 min for ECG;
Sofia Pinho reported ~10 min on her tenant. My benchmark of ~2 min
on a 42-asset tenant is the BEST CASE and doesn't reflect real
production tenants. The skills' token budgets were over-optimistic
about the "harness auto-save handles everything" pattern.

**Top hypothesis** (no specifics from testers yet, ships defensively):
the model is violating the *"don't Read the harness-saved file"*
anti-pattern under specific conditions — pulling 50-150 KB of MCP
response data back into context on each turn, slowing every
subsequent turn nonlinearly. A clean run is ~3-5K tokens; a violating
run could balloon to 50-100K. Secondary suspect: unintentional skill
chaining ("show me the ECG" → tenant-architecture + app-architecture
× 100 apps).

### Changed — `outsystems-tenant-architecture` v1.4.2

- **Description** explicit about single-pass scope ("ONE tenant-level
  pass per invocation — does NOT loop into per-app deep dives"), demo-
  prep recommendation, and 2-5 min first-run / ~5s cached.
- **`AskUserQuestion`** added to `allowed-tools` for the new scope gate.
- **Token budget table** rewritten with honest three-band scaling
  (small / mid / large tenants), explicit call-out of the §8c
  mid-tenant trap, and the "leading-suspect" theory for the 10-20 min
  field reports.

### Added — `outsystems-tenant-architecture` v1.4.2

- **Step 0 — Scope guard.** Detects "tenant + per-app deep dives"
  requests and gates the chain via `AskUserQuestion` with explicit
  N × 10K token math. Defaults to tenant-only on ambiguity.
- **Step 0.5 — Demo prep tip.** Tells SAs to warm the cache before
  the demo and run the cached path live (~5s) instead of the
  first-time path (~2-5 min).
- **Anti-pattern: HARD STOP "Do NOT `Read` the harness-saved file".**
  Moved to top of anti-patterns with explicit token-cost math (280-asset
  tenant = 50 KB ≈ 12-15K tokens; 1000-asset = 150 KB ≈ 35-50K). For
  debugging, use Bash `head -c 1000 <path>` instead of Read.

### Changed — `outsystems-app-architecture` v1.3.2

- **Description** explicit about single-app scope ("ONE app per
  invocation — do NOT iterate over multiple apps in a single call").
- **`AskUserQuestion`** added to `allowed-tools`.

### Added — `outsystems-app-architecture` v1.3.2

- **Step 0 — Scope guard.** Three branches: one specific app
  (continue), multiple apps (sequential per-app, gate at N > 3),
  whole tenant (route to `outsystems-tenant-architecture`).
- **Anti-pattern: HARD STOP "Do NOT `Read` any `context_*` harness-
  saved file".** Per-call token-cost math for context_screens / etc.
- **Anti-pattern: "Don't iterate this skill over many apps in one go".**
  Same gating rationale as tenant-architecture; prefers tenant-arch
  for tenant-wide views.

### Deliberately NOT done

- **No live-test on a large tenant** (my dev tenant is 42 assets).
  Need a production-scale tenant + a few SAs willing to re-run with
  the v1.4.2 / v1.3.2 patch.
- **No diagnostic ask of Sezen/Sofia** (user explicitly chose "ship
  defensive fixes now without specifics"). Defer until a follow-up
  if these fixes don't move the needle.

---

## 2026-06-06 — `outsystems-dependency-impact` v1.2.2 (third field-test patch — live-test bundle)

**Driver:** live-test of v1.2.1 (2026-06-05, internal validation on
one26-legacymod tenant) surfaced 3 issues bundled into one v1.2.2 patch:

1. 🔴 **Schema drift** — `app_refs` now returns `schemaVersion: 2`
   shape `{producerAssetKey, producerAssetName, importedKind}` via
   `source: oml-fallback` instead of the legacy
   `{moduleKey, name, kind, revision}`. The skill was silently dropping
   every dep (its `build.py` only knew the legacy shape). Filed as
   **S14** in upstream-work.md for the MCP server team.
2. 🟡 **System-template scan waste** — Step 4 filtered by `assetType`
   only, so it scanned `Template_*`, `Screen Templates *`, and
   `OutSystems Sample Data` assets that deterministically fail
   `app_refs` ("System modules cannot be loaded with the Model API").
   ~9 wasted calls × ~3s = ~30s + 2-3K tokens per typical tenant.
3. 🟡 **ETA hardcoded** — the v1.2.1 pre-flight gate said
   "~150 consumer assets, 9-25 min" regardless of tenant size. For a
   20-asset tenant the real ETA is ~1-3 min — the bigger number felt
   misleading and arguably scared users off cheap scans.

### Changed — `outsystems-dependency-impact` v1.2.2

- **`build.py` reference-parsing** now accepts BOTH schemas (v1 + v2)
  seamlessly. Reference items can carry either `moduleKey` or
  `producerAssetKey`, either `name` or `producerAssetName`, either
  `kind` or `importedKind`. v2 (current) lacks per-reference `revision`,
  so `gap` is `None` for those — graceful degradation.
- **Step 0 no longer gates with `AskUserQuestion`** for reverse-dep
  queries. It just routes; the gate moves to Step 4.5 with accurate
  per-tenant numbers.
- **Description** reworded — "9-25 min" replaced with "duration
  proportional to consumer asset count (typical: 1-3 min for 20-asset
  tenant, 9-25 min for 150-asset tenant)".

### Added — `outsystems-dependency-impact` v1.2.2

- **Step 4 name-pattern filter** for `Template `, `Template_`,
  `template_`, `Screen Templates `, and exact-match
  `OutSystems Sample Data`. These deterministically fail `app_refs`;
  no point calling them. Live-test saved ~9 calls for the test tenant.
- **Step 4.5 — Pre-flight confirmation with actual count.** Computes
  ETA from `len(scan_list)` × empirical seconds-per-asset (3.5s
  healthy → 12s degraded) and token count (~0.55K per asset). Fires
  `AskUserQuestion` with real numbers before any `app_refs` call.
- **Step 5 dual-schema Write guidance** — model can Write whichever
  schema the API returned without field-mapping; `build.py` handles
  both.

### Deliberately NOT done

- **Schema-drift escalation** stays a recommendation to file with the
  MCP server team (S14 in upstream-work.md). Skill-side patch is
  defensive; the right long-term fix is the MCP server stabilizing
  on one schema OR documenting v2 as the official replacement for v1.

---

## 2026-06-02 — `outsystems-dependency-impact` v1.2.1 (second field-test patch)

**Driver:** field-test, João Leitão (follow-up after v1.2.0 was
released). Second report: "dependency analysis needs to scan every
consumer app in the tenant which takes a long long time." The
complaint is about the *fundamental* scan time, not the UX gaps that
v1.2.0 fixed.

**Root cause** (not in the skill): the upstream MCP `app_refs`
endpoint caps at 2 parallel calls (CONVENTIONS §7b, also S3 in our
upstream-work backlog). For a 150-asset tenant, the math is
`150/2 × ~5s = ~9 min minimum`, plus cool-down overhead and any
sequential-fallback time. The skill cannot accelerate this — only the
S3 upstream fix will.

### Changed — `outsystems-dependency-impact` v1.2.1

- **Description tightened** — wall-time range now stated as "9-25 min
  depending on upstream health" (was just "9-15 min"), so users
  aren't misled by the happy-path number.
- **Step 0 pre-flight question** — same honest 9-25 min range surfaced
  in the AskUserQuestion option description. Field signal: users who
  saw only "9-15 min" felt misled when the scan took longer.

### Added — `outsystems-dependency-impact` v1.2.1

- **"Why is this slow?" section** at the top of SKILL.md — explains
  the upstream 2-parallel cap, gives a wall-time table by upstream
  health (healthy / realistic / degraded), points at S3 as the fix
  path. Sets honest expectations BEFORE the scan starts.
- **Periodic progress reports (Step 5)** — every 10 batches, the model
  must emit a one-liner with `scanned/total`, `targets found`,
  `timeouts so far`, and a recomputed ETA. Removes the "silently
  stuck for 15 minutes" UX failure mode.

### Deliberately NOT done

- **Streaming/background scan mode** — too large a redesign for
  marginal UX gain; deferred indefinitely.
- **Cross-skill `app_refs` cache** — promising (reuse refs already
  fetched by `outsystems-app-architecture`) but design work; flagged
  as v1.3.0 candidate.

---

## 2026-06-01 — `outsystems-dependency-impact` v1.2.0 (field-test patch)

**Driver:** field-test, João Leitão. Skill was triggered for an
"analyze two apps" query, ran the full-tenant reverse scan (130
consumer assets), hit `app_refs` upstream timeouts on batches of 2,
and ran for 20+ minutes before the user could see what was happening.
The model also organically improvised "10 calls at once" mid-scan,
violating the documented 2-parallel cap.

### Changed — `outsystems-dependency-impact` v1.2.0

- **Description tightened** — explicit REVERSE-dependency framing.
  Dropped ambiguous triggers ("dependency tree", "dependency audit",
  "dependency impact") that attracted forward-dep questions. Upfront
  cost disclosure (80-100K tokens, 9-15 min) in the description so
  the harness can surface it to the user before triggering.
- **Description points at cheaper alternatives** for forward-dep
  questions (`outsystems-app-architecture` or direct `app_refs`).

### Added — `outsystems-dependency-impact` v1.2.0

- **Step 0 — Scope detection + pre-flight confirmation.** Three
  branches:
  - Forward-deps for 1 app → route to `outsystems-app-architecture`
    (stop)
  - Forward-deps for 2-3 apps → direct `app_refs` (stop)
  - Reverse-deps → continue, but first show ETA + ask confirmation
    via `AskUserQuestion` before any cost is incurred
- **Step 5 throttle contract codified** — replaced prose-style
  guidance with hard rules:
  - Start: batches of 2 + 5s cool-down
  - Downshift to sequential single calls after 3 consecutive batches
    with ≥1 timeout each — and stay there
  - Abort after 10 consecutive single-call timeouts (don't keep
    trying)
  - Explicitly forbidden: escalating above batches of 2 even if it
    "looks like it might work"
- **Step 5b — Resume from partial scan.** Before each `app_refs`
  call, check if `$CACHE/refs/<key>.json` already exists; if yes,
  skip. Makes the scan resumable across SKILL invocations after
  timeout-abort, ctrl-C, or MCP reconnect. No duplicate cost on
  re-runs.
- **`AskUserQuestion`** added to `allowed-tools`.

---

## 2026-05-31 — `outsystems-spec-driven-build` v1.0.0 (new skill)

**Driver:** field-test synthesis. The top theme across 49 tester reports
was cost-fear (Peter's $10 form, Donnie's burned Kiro credits,
Rodolfo's 29.6 M tokens). Donnie independently built an external
spec-driven pattern (github.com/donnieprakoso/mcp-outsystems-docs) that
he reports "didn't have any issues" with on real builds. Vasco's RFP
attempt failed at Mentor's known RBAC weakness. This skill productizes
the pattern + adds anti-failure guardrails.

### Added — `outsystems-spec-driven-build` v1.0.0

- **Three entry modes:**
  - Spec file — user brings their own `spec.md`, skill validates + drives
  - Interview — 12-question structured walk-through producing a valid spec
  - Clone example — start from `templates/example-spec.md` (TaskTracker), edit, fire
- **Spec validation** — `scripts/build.py validate-spec` enforces required
  sections (Overview / Roles / Data model / Screens+RBAC / Out-of-scope)
  and catches unfilled placeholders, invalid app-shell keys
- **Anti-failure guardrails baked into the Mentor prompt:**
  - Role-per-screen RBAC must be respected exactly (Vasco's failure mode)
  - OutSystemsUI applied to all screens (João's failure mode)
  - ODC terminology only — no "Service Studio" / "eSpace" (Inês's report)
  - Out-of-scope respected absolutely (over-build prevention)
  - Don't call `eSpace.AddDependency` — known broken (Peter's B2)
  - Exact attribute types from spec — no silent substitution
- **Build report renderer** — combines spec + Mentor summary + publish
  handoff + suggested next-skill chain (test-gen, architecture viz, etc.)
- **Honest scope:** greenfield only. Iteration on existing apps stays in
  `outsystems-mentor-copilot`.

### Token cost (estimate)
- Tight spec, simple app: $1–2 (vs ad-hoc $3–10 historically)
- Ambitious spec with RBAC + integrations: $2–5
- Re-running with same spec: ~$0.10 (session reuse)
- Re-rendering past build: ~$0.01

### Honest framing
This is the first prevention-shaped skill in the catalog. The other 7
respond to existing intent ("show me X"). This one constrains the next
step before it happens.

---

## 2026-05-30 — `outsystems-app-architecture` v1.3.1 + `outsystems-app-documentation` v1.3.1

**Driver:** field-test report #2 from Rui Madaleno on the same
`rmad employee directory` app. The skill summary claimed every screen
in the Common UI flow had role `RMadEmployeeDirectory` — but Studio
showed those screens as `Accessible by: Everyone` (anonymous). The
fabrication was confabulation: `context_screens` doesn't return any
per-screen authorization data, but the model output a Roles column
anyway by cross-producting the app's primary role name across the
screen list.

### Added
- Anti-pattern bullets in both `outsystems-app-architecture` and
  `outsystems-app-documentation` SKILL.md files explicitly forbidding
  per-screen role-assignment confabulation. Includes the field-test
  reference so future readers understand the why.
- New entry in `docs/CONVENTIONS.md` §7b documenting that
  `context_screens` does not surface authorization metadata —
  catalog-wide guardrail.

### Rationale
- Without auth to the MCP we can't yet confirm whether a richer
  `context_screens` response is available in some future schema
  version. Conservative path: forbid the confabulation now; expand
  the data capture later if/when we learn `context_screens` returns
  auth metadata we missed.
- This is a documentation/procedure patch only — no code changes.
  Patch-level version bump (1.3.0 → 1.3.1).

### Open follow-up
- Live verification attempted post-patch: MCP auth restored, but the
  `one26-legacymod` tenant has an empty Context Service (0 rows
  tenant-wide across `context_screens`, `context_actions`,
  `context_entities`). Unable to introspect `context_screens` shape
  here. Verification deferred until access to a populated tenant.
  Tracked as KNOWN-ISSUES #006.

---

## 2026-05-30 — `outsystems-app-architecture` v1.3.0 + `outsystems-app-documentation` v1.3.0

**Driver:** field-test report from Rui Madaleno on `rmad employee
directory`. The skill reported "no owned entities" when the app
clearly has a rich data model (Employee, Department, Project, etc.).
Diagnosis: those entities live in a referenced library module
(`EmployeeDirectory_DataModel`), so `context_entities` with
`owned_only: true` correctly returned empty — but the wording was
materially misleading.

### Changed
- `outsystems-app-architecture` procedure now calls `context_entities`
  with **`owned_only: false`** (unlike the other 5 context_* calls).
  `build.py` partitions the response into `entities` (owned by this
  app) vs `inheritedEntities` (from referenced libraries) and renders
  both.
- Compact-write whitelist for `entities-raw.json` extended to capture
  `isReferenced` and `producerAssetName` (so the source module is
  preserved end-to-end).
- Graph template (`assets/template.html`) adds a new "Entities
  (inherited)" sub-group in the Data layer, color #6EE7B7 (mint),
  with the source module surfaced in node tooltips.
- New `Inherited` category in the filter sidebar.
- `outsystems-app-documentation` Data section now renders inherited
  entities grouped by source module, with the wording: *"This app
  uses entities defined in referenced library modules: From
  `<ModuleName>` (N entities): ..."* — replaces the pre-v1.3
  *"No owned entities"* dead-end.
- Bundle data shape adds `inheritedEntities: [{k, n, desc, fromModule}]`.

### Cost impact
- `context_entities` with `owned_only: false` returns more rows for
  apps that inherit entities (~5–30 extra rows per referenced
  library). Net first-run token cost: +200–500 tokens. Empty-fetch
  case (no inherited entities) costs the same as before.
- Cached re-runs: unchanged (~1 K).

### Honest framing
- For apps that DO own their entities (most web apps), behavior is
  identical to v1.2 except for ~50 extra tokens spent fetching
  `owned_only: false`.
- For thin-UI apps (rmad pattern), output is now correct rather than
  misleading. This is the value delivery.
- v1.3 ships the entity fix; the second Rui report (hallucinated
  per-screen roles) is held for a separate patch — see KNOWN-ISSUES
  for the open investigation.

---

## 2026-05-29 — `outsystems-app-architecture` v1.2.0

**Driver:** week-1 field-test report. Tester noted that the rendered
architecture graph showed the agent node and the AI model connection
nodes, but **no edge connecting them** — making it impossible to tell
which model a given agent was using.

### Added
- `outsystems-app-architecture` now surfaces a **Dependencies layer**
  in the graph: AI model connections + library / extension references.
  Driven by the `app_refs` data source.
- New `--refs` flag on `outsystems-app-architecture/scripts/build.py`
  — accepts either the raw MCP `app_refs` response or the compact
  `outsystems-dependency-impact` cache form (identical shape).
- New `AIModel` and `Library` categories in the filter sidebar.
- Cross-skill cache reuse: if `outsystems-dependency-impact` has scanned
  the app within 24h, the deps are read from that cache for free (no
  extra MCP call).

### Changed
- Step 3 of the procedure became Step 3 + new Step 3.5 (refs
  resolution: cache → fresh small-app fallback → skip-with-note for
  large apps that would hit `app_refs` timeouts — see KNOWN-ISSUES #003).
- Built-in OutSystems modules (`(System)`, `OutSystemsUI`,
  `OutSystemsCharts`, `OutSystemsMaps`, `OutSystemsSampleData`,
  `OutSystemsSecurity`, `OutSystemsPipelines`,
  `OutSystemsServerlessAddon`) are filtered out of the deps layer as
  noise.

### Token cost
- Cross-skill cache hit: **+0 tokens, +0 MCP calls.**
- Fresh small-app `app_refs` call: **+~500 tokens, +1 MCP call.**
- Large app, deps layer skipped: **+0 tokens**, with a note in the
  report.

---

## 2026-05-25 — Catalog v0.5 (polish pass)

### Changed
- All 7 skills bumped to consistent `1.X.1` patch level.
- SKILL.md bodies tightened: duplicated "core trick" / harness-disk
  explanations hoisted into `docs/CONVENTIONS.md` §8.1.
- Shared anti-patterns (`Don't use jq`, `Don't paginate
  prophylactically`, etc.) referenced from CONVENTIONS rather than
  restated per skill.
- Per-skill Prerequisites collapsed to a one-line reference to
  CONVENTIONS §4b ("Standard Prerequisites").
- Common troubleshooting entries (MCP disconnect, auth expiry,
  missing `python3`) moved to CONVENTIONS §7c.

### Added
- CONVENTIONS §4b: shared prerequisites.
- CONVENTIONS §7c: common troubleshooting.
- `outsystems-deploy-preview`: cross-skill `env_list` cache at
  `~/.claude/cache/outsystems-tenant-envs/<tenant-id>.json`, 24h TTL.

### Cost impact
- Net catalog reduction: ~60 lines across 7 SKILL.md files (~3.9%).
- Per-invocation token cost on cached runs drops slightly because
  the duplicated prose is gone.

---

## 2026-05-25 — Catalog v0.4 (structural polish pass)

### Changed
- Dropped the duplicated "## The core trick — keep large data off the
  model's tokens" prose from 4 skills (it lived in `outsystems-tenant-architecture`,
  `outsystems-app-architecture`, `outsystems-ai-agent-landscape`, and
  was implicit in `outsystems-dependency-impact`). Now referenced
  from CONVENTIONS §8.
- Token budget tables across all skills now report empirical numbers
  from live-test runs, not paper estimates.

---

## 2026-05-24 — Catalog v0.3 (initial 7 skills)

### Added
- `outsystems-tenant-architecture` v1.0 — tenant-wide HTML graph
- `outsystems-app-architecture` v1.0 — single-app HTML graph
- `outsystems-app-documentation` v1.0 — Markdown docs renderer
- `outsystems-ai-agent-landscape` v1.0 — AI agents + connections dashboard
- `outsystems-dependency-impact` v1.0 — reverse-dependency explorer
- `outsystems-deploy-preview` v1.0 — promotion risk preview
- `outsystems-mentor-copilot` v1.0 — curated Mentor task library

### Documented
- `docs/CONVENTIONS.md` — shared rules across the catalog
- `docs/KNOWN-ISSUES.md` — 4 MCP-layer bugs found during build, each
  with a reproducer and the skill-side workaround.
