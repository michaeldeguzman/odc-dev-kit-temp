---
name: odc-crud-wrapper
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

**Helper Server Actions:**
- `EntityActionResult_BuildFromSuccess(EntityActionResultMessageText: Text)` → `EntityActionResult`
- `EntityActionResult_BuildFromError(EntityActionResultMessageText: Text)` → `EntityActionResult`
- `EntityActionResult_CombineEntityActionMessages(EntityActionMessages: EntityActionMessage List)` → `CombinedEntityActionMessageTypeId`, `CombinedEntityActionMessageText`
- `Session_GetNormalizedSessionUserId()` → `NormalizedSessionUserId: User Identifier` — **must be marked as Function** (ODC "Function" toggle = True) so it can be called inline in assignment expressions

If any of these don't exist in the target app, create them first by referencing ModelApplication or recreating the pattern.

## The 4 CRUD Actions

### 1. `{Entity}_Validate`

```
Input:  Source ({Entity} record, mandatory)
Output: EntityActionResult

Flow:
  1. For each mandatory business field (e.g. Name):
     a. If Source.FieldName = "" (or default/empty):
        ListAppend to EntityActionResult.EntityActionMessages:
          { MessageText: "FieldName is required.", MessageTypeId: Entities.MessageType.Error }
     b. If Length(Source.FieldName) > MaxLength:
        ListAppend to EntityActionResult.EntityActionMessages:
          { MessageText: "FieldName cannot be longer than N characters.", MessageTypeId: Entities.MessageType.Error }

  2. If EntityActionResult.EntityActionMessages.Empty  [label: "Valid?"]
     True  → Assign EntityActionResult.IsSuccess = True → End
     False → Call EntityActionResult_CombineEntityActionMessages(EntityActionResult.EntityActionMessages)
             Assign EntityActionResult.IsSuccess = False
             Assign EntityActionResult.CombinedEntityMessageText = CombineResult.CombinedEntityActionMessageText
             Assign EntityActionResult.CombinedEntityActionMessageTypeId = CombineResult.CombinedEntityActionMessageTypeId
             → End

IMPORTANT: Do NOT call BuildFromError/BuildFromSuccess inside Validate.
Use ListAppend + CombineEntityActionMessages + direct assignment only.
```

### 2. `{Entity}_Upsert`

```
Input:  Source ({Entity} record, mandatory)
Output: EntityActionResult, Id ({Entity} Identifier)

Flow:
  1. Call {Entity}_Validate(Source)
  2. If NOT SampleEntity_Validate.EntityActionResult.IsSuccess  [label: "Valid?"]
     → Assign EntityActionResult = {Entity}_Validate.EntityActionResult → End

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

  4. Assign EntityActionResult = EntityActionResult_BuildFromSuccess(
       "{Entity} """ + Source.{NameField} + """ has been saved.")
  5. End

Exception Handlers:
  DatabaseException → EntityActionResult = EntityActionResult_BuildFromError(
    "An error has occurred. Please see a system administrator.") → End
  AllExceptions     → EntityActionResult = EntityActionResult_BuildFromError(
    AllExceptions.ExceptionMessage) → End

IMPORTANT:
- Use separate Create{Entity} and Update{Entity} — NOT CreateOrUpdate{Entity}.
- On create, UpdatedOn = Source.CreatedOn (copy), NOT a second CurrDateTime() call.
- UpdatedByUserId = Source.CreatedByUserId (copy) on create path.
- Must include both exception handlers.
```

### 3. `{Entity}_GetCanRemove`

```
Input:  Id ({Entity} Identifier, mandatory)
Output: EntityActionResult

Flow:
  1. Aggregate GetById: fetch {Entity} where {Entity}.Id = Id, MaxRecords = 1
  2. If GetById.List.Current.{Entity}.Id = NullIdentifier()  [record exists?]
     → EntityActionResult = EntityActionResult_BuildFromError(
         "Cannot remove an unsaved {Entity}.") → End
  3. If GetById.List.Current.{Entity}.IsActive  [still active?]
     True  → EntityActionResult = EntityActionResult_BuildFromSuccess("") → End
     False → EntityActionResult = EntityActionResult_BuildFromError(
               "Cannot remove {Entity} """ + GetById.List.Current.{Entity}.{NameField} +
               """, it is already removed.") → End

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
  2. If NOT {Entity}_GetCanRemove.EntityActionResult.IsSuccess
     → Raise ProcessingException(
         {Entity}_GetCanRemove.EntityActionResult.CombinedEntityMessageText)
       ← RAISE, do NOT return EntityActionResult with IsSuccess=False

  3. Call GetForUpdate{Entity}(Id)   ← locks record for update
  4. Assign GetForUpdate{Entity}.Record.{Entity}.UpdatedOn = CurrDateTime()
     Assign GetForUpdate{Entity}.Record.{Entity}.UpdatedByUserId = Session_GetNormalizedSessionUserId()
     Assign GetForUpdate{Entity}.Record.{Entity}.IsActive = False
  5. Call Update{Entity}(GetForUpdate{Entity}.Record)
  6. Assign EntityActionResult = EntityActionResult_BuildFromSuccess(
       "{Entity} """ + GetForUpdate{Entity}.Record.{Entity}.{NameField} +
       """ has been removed.")
  7. End

Exception Handlers:
  DatabaseException → EntityActionResult = EntityActionResult_BuildFromError(
    "An error has occurred. Please see a system administrator.") → End
  AllExceptions     → EntityActionResult = EntityActionResult_BuildFromError(
    AllExceptions.ExceptionMessage) → End

IMPORTANT:
- When GetCanRemove fails → RAISE ProcessingException, do NOT return failure result.
- Use GetForUpdate{Entity} (locks the row) — not GetById aggregate.
- Assign fields on GetForUpdate{Entity}.Record.{Entity}, not on Source.
- Must include both exception handlers.
```

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Validate | `{Entity}_Validate` | `SampleEntity_Validate` |
| Upsert | `{Entity}_Upsert` | `SampleEntity_Upsert` |
| CanRemove check | `{Entity}_GetCanRemove` | `SampleEntity_GetCanRemove` |
| Remove (soft-delete) | `{Entity}_Remove` | `SampleEntity_Remove` |
| Input record param | `Source` | `Source` (always) |
| ID input param | `Id` | `Id` (always) |
| ID output param | `Id` | `Id` (always) |
| Validate aggregate | `GetById` | `GetById` (always, in GetCanRemove) |

## Mentor Prompt Template

```
Create CRUD wrapper server actions for the {EntityName} entity following the
ModelApplication SampleEntity pattern exactly.

Entity business fields: {list fields with type/mandatory/max-length}
Standard audit fields (Id, IsActive, CreatedByUserId, CreatedOn, UpdatedByUserId,
UpdatedOn) are already on the entity.

Create these 4 server actions:

1. {EntityName}_Validate — Input: Source ({EntityName} record, mandatory).
   Output: EntityActionResult.
   For each mandatory business field, use ListAppend to append an EntityActionMessage
   { MessageText: "FieldName is required.", MessageTypeId: Entities.MessageType.Error }
   to EntityActionResult.EntityActionMessages. Also check max-length constraints.
   Then: if EntityActionResult.EntityActionMessages.Empty → set EntityActionResult.IsSuccess=True.
   Else → call EntityActionResult_CombineEntityActionMessages and set IsSuccess=False,
   CombinedEntityMessageText, CombinedEntityActionMessageTypeId from its output.
   Do NOT use BuildFromError or BuildFromSuccess inside Validate.

2. {EntityName}_Upsert — Input: Source ({EntityName} record, mandatory).
   Output: EntityActionResult + Id ({EntityName} Identifier).
   Call _Validate first; if not IsSuccess assign EntityActionResult from it and End.
   If Source.Id = NullIdentifier(): set CreatedOn=CurrDateTime(), CreatedByUserId=
   Session_GetNormalizedSessionUserId(), UpdatedOn=Source.CreatedOn (copy),
   UpdatedByUserId=Source.CreatedByUserId (copy), IsActive=True, then call
   Create{EntityName}(Source) and assign Id = Create{EntityName}.Id.
   Else: set UpdatedOn=CurrDateTime(), UpdatedByUserId=Session_GetNormalizedSessionUserId(),
   call Update{EntityName}(Source), assign Id=Source.Id.
   Both paths: EntityActionResult = EntityActionResult_BuildFromSuccess(
   "{EntityName} """ + Source.{NameField} + """ has been saved.").
   Add DatabaseException handler → BuildFromError("An error has occurred. Please see
   a system administrator.") and AllExceptions handler → BuildFromError(ExceptionMessage).

3. {EntityName}_GetCanRemove — Input: Id ({EntityName} Identifier, mandatory).
   Output: EntityActionResult.
   Use an Aggregate (named GetById) filtering {EntityName}.Id = Id, MaxRecords=1.
   If GetById.List.Current.{EntityName}.Id = NullIdentifier() → BuildFromError(
   "Cannot remove an unsaved {EntityName}.").
   Else if GetById.List.Current.{EntityName}.IsActive → BuildFromSuccess("").
   Else → BuildFromError("Cannot remove {EntityName} """ + Name + """, it is already removed.").
   Add DatabaseException handler that raises ProcessingException(
   "An error has occurred. Please see a system administrator.").

4. {EntityName}_Remove — Input: Id ({EntityName} Identifier, mandatory).
   Output: EntityActionResult.
   Call _GetCanRemove; if not IsSuccess → Raise ProcessingException(
   CombinedEntityMessageText) — do NOT return EntityActionResult.
   Call GetForUpdate{EntityName}(Id). Assign UpdatedOn=CurrDateTime(),
   UpdatedByUserId=Session_GetNormalizedSessionUserId(), IsActive=False on
   GetForUpdate{EntityName}.Record.{EntityName}. Call Update{EntityName}(Record).
   EntityActionResult = BuildFromSuccess("{EntityName} """ + Record.Name +
   """ has been removed.").
   Add DatabaseException and AllExceptions handlers → BuildFromError.

All shared helpers (EntityActionResult_BuildFromSuccess, BuildFromError,
CombineEntityActionMessages, Session_GetNormalizedSessionUserId) already exist in the app.
Session_GetNormalizedSessionUserId is marked as a Function and must be called inline
in assignment expressions (not as a separate action call node in the flow).
```

## Edge Cases

| Scenario | Handling |
|---|---|
| External/Snowflake entity | Remove and Upsert may not support Create/Update — use SQL-style CreateOnly + UpdateOnly; no audit fields unless added in ODC Studio |
| Entity without IsActive | Skip GetCanRemove; Remove performs hard delete |
| Entity with Text PK (not Long Integer) | Upsert cannot use NullIdentifier() to detect new — caller must pass explicit flag or check by querying |
| All-optional business fields | Validate still created; ListAppend blocks may be empty; CombineMessages still called on non-empty list |
| Entity already has CreatedOn/UpdatedOn | Confirm field names match exactly; OutSystems is case-sensitive |
| Adding audit fields to entity with existing data | Make audit fields optional (IsMandatory=False) with safe defaults (IsActive=True, DateTime fields=#1900-01-01 00:00:00#). Mandatory fields without defaults on existing tables trigger OS-DPL-50205 at publish time. User Identifier audit fields need no default — just set IsMandatory=False. |
| App also references Snowflake/external entities | Publish may fail with OS-DPL-50205 if Snowflake external connection not configured in target stage. Fix in ODC Portal → Configurations → [Stage]. Verify via context_actions instead of publish result. |

## Verification Checklist

After mentor run, confirm via `context_actions` and mentor inspection:
- [ ] 4 actions exist: `_Validate`, `_Upsert`, `_GetCanRemove`, `_Remove`
- [ ] `_Upsert` has `Source` input + `EntityActionResult` output + `Id` output
- [ ] `_Upsert` uses `Create{Entity}` + `Update{Entity}` separately (not `CreateOrUpdate`)
- [ ] `_Upsert` has DatabaseException + AllExceptions handlers
- [ ] `_Validate` uses `ListAppend` + `CombineEntityActionMessages` (NOT BuildFromError/BuildFromSuccess)
- [ ] `_GetCanRemove` uses an Aggregate named `GetById` (not entity Get action)
- [ ] `_Remove` raises `ProcessingException` on GetCanRemove failure (not returns EntityActionResult)
- [ ] `_Remove` uses `GetForUpdate{Entity}` (not aggregate)
- [ ] `_Remove` has DatabaseException + AllExceptions handlers
- [ ] 0 errors in validation (warnings for unused actions are expected)
