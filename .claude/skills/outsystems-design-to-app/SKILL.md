---
name: outsystems-design-to-app
description: Drive ODC Mentor to bootstrap an OutSystems app from a VISUAL design source — Figma URL, screenshot/image, or HTML mockup. EXPERIMENTAL — Mentor is officially positioned for in-flow edits to existing apps; using it for greenfield builds from a design is a pattern this skill layers on top, and output fidelity varies. Treat results as draft scaffolds for human review and iteration, NOT ship-ready apps. Extracts design tokens + structure, composes a structured spec.json that maps every visual element to a real OutSystems UI block (no fake CSS-styled containers), then drives mentor_start in batches (entities → screens) and publishes the result. Use ONLY when the user provides a VISUAL artifact (Figma URL, image, HTML file). For prose-only specs or written briefs with NO design source, use `outsystems-spec-driven-build` instead. Use when the user asks to "build this design as an OutSystems app", "implement this Figma in OutSystems", "design to model", "design to app", "generate a screen from this mockup", "build this screen", or provides a Figma URL / image path / HTML file and wants it turned into a live OutSystems app.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. Mentor must be enabled on the tenant. For Figma sources, the Figma MCP server must also be connected.
allowed-tools: AskUserQuestion Bash Read Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_create mcp__outsystems__env_list mcp__outsystems__env_app mcp__outsystems__context_screens mcp__outsystems__context_entities mcp__outsystems__context_actions mcp__outsystems__context_themes mcp__outsystems__mentor_start mcp__outsystems__mentor_get_run mcp__outsystems__mentor_cancel mcp__outsystems__publish_start mcp__outsystems__publish_status mcp__outsystems__publish_logs mcp__plugin_figma_figma__get_screenshot mcp__plugin_figma_figma__get_variable_defs mcp__plugin_figma_figma__get_design_context
metadata:
  version: "1.1.0"
  author: outsystems-r-and-d
---

# OutSystems Design-to-App

Turn a design source (Figma, screenshot, HTML mockup, or written brief) into a working OutSystems app via the OutSystems MCP / Mentor. The skill bridges three things a vanilla LLM does poorly on its own: **design extraction**, **OutSystems UI domain knowledge**, and **Mentor invocation discipline**.

**Why this exists:** field testing showed that LLMs given a Figma URL routinely emit `Container + CustomStyle` walls that *look* right in screenshots but render as accessibility-blind, theme-fragile fake UI. This skill codifies a 4-part spec format and a mandatory block-mapping gate that forces every visual element through a real OutSystems UI block — then drives Mentor in tight batches so the build doesn't spin on under-specified requirements.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b — **plus** the following:
- **Mentor enabled on the tenant** (this skill calls `mentor_start`).
- **Figma MCP server connected** if the design source is a Figma URL (`mcp__plugin_figma_figma__*` tools). For HTML / image / text sources, the Figma MCP is not required.
- An empty target app shell in the OutSystems environment. The skill mints one via `app_create` if the user has none. **Do not** use `Template_*` / `template_*` / `OutSystems Sample Data` as the shell — Mentor's Model API rejects System modules.

## When NOT to use

- **Just running Mentor with a free-form prompt** (no design source, no spec discipline needed) → call `mentor_start` directly.
- **Building from a structured written spec** (no design source) → use `outsystems-spec-driven-build` — it specializes in spec validation + interview + template flow.
- **Adding features to an existing app** → use `outsystems-mentor-copilot`'s `add-feature` task; it preserves more session context.
- **Auditing / reviewing an existing app** → use `outsystems-mentor-copilot`'s `quality-review` / `security-review` / `accessibility-review` tasks.

## The core trick — keep large data off the model's tokens

Three big payloads in this pipeline can each exceed 50 KB:
1. **Figma `get_design_context` XML** for complex screens
2. **The composed `spec.json`** (15–80 KB)
3. **Mentor's terminal `mentor_get_run` event** (50–500 KB — Mentor's OML introspection)

For each, follow the harness disk auto-save pattern: on Claude Code the harness auto-saves oversized MCP results to disk and injects only the path, while a harness without that auto-save (Codex) gets the payload inline — so write it out yourself:
- If the tool result is inline and large, save it to `$CACHE/<name>.json` and re-read only specific paths.
- If the harness auto-spills to disk (saved-to-file notice), `cp` to `$CACHE/` — **don't read the spilled file into context.**
- Pass paths, not contents, to the next pipeline step.

```
APP_NAME=<human name>
CACHE=~/.claude/cache/outsystems-design-to-app/<APP_NAME>/
SKILL=<this skill's directory>
mkdir -p "$CACHE"
```

## Procedure

The full pipeline lives in `references/workflow.md`. The MCP Mentor flow (cursor poll, session-token handling) lives in `references/mcp-flow.md`. The summary below is what you need to keep in context.

### Step 1 — Identify the design source + the target app

Ask via `AskUserQuestion`:
1. **Design source** (required unless pre-built spec provided) — Figma URL, web URL, image path, HTML file, or written brief
2. **App name** (required) — target app in the OutSystems environment
3. **App context** (optional) — path to a `context.md` describing the existing app state. The spec should reference existing entities/themes/blocks by name, not recreate them.
4. **Pre-built spec** (optional) — skip to Step 4 if the user has already composed `spec.json`

App discovery:
- `mcp__outsystems__app_list { search: "<app-name>" }` → if found, capture `app_key`
- If not found → `mcp__outsystems__app_create { name: "<app-name>" }` to mint a fresh shell

### Step 2 — Load the OutSystems UI knowledge + start design extraction (in parallel)

Load skills AND start extraction in **the same message** — they're independent and the parallelism shaves real wall-clock. See `references/workflow.md` for the exact tool-call manifest. Default load set:

```
references/outsystems-ui/ui-reference.md        # OS UI widget reference: semantic hierarchy, anti-patterns, polish gates, Entities enums, Quick lookup
references/outsystems-ui/layouts.md        # LayoutSideMenu / LayoutTopMenu / LayoutBlank (delete-default gate)
references/outsystems-ui/styles-and-utilities.md  # utility classes + theme CSS variable overrides
references/outsystems-ui/patterns/{adaptive,navigation,content,numbers}.md
```

Load on demand (only when the design contains the matching element):

- **Charts** → `references/outsystems-ui/charts.md`
- **Maps** → `references/outsystems-ui/maps.md`
- **Carousel / Sidebar / DatePicker / Dropdown** → `references/outsystems-ui/patterns/interaction.md`
- **AlignCenter / Separator / gestures** → `references/outsystems-ui/patterns/utilities.md`
- **Screen archetype** → `references/screen-guides/{dashboard,list-table,detail-view,edit-form,master-detail,gallery-grid,kanban,timeline,calendar,wizard,map-view,inbox-notifications,settings}.md`
- **Cross-cutting implementation guides** (theme tokens + brand recolor, picking the right block, empty/loading/error states, reusable blocks, Reactive Web vs Phone App differences) → `references/screen-guides/{design-system,component-selection,states-and-feedback,reusable-blocks,app-type-styling}.md`
- **Design tokens** → `references/outsystems-ui/design-tokens.md`
- **Field-tested gotchas** (engine-level traps + anti-patterns that bite regardless of build approach — SVG icon baking, theme class collisions, SPA visibility toggles, TableRecords seeding, etc.) → `references/gotchas/INDEX.md` and the individual gotcha files. See the INDEX for the full catalog; load each on demand when the source contains the matching pattern. Sourced with attribution from `OutSystems/claude-oml-tool`'s `validated/` corpus

### Step 3 — Compose `spec.json` (the heart of the skill)

This step has FOUR sub-steps. **Do not skip ahead** — each produces output the next depends on.

#### Step 3.0 — Layout + structural skeleton gates (MANDATORY upstream of block mapping)

Two pre-conditions to enforce in the spec before the block-mapping pass:

- **Pick the right Layout block** (`LayoutSideMenu`, `LayoutTopMenu`, or `LayoutBlank`) based on the screen's navigation pattern. **Do not default to `LayoutBlank`** — see `layouts.md`.
- **Delete the default `LayoutTopMenu`** that `CreateScreen` ships with before adding your chosen Layout. Skipping this is the #1 cause of "two layouts at the screen root" regressions — see the inspect-delete-add code pattern in `layouts.md`.
- **Sketch the structural skeleton** — answer two questions for each Layout placeholder: *what is the column grid?* and *what are the card surfaces?* The output is a tree of `Columns*` and `Card` family blocks with NO `Container` nodes. Then commit a **block inventory** ("this region → that block") for every visual region.

Without these gates, design pressure pushes the agent into "Container + custom CSS class" mode regardless of how good the block mapping is.

#### Step 3a — Block mapping pass (MANDATORY)

Before writing any spec JSON, produce a **block mapping table** that lists every layout element from the visual inventory and resolves it to either an OutSystems UI block or custom CSS. **Print this table to the user** before proceeding.

```
BLOCK MAPPING:
  KPI 5-column grid         → Columns5 (patterns/adaptive.md)
  Customer card grid        → Gallery RowItemsDesktop=3 (patterns/adaptive.md)
  Pipeline 5-stage strip    → Columns5 (patterns/adaptive.md)
  Balance progress bar      → ProgressBar (patterns/numbers.md)
  Digital adoption ring     → ProgressCircle (patterns/numbers.md)
  Bottom 2-column row       → Columns2 (patterns/adaptive.md)
  Customer card surface     → custom CSS (card sub-layout, no OS block equivalent)
  Segment filter pills      → custom CSS (no OS "pill bar" block — styled ILinks)
  Risk chip                 → custom CSS (inline badge variant)
```

**Reject rules** — if any of these appear as "custom CSS", the mapping is wrong:

❌ **NEVER spec custom CSS flex/grid for screen-level or section-level layout.** Any region with 2+ children visually laid side-by-side or in a grid MUST use a real OS UI Adaptive block (`Columns2`–`Columns6`, `ColumnsMediumLeft`, `ColumnsMediumRight`, `ColumnsSmallLeft`, `ColumnsSmallRight`, `Gallery`, `MasterDetail`, `DisplayOnDevice`). **If the spec would emit `display-flex`, `display-grid`, `flex:`, `flex-1`, `flex-direction-row`, `grid-template-columns`, or `repeat(N, 1fr)` as a layout class in `outsystems_hints.css_classes` — STOP. Re-spec as one of the Adaptive blocks.** See `references/outsystems-ui/patterns/adaptive.md`.

> The **one legitimate use** of `display-flex` in `css_classes` is for **inline alignment INSIDE a single block placeholder** — e.g. icon + text inside `CardItem.Left`, or "title left, action right" inside a single `Card.Content`. Never for screen-level or section-level layout where the children are independent visual blocks.

Plus the rest:

- N equal columns (2–6) → always `ColumnsN` block
- Repeating card/item grid → always `Gallery` block
- Horizontal track + fill bar → always `ProgressBar` block
- Circular/radial progress → always `ProgressCircle` block
- Tab header + content switching → always `Tabs` block
- Card-shaped surface → `Card` / `CardItem` / `CardSectioned` block
- Inline chip / numeric pill → `Tag` / `Badge` block

**Source-name → block (non-negotiable):** if a Figma frame / layer is named `Carousel` / `Carrousel` / `Slider` → `Carousel` block. **Do NOT** substitute `Columns3` because the screenshot shows all 3 cards side-by-side. Same for `Gallery`, `Tabs`, `Wizard`, `Accordion`, `Sidebar`, `Stepper`. Look up the block's args / placeholders in `outsystems-ui/ui-reference.md` (Quick lookup) and the matching `outsystems-ui/patterns/*.md` before writing the spec section.

#### Step 3b — Write `spec.json` sections using the block mapping

Every section's `description` and `outsystems_hints.block` MUST reference the blocks resolved in Step 3a.

**4-part description format (CRITICAL)** — every `main_content[].description` MUST have four labeled parts:

- **VISUAL LAYOUT** — Container/widget tree, every Container with exact `Style` values, child nesting, alignment as CSS class names
- **DATA FLOW** — per-widget data descriptions in entity/attribute terms. For EVERY Expression that shows data, state what entity/attribute it comes from. Include derivation formulas and formatting rules. **Do NOT prescribe aggregate names, screen action names, or local variable names.**
  - **Anti-pattern**: if DATA FLOW is 2-3 sentences while VISUAL LAYOUT is 30+ lines, the agent WILL hardcode static text.
- **FUNCTIONAL BEHAVIOR** — what the section does:
  - Data-driven: *"Display only — all values are live from entity data, loaded on page entry."*
  - Interactive: full behavior in user terms (*"Clicking a pill filters the list to status = clicked pill. Active pill gets BLACK background. Other pills go neutral-3 background."*)
  - Navigation: target screen and context passed
  - Static: *"Static content — no data binding or interaction."*
- **PRESENTATION ORDER** — explicit sequence when elements appear in order

**Composition rules:**
- `outsystems_hints` is a **lean index** (block name + CSS class list) — NOT a duplicate of description
- **`outsystems_hints.block` must be a bare OS UI block name** (e.g. `"Columns3"`, `"Gallery"`, `"Card"`, `"Counter"`, `"Tabs"`) — NOT a prose sentence like `"Container widget with two children, the LEFT for filter list, RIGHT for Pagination"`. Mentor reads this value as a block-name identifier. If the section needs prose to explain composition, that prose goes in `description`, NOT in `outsystems_hints.block`.
- **For any region with 2+ children laid side-by-side or in a grid**, the block MUST be one of: `Columns2` / `Columns3` / `Columns4` / `Columns5` / `Columns6` / `ColumnsMediumLeft` / `ColumnsMediumRight` / `ColumnsSmallLeft` / `ColumnsSmallRight` / `Gallery` / `MasterDetail` / `DisplayOnDevice`. NEVER `Container` with `display-flex` / `grid-template-columns` css_classes for layout.
- When app context exists: reference existing entities/classes/blocks **by name**, don't recreate
- Every hex color, pixel size, font weight must come from the **extracted design** (no generalizing — `bg-[#edf0ed]` → `#EDF0ED`, not `#FFFFFF`)
- Every clickable element needs an `action` describing full behavior (not just "what it does" but "what happens to the data and UI")
- Every `main_content` entry needs `margin_bottom`
- **Figma extracts Tailwind → spec uses OutSystems**: read hex / px / direction from Tailwind classes during extraction, but write OS UI CSS variables and classes in the spec. Never write Tailwind class names into `outsystems_hints.css_classes`.

#### Step 3c — Inline verification (reject if mapping is contradicted)

Before saving `spec.json`, scan `design_system.new_classes` for any CSS that reimplements a block from Step 3a (`grid-template-columns: repeat(N, 1fr)` → use `ColumnsN`; track + fill divs → use `ProgressBar`; SVG ring → use `ProgressCircle`; styled tab-strip → use `Tabs`). If any leak, fix the section to reference the block and remove the class. Also verify:
- Every visible region has a matching `app_chrome` entry or `main_content` section
- DATA FLOW Expression count matches VISUAL LAYOUT Expression count (parity gate)
- Every section has FUNCTIONAL BEHAVIOR
- Every clickable element has an `action`
- Colors/sizes/border-radius match extraction, not generalized
- **Source-name → block check**: walk every named frame in the extracted metadata — `Carousel` / `Gallery` / `Tabs` / `Wizard` / `Accordion` / `Sidebar` / `Stepper` → confirm the corresponding spec section uses the matching block, not a `Columns` substitute
- **Block-name shape check:** every `outsystems_hints.block` value is a bare block name (e.g. `"Columns3"`, `"Gallery"`, `"Card"`) — not a prose sentence. If any section's block field contains a multi-word sentence ("Container widget with two children...", "The outer wrapper is..."), rewrite as a bare block name and move the prose to `description`.
- **Layout-block reject scan (CRITICAL):** for every section in the spec, if `outsystems_hints.css_classes` contains any of `display-flex`, `display-grid`, `flex:`, `flex-1`, `flex-direction-row`, `grid-template-columns`, `repeat(N,` AND the section describes 2+ visually independent children laid side-by-side or in a grid → **REJECT and rewrite** using `Columns2`–`Columns6` / `Gallery` / `MasterDetail`. The Adaptive blocks own multi-child layout; custom CSS flex/grid for layout is forbidden. (The one exception: inline alignment INSIDE a single placeholder — icon+text in `CardItem.Left`, title-left+action-right inside a single `Card.Content` — that's fine because the children belong to the same conceptual element.)

Save to `$CACHE/spec.json`.

#### Step 3d — Polish-checklist acceptance items (MANDATORY in the spec)

A "valid" spec with no polish reads as a wireframe. Bake these polish gates into the spec's `acceptance_checklist` so Mentor enforces them during the build, not just at review time:

- Default children stripped from each block (Tabs / Carousel / Accordion / etc. ship with placeholder children)
- Typography hierarchy applied (`h1` for screen title, `h2` for section headings, `h3` for card titles, `strong` for inline emphasis)
- Brand color used sparingly (2–3 deliberate uses per screen, on the most important affordances)
- Section spacing via OS UI utility classes (`margin-top-xl`, `margin-bottom-l`), NOT custom CSS
- Realistic placeholder content (real names, masked PANs, exact currency counts — not "User 1" / "Product 1" / "TBD")
- A clear focal point (don't let everything have the same visual weight)
- Section headings as `AdvancedHtml Tag="h2"`, never plain `Text` or styled `Container`
- Final "VERIFICATION GATE" acceptance item instructing Mentor to read the app state and verify every preceding checklist item before declaring done

### Step 4 — Confirm with the user before firing Mentor

Mentor calls are expensive ($1–$5 typical for a greenfield build). Always show the user the block-mapping table + the spec summary (entity / screen counts, sizes) and ask via `AskUserQuestion` for explicit go/no-go.

> Claude Code exposes this confirmation as the `AskUserQuestion` tool. On a harness without it (Codex), ask the same question inline and wait for an explicit answer before continuing. The gate is the confirmation, not the tool.

### Step 5 — Drive Mentor in batches (MCP)

See `references/mcp-flow.md` for the full cursor poll loop, session-token handling, and error categories.

**Batch strategy:**
1. **Entities + roles** → first batch
2. **Screens + theme CSS** → second batch (resume same session with `mentor_session_token` from batch 1)

**Spec preamble** (prepend verbatim to every batch prompt):
```
Implement the following spec COMPLETELY. Do NOT stop until every item in the
acceptance_checklist is satisfied. After all code executions, verify each
acceptance_checklist item by reading the app state — if any item fails, fix it
before finishing. Here is the spec:
```

### Step 6 — Publish

After all batches succeed:
```
mcp__outsystems__env_list {}
mcp__outsystems__publish_start { mentor_session_id, mentor_session_token, env_key }
# Poll publish_status until Completed
mcp__outsystems__env_app { env_key, application_key }
# Render `url` as a markdown link to the user
```

**Publish is mandatory** — session changes auto-GC after 30 minutes idle.

### Step 7 — Report to the user (3–5 lines)

- Run ID + cache path
- App name + `app_key`
- Entity / screen counts (from the spec)
- Mentor cost estimate (poll count × $0.10 rough)
- Runtime URL (markdown link)
- *"Resume the Mentor session with the newest `mentor_session_token` for refinements. Or chain into `outsystems-mentor-copilot` for follow-up audits."*

## Data shape contract

The `spec.json` schema lives in `assets/enriched-blueprint.json`. Top-level keys:

- `name`, `description`, `primary_color`
- `app_chrome` — sidebar nav groups + header content, defined once, shared across all authenticated screens. Login / LayoutBlank screens set `layout_override` and skip `app_chrome`.
- `blocks` — reusable Web Blocks for patterns used on **multiple screens**. Single-screen components live inline in `main_content`, not here.
- `design_system` — colors, typography, spacing, radius, shadows, visual_rules, css_architecture, new_classes (theme extensions)
- `entities` — only if NEW entities are needed (skip when App context provided)
- `screens[]` — each with `title`, `subtitle`, `template` (archetype), `main_content[]`, optional `popups[]`
- `icon_mapping`, `roles`, `acceptance_checklist`

Section types in `main_content[]`:
- Standalone section: `{ id, name, margin_bottom, description (4-part), outsystems_hints, verify }`
- Group: `{ type: "group", columns, columns_config, margin_bottom, items: [...] }` for side-by-side sections (e.g., KPIs in Columns3, Activity+Storage in ColumnsMediumLeft)

## Cache rules

- Location: `~/.claude/cache/outsystems-design-to-app/<APP_NAME>/`
- TTL: **none** — design-to-app builds are user-initiated, the user owns retention.
- Contents: `spec.json`, `extraction.md` (Figma / HTML / image notes), `mentor-batch-<N>.json` (terminal responses), `publish-log.json`, `timing.log`.
- Re-running with the same spec: skip Step 3, go straight to Step 5.

> The cache path stays at `~/.claude/cache/outsystems-design-to-app/<APP_NAME>/` on **every** harness — it is a shared cross-agent cache, not a Claude-only location. The `~/.claude/` prefix is a stable path, not a Claude Code dependency.

## Token budget

| Scenario | Mechanism | Total |
|---|---|---|
| Figma → small app (3 entities, 5 screens) | extract + spec + 2 batches + publish | **~80–150K** ($3–$6 on Opus 4.7) |
| Figma → ambitious (10+ entities, RBAC, charts) | extract + spec + 3 batches + publish | **~200–400K** ($8–$15) |
| Pre-built spec → app | skip Stage 1; 2 batches + publish | **~50–100K** |
| Re-running with the same spec | spec from cache + Mentor session reuse | **~30–60K** |
| Refinement turn after build | resume session + small prompt | **~10–20K** |

Empirically: testers using the block-mapping gate report 40–60% fewer Mentor retry passes than ad-hoc design-to-Mentor workflows. The savings come from Mentor not building fake `Container`+CSS UI that has to be rebuilt later.

## Troubleshooting

### Mentor errors
| Category | Action |
|---|---|
| `AuthError` | Call `mcp__outsystems__auth_status`; if expired, surface re-auth; retry ONCE |
| `ValidationError` | Fix prompt/spec, retry |
| `UpstreamError` | Transient — wait and retry once |
| `InternalError` | Report to user, don't retry |

### Common spec issues
| Symptom | Cause | Fix |
|---|---|---|
| Agent builds static shell with hardcoded text | DATA FLOW is too thin | Add per-widget data descriptions matching VISUAL LAYOUT detail |
| Agent skips data bindings | Missing FUNCTIONAL BEHAVIOR | Add "Display only — live from entity data" or interaction description |
| Gallery shows one column | CSS grid + List widget | Use `Gallery` block instead |
| ProgressBar / Counter rendered as raw div | Description says "Container with height 8px" | Name the OS block in BOTH `description` AND `outsystems_hints.block` |
| Agent prescribes aggregate names | DATA FLOW uses implementation terms | Describe in entity/attribute terms only |
| Cards Carousel rendered as Columns3 | Source-name → block check skipped | Re-spec the region as `Carousel` block |
| Chrome (search / theme toggle / notification badge) missing after publish | Chrome edits buried in screens batch | Run a dedicated chrome batch BEFORE the screens batch, with its own acceptance checklist |

### Figma extraction
- Root `get_design_context` returns metadata XML for complex screens — parse child node IDs and batch `get_design_context` on children in **pairs of 2** (4+ concurrent calls cause timeouts).
- If `get_variable_defs` returns empty, extract colors from the design-context code.
- Skip decorative nodes (vectors, masks, lines < 50px). Filter to frames > 100×50.

## Harness notes

- **Claude Code** auto-saves any MCP result larger than ~25 KB to disk and injects only the file path into context. All three big payloads in this pipeline — Figma `get_design_context` XML, the composed `spec.json`, and Mentor's 50–500 KB terminal event — routinely cross that threshold, so on Claude Code they stay out of the model's context.
- **Codex** has no such auto-save: the full MCP result is injected inline. A greenfield design-to-app build therefore costs materially more on Codex's first pass — every large Figma extract and `mentor_get_run` payload lands in context instead of spilling to disk. The token-budget table above reflects Claude Code; add the inline payload volume for a Codex estimate.
- On a harness without auto-save, write each large result to `$CACHE/` yourself and re-read only the paths you need, instead of relying on the harness spill.
- Composing `spec.json` (Step 3 — the block-mapping and inline-verification passes) makes zero MCP calls: it reads the extracted design locally, so that stage costs the same on both harnesses. The divergence is entirely in the MCP-payload steps (Figma extraction, Mentor polling).

## Anti-patterns — do NOT do these

Shared rules apply (CONVENTIONS §8.4). Skill-specific:

- **Don't skip the block-mapping pass (Step 3a).** It's the single biggest source of fake UI when omitted.
- **Don't write Tailwind class names in the spec's `outsystems_hints.css_classes`.** Figma extracts Tailwind; the spec uses OutSystems CSS variables and utility classes.
- **Don't generalize extracted hex codes** (`#EDF0ED` → `#FFFFFF`). If cards use `#EDF0ED` but the page uses `#FFFFFF`, those are DIFFERENT tokens.
- **Don't describe block primitives as raw HTML/SVG in `description`.** A ProgressBar with `description: "Container with height 8px"` makes the agent build a div even when `outsystems_hints.block: ProgressBar`.
- **Don't fire Mentor without user confirmation (Step 4).** A $5 call shouldn't happen on assumption.
- **Don't skip the spec preamble.** It's a field-tested instruction that prevents Mentor from stopping mid-build or skipping acceptance items.
- **Don't auto-publish to Prod.** Publish goes to whatever `env_key` the user selects from `env_list` — surface options, don't pick for them.
- **Don't use a System-module template app as the shell** — `Template_*` / `template_*` / `OutSystems Sample Data` are rejected by Mentor's Model API. Use `app_create` instead.
- **Don't load all reference docs at once.** Start with the default load set (Step 2), then load on demand based on what the design contains.
- **Don't skip the `references/gotchas/` checklist for visual-source builds.** Twelve specific engine-level traps (SVG icon baking, theme class collisions, SPA visibility toggles, TableRecords empty Source, duplicate primary actions, etc.) are documented in `references/gotchas/INDEX.md`. Each maps a specific source pattern → the fix. Field-tested against real app builds; ignoring them is the difference between a polished published surface and a "mostly works but icons are black and tables are empty" outcome.

## Related skills

- **`outsystems-spec-driven-build`** — when there's no design source, just a structured spec. Same Mentor invocation pattern, different upstream.
- **`outsystems-mentor-copilot`** — chain after a successful build for `test-generation`, `accessibility-review`, `add-feature`, etc.
- **`outsystems-app-architecture`** — visualize what was built (interactive HTML graph of screens / actions / entities).
- **`outsystems-app-documentation`** — generate Markdown docs for the new app.
- **`outsystems-deploy-preview`** — check the build before promoting to Test / Prod.

Workflow: design-to-app → mentor-copilot (test-generation + accessibility) → app-architecture (visualize) → deploy-preview (gate to Test) → publish.
