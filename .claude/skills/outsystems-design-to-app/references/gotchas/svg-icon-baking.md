# SVG icon baking — why your icons go black or render blank

**The trap:** SVG icons that look correct in the source HTML render BLACK on dark containers (sidebar nav, primary buttons, coloured tiles) or simply don't render at all in the published ODC app.

**Why it happens (engine level):** ODC chunks bake each `<svg>` into a base64 data-URL `background-image: url(data:image/svg+xml;base64,...)`. Once an SVG is a background-image:

1. **`currentColor` resolves to BLACK** — there's no DOM context to inherit from inside a background-image. A `<svg fill="currentColor">` in a dark sidebar becomes black-on-dark and is effectively invisible.
2. **CSS selectors can't reach the SVG** — rules like `.sidebar svg { fill: white }` never apply, because the SVG is no longer a DOM element.
3. **Color inheritance from the parent's `color` property is lost** — the SVG sees no `color` either.

**Plus a separate hard rule:** `<i class="ph ph-name">` Phosphor font-icon markup **does NOT render** in ODC's React runtime. It works in static HTML mockups (Phosphor webfont is on the page) but ODC's SPA doesn't load the Phosphor font — the icons come out blank.

## How to detect

In the source HTML / Figma extract, scan for:
- `<svg fill="currentColor">` or `<svg>` with no explicit `fill`
- `<svg>` inside any container with a `background`-coloured parent (sidebar, primary button, gradient tile, dark card)
- `<i class="ph ph-..."` or `<i class="lucide ..."` font-icon patterns
- CSS rules like `.X svg { fill: ... }` (these won't apply post-bake)

## How to prevent (Mentor instructions)

Three rules, prepended to any design-to-app spec preamble:

1. **Bake explicit colors into every `<svg>` element** that lands in a chunk. Replace `fill="currentColor"` with the literal hex value the source's `color` / `.X svg { fill: ... }` would have resolved to. For icons on dark backgrounds, that's `fill="#fff"` (and `stroke="#fff"` if the icon is stroked rather than filled). Inner shapes inherit the outer `fill` so one attribute on `<svg>` is enough for most icons.

2. **Never ship `<i class="ph ph-X">` font-icon markup to ODC.** Use inline `<svg>` only — copy the SVG path from the source mockup or the Phosphor SVG catalog. Include `xmlns="http://www.w3.org/2000/svg"` and bake colors per rule 1.

3. **For icons that ARE matched by the SVG-to-Icon converter** (real OutSystemsUI Icon widget), the engine sets `font-family: "Phosphor"` via theme CSS and `ph-<name>` maps to a unicode codepoint via `::before`. Those work — but they need an exact name match. The mapper carries the source CSS class onto the Icon widget so sizing/layout CSS still applies. Confidence-graded fallback: if no confident name match, the engine falls back to `EmitSvgAsImage` — so the bake rule (#1) still applies.

In the `spec.json`'s per-section description, for any section whose source contains SVG icons on a coloured/dark surface, the **VISUAL LAYOUT** part must spell out the color:

> *"Sidebar nav icon (Phosphor home glyph) — `<svg fill="#ffffff" viewBox="...">...</svg>` on the navy `#0a1a3d` sidebar. White, not currentColor."*

## Anti-pattern in the spec

❌ Section description that says *"Icon inherits color from parent"* — won't work post-bake.

❌ CSS rule in `design_system.new_classes` that targets `.X svg { fill: ... }` — won't apply post-bake.

✅ Section description with explicit hex on every SVG.

## Attribution

- [`claude-oml-tool/oml-tool/skills/odc/validated/currentcolor-svg-in-dark-container.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/currentcolor-svg-in-dark-container.md) — validated 2026-06-03 (APP562 — verified in live DOM)
- [`claude-oml-tool/oml-tool/skills/odc/validated/icons-render-verify.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/icons-render-verify.md) — migrated from instruction #14 on 2026-05-09. This doc is the source of the `<i class="ph">` doesn't-render rule
