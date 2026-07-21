---
name: dbresults-odc-crud-wrapper
description: Use when asked to "create a CRUD wrapper for <EntityName>" for an ODC entity in the ModelApplication pattern. Generates Upsert, Validate, Remove, and GetCanRemove server actions matching the SampleEntity convention — with audit fields, soft-delete, and EntityActionResult return type.
---

# ODC CRUD Wrapper — ModelApplication Pattern

## Overview

Derived from `SampleEntity` in the `Model Application` app (`6b261520-1972-48bd-b335-15ba95e2fb93`). Every ODC entity gets **4 server actions** (not 5 — no GetAll/GetById, no hard delete). GetAll/GetById are handled inline by screen aggregates.

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

Run before starting any mentor session for a new entity. Do not skip — missing fields cause compile errors; silent adds on populated tables cause publish failures.

### 1. Check entity fields

Call `context_entities {app: "<app>"}` and locate the target entity. Verify all 6 standard fields exist with correct names and types (OutSystems is case-sensitive).

If any are missing:

1. Report which fields are absent
2. Confirm with user before adding:
   > "Entity `{Entity}` is missing: `IsActive`, `CreatedOn`. Add them now?
   > Fields will be added as optional with safe defaults — safe for both new and existing tables."
3. On confirmation, add in the same mentor session:

| Field | Type | IsMandatory | Default |
|---|---|---|---|
| `IsActive` | Boolean | False | `True` |
| `CreatedOn` | DateTime | False | `#1900-01-01 00:00:00#` |
| `UpdatedOn` | DateTime | False | `#1900-01-01 00:00:00#` |
| `CreatedByUserId` | User Identifier | False | _(none)_ |
| `UpdatedByUserId` | User Identifier | False | _(none)_ |

**Always add as `IsMandatory=False`** — safe for new tables and required for existing ones with data. No downside.

### 2. Check shared infrastructure

Call `context_actions {app: "<app>"}` and confirm required helper actions exist (see Shared Infrastructure below). If missing, create them in the same mentor session before the CRUD actions.

## Shared Infrastructure (must exist in app before wrapping)

**Structures:**

`EntityActionResult`
- `IsSuccess` (Boolean)
- `EntityActionMessages` (EntityActionMessage List, mandatory)
- `CombinedEntityMessageText` (Text)
- `CombinedEntityActionMessageTypeId` (MessageType Identifier, mandatory)

`EntityActionMessage`
- `MessageTypeId` (MessageType Identifier)
- `MessageText` (Text)

**Static Entity:** `MessageType` — records: Success(1), Error(2), Warning(3), Info(4)

**User Exception:** `ProcessingException` — must be defined in the app; raised by `_GetCanRemove` (DatabaseException handler) and `_Remove` (GetCanRemove failure path).

**Helper Server Actions (with required folder placement and implementations):**

Folder `EntityActionResult`:

`EntityActionResult_BuildFromSuccess(EntityActionResultMessageText: Text)` → `EntityActionResult`
- Assign: `EntityActionResult.IsSuccess = True`
- Assign: `EntityActionResult.CombinedEntityMessageText = EntityActionResultMessageText`
- Assign: `EntityActionResult.CombinedEntityActionMessageTypeId = Entities.MessageType.Success`

`EntityActionResult_BuildFromError(EntityActionResultMessageText: Text)` → `EntityActionResult`
- Assign: `EntityActionResult.IsSuccess = False`
- Assign: `EntityActionResult.CombinedEntityMessageText = EntityActionResultMessageText`
- Assign: `EntityActionResult.CombinedEntityActionMessageTypeId = Entities.MessageType.Error`

`EntityActionResult_CombineEntityActionMessages(EntityActionMessages: EntityActionMessage List)` → `CombinedEntityActionMessageTypeId` (MessageType Identifier), `CombinedEntityActionMessageText` (Text)
- Local variable: `CurrentMessage` (EntityActionMessage)
- Assign init: `CombinedEntityActionMessageTypeId = Entities.MessageType.Info`
- ForEach over `EntityActionMessages`:
  - Assign: `CurrentMessage = EntityActionMessages.Current`
  - Assign: `CombinedEntityActionMessageText = If(CombinedEntityActionMessageText = "", CurrentMessage.MessageText, CombinedEntityActionMessageText + "; " + CurrentMessage.MessageText)`
  - If `CurrentMessage.MessageTypeId = Entities.MessageType.Error` → Assign `CombinedEntityActionMessageTypeId = Entities.MessageType.Error`
  - Else If `CurrentMessage.MessageTypeId = Entities.MessageType.Warning and CombinedEntityActionMessageTypeId <> Entities.MessageType.Error` → Assign `CombinedEntityActionMessageTypeId = Entities.MessageType.Warning`
  - Else: no-op (loop back)
- Severity escalates Info → Warning → Error; never downgrades. Messages joined with `"; "` separator.

Folder `Session`:

`Session_GetNormalizedSessionUserId()` → `NormalizedSessionUserId: User Identifier`
- Assign: `NormalizedSessionUserId = GetUserId()`
- **Must be marked as Function** (ODC "Function" toggle = True) so it can be called inline in assignment expressions

If any of these don't exist in the target app, create them first (in the correct folders) using the implementations above.

## The 4 CRUD Actions

### 1. `{Entity}_Validate`

```
Input:  Source ({Entity} record, mandatory)
Output: EntityActionResult
Local variables: NewMessage (EntityActionMessage)

Flow:
  1. For each mandatory business field (e.g. Name):
     a. If Source.FieldName = "" (or default/empty):
        Assign NewMessage.MessageTypeId = Entities.MessageType.Error
        Assign NewMessage.MessageText = "FieldName is required."
        ListAppend(NewMessage) → EntityActionResult.EntityActionMessages
     b. If Length(Source.FieldName) > MaxLength:
        Assign NewMessage.MessageTypeId = Entities.MessageType.Error
        Assign NewMessage.MessageText = "FieldName cannot be longer than N characters."
        ListAppend(NewMessage) → EntityActionResult.EntityActionMessages

  2. If EntityActionResult.EntityActionMessages.Empty  [label: "No errors?"]
     True  → Assign EntityActionResult.IsSuccess = True → End
     False → Call EntityActionResult_CombineEntityActionMessages(EntityActionResult.EntityActionMessages)
             Assign EntityActionResult.IsSuccess = False
             Assign EntityActionResult.CombinedEntityMessageText = CombineMessages.CombinedEntityActionMessageText
             Assign EntityActionResult.CombinedEntityActionMessageTypeId = CombineMessages.CombinedEntityActionMessageTypeId
             → End

IMPORTANT: Do NOT call BuildFromError/BuildFromSuccess inside Validate.
Use NewMessage local variable + ListAppend + CombineEntityActionMessages + direct assignment only.
```

### 2. `{Entity}_Upsert`

```
Input:  Source ({Entity} record, mandatory)
Output: EntityActionResult, Id ({Entity} Identifier)

Flow:
  1. Call {Entity}_Validate(Source)
  2. If {Entity}_Validate.EntityActionResult.IsSuccess  [label: "Valid?"]
     False → Assign EntityActionResult = {Entity}_Validate.EntityActionResult → End
     True  → continues

  3. If Source.Id = NullIdentifier()  [label: "New record?"]
     CREATE path:
       Assign Source.CreatedOn = CurrDateTime()
       Assign Source.CreatedByUserId = Session_GetNormalizedSessionUserId()
       Assign Source.UpdatedOn = Source.CreatedOn        ← copy, not new CurrDateTime()
       Assign Source.UpdatedByUserId = Source.CreatedByUserId  ← copy
       Assign Source.IsActive = True
       Call Create{Entity}(Source)
       Assign Id = Create{Entity}.Id
     UPDATE path:
       Assign Source.UpdatedOn = CurrDateTime()
       Assign Source.UpdatedByUserId = Session_GetNormalizedSessionUserId()
       Call Update{Entity}(Source)
       Assign Id = Source.Id

  4. Call EntityActionResult_BuildFromSuccess(
       "{Entity} " + Chr(34) + Source.{NameField} + Chr(34) + " has been saved.")
  5. Assign EntityActionResult = BuildFromSuccess.EntityActionResult
  6. End

Exception Handlers:
  DatabaseException (AbortTransaction = Yes) → EntityActionResult_BuildFromError(
    "An error has occurred. Please see a system administrator.")
    Assign EntityActionResult = result → End
  AllExceptions (AbortTransaction = No) → EntityActionResult_BuildFromError(
    AllExceptions.ExceptionMessage)
    Assign EntityActionResult = result → End

IMPORTANT:
- Use separate Create{Entity} and Update{Entity} — NOT CreateOrUpdate{Entity}.
- On create, UpdatedOn = Source.CreatedOn (copy), NOT a second CurrDateTime() call.
- UpdatedByUserId = Source.CreatedByUserId (copy) on create path.
- Session_GetNormalizedSessionUserId() MUST be called inline inside the assign expression — do NOT add a separate action call node before the assign widget.
- AllExceptions handler MUST have AbortTransaction = No.
- Must include both exception handlers.
```

### 3. `{Entity}_GetCanRemove`

```
Input:  Id ({Entity} Identifier, mandatory)
Output: EntityActionResult

Flow:
  1. Aggregate GetById: fetch {Entity} where {Entity}.Id = Id, MaxRecords = 1
  2. If GetById.List.Current.{Entity}.Id = NullIdentifier()  [label: "Exists?"]
     True  (not found) → Call EntityActionResult_BuildFromError(
                             "Cannot remove an unsaved {Entity}.")
                          Assign EntityActionResult = result → End
     False (found)     → continues
  3. If GetById.List.Current.{Entity}.IsActive  [label: "IsActive?"]
     True  → Call EntityActionResult_BuildFromSuccess("")
             Assign EntityActionResult = result → End
     False → Call EntityActionResult_BuildFromError(
               "Cannot remove {Entity} " + Chr(34) +
               GetById.List.Current.{Entity}.{NameField} +
               Chr(34) + ", it is already removed.")
             Assign EntityActionResult = result → End

Exception Handler:
  DatabaseException → Raise ProcessingException(
    "An error has occurred. Please see a system administrator.")

IMPORTANT: Use an Aggregate (not the built-in Get{Entity} entity action).
Include the record's name in the "already removed" error message.
```

### 4. `{Entity}_Remove`

```
Input:  Id ({Entity} Identifier, mandatory)
Output: EntityActionResult

Flow:
  1. Call {Entity}_GetCanRemove(Id)
  2. If {Entity}_GetCanRemove.EntityActionResult.IsSuccess  [label: "Can Remove?"]
     False → Raise ProcessingException(
               {Entity}_GetCanRemove.EntityActionResult.CombinedEntityMessageText)
             ← RAISE, do NOT return EntityActionResult with IsSuccess=False

  3. Call Get{Entity}ForUpdate(Id)   ← locks record for update
  4. Assign Get{Entity}ForUpdate.Record.{Entity}.UpdatedOn = CurrDateTime()
     Assign Get{Entity}ForUpdate.Record.{Entity}.UpdatedByUserId = Session_GetNormalizedSessionUserId()
     Assign Get{Entity}ForUpdate.Record.{Entity}.IsActive = False
  5. Call Update{Entity}(Get{Entity}ForUpdate.Record.{Entity})
             ← pass the entity record (.Record.{Entity}), NOT .Record alone
  6. Call EntityActionResult_BuildFromSuccess(
       "{Entity} " + Chr(34) + Get{Entity}ForUpdate.Record.{Entity}.{NameField} +
       Chr(34) + " has been removed.")
  7. Assign EntityActionResult = BuildFromSuccess.EntityActionResult
  8. End

Exception Handlers:
  DatabaseException (AbortTransaction = Yes) → EntityActionResult_BuildFromError(
    "An error has occurred. Please see a system administrator.")
    Assign EntityActionResult = result → End
  AllExceptions (AbortTransaction = No) → EntityActionResult_BuildFromError(
    AllExceptions.ExceptionMessage)
    Assign EntityActionResult = result → End

IMPORTANT:
- When GetCanRemove fails → RAISE ProcessingException, do NOT return failure result.
- Row-lock action is Get{Entity}ForUpdate — NOT GetForUpdate{Entity} (wrong order).
- Assign fields on Get{Entity}ForUpdate.Record.{Entity}, not on a separate Source variable.
- Pass Get{Entity}ForUpdate.Record.{Entity} to Update{Entity} — NOT .Record alone.
- Session_GetNormalizedSessionUserId() MUST be called inline inside the assign expression — do NOT add a separate action call node before the assign widget.
- AllExceptions handler MUST have AbortTransaction = No.
- Must include both exception handlers.
```

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Folder | `{Entity}` (same as entity name) | `SampleEntity` |
| Validate | `{Entity}_Validate` | `SampleEntity_Validate` |
| Upsert | `{Entity}_Upsert` | `SampleEntity_Upsert` |
| CanRemove check | `{Entity}_GetCanRemove` | `SampleEntity_GetCanRemove` |
| Remove (soft-delete) | `{Entity}_Remove` | `SampleEntity_Remove` |
| Row-lock action | `Get{Entity}ForUpdate` | `GetSampleEntityForUpdate` |
| Input record param | `Source` | `Source` (always) |
| ID input param | `Id` | `Id` (always) |
| ID output param | `Id` | `Id` (always) |
| Validate aggregate | `GetById` | `GetById` (always, in GetCanRemove) |

All 4 server actions must be placed inside a folder named exactly `{Entity}` (e.g. all `Employee_*` actions go in folder `Employee`).

## Mentor Prompt Template

```
Create CRUD wrapper server actions for the {EntityName} entity following the
ModelApplication SampleEntity pattern exactly.

Place all 4 server actions inside a folder named exactly `{EntityName}`.

Entity business fields: {list fields with type/mandatory/max-length}
Standard audit fields (Id, IsActive, CreatedByUserId, CreatedOn, UpdatedByUserId,
UpdatedOn) are already on the entity.

Create these 4 server actions with the descriptions specified:

1. {EntityName}_Validate
   Description: "Validates the {EntityName} record fields. Returns EntityActionResult
   with IsSuccess=False and accumulated error messages if any validation rules fail."
   Input: Source ({EntityName} record, mandatory).
   Output: EntityActionResult.
   Local variable: NewMessage (EntityActionMessage).
   For each mandatory business field: assign NewMessage.MessageTypeId = Entities.MessageType.Error
   and NewMessage.MessageText = "FieldName is required.", then ListAppend NewMessage to
   EntityActionResult.EntityActionMessages. Also check max-length constraints the same way.
   Then: if EntityActionResult.EntityActionMessages.Empty → set EntityActionResult.IsSuccess=True.
   Else → call EntityActionResult_CombineEntityActionMessages and set IsSuccess=False,
   CombinedEntityMessageText, CombinedEntityActionMessageTypeId from its output.
   Do NOT use BuildFromError or BuildFromSuccess inside Validate.

2. {EntityName}_Upsert
   Description: "Creates or updates a {EntityName} record after validation. Returns
   EntityActionResult and the Id of the saved record."
   Input: Source ({EntityName} record, mandatory).
   Output: EntityActionResult + Id ({EntityName} Identifier).
   Call _Validate first; if not IsSuccess assign EntityActionResult from it and End.
   If Source.Id = NullIdentifier(): set CreatedOn=CurrDateTime(), CreatedByUserId=
   Session_GetNormalizedSessionUserId(), UpdatedOn=Source.CreatedOn (copy),
   UpdatedByUserId=Source.CreatedByUserId (copy), IsActive=True, then call
   Create{EntityName}(Source) and assign Id = Create{EntityName}.Id.
   Else: set UpdatedOn=CurrDateTime(), UpdatedByUserId=Session_GetNormalizedSessionUserId(),
   call Update{EntityName}(Source), assign Id=Source.Id.
   Both paths: call EntityActionResult_BuildFromSuccess with message
   "{EntityName} " + Chr(34) + Source.{NameField} + Chr(34) + " has been saved.",
   then assign EntityActionResult from it.
   Add DatabaseException handler (AbortTransaction=Yes) → BuildFromError("An error has occurred.
   Please see a system administrator.") and AllExceptions handler (AbortTransaction=No) →
   BuildFromError(AllExceptions.ExceptionMessage).

3. {EntityName}_GetCanRemove
   Description: "Checks whether the {EntityName} record is eligible for soft-deletion.
   Returns EntityActionResult with IsSuccess=True if removal is allowed."
   Input: Id ({EntityName} Identifier, mandatory).
   Output: EntityActionResult.
   Use an Aggregate named GetById filtering {EntityName}.Id = Id, MaxRecords=1.
   If GetById.List.Current.{EntityName}.Id = NullIdentifier() → call BuildFromError(
   "Cannot remove an unsaved {EntityName}.") and assign EntityActionResult from it.
   Else if GetById.List.Current.{EntityName}.IsActive → call BuildFromSuccess("") and assign.
   Else → call BuildFromError("Cannot remove {EntityName} " + Chr(34) +
   GetById.List.Current.{EntityName}.{NameField} + Chr(34) + ", it is already removed.")
   and assign.
   Add DatabaseException handler that raises ProcessingException(
   "An error has occurred. Please see a system administrator.").

4. {EntityName}_Remove
   Description: "Soft-deletes the {EntityName} record by setting IsActive=False and
   updating audit fields. Raises ProcessingException if the record cannot be removed."
   Input: Id ({EntityName} Identifier, mandatory).
   Output: EntityActionResult.
   Call _GetCanRemove; if not IsSuccess → Raise ProcessingException(
   CombinedEntityMessageText) — do NOT return EntityActionResult.
   Call Get{EntityName}ForUpdate(Id). Assign UpdatedOn=CurrDateTime(),
   UpdatedByUserId=Session_GetNormalizedSessionUserId(), IsActive=False on
   Get{EntityName}ForUpdate.Record.{EntityName}. Call Update{EntityName}(
   Get{EntityName}ForUpdate.Record.{EntityName}) — pass the entity record, not .Record alone.
   Call BuildFromSuccess("{EntityName} " + Chr(34) +
   Get{EntityName}ForUpdate.Record.{EntityName}.{NameField} + Chr(34) + " has been removed.")
   and assign EntityActionResult from it.
   Add DatabaseException (AbortTransaction=Yes) and AllExceptions (AbortTransaction=No)
   handlers → BuildFromError as above.

All shared helpers (EntityActionResult_BuildFromSuccess, BuildFromError,
CombineEntityActionMessages, Session_GetNormalizedSessionUserId) already exist in the app.
Session_GetNormalizedSessionUserId is marked as a Function and must be called inline
in assignment expressions (not as a separate action call node in the flow).
```

## Auto-Layout (required after creation)

After the 4 actions are created, run a **second mentor turn** (resume same session) to auto-position all nodes in each action:

```
Auto-position all flow nodes in each of these actions so the layout is clean
and readable: {EntityName}_Validate, {EntityName}_Upsert,
{EntityName}_GetCanRemove, {EntityName}_Remove.

Do not change any logic, connections, inputs, outputs, or expressions —
only reposition the nodes.
```

Then publish.

## Edge Cases

| Scenario | Handling |
|---|---|
| External/Snowflake entity | Remove and Upsert may not support Create/Update — use SQL-style CreateOnly + UpdateOnly; no audit fields unless added in ODC Studio |
| Entity without IsActive | Skip GetCanRemove; Remove performs hard delete |
| Entity with Text PK (not Long Integer) | Upsert cannot use NullIdentifier() to detect new — caller must pass explicit flag or check by querying |
| All-optional business fields | Validate still created; ListAppend blocks may be empty; CombineMessages still called on non-empty list |
| Entity already has CreatedOn/UpdatedOn | Confirm field names match exactly; OutSystems is case-sensitive |
| Adding audit fields to entity with existing data | Handled by Pre-flight Check — always adds as IsMandatory=False with safe defaults. Never add mandatory audit fields without defaults on populated tables; triggers OS-DPL-50205 at publish. |
| App also references Snowflake/external entities | Publish may fail with OS-DPL-50205 if Snowflake external connection not configured in target stage. Fix in ODC Portal → Configurations → [Stage]. Verify via context_actions instead of publish result. |

## Verification Checklist

After mentor run, confirm via `context_actions` and mentor inspection:
- [ ] Pre-flight run: entity fields verified (or added as IsMandatory=False with safe defaults)
- [ ] Pre-flight run: shared infrastructure confirmed present before CRUD actions created
- [ ] `ProcessingException` user exception exists in the app
- [ ] `EntityActionResult_*` helpers are inside folder `EntityActionResult`
- [ ] `Session_GetNormalizedSessionUserId` is inside folder `Session`
- [ ] All 4 actions are inside a folder named `{Entity}`
- [ ] 4 actions exist: `_Validate`, `_Upsert`, `_GetCanRemove`, `_Remove`
- [ ] All 4 actions have non-empty descriptions (`rules/descriptions.md`)
- [ ] `_Upsert` has `Source` input + `EntityActionResult` output + `Id` output
- [ ] `_Upsert` uses `Create{Entity}` + `Update{Entity}` separately (not `CreateOrUpdate`)
- [ ] `_Upsert` has DatabaseException (AbortTransaction=Yes) + AllExceptions (AbortTransaction=No) handlers
- [ ] `_Validate` uses NewMessage local variable + `ListAppend` + `CombineEntityActionMessages` (NOT BuildFromError/BuildFromSuccess)
- [ ] `_GetCanRemove` uses an Aggregate named `GetById` (not entity Get action)
- [ ] `_Remove` raises `ProcessingException` on GetCanRemove failure (not returns EntityActionResult)
- [ ] `_Remove` uses `Get{Entity}ForUpdate` (NOT `GetForUpdate{Entity}`)
- [ ] `_Remove` passes `Get{Entity}ForUpdate.Record.{Entity}` to `Update{Entity}` (NOT `.Record` alone)
- [ ] `_Remove` has DatabaseException (AbortTransaction=Yes) + AllExceptions (AbortTransaction=No) handlers
- [ ] `Session_GetNormalizedSessionUserId()` called inline in assign expressions in `_Upsert` and `_Remove` — no separate call node before the assign widget
- [ ] All 4 actions have been auto-positioned (clean, readable layout)
- [ ] 0 errors in validation (warnings for unused actions are expected)
