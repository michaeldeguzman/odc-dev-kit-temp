# SPA shell fidelity — four patterns that don't auto-resolve

**The trap:** Even when the design-to-app pipeline handles the common SPA-shell shapes correctly, there are four specific patterns that fall through to the agent / Mentor and silently ship wrong. The build passes, the publish succeeds — but the rendered surface has subtle defects that only become visible on a real human comparison against the source.

**Why these are silent:** each defect is hidden by JavaScript that the source HTML uses to *initialize* state, but the OML runtime doesn't execute that JS. So the rendered page falls back to the static default — which is the wrong static default for every screen except the first one.

## Pattern 1 — Header title stuck on the default

**Defect:** the header's current-page label (a breadcrumb `<span class="current">`, a `#breadcrumb-current` element, or the last span in a `.breadcrumb(s)` / `#breadcrumb` box) shows the **default page's name on every screen** — because the source has a JS handler that updates it at navigation time. The OML runs no JS.

**Fix:** per screen, set that element's text to THIS screen's title. Pick the source in this order:
1. A JS map (`breadcrumbMap` / `titles` / `pageTitles` / `titleMap` = `{screenId: title}`).
2. The nav item that targets this screen (`<… data-screen="X" / onclick="navigateTo('X')">LABEL</…>` → use `LABEL`).
3. This screen's own `<h1 class="screen-title">` or first `<h1>`.

In the spec.json, encode this per-screen as a `header_title_text` field — Mentor sets the literal text on the breadcrumb element per screen.

## Pattern 2 — Table header colour stuck on a default

**Defect:** a data grid's header renders a **fixed colour (often navy)** regardless of the source. The source header might actually be dark (solid brand colour) OR light (a faint `rgba(...,0.05)` tint + a bottom border).

**Fix:** read the source `thead` / `th` / `.table-header` CSS rule and apply its **actual** background and color onto the header cells with `!important`. A faint-alpha bg is a deliberately LIGHT header — honour it; don't treat it as "no colour given, default to navy."

**Critical sub-fix — contrast:** a LIGHT header needs DARK text; a DARK header needs WHITE text. A faint-alpha bg (e.g., `rgba(0,74,153,0.05)`) sits over the light grid surface and reads as near-white — so it needs DARK text even though the raw rgba has low luminance. Don't ship white-on-light invisible headers.

In the spec.json, the per-section `outsystems_hints.css_classes` for the table header should carry the source's actual colors, not defaults.

## Pattern 3 — Upload widget loses its styled drop-zone

**Defect:** a styled `.drop-zone` / `.upload-area` / `.doc-upload-zone` (dashed border, gradient icon, title, hint copy) gets replaced by a **bare native Upload widget**, losing the design. The OS parser strips `<input type=file>` (so a real Upload widget is required) — but the conversion erases the styled container.

**Fix:** KEEP the styled container + its inner visual. Place the native Upload widget in a slot INSIDE the styled container, not as a replacement for it:

```html
<div class="doc-upload-zone">
  <svg class="upload-icon" .../>
  <h3>Drop files here</h3>
  <p>or click to browse</p>
  <div id="USlot" data-widget-slot="slot"></div>
</div>
```

Then graft the Upload widget into `USlot`. See [`widget-link-slot.md`](widget-link-slot.md) for why `<div data-widget-slot>` (not `<a>`) is the correct slot wrapper.

## Pattern 4 — Icons on coloured tiles rendered BLACK

**Defect:** an `<svg>` inside a dark/gradient container (`.stat-icon`, `.provision-icon`, a primary button, a coloured badge) renders BLACK. Root cause: the engine bakes the SVG to a base64 background-image where CSS can't reach it.

**Fix:** bake the colour INTO the svg markup itself. For dark/coloured containers, add `fill="#fff"` (and `stroke="#fff"` for stroked icons) to the `<svg>` element. Inner shapes inherit. Never rely on `currentColor` reaching a baked SVG.

This is the same root cause as [`svg-icon-baking.md`](svg-icon-baking.md) — cross-reference there for the full explanation.

## How to detect during source inspection

Before composing the spec.json, scan the source for these four patterns:

1. **Header title** — does the source HTML have a `.current` / `#breadcrumb-current` / `.breadcrumb` element that JS updates at runtime?
2. **Table header** — is there a `thead` with a faint-alpha background OR a `.table-header` class with non-default colours?
3. **Upload zone** — does the source have a styled `.drop-zone` / `.upload-area` container, OR just a bare `<input type=file>`?
4. **SVG color** — are there `<svg>` elements inside containers with a coloured background and CSS that sets `.X svg { fill: ... }`?

For each detected pattern, the spec.json must include the explicit override per the fixes above.

## Why this is your job (not the theme's)

All four are "the design is a contract" — the source encodes them in CSS or JS that the OML runtime doesn't execute, so the value must be **baked into the plan/spec** at build time. The transpiler / Mentor handles the common shapes deterministically; you (or the agent) are the fallback for novel shapes.

## Attribution

- [`claude-oml-tool/oml-tool/skills/odc/validated/spa-shell-fidelity.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/spa-shell-fidelity.md)
