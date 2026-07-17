---
name: dbresults-odc-scaffold-entity
description: Use when asked to "scaffold <EntityName>", "generate a full CRUD screen for <EntityName>", "build the list and detail screens for <EntityName>", or similar full-stack asks for an ODC entity in the ModelApplication pattern. Generates the 4-action server layer (Validate/Upsert/GetCanRemove/Remove) PLUS a list screen and a create/edit detail screen wired to those actions. For server actions only (no screens), use `dbresults-odc-crud-wrapper` instead.
---

# ODC Entity Scaffold — Full-Stack (Actions + Screens)

## Overview

Pattern originally observed in `SampleEntity` / `SampleEntities` / `SampleEntityDetail` in the `Model Application` reference app (`6b261520-1972-48bd-b335-15ba95e2fb93`) — that's where the convention comes from, not a dependency. This skill is **generic**: it applies to any entity in any ODC app. Everywhere below, `{Entity}` is whatever entity name you're scaffolding, `{NameField}` is that entity's own primary human-readable field (commonly `Name`, but could be `Title`, `Label`, etc. — use whatever the target entity actually has), and layout/role/theme-asset names are illustrative — detect the app's real ones via `context_screens` / `context_roles` / `context_themes` rather than assuming they match the reference app.

Produces three layers for one entity:

1. **Server Action Layer** (folder `{Entity}`) — same 4-action contract as `dbresults-odc-crud-wrapper`
2. **List Screen** (`{Entity}s`) — searchable, sortable, paginated table
3. **Detail Screen** (`{Entity}Detail`) — create/edit form driving the same actions

If the app already has the action layer wrapped (via `dbresults-odc-crud-wrapper`), skip straight to the screens section and reuse the existing actions instead of regenerating them.

## Entity Standard Fields

Every wrapped entity must carry these fields beyond its business attributes:

| Field | Type | Mandatory | Notes |
|---|---|---|---|
| `Id` | Long Integer | Yes | Auto-number, Primary Key |
| `IsActive` | Boolean | Yes | Soft-delete flag |
| `CreatedByUserId` | User Identifier | Yes | Audit — FK to User |
| `CreatedOn` | DateTime | Yes | Audit |
| `UpdatedByUserId` | User Identifier | Yes | Audit — FK to User |
| `UpdatedOn` | DateTime | Yes | Audit |

Business-specific fields go between `Id` and the audit block.

## Pre-flight Check

Run before starting any mentor session for a new entity.

1. Call `context_entities {app: "<app>"}` — verify all 6 standard fields exist on the target entity (case-sensitive). If missing, confirm with user before adding (same safe-default rules as `dbresults-odc-crud-wrapper`: always `IsMandatory=False` on add).
2. Call `context_actions {app: "<app>"}` — confirm shared infrastructure exists (see below); create first if missing.
3. Call `context_screens {app: "<app>"}` / `context_roles {app: "<app>"}` — identify the app's actual standard layout (e.g. `LayoutTopMenu` in the reference app, but use whatever this app has) and the role that should protect the new screens (don't assume a role named `ModelApplication` exists — ask the user if it's unclear which role to use).
4. Confirm a `User` entity is available in the app's data model — both screens join/list against it (`CreatedByUserId`/`UpdatedByUserId` dropdowns, `Created By User` column).

## Shared Infrastructure (must exist before scaffolding)

Same as `dbresults-odc-crud-wrapper`:

- **Structures:** `EntityActionResult` (`IsSuccess`, `EntityActionMessages` list, `CombinedEntityMessageText`, `CombinedEntityActionMessageTypeId`), `EntityActionMessage` (`MessageTypeId`, `MessageText`)
- **Static Entity:** `MessageType` — Success(1) / Error(2) / Warning(3) / Info(4)
- **Helper actions** (folder `EntityActionResult`): `EntityActionResult_BuildFromSuccess`, `EntityActionResult_BuildFromError`, `EntityActionResult_CombineEntityActionMessages`
- **Session helper** (folder `Session`): `Session_GetNormalizedSessionUserId()` — marked as **Function**, called inline in assign expressions, never as a separate call node
- **User Exception:** `ProcessingException`

If any are missing, create them first (reference ModelApplication or recreate the pattern) — see `dbresults-odc-crud-wrapper` for the full spec.

## Layer 1 — Server Actions (folder: `{Entity}`)

Four actions, full CRUD lifecycle. Identical contract to `dbresults-odc-crud-wrapper` — reuse that skill's action bodies verbatim. Summary:

### `{Entity}_Validate(Source)`

- Mandatory-field checks (e.g. `{NameField}` not empty → `"{NameField} is required."`; `Length({NameField}) > 50` → `"{NameField} cannot be longer than 50 characters."` — repeat per mandatory business field, not just the name field) via `ListAppend` to `EntityActionMessages`
- Empty messages → `IsSuccess = True`; otherwise `CombineEntityActionMessages` + `IsSuccess = False`
- Returns `EntityActionResult`. Do NOT call `BuildFromError`/`BuildFromSuccess` here.

### `{Entity}_Upsert(Source)`

- Calls `{Entity}_Validate` first — short-circuits with the validation result if invalid
- `Source.Id = NullIdentifier()` branch:
  - **Create:** `CreatedOn`/`CreatedByUserId` set fresh; `UpdatedOn`/`UpdatedByUserId` copied from the same values (not a second `CurrDateTime()` call); `IsActive = True`; calls `Create{Entity}`
  - **Update:** `UpdatedOn`/`UpdatedByUserId` set fresh; calls `Update{Entity}`
- Assigns `Id` from the create/update result
- Success message: `"{Entity} \"<{NameField}>\" has been saved."`
- Exception handlers: `DatabaseException` → generic user-safe message; `AllExceptions` → passes `ExceptionMessage` through
- Returns `EntityActionResult` + `Id`

### `{Entity}_GetCanRemove(Id)`

- Aggregate fetch by `Id`, `MaxRecords = 1` (named `GetById`, not the built-in `Get{Entity}` action)
- `Id = NullIdentifier()` → error `"Cannot remove an unsaved {Entity}."`
- `IsActive = False` → error `"Cannot remove {Entity} \"<{NameField}>\", it is already removed."`
- Otherwise → success
- `DatabaseException` re-raises as `ProcessingException` (not swallowed, no `AllExceptions` handler)
- Returns `EntityActionResult`

### `{Entity}_Remove(Id)`

- Calls `{Entity}_GetCanRemove` — if not allowed, **raises** `ProcessingException` with the combined message (does NOT return a failed `EntityActionResult`)
- Calls `Get{Entity}ForUpdate` (row-lock)
- Sets `UpdatedOn`/`UpdatedByUserId`, `IsActive = False`; calls `Update{Entity}`
- Success message: `"{Entity} \"<{NameField}>\" has been removed."`
- Exception handlers: `DatabaseException` → generic error; `AllExceptions` → passes message through
- Returns `EntityActionResult`

> **Frontmatter note on `GetCanRemove`/`Remove` as Functions:** the source app has both actions marked with the ODC "Function" toggle. `GetCanRemove` being a Function is unremarkable (read-only). `Remove` being a Function is atypical — Functions are conventionally side-effect-free, and `Remove` mutates data. Confirm with the user whether to replicate this (matches source exactly, enables inline calling) or leave `Remove` as a regular action (safer convention) before generating — don't silently pick one.

## Layer 2 — List Screen (`{Entity}s`)

Role-protected (same role gating the rest of the app's CRUD screens).

**Aggregate `Get{Entity}s`:**
- Sources: `{Entity}` inner-joined to `User` on `{Entity}.CreatedByUserId = User.Id`
- Filter: `SearchKeyword = "" or {Entity}.{NameField} like "%" + SearchKeyword + "%"`
- Sort: dynamic via `TableSort` local variable
- Pagination: `StartIndex` / `MaxRecords` (default 10)

**Local variables:** `SearchKeyword` (Text), `StartIndex` (Integer, default 0), `MaxRecords` (Integer, default 10), `TableSort` (Text)

**Screen actions:**

| Action | Logic |
|---|---|
| `DeleteOnClick(Id)` | Calls `{Entity}_Remove`; if `IsSuccess = False` → show Error message |
| `OnSearch` | Resets `StartIndex = 0`, refreshes aggregate |
| `OnPaginationNavigate(NewStartIndex)` | Assigns new start index, refreshes aggregate |
| `OnSort(SortBy)` | Same column clicked twice → append `" DESC"` (toggle); otherwise `TableSort = SortBy`; resets `StartIndex = 0`; refreshes aggregate |

**UI structure** (inside the app's standard layout, e.g. `LayoutTopMenu` in the reference app — use whatever layout this app actually uses):

- Title placeholder: `<h1>{Entity} List</h1>`
- Actions placeholder: Columns2-style container — Search block (input bound to `SearchKeyword`, `OnChange` → `OnSearch`) + `"Add {Entity}"` button (navigates to `{Entity}Detail` with `NullIdentifier()`)
- MainContent placeholder:
  - `TableRecords` bound to `Get{Entity}s.List`, `OnSort` → `OnSort`
  - Columns: `{NameField}` (link → detail), `Created On` (formatted datetime, right-aligned), `Created By User` (`User.Name`), `Updated On` (formatted datetime, right-aligned), actions column (trash icon link → `DeleteOnClick`)
  - `IsTableLoadingOrEmpty` container with an `IfWidget`: empty state → `"No items to show..."`, loading state → list-updating container
  - Pagination block wired to `OnPaginationNavigate`, caret-left/right icons

No `OnInitialize` — data comes from the screen aggregate at load, not an initialize action.

## Layer 3 — Detail Screen (`{Entity}Detail`)

Role-protected (same as list screen). Input parameter: `{Entity}Id` (`{Entity}` Identifier).

**Aggregates:**
- `Get{Entity}ById` — fetches `{Entity}` filtered by `{Entity}.Id = {Entity}Id`, single record
- `GetUsers` — all `User` records sorted by `User.Name` (populates the audit-field dropdowns)

**Screen action `SaveDetail`:**
- Checks `Form1.Valid` — if invalid, shows `"Navigate to another screen or implement the required logic."`
- Calls `{Entity}_Upsert` with `Get{Entity}ById.List.Current` as source
- `IsSuccess = False` → show Error message
- `IsSuccess = True` → navigate back to `{Entity}s`

**UI structure** (inside the app's standard layout, e.g. `LayoutTopMenu` in the reference app — use whatever layout this app actually uses):

- Title placeholder: `IfWidget` on `{Entity}Id <> NullIdentifier()` → `<h1>Edit {Entity}</h1>` / `<h1>New {Entity}</h1>`
- MainContent placeholder: Columns2 block (`PhoneBehavior = BreakColumns.All`)
  - **Column 1:** `Form1` — one container per field:
    - `{NameField}` — Text input, mandatory, bound to `Get{Entity}ById.List.Current.{Entity}.{NameField}`
    - One input per remaining business field (mandatory/optional and widget type follow that field's own definition — not prescribed here)
    - `Created On` — Datetime input, mandatory
    - `Created By User` — Dropdown (Text mode), list = `GetUsers.List`, values = `User.Id`, labels = `User.Name`, bound to `CreatedByUserId`
    - `Updated On` — Datetime input, mandatory
    - `Updated By User` — Dropdown (same pattern), bound to `UpdatedByUserId`
    - `Is Active` — Checkbox, bound to `IsActive`
    - Buttons container: `"Back"` (navigates to `{Entity}s`, `ValidateAndContinue`) + `"Save"` (default button, calls `SaveDetail`, `ValidateAndContinue`, `btn btn-primary`)
  - **Column 2 (optional):** decorative image filling the column width, if the app's theme has a suitable asset — purely cosmetic, skip if none fits or if the user doesn't want it

## Mentor Prompt Template

```
Scaffold the full CRUD stack for the {EntityName} entity following the
ModelApplication SampleEntity/SampleEntities/SampleEntityDetail pattern exactly.

--- Server Actions (folder {EntityName}) ---
[paste the Layer 1 action specs above, filled in with {EntityName} and its
business fields]

--- List Screen ({EntityName}s) ---
[paste the Layer 2 spec above]

--- Detail Screen ({EntityName}Detail) ---
[paste the Layer 3 spec above]

All shared helpers (EntityActionResult_BuildFromSuccess, BuildFromError,
CombineEntityActionMessages, Session_GetNormalizedSessionUserId) already
exist in the app. Session_GetNormalizedSessionUserId is marked as a Function
and must be called inline in assignment expressions.
```

Run screens in a follow-up mentor turn after the actions are confirmed compiling — don't generate all three layers in one shot if the app is unfamiliar; smaller batches make failures easier to isolate.

## Key Patterns

- **Soft-delete over hard-delete** — `IsActive = False` via `GetForUpdate` + `Update`, never `Delete`.
- **`EntityActionResult` contract** — every server action returns this; the UI checks `IsSuccess` and shows `CombinedEntityMessageText` on failure.
- **Audit fields auto-populated in Upsert** — `CreatedOn`/`By` only on create; `UpdatedOn`/`By` on both create and update.
- **Validation is a separate action** — `_Validate` is called first inside `_Upsert`, keeping concerns separated.
- **`GetCanRemove` guard** — dedicated pre-check action before any remove, raising `ProcessingException` if the record is ineligible.
- **Exception handler pattern** — `DatabaseException` gets a generic user-safe message; `AllExceptions` passes the raw exception message through.
- **Dynamic sort toggle** — same column clicked twice appends `" DESC"`; pagination resets on sort change.
- **Dual-aggregate detail screen** — `Get{Entity}ById` for the record, `GetUsers` for dropdown population.
- **Create vs. edit title** — `IfWidget` on `{Entity}Id <> NullIdentifier()` drives the `<h1>` text.
- **No `OnInitialize`** — data is fetched via screen aggregates at start, not in `OnInitialize`.

## Known Issues to Flag

- **Phosphor icon version mismatch.** The `"Add"` button's plus icon may be authored against Phosphor 1.x naming. Phosphor 2.0 also has a `plus` icon but weight/variant can differ, which produces a validation warning. Check the app's icon library version before scaffolding and confirm the icon name resolves cleanly — don't ignore the warning as cosmetic without checking.
- **`Remove` marked as Function** (see Layer 1 note above) — confirm intent before replicating.

## Verification Checklist

After mentor run, confirm via `context_actions` + `context_screens`:

- [ ] Pre-flight run: entity fields verified, shared infra confirmed present
- [ ] All 4 server actions exist in folder `{Entity}`, matching `dbresults-odc-crud-wrapper`'s checklist
- [ ] List screen: aggregate joins `User`, filter/sort/pagination wired, all 4 screen actions present
- [ ] List screen: empty/loading states present, no `OnInitialize`
- [ ] Detail screen: both aggregates present, `Form1` fields bound correctly, `SaveDetail` wired to `_Upsert`
- [ ] Detail screen: title toggles Create/Edit via `{Entity}Id <> NullIdentifier()`
- [ ] Both screens role-protected
- [ ] No icon validation warnings (or flagged/resolved if present)
- [ ] 0 errors in validation (warnings for unused actions are expected)
