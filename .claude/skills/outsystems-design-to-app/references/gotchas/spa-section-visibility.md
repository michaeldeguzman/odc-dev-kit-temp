# SPA section-visibility toggle — content vanishes post-publish

**The trap:** Source HTML mockups frequently use a single-page-app pattern: all sections live in one HTML document, hidden with `display: none`, and a JS handler adds `.active` (which CSS toggles to `display: block`) when the user navigates. Looks great in a static mockup; doesn't work in an ODC SPA.

**Why it happens:** when those sections become per-screen `add_widgets_from_html` chunks (or equivalent Mentor-driven screen splits), each screen IS one section — so the JS that adds `.active` no longer needs to run, AND no longer does run. But the **source's visibility CSS still applies** (the chunk carries it forward verbatim). Every non-default screen renders the **chrome only** — the content sits there with `display: none`, invisible.

## Symptom

User opens the published app, navigates to a non-default screen, and sees:
- The sidebar nav renders.
- The header renders.
- The main content area is empty / shows just a background.

If they View Source / Inspect, the content is in the DOM but `display: none`.

## The fix — three options, preferred order

**Option 1 (preferred): strip the visibility CSS from the chunk.** If the source has `.section { display: none } .section.active { display: block }`, the chunk on each screen should **drop both rules** (or override them to `display: block !important`). The screen IS the section — no toggle needed.

**Option 2: override on the wrapping selector.** Add an explicit `.<section-id> { display: block !important }` rule to the screen CSS, scoped to whichever section is on that screen.

**Option 3: rename the wrapper class.** Strip the `section` / `view` / `pane` class entirely from the per-screen chunk. The CSS rule no longer matches; visibility defaults to `block`.

## Important EXCEPTION — transient overlays

JS-toggled TRANSIENT overlays (modals, dropdowns, popovers, success toasts, mobile sidebars that slide in) must STAY hidden by default. The `display: none` + a JS show/hide is correct for them — and in our flow, the user-action is wired to a Mentor action that toggles the OutSystemsUI equivalent widget (Modal, Toast, Popover, Sidebar).

So the rule is: **strip `display: none` only when the section IS the screen's main content.** Keep `display: none` for overlays.

## How to detect during source inspection

In the source CSS / extracted styles:

```bash
grep -nE '\.(section|view|pane|screen)[^.]* *\{[^}]*display: *none' source.css
grep -nE '\.(section|view|pane|screen)[^.]*\.active *\{[^}]*display' source.css
```

If you see this pattern AND each section is going to become its own screen, strip the visibility CSS per Option 1.

Cross-check with the source's JS:

```bash
grep -nE 'navigateTo|showSection|switchView|setActive|\.classList\.(add|remove)\(.active.' source.js
```

If JS exists that adds/removes `.active` between sections (not for overlay open/close), the pattern applies.

## How to prevent (Mentor instructions)

In the spec.json's `design_system.visibility_rules` field, encode the strip rule:

```json
"visibility_rules": {
  "strip_section_display_none": true,
  "preserve_overlay_visibility": ["modal", "toast", "popover", "mobile-sidebar"]
}
```

In the spec preamble, instruct Mentor:

> *"If the source HTML uses a `display: none / .active → display: block` pattern to switch between sections, and each section is being mapped to its own screen, strip the visibility CSS from the per-screen chunk. The screen IS the section; no JS toggle is required. EXCEPTION: keep `display: none` for transient overlays (modals, toasts, popovers, mobile sidebars) — those still get wired to OutSystemsUI widgets that handle show/hide via real events."*

## Field-test evidence

This bit three different builds on 2026-06-02: APP1388 prod (6-screen ConstructionOperations) and TestV3 shadow with the same source HTML. The fix is now baked into the transpiler's plan-lint but worth knowing for novel sources the transpiler doesn't recognise.

## Attribution

- [`claude-oml-tool/oml-tool/skills/odc/validated/spa-visibility-toggle-neutralization.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/spa-visibility-toggle-neutralization.md) — validated 2026-06-02 (APP1388 / TestV3)
