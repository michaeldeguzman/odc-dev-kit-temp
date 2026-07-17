# OutSystems MCP — Mentor Flow Reference

This skill drives app generation via the **OutSystems MCP server** (`mcp__outsystems__*` tools). Server-side OML editing through `mentor_start` / `mentor_get_run`, then `publish_start` to ship the build.

## Prerequisites

- `outsystems` MCP server connected in Claude Code (`mcp__outsystems__*` tools available)
- User authenticated — call `mcp__outsystems__auth_status` first; if expired, surface a re-auth prompt
- Target app exists in the OutSystems environment (use `app_list` to find it, or `app_create` to mint a new shell)

## Finding the App

```
app_list { search: "<app-name>" }
```

Returns `app_key` (UUID) — use this for all subsequent calls. If multiple results, confirm with the user before proceeding.

## Sending a Spec to Mentor

**First turn** — start a new editing session:

```
mentor_start {
  app_key: "<app-key-uuid>",
  prompt: "<SPEC_PREAMBLE><minified-spec-json>"
}
```

Returns a `runId`. OML editing happens entirely server-side.

### Cursor-based poll loop

```
# Step 1: Poll immediately after mentor_start (cursor = null for first call)
cursor = null

# Step 2: Loop until terminal
LOOP:
  result = mentor_get_run { runId: "<runId>", cursor: cursor }

  # result contains: { status, events[], cursor?, mentor_session_id?, mentor_session_token? }

  IF result.status is "SUCCESS":
    → DONE. Save result.mentor_session_id and result.mentor_session_token for resume/publish.
    → result.summary describes what the agent did.
    → BREAK loop.

  IF result.status is "ERROR" or "CANCELLED":
    → FAILED. Log result. BREAK loop.

  IF result.status is "RUNNING" or "PENDING":
    IF result.cursor != cursor:
      → Events arrived. Update cursor = result.cursor.
      → Poll again IMMEDIATELY (more events may be buffered).
    ELSE:
      → Cursor didn't advance — agent is still working, no new events yet.
      → Wait ~30 seconds, then poll again.
    → CONTINUE loop.
```

**Key rules:**
- Always pass the latest `cursor` from the previous response. `null` on first call.
- Poll immediately when cursor advances (events arrive in batches — drain them fast).
- Only pause ~30s when cursor is stalled and status is non-terminal.
- Don't bare-sleep — use the harness background-task mechanism (e.g., `run_in_background` in Claude Code).

**Terminal states:** `SUCCESS`, `ERROR`, `CANCELLED`

On `SUCCESS`, the response includes:
- `mentor_session_id` — identifies the session
- `mentor_session_token` — HMAC-signed token for resuming or publishing (echo back VERBATIM)
- `summary` — what the agent did
- `events` — cursor-paginated list of changes

### Follow-up turns — resume the same session

```
mentor_start {
  mentor_session_id: "<session-id>",
  mentor_session_token: "<token-from-last-success>",
  prompt: "<next-batch-spec-or-refinement>"
}
```

Always use the **newest** `mentor_session_token` from the most recent terminal-success `mentor_get_run`.

### Cancel a stuck session

```
mentor_cancel { runId: "<runId>" }
```

## Publishing After Edits

After all Mentor turns succeed:

```
publish_start {
  mentor_session_id: "<session-id>",
  mentor_session_token: "<latest-token>",
  env_key: "<target-environment-key>"
}
```

Returns `publication_id`. Poll with:

```
publish_status { publication_id: "<publication_id>" }
```

On `Completed`, follow up with `env_app` (reusing `env_key` + `application_key` from the publish call) to fetch the deployed runtime URL and report it to the user as a markdown link or bare URL — never wrap in backticks (disables terminal click-to-open).

On failure, get diagnostics:

```
publish_logs { pub_key: "<publication_id>" }
```

## Getting Context (optional — for validation)

Before or after Mentor edits, inspect the app:

```
# Run in parallel for speed:
context_screens  { app: "<app-name>" }
context_entities { app: "<app-name>" }
context_actions  { app: "<app-name>" }
context_themes   { app: "<app-name>" }
```

## Full Example

```
# 1. Find the app
app_list { search: "BankingPortal" }
# → app_key: "abc-123-def"

# 2. Send entities + roles batch
mentor_start { app_key: "abc-123-def", prompt: "<entities-spec>" }
# → runId: "run-1"
mentor_get_run { runId: "run-1" }
# → poll until SUCCESS → get session_id + token

# 3. Send screens batch (resume session)
mentor_start {
  mentor_session_id: "<session-id>",
  mentor_session_token: "<token>",
  prompt: "<screens-spec>"
}
# → runId: "run-2"
mentor_get_run { runId: "run-2" }
# → poll until SUCCESS → get updated token

# 4. Publish
publish_start {
  mentor_session_id: "<session-id>",
  mentor_session_token: "<latest-token>",
  env_key: "<env-key>"
}
publish_status { publication_id: "<pub-id>" }

# 5. Get the runtime URL
env_app { env_key: "<env-key>", application_key: "abc-123-def" }
# → render `url` as a markdown link to the user
```

## Error Handling

| Error category | Action |
|---|---|
| `AuthError` | Call `mcp__outsystems__auth_status`; if expired, surface re-auth to the user; then retry the original call ONCE |
| `ValidationError` | Fix the prompt/spec and retry |
| `UpstreamError` | Transient — wait and retry once |
| `InternalError` | Report to user, don't retry |

## Session Lifecycle Notes

- Sessions auto-GC after **30 minutes idle**. Resuming after GC transparently re-downloads the OML — same session continues.
- Always carry the **latest** `mentor_session_token` forward — each successful turn issues a fresh one.
- For long batches (entities → chrome → screens), keep the session alive by issuing the next batch immediately after the previous one succeeds.

## Spec Preamble (use verbatim)

Prepend to every Mentor batch prompt:

```
Implement the following spec COMPLETELY. Do NOT stop until every item in the
acceptance_checklist at the end of the spec is satisfied. After all code
executions, verify each acceptance_checklist item by reading the app state —
if any item fails, fix it before finishing. Here is the spec:
```

This preamble was derived from field-tested Mentor failures where the agent stopped mid-build or skipped acceptance items. Removing it re-introduces those failures.
