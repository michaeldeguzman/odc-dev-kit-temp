---
description: ODC server/client action folder-organization conventions. Apply when generating any new server action, client action, or when driving Mentor to build features/screens for an ODC app.
---

# ODC Action Folder Organization

## Core Rule

- Every server/client action created for an app goes into a named folder — never left in the app's root/default folder
- Folder name matches what the action is *for*: the entity it wraps, the feature it belongs to, or the shared concern it serves — not a generic bucket like "Actions" or "Logic"

## Established Folder Conventions

- CRUD wrapper actions (`{Entity}_Validate`/`_Upsert`/`_GetCanRemove`/`_Remove`): folder `{Entity}`, exact name match (`dbresults-odc-crud-wrapper`, `dbresults-odc-scaffold-entity`)
- Shared CRUD helpers: `EntityActionResult_*` → folder `EntityActionResult`; `Session_GetNormalizedSessionUserId` → folder `Session`
- Auth baseline actions (`SendResetPasswordEmail`, `SendChangeEmail`, `UpdateUser`, `DoLogin`, `DoLogout`, etc.): folder `Authentication` (`dbresults-odc-new-app-baseline`)
- Cross-app BDD test Service Actions (`{Entity}_*_SA`): folder named after the source entity they wrap (`rules/testing.md`)

## When Driving Mentor

Applies to `outsystems-spec-driven-build`, `outsystems-design-to-app`, and `outsystems-mentor-copilot` tasks that create logic — not just the CRUD-wrapper skills, which already enforce this themselves.

- Any Mentor prompt asking for new server/client actions must name the target folder explicitly — Mentor defaults to the app root if not told otherwise
- For a business feature with no existing entity/CRUD convention to anchor to, use the feature name as the folder (e.g. `Reporting`, `Notifications`) — confirm the name with the user rather than inventing one silently
- Don't let generated actions accumulate unfoldered "just this once" — retrofitting folders is expensive once dozens of actions exist unorganized

## Auto-Layout (required after creation)

After any batch that creates or modifies Server Actions, Client Actions, or Service Actions, run a follow-up Mentor turn to auto-position all flow nodes:

```
Auto-position all flow nodes in each of these actions so the layout is clean
and readable: {Action1}, {Action2}, ...

Do not change any logic, connections, inputs, outputs, or expressions —
only reposition the nodes.
```

- Run as a separate Mentor turn (resume the same session, do NOT combine with logic changes)
- List every action created in the batch — do not auto-layout in the same turn as logic creation
- After auto-layout, publish

## Verification

- `context_actions` returns the folder for each action — spot-check after any Mentor batch that creates actions
- A newly created action with no folder in `context_actions` output is a defect, not a cosmetic nit
