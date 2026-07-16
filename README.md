# OutSystems MCP

Claude Code workspace template for building OutSystems Developer Cloud (ODC) apps via the OutSystems MCP HTTP transport.

## Starting a new project from this template

1. Clone this repo
2. Edit **`PROJECT_CONFIG.md`** — set your app name, app key, tenant, and runtime URL. That's the only file with project-specific values.
3. Register the OutSystems MCP server (replace `<tenant>` with your tenant from `PROJECT_CONFIG.md`):
   ```
   claude mcp add -s user --transport http --client-id service_studio --callback-port 7890 outsystems https://<tenant>.outsystems.dev/mcp
   ```
4. Authenticate when prompted (OAuth flow via browser)
5. Update `CLAUDE.md` — replace the build history with your own app's history

## Setup (existing project)

1. Install [Claude Code](https://claude.ai/claude-code)
2. Register the MCP server using the tenant in `PROJECT_CONFIG.md`
3. Authenticate when prompted

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

### `odc-catchup`

Recaps current app state at session start — reads `CLAUDE.md` build history and calls `context_actions` / `context_entities` to show what's deployed.

### `odc-ship`

Handles the full mentor → publish → deploy flow, including `no_changes_detected` verification and `CLAUDE.md` build log update.

## Target App

See [`PROJECT_CONFIG.md`](PROJECT_CONFIG.md) for the active app name, app key, tenant, and runtime URL.

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
