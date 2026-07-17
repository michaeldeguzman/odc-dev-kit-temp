---
name: outsystems-mentor-polling-behavior
description: >
  Three modes. Mode 1 — token-efficient Mentor invocation: enforces correct
  operation-tier polling (Tier 1 sync / Tier 2 30s / Tier 3 30s cadence +
  cursor discipline), records per-poll telemetry silently, does NOT render HTML.
  Use for: "use Mentor on [app] to do X", "run Mentor on [app]",
  "have Mentor [do something] on [app]", "token-efficient Mentor session".
  Mode 2 — generate dashboard: renders the HTML from existing session data.
  Use for: "generate Mentor polling dashboard", "show my Mentor report",
  "generate the HTML", "render the dashboard".
  Mode 3 — summary and recommendations: reads all session data and produces
  a cross-session digest plus trend analysis.
  Use for: "Mentor polling summary", "summarise my Mentor sessions",
  "how is Mentor performing", "Mentor session trends", "give me recommendations".
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. No other system packages needed.
allowed-tools: AskUserQuestion Bash Write Edit mcp__outsystems__auth_status mcp__outsystems__app_list mcp__outsystems__app_info mcp__outsystems__mentor_start mcp__outsystems__mentor_get_run mcp__outsystems__mentor_cancel
metadata:
  version: "1.4.0"
  author: outsystems-r-and-d
---

# OutSystems Mentor Polling Behavior

Three modes — one skill.

**Mode 1 — Mentor invocation:** The correct way to run Mentor. Enforces
30s polling cadence, cursor discipline, and records per-poll telemetry.
The HTML dashboard is **not** rendered automatically — telemetry accumulates
silently and the dashboard is generated on demand (Mode 2).

**Mode 2 — Generate dashboard:** Renders `index.html` + per-session
`detail.html` from all accumulated session data. On demand only.

**Mode 3 — Summary + recommendations:** Reads all session data and produces
a cross-session digest (Option A) plus trend analysis with recommendations
(Option B). The model interprets structured JSON from `run.py summary`.

**What this skill is NOT:** it does not solve Mentor's context-verbosity
problem (verbose events still land in context per poll — that is a Mentor
concern). It reduces poll *count*, not event *verbosity* per poll.

## How to use this skill in practice

> Added 2026-06-24 after field feedback (Rui M.) — the most common
> mistake is treating Mode 1 as a separate "activation" step. It isn't.
> Mode 1 IS the Mentor invocation, with polling discipline + telemetry
> bundled in.

### Typical session

1. **Start a Mentor task by describing it in plain English.**
   Examples that auto-route through Mode 1:
   - *"use Mentor to add a Submit button to the Profile screen on Banking Portal"*
   - *"have Mentor generate tests for the LoanApproval action"*
   - *"run Mentor on [app] to do [thing]"*

   The agent picks this skill (Mode 1) because the description includes
   those trigger phrases. The polling discipline + telemetry happen as
   part of the Mentor invocation. **You don't need to "pre-activate"
   anything** — just ask for the Mentor task you want.

2. **(Optional) Do more Mentor tasks in the same session.** Each one
   gets its own telemetry record automatically.

3. **When you want the dashboard, ask for it.**
   Examples that auto-route through Mode 2:
   - *"generate the Mentor polling dashboard"*
   - *"show me my Mentor report"*

   Opens `~/.claude/cache/outsystems-mentor-polling-behavior/index.html`
   with cards for every Mentor session this skill recorded.

4. **(Optional) Cross-session trends.** *"Mentor session summary"* or
   *"how is Mentor performing"* triggers Mode 3.

### Common mistakes (and why the dashboard might be empty)

- ❌ **Running the skill name alone with no Mentor task.** Examples
  that DON'T do useful work:
  - invoking the skill by name with no follow-up
  - invoking the skill by name and saying only "mode 1" (no task described)

  Mode 1 needs an actual Mentor task to wrap. Without one, the skill
  has nothing to do — no telemetry is recorded.

- ❌ **Activating, then using NON-Mentor skills, then expecting telemetry.**
  Skills like `outsystems-deploy-preview`, `outsystems-tenant-architecture`,
  `outsystems-app-architecture`, `outsystems-dependency-impact`,
  `outsystems-ai-agent-landscape`, `outsystems-app-documentation` **do
  not invoke Mentor.** They use other MCP tools (`app_list`, `context_*`,
  `app_refs`, `env_list`, etc.). The polling-behavior skill cannot
  record what didn't happen through Mentor.

  Mentor-using skills are: `outsystems-mentor-copilot`,
  `outsystems-spec-driven-build`, `outsystems-design-to-app`,
  `outsystems-change-planner` (private), and any direct
  `mentor_start` call. Only these generate Mode 1 telemetry.

- ❌ **Generating the dashboard before any Mentor task ran.** The
  dashboard renders from `~/.claude/cache/outsystems-mentor-polling-behavior/<runId>/`
  directories. If no Mentor task ran through Mode 1, the cache is empty
  and the dashboard correctly reports "no data yet."

### Quick mental model

| Think of it as... | NOT as... |
|---|---|
| "The way I run Mentor (with discipline + recording bundled in)" | "A background recorder I turn on/off" |
| "Telemetry is captured DURING a Mentor invocation" | "Telemetry is captured for everything I do in the session" |
| "Mode 2 shows what Mode 1 captured" | "Mode 2 shows me my whole session" |

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b. Mentor must be enabled on the
tenant. Shared rules: §7b (API quirks), §8 (token-efficiency).

---

## Configuration (optional)

**Location:** your harness's skills directory — on Claude Code that is
`~/.claude/skills/outsystems-mentor-polling-behavior/config.json`.

The skill ships with a `config.json` containing defaults. Edit it to tune
behavior for your tenant. The skill never breaks if the file is missing,
partially filled, or malformed — it falls back to defaults on any read error.

```json
{
  "polling": {
    "tier2CadenceSecs": 30,
    "tier3CadenceSecs": 30,
    "maxPollsBeforeWarning": 20
  },
  "tierOverrides": {
    "publish_start": 2
  },
  "feedback": {
    "enabled": true,
    "minSessionsRequired": 5,
    "thresholds": {
      "avgMentorDurationSecs": 60,
      "avgPollCount": 5
    }
  },
  "dashboard": {
    "staleSessionDays": 30
  }
}
```

| Key | Default | What it controls |
|---|---|---|
| `polling.tier2CadenceSecs` | 30 | Sleep between Tier 2 status checks |
| `polling.tier3CadenceSecs` | 30 | Sleep between Tier 3 `mentor_get_run` polls |
| `polling.maxPollsBeforeWarning` | 20 | Poll count at which the procedure should warn the user |
| `tierOverrides.<tool>` | (see defaults) | Reclassify a tool to tier 1, 2, or 3 |
| `feedback.enabled` | true | Show/hide the Tier Review Signal panel in `index.html` |
| `feedback.minSessionsRequired` | 5 | Minimum succeeded sessions before signal can fire |
| `feedback.thresholds.avgMentorDurationSecs` | 60 | Signal fires if rolling avg Mentor duration drops below this |
| `dashboard.staleSessionDays` | 30 | Sessions older than this are dimmed in `index.html` (not deleted) |

**Tier overrides** let you reclassify any tool when its behavior changes on
your tenant without editing `SKILL.md`. Values: `1` (sync), `2` (fast async),
`3` (long async). The current tier table is always visible in `index.html`
with overrides highlighted.

To verify the resolved config at any time:
```bash
python3 "$SKILL/scripts/run.py" show-config
```

---

## Operation Tiers — the core concept

Every OutSystems MCP tool falls into one of three tiers. The tier determines
the polling strategy. **Never apply a polling strategy from a higher tier to a
lower-tier tool — it wastes tokens. Never apply a lower-tier strategy to a
higher-tier tool — it floods context.**

### Tier 1 — Synchronous (no polling)

Call once, use the result immediately. No sleep, no cursor, no retry loop.

| Tool | Notes |
|---|---|
| `app_list` | Full tenant app list |
| `app_info` | Single app metadata |
| `app_refs` | Dependency graph |
| `env_list` | All environments |
| `env_apps` | Deployed apps in an env |
| `context_screens` | Screen list |
| `context_entities` | Entity list |
| `context_actions` | Action list |
| `context_roles` | Role list |
| `context_structures` | Structure list |
| `context_themes` | Theme list |
| `context_search` | Search results |

**Rule:** Never add a sleep or poll loop before using results from these tools.

### Tier 2 — Fast async (30s inline poll)

These operations are async but typically complete in 30–90 seconds. Intermediate
poll responses are compact (a status string and a key). One 30s sleep before the
first status check is sufficient.

| Tool | Poll tool | Terminal states |
|---|---|---|
| `publish_start` | `publish_status` | `Finished`, `Failed` |
| `deploy_start` | `deploy_status` | `Finished`, `Failed` |
| `extlib_upload` | `extlib_status` | `Published`, `Failed` |
| `test_setup_start` | `test_setup_status` | `ready`, `failed` |

**Rule:** Sleep 30s → call status tool once. If not terminal, sleep 30s again
and repeat. Do not poll more frequently.

```bash
# Pattern:
sleep 30
# check status — if still running: sleep 30, check again
```

### Tier 3 — Long async / verbose (30s cadence, terminal result only)

`mentor_get_run` is the only tool in this tier. Two properties make it
expensive to poll naively:

1. **Duration:** Mentor runs typically take 2–10 minutes.
2. **Verbosity:** Every poll during an active run contains the full batch of
   internal `applyModelApiCode` tool events — raw C# code, compilation output,
   validation messages. Irrelevant to the user; often 10–50KB per response.

Polling at 500ms (the server's `pollAfterMs` hint) × 50–100 polls = 50–100
large responses entering context before the run completes. Each burns tokens.

**Rule:** Poll at ~30s intervals. Always pass `nextCursor` from the previous
response. Stop at `succeeded`, `failed`, or `cancelled`. Surface only the
terminal result — not the intermediate event stream.

```bash
# Pattern:
sleep 30
mentor_get_run(runId, cursor=<nextCursor>)
# if running: record poll → sleep 30 → repeat
# if terminal: record final poll → exit loop
```

**Why 30s, not `pollAfterMs`:** The server's 500ms hint is designed for
real-time UI progress bars, not LLM agents where every response has a token
cost. A 30s cadence means at most ~10–20 polls for a typical Mentor run vs
100–200+ at 500ms. The run does not complete faster by polling more often.

**Cursor discipline (mandatory):**
- First poll: call `mentor_get_run(runId)` with NO cursor.
- All subsequent polls: pass `cursor=<nextCursor>` from the previous response.
- If `nextCursor` is `null` on the first 1–2 polls: omit `cursor` on the next
  poll too. Once Mentor emits its first real event the cursor becomes non-null —
  thread it through every subsequent poll from that point.
- If `cursor_dropped` error: restart the poll without a cursor to get current state.
- **Never omit the cursor once it is non-null.** Doing so re-returns the entire
  buffered event stream from the beginning — multiplying token cost on every
  subsequent poll.

---

## Procedure

### Step 0 — Route to the correct mode

Read the user's request and pick the matching branch. **Do not mix modes.**

**Mode 1 — Mentor invocation**
Trigger: user wants to run Mentor on an app
→ Continue to Step 1.

**Mode 2 — Generate dashboard**
Trigger: user asks for the HTML dashboard, report, or to render sessions
→ Skip to **Mode 2 procedure** below.

**Mode 3 — Summary + recommendations**
Trigger: user asks for a summary, trends, or recommendations about their sessions
→ Skip to **Mode 3 procedure** below.

---

## Mode 1 — Mentor invocation

### Step 1 — Auth + resolve app + ask permission once

Call `mcp__outsystems__auth_status`. If `logged_in: false`, stop.

Resolve the app (Tier 1 — no sleep):
- Asset key (UUID) → use directly.
- Otherwise `mcp__outsystems__app_list` with `search: "<name>"`. 1 match →
  use; multiple → list candidates, ask user to pick; 0 → ask for a more
  specific name.

**Ask the user once via `AskUserQuestion` before proceeding:**

> Claude Code exposes this confirmation as the `AskUserQuestion` tool. On a
> harness without it (Codex), ask the same question inline and wait for an
> explicit answer before continuing. The gate is the confirmation, not the tool.

```
Question: "Run Mentor on <APP_NAME> with 30s polling discipline?
           Telemetry (poll count, timing, payload size) will be recorded
           to ~/.claude/cache/outsystems-mentor-polling-behavior/ and
           rendered as an HTML dashboard. No prompt content is stored."
Header:   "Confirm Mentor run"
Options:
  - "Yes — proceed"
  - "No — cancel"
```

On "No" → stop. On "Yes" → continue. **This is the only permission prompt
the user will see for this entire run.**

```
APP_KEY  = <asset key>
APP_NAME = <human name>
CACHE    = ~/.claude/cache/outsystems-mentor-polling-behavior
SKILL    = <this skill's directory>
```

> The cache stays at `~/.claude/cache/outsystems-mentor-polling-behavior/` on **every**
> harness. It is a shared cross-agent cache, not a Claude-only path — Codex reads and writes
> the same directory, so dashboards render from one session history regardless of which agent
> recorded it.

### Step 2 — Init session (silent)

> **Run silently. Do not narrate this step.**

```bash
python3 "$SKILL/scripts/run.py" init \
  --cache    "$CACHE"   \
  --app-key  "$APP_KEY" \
  --app-name "$APP_NAME"
```

`init` creates `$CACHE/sessions/<provisional-id>/meta.json` and writes the
session path to `$CACHE/.current-session`. No stdout output.

### Step 3 — Fire Mentor (Tier 3)

Call `mcp__outsystems__mentor_start` with the user's prompt:

```
mcp__outsystems__mentor_start(
  app_key = "$APP_KEY",
  prompt  = "$USER_PROMPT"
)
```

Capture `RUN_ID` and `CURSOR` (may be null). Then update the session record
with the real run ID — **silently** (no stdout; and on Claude Code, no
permission prompt):

```bash
python3 "$SKILL/scripts/run.py" update-run-id \
  --session "$CACHE/sessions/pending-XXXXXXXX" \
  --run-id  "$RUN_ID"
```

Replace `pending-XXXXXXXX` with the provisional session dir name written to
`$CACHE/.current-session` by `init`. Do NOT use `$(...)` to read it — instead
read the file content directly and substitute it as a literal string.

Then read the updated session path — **this is the only stdout capture,
and it happens exactly once before the poll loop:**

```bash
SESSION_DIR=$(python3 "$SKILL/scripts/run.py" show-session --cache "$CACHE")
```

Store `SESSION_DIR` as a shell variable. It will not change for the rest
of this run.

### Step 4 — Poll loop (Tier 3 discipline)

Initialize: `POLL_N=0`, `CURSOR=<nextCursor from mentor_start or null>`.

**Each iteration is THREE separate, sequential steps. Never chain them with
`&&` or combine them into one Bash call.**

**Step 4a — Sleep** (standalone, no chaining):
```bash
sleep 30
```

**Step 4b — Poll Mentor** (MCP tool call, not Bash):
```
mcp__outsystems__mentor_get_run(runId="$RUN_ID" [, cursor="$CURSOR"])
```

**Step 4c — Record poll** (silent Bash, standalone):
```bash
python3 "$SKILL/scripts/run.py" record-poll \
  --session       "$SESSION_DIR" \
  --poll          $POLL_N        \
  --status        "<status>"     \
  --event-count   <N>            \
  --payload-bytes <bytes>
```

Then update loop state and check for terminal:
```
POLL_N = POLL_N + 1
CURSOR = <nextCursor from response>
if status is succeeded / failed / cancelled → exit loop
```

> **Run Step 4c silently every time. Do not narrate it. Do not chain it
> with sleep or any other command.**

**HARD STOP — never do any of these:**

> On Claude Code each of these triggers an interactive permission prompt, which breaks the
> skill's silent-telemetry contract. On harnesses without that prompt (Codex) the same rule
> still applies: chaining defeats the per-poll record and the standalone-step discipline.

- `record-poll ... && python3 -c "import time; time.sleep(30)..."` — chaining causes a permission prompt
- `python3 -c "import time; time.sleep(30)"` — inline Python sleep causes a permission prompt
- `sleep 30 && record-poll ...` — chaining causes a permission prompt
- `$(date +%s)` anywhere — causes a permission prompt
- `$((POLL_N + 1))` — arithmetic expansion causes a permission prompt; use `POLL_N = POLL_N + 1` as a model-side variable update instead

**Payload bytes:** `len(json.dumps(response_events))` — byte length of the
`events` array. Token-cost proxy.

**Event count:** `len(response_events)`.

**Do not read or summarize intermediate event content.** The findings are
in the terminal result only.

If user aborts: `mcp__outsystems__mentor_cancel(runId="$RUN_ID")`, record
one final poll with `status=cancelled`, proceed to Step 5.

### Step 5 — Finalize + print summary

Print the Mentor findings inline to the user directly from the terminal
result's `summary` or `message` field. **Do not write findings to any
file or variable — display them in the conversation only.**

Then finalize the session — **silently, as a standalone command:**

```bash
python3 "$SKILL/scripts/run.py" finalize \
  --session "$SESSION_DIR" \
  --status  "$FINAL_STATUS"
```

Then print the polling summary — **as a separate standalone command:**

```bash
python3 "$SKILL/scripts/run.py" summarize --session "$SESSION_DIR"
```

This prints:
```
Polling summary: 8 polls · 4m 12s · ~180KB received · ~45K token-equivalent
Cadence applied: Tier 3 = 30s  |  Tier 2 = 30s
outsystems-mentor-polling-behavior saved 1,213 polls with ~8.5MB of event data compared to 500ms default polling.
```

**HARD STOP — never do these in Step 5:**

> Same reason as Step 4: on Claude Code each of these triggers an interactive permission
> prompt; on other harnesses (Codex) the standalone-command rule still holds.

- Pass findings via `--findings "..."` or `--findings-file` — removed, not supported
- Save findings to a file (with a file-writing tool or `echo`) — on Claude Code this triggers a permission prompt
- Chain `finalize && summarize` — triggers a permission prompt
- Use `python3 -c "..."` for anything — triggers a permission prompt

Each of `finalize` and `summarize` must be a separate, standalone Bash call.

> **Mode 1 ends here. The HTML dashboard is NOT rendered automatically.**
> Telemetry is now recorded in the cache. The user can generate the dashboard
> or get a summary at any time using Mode 2 or Mode 3.

---

## Mode 2 — Generate dashboard

```bash
CACHE="$HOME/.claude/cache/outsystems-mentor-polling-behavior"
SKILL="<this skill's directory>"
python3 "$SKILL/scripts/run.py" render --cache "$CACHE"
```

Then tell the user:
```
Dashboard generated: ~/.claude/cache/outsystems-mentor-polling-behavior/index.html
```

Open it in a browser to see all recorded sessions.

---

## Mode 3 — Summary + recommendations

```bash
CACHE="$HOME/.claude/cache/outsystems-mentor-polling-behavior"
SKILL="<this skill's directory>"
python3 "$SKILL/scripts/run.py" summary --cache "$CACHE"
```

This outputs structured JSON. Read it and produce a natural-language response
covering **both**:

**Option A — Cross-session digest:**
- How many sessions recorded, how many succeeded/failed
- Which apps have been run through Mentor and how many times each
- Total polls saved and event data avoided vs 500ms default across all sessions
- Total wall time spent in Mentor sessions

**Option B — Trend analysis + recommendations:**
- Are Mentor runs getting faster or slower over time? (compare oldest half vs newest half of succeeded sessions)
- Is the current 30s cadence still appropriate given the trend?
- If avg duration is dropping significantly, suggest lowering `tier3CadenceSecs` in config
- If avg duration is stable and well above the threshold, confirm the current config is well-tuned
- Surface any config mismatches (e.g. `avgPollThreshold` triggering on healthy data)

Be specific with numbers. Reference the actual values from the JSON, not vague generalities.

---

## Session storage

```
~/.claude/cache/outsystems-mentor-polling-behavior/
├── index.html                         ← Session List (all apps, all runs)
└── sessions/
    └── <runId>/
        ├── meta.json                  ← app-key, app-name, run-id, start-time,
        │                                 end-time, status, prompt-used
        ├── poll-log.jsonl             ← one JSON line per poll
        └── detail.html               ← Detail Page for this run
```

### `meta.json` shape

```json
{
  "runId":     "<mentor run id>",
  "appKey":    "<asset key>",
  "appName":   "<human name>",
  "startTime": 1718540000,
  "endTime":   1718540252,
  "status":    "succeeded",
  "prompt":    "<the user's Mentor instruction verbatim>"
}
```

### `poll-log.jsonl` shape (one JSON object per line)

```json
{"poll": 0, "t": 1718540030, "status": "running", "eventCount": 3, "payloadBytes": 12400, "cursor": "opaque-token"}
{"poll": 1, "t": 1718540060, "status": "running", "eventCount": 1, "payloadBytes": 4200, "cursor": "opaque-token-2"}
{"poll": 2, "t": 1718540252, "status": "succeeded", "eventCount": 5, "payloadBytes": 18900, "cursor": null}
```

---

## HTML output

### `index.html` — Session List

Self-contained HTML. Columns:

| Run ID (truncated, linked) | App | Date | Status | Polls | Wall time | ~Payload | ~Tokens |
|---|---|---|---|---|---|---|---|

Each row links to `sessions/<runId>/detail.html` via a relative path.
OutSystems dark theme. Opens in any browser with no server.

### `sessions/<runId>/detail.html` — Detail Page

- **Header:** App name · Run ID · Date · Status
- **Prompt used** (collapsible `<details>` block)
- **Poll timeline table:** Poll # · Timestamp · Δt · Status · Events · Bytes · Cumulative bytes
- **Summary panel:** Total polls · Wall time · Total payload · Token proxy · "500ms equivalent: ~N polls · Saved: ~M"
- **Findings** (from terminal result summary, rendered as Markdown-in-HTML)
- Back link → `../index.html`

Both files use relative links and are fully self-contained (no CDN, no server).

`index.html` also shows:
- **Tier Review Signal panel** (orange) — fires when rolling averages across
  recent sessions cross the configured feedback thresholds. Tells you when
  Mentor's behavior may have changed enough to warrant reviewing the tier
  classification. Suppressed if `feedback.enabled = false` in config.
- **Operation Tier Classification table** — shows every tool's current tier,
  with user overrides from `config.json` highlighted in orange.

---

## Token budget (estimate)

| Scenario | Polls | Notes |
|---|---|---|
| Typical Mentor run, 30s cadence | ~8–15 polls | ~2–5 min wall time |
| Same run at 500ms default | ~240–600 polls | Token cost 30–40× higher |
| Cached re-render (render only) | 0 MCP calls | `run.py render` re-reads existing sessions |

Token cost is dominated by Mentor's Tier 3 event verbosity, not by this skill's
overhead. The 30s cadence is the single lever this skill controls.

---

## Honest limitations

- **Token count is a proxy.** `payloadBytes / 4` is a rough estimate (1 token ≈
  4 bytes). The real token count depends on the model's tokenizer and the
  content type. Use it for relative comparison, not absolute billing.
- **Context-bloat is not solved.** Mentor's intermediate event payloads still
  land in context on every poll. The 30s cadence reduces poll *count* — it
  does not reduce event *verbosity* per poll. That is a Mentor-side concern.
- **500ms comparison is extrapolated.** The "polls saved" figure is
  `wall_time_seconds / 0.5` — the number of 500ms polls that would have fired
  in the same window. It is not a measured baseline.
- **Mentor session token.** If the terminal result includes a
  `mentor_session_token`, this skill does NOT auto-publish. Surface it to the
  user for manual review — they decide whether to publish the changes.

---

## Troubleshooting

Common failures (MCP disconnect, auth expiry, missing `python3`) — see
CONVENTIONS §7c. Skill-specific:

- **`mentor_start` errors immediately** → Mentor not enabled on the tenant.
  Ask the user to enable it in ODC Portal.
- **`cursor_dropped` on a poll** → cursor predated the retained buffer. Call
  `mentor_get_run(runId)` without a cursor to get current state, then resume
  normal cursor threading from the new `nextCursor`.
- **Poll loop runs >20 polls with no terminal** → prompt may be too broad.
  Cancel via `mcp__outsystems__mentor_cancel`, note the partial session, and
  ask the user to narrow scope.
- **`index.html` shows no sessions** → `$CACHE/sessions/` may be empty or
  `meta.json` files missing. Re-run the skill for at least one complete session.

---

## Harness notes

- **Claude Code** auto-saves MCP results larger than ~25 KB to disk and injects only the
  file path into context, keeping the payload itself out of the model's context.
- **Codex** has no such auto-save: the full result is injected inline.
- **The honest cost delta, and why it matters more here than in other skills:** this skill's
  whole purpose is Tier 3 poll-cost control, and `mentor_get_run` returns 10–50 KB of
  `applyModelApiCode` events *per poll*. On Claude Code most of those responses spill to disk
  and never enter context. On Codex every poll's payload lands inline, so a Mentor run costs
  materially more on the first pass. The 30s cadence is the lever on both harnesses, and it is
  what makes the skill worth using on Codex at all (~8–15 polls instead of ~240–600).
- **Mode 2** (render) and **Mode 3** (summary) make zero MCP calls — they read the local
  cache — so they cost the same on both harnesses.
- The skill's telemetry (`payloadBytes`) measures what the *tool returned*, not what entered
  the model's context. On Claude Code the two differ whenever a payload spills to disk. Read
  the dashboard's token proxy as a Codex-equivalent upper bound.

---

## Anti-patterns — do NOT do these

- **Don't poll `mentor_get_run` at 500ms.** That is the server's UI hint, not
  the LLM polling cadence. 30s is the floor.
- **Don't omit `cursor` once it is non-null.** Re-returns the entire buffered
  event stream from the beginning on every subsequent poll.
- **Don't read or summarize intermediate event content.** Record byte count and
  event count only. The findings are in the terminal result.
- **Don't apply Tier 3 sleep to Tier 1 tools.** `app_list`, `context_*`,
  `env_list` are synchronous — adding sleep before them wastes wall time with
  zero benefit.
- **Don't apply Tier 1 (no-sleep) behavior to Tier 2 or 3 tools.** Hammering
  `publish_status` without sleep creates unnecessary load and burns tokens on
  compact-but-frequent status responses.
- **Don't auto-publish.** If `mentor_session_token` is present in the terminal
  result, surface it to the user. Never call `publish_start` automatically from
  this skill.

## When NOT to use

- User wants to call Mentor without any polling discipline or telemetry →
  call `mcp__outsystems__mentor_start` directly.
- User wants a curated Mentor task library (11 templates, workflows) →
  use `outsystems-mentor-copilot` instead.
- User wants a full app architecture view → run `outsystems-app-architecture`
  separately (Tier 1 tools, no Mentor needed).
