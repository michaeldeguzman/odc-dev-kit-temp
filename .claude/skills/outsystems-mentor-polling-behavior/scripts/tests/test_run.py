# tests/test_run.py
# outsystems-mentor-polling-behavior — run.py test suite
# SFTDD — tests added one use case at a time via Red→Green→Enhancement→Refactor.

import json
import pytest
from run import _load_config, _deep_merge, _resolved_tiers, DEFAULT_TIERS, _CONFIG_DEFAULTS


# ---------------------------------------------------------------------------
# UC#1 — Config loading with deep merge and graceful fallback
# ---------------------------------------------------------------------------

def test_deep_merge_returns_defaults_when_override_empty():
    result = _deep_merge({"a": 1, "b": 2}, {})
    assert result == {"a": 1, "b": 2}


def test_deep_merge_override_wins():
    result = _deep_merge({"a": 1, "b": 2}, {"b": 99})
    assert result["b"] == 99
    assert result["a"] == 1


def test_deep_merge_nested():
    base = {"polling": {"tier2CadenceSecs": 30, "tier3CadenceSecs": 30}}
    override = {"polling": {"tier3CadenceSecs": 15}}
    result = _deep_merge(base, override)
    assert result["polling"]["tier3CadenceSecs"] == 15
    assert result["polling"]["tier2CadenceSecs"] == 30


def test_deep_merge_skips_comment_keys():
    result = _deep_merge({"a": 1}, {"_comment": "ignore me", "a": 2})
    assert result["a"] == 2
    assert "_comment" not in result


def test_load_config_returns_defaults_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    config = _load_config()
    assert config["polling"]["tier2CadenceSecs"] == 30
    assert config["polling"]["tier3CadenceSecs"] == 30
    assert config["feedback"]["enabled"] is True


def test_load_config_returns_defaults_on_malformed_json(tmp_path, monkeypatch):
    (tmp_path / "config.json").write_text("NOT JSON {{{", encoding="utf-8")
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    config = _load_config()
    assert config["polling"]["tier3CadenceSecs"] == 30


def test_load_config_merges_partial_override(tmp_path, monkeypatch):
    (tmp_path / "config.json").write_text(
        json.dumps({"polling": {"tier3CadenceSecs": 15}}), encoding="utf-8"
    )
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    config = _load_config()
    assert config["polling"]["tier3CadenceSecs"] == 15
    assert config["polling"]["tier2CadenceSecs"] == 30


def test_resolved_tiers_returns_defaults_when_no_overrides():
    config = _deep_merge(_CONFIG_DEFAULTS, {})
    tiers = _resolved_tiers(config)
    assert tiers["app_list"] == 1
    assert tiers["publish_start"] == 2
    assert tiers["mentor_get_run"] == 3


def test_resolved_tiers_applies_valid_override():
    config = _deep_merge(_CONFIG_DEFAULTS, {"tierOverrides": {"publish_start": 1}})
    tiers = _resolved_tiers(config)
    assert tiers["publish_start"] == 1


def test_resolved_tiers_ignores_invalid_tier_value():
    config = _deep_merge(_CONFIG_DEFAULTS, {"tierOverrides": {"publish_start": 99}})
    tiers = _resolved_tiers(config)
    assert tiers["publish_start"] == 2


def test_resolved_tiers_ignores_comment_keys():
    config = _deep_merge(_CONFIG_DEFAULTS, {"tierOverrides": {"_comment": "ignore"}})
    tiers = _resolved_tiers(config)
    assert "_comment" not in tiers


def test_deep_merge_does_not_mutate_base():
    base = {"a": {"x": 1}}
    _deep_merge(base, {"a": {"x": 2}})
    assert base["a"]["x"] == 1


def test_load_config_strips_comment_keys_from_tier_overrides(tmp_path, monkeypatch):
    cfg = {"tierOverrides": {"_comment": "a note", "publish_start": 1}}
    (tmp_path / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    config = _load_config()
    tiers = _resolved_tiers(config)
    assert "_comment" not in tiers
    assert tiers["publish_start"] == 1


def test_resolved_tiers_new_tool_added_via_override():
    config = _deep_merge(_CONFIG_DEFAULTS, {"tierOverrides": {"brand_new_tool": 2}})
    tiers = _resolved_tiers(config)
    assert tiers["brand_new_tool"] == 2


def test_resolved_tiers_ignores_non_int_tier_value():
    config = _deep_merge(_CONFIG_DEFAULTS, {"tierOverrides": {"publish_start": "fast"}})
    tiers = _resolved_tiers(config)
    assert tiers["publish_start"] == 2  # default preserved


# ---------------------------------------------------------------------------
# UC#2 — Session init — create provisional session directory
# ---------------------------------------------------------------------------

import sys
from pathlib import Path
from run import main as run_main


def test_init_creates_session_dir_and_meta(tmp_path):
    result = run_main([
        "init",
        "--cache", str(tmp_path),
        "--app-key", "key-abc",
        "--app-name", "MyApp",
    ])
    assert result == 0
    sessions = list((tmp_path / "sessions").iterdir())
    assert len(sessions) == 1
    meta = json.loads((sessions[0] / "meta.json").read_text())
    assert meta["appKey"] == "key-abc"
    assert meta["appName"] == "MyApp"
    assert "prompt"   not in meta    # prompt is never stored
    assert "findings" not in meta    # findings are never stored
    assert meta["status"] == "running"
    assert meta["endTime"] is None
    assert meta["runId"].startswith("pending-")


def test_init_writes_current_session_pointer(tmp_path):
    run_main(["init", "--cache", str(tmp_path),
              "--app-key", "k", "--app-name", "A"])
    pointer = tmp_path / ".current-session"
    assert pointer.exists()
    sess_path = Path(pointer.read_text().strip())
    assert sess_path.is_dir()
    assert (sess_path / "meta.json").exists()


def test_init_produces_no_stdout(tmp_path, capsys):
    run_main(["init", "--cache", str(tmp_path),
              "--app-key", "k", "--app-name", "A"])
    out = capsys.readouterr().out
    assert out == ""


def test_init_creates_parent_dirs_if_missing(tmp_path):
    deep_cache = tmp_path / "a" / "b" / "c"
    result = run_main([
        "init", "--cache", str(deep_cache),
        "--app-key", "k", "--app-name", "A",
    ])
    assert result == 0
    assert (deep_cache / "sessions").exists()


def test_init_stores_start_time_as_int(tmp_path):
    run_main(["init", "--cache", str(tmp_path),
              "--app-key", "k", "--app-name", "A"])
    sessions = list((tmp_path / "sessions").iterdir())
    meta = json.loads((sessions[0] / "meta.json").read_text())
    assert isinstance(meta["startTime"], int)
    assert meta["startTime"] > 0


def test_init_each_call_produces_unique_session_dir(tmp_path):
    for _ in range(3):
        run_main(["init", "--cache", str(tmp_path),
                  "--app-key", "k", "--app-name", "A"])
    sessions = list((tmp_path / "sessions").iterdir())
    assert len(sessions) == 3
    names = {s.name for s in sessions}
    assert len(names) == 3  # all unique


# ---------------------------------------------------------------------------
# UC#3 — Session rename — update provisional ID to real Mentor runId
# ---------------------------------------------------------------------------

def _make_session(tmp_path, run_main, app_key="k", app_name="A"):
    """Helper: init a session and return the provisional session dir path."""
    run_main(["init", "--cache", str(tmp_path),
              "--app-key", app_key, "--app-name", app_name])
    return Path((tmp_path / ".current-session").read_text().strip())


def test_update_run_id_renames_dir(tmp_path):
    sess = _make_session(tmp_path, run_main)
    result = run_main(["update-run-id", "--session", str(sess), "--run-id", "real-run-001"])
    assert result == 0
    assert not sess.exists()
    assert (tmp_path / "sessions" / "real-run-001").exists()


def test_update_run_id_updates_meta_json(tmp_path):
    sess = _make_session(tmp_path, run_main)
    run_main(["update-run-id", "--session", str(sess), "--run-id", "real-run-002"])
    meta = json.loads((tmp_path / "sessions" / "real-run-002" / "meta.json").read_text())
    assert meta["runId"] == "real-run-002"


def test_update_run_id_updates_current_session_pointer(tmp_path):
    sess = _make_session(tmp_path, run_main)
    run_main(["update-run-id", "--session", str(sess), "--run-id", "real-run-003"])
    pointer_val = Path((tmp_path / ".current-session").read_text().strip())
    assert pointer_val.name == "real-run-003"
    assert pointer_val.exists()


def test_update_run_id_produces_no_stdout(tmp_path, capsys):
    sess = _make_session(tmp_path, run_main)
    run_main(["update-run-id", "--session", str(sess), "--run-id", "real-run-004"])
    out = capsys.readouterr().out
    assert out == ""


def test_update_run_id_fails_when_session_missing(tmp_path):
    result = run_main(["update-run-id",
                       "--session", str(tmp_path / "sessions" / "ghost"),
                       "--run-id", "x"])
    assert result == 1


def test_update_run_id_fails_when_meta_missing(tmp_path):
    sess = _make_session(tmp_path, run_main)
    (sess / "meta.json").unlink()
    result = run_main(["update-run-id", "--session", str(sess), "--run-id", "x"])
    assert result == 1


def test_update_run_id_fails_on_collision(tmp_path):
    sess = _make_session(tmp_path, run_main)
    # Pre-create the target dir to trigger collision
    (tmp_path / "sessions" / "collision").mkdir(parents=True)
    result = run_main(["update-run-id", "--session", str(sess), "--run-id", "collision"])
    assert result == 1


# ---------------------------------------------------------------------------
# UC#4 — Poll recording — append telemetry to poll-log.jsonl
# ---------------------------------------------------------------------------

def test_record_poll_appends_entry(tmp_path):
    sess = tmp_path / "sessions" / "run-1"
    sess.mkdir(parents=True)
    before = int(__import__("time").time())
    run_main(["record-poll", "--session", str(sess),
              "--poll", "0", "--status", "running",
              "--event-count", "3", "--payload-bytes", "1200"])
    after = int(__import__("time").time())
    lines = (sess / "poll-log.jsonl").read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["poll"] == 0
    assert entry["status"] == "running"
    assert entry["eventCount"] == 3
    assert entry["payloadBytes"] == 1200
    assert before <= entry["t"] <= after + 1
    assert "cursor" not in entry          # cursor no longer recorded


def test_record_poll_appends_multiple(tmp_path):
    sess = tmp_path / "sessions" / "run-2"
    sess.mkdir(parents=True)
    for i in range(5):
        run_main(["record-poll", "--session", str(sess),
                  "--poll", str(i), "--status", "running"])
    lines = (sess / "poll-log.jsonl").read_text().splitlines()
    assert len(lines) == 5
    for i, line in enumerate(lines):
        assert json.loads(line)["poll"] == i


def test_record_poll_defaults_counts_to_zero(tmp_path):
    sess = tmp_path / "sessions" / "run-3"
    sess.mkdir(parents=True)
    run_main(["record-poll", "--session", str(sess),
              "--poll", "0", "--status", "running"])
    entry = json.loads((sess / "poll-log.jsonl").read_text())
    assert entry["eventCount"] == 0
    assert entry["payloadBytes"] == 0


def test_record_poll_creates_session_dir_if_missing(tmp_path):
    sess = tmp_path / "sessions" / "run-5"
    assert not sess.exists()
    result = run_main(["record-poll", "--session", str(sess),
                       "--poll", "0", "--status", "running"])
    assert result == 0
    assert (sess / "poll-log.jsonl").exists()


# ---------------------------------------------------------------------------
# UC#5 — Session finalize — write terminal state to meta.json
# ---------------------------------------------------------------------------

def _make_finalized_session(tmp_path, run_main, status="succeeded"):
    sess = _make_session(tmp_path, run_main)
    new_sess = Path(str(sess).replace(sess.name, "run-fin"))
    run_main(["update-run-id", "--session", str(sess), "--run-id", "run-fin"])
    run_main(["finalize", "--session", str(new_sess), "--status", status])
    return new_sess


def test_finalize_writes_status_and_end_time(tmp_path):
    before = int(__import__("time").time())
    sess = _make_finalized_session(tmp_path, run_main, status="succeeded")
    after = int(__import__("time").time())
    meta = json.loads((sess / "meta.json").read_text())
    assert meta["status"] == "succeeded"
    assert before <= meta["endTime"] <= after + 1


def test_finalize_does_not_store_findings(tmp_path):
    sess = _make_finalized_session(tmp_path, run_main)
    meta = json.loads((sess / "meta.json").read_text())
    assert "findings" not in meta


def test_finalize_fails_when_meta_missing(tmp_path):
    sess = tmp_path / "ghost"
    sess.mkdir()
    result = run_main(["finalize", "--session", str(sess), "--status", "succeeded"])
    assert result == 1


def test_finalize_always_uses_current_time(tmp_path):
    sess = _make_session(tmp_path, run_main)
    run_main(["update-run-id", "--session", str(sess), "--run-id", "run-ct"])
    new_sess = sess.parent / "run-ct"
    before = int(__import__("time").time())
    run_main(["finalize", "--session", str(new_sess), "--status", "succeeded"])
    after = int(__import__("time").time())
    meta = json.loads((new_sess / "meta.json").read_text())
    assert before <= meta["endTime"] <= after + 1


# ---------------------------------------------------------------------------
# UC#6 — Stats computation
# ---------------------------------------------------------------------------

from run import _compute_stats, _fmt_bytes, _fmt_duration, _fmt_tokens


def test_compute_stats_basic():
    meta  = {"startTime": 1000, "endTime": 1250}
    polls = [
        {"payloadBytes": 1000},
        {"payloadBytes": 2000},
        {"payloadBytes": 500},
    ]
    s = _compute_stats(meta, polls)
    assert s["totalPolls"]  == 3
    assert s["totalBytes"]  == 3500
    assert s["wallSeconds"] == 250
    assert s["polls500ms"]  == 500   # ceil(250 / 0.5)
    assert s["pollsSaved"]  == 497   # 500 - 3


def test_compute_stats_zero_polls():
    meta = {"startTime": 1000, "endTime": 1060}
    s = _compute_stats(meta, [])
    assert s["totalPolls"] == 0
    assert s["totalBytes"] == 0
    assert s["wallSeconds"] == 60


def test_compute_stats_missing_times():
    s = _compute_stats({}, [])
    assert s["wallSeconds"] == 0
    assert s["polls500ms"]  == 0
    assert s["pollsSaved"]  == 0


def test_compute_stats_polls_saved_never_negative():
    meta  = {"startTime": 1000, "endTime": 1001}  # 1s wall → polls500ms = 2
    polls = [{"payloadBytes": 0}] * 10             # 10 polls > 2
    s = _compute_stats(meta, polls)
    assert s["pollsSaved"] == 0


def test_fmt_bytes_bytes():
    assert _fmt_bytes(0)    == "0 B"
    assert _fmt_bytes(512)  == "512 B"
    assert _fmt_bytes(1023) == "1023 B"


def test_fmt_bytes_kilobytes():
    assert _fmt_bytes(1024)    == "1.0 KB"
    assert _fmt_bytes(1536)    == "1.5 KB"
    assert _fmt_bytes(1024*10) == "10.0 KB"


def test_fmt_bytes_megabytes():
    assert _fmt_bytes(1024 * 1024)     == "1.00 MB"
    assert _fmt_bytes(1024 * 1024 * 2) == "2.00 MB"


def test_fmt_duration_seconds():
    assert _fmt_duration(0)  == "0s"
    assert _fmt_duration(45) == "45s"
    assert _fmt_duration(59) == "59s"


def test_fmt_duration_minutes():
    assert _fmt_duration(60)  == "1m 00s"
    assert _fmt_duration(90)  == "1m 30s"
    assert _fmt_duration(125) == "2m 05s"


def test_fmt_tokens_small():
    assert _fmt_tokens(0)    == "0"
    assert _fmt_tokens(400)  == "100"
    assert _fmt_tokens(3999) == "999"


def test_fmt_tokens_thousands():
    assert _fmt_tokens(4000)  == "1.0K"
    assert _fmt_tokens(40000) == "10.0K"


# ---------------------------------------------------------------------------
# UC#7 — Session loading — read meta.json and poll-log.jsonl
# ---------------------------------------------------------------------------

from run import _load_session, _is_stale
import time as _time_mod


def test_load_session_reads_meta_and_polls(tmp_path):
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "meta.json").write_text(json.dumps({"runId": "r1", "appName": "App"}))
    (sess / "poll-log.jsonl").write_text(
        json.dumps({"poll": 0, "payloadBytes": 100}) + "\n" +
        json.dumps({"poll": 1, "payloadBytes": 200}) + "\n"
    )
    meta, polls = _load_session(sess)
    assert meta["runId"] == "r1"
    assert len(polls) == 2
    assert polls[1]["payloadBytes"] == 200


def test_load_session_missing_meta_returns_empty(tmp_path):
    sess = tmp_path / "s"
    sess.mkdir()
    meta, polls = _load_session(sess)
    assert meta == {}
    assert polls == []


def test_load_session_missing_log_returns_empty_polls(tmp_path):
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "meta.json").write_text(json.dumps({"runId": "r1"}))
    meta, polls = _load_session(sess)
    assert meta["runId"] == "r1"
    assert polls == []


def test_load_session_skips_malformed_jsonl_lines(tmp_path):
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "meta.json").write_text("{}")
    (sess / "poll-log.jsonl").write_text(
        '{"poll": 0}\nNOT JSON\n{"poll": 2}\n'
    )
    _, polls = _load_session(sess)
    assert len(polls) == 2
    assert polls[0]["poll"] == 0
    assert polls[1]["poll"] == 2


def test_load_session_skips_blank_lines(tmp_path):
    sess = tmp_path / "s"
    sess.mkdir()
    (sess / "meta.json").write_text("{}")
    (sess / "poll-log.jsonl").write_text('\n{"poll": 0}\n\n{"poll": 1}\n\n')
    _, polls = _load_session(sess)
    assert len(polls) == 2


def test_is_stale_old_session(tmp_path):
    old_ts = int(_time_mod.time()) - (40 * 86400)  # 40 days ago
    assert _is_stale({"startTime": old_ts}, stale_days=30) is True


def test_is_stale_fresh_session(tmp_path):
    recent_ts = int(_time_mod.time()) - (10 * 86400)  # 10 days ago
    assert _is_stale({"startTime": recent_ts}, stale_days=30) is False


def test_is_stale_zero_stale_days_never_stale():
    old_ts = int(_time_mod.time()) - (365 * 86400)
    assert _is_stale({"startTime": old_ts}, stale_days=0) is False


def test_is_stale_missing_start_time():
    assert _is_stale({}, stale_days=30) is False


# ---------------------------------------------------------------------------
# UC#8 — Feedback signal — tier review threshold detection
# ---------------------------------------------------------------------------

from run import _compute_feedback_signal
from pathlib import Path as _Path


def _make_sessions(count, status="succeeded", wall_secs=45, polls=3):
    """Build a fake sessions list as _compute_feedback_signal expects."""
    sessions = []
    for i in range(count):
        meta = {
            "startTime": 1000 * (i + 1),
            "endTime":   1000 * (i + 1) + wall_secs,
            "status":    status,
        }
        poll_list = [{"payloadBytes": 100}] * polls
        sessions.append((meta, poll_list, _Path(f"/fake/{i}")))
    return sessions


def test_feedback_signal_not_enough_sessions():
    cfg = _deep_merge(_CONFIG_DEFAULTS, {})
    sessions = _make_sessions(3, wall_secs=10, polls=2)  # below min=5
    assert _compute_feedback_signal(sessions, cfg) is None


def test_feedback_signal_disabled_in_config():
    cfg = _deep_merge(_CONFIG_DEFAULTS, {"feedback": {"enabled": False}})
    sessions = _make_sessions(10, wall_secs=10, polls=2)
    assert _compute_feedback_signal(sessions, cfg) is None


def test_feedback_signal_fires_when_duration_below_threshold():
    cfg = _deep_merge(_CONFIG_DEFAULTS, {})  # avgMentorDurationSecs=60, min=5
    sessions = _make_sessions(6, wall_secs=30, polls=10)  # avg 30s < 60s threshold
    signal = _compute_feedback_signal(sessions, cfg)
    assert signal is not None
    assert signal["triggered"][0]["metric"] == "avg duration"


def test_feedback_signal_none_when_duration_above_threshold():
    cfg = _deep_merge(_CONFIG_DEFAULTS, {})
    sessions = _make_sessions(6, wall_secs=120, polls=10)  # avg 120s > 60s threshold
    assert _compute_feedback_signal(sessions, cfg) is None


def test_feedback_signal_ignores_failed_sessions():
    cfg = _deep_merge(_CONFIG_DEFAULTS, {})
    failed    = _make_sessions(3, status="failed",    wall_secs=5,   polls=1)
    succeeded = _make_sessions(3, status="succeeded", wall_secs=120, polls=10)
    sessions  = failed + succeeded
    # Only 3 succeeded — below min=5, so no signal
    assert _compute_feedback_signal(sessions, cfg) is None


def test_feedback_signal_uses_only_min_sessions_required():
    cfg = _deep_merge(_CONFIG_DEFAULTS, {"feedback": {"minSessionsRequired": 3}})
    fast = _make_sessions(3, wall_secs=10, polls=1)
    slow = _make_sessions(10, wall_secs=200, polls=20)
    sessions = fast + slow  # fast is "newest first"
    signal = _compute_feedback_signal(sessions, cfg)
    assert signal is not None  # fast sessions trigger the threshold


# ---------------------------------------------------------------------------
# UC#8b — Cross-session summary subcommand
# ---------------------------------------------------------------------------


def test_summary_empty_cache(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    result = run_main(["summary", "--cache", str(tmp_path)])
    assert result == 0
    out = json.loads(capsys.readouterr().out)
    assert out["sessionCount"] == 0


def test_summary_counts_sessions(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "s1", status="succeeded", wall=300, n_polls=5)
    _seed_session(tmp_path, "s2", status="succeeded", wall=240, n_polls=4)
    _seed_session(tmp_path, "s3", status="failed",    wall=60,  n_polls=1)
    result = run_main(["summary", "--cache", str(tmp_path)])
    assert result == 0
    out = json.loads(capsys.readouterr().out)
    assert out["sessionCount"]   == 3
    assert out["succeededCount"] == 2
    assert out["failedCount"]    == 1


def test_summary_app_breakdown(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "s1", app_name="BankingPortal", status="succeeded")
    _seed_session(tmp_path, "s2", app_name="BankingPortal", status="succeeded")
    _seed_session(tmp_path, "s3", app_name="TaskTracker",   status="succeeded")
    run_main(["summary", "--cache", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    apps = {a["appName"]: a["sessionCount"] for a in out["apps"]}
    assert apps["BankingPortal"] == 2
    assert apps["TaskTracker"]   == 1


def test_summary_totals(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    # Each session: 4 polls × 5000 bytes = 20000 bytes total
    _seed_session(tmp_path, "s1", status="succeeded", wall=120, n_polls=4)
    _seed_session(tmp_path, "s2", status="succeeded", wall=120, n_polls=4)
    run_main(["summary", "--cache", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert out["totals"]["totalPolls"]  == 8
    assert out["totals"]["totalBytes"]  == 40000
    assert out["totals"]["wallSeconds"] == 240


def test_summary_trend_present_with_enough_sessions(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    # 4 succeeded sessions needed for trend (split into 2+2)
    for i in range(4):
        _seed_session(tmp_path, f"s{i}", status="succeeded", wall=300, n_polls=8)
    run_main(["summary", "--cache", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert out["trend"] is not None
    assert len(out["trend"]["periods"]) == 2
    assert out["trend"]["direction"] in ("faster", "slower", "stable")


def test_summary_trend_none_with_few_sessions(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    # Only 2 succeeded — not enough for trend
    _seed_session(tmp_path, "s1", status="succeeded", wall=300, n_polls=8)
    _seed_session(tmp_path, "s2", status="succeeded", wall=240, n_polls=6)
    run_main(["summary", "--cache", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert out["trend"] is None


def test_summary_includes_config(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "s1", status="succeeded")
    run_main(["summary", "--cache", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert "config" in out
    assert "tier3CadenceSecs"      in out["config"]
    assert "avgDurationThreshold"  in out["config"]
    assert "avgPollThreshold"     not in out["config"]


def _seed_session(cache, run_id, app_name="TestApp",
                  status="succeeded", wall=120, n_polls=4):
    """Create a fully populated session under cache/sessions/<run_id>/."""
    sess = cache / "sessions" / run_id
    sess.mkdir(parents=True)
    start = 1718540000
    end   = start + wall
    meta  = {
        "runId": run_id, "appKey": "k", "appName": app_name,
        "startTime": start, "endTime": end,
        "status": status,
    }
    (sess / "meta.json").write_text(json.dumps(meta))
    with (sess / "poll-log.jsonl").open("w") as f:
        for i in range(n_polls):
            f.write(json.dumps({
                "poll": i, "t": start + i * 30,
                "status": "running" if i < n_polls - 1 else status,
                "eventCount": 2, "payloadBytes": 5000,
            }) + "\n")
    return sess


def _install_templates(skill_dir: Path) -> None:
    """Copy the real asset templates into skill_dir/assets/ for tests that
    monkeypatch SKILL_DIR to tmp_path."""
    import shutil
    real_assets = Path(__file__).resolve().parent.parent.parent / "assets"
    dest_assets = skill_dir / "assets"
    dest_assets.mkdir(parents=True, exist_ok=True)
    for tmpl in ("template-index.html", "template-detail.html"):
        shutil.copy(real_assets / tmpl, dest_assets / tmpl)


def test_render_empty_cache_writes_index(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    result = run_main(["render", "--cache", str(tmp_path)])
    assert result == 0
    index = tmp_path / "index.html"
    assert index.exists()
    content = index.read_text()
    assert "No sessions recorded yet" in content


def test_render_creates_index_and_detail(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "run-abc")
    result = run_main(["render", "--cache", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "sessions" / "run-abc" / "detail.html").exists()


def test_render_index_contains_session_row(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "run-xyz", app_name="BankingPortal")
    run_main(["render", "--cache", str(tmp_path)])
    content = (tmp_path / "index.html").read_text()
    assert "BankingPortal" in content
    assert "run-xyz" in content


def test_render_detail_contains_poll_timeline(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "run-tl", n_polls=3)
    run_main(["render", "--cache", str(tmp_path)])
    detail = (tmp_path / "sessions" / "run-tl" / "detail.html").read_text()
    assert ">0<" in detail or "<td>0</td>" in detail


def test_render_is_idempotent(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "run-idem")
    run_main(["render", "--cache", str(tmp_path)])
    first = (tmp_path / "index.html").read_text()
    run_main(["render", "--cache", str(tmp_path)])
    second = (tmp_path / "index.html").read_text()
    assert first == second


def test_render_multiple_sessions(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    for i in range(3):
        _seed_session(tmp_path, f"run-{i:03d}", app_name=f"App{i}")
    run_main(["render", "--cache", str(tmp_path)])
    content = (tmp_path / "index.html").read_text()
    assert "App0" in content
    assert "App1" in content
    assert "App2" in content
    for i in range(3):
        assert (tmp_path / "sessions" / f"run-{i:03d}" / "detail.html").exists()


def test_render_html_escapes_app_name(tmp_path, monkeypatch):
    _install_templates(tmp_path)
    monkeypatch.setattr("run.SKILL_DIR", tmp_path)
    _seed_session(tmp_path, "run-esc",
                  app_name='App<script>alert("xss")</script>')
    run_main(["render", "--cache", str(tmp_path)])
    detail = (tmp_path / "sessions" / "run-esc" / "detail.html").read_text()
    assert "<script>" not in detail
    assert "&lt;script&gt;" in detail
