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

## Skills (`.claude/skills/`)

Project-scoped — Claude Code auto-discovers these from `.claude/skills/<name>/SKILL.md` on every clone. No manual install step.

### `dbresults-odc-crud-wrapper`

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

### `dbresults-odc-catchup`

Recaps current app state at session start — reads `CLAUDE.md` build history and calls `context_actions` / `context_entities` to show what's deployed.

### `dbresults-odc-ship`

Handles the full mentor → publish → deploy flow, including `no_changes_detected` verification and `CLAUDE.md` build log update.

### `dbresults-odc-scaffold-entity`

Full-stack scaffold for one entity: the same 4-action CRUD layer as `dbresults-odc-crud-wrapper`, plus a searchable/sortable/paginated list screen and a create/edit detail screen wired to those actions. Use `dbresults-odc-crud-wrapper` instead if you only need the server actions.

**Invoke:**
```
Scaffold <EntityName>
```

### dbresults-skills catalog (`outsystems-*`)

Vendored from [dbresults/dbresults-skills](https://github.com/dbresults/dbresults-skills) (MIT, prototype/R&D status — see [docs/dbresults-skills/CATALOG-README.md](docs/dbresults-skills/CATALOG-README.md)). 12 skills covering explore/build/operate workflows on top of the `outsystems` MCP server:

| Skill | Category | What it produces |
|---|---|---|
| `outsystems-tenant-architecture` | Explore | Interactive HTML graph of every asset in the tenant |
| `outsystems-app-architecture` | Explore | Interactive HTML graph of one app's screens/actions/entities/roles |
| `outsystems-ai-agent-landscape` | Explore | HTML dashboard of every AI agent + model connection |
| `outsystems-dependency-impact` | Explore | Reverse-dependency explorer ("who breaks if I publish X?") |
| `outsystems-design-to-app` | Build | Figma/screenshot/mockup → working ODC app via Mentor |
| `outsystems-spec-driven-build` | Build | Text spec → new app via Mentor + guardrails |
| `outsystems-plan-to-mentor` | Build | Coverage-review a saved plan against its PRD, emit Mentor-ready prompts |
| `outsystems-mentor-copilot` | Build | 11-task library + 3 workflows on top of ODC Mentor |
| `outsystems-custom-code` | Build | C# External Logic library reference + workflow |
| `outsystems-deploy-preview` | Operate | HTML risk preview of a Dev→Test / Test→Prod promotion |
| `outsystems-app-documentation` | Operate | Markdown docs for one app (Confluence-ready) |
| `outsystems-mentor-polling-behavior` | Optional companion | Enforces Mentor polling discipline, tracks token telemetry |

Docs: [`docs/dbresults-skills/INTRO.md`](docs/dbresults-skills/INTRO.md) (plain-English overview), [`SKILL-INDEX.md`](docs/dbresults-skills/SKILL-INDEX.md) (which skill for which job), [`TRIGGER-MAP.md`](docs/dbresults-skills/TRIGGER-MAP.md) (disambiguation rules), [`CONVENTIONS.md`](docs/dbresults-skills/CONVENTIONS.md) (shared engineering rules).

> These are marked prototype/R&D by the upstream maintainer — not for customer-facing production work. `outsystems-design-to-app`'s Figma path additionally needs a separate Figma MCP server connected (`mcp__plugin_figma_figma__*` tools) — not required for its screenshot/HTML-mockup paths.

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
