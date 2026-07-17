# Duplicate primary actions — two buttons doing the same thing

**The trap:** A screen ends up with two primary-action buttons that target the same destination. One comes from the source HTML's `<button>Sign In</button>` (emitted into the chunk verbatim). The other is a separately-authored Button widget the agent added because the spec said "the login form needs a Submit button." Both target the dashboard. The user sees two overlapping, redundant buttons.

**Why it happens:** the spec composition step doesn't reconcile against the chunk. The chunk is treated as opaque visual content; the spec adds widgets in parallel. Without an explicit reconcile pass, both end up in the final OML.

## Where it shows up

- Login screens (the source's `<button>Sign In</button>` + an authored Login button).
- Form submit screens (source's submit + authored Save).
- Search bars (source's search button + authored "Apply filter").
- Card actions (source's "View details" link rendered as button + authored "Open" button).

## The fix — keep ONE wired primary action

Decide which one survives:

- **Prefer keeping the authored Button widget** if it's wired to a real screen action (better behaviour, role-aware).
- **Drop the chunk-emitted `<button>`** by stripping it from the chunk HTML before adding to the screen.

OR:

- **Prefer keeping the chunk-emitted button** if its styling is hard to replicate.
- **Don't author a duplicate Button widget** — wire an OnClick handler to the chunk button instead.

The principle: one primary action = one widget = one wired event.

## How to detect during source inspection

For each screen in the source:

1. Enumerate the source's primary-action buttons (`<button class="primary">` / `<button class="btn-primary">` / `<button type="submit">`).
2. Enumerate the spec's authored Button widgets.
3. For each authored Button, check whether the chunk already contains a button with the same text + same target.
4. If yes → reconcile (drop one).

```bash
grep -nE '<button[^>]*>(Sign In|Login|Submit|Save|Continue|Next|Apply|Search)' source.html
```

In the spec.json's block-mapping pass (Step 3a of the design-to-app procedure), include a "primary action reconcile" verification:

> *"For each screen, count primary-action buttons in the chunk + count authored Button widgets. If both exist with the same label/target, keep ONE — preferably the authored widget (better wiring). Remove the duplicate from the chunk."*

## How to prevent (Mentor instructions)

Spec preamble line:

> *"Before adding any Button widget to a screen, scan the screen's chunk HTML for `<button>` / `<a class="btn-primary">` / similar elements with the same label or target. If a matching button exists in the chunk, do NOT author a separate Button widget — wire the chunk button to the screen action via OnClick instead. Otherwise, remove the chunk button before adding the authored Button. One primary action per screen, one wiring."*

## Field-test evidence

APP1387 (2026-06-02): the login page rendered TWO buttons — a chunk-emitted `<button>Sign In</button>` AND a separately-authored `Secure Login` Button widget, both targeting the dashboard.

## Attribution

- [`claude-oml-tool/oml-tool/skills/odc/validated/duplicate-primary-action.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/duplicate-primary-action.md) — validated 2026-06-02 (APP1387 — "login page has two buttons")
