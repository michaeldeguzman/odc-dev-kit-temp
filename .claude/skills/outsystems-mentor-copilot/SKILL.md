---
name: outsystems-mentor-copilot
description: Curated task library on top of ODC Mentor. Pick from 11 ready-made prompts (quality review, perf audit, security review, accessibility, test generation, doc gap fill, refactor, AI model migration, add feature, demo data, demo readiness) or run a multi-step workflow (audit-and-fix, add-feature-then-test, publish-after-mentor). Handles the polling loop and renders a clean markdown report. Use when the user asks "run mentor", "have mentor review", "use mentor to", "audit with mentor", "generate tests with mentor", "have mentor add", "mentor demo readiness", or names any of the task IDs directly.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code (Claude Code is the most token-efficient path — see Harness notes). Requires Python 3.7+ (stdlib only) and the `outsystems` MCP server connected and authenticated. Mentor must be enabled on the tenant.
allowed-tools: Bash Write Edit Read mcp__outsystems__auth_status mcp__outsystems__mentor_start mcp__outsystems__mentor_get_run mcp__outsystems__mentor_cancel mcp__outsystems__publish_start
metadata:
  version: "1.2.0"
  author: outsystems-r-and-d
---

# OutSystems Mentor Co-pilot

Curated prompts + per-invocation polling discipline + markdown rendering
on top of `mentor_start` / `mentor_get_run`.

The schemas give nothing semantic — just a `prompt` string and a stream
of events. This skill's value is **what we put in the prompt** and
**how we read the events without ballooning context**.

**Scope vs `outsystems-mentor-polling-behavior`** (optional companion):
this skill owns the per-invocation polling loop (cursor, sandbox-safe
sleep, Claude Code's harness disk-save for the terminal event) AND the curated 11-task
prompt library. The companion skill is a **cross-session telemetry
layer** that records per-poll metrics across runs, generates an HTML
dashboard, and surfaces summaries/trends. They co-exist: install
polling-behavior alongside this skill if you want benchmark data on
Mentor token usage; this skill works fine standalone without it.

## Prerequisites

Standard catalog prereqs — see CONVENTIONS §4b — **plus Mentor
enabled on the tenant.** Shared rules: §7b (API quirks), §8
(token-efficiency). Skill-specific polling discipline lives in Step 4
below (cursor handling, sandbox-safe sleeps, expected payload sizes)
and overrides anything more general.

## Procedure — single task

### Step 1 — Pick a task

```bash
python3 "$SKILL/scripts/run.py" list-tasks
```

Output is `<id>  <category>  <name>`. Categories: `audit` / `build` / `docs`.

If the user named a task (e.g. "have mentor do a security review on
Banking Portal"), match it to a task id and skip to step 2.

### Step 2 — Resolve the prompt

```bash
PROMPT=$(python3 "$SKILL/scripts/run.py" show-task \
  --task <task-id> \
  --var key=value --var key=value)
echo "$PROMPT" > "$CACHE/last-prompt.txt"
```

Variables required by the task (see `templates/tasks.json`) must be
provided as `--var k=v` or the script exits. Defaults apply otherwise.

### Step 3 — Start the run

Call `mcp__outsystems__mentor_start` with:
- `app_key` (required first turn)
- `prompt` ($PROMPT from step 2)

Response shape: `{ runId, status, pollAfterMs, mentor_session_id }`.
Capture `runId`.

### Step 4 — Poll until terminal

**Polling contract — do this exactly, it's where context bloat hides:**

1. First poll: `mentor_get_run(runId=<run>)` — **no cursor**.
2. Inspect `status`:
   - `running` → save `nextCursor`, sleep (see sleep rules below), then
     `mentor_get_run(runId=<run>, cursor=<nextCursor>)`. Repeat.
   - `succeeded` / `failed` / `cancelled` → terminal, stop polling.
3. **Always pass the previous `nextCursor` on subsequent polls** *unless
   it's `null`*. The cursor-paged API returns only new events since the
   passed cursor; omitting it re-returns the full buffer.
4. **`nextCursor: null` handling.** Mentor often returns `null` on the
   first one or two polls (no events emitted yet). In that case **omit
   `cursor` on the next poll too** — do NOT fabricate a placeholder.
   Once Mentor emits its first real event, `nextCursor` becomes a
   non-null opaque token; thread it through every subsequent poll.

**Sleep rules (sandbox-safe):**

- Honor `pollAfterMs` as a *minimum*, not an exact value. Mentor's
  typical hint is 500 ms, but the model gets cheaper context overall
  by sleeping 2–5 s between polls (fewer round-trips).
- **Claude Code's Bash sandbox blocks long standalone sleeps** (≥ ~10 s).
  Stick to `sleep 2` to `sleep 5`. For longer waits, use an until-loop:
  `until <condition>; do sleep 2; done`, or run the sleep in background
  via that harness's `run_in_background` flag. On harnesses without that
  sandbox restriction (e.g. Codex), a plain `sleep` works — but keep the
  2–5 s cadence anyway, since it is a token optimisation, not just a
  sandbox workaround, and use whatever background-execution mechanism
  your harness provides.
- **If the previous poll returned 0 new events**, increase the next
  sleep to ~5 s. Mentor is mid-thinking; polling fast just burns
  tokens for empty responses.

**Expected payload sizes — don't be surprised:**

- One early poll usually carries a **30–500 KB** `tool_end` event
  containing Mentor's internal OML scan output (`getDataModel`,
  `applyModelApiCode`, etc.). This is unavoidable; you pay it once.
  On Claude Code, anything over 25 KB is auto-saved to disk by the
  harness and never enters model context; otherwise it lands inline.
  On harnesses without that auto-save (Codex) it always lands inline —
  save it straight to the cache and never re-print it. Either way,
  subsequent polls are much smaller.
- The **terminal poll** carries `result.summary` (the full answer)
  and may itself exceed the model's max-tokens limit. On Claude Code, if
  you get `exceeds maximum allowed tokens` on the terminal poll, the
  harness has spilled it to disk — read the file from the path it gives
  you to access `result.summary`, then proceed to Step 5. On harnesses
  without a spill mechanism the terminal response arrives inline; save it
  to `$CACHE/runs/<runId>.result.json` and proceed to Step 5 the same way.

If user wants to abort: `mcp__outsystems__mentor_cancel(runId=<run>)`.

### Step 5 — Save the terminal result

**Goal:** end this step with a JSON file at
`$CACHE/runs/<runId>.result.json` containing the terminal response
(must include `result: {...}` at the top level). Three paths cover
every case:

1. **Terminal response came back inline and fits in context** → save
   the response JSON directly to `$CACHE/runs/<runId>.result.json`.
   This is the most common path for small/medium runs, and the only
   path on harnesses without a disk spill (Codex).
2. **Terminal response auto-spilled to disk by the harness** (>25 KB
   or exceeded max-tokens; Claude Code only) → the harness gives you
   the path. Either `cp` it to `$CACHE/runs/<runId>.result.json` or
   pass its path directly to the render step in Step 6.
3. **Inline response is fine but you want it on disk for caching /
   sharing** → save it. Same as path 1.

**Do NOT re-poll a terminal `succeeded` run to force a spill.** Once
`status` is terminal, the buffer is final — re-polling just costs
extra round-trips for the same payload. If you have the response
inline, write it; if the harness spilled it, use the path.

### Step 6 — Render

```bash
python3 "$SKILL/scripts/run.py" render \
  --result      "$CACHE/runs/<runId>.result.json" \
  --output      "$CACHE/runs/<runId>.md" \
  --task        "<task-id>" \
  --app-key     "<app_key>" \
  --run-id      "<runId>" \
  --prompt-file "$CACHE/last-prompt.txt"
```

Output is a markdown report. If the terminal result included a
refreshed `mentor_session_token`, the report ends with a "Publish
handoff" section containing the exact `publish_start` call to fire —
**never auto-publish.**

### Step 7 — Report (3–5 lines)

- Output path (`$CACHE/runs/<runId>.md`)
- Task ran, app, status
- Token-cost note: how many polls happened
- "Open the report" / "Run publish-handoff to commit" if applicable

## Procedure — workflow (multi-step)

Workflows chain task templates in the same Mentor session. Steps 1–6
repeat per step; between steps:

- **Step N start**: pass `mentor_session_id` + the `mentor_session_token`
  from the previous step's terminal `result` to `mentor_start`. Do NOT
  pass `app_key` again.
- Render once at the end — the final step's response is the
  consolidated output.

```bash
python3 "$SKILL/scripts/run.py" show-workflow \
  --workflow <wf-id> \
  --var task_id=<id>  # for publish-after-mentor only
```

Outputs the resolved step plan as JSON. Iterate through `steps[]`,
running each as Step 3–5 above.

## Cache rules

- Location: `~/.claude/cache/outsystems-mentor-copilot/<tenant-id>/`
- Per-run subdir: `runs/<runId>/`
- TTL: **none** — Mentor runs are user-initiated and the user owns the
  retention decision. Past runs are kept until the user cleans them up.
- Re-rendering a past run: just re-run step 6 against the existing
  `result.json`. ~1K tokens.

> `~/.claude/cache/` is this catalog's shared cache root on every harness
> (including Codex) — do not relocate it per-agent; sharing it lets agents
> reuse each other's fetches.

## Token budget (estimate, empirical)

These numbers come from real live-test runs on the `morpheus-qa`
tenant, not paper estimates.

| Scenario | Polls | Cache writes | Notes |
|---|---|---|---|
| `doc-gap-fill count=5`, warm-cache test | 3 | ~30 K | In-session continuation, Mentor scan fit inline |
| `demo-readiness`, fresh-session cold cache | 11 | **~300 K** | One poll dumped 340 KB inline before cursor gating |
| Re-render past run | 0 | ~1 K | run.py render only |

**Cost dominator: Mentor's first big `tool_end` event** (the OML scan
dump). Once that lands, every subsequent model turn re-reads it as
cache. A `demo-readiness`-class run on Opus 4.7 costs roughly **$5–15
fresh-session**, **$0.50–1.50 in-session continuation**.

Re-rendering is near-free because `result.summary` is already on disk.

**Cost-reduction levers:**
- Bias toward longer polls when events buffer is empty (the
  sleep-on-idle rule in Step 4).
- For follow-up turns in the same session, reuse `mentor_session_id` +
  `mentor_session_token` — Mentor keeps the OML loaded server-side, so
  it doesn't re-scan.
- If you only need a re-render of a past run, skip Steps 3–5 entirely.

## Harness notes

- **Claude Code**: two harness behaviours make this the cheapest path.
  (a) MCP results over ~25 KB are auto-saved to disk and never enter
  model context — which matters a lot here, because Mentor's first
  `tool_end` OML-scan event is 30–500 KB. (b) If the terminal poll
  exceeds the model's max-tokens limit, the harness spills it to disk
  and hands you a path. Its Bash sandbox also blocks long standalone
  sleeps, hence the until-loop pattern and the `run_in_background` flag.
- **Codex**: no auto-save and no max-tokens spill — the 30–500 KB
  `tool_end` event and the terminal `result.summary` both arrive inline.
  Save each straight to `$CACHE` and never re-print it. Expect the
  first-run cost to be materially higher than on Claude Code, since that
  one scan event is the cost dominator; this is why `compatibility:`
  names Claude Code as the most token-efficient path. The polling
  contract, cursor rules and the 2–5 s cadence are identical on both.
- Re-rendering a past run (Step 6 alone) costs the same on both
  harnesses — it never calls Mentor at all.
- Cache location `~/.claude/cache/` is shared across harnesses (see the
  Cache rules note).

## Anti-patterns — do NOT do these

- **Don't omit `cursor` once Mentor has issued a non-null one.** Doing
  so re-returns the entire buffered stream every poll — including the
  30–500 KB scan dump. Costs 5–10× more tokens. The null-cursor
  exception (Step 4 §4) is the only one.
- **Don't tighten `pollAfterMs` below the server's hint.** Tightening
  burns tokens; the schema also warns `cursor_dropped` if the buffer
  rolls. *Loosening* by 2–5× is fine and recommended (Step 4 sleep
  rules).
- **Don't issue `sleep 30+` standalone in Bash.** The Claude Code
  sandbox blocks long single sleeps as anti-polling protection. Use
  the `until …; do sleep 2; done` pattern, or that harness's
  `run_in_background` flag. The until-loop works on every harness.
- **Don't auto-publish.** The skill surfaces the publish handoff — the
  human confirms. Auto-publishing changes the trust contract this skill
  ships with.
- **Don't combine `app_key` + `mentor_session_id` on the same
  `mentor_start`.** First turn uses `app_key`. Subsequent turns reuse
  the session — passing both is undefined.
- **Don't poll a cancelled run.** `mentor_cancel` is fire-and-forget;
  poll once after to confirm `cancelled`, then stop.
- **Don't poll past ~20 iterations on a single turn.** If Mentor is
  still running at that point, the prompt is likely too broad. Cancel,
  narrow the scope, and start a fresh run.
- **Don't re-poll a terminal `succeeded` run to coerce a disk spill.**
  Step 5 covers all three save paths — re-polling once `status` is
  terminal just costs extra round-trips for the same payload. If the
  response is inline, save it directly.

## When NOT to use

- User wants a Mentor task that doesn't fit any template → call
  `mentor_start` directly with their custom prompt. This skill earns
  its keep through the curated library; ad-hoc prompts skip the
  library and the rendering wrapper is overkill for one-off questions.
- User wants synchronous answers fast (Mentor runs can take 1–10 min) →
  use `outsystems-app-architecture` or the context_* tools directly.
- Mentor isn't enabled on the tenant → `mentor_start` will error
  immediately. Tell the user to enable Mentor in ODC Portal first.
- User wants telemetry across multiple Mentor runs (poll-count savings,
  trend analysis, on-demand dashboard) → install
  `outsystems-mentor-polling-behavior` alongside this skill. This skill
  doesn't track cross-session data.
- User asks for **Studio-native pseudocode** specifically (where does
  this logic go? which element type? action steps with real parameter
  labels?) → use `outsystems-mentor-implementation` (companion in
  Paulo's `portable-agent-skills` repo, linked from our README). That
  skill specializes in the deterministic intent-to-pseudocode
  transformation layer; this skill specializes in curated audit/build
  task templates.
- User has a **saved plan file** from `superpowers:writing-plans`,
  `outsystems-spec-driven-build`, or a hand-written planner, and needs
  coverage review + patching before Mentor conversion →
  `outsystems-plan-to-mentor` (companion in Paulo's repo). This skill
  doesn't do PRD coverage validation.
