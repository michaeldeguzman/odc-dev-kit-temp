---
description: ODC element description conventions. Apply when creating or modifying any element in OutSystems Developer Cloud apps.
---

# ODC Description Conventions

## Rule

Every named element must have a non-empty `Description` — never leave it blank.

## Applies To

- Entities and entity attributes
- Server Actions, Client Actions, Service Actions
- Screens and Web Blocks
- Input and Output parameters on actions and blocks
- Local Variables (when purpose is non-obvious)
- Structures and structure attributes
- Roles
- Client Variables and Site Properties
- UI Flows

## What a Good Description Contains

- **What it is / what it does** — one sentence, plain language
- **Why it exists** — if not obvious from the name alone
- **Units or format** — for numeric/text fields where it matters (e.g. "stored in UTC", "percentage 0–100")
- **Constraints or invariants** — e.g. "set once on create, never updated", "soft-delete flag — False means inactive"

## What to Avoid

- Restating the name verbatim ("UserName — the user name")
- Vague filler ("used by the system", "various purposes")
- Leaving descriptions blank because the name "seems obvious" — names drift; descriptions don't

## When Driving Mentor

- Any Mentor prompt creating new elements must include description text for each element
- Spot-check via `context_entities`/`context_actions`/`context_screens` — a blank `description` field is a defect, not a cosmetic nit
