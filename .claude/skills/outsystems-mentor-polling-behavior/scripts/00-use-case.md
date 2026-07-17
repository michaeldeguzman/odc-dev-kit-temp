# Project: outsystems-mentor-polling-behavior / run.py

## Project Context

**Description**: Session lifecycle, telemetry, config loading, HTML rendering,
and cross-session summary driver for the `outsystems-mentor-polling-behavior`
Claude Code skill. Called by the model loop during a Mentor invocation to
record per-poll telemetry. HTML dashboard and summary are on-demand only —
not generated automatically at the end of a Mentor run.

**Tech Stack**:
- **Language**: Python 3.7+
- **Framework**: stdlib only (argparse, json, pathlib, math, uuid, time, datetime)
- **Testing**: pytest (dev only)
- **Dependencies**: none (pure stdlib for production code)
- **Package Manager**: uv

**Architecture**:
- Single-file CLI (`run.py`) with subcommand dispatch via argparse
- Ten subcommands: `init`, `update-run-id`, `show-session`, `show-config`,
  `record-poll`, `finalize`, `summarize`, `summary`, `render`
- Session path communicated via `.current-session` pointer file — no stdout
  capture (`$(...)`) in any bookkeeping call except `show-session` (once)
- All file I/O via `pathlib.Path`
- HTML templates loaded from `SKILL_DIR/assets/` via `_render_template()`

**Development Environment**:
- **OS**: macOS (darwin)
- **Runtime**: Python 3.7+
- **Package Manager**: uv
- **Test Command**: `uv run pytest` (run from `scripts/`)
- **Test File**: `scripts/tests/test_run.py`

---

## Use Cases

### 1. Config loading with deep merge and graceful fallback
**Description**: `_load_config()` reads `config.json` from the skill
directory and deep-merges it with `_CONFIG_DEFAULTS`. Must return full
defaults when the file is missing, when JSON is malformed, or when only
some keys are present. `_comment` keys (starting with `_`) must be
stripped from the merge. `_resolved_tiers()` must apply `tierOverrides`
from the config on top of `DEFAULT_TIERS`, ignoring invalid tier values
and non-integer values.

**Status**: Completed
**Test Coverage**: 15 tests (UC#1 block in test_run.py)

---

### 2. Session init — create provisional session directory
**Description**: `cmd_init` creates a provisional session directory under
`<cache>/sessions/pending-<uuid>/`, writes `meta.json` with `runId`,
`appKey`, `appName`, `startTime`, `endTime=None`, `status="running"`.
Does NOT store `prompt` or `findings` — prompt privacy is by design.
Writes the session path to `<cache>/.current-session` pointer file.
Produces NO stdout output. Must work even if `<cache>/sessions/` does
not yet exist.

**Status**: Completed
**Test Coverage**: 6 tests — pointer file creation, no stdout, unique dirs,
parent dir creation, startTime type, meta fields

---

### 3. Session rename — update provisional ID to real Mentor runId
**Description**: `cmd_update_run_id` renames a provisional session
directory (`pending-*`) to the real Mentor `runId`, updates `runId` in
`meta.json`, and updates the `.current-session` pointer file. Produces
NO stdout output. Must fail gracefully (exit 1, stderr) when the session
directory does not exist, when `meta.json` is missing, and when the
target directory already exists (collision guard).

**Status**: Completed
**Test Coverage**: 7 tests — rename, meta update, pointer update, no stdout,
three error cases

---

### 4. Poll recording — append telemetry to poll-log.jsonl
**Description**: `cmd_record_poll` appends one JSON line to
`<session>/poll-log.jsonl` containing `poll` (int), `t` (unix timestamp
from `time.time()` — never from a shell argument), `status`, `eventCount`,
and `payloadBytes`. `cursor` is no longer recorded. When `--event-count`
or `--payload-bytes` are omitted, defaults to 0. Creates the session
directory if missing. Appends — never overwrites.

**Status**: Completed
**Test Coverage**: 4 tests — entry content, multiple appends, zero defaults,
dir creation

---

### 5. Session finalize — write terminal state to meta.json
**Description**: `cmd_finalize` updates `meta.json` with `endTime`
(always `time.time()` — no `--end-time` argument) and `status`. Does
NOT accept or store findings — findings are displayed inline in the
conversation only. Must fail gracefully (exit 1, stderr) when `meta.json`
is missing.

**Status**: Completed
**Test Coverage**: 4 tests — status+endTime written, no findings stored,
error on missing meta, current time used

---

### 6. Stats computation — polls, bytes, wall time, 500ms comparison
**Description**: `_compute_stats()` computes `totalPolls`, `totalBytes`,
`wallSeconds`, `polls500ms` (ceil of wallSeconds / 0.5), `pollsSaved`
(max 0, polls500ms - totalPolls), and `bytesAvoided` (avg bytes per poll
× pollsSaved — the extrapolated event data avoided vs 500ms default).
`_fmt_bytes()`, `_fmt_duration()`, and `_fmt_tokens()` format raw numbers
into human-readable strings. All must handle zero, negative, and very
large inputs without raising.

**Status**: Completed
**Test Coverage**: 11 tests

---

### 7. Session loading — read meta.json and poll-log.jsonl
**Description**: `_load_session()` reads `meta.json` and
`poll-log.jsonl` from a session directory. Returns empty dict and empty
list when either file is missing. Silently skips malformed JSON lines in
`poll-log.jsonl` rather than raising. `_is_stale()` returns True when
the session's `startTime` is older than `staleSessionDays`, False when
`staleSessionDays <= 0` or `startTime` is 0.

**Status**: Completed
**Test Coverage**: 9 tests

---

### 8. Feedback signal — tier review threshold detection
**Description**: `_compute_feedback_signal()` returns `None` when
feedback is disabled in config, when fewer than `minSessionsRequired`
succeeded sessions exist, or when the `avgMentorDurationSecs` threshold
is NOT crossed. Returns a signal dict when the rolling average Mentor run
duration across the last N succeeded sessions drops below the threshold.
Only `avgMentorDurationSecs` is checked — `avgPollCount` was removed as
a noisy proxy. Uses only succeeded sessions. Sessions are assumed
newest-first.

**Status**: Completed
**Test Coverage**: 6 tests — disabled, not enough sessions, fires on
duration, no signal above threshold, ignores failed, uses min sessions

---

### 9. HTML render — index.html and detail.html generation
**Description**: `cmd_render` generates `<cache>/index.html` (Session
List) and `<cache>/sessions/<runId>/detail.html` (Detail Page) from all
session data. `index.html` includes the tier classification table and,
when triggered, the feedback signal panel (duration threshold only).
`detail.html` includes poll timeline and summary metrics — does NOT
include findings or prompt (privacy by design). Templates loaded from
`SKILL_DIR/assets/` via `_render_template()`. Both files are
self-contained HTML using the tenant-architecture design style (Inter +
JetBrains Mono fonts, OutSystems dark theme). When `<cache>/sessions/`
does not exist, renders an empty index. Re-running is idempotent.
**On-demand only — not called automatically after a Mentor run.**

**Status**: Completed
**Test Coverage**: 7 tests — empty cache, creates both files, index content,
poll timeline, idempotent, multiple sessions, XSS escaping

---

### 10. Session pointer — show-session subcommand
**Description**: `cmd_show_session` prints the current session dir path
from the `<cache>/.current-session` pointer file to stdout. This is the
only `run.py` call that writes to stdout in the Mode 1 procedure, and it
fires exactly once (after `update-run-id`). Must fail gracefully (exit 1,
stderr) when the pointer file does not exist.

**Status**: Completed
**Test Coverage**: covered implicitly by UC#2 and UC#3 pointer tests

---

### 11. Cross-session summary — structured JSON output
**Description**: `cmd_summary` reads all sessions from the cache and
outputs structured JSON for model interpretation covering:
(A) Cross-session digest — session counts by status, per-app breakdown
(name, count, last run date), totals (polls saved, bytes avoided, total
bytes, wall time, poll count).
(B) Trend analysis — splits succeeded sessions chronologically into
oldest half and newest half, computes avg duration and avg poll count
per half, direction (faster/slower/stable), change percent. Returns
`None` for trend when fewer than 4 succeeded sessions exist.
Also includes current config values (cadence, threshold) for the model
to reference when making recommendations.

**Status**: Completed
**Test Coverage**: 7 tests — empty cache, session counts, app breakdown,
totals, trend present/absent, config fields

---

### 12. Three-mode routing — Mentor run / generate / summary
**Description**: The skill operates in three modes detected at Step 0:
Mode 1 (Mentor invocation — full procedure, no auto-render),
Mode 2 (generate dashboard — `run.py render`),
Mode 3 (summary + recommendations — `run.py summary` + model interprets).
All bookkeeping commands in Mode 1 are silent (no stdout, no permission
prompts). The only stdout capture is `show-session` (once). No shell
command substitutions `$(...)` except that single `show-session` capture.
HARD STOP rules in SKILL.md forbid chaining, inline Python, shell
variables for findings, and `$(date +%s)`.

**Status**: Completed
**Test Coverage**: verified via integration — all UC tests exercise the
individual subcommands that compose the three modes
