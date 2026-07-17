# Design-to-App Workflow

End-to-end pipeline for generating an OutSystems app from a design source via the OutSystems MCP / Mentor. Follows the flow described in `SKILL.md` — read it first for spec format rules, composition guidelines, and Mentor interaction patterns.

## Load Skills + Start Extraction (in parallel)

Launch ALL of these tool calls together in a single message:

```
Parallel group A (design extraction — start immediately):
  get_screenshot(nodeId)          # Figma
  get_variable_defs(nodeId)       # Figma
  get_design_context(nodeId)      # Figma
  # OR: Read the HTML/image file directly for non-Figma sources

Parallel group B (skill loading — runs at the same time):
  references/outsystems-ui/ui-reference.md              # OS UI widget reference (semantic hierarchy, anti-patterns, polish gates, Quick lookup)
  references/outsystems-ui/layouts.md              # Layout block + delete-default gate
  references/outsystems-ui/styles-and-utilities.md # utility classes + theme variables
  references/outsystems-ui/patterns/adaptive.md
  references/outsystems-ui/patterns/navigation.md
  references/outsystems-ui/patterns/content.md
  references/outsystems-ui/patterns/numbers.md
```

Load on demand (see SKILL.md for the mapping table):
```
references/outsystems-ui/charts.md      # when design has charts
references/outsystems-ui/maps.md        # when design has an interactive map
references/outsystems-ui/patterns/interaction.md   # Carousel, Sidebar, DatePicker, Dropdown
references/outsystems-ui/patterns/utilities.md     # AlignCenter, Separator, gestures
references/screen-guides/<screen-archetype>.md                   # dashboard | list-table | detail-view | edit-form | master-detail | gallery-grid | kanban | timeline | calendar | wizard | map-view | inbox-notifications | settings
references/screen-guides/design-system.md                        # theme tokens, brand recolor, palette swap (cross-cutting)
references/screen-guides/component-selection.md                  # picking the right block per requirement (cross-cutting)
references/screen-guides/states-and-feedback.md                  # empty/loading/error states, toasts (cross-cutting)
references/screen-guides/reusable-blocks.md                      # when to extract a Web Block vs inline (cross-cutting)
references/screen-guides/app-type-styling.md                     # Reactive Web vs Phone App differences (cross-cutting)
references/outsystems-ui/design-tokens.md
```

## Setup

```bash
RUN_ID="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="logs/${RUN_ID}"
mkdir -p "$LOG_DIR"
echo "[$(date +%H:%M:%S)] Pipeline started" > "$LOG_DIR/timing.log"
```

## Input

Ask the user for:
1. **Design source** (required unless Pre-built spec provided) — Figma URL, web URL, image path, or HTML file
2. **App context** (optional) — path to a context.md describing existing app state. Reference existing elements by name, don't recreate.
3. **App name** (required) — target app name in the OutSystems environment. If the app doesn't exist, `app_create` mints a shell.
4. **Pre-built spec** (optional) — skip Stage 1, go straight to Stage 2.

## Design Extraction

**Figma** (prefer Desktop MCP `mcp__figma-desktop__*` over Plugin MCP):
- Phase 1 calls launched above. If root `get_design_context` returns metadata XML, parse child node IDs and batch `get_design_context` on children (pairs of 2, skip failures).
- If `get_variable_defs` returns empty, extract colors from the design context code.

**HTML file**: Read the file, extract CSS (`:root` variables, class definitions) and structure (routes, components).

**Image**: Analyze visually. Hex values may need approximation — note uncertainty in the extraction log.

## Stage 1: Compose spec.json

**If Pre-built spec provided, skip to Stage 2.**

1. **Extract** design tokens and structure per the extraction strategy above. If App context provided, read it — reference existing entities/themes/blocks by name.

2. **Visual inventory** — enumerate every visible region top-to-bottom before composing. Every item must map to a spec section.

3. **Layout + structural skeleton gates (MANDATORY upstream of block mapping)** — see SKILL.md → "Step 3.0":
   - Pick the right Layout block (`LayoutSideMenu` / `LayoutTopMenu` / `LayoutBlank`) per `layouts.md`. Don't default to `LayoutBlank`.
   - Spec that the agent must DELETE the default `LayoutTopMenu` that `CreateScreen` ships with before adding the chosen Layout.
   - Sketch the structural skeleton — answer two questions for each Layout placeholder: *what is the column grid?* and *what are the card surfaces?* The output is a tree of `Columns*` and `Card` family blocks with no `Container` nodes. Then commit a block inventory — "this region → that block" for every visual region.

4. **Block mapping pass (MANDATORY)** — see SKILL.md → "Step 3a". Walk every layout element from the visual inventory and resolve it against `outsystems-ui/ui-reference.md` (Quick lookup by requirement + Critical rules) and the relevant pattern files. Produce a mapping table and print it to the user. Past failures (e.g., spec'ing `display: grid; grid-template-columns: repeat(5, 1fr)` instead of `Columns5`, custom `track + fill` CSS instead of `ProgressBar`) all came from skipping this gate.

5. **Compose** `output/<app-name>/spec.json` using:
   - **SKILL.md** for the 4-part description format (VISUAL LAYOUT, DATA FLOW, FUNCTIONAL BEHAVIOR, PRESENTATION ORDER), anti-patterns, and OS block mapping
   - **OutSystems UI references** for block arguments, CSS classes (`styles-and-utilities.md`), recipes, and patterns
   - See `assets/enriched-blueprint.json` for the full spec schema

   **When App context exists**: reference by name only, only include NEW items. When NO context: define everything from scratch with exact values from extraction.

6. **Polish acceptance items (MANDATORY in the spec)** — bake polish gates into the spec's `acceptance_checklist` so Mentor enforces them during the build. Items: strip block default children, apply typography hierarchy (`h1` screen title → `h6`), use brand color sparingly (2–3 deliberate uses), use OS utility classes (`margin-top-xl`) not custom CSS for spacing, realistic placeholder content (no "User 1" / "TBD"), one clear focal point, section headings as `AdvancedHtml Tag="h2"`, plus a "VERIFICATION GATE" item instructing Mentor to read the app state and verify each checklist item before declaring done.

7. **Verify** before saving — per the checklist in SKILL.md → "Step 3c":
   - Every visible region has a matching section
   - DATA FLOW Expression count matches VISUAL LAYOUT Expression count
   - Every section has FUNCTIONAL BEHAVIOR
   - Every clickable element has an `action`
   - Colors/sizes match extraction, not generalized
   - No CSS class in `new_classes` reimplements an OS block (track+fill, grid-template-columns, etc.)
   - Source-name → block check (named `Carousel` / `Gallery` / `Tabs` / `Wizard` / `Accordion` / `Sidebar` / `Stepper` frames map to the matching block, not a `Columns` substitute)

```bash
echo "[$(date +%H:%M:%S)] Stage 1: Spec composed and verified" >> "$LOG_DIR/timing.log"
```

## Stage 2: Invoke Mentor (MCP)

See `mcp-flow.md` for the full reference (cursor poll loop, session-token handling, error categories).

### App discovery / creation

```
app_list { search: "<app-name>" }
```

- If found → use `app_key`
- If not found → `app_create { name: "<app-name>" }` to mint a shell (recommended for clean tests). **Do not** use `Template_*` / `template_*` / `OutSystems Sample Data` shells — Mentor's Model API rejects System modules.

### Batch strategy

Split the spec into focused batches. Mentor works best when given focused work — not everything at once.

1. **Entities + roles + ERD** → first batch
2. **App-chrome blocks (optional but RECOMMENDED)** → its own batch when `app_chrome.header.content[]` lists more than the layout's default brand wordmark + avatar. Buried inside the bulk screens batch, chrome edits are skipped consistently — the agent doesn't visit `Common/ApplicationTitle` / `Common/UserInfo` during screen construction.
3. **Screens + theme CSS** → final batch (references entities + chrome blocks already created, resuming the same Mentor session)

If `app_chrome.header.content[]` has only the default brand + avatar, fold step 2 into step 3.

For each batch, prepend the **spec preamble** (see SKILL.md):

```
Implement the following spec COMPLETELY. Do NOT stop until every item in the
acceptance_checklist is satisfied. After all code executions, verify each
acceptance_checklist item by reading the app state — if any item fails, fix it
before finishing.

ENGINE-LEVEL HARD RULES — apply to every section of the spec:

(R1) THEME CLASS COLLISIONS. NEVER use these 5 class names in chunk HTML or
     screen CSS: `main-content`, `sidebar`, `header`, `content`, `footer`.
     They collide with OutSystemsUI's LayoutBlank theme. Prefix with the app
     name: `banking-sidebar`, `dashboard-main-content`. For sidebar / header /
     footer markup, use prefixed semantic divs (e.g. `<div class="app-sidebar">`)
     not raw `<aside>` / `<nav>` / `<header>` / `<footer>`. For link colors,
     always use `!important` to override the theme's `a { color: inherit
     !important }` rule. See gotchas/theme-collisions.md.

(R2) SVG ICON COLOR BAKING. Every `<svg>` element that lands in a chunk has
     its color baked into a base64 background-image, where `currentColor`
     resolves to BLACK and CSS rules like `.X svg { fill: ... }` no longer
     apply. For ANY SVG inside a dark/coloured container (sidebar, primary
     button, gradient tile, dark card), set `fill="#fff"` (and `stroke="#fff"`
     for stroked icons) directly on the `<svg>` element. Inner shapes inherit.
     NEVER ship `<i class="ph ph-X">` font-icon markup — it does NOT render in
     ODC's SPA runtime. Use inline `<svg>` only. See gotchas/svg-icon-baking.md.

(R3) TABLERECORDS NEED A SEEDED SOURCE. Every TableRecords widget MUST have a
     non-empty `Source`. For static-demo tables (no entity backing), seed via
     a Local Variable of `List<Entity>` populated in OnInitialize using
     `ListAppend`, one append per source `<tr>` row, copying cell values
     verbatim. For data-backed tables, bind to an aggregate. NEVER ship a
     TableRecords with unset Source — published table renders "no records".
     See gotchas/tablerecords-seeding.md.

(R4) INTERACTIVE WIDGETS NEED DIV SLOTS, NOT ANCHOR SLOTS. Slots that receive
     Upload / Input / Form / Button / TableRecords / Chart MUST be
     `<div id="X" data-widget-slot="slot">`, not `<a id="X">`. An `<a>` slot
     wraps the widget in a Link that intercepts clicks. Use `<a>` slots ONLY
     when the grafted thing IS a navigation target (clickable card / row).
     See gotchas/widget-link-slot.md.

(R5) RECONCILE DUPLICATE PRIMARY ACTIONS. Before adding a Button widget to a
     screen, scan the screen's chunk for `<button>` / `<a class="btn-primary">`
     with the same label or target. If one exists in the chunk, do NOT author
     a separate Button — wire the chunk button via OnClick. Otherwise remove
     the chunk button before adding the authored Button. One primary action
     per screen. See gotchas/duplicate-buttons.md.

(R6) SPA SECTION VISIBILITY. If the source uses a `display: none / .active →
     display: block` pattern with JS-driven nav toggle, AND each section is
     becoming its own screen, STRIP the visibility CSS from the per-screen
     chunk. The screen IS the section; no JS toggle. EXCEPT keep `display:
     none` for transient overlays (modals / toasts / popovers / mobile
     sidebars) — those wire to real OutSystemsUI widgets that toggle properly.
     See gotchas/spa-section-visibility.md.

Here is the spec:
```

**Chrome-batch preamble** (use verbatim when sending the chrome batch — prepend BEFORE the spec preamble above):

```
Phase 0 — Edit the SHARED chrome blocks BEFORE any screen work:
  1) Open Common/ApplicationTitle and style the existing app-name Expression
     per app_chrome.header (apply the wordmark class via ExtendedClass; do NOT
     hand-roll a new wordmark widget anywhere).
  2) Open Common/UserInfo and ADD to its widget tree, in left-to-right order:
     the chrome icon cluster (search / theme toggle / notification IconBadge
     with the count) FOLLOWED BY a welcome-text Expression and the existing
     UserAvatar. Wrap the cluster in a Container with display-flex
     align-items-center column-gap-s.
  3) In the screen's Layout placeholder (LayoutTopMenu.Header or
     LayoutSideMenu.Navigation), add the Menu block from Common and place the
     ILink widgets DIRECTLY inside Menu.PageLinks (no wrapper Container, no
     Style on PageLinks).
After both blocks AND the Menu are populated, read each block's widget tree
back and confirm the expected children landed before declaring this phase
done. Spec follows:
```

Then call `mentor_start` and drain the cursor poll loop:

```
# Batch 1: entities + roles
mentor_start { app_key, prompt: "<spec_preamble + entities-spec>" }
# → poll mentor_get_run with cursor loop until SUCCESS
# → capture mentor_session_id + mentor_session_token

# Batch 2: chrome (only if app_chrome.header has more than brand+avatar)
mentor_start {
  mentor_session_id,
  mentor_session_token,         # newest token from batch 1
  prompt: "<chrome_preamble + spec_preamble + chrome-spec>"
}
# → poll until SUCCESS → updated token

# Batch 3: screens + theme (resume same session)
mentor_start {
  mentor_session_id,
  mentor_session_token,         # newest token
  prompt: "<spec_preamble + screens-spec>"
}
# → poll until SUCCESS → updated token
```

### Publish

After all batches succeed:

```
env_list {}
publish_start {
  mentor_session_id,
  mentor_session_token,           # latest
  env_key
}
# → poll publish_status until Completed
# → call env_app { env_key, application_key } and report runtime URL
```

**Publish is mandatory** — session changes auto-GC after 30 minutes idle.

```bash
echo "[$(date +%H:%M:%S)] Stage 2: Mentor — done" >> "$LOG_DIR/timing.log"
```

## Stage 3: Summary

```bash
echo "[$(date +%H:%M:%S)] Pipeline complete" >> "$LOG_DIR/timing.log"
```

Report to the user (3–5 lines):
- Run ID + logs path
- App name + `app_key`
- Entity / screen counts (from the spec)
- Spec size + Mentor cost estimate
- Runtime URL (rendered as a markdown link)

## Follow-up

Resume the same Mentor session for refinements — always with the **newest** `mentor_session_token`:

```
mentor_start {
  mentor_session_id,
  mentor_session_token,
  prompt: "<refinement-prompt>"
}
```

If the 30-minute idle GC has passed, the session transparently re-downloads the OML — same session continues.
