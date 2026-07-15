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
- `Session_GetNormalizedSessionUserId()` → `NormalizedSessionUserId: User Identifier`

If any of these don't exist in the target app, create them first by referencing ModelApplication or recreating the pattern.

## The 4 CRUD Actions

### 1. `{Entity}_Validate`
```
Input:  Source ({Entity} record, mandatory)
Output: EntityActionResult

Logic:
  - Check each mandatory business field is not empty/default
  - For each violation: add EntityActionMessage (MessageType=Error, text describing issue)
  - If any errors: EntityActionResult_BuildFromError
  - If all valid:  EntityActionResult_BuildFromSuccess
```

### 2. `{Entity}_Upsert`
```
Input:  Source ({Entity} record, mandatory)
Output: EntityActionResult, Id ({Entity} Identifier)

Logic:
  1. Call {Entity}_Validate(Source) → if not IsSuccess, return that result
  2. Call Session_GetNormalizedSessionUserId() → UserId
  3. If Source.Id = NullIdentifier({Entity}):
       - Set Source.CreatedByUserId = UserId
       - Set Source.CreatedOn = CurrDateTime()
       - Set Source.IsActive = True
     Else:
       - Get existing record to preserve CreatedBy/CreatedOn
  4. Set Source.UpdatedByUserId = UserId
  5. Set Source.UpdatedOn = CurrDateTime()
  6. CreateOrUpdate{Entity}(Source) → Id
  7. EntityActionResult_BuildFromSuccess("Record saved successfully")
```

### 3. `{Entity}_GetCanRemove`
```
Input:  Id ({Entity} Identifier, mandatory)
Output: EntityActionResult

Logic:
  - Get{Entity}(Id) → Record
  - If Record.IsActive = False OR Id = NullIdentifier({Entity}):
      EntityActionResult_BuildFromError("Record is already inactive or not found")
  - Else:
      EntityActionResult_BuildFromSuccess("{Entity} can be removed")
```

### 4. `{Entity}_Remove`
```
Input:  Id ({Entity} Identifier, mandatory)
Output: EntityActionResult

Logic:
  1. Call {Entity}_GetCanRemove(Id) → if not IsSuccess, return that result
  2. GetForUpdate{Entity}(Id) → Record
  3. Set Record.IsActive = False
  4. Set Record.UpdatedByUserId = Session_GetNormalizedSessionUserId()
  5. Set Record.UpdatedOn = CurrDateTime()
  6. Update{Entity}(Record)
  7. EntityActionResult_BuildFromSuccess("{Entity} removed successfully")
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

## Mentor Prompt Template

When invoking mentor to create this wrapper, use:

```
Create CRUD wrapper server actions for the {EntityName} entity following the ModelApplication SampleEntity pattern:

Entity has these business fields: {list fields with type/mandatory}
Standard audit fields (Id, IsActive, CreatedByUserId, CreatedOn, UpdatedByUserId, UpdatedOn) are already on the entity.

Create these 4 server actions:

1. {EntityName}_Validate — Input: Source ({EntityName} record, mandatory). Output: EntityActionResult.
   Validate all mandatory business fields. Use EntityActionResult_BuildFromError/BuildFromSuccess helpers.

2. {EntityName}_Upsert — Input: Source ({EntityName} record, mandatory). Output: EntityActionResult + Id ({EntityName} Identifier).
   Call _Validate first. Set audit fields via Session_GetNormalizedSessionUserId() and CurrDateTime(). Use CreateOrUpdate{EntityName}.

3. {EntityName}_GetCanRemove — Input: Id ({EntityName} Identifier, mandatory). Output: EntityActionResult.
   Check record exists and IsActive=True.

4. {EntityName}_Remove — Input: Id ({EntityName} Identifier, mandatory). Output: EntityActionResult.
   Call _GetCanRemove first. Set IsActive=False, update audit fields, call Update{EntityName}.

All actions return EntityActionResult using the BuildFromSuccess/BuildFromError helpers already in the app.
```

## Edge Cases

| Scenario | Handling |
|---|---|
| External/Snowflake entity | Remove and Upsert may not support CreateOrUpdate — use SQL-style CreateOnly + UpdateOnly; no audit fields unless added in ODC studio |
| Entity without IsActive | Skip GetCanRemove; Remove performs hard delete |
| Entity with Text PK (not Long Integer) | Upsert cannot use NullIdentifier() to detect new — caller must pass explicit flag or check by querying |
| All-optional business fields | Validate action still created but may always succeed |
| Entity already has CreatedOn/UpdatedOn | Confirm field names match exactly; OutSystems is case-sensitive |
| Adding audit fields to entity with existing data | Make audit fields optional (IsMandatory=False) with safe defaults (IsActive=True, DateTime fields=#1900-01-01 00:00:00#). Mandatory fields without defaults on existing tables trigger OS-DPL-50205 at publish time. User Identifier audit fields (CreatedByUserId, UpdatedByUserId) need no default — just set IsMandatory=False. |
| App also references Snowflake/external entities | Publish will fail with OS-DPL-50205 if the Snowflake external connection isn't configured in the target stage. Fix in ODC Portal → Configurations → [Stage] → verify connection is active. Unrelated to CRUD wrapper correctness — verify OML via context_actions instead. |

## Verification Checklist

After mentor run, confirm via `context_actions`:
- [ ] 4 actions exist: `_Validate`, `_Upsert`, `_GetCanRemove`, `_Remove`
- [ ] `_Upsert` has `Source` input + `EntityActionResult` output + `Id` output
- [ ] `_Remove` and `_GetCanRemove` have `Id` input + `EntityActionResult` output
- [ ] `_Validate` has `Source` input + `EntityActionResult` output
- [ ] 0 errors in validation (warnings for unused actions are expected)
