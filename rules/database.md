---
description: ODC data access and entity conventions. Apply when creating or modifying entities and server actions in OutSystems Developer Cloud apps.
---

# ODC Database / Data Access

## Soft Delete

- Never hard-delete entity records. Always soft-delete: `IsActive = False`
- `{Entity}_Remove` sets `IsActive = False` via `Update{Entity}` — it does not call `Delete{Entity}`
- All list aggregates must filter `{Entity}.IsActive = True` unless specifically querying inactive records

## CRUD Operations

- Use separate `Create{Entity}` and `Update{Entity}` — **never** `CreateOrUpdate{Entity}`
- Detect new vs existing in `_Upsert` via `Source.Id = NullIdentifier()`
- For row-lock before update in `_Remove`: use `GetForUpdate{Entity}(Id)` — not an aggregate

## Aggregates

- GetById-style lookups: set `MaxRecords = 1`
- In `{Entity}_GetCanRemove`: use an **Aggregate** named `GetById` filtering `{Entity}.Id = Id` — do not use the built-in `Get{Entity}` entity action
- Never leave `MaxRecords` uncapped on list aggregates in server actions — set an explicit limit

## Audit Fields

Every wrapped entity carries these 6 standard fields:

| Field | Set on Create | Set on Update |
|---|---|---|
| `CreatedOn` | `CurrDateTime()` | (never change) |
| `CreatedByUserId` | `Session_GetNormalizedSessionUserId()` | (never change) |
| `UpdatedOn` | Copy of `Source.CreatedOn` | `CurrDateTime()` |
| `UpdatedByUserId` | Copy of `Source.CreatedByUserId` | `Session_GetNormalizedSessionUserId()` |
| `IsActive` | `True` | (set to `False` on Remove only) |

- On create: `UpdatedOn = Source.CreatedOn` (copy) — NOT a second `CurrDateTime()` call
- On create: `UpdatedByUserId = Source.CreatedByUserId` (copy)
- `Session_GetNormalizedSessionUserId()` is marked as **Function** — call it **inline** inside the assign expression, never as a separate action call node in the flow

## Adding Audit Fields to Tables with Existing Data

When adding mandatory audit fields to a table that already has rows:

- Set `IsMandatory = False` for all audit fields initially; add safe defaults
- `IsActive`: default `True`; `DateTime` fields: default `#1900-01-01 00:00:00#`
- `User Identifier` fields: no default needed, just set `IsMandatory = False`
- Mandatory fields without defaults on existing tables trigger `OS-DPL-50205` at publish

## External / Snowflake Entities

- Publish may fail with `OS-DPL-50205` if Snowflake connection is not configured in the target stage
- Fix in ODC Portal → Configurations → [Stage] → configure external connection
- Verify OML correctness via `context_actions` rather than waiting for a clean publish
