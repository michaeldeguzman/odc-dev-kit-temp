# Interactive widgets in `<a>` slots — the rendered Link swallows everything

**The trap:** When grafting an interactive widget (Upload / Input / Dropdown / TextArea / Checkbox / Switch / Form / Button / RadioGroup) OR a structural data widget (TableRecords / Chart / List) into an `<a id="XSlot">` anchor slot, the rendered `<a>` Link widget **wraps** the grafted widget.

Consequences:
- The Link intercepts clicks — a file picker never opens, an Input never focuses, a Button's onclick doesn't fire (or fires Link navigation first).
- Table / chart layout breaks — the Link's `<a>` element does the wrong thing with the contained TableRecords' headers/rows; alignment goes off.

**Why it happens at the engine level:** ODC's HTML-to-widget translation maps `<a>` tags to OutSystemsUI Link widgets. When a slot is defined as `<a id="X">`, the slot's host widget is a Link — and a Link wraps its children. Grafting a Form / Upload / TableRecords inside means the Form / Upload / TableRecords is inside an `<a>` at runtime.

## The fix — use `<div data-widget-slot>` for interactive / data widgets

For any slot that's going to receive an interactive widget OR a data widget, the slot wrapper must be a `<div>`, not an `<a>`:

```html
<!-- ❌ Wrong: Link wraps the Upload, clicks intercepted -->
<a id="UploadSlot" class="upload-zone">...</a>

<!-- ✅ Correct: Container slot, Upload renders independently -->
<div id="UploadSlot" data-widget-slot="slot" class="upload-zone">...</div>
```

The `data-widget-slot="slot"` attribute is what signals to the engine that this `<div>` is a Container-type slot, not a regular content `<div>`.

## When `<a>` slots ARE still correct

`<a>` slots are correct when the grafted widget IS the link's content — i.e., when the user clicking the slot should navigate. Examples:
- A whole card that's clickable to navigate to a detail page → `<a id="CardSlot">` is correct.
- A list-item that drills into detail → `<a id="RowSlot">` is correct.

The rule of thumb: **if the slot's content is a thing that needs to receive direct user interaction (click, focus, type, drag, drop), use `<div data-widget-slot>`. If the slot's content IS a navigation target, `<a>` is correct.**

## How to detect during source inspection

In the source HTML / Figma extract, scan for the `<a class="...upload..." | ...input... | ...form...">` pattern — anywhere an anchor element wraps something that's clearly interactive.

In the spec.json composition pass, when authoring slot wrappers:
- Slot for Upload / Input / Form / Dropdown / Button / Checkbox / Switch / TextArea / RadioGroup / TableRecords / Chart / List → use `<div data-widget-slot="slot">`
- Slot for a navigation target (clickable card / row / tile) → `<a>` is OK

## Field-test evidence

APP992 build `bld_fc70943003` (2026-06-03): `DocsUpload` was grafted into `<a id="UploadSlot">`. The wrapping Link's `<a>` swallowed every click — the native file picker never opened. Switching to `<div id="UploadSlot" data-widget-slot="slot">` fixed it immediately and didn't break the upload-zone styling (the styled border / drop hint / icon all rendered correctly inside the div).

## How to prevent (Mentor instructions)

In the spec.json's per-section description, the VISUAL LAYOUT must specify slot wrapper type explicitly:

> *"Upload section: outer `<div class="doc-upload-zone">` with dashed border, gradient icon, title, hint copy. Native Upload widget grafted into `<div id="UploadSlot" data-widget-slot="slot">` inside the upload-zone container. NOT an `<a>` slot — Upload must receive clicks directly, not via a wrapping Link."*

## Attribution

- [`claude-oml-tool/oml-tool/skills/odc/validated/widget-grafted-into-link-slot.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/widget-grafted-into-link-slot.md) — validated 2026-06-03 (APP992 bld_fc70943003)
