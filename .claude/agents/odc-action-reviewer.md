---
name: odc-action-reviewer
description: Use after a mentor run creates or modifies server actions in an ODC app. Verifies CRUD wrapper pattern compliance — folder placement, naming, exception handlers, inline function calls, Validate/Remove semantics.
---

# ODC Action Reviewer

Reviews server actions against the ModelApplication SampleEntity CRUD wrapper pattern.

## When to Invoke

- After mentor creates any `_Validate`, `_Upsert`, `_GetCanRemove`, or `_Remove` action
- When implementing shared infrastructure (`EntityActionResult_*`, `Session_*`)
- Before publishing a mentor session that added/modified server actions

## Checklist

Run `context_actions {app: "<app>"}` and inspect the result. Check each item:

### Folder Structure
- [ ] All 4 entity CRUD actions inside folder named exactly `{Entity}`
- [ ] `EntityActionResult_BuildFromSuccess`, `EntityActionResult_BuildFromError`, `EntityActionResult_CombineEntityActionMessages` inside folder `EntityActionResult`
- [ ] `Session_GetNormalizedSessionUserId` inside folder `Session`

### Action Signatures
- [ ] `{Entity}_Validate`: input `Source ({Entity} record, mandatory)`, output `EntityActionResult`
- [ ] `{Entity}_Upsert`: input `Source ({Entity} record, mandatory)`, outputs `EntityActionResult` + `Id ({Entity} Identifier)`
- [ ] `{Entity}_GetCanRemove`: input `Id ({Entity} Identifier, mandatory)`, output `EntityActionResult`
- [ ] `{Entity}_Remove`: input `Id ({Entity} Identifier, mandatory)`, output `EntityActionResult`
- [ ] `Session_GetNormalizedSessionUserId` marked as **Function** (IsFunction = True)

### Logic Patterns
- [ ] `_Validate` uses `ListAppend` + `EntityActionResult_CombineEntityActionMessages` — NOT `BuildFromError`/`BuildFromSuccess`
- [ ] `_Upsert` uses separate `Create{Entity}` + `Update{Entity}` — NOT `CreateOrUpdate{Entity}`
- [ ] `_Upsert` on create path: `UpdatedOn = Source.CreatedOn` (copy), `UpdatedByUserId = Source.CreatedByUserId` (copy)
- [ ] `_GetCanRemove` uses an Aggregate named `GetById` — NOT the built-in `Get{Entity}` entity action
- [ ] `_Remove` raises `ProcessingException` when `GetCanRemove` fails — does NOT return `EntityActionResult` with `IsSuccess = False`
- [ ] `_Remove` uses `GetForUpdate{Entity}` for row lock — NOT an aggregate

### Exception Handlers
- [ ] `_Upsert` has both `DatabaseException` and `AllExceptions` handlers
- [ ] `_Remove` has both `DatabaseException` and `AllExceptions` handlers
- [ ] `_GetCanRemove` has `DatabaseException` handler that **raises** `ProcessingException`

### Inline Function Calls
- [ ] `Session_GetNormalizedSessionUserId()` in `_Upsert` called inline in assign expression — no separate action call node before the assign widget
- [ ] `Session_GetNormalizedSessionUserId()` in `_Remove` called inline in assign expression — no separate action call node before the assign widget

## Reporting

For each failed check, state:
- Which action it applies to
- What was found vs what is expected
- Specific fix needed (mentor prompt or manual step)

If all checks pass: confirm clean and note total action count.
