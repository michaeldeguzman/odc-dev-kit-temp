---
name: odc-catchup
description: Use when starting an OutSystems ODC session, when asked about current app state, or when unsure what was built in a previous session. Reads CLAUDE.md build history and inspects the deployed app via context tools.
---

# ODC Catchup

Recap current ODC state at session start or on demand.

## Steps

1. Read `CLAUDE.md` — find last build entry (revision, date, what was built, any pending notes)
2. Call `context_actions {app: "TestAnything"}` — count total deployed actions, note folders and names
3. Call `context_entities {app: "TestAnything"}` — list current entities
4. Summarize discrepancies: if action count doesn't match CLAUDE.md, note it

## App Reference

| | |
|---|---|
| App | Test Anything |
| App Key | `f464e3e1-4a26-4187-9d73-330de60ed791` |
| Tenant | `dbresults-rd.outsystems.dev` |
| Runtime | https://dbresults-rd-dev.outsystems.app/TestAnything |

## Output Format

```
App: Test Anything (rev N) — Development
Entities: EntityA, EntityB, ...
Actions: N total — folders: EntityA (4), EntityB (4), EntityActionResult (3), Session (1), ...
Last build: YYYY-MM-DD — [what was built]
Pending: [anything noted in CLAUDE.md]
```

## Caveats

- `no_changes_detected: true` on any prior publish does NOT mean that change deployed — `context_actions` is the authoritative source
- If `context_actions` returns AuthError, call `authenticate` first then retry
- Pass `owned_only: false` if action count seems low — inherited library actions are excluded by default
