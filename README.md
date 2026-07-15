# OutSystems MCP

Claude Code workspace for building OutSystems Developer Cloud (ODC) apps via the OutSystems MCP HTTP transport.

## Setup

1. Install [Claude Code](https://claude.ai/claude-code)
2. Register the OutSystems MCP server:
   ```
   claude mcp add -s user --transport http --client-id service_studio --callback-port 7890 outsystems https://<tenant>.outsystems.dev/mcp
   ```
3. Authenticate when prompted (OAuth flow via browser)

## Skills

### `odc-crud-wrapper`

Generates the ModelApplication SampleEntity CRUD wrapper pattern for any ODC entity.

Creates 4 server actions per entity:

| Action | Description |
|---|---|
| `{Entity}_Validate` | Validates mandatory fields and length constraints using ListAppend + CombineEntityActionMessages |
| `{Entity}_Upsert` | Create or update with audit fields, soft-delete, and exception handlers |
| `{Entity}_GetCanRemove` | Checks record exists and is still active before removal |
| `{Entity}_Remove` | Soft-deletes the record (IsActive = False) with row lock |

**Conventions:**
- All 4 actions placed in a folder named `{Entity}`
- Shared infrastructure in dedicated folders: `EntityActionResult` (helpers) and `Session` (user helper)
- `Session_GetNormalizedSessionUserId` marked as Function — called inline in assign expressions, never as a separate call node
- Auto-layout applied after creation (second mentor turn)

**Invoke:**
```
Create CRUD wrapper for <EntityName>
```

## Test Application

**Test Anything** — `f464e3e1-4a26-4187-9d73-330de60ed791`  
Runtime: https://dbresults-rd-dev.outsystems.app/TestAnything  
Tenant: `dbresults-rd.outsystems.dev`

Entities with CRUD wrappers: `TestEntity`, `Employee`

## Shared Infrastructure (required before wrapping any entity)

| Element | Type |
|---|---|
| `EntityActionResult` | Structure |
| `EntityActionMessage` | Structure |
| `MessageType` | Static Entity (Success/Error/Warning/Info) |
| `EntityActionResult_BuildFromSuccess` | Server Action (folder: EntityActionResult) |
| `EntityActionResult_BuildFromError` | Server Action (folder: EntityActionResult) |
| `EntityActionResult_CombineEntityActionMessages` | Server Action (folder: EntityActionResult) |
| `Session_GetNormalizedSessionUserId` | Server Action — Function (folder: Session) |
| `ProcessingException` | User Exception |

## Build History

See [CLAUDE.md](CLAUDE.md) for full build history and session notes.
