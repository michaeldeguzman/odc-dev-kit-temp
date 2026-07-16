---
description: ODC server action error handling conventions. Apply to all server actions in OutSystems Developer Cloud apps.
---

# ODC Error Handling

## Exception Handlers

- Every server action that calls `Create{Entity}`, `Update{Entity}`, or `Delete{Entity}` (or their row-lock variants) **must** have both:
  - `DatabaseException` handler
  - `AllExceptions` handler
- `GetCanRemove` uses only a `DatabaseException` handler — it raises `ProcessingException`, it does not return an error result
- No bare `AllExceptions`-only handlers on data actions — database errors need the specific handler

## EntityActionResult Pattern

- User-facing error text goes in `EntityActionResult.CombinedEntityMessageText` via `EntityActionResult_BuildFromError`
- Internal error details (stack traces, column names, SQL) must never appear in user-facing messages
- Standard database error message: `"An error has occurred. Please see a system administrator."`
- `AllExceptions` handler may expose `ExceptionMessage` directly — acceptable for dev context, review before going to production

## Raise vs Return

- In `{Entity}_Remove`: if `{Entity}_GetCanRemove` returns `IsSuccess = False` → **raise** `ProcessingException` with `CombinedEntityMessageText` — do NOT assign `EntityActionResult` and return
- In `{Entity}_GetCanRemove`: `DatabaseException` handler → **raise** `ProcessingException("An error has occurred. Please see a system administrator.")` — do not return an error result
- Raise = caller's problem. Return = action's problem. Remove delegates guard check to GetCanRemove; a failed guard is a caller error.

## Validate Action

- `{Entity}_Validate` must use `ListAppend` + `EntityActionResult_CombineEntityActionMessages` — never `BuildFromError` or `BuildFromSuccess` inside Validate
- Validate accumulates all errors before returning; it does not short-circuit on first failure

## Exception Handler Placement

- Exception handlers attach to the action scope, not to individual call nodes
- Both `DatabaseException` and `AllExceptions` handlers must end with an `End` node (not fall through)
