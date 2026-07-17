#!/usr/bin/env python3
"""
outsystems-mentor-polling-behavior driver.

This script does NOT call Mentor. Mentor is invoked via MCP tools
(mentor_start + mentor_get_run) by the model loop. This script handles
session lifecycle, telemetry, config loading, and HTML rendering only:

  init           — create a session directory + write .current-session pointer
  update-run-id  — rename provisional dir to real Mentor runId, update pointer
  show-session   — print the current session dir path (reads .current-session)
  show-config    — print the resolved config (defaults + any user overrides)
  record-poll    — append one telemetry line to poll-log.jsonl
  finalize       — write end-time + final status to meta.json
  summarize      — read poll-log.jsonl + meta.json, print terminal summary
  summary        — output structured JSON of cross-session stats + trends (for model interpretation)
  render         — read all sessions, generate index.html + detail.html (on-demand only)

Session path is communicated via a .current-session pointer file rather than
stdout capture, eliminating all command substitution $(...) from the procedure.

User prompts are NOT stored — this script records telemetry about how Mentor
was called (timing, poll counts, payload sizes), not what was asked.

Config file (optional):
  ~/.claude/skills/outsystems-mentor-polling-behavior/config.json
  If missing or malformed, all defaults apply. See config.json for the
  full schema and inline documentation.

Pure stdlib. No pip install.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Skill root — parent of scripts/
# ---------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Default tier classification
# ---------------------------------------------------------------------------

DEFAULT_TIERS: dict[str, int] = {
    # Tier 1 — synchronous
    "app_list":          1,
    "app_info":          1,
    "app_refs":          1,
    "env_list":          1,
    "env_apps":          1,
    "context_screens":   1,
    "context_entities":  1,
    "context_actions":   1,
    "context_roles":     1,
    "context_structures":1,
    "context_themes":    1,
    "context_search":    1,
    # Tier 2 — fast async
    "publish_start":     2,
    "deploy_start":      2,
    "extlib_upload":     2,
    "test_setup_start":  2,
    # Tier 3 — long async / verbose
    "mentor_get_run":    3,
}

TIER_LABELS = {
    1: "Tier 1 — Synchronous (no sleep)",
    2: "Tier 2 — Fast async (30s inline poll)",
    3: "Tier 3 — Long async / verbose (30s cadence, terminal result only)",
}


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

_CONFIG_DEFAULTS: dict = {
    "polling": {
        "tier2CadenceSecs":      30,
        "tier3CadenceSecs":      30,
        "maxPollsBeforeWarning": 20,
    },
    "tierOverrides": {},
    "feedback": {
        "enabled":             True,
        "minSessionsRequired": 5,
        "thresholds": {
            "avgMentorDurationSecs": 60,
        },
    },
    "dashboard": {
        "staleSessionDays": 30,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, returning a new dict.
    Keys present in base but missing from override keep their base value.
    Skips keys whose names start with '_' (comment keys)."""
    result = dict(base)
    for k, v in override.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _load_config() -> dict:
    """Load config.json from the skill directory, merging with defaults.
    Never raises — returns defaults on any error."""
    config_path = SKILL_DIR / "config.json"
    if not config_path.exists():
        return _deep_merge(_CONFIG_DEFAULTS, {})
    try:
        raw = json.loads(config_path.read_text("utf-8"))
        return _deep_merge(_CONFIG_DEFAULTS, raw)
    except (json.JSONDecodeError, OSError):
        return _deep_merge(_CONFIG_DEFAULTS, {})


def _resolved_tiers(config: dict) -> dict[str, int]:
    """Return the tier map with any user overrides applied."""
    tiers = dict(DEFAULT_TIERS)
    for tool, tier in (config.get("tierOverrides") or {}).items():
        if isinstance(tier, int) and tier in (1, 2, 3):
            tiers[tool] = tier
    return tiers


# ---------------------------------------------------------------------------
# HTML templates — loaded from assets/ at render time
# ---------------------------------------------------------------------------

def _render_template(name: str, **slots: str) -> str:
    """Load a template from SKILL_DIR/assets/<name> and substitute {{SLOT}} placeholders.

    Each key in slots maps to a {{KEY}} token in the template file.
    Unknown slots are silently ignored; unknown tokens are left as-is.
    Raises FileNotFoundError if the template file is missing.
    """
    template_path = SKILL_DIR / "assets" / name
    html = template_path.read_text(encoding="utf-8")
    for key, value in slots.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    return html


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_bytes(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b / (1024 * 1024):.2f} MB"


def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s"


def _fmt_tokens(b: int) -> str:
    t = b // 4
    if t < 1000:
        return str(t)
    return f"{t / 1000:.1f}K"


def _fmt_pct(pct: int) -> str:
    return f"{pct}%"


def _badge_class(status: str) -> str:
    s = (status or "").lower()
    if s == "succeeded":
        return "badge-ok"
    if s == "failed":
        return "badge-fail"
    if s == "cancelled":
        return "badge-cancel"
    return "badge-run"


def _ts_to_date(ts: int) -> str:
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "—"


def _html_escape(s: str) -> str:
    return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _load_session(session_dir: Path) -> tuple[dict, list[dict]]:
    """Load meta.json + poll-log.jsonl from a session directory."""
    meta_path = session_dir / "meta.json"
    log_path  = session_dir / "poll-log.jsonl"
    meta: dict = {}
    polls: list[dict] = []
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text("utf-8"))
        except json.JSONDecodeError:
            pass
    if log_path.exists():
        for line in log_path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                polls.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return meta, polls


def _compute_stats(meta: dict, polls: list[dict]) -> dict:
    total_polls  = len(polls)
    total_bytes  = sum(p.get("payloadBytes", 0) for p in polls)
    start_time   = meta.get("startTime", 0)
    end_time     = meta.get("endTime", 0)
    wall_seconds = (end_time - start_time) if (end_time and start_time) else 0
    polls_500ms  = max(0, math.ceil(wall_seconds / 0.5)) if wall_seconds else 0
    polls_saved  = max(0, polls_500ms - total_polls)
    avg_bytes    = (total_bytes // total_polls) if total_polls else 0
    bytes_avoided = avg_bytes * polls_saved
    bytes_500ms  = avg_bytes * polls_500ms  # extrapolated total at 500ms
    # Reduction percentages (0–100, rounded to nearest int)
    polls_pct = round(polls_saved / polls_500ms * 100) if polls_500ms else 0
    bytes_pct = round(bytes_avoided / bytes_500ms * 100) if bytes_500ms else 0
    return {
        "totalPolls":       total_polls,
        "totalBytes":       total_bytes,
        "wallSeconds":      wall_seconds,
        "polls500ms":       polls_500ms,
        "pollsSaved":       polls_saved,
        "pollsReductionPct": polls_pct,
        "bytesAvoided":     bytes_avoided,
        "bytesReductionPct": bytes_pct,
    }


def _is_stale(meta: dict, stale_days: int) -> bool:
    if stale_days <= 0:
        return False
    start = meta.get("startTime", 0)
    if not start:
        return False
    age_days = (time.time() - start) / 86400
    return age_days > stale_days


# ---------------------------------------------------------------------------
# Feedback signal computation
# ---------------------------------------------------------------------------

def _compute_feedback_signal(
    sessions: list[tuple[dict, list[dict], Path]],
    config: dict,
) -> dict | None:
    """Return a signal dict if avgMentorDurationSecs threshold is crossed, else None.

    Only avgMentorDurationSecs is checked — avgPollCount was removed as it
    was a noisy proxy for the same thing duration captures more accurately.
    """
    fb = config.get("feedback", {})
    if not fb.get("enabled", True):
        return None

    min_sessions   = fb.get("minSessionsRequired", 5)
    thresholds     = fb.get("thresholds", {})
    avg_dur_thresh = thresholds.get("avgMentorDurationSecs", 60)

    succeeded = [
        (m, p) for m, p, _ in sessions
        if m.get("status") == "succeeded"
    ]
    if len(succeeded) < min_sessions:
        return None

    recent    = succeeded[:min_sessions]
    durations = [
        _compute_stats(m, p)["wallSeconds"]
        for m, p in recent
        if _compute_stats(m, p)["wallSeconds"] > 0
    ]

    if not durations:
        return None

    avg_duration = sum(durations) / len(durations)

    if avg_duration >= avg_dur_thresh:
        return None

    return {
        "triggered":    [{"metric": "avg duration",
                          "value":  f"{avg_duration:.0f}s",
                          "threshold": f"{avg_dur_thresh}s"}],
        "sessionCount": len(recent),
        "avgDuration":  avg_duration,
    }


# ---------------------------------------------------------------------------
# Tier table HTML (for index page)
# ---------------------------------------------------------------------------

def _render_tier_table_html(config: dict) -> str:
    tiers    = _resolved_tiers(config)
    overrides = {
        k: v for k, v in (config.get("tierOverrides") or {}).items()
        if not k.startswith("_") and isinstance(v, int) and v in (1, 2, 3)
    }

    tier_badge = {
        1: '<span class="tier-badge t1">Tier 1 &mdash; sync</span>',
        2: '<span class="tier-badge t2">Tier 2 &mdash; fast async</span>',
        3: '<span class="tier-badge t3">Tier 3 &mdash; long async</span>',
    }
    tier_desc = {
        1: "Call once, use result immediately. No sleep.",
        2: "Sleep 30s between status checks.",
        3: "Sleep 30s between polls, cursor discipline, terminal result only.",
    }

    rows = ""
    for tool in sorted(tiers.keys()):
        tier = tiers[tool]
        override_note = ""
        if tool in overrides:
            default_tier = DEFAULT_TIERS.get(tool, "?")
            override_note = (
                f'<span class="override-note">'
                f'&#9888; overridden from Tier {default_tier}</span>'
            )
        rows += (
            f"<tr>"
            f"<td class='mono'>{_html_escape(tool)}</td>"
            f"<td>{tier_badge.get(tier, '?')}{override_note}</td>"
            f"<td class='tier-desc'>{tier_desc.get(tier, '')}</td>"
            f"</tr>\n"
        )

    override_count = len(overrides)
    override_note_header = (
        f" ({override_count} user override{'s' if override_count != 1 else ''})"
        if override_count else ""
    )

    return f"""\
<div class="tier-table-wrap">
  <table>
  <thead>
    <tr>
      <th>Tool</th>
      <th>Tier{override_note_header}</th>
      <th>Polling rule</th>
    </tr>
  </thead>
  <tbody>
{rows}  </tbody>
  </table>
</div>"""


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    """Create a provisional session directory and write .current-session pointer."""
    cache_dir = Path(args.cache).resolve()
    temp_id   = f"pending-{uuid.uuid4().hex[:8]}"
    sess_dir  = cache_dir / "sessions" / temp_id
    sess_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "runId":     temp_id,
        "appKey":    args.app_key or "",
        "appName":   args.app_name or "",
        "startTime": int(time.time()),
        "endTime":   None,
        "status":    "running",
    }
    (sess_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    # Write pointer file — procedure reads this via show-session, no $(...) needed
    (cache_dir / ".current-session").write_text(str(sess_dir), encoding="utf-8")
    return 0


def cmd_update_run_id(args: argparse.Namespace) -> int:
    """Rename the provisional session dir to the real Mentor runId, update pointer."""
    sess_dir = Path(args.session).resolve()
    new_id   = args.run_id.strip()
    if not sess_dir.exists():
        print(f"session dir not found: {sess_dir}", file=sys.stderr)
        return 1
    meta_path = sess_dir / "meta.json"
    if not meta_path.exists():
        print(f"meta.json not found in {sess_dir}", file=sys.stderr)
        return 1
    meta = json.loads(meta_path.read_text("utf-8"))
    meta["runId"] = new_id
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    new_dir = sess_dir.parent / new_id
    if new_dir.exists() and new_dir != sess_dir:
        print(f"target dir already exists: {new_dir}", file=sys.stderr)
        return 1
    if new_dir != sess_dir:
        sess_dir.rename(new_dir)
    # Update the pointer file
    pointer = sess_dir.parent.parent / ".current-session"
    pointer.write_text(str(new_dir), encoding="utf-8")
    return 0


def cmd_show_session(args: argparse.Namespace) -> int:
    """Print the current session dir path from the .current-session pointer file.

    This is the only run.py call that writes to stdout in the procedure,
    and it is called exactly once (before the poll loop) with no command
    substitution — the model reads the printed path and stores it.
    """
    pointer = Path(args.cache).resolve() / ".current-session"
    if not pointer.exists():
        print(f"no current session found in {args.cache}", file=sys.stderr)
        return 1
    print(pointer.read_text("utf-8").strip())
    return 0


def cmd_show_config(_args: argparse.Namespace) -> int:
    """Print the resolved config (defaults merged with user overrides)."""
    config = _load_config()
    tiers  = _resolved_tiers(config)
    config_path = SKILL_DIR / "config.json"

    print(f"Config file: {config_path}")
    print(f"  {'EXISTS' if config_path.exists() else 'NOT FOUND — using all defaults'}")
    print()
    print("Resolved config:")
    print(json.dumps(config, indent=2))
    print()
    print("Resolved tier classification:")
    for tool, tier in sorted(tiers.items()):
        default = DEFAULT_TIERS.get(tool, "?")
        override = " (overridden)" if tool in (config.get("tierOverrides") or {}) else ""
        print(f"  {tool:<28} Tier {tier}{override}")
    return 0


def cmd_record_poll(args: argparse.Namespace) -> int:
    """Append one telemetry line to poll-log.jsonl (silent — no stdout)."""
    sess_dir = Path(args.session).resolve()
    log_path = sess_dir / "poll-log.jsonl"
    sess_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "poll":         int(args.poll),
        "t":            int(time.time()),
        "status":       args.status or "unknown",
        "eventCount":   int(args.event_count)   if args.event_count   is not None else 0,
        "payloadBytes": int(args.payload_bytes) if args.payload_bytes is not None else 0,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    """Write end-time + final status to meta.json (silent — no stdout).

    Findings are NOT stored here — they are displayed inline in the
    conversation from the Mentor terminal result. Storing them via any
    Bash mechanism (shell variable, file write, pipe) triggers Claude
    Code permission prompts due to special characters in the content.
    """
    sess_dir  = Path(args.session).resolve()
    meta_path = sess_dir / "meta.json"
    if not meta_path.exists():
        print(f"meta.json not found: {meta_path}", file=sys.stderr)
        return 1
    meta = json.loads(meta_path.read_text("utf-8"))
    meta["endTime"] = int(time.time())
    meta["status"]  = args.status or "unknown"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    """Print a terminal polling summary to stdout."""
    config      = _load_config()
    sess_dir    = Path(args.session).resolve()
    meta, polls = _load_session(sess_dir)
    stats       = _compute_stats(meta, polls)

    tier3 = config["polling"]["tier3CadenceSecs"]
    tier2 = config["polling"]["tier2CadenceSecs"]
    wall  = _fmt_duration(stats["wallSeconds"])
    byt   = _fmt_bytes(stats["totalBytes"])
    tok   = _fmt_tokens(stats["totalBytes"])
    avoid = _fmt_bytes(stats["bytesAvoided"])

    print(f"\nPolling summary: {stats['totalPolls']} polls · {wall} · "
          f"~{byt} received · ~{tok} token-equivalent")
    print(f"Cadence applied: Tier 3 = {tier3}s  |  Tier 2 = {tier2}s")
    print(f"outsystems-mentor-polling-behavior: {stats['pollsReductionPct']}% fewer polls "
          f"({stats['totalPolls']:,} vs {stats['polls500ms']:,} at 500ms) · "
          f"{stats['bytesReductionPct']}% context saved "
          f"({_fmt_bytes(stats['bytesAvoided'])} of {_fmt_bytes(stats['bytesAvoided'] + stats['totalBytes'])}).")
    print()
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    """Generate index.html and all detail.html files from session data."""
    config     = _load_config()
    cache_dir  = Path(args.cache).resolve()
    sess_root  = cache_dir / "sessions"
    index_path = cache_dir / "index.html"

    stale_days    = config["dashboard"]["staleSessionDays"]
    tier3_cadence = config["polling"]["tier3CadenceSecs"]

    if not sess_root.exists():
        html = _render_template(
            "template-index.html",
            SESSION_COUNT   = "0",
            STATS_HTML      = _render_index_stats_html([]),
            SIGNAL_HTML     = "",
            TABLE_HTML      = '<p class="empty">No sessions recorded yet. Run the skill against an app to start tracking.</p>',
            TIER_TABLE_HTML = _render_tier_table_html(config),
        )
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(html, encoding="utf-8")
        print(f"wrote {index_path} (empty)")
        return 0

    # Collect + sort sessions newest first
    sessions: list[tuple[dict, list[dict], Path]] = []
    for d in sorted(sess_root.iterdir()):
        if not d.is_dir():
            continue
        meta, polls = _load_session(d)
        if not meta:
            continue
        sessions.append((meta, polls, d))
    sessions.sort(key=lambda x: x[0].get("startTime", 0), reverse=True)

    # Render each detail page
    for meta, polls, sess_dir in sessions:
        _render_detail(meta, polls, sess_dir, config)

    # Feedback signal
    signal = _compute_feedback_signal(sessions, config)
    signal_html = _render_signal_html(signal, config) if signal else ""

    # Session table rows
    rows = ""
    _em       = "\u2014"   # em dash — pre-3.12 cannot use backslash escapes inside f-strings
    _ellipsis = "\u2026"   # horizontal ellipsis
    _stale_cls = '  class="stale"'
    for meta, polls, _ in sessions:
        stats    = _compute_stats(meta, polls)
        run_id   = meta.get("runId", _em)
        stale    = _is_stale(meta, stale_days)
        app_name = _html_escape(meta.get("appName", _em))
        status   = meta.get("status", _em)
        sc       = _stale_cls if stale else ""
        rid_disp = run_id[:16] + _ellipsis if len(run_id) > 16 else run_id
        rows += (
            f'<tr{sc}>'
            f'<td><a href="sessions/{run_id}/detail.html" class="mono">'
            f'{rid_disp}</a></td>'
            f'<td>{app_name}</td>'
            f'<td class="mono">{_ts_to_date(meta.get("startTime", 0))}</td>'
            f'<td><span class="badge {_badge_class(status)}">'
            f'{status}</span></td>'
            f'<td>{stats["totalPolls"]}</td>'
            f'<td>{_fmt_duration(stats["wallSeconds"])}</td>'
            f'<td>{_fmt_bytes(stats["totalBytes"])}</td>'
            f'<td>{_fmt_tokens(stats["totalBytes"])}</td>'
            '</tr>\n'
        )

    if sessions:
        table_html = (
            '<table><thead><tr>'
            '<th>Run ID</th><th>App</th><th>Date</th><th>Status</th>'
            '<th>Polls</th><th>Wall time</th><th>~Payload</th><th>~Tokens</th>'
            '</tr></thead><tbody>'
            + rows +
            '</tbody></table>'
        )
    else:
        table_html = '<p class="empty">No sessions recorded yet.</p>'

    count = len(sessions)
    html = _render_template(
        "template-index.html",
        SESSION_COUNT   = str(count),
        STATS_HTML      = _render_index_stats_html(sessions),
        SIGNAL_HTML     = signal_html,
        TABLE_HTML      = table_html,
        TIER_TABLE_HTML = _render_tier_table_html(config),
    )
    index_path.write_text(html, encoding="utf-8")
    print(f"wrote {index_path} ({count} session{'s' if count != 1 else ''})")
    return 0


def _render_signal_html(signal: dict, config: dict) -> str:
    """Render the feedback signal panel HTML (tenant-architecture style)."""
    fb         = config.get("feedback", {})
    thresholds = fb.get("thresholds", {})
    dur_thresh = thresholds.get("avgMentorDurationSecs", 60)

    return f"""\
<div class="signal-panel">
  <h2>&#9888;&#65039; Tier Review Signal</h2>
  <p>
    Rolling average Mentor run duration across the last {signal['sessionCount']}
    succeeded sessions ({signal['avgDuration']:.0f}s) has dropped below the
    configured threshold ({dur_thresh}s). Mentor may be completing faster than
    when the Tier 3 classification was set &#8212; consider whether the 30s
    cadence is still appropriate, or raise the threshold in
    <code>config.json</code> to suppress this signal.
  </p>
  <div class="metrics">
    <div class="m">Avg duration: <span>{signal['avgDuration']:.0f}s</span> (threshold: {dur_thresh}s)</div>
  </div>
</div>"""


def _render_index_stats_html(sessions: list) -> str:
    """Render the stat cards row for the index page."""
    total       = len(sessions)
    succeeded   = sum(1 for m, _, __ in sessions if m.get("status") == "succeeded")
    failed      = sum(1 for m, _, __ in sessions if m.get("status") == "failed")
    all_stats   = [_compute_stats(m, p) for m, p, _ in sessions]
    all_polls   = sum(s["totalPolls"]   for s in all_stats)
    all_500ms   = sum(s["polls500ms"]   for s in all_stats)
    all_saved   = sum(s["pollsSaved"]   for s in all_stats)
    all_avoided = sum(s["bytesAvoided"] for s in all_stats)
    all_bytes   = sum(s["totalBytes"]   for s in all_stats)
    polls_pct   = round(all_saved / all_500ms * 100) if all_500ms else 0
    return f"""\
  <div class="stat" style="--accent:var(--os-red)">
    <div class="stat-label">Total sessions</div>
    <div class="stat-value">{total}</div>
    <div class="stat-detail">all apps</div>
  </div>
  <div class="stat" style="--accent:var(--c-ok)">
    <div class="stat-label">Succeeded</div>
    <div class="stat-value">{succeeded}</div>
    <div class="stat-detail">terminal OK</div>
  </div>
  <div class="stat" style="--accent:var(--c-fail)">
    <div class="stat-label">Failed</div>
    <div class="stat-value">{failed}</div>
    <div class="stat-detail">terminal error</div>
  </div>
  <div class="stat" style="--accent:var(--c-run)">
    <div class="stat-label">Polls reduced</div>
    <div class="stat-value">{polls_pct}%</div>
    <div class="stat-detail">{all_polls:,} polls vs {all_500ms:,} at 500ms</div>
  </div>
  <div class="stat" style="--accent:var(--c-purple)">
    <div class="stat-label">Context received</div>
    <div class="stat-value">{_fmt_bytes(all_bytes)}</div>
    <div class="stat-detail">~{_fmt_bytes(all_avoided)} extrapolated at 500ms</div>
  </div>"""


def _render_detail(
    meta: dict,
    polls: list[dict],
    sess_dir: Path,
    config: dict,
) -> None:
    """Write detail.html for one session."""
    stats         = _compute_stats(meta, polls)
    run_id        = meta.get("runId", "—")
    tier3_cadence = config["polling"]["tier3CadenceSecs"]
    detail_path   = sess_dir / "detail.html"

    # Poll timeline rows
    poll_rows  = ""
    cumulative = 0
    prev_t     = meta.get("startTime", 0)
    for p in polls:
        t          = p.get("t", 0)
        delta      = t - prev_t if prev_t else 0
        prev_t     = t
        cumulative += p.get("payloadBytes", 0)
        status     = p.get("status", "—")
        poll_rows += (
            f"      <tr>"
            f"<td>{p.get('poll', '—')}</td>"
            f"<td class='mono'>{_ts_to_date(t)}</td>"
            f"<td class='mono'>+{delta}s</td>"
            f"<td><span class='badge {_badge_class(status)}'>{status}</span></td>"
            f"<td>{p.get('eventCount', '—')}</td>"
            f"<td class='mono'>{_fmt_bytes(p.get('payloadBytes', 0))}</td>"
            f"<td class='mono'>{_fmt_bytes(cumulative)}</td>"
            f"</tr>\n"
        )
    if not poll_rows:
        poll_rows = "        <tr><td colspan='7' style='color:var(--os-text-dim);text-align:center;padding:20px'>No poll data recorded</td></tr>\n"

    html = _render_template(
        "template-detail.html",
        RUN_ID_SHORT        = run_id[:16] + ("\u2026" if len(run_id) > 16 else ""),
        APP_NAME            = _html_escape(meta.get("appName", "\u2014")),
        DATE                = _ts_to_date(meta.get("startTime", 0)),
        BADGE_CLASS         = _badge_class(meta.get("status", "")),
        STATUS              = meta.get("status", "\u2014"),
        TOTAL_POLLS         = str(stats["totalPolls"]),
        POLLS_500MS         = f"{stats['polls500ms']:,}",
        TIER3_CADENCE       = str(tier3_cadence),
        WALL_TIME           = _fmt_duration(stats["wallSeconds"]),
        PAYLOAD_HUMAN       = _fmt_bytes(stats["totalBytes"]),
        TOKEN_PROXY         = _fmt_tokens(stats["totalBytes"]),
        POLLS_SAVED_PCT     = _fmt_pct(stats["pollsReductionPct"]),
        POLLS_SAVED_DETAIL  = f"{stats['totalPolls']:,} polls vs {stats['polls500ms']:,} at 500ms",
        CONTEXT_SAVED_PCT   = _fmt_pct(stats["pollsReductionPct"]),
        CONTEXT_SAVED_DETAIL= f"{_fmt_bytes(stats['totalBytes'])} received · ~{_fmt_bytes(stats['bytesAvoided'])} extrapolated at 500ms",
        POLL_ROWS           = poll_rows,
    )
    detail_path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Cross-session summary
# ---------------------------------------------------------------------------

def cmd_summary(args: argparse.Namespace) -> int:
    """Output structured JSON summarising all sessions for model interpretation.

    Covers:
      Option A — cross-session stats: app breakdown, totals (polls saved,
                 bytes avoided, wall time), session counts.
      Option B — trend analysis: oldest-half vs newest-half avg duration
                 and poll count, direction, change percent.

    The model reads this JSON and produces the A+B narrative. run.py does
    not generate prose — that is the model's job.
    """
    config    = _load_config()
    cache_dir = Path(args.cache).resolve()
    sess_root = cache_dir / "sessions"

    if not sess_root.exists():
        print(json.dumps({"sessionCount": 0, "message": "No sessions recorded yet."}))
        return 0

    # Load all sessions newest-first
    sessions: list[tuple[dict, list[dict]]] = []
    for d in sorted(sess_root.iterdir()):
        if not d.is_dir():
            continue
        meta, polls = _load_session(d)
        if not meta:
            continue
        sessions.append((meta, polls))
    sessions.sort(key=lambda x: x[0].get("startTime", 0), reverse=True)

    if not sessions:
        print(json.dumps({"sessionCount": 0, "message": "No sessions recorded yet."}))
        return 0

    succeeded = [s for s in sessions if s[0].get("status") == "succeeded"]
    failed    = [s for s in sessions if s[0].get("status") == "failed"]
    cancelled = [s for s in sessions if s[0].get("status") == "cancelled"]

    # Per-app breakdown
    app_map: dict[str, dict] = {}
    for meta, _ in sessions:
        name = meta.get("appName") or meta.get("appKey") or "unknown"
        if name not in app_map:
            app_map[name] = {"appName": name, "sessionCount": 0, "lastRun": ""}
        app_map[name]["sessionCount"] += 1
        ts = meta.get("startTime", 0)
        date = _ts_to_date(ts)[:10] if ts else ""
        if not app_map[name]["lastRun"] or date > app_map[name]["lastRun"]:
            app_map[name]["lastRun"] = date
    apps = sorted(app_map.values(), key=lambda x: -x["sessionCount"])

    # Totals across all sessions
    all_stats = [_compute_stats(m, p) for m, p in sessions]
    totals = {
        "pollsSaved":   sum(s["pollsSaved"]   for s in all_stats),
        "bytesAvoided": sum(s["bytesAvoided"] for s in all_stats),
        "totalBytes":   sum(s["totalBytes"]   for s in all_stats),
        "wallSeconds":  sum(s["wallSeconds"]  for s in all_stats),
        "totalPolls":   sum(s["totalPolls"]   for s in all_stats),
    }

    # Trend: split succeeded sessions into oldest half vs newest half
    # Sessions are newest-first, so reverse for chronological order
    trend = None
    if len(succeeded) >= 4:
        chron   = list(reversed(succeeded))
        half    = len(chron) // 2
        older   = chron[:half]
        newer   = chron[half:]

        def _avg(items: list, key: str) -> float:
            vals = [_compute_stats(m, p)[key] for m, p in items
                    if _compute_stats(m, p)["wallSeconds"] > 0]
            return sum(vals) / len(vals) if vals else 0.0

        older_dur   = _avg(older, "wallSeconds")
        newer_dur   = _avg(newer, "wallSeconds")
        older_polls = _avg(older, "totalPolls")
        newer_polls = _avg(newer, "totalPolls")

        if older_dur > 0:
            change_pct = round((older_dur - newer_dur) / older_dur * 100, 1)
            direction  = "faster" if newer_dur < older_dur else (
                         "slower" if newer_dur > older_dur else "stable")
        else:
            change_pct = 0.0
            direction  = "stable"

        trend = {
            "periods": [
                {
                    "label":           f"oldest {half} sessions",
                    "avgDurationSecs": round(older_dur, 1),
                    "avgPolls":        round(older_polls, 1),
                },
                {
                    "label":           f"newest {len(newer)} sessions",
                    "avgDurationSecs": round(newer_dur, 1),
                    "avgPolls":        round(newer_polls, 1),
                },
            ],
            "direction":     direction,
            "changePercent": change_pct,
        }

    fb         = config.get("feedback", {})
    thresholds = fb.get("thresholds", {})
    output = {
        "sessionCount":   len(sessions),
        "succeededCount": len(succeeded),
        "failedCount":    len(failed),
        "cancelledCount": len(cancelled),
        "apps":           apps,
        "totals":         totals,
        "trend":          trend,
        "config": {
            "tier3CadenceSecs":     config["polling"]["tier3CadenceSecs"],
            "tier2CadenceSecs":     config["polling"]["tier2CadenceSecs"],
            "avgDurationThreshold": thresholds.get("avgMentorDurationSecs", 60),
        },
    }
    print(json.dumps(output, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Argument dispatch
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    # init
    sp = sub.add_parser("init", help="Create a provisional session directory, write .current-session pointer")
    sp.add_argument("--cache",    required=True)
    sp.add_argument("--app-key",  required=True)
    sp.add_argument("--app-name", required=True)

    # update-run-id
    sp = sub.add_parser("update-run-id", help="Rename provisional session dir to real Mentor runId, update pointer")
    sp.add_argument("--session", required=True)
    sp.add_argument("--run-id",  required=True)

    # show-session
    sp = sub.add_parser("show-session", help="Print the current session dir path from .current-session pointer")
    sp.add_argument("--cache", required=True)

    # show-config
    sub.add_parser("show-config", help="Print the resolved config (defaults + user overrides)")

    # record-poll
    sp = sub.add_parser("record-poll", help="Append one telemetry entry to poll-log.jsonl (silent)")
    sp.add_argument("--session",       required=True)
    sp.add_argument("--poll",          required=True, type=int)
    sp.add_argument("--status",        required=True)
    sp.add_argument("--event-count",   type=int, default=0)
    sp.add_argument("--payload-bytes", type=int, default=0)

    # finalize
    sp = sub.add_parser("finalize", help="Write end-time + final status to meta.json (silent)")
    sp.add_argument("--session", required=True)
    sp.add_argument("--status",  required=True)

    # summarize
    sp = sub.add_parser("summarize", help="Print terminal polling summary to stdout")
    sp.add_argument("--session", required=True)

    # summary
    sp = sub.add_parser("summary", help="Output structured JSON of cross-session stats and trends for model interpretation")
    sp.add_argument("--cache", required=True)

    # render
    sp = sub.add_parser("render", help="Generate index.html + all detail.html files")
    sp.add_argument("--cache", required=True)

    args = p.parse_args(argv)

    dispatch = {
        "init":           cmd_init,
        "update-run-id":  cmd_update_run_id,
        "show-session":   cmd_show_session,
        "show-config":    cmd_show_config,
        "record-poll":    cmd_record_poll,
        "finalize":       cmd_finalize,
        "summarize":      cmd_summarize,
        "summary":        cmd_summary,
        "render":         cmd_render,
    }
    fn = dispatch.get(args.cmd)
    if fn:
        return fn(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
