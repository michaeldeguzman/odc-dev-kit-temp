# Mentor co-pilot — {{task_or_workflow_name}}

- **Run ID:** `{{run_id}}`
- **App:** `{{app_key}}`
- **Status:** `{{status}}`
- **Generated:** {{timestamp}}
- **Task:** `{{task_id}}` — {{task_description}}

## Prompt used

```
{{resolved_prompt}}
```

## Mentor response

{{response_body}}

## Publish handoff

_(rendered only when Mentor returns a refreshed session token)_

Mentor produced changes. To commit them, call `publish_start` with the refreshed `mentor_session_token` below. To discard, do nothing — the session expires server-side.

```json
{
  "tool": "mcp__outsystems__publish_start",
  "args": {
    "app_key": "{{app_key}}",
    "mentor_session_token": "{{session_token}}"
  }
}
```
