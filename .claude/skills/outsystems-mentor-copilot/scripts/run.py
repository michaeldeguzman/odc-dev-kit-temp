#!/usr/bin/env python3
"""
outsystems-mentor-copilot driver.

This script does NOT call Mentor. Mentor is invoked via MCP tools (mentor_start
+ mentor_get_run) by the model loop. This script handles three things only:

  1. Listing the task / workflow library.
  2. Resolving a task or workflow into a concrete prompt (variable substitution),
     emitted to stdout so the SKILL.md procedure pipes it into mentor_start.
  3. Rendering the terminal mentor_get_run result into a markdown report.

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------- IO

SKILL_DIR = Path(__file__).resolve().parent.parent
TASKS_PATH = SKILL_DIR / "templates" / "tasks.json"
WORKFLOWS_PATH = SKILL_DIR / "templates" / "workflows.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def _tasks() -> list[dict]:
    return _load_json(TASKS_PATH)["tasks"]


def _workflows() -> list[dict]:
    return _load_json(WORKFLOWS_PATH)["workflows"]


def _task_by_id(tid: str) -> dict | None:
    return next((t for t in _tasks() if t["id"] == tid), None)


def _workflow_by_id(wid: str) -> dict | None:
    return next((w for w in _workflows() if w["id"] == wid), None)


# ---------------------------------------------------------- Variable resolver

VAR_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def _parse_kv(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            raise SystemExit(f"--var expects key=value, got: {p!r}")
        k, v = p.split("=", 1)
        out[k.strip()] = v
    return out


def _resolve(prompt: str, var_defs: dict[str, dict], overrides: dict[str, str]) -> str:
    """Substitute {{name}} placeholders. Defaults from var_defs; overrides win."""
    resolved: dict[str, str] = {}
    for name, spec in (var_defs or {}).items():
        if name in overrides:
            resolved[name] = overrides[name]
        elif "default" in spec:
            resolved[name] = str(spec["default"])
        elif spec.get("required"):
            raise SystemExit(f"variable {name!r} is required (pass --var {name}=...)")
        else:
            resolved[name] = ""
    # Any override not in var_defs is allowed too (workflow-level vars pass through).
    for k, v in overrides.items():
        resolved.setdefault(k, v)
    return VAR_RE.sub(lambda m: resolved.get(m.group(1), m.group(0)), prompt)


# --------------------------------------------------------------- List commands


def cmd_list_tasks() -> int:
    rows = []
    for t in _tasks():
        rows.append((t["id"], t["category"], t["name"]))
    width_id = max(len(r[0]) for r in rows)
    width_cat = max(len(r[1]) for r in rows)
    for tid, cat, name in rows:
        print(f"{tid:<{width_id}}  {cat:<{width_cat}}  {name}")
    return 0


def cmd_list_workflows() -> int:
    for w in _workflows():
        steps = " -> ".join(s.get("task_id") or "<follow-up>" for s in w["steps"])
        print(f"{w['id']:<28}  {w['name']}")
        print(f"    steps: {steps}")
        print(f"    {w['description']}")
        print()
    return 0


def cmd_show_task(args: argparse.Namespace) -> int:
    t = _task_by_id(args.task)
    if not t:
        raise SystemExit(f"unknown task: {args.task}")
    overrides = _parse_kv(args.var or [])
    prompt = _resolve(t["prompt"], t.get("vars", {}), overrides)
    if args.format == "json":
        print(json.dumps({
            "id": t["id"],
            "name": t["name"],
            "prompt": prompt,
            "mode": t.get("mode"),
        }, indent=2))
    else:
        print(prompt)
    return 0


def cmd_show_workflow(args: argparse.Namespace) -> int:
    w = _workflow_by_id(args.workflow)
    if not w:
        raise SystemExit(f"unknown workflow: {args.workflow}")
    overrides = _parse_kv(args.var or [])
    print(json.dumps({
        "id": w["id"],
        "name": w["name"],
        "steps": _resolve_steps(w["steps"], overrides),
        "terminal": w.get("terminal"),
    }, indent=2))
    return 0


def _resolve_steps(steps: list[dict], overrides: dict[str, str]) -> list[dict]:
    out = []
    for i, s in enumerate(steps):
        if s.get("task_id") and "{{" not in s["task_id"]:
            t = _task_by_id(s["task_id"])
            if not t:
                raise SystemExit(f"step {i}: unknown task_id {s['task_id']}")
            out.append({
                "step": i + 1,
                "kind": "task",
                "task_id": t["id"],
                "prompt": _resolve(t["prompt"], t.get("vars", {}), overrides),
            })
        elif s.get("task_id"):  # parameterized like "{{task_id}}"
            tid = _resolve(s["task_id"], s.get("vars", {}), overrides)
            t = _task_by_id(tid)
            if not t:
                raise SystemExit(f"step {i}: unknown task_id {tid!r}")
            out.append({
                "step": i + 1,
                "kind": "task",
                "task_id": t["id"],
                "prompt": _resolve(t["prompt"], t.get("vars", {}), overrides),
            })
        elif s.get("follow_up_prompt"):
            out.append({
                "step": i + 1,
                "kind": "follow-up",
                "prompt": _resolve(s["follow_up_prompt"], s.get("vars", {}), overrides),
            })
        else:
            raise SystemExit(f"step {i}: must have task_id or follow_up_prompt")
    return out


# ------------------------------------------------------------ Render the report


def _extract_text(events: list[dict]) -> str:
    """Pull the human-readable text out of the event stream. Mentor emits various
    event kinds; we surface 'message' and 'response' content. Best-effort —
    we don't depend on a fixed schema beyond {kind, content?}."""
    chunks: list[str] = []
    for ev in events or []:
        kind = ev.get("kind") or ev.get("type") or ""
        if kind in ("message", "response", "assistant_message", "text"):
            content = ev.get("content") or ev.get("text") or ""
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and "text" in c:
                        chunks.append(c["text"])
            elif isinstance(content, str):
                chunks.append(content)
    return "\n\n".join(c for c in chunks if c.strip())


def cmd_render(args: argparse.Namespace) -> int:
    """Render a markdown report from a terminal mentor_get_run result file."""
    result_path = Path(args.result)
    if not result_path.exists():
        raise SystemExit(f"result file not found: {result_path}")
    raw = json.loads(result_path.read_text("utf-8"))

    # Accept either the full mentor_get_run response OR just its `result` block.
    if "result" in raw and isinstance(raw["result"], dict):
        terminal = raw["result"]
        events = raw.get("events", [])
        status = raw.get("status", "unknown")
    else:
        terminal = raw
        events = raw.get("events", [])
        status = raw.get("status", "succeeded")

    body_text = ""
    if isinstance(terminal, dict):
        # Mentor's terminal result usually has {message, summary, ...}
        body_text = (
            terminal.get("message")
            or terminal.get("summary")
            or terminal.get("text")
            or ""
        )
    if not body_text:
        body_text = _extract_text(events)
    if not body_text:
        body_text = "_(no text content in result — inspect the raw event stream)_"

    task = _task_by_id(args.task) if args.task else None
    workflow = _workflow_by_id(args.workflow) if args.workflow else None

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    md: list[str] = []
    md.append(f"# Mentor co-pilot — {(task or workflow or {}).get('name', 'Run')}")
    md.append("")
    md.append(f"- **Run ID:** `{args.run_id or '-'}`")
    md.append(f"- **App:** `{args.app_key or '-'}`")
    md.append(f"- **Status:** `{status}`")
    md.append(f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    if task:
        md.append(f"- **Task:** `{task['id']}` — {task['description']}")
    if workflow:
        md.append(f"- **Workflow:** `{workflow['id']}` — {workflow['description']}")
    md.append("")

    if args.prompt_file and Path(args.prompt_file).exists():
        md.append("## Prompt used")
        md.append("")
        md.append("```")
        md.append(Path(args.prompt_file).read_text("utf-8").strip())
        md.append("```")
        md.append("")

    md.append("## Mentor response")
    md.append("")
    md.append(body_text.strip())
    md.append("")

    # Publish handoff surfacing — only if a refreshed session token survived.
    session_token = None
    if isinstance(terminal, dict):
        session_token = terminal.get("mentor_session_token")
    if session_token:
        md.append("## Session continuation / publish handoff")
        md.append("")
        md.append(
            "The Mentor session is alive — the refreshed `mentor_session_token` "
            "below is valid for ~24 h. You can either:\n\n"
            "1. **Continue the conversation** — pass `mentor_session_id` + this "
            "token back to `mentor_start` with a follow-up prompt. The server-side "
            "OML and tool history stay loaded.\n"
            "2. **Publish any pending changes** — if Mentor actually modified OML "
            "in this run, call `publish_start` with the token to commit. For "
            "analysis-only tasks this will be a no-op publish; check the response "
            "above for whether Mentor made changes vs. just suggested them.\n\n"
            "Discard by doing nothing — the session expires server-side."
        )
        md.append("")
        md.append("```json")
        md.append(json.dumps({
            "tool": "mcp__outsystems__publish_start",
            "args": {
                "app_key": args.app_key,
                "mentor_session_token": session_token,
            },
        }, indent=2))
        md.append("```")
        md.append("")

    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
    return 0


# --------------------------------------------------------------- arg dispatch


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="run.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-tasks", help="Print the task library")
    sub.add_parser("list-workflows", help="Print the workflow library")

    sp = sub.add_parser("show-task", help="Resolve a task -> concrete prompt")
    sp.add_argument("--task", required=True)
    sp.add_argument("--var", action="append", help="key=value (repeatable)")
    sp.add_argument("--format", default="text", choices=["text", "json"])

    sp = sub.add_parser("show-workflow", help="Resolve a workflow -> step plan")
    sp.add_argument("--workflow", required=True)
    sp.add_argument("--var", action="append")

    sp = sub.add_parser("render", help="Render a markdown report from a terminal mentor_get_run result")
    sp.add_argument("--result", required=True, help="Path to a JSON file containing the terminal mentor_get_run response (or just its `result` block)")
    sp.add_argument("--output", required=True, help="Output markdown path")
    sp.add_argument("--task", help="Task id used (for header)")
    sp.add_argument("--workflow", help="Workflow id used (for header)")
    sp.add_argument("--app-key", help="App key (for header)")
    sp.add_argument("--run-id", help="Mentor run id (for header)")
    sp.add_argument("--prompt-file", help="Optional path to the resolved prompt (included verbatim in the report)")

    args = p.parse_args(argv)

    if args.cmd == "list-tasks":
        return cmd_list_tasks()
    if args.cmd == "list-workflows":
        return cmd_list_workflows()
    if args.cmd == "show-task":
        return cmd_show_task(args)
    if args.cmd == "show-workflow":
        return cmd_show_workflow(args)
    if args.cmd == "render":
        return cmd_render(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
