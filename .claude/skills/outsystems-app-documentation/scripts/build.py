#!/usr/bin/env python3
"""
build.py — generate Markdown documentation for an OutSystems app.

Pure stdlib Python. No template file needed — this is pure code-gen.

Usage (fast path — reuse outsystems-app-architecture's cache):
    python3 build.py <cache-dir> <output-path> \
        --app-data <path to existing app-data.json>

Usage (slow path — same raw inputs as outsystems-app-architecture):
    python3 build.py <cache-dir> <output-path> \
        --app-info       <path>  \
        --screens        <path>  \
        --actions        <path>  \
        --entities       <path>  \
        --structures     <path>  \
        --roles          <path>

In fast mode the script reads an existing app-data.json (typically
produced by outsystems-app-architecture's build.py) and renders the
Markdown directly. Zero transformation needed.

In slow mode the script reads the 6 raw MCP responses, transforms them
into the same app-data.json shape (logic mirrors app-architecture's
build.py), caches the bundle, then renders.

Either way, output is a single .md file ready to paste into Confluence,
a wiki, a README, or convert to PDF/Word via pandoc.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cache_dir", type=pathlib.Path)
    p.add_argument("out_path",  type=pathlib.Path)
    # Fast path
    p.add_argument("--app-data", type=pathlib.Path, default=None)
    # Slow path
    p.add_argument("--app-info",   type=pathlib.Path, default=None)
    p.add_argument("--screens",    type=pathlib.Path, default=None)
    p.add_argument("--actions",    type=pathlib.Path, default=None)
    p.add_argument("--entities",   type=pathlib.Path, default=None)
    p.add_argument("--structures", type=pathlib.Path, default=None)
    p.add_argument("--roles",      type=pathlib.Path, default=None)
    return p.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    cache_dir = args.cache_dir.resolve()
    out_path  = args.out_path.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    bundle = None

    # Fast path: reuse an existing app-data.json
    if args.app_data is not None:
        try:
            bundle = json.loads(args.app_data.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"failed to read --app-data: {exc}", file=sys.stderr)
            return 1
        # Persist into this skill's cache too, so cached re-renders work
        # even if the source arch-cache gets cleared later.
        (cache_dir / "app-data.json").write_text(
            json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
        (cache_dir / "meta.json").write_text(json.dumps({
            "revision":   bundle["app"]["revision"],
            "fetched_at": int(time.time()),
        }, separators=(",", ":")), encoding="utf-8")

    # Slow path: build from raw MCP responses
    slow_inputs = [args.app_info, args.screens, args.actions,
                   args.entities, args.structures, args.roles]
    if bundle is None and any(p is not None for p in slow_inputs):
        if not all(p is not None for p in slow_inputs):
            print("slow path requires all six --* paths", file=sys.stderr)
            return 2
        try:
            bundle = _build_from_raw(args)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            print(f"build failed: {exc}", file=sys.stderr)
            return 1
        # Cache for next run
        (cache_dir / "app-data.json").write_text(
            json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
        (cache_dir / "meta.json").write_text(json.dumps({
            "revision":   bundle["app"]["revision"],
            "fetched_at": int(time.time()),
        }, separators=(",", ":")), encoding="utf-8")

    # Cached doc re-render: read our own cached app-data.json
    if bundle is None:
        own_cache = cache_dir / "app-data.json"
        if own_cache.exists():
            bundle = json.loads(own_cache.read_text(encoding="utf-8"))
        else:
            print("no input provided and no cache found — pass --app-data "
                  "or the six --* raw paths", file=sys.stderr)
            return 1

    # Render Markdown
    md = _render_markdown(bundle)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

    size_kb = out_path.stat().st_size / 1024
    a = bundle["app"]
    print(f"wrote {out_path} ({size_kb:.1f} KB)")
    print(f"  app: {a['name']} rev {a['revision']}")
    counts = (f"{len(bundle['uiFlows'])} flows · "
              f"{len(bundle['screens'])} screens · "
              f"{sum(1 for x in bundle['actions'] if x['kind']=='action')} actions · "
              f"{sum(1 for x in bundle['actions'] if x['kind']=='function')} functions · "
              f"{len(bundle['entities'])} entities · "
              f"{len(bundle['enums'])} enums · "
              f"{len(bundle['structures'])} structures · "
              f"{len(bundle['roles'])} roles")
    print(f"  {counts}")
    return 0


# =====================================================================
# Transform (slow path) — mirrors outsystems-app-architecture/build.py
# =====================================================================

def _build_from_raw(args: argparse.Namespace) -> dict:
    app_info = json.loads(args.app_info.read_text(encoding="utf-8"))
    screens_raw    = json.loads(args.screens.read_text(encoding="utf-8"))
    actions_raw    = json.loads(args.actions.read_text(encoding="utf-8"))
    entities_raw   = json.loads(args.entities.read_text(encoding="utf-8"))
    structures_raw = json.loads(args.structures.read_text(encoding="utf-8"))
    roles_raw      = json.loads(args.roles.read_text(encoding="utf-8"))

    app_key = app_info["assetKey"]

    app = {
        "key":         app_info["assetKey"],
        "name":        app_info["name"],
        "type":        app_info.get("assetType", "WebApplication"),
        "revision":    app_info["revision"],
        "description": app_info.get("description", "") or "",
        "date":        app_info.get("revisionDateTime", "")[:10],
    }

    ui_flows: dict[str, dict] = {}
    screens: list[dict] = []
    for s in screens_raw.get("data", []):
        if s.get("ownerAppKey") != app_key:
            continue
        flow_key  = s.get("additionalData", {}).get("uiFlowKey", "default")
        flow_name = s.get("additionalData", {}).get("uiFlowName", "Default")
        ui_flows.setdefault(flow_key, {"key": flow_key, "name": flow_name})
        screens.append({
            "k":    s["key"],
            "n":    s["name"],
            "flow": flow_key,
            "desc": (s.get("description") or "")[:200],
            "pub":  bool(s.get("isPublic", False)),
            "date": (s.get("timestamp", "") or "")[:10],
        })

    actions = []
    for a in actions_raw.get("data", []):
        if a.get("ownerAppKey") != app_key:
            continue
        kind = "function" if a.get("additionalData", {}).get("actionType", 0) == 1 else "action"
        actions.append({
            "k":    a["key"],
            "n":    a["name"],
            "kind": kind,
            "desc": (a.get("description") or "")[:240],
            "pub":  bool(a.get("isPublic", False)),
        })

    # v1.3: partition into owned vs inherited (was: drop all inherited).
    # Many apps define their data model in a referenced library module —
    # pre-v1.3 we silently reported "no owned entities" which is materially
    # misleading. Now we surface inherited business entities with attribution.
    entities, inherited_entities, enums, inherited = [], [], [], 0
    for e in entities_raw.get("data", []):
        is_owned = e.get("ownerAppKey") == app_key
        item = {"k": e["key"], "n": e["name"],
                "desc": (e.get("description") or "")[:200]}
        if e.get("isStatic", False):
            if is_owned:
                enums.append(item)
            else:
                inherited += 1
            continue
        if is_owned:
            entities.append(item)
        else:
            inherited += 1
            item["fromModule"] = (
                e.get("producerAssetName")
                or (e.get("additionalData") or {}).get("producerAssetName")
                or "<unknown module>"
            )
            inherited_entities.append(item)

    structures = [
        {"k": s["key"], "n": s["name"],
         "desc": (s.get("description") or "")[:200]}
        for s in structures_raw.get("data", [])
        if s.get("ownerAppKey") == app_key
    ]
    roles = [
        {"k": r["key"], "n": r["name"],
         "desc": (r.get("description") or "") or "",
         "pub": bool(r.get("isPublic", False))}
        for r in roles_raw.get("data", [])
        if r.get("ownerAppKey") == app_key
    ]

    return {
        "app":               app,
        "uiFlows":           list(ui_flows.values()),
        "screens":           screens,
        "actions":           actions,
        "entities":          entities,
        "inheritedEntities": inherited_entities,
        "enums":             enums,
        "structures":        structures,
        "roles":             roles,
        "inheritedCount":    inherited,
    }


# =====================================================================
# Render Markdown
# =====================================================================

def _render_markdown(d: dict) -> str:
    a = d["app"]
    today = time.strftime("%Y-%m-%d", time.gmtime())

    act_count = sum(1 for x in d["actions"] if x["kind"] == "action")
    fn_count  = sum(1 for x in d["actions"] if x["kind"] == "function")

    lines: list[str] = []
    push = lines.append

    # ----- Header -----
    push(f"# {a['name']}")
    push("")
    parts = []
    if a.get("description"): parts.append(f"**{a['description']}**")
    parts.append(a["type"])
    parts.append(f"Revision {a['revision']}")
    if a.get("date"):        parts.append(f"Updated {a['date']}")
    push("> " + " · ".join(parts))
    push("")

    # ----- Overview table -----
    push("## Overview")
    push("")
    push("| Metric | Count |")
    push("|---|---|")
    push(f"| UI flows | {len(d['uiFlows'])} |")
    push(f"| Screens | {len(d['screens'])} |")
    push(f"| Server actions | {act_count} |")
    push(f"| Functions | {fn_count} |")
    push(f"| Business entities | {len(d['entities'])} |")
    push(f"| Static enums | {len(d['enums'])} |")
    push(f"| Structures | {len(d['structures'])} |")
    push(f"| Roles | {len(d['roles'])} |")
    push(f"| Inherited library items | {d.get('inheritedCount', 0)} |")
    push("")

    # ----- UI: flows → screens -----
    push("## UI")
    push("")
    if not d["uiFlows"]:
        push("_No UI flows in this app._")
        push("")
    else:
        flow_by_key = {f["key"]: f["name"] for f in d["uiFlows"]}
        screens_by_flow: dict[str, list[dict]] = {}
        for s in d["screens"]:
            screens_by_flow.setdefault(s["flow"], []).append(s)
        for fkey, fname in flow_by_key.items():
            screen_list = screens_by_flow.get(fkey, [])
            push(f"### UI Flow: {fname}  _({len(screen_list)} screen"
                 f"{'s' if len(screen_list) != 1 else ''})_")
            push("")
            for s in sorted(screen_list, key=lambda x: x["n"].lower()):
                desc = s.get("desc") or "_(no description)_"
                pub = " — *public*" if s.get("pub") else ""
                push(f"- **{s['n']}** — {desc}{pub}")
            push("")

    # ----- Logic -----
    push("## Logic")
    push("")
    if act_count:
        push(f"### Server actions ({act_count})")
        push("")
        for x in sorted([a for a in d["actions"] if a["kind"] == "action"],
                        key=lambda x: x["n"].lower()):
            desc = x.get("desc") or "_(no description)_"
            pub = " — *public*" if x.get("pub") else ""
            push(f"- **{x['n']}** — {desc}{pub}")
        push("")
    if fn_count:
        push(f"### Functions ({fn_count})")
        push("")
        push("_Inline-callable from expressions._")
        push("")
        for x in sorted([a for a in d["actions"] if a["kind"] == "function"],
                        key=lambda x: x["n"].lower()):
            desc = x.get("desc") or "_(no description)_"
            push(f"- **{x['n']}** — {desc}")
        push("")
    if not d["actions"]:
        push("_No logic items in this app._")
        push("")

    # ----- Data -----
    push("## Data")
    push("")
    inherited_ents = d.get("inheritedEntities") or []
    if d["entities"]:
        push(f"### Business entities ({len(d['entities'])}, owned)")
        push("")
        for e in sorted(d["entities"], key=lambda x: x["n"].lower()):
            desc = e.get("desc") or "_(no description)_"
            push(f"- **{e['n']}** — {desc}")
        push("")
    if inherited_ents:
        # v1.3: surface inherited business entities (e.g. when this app's
        # data model lives in a separate referenced library module).
        # Group by source module so the attribution is obvious.
        from collections import defaultdict
        by_mod = defaultdict(list)
        for e in inherited_ents:
            by_mod[e.get("fromModule") or "<unknown module>"].append(e)
        push(f"### Business entities ({len(inherited_ents)}, inherited)")
        push("")
        push("This app uses entities defined in referenced library modules:")
        push("")
        for mod_name in sorted(by_mod.keys(), key=str.lower):
            items = sorted(by_mod[mod_name], key=lambda x: x["n"].lower())
            push(f"**From `{mod_name}`** ({len(items)} entit{'y' if len(items)==1 else 'ies'}):")
            for e in items:
                desc = e.get("desc") or "_(no description)_"
                push(f"- **{e['n']}** — {desc}")
            push("")
    if d["enums"]:
        push(f"### Static enums ({len(d['enums'])})")
        push("")
        # Enums are usually trivial — render as a comma-joined list
        names = ", ".join(f"`{e['n']}`" for e in sorted(d["enums"], key=lambda x: x["n"].lower()))
        push(names)
        push("")
    if d["structures"]:
        push(f"### Structures ({len(d['structures'])})")
        push("")
        for s in sorted(d["structures"], key=lambda x: x["n"].lower()):
            desc = s.get("desc") or "_(no description)_"
            push(f"- **{s['n']}** — {desc}")
        push("")
    if not (d["entities"] or inherited_ents or d["enums"] or d["structures"]):
        push("_No data model items found — neither owned nor inherited._")
        push("")

    # ----- Security -----
    push("## Security")
    push("")
    if d["roles"]:
        for r in sorted(d["roles"], key=lambda x: x["n"].lower()):
            desc = r.get("desc") or "_(no description)_"
            pub = " — *public*" if r.get("pub") else " — *application role*"
            push(f"- **{r['n']}**{pub} — {desc}")
    else:
        push("_No app-defined roles._")
    push("")

    # ----- Dependencies -----
    push("## Dependencies")
    push("")
    if d.get("inheritedCount", 0) > 0:
        push(f"This app inherits {d['inheritedCount']} item(s) from referenced "
             "libraries (UI patterns, Charts, Maps, BPT, etc.). For the full "
             "dependency tree, run the `outsystems-app-architecture` skill.")
    else:
        push("_No tracked library inheritance._")
    push("")

    # ----- Footer -----
    push("---")
    push("")
    push(f"_Asset key:_ `{a['key']}`  ")
    push(f"_Generated:_ {today}  ")
    push("_Tool:_ `outsystems-app-documentation` v1.0.0  ")
    push("")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
