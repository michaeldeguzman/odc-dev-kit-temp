---
name: odc-ship
description: Use when asked to publish, deploy, or ship an ODC app after mentor editing. Handles the full mentor→publish→deploy flow including no_changes_detected verification and CLAUDE.md update.
---

# ODC Ship

Publish current mentor session to Development and optionally promote to next stage.

## Prerequisites

- `mentor_session_id` + `mentor_session_token` from last terminal `mentor_get_run` result
- `env_key` for target environment
- App key from `PROJECT_CONFIG.md`

## Environments

Resolve `env_key` via `env_list`. Environment names and runtime URLs are in `PROJECT_CONFIG.md`.

## Publish Flow

1. **Confirm** — state planned change + target environment; wait for explicit user OK
2. `publish_start {mentor_session_id, mentor_session_token, env_key}`
3. Poll `publish_status` every 15s until terminal
4. **`no_changes_detected: true`** → do NOT report as success:
   - Call `context_actions` to verify actual deployed state
   - Report: "No new revision deployed — submitted OML matched current deployment. [N actions confirmed]"
5. **`succeeded`**:
   - Call `env_app {env_key, application_key: "<AppKey from PROJECT_CONFIG.md>"}` for runtime URL
   - Report revision + URL as markdown link
   - Update CLAUDE.md build log (see below)
6. **`failed`**:
   - Call `publish_logs {pub_key: operation_id}` — surface error codes verbatim
   - `OS-DPL-50205` = Snowflake/external connection not configured in stage → acceptable; verify OML via `context_actions` instead
   - `OS-BEW-*` / other `OS-DPL-*` = retries exhausted → surface code, investigate before re-publishing

## Deploy Flow (only when user asks to promote)

1. `deploy_start {asset_key, env_key: "<target>", from_env: "<source>"}`
2. Poll `deploy_status` every 10s until terminal
3. On failure: `deploy_messages {operation_key}` for diagnostics

## CLAUDE.md Build Log Update

After a confirmed new publish (not no_changes_detected), append row:

```markdown
| [description of what was built] | Rev N → N+1 | [notes] |
```

Under the current session's date heading in the table for this app.

## Rules

- Never call `publish_start` without explicit user confirmation in the current turn
- Consecutive publishes are serialized cluster-wide — do not re-publish while one is in progress
- `no_changes_detected` means nothing new deployed; always verify with `context_actions`
- Do not retry `failed` publishes blindly — read the error code first
