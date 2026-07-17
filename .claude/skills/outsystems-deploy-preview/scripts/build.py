#!/usr/bin/env python3
"""
build.py — build the deploy-preview HTML.

Pure stdlib Python. No external dependencies.

Usage (fresh build):
    python3 build.py <cache-dir> <output-path> \
        --app-info <path>              \
        --target-env-apps <path>       \
        --env-list <path>              \
        --target-env-key <uuid>        \
        --source-env-name <name>

Usage (cached re-render):
    python3 build.py <cache-dir> <output-path>

Inputs (read in fresh mode):
    --app-info        app_info MCP response
    --target-env-apps env_apps MCP response (search-filtered to one app)
    --env-list        env_list MCP response
    --target-env-key  the target env's UUID (looked up in env-list for metadata)
    --source-env-name human-readable source env name (default "Development")

Outputs (write):
    <cache-dir>/preview-data.json
    <cache-dir>/meta.json
    <output-path>: final HTML

The template placeholder is /*__PREVIEW_DATA__*/null.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


PLACEHOLDER = "/*__PREVIEW_DATA__*/null"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cache_dir", type=pathlib.Path)
    p.add_argument("out_path", type=pathlib.Path)
    p.add_argument("--app-info",        type=pathlib.Path, default=None)
    p.add_argument("--target-env-apps", type=pathlib.Path, default=None)
    p.add_argument("--env-list",        type=pathlib.Path, default=None)
    p.add_argument("--target-env-key",  type=str,          default=None)
    p.add_argument("--source-env-name", type=str,          default="Development")
    return p.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    template_path = skill_dir / "assets" / "template.html"

    cache_dir = args.cache_dir.resolve()
    out_path  = args.out_path.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    fresh_inputs = [args.app_info, args.target_env_apps, args.env_list,
                    args.target_env_key]
    fresh_mode = any(x is not None for x in fresh_inputs)

    if fresh_mode:
        # All inputs required together
        if not all(x is not None for x in fresh_inputs):
            print("fresh mode requires all of --app-info, --target-env-apps, "
                  "--env-list, --target-env-key", file=sys.stderr)
            return 2
        try:
            preview = _build_preview(args)
        except (FileNotFoundError, KeyError, json.JSONDecodeError, ValueError) as exc:
            print(f"build failed: {exc}", file=sys.stderr)
            return 1
        (cache_dir / "preview-data.json").write_text(
            json.dumps(preview, separators=(",", ":")), encoding="utf-8")
        (cache_dir / "meta.json").write_text(json.dumps({
            "source_revision": preview["app"]["sourceRev"],
            "fetched_at":      int(time.time()),
        }, separators=(",", ":")), encoding="utf-8")

    # Inject
    data_path = cache_dir / "preview-data.json"
    if not data_path.exists():
        print(f"missing {data_path} — run fresh mode first", file=sys.stderr)
        return 1
    if not template_path.exists():
        print(f"template not found: {template_path}", file=sys.stderr)
        return 1

    html = template_path.read_text(encoding="utf-8")
    payload = data_path.read_text(encoding="utf-8").strip()
    try:
        json.loads(payload)
    except json.JSONDecodeError as exc:
        print(f"{data_path} not valid JSON: {exc}", file=sys.stderr)
        return 1
    if PLACEHOLDER not in html:
        print(f"placeholder {PLACEHOLDER!r} not in template", file=sys.stderr)
        return 1
    html = html.replace(PLACEHOLDER, payload, 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    bundle = json.loads(payload)
    size_kb = out_path.stat().st_size / 1024
    print(f"wrote {out_path} ({size_kb:.1f} KB)")
    print(f"  app: {bundle['app']['name']} rev {bundle['app']['sourceRev']}")
    print(f"  {bundle['sourceEnv']['name']} → {bundle['targetEnv']['name']}: "
          f"{bundle['classification']} (risk: {bundle['risk']['level']})")
    return 0


# =====================================================================
# Transform & classification
# =====================================================================

def _build_preview(args: argparse.Namespace) -> dict:
    app_info_raw      = json.loads(args.app_info.read_text(encoding="utf-8"))
    env_apps_raw      = json.loads(args.target_env_apps.read_text(encoding="utf-8"))
    env_list_raw      = json.loads(args.env_list.read_text(encoding="utf-8"))

    # ----- App identity (source) -----
    app = {
        "key":         app_info_raw["assetKey"],
        "name":        app_info_raw["name"],
        "type":        app_info_raw.get("assetType", "WebApplication"),
        "description": app_info_raw.get("description") or "",
        "sourceRev":   app_info_raw["revision"],
        "sourceDate":  (app_info_raw.get("revisionDateTime") or "")[:10],
    }

    # ----- Target environment metadata -----
    target_env = None
    for e in env_list_raw.get("results", []):
        if e["key"] == args.target_env_key:
            target_env = {
                "key":     e["key"],
                "name":    e["name"],
                "purpose": e.get("purpose", ""),
                "host":    e.get("hostname", ""),
            }
            break
    if target_env is None:
        raise ValueError(f"target env key not found in env-list: {args.target_env_key}")

    # ----- Target deployment state -----
    target = {"deployed": False}
    for a in env_apps_raw.get("results", []):
        if a.get("applicationKey") == app["key"]:
            target = {
                "deployed":  True,
                "rev":       a.get("revision"),
                "date":      (a.get("deploymentDateTime") or "")[:10],
                "buildKey":  a.get("buildKey"),
                "url":       a.get("url"),
            }
            break

    # ----- Diff math -----
    if not target["deployed"]:
        rev_gap = app["sourceRev"]  # everything is "new"
        classification = "fresh"
    else:
        rev_gap = app["sourceRev"] - target["rev"]
        if rev_gap == 0:
            classification = "noop"
        elif rev_gap < 0:
            classification = "concerning"
        else:
            classification = "update"

    risk = _risk_for(classification, rev_gap)
    recs = _recommendations(classification, rev_gap, target_env, app)

    return {
        "app":             app,
        "sourceEnv":       {"name": args.source_env_name},
        "targetEnv":       target_env,
        "target":          target,
        "classification":  classification,
        "risk":            risk,
        "revGap":          rev_gap,
        "recommendations": recs,
    }


def _risk_for(classification: str, rev_gap: int) -> dict:
    if classification == "noop":
        return {"level": "none", "label": "No change",
                "note": "Target is already at the source revision."}
    if classification == "fresh":
        return {"level": "medium", "label": "Fresh deploy",
                "note": "App does not exist in target yet — first promotion."}
    if classification == "concerning":
        return {"level": "concerning", "label": "Target ahead of source",
                "note": f"Target is {abs(rev_gap)} revision(s) ahead — "
                        "potential rollback. Verify before proceeding."}
    # update
    if rev_gap == 1:
        return {"level": "low", "label": "Minor update (+1 revision)",
                "note": "Single revision bump."}
    if rev_gap <= 5:
        return {"level": "low", "label": f"Small update (+{rev_gap} revisions)",
                "note": "Few revisions accumulated. Standard promotion."}
    if rev_gap <= 50:
        return {"level": "medium",
                "label": f"Moderate update (+{rev_gap} revisions)",
                "note": "Multiple revisions accumulated since the last promotion."}
    return {"level": "high",
            "label": f"Large update (+{rev_gap} revisions)",
            "note": "Many revisions accumulated. Consider a staged promotion "
                    "or schedule outside business hours."}


def _recommendations(classification: str, rev_gap: int,
                     target_env: dict, app: dict) -> list[str]:
    recs: list[str] = []

    if classification == "fresh":
        recs.append("Verify dependencies (libraries, agents) are deployed "
                    "or will be deployed alongside this app.")
        recs.append("If `deploy_start` requires a build, ensure a Release "
                    "build is finished via `build_list` before deploying.")
    elif classification == "noop":
        recs.append("No promotion needed — target is already up to date.")
    elif classification == "concerning":
        recs.append("Investigate why the target environment has a newer "
                    "revision. Don't proceed without confirmation.")
    elif classification == "update":
        if rev_gap > 5:
            recs.append("Review the revision history "
                        "(`mcp__outsystems__app_revisions`) to spot any "
                        "breaking changes before promoting.")
        if target_env.get("purpose") == "Production":
            recs.append("Promoting to Production — schedule outside business "
                        "hours and notify stakeholders.")
        if rev_gap > 50:
            recs.append("Large accumulation. Consider an intermediate promotion "
                        "to a staging environment first.")

    if target_env.get("purpose") == "Production":
        recs.append("Production promotion — ensure rollback path is ready "
                    "(`deploy_start` with a previous buildKey).")
    return recs


if __name__ == "__main__":
    sys.exit(main(sys.argv))
