#!/usr/bin/env python3
"""
build.py — build the per-app architecture HTML from MCP responses.

Pure stdlib Python. No external dependencies.

Usage (fresh build):
    python3 build.py <cache-dir> <output-path> \
        --app-info <path>     \
        --screens <path>      \
        --actions <path>      \
        --entities <path>     \
        --structures <path>   \
        --roles <path>        \
        [--refs <path>]

Usage (cached re-render):
    python3 build.py <cache-dir> <output-path>

In fresh mode each `--<section>` flag is a path to a raw MCP response
file (either an inline-Write'd cache file or a harness-saved tool-result
file). `--refs` is optional — if provided, it points to a compact
`app_refs` response (the shape `{assetKey, references: [...]}` used by
both raw MCP and the outsystems-dependency-impact cache). When present,
build.py extracts library/AIModelConnection dependencies and surfaces
them as a fifth "Dependencies" layer in the graph.

The script transforms them, writes the compact bundle to
<cache-dir>/app-data.json + meta.json, then injects into the template.

In cached mode the script reads <cache-dir>/app-data.json directly.

The template (assets/template.html) has a single placeholder:
    const APP_DATA = /*__APP_DATA__*/null;
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


PLACEHOLDER = "/*__APP_DATA__*/null"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cache_dir", type=pathlib.Path)
    p.add_argument("out_path", type=pathlib.Path)
    p.add_argument("--app-info",   type=pathlib.Path, default=None)
    p.add_argument("--screens",    type=pathlib.Path, default=None)
    p.add_argument("--actions",    type=pathlib.Path, default=None)
    p.add_argument("--entities",   type=pathlib.Path, default=None)
    p.add_argument("--structures", type=pathlib.Path, default=None)
    p.add_argument("--roles",      type=pathlib.Path, default=None)
    p.add_argument("--refs",       type=pathlib.Path, default=None,
                   help="Optional: app_refs response for dependency edges (libraries, AIModelConnections)")
    return p.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    # Skill root = parent of scripts/
    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    template_path = skill_dir / "assets" / "template.html"

    cache_dir = args.cache_dir.resolve()
    out_path  = args.out_path.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    raw_flags = [args.app_info, args.screens, args.actions,
                 args.entities, args.structures, args.roles]
    fresh_mode = any(p is not None for p in raw_flags)

    if fresh_mode:
        if not all(p is not None for p in raw_flags):
            print("fresh mode requires ALL --* paths (or none for cached mode)",
                  file=sys.stderr)
            return 2
        try:
            app_data = _build_from_raw(args)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            print(f"build failed: {exc}", file=sys.stderr)
            return 1
        # Write compact bundle + freshness metadata
        (cache_dir / "app-data.json").write_text(
            json.dumps(app_data, separators=(",", ":")), encoding="utf-8")
        (cache_dir / "meta.json").write_text(
            json.dumps({
                "revision": app_data["app"]["revision"],
                "fetched_at": int(time.time()),
            }, separators=(",", ":")), encoding="utf-8")

    # Inject
    data_path = cache_dir / "app-data.json"
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
        print(f"{data_path} is not valid JSON: {exc}", file=sys.stderr)
        return 1
    if PLACEHOLDER not in html:
        print(f"placeholder {PLACEHOLDER!r} not in template", file=sys.stderr)
        return 1
    html = html.replace(PLACEHOLDER, payload, 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    bundle = json.loads(payload)
    counts = {
        "uiFlows":    len(bundle["uiFlows"]),
        "screens":    len(bundle["screens"]),
        "actions":    sum(1 for a in bundle["actions"] if a["kind"] == "action"),
        "functions":  sum(1 for a in bundle["actions"] if a["kind"] == "function"),
        "entities":   len(bundle["entities"]),
        "enums":      len(bundle["enums"]),
        "structures": len(bundle["structures"]),
        "roles":      len(bundle["roles"]),
        "deps":       len(bundle.get("deps", [])),
    }
    size_kb = out_path.stat().st_size / 1024
    print(f"wrote {out_path} ({size_kb:.1f} KB)")
    print(f"  app: {bundle['app']['name']} (rev {bundle['app']['revision']})")
    print("  " + " · ".join(f"{k}:{v}" for k, v in counts.items()))
    return 0


# =====================================================================
# Transform functions
# =====================================================================

# Built-in OutSystems modules to filter out of the "Dependencies" view.
# They're inherited by virtually every app and add noise without signal.
# Tweak this list if you want to surface them.
_BUILTIN_MODULES = {
    "(System)",
    "OutSystemsUI",
    "OutSystemsCharts",
    "OutSystemsMaps",
    "OutSystemsSampleData",
    "OutSystemsSecurity",
    "OutSystemsPipelines",
    "OutSystemsServerlessAddon",
}


def _categorize_dep(kind: str) -> str:
    """Map a reference's kind → visual category in the graph.

    Only the legacy producer-asset kind (`kind`/`importedKind`) ever
    carried "AIModelConnection". The current schemaVersion-2
    context-service shape reports imported ELEMENT kinds instead
    (entities/actions/…), which never identify the producer as an AI
    model — so those correctly fall through to Library. AI model
    connections do not surface through app_refs on the current platform;
    they come via context_connections.
    """
    if kind == "AIModelConnection":
        return "AIModel"
    return "Library"  # eSpace, Extension, entities-import, etc.


def _ref_kind(r: dict) -> str:
    """Best scalar 'kind' for a reference across every app_refs shape.

    Prefers the scalar producer kind when present:
      - legacy MCP:                     `kind`  (e.g. "AIModelConnection", "eSpace")
      - schemaVersion 2 / oml-fallback: `importedKind`
    Otherwise falls back to the schemaVersion-2 / context-service `kinds`
    LIST of imported element kinds (e.g. ["entities"]), joined to a string.
    """
    scalar = r.get("kind") or r.get("importedKind")
    if scalar:
        return scalar
    kinds = r.get("kinds")
    if isinstance(kinds, list):
        return ", ".join(str(k) for k in kinds if k)
    if isinstance(kinds, str):
        return kinds
    return ""


def _build_deps(refs_path, app_key: str) -> list[dict]:
    """Read an app_refs response and return filtered dependency edges.

    Tolerant of every app_refs reference shape seen in the wild — the
    fresh MCP response and the outsystems-dependency-impact
    `refs/<APP_KEY>.json` cross-skill cache are the same raw
    {assetKey, references: [...]} envelope, but the reference items differ:
      - legacy:                         {moduleKey, name, kind, revision}
      - schemaVersion 2 / oml-fallback: {producerAssetKey, producerAssetName, importedKind}
      - schemaVersion 2 / context-service (live 2026-07-09):
                                        {producerAssetKey, producerAssetName, kinds: [...]}
    Returns [] if the file is missing, malformed, or marked failed (the
    dependency-impact placeholder for timeout cases).
    """
    if refs_path is None:
        return []
    try:
        raw = json.loads(refs_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    if raw.get("failed"):
        return []  # scan timed out (upstream concurrency limit) — fall back to no-deps
    deps: list[dict] = []
    for r in raw.get("references", []) or []:
        name = r.get("name") or r.get("producerAssetName") or ""
        if not name or name in _BUILTIN_MODULES:
            continue
        kind = _ref_kind(r)
        deps.append({
            "k":    r.get("moduleKey") or r.get("producerAssetKey") or "",
            "n":    name,
            "kind": kind,
            "cat":  _categorize_dep(kind),
            "rev":  str(r.get("revision") or ""),
        })
    return deps


def _build_from_raw(args: argparse.Namespace) -> dict:
    """Transform raw MCP responses into the compact bundle."""

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

    # ----- UI flows (derived from screens) -----
    ui_flows: dict[str, dict] = {}
    screens: list[dict] = []
    for s in screens_raw.get("data", []):
        if s.get("ownerAppKey") != app_key:
            continue  # skip inherited
        flow_key = s.get("additionalData", {}).get("uiFlowKey", "default")
        flow_name = s.get("additionalData", {}).get("uiFlowName", "Default")
        if flow_key not in ui_flows:
            ui_flows[flow_key] = {"key": flow_key, "name": flow_name}
        screens.append({
            "k":    s["key"],
            "n":    s["name"],
            "flow": flow_key,
            "desc": (s.get("description") or "")[:200],
            "pub":  bool(s.get("isPublic", False)),
            "date": (s.get("timestamp", "") or "")[:10],
        })

    # ----- Actions (split into actions and functions) -----
    actions = []
    for a in actions_raw.get("data", []):
        if a.get("ownerAppKey") != app_key:
            continue
        action_type = a.get("additionalData", {}).get("actionType", 0)
        kind = "function" if action_type == 1 else "action"
        actions.append({
            "k":    a["key"],
            "n":    a["name"],
            "kind": kind,
            "desc": (a.get("description") or "")[:240],
            "pub":  bool(a.get("isPublic", False)),
        })

    # ----- Entities (business non-static) vs static enums -----
    # v1.3: also keep inherited entities — many apps (thin-UI / multi-module
    # architecture, e.g. rmad employee directory) define their data model in a
    # referenced library module. Pre-v1.3 we dropped these silently and
    # reported "no owned entities" — materially misleading. Now we partition.
    entities = []
    inherited_entities = []
    enums = []
    inherited_entity_count = 0
    for e in entities_raw.get("data", []):
        is_owned = e.get("ownerAppKey") == app_key
        item = {
            "k":    e["key"],
            "n":    e["name"],
            "desc": (e.get("description") or "")[:200],
        }
        if e.get("isStatic", False):
            # Static enums: only show if owned (inherited enums are platform
            # noise — Locale, BooleanLabel, etc. from OutSystemsUI).
            if is_owned:
                enums.append(item)
            else:
                inherited_entity_count += 1
            continue
        if is_owned:
            entities.append(item)
        else:
            # Inherited business entity — keep it with attribution.
            inherited_entity_count += 1
            item["fromModule"] = (
                e.get("producerAssetName")
                or (e.get("additionalData") or {}).get("producerAssetName")
                or "<unknown module>"
            )
            inherited_entities.append(item)

    # ----- Structures -----
    structures = [
        {
            "k":    s["key"],
            "n":    s["name"],
            "desc": (s.get("description") or "")[:200],
        }
        for s in structures_raw.get("data", [])
        if s.get("ownerAppKey") == app_key
    ]

    # ----- Roles -----
    roles = [
        {
            "k":    r["key"],
            "n":    r["name"],
            "desc": (r.get("description") or "") or "",
            "pub":  bool(r.get("isPublic", False)),
        }
        for r in roles_raw.get("data", [])
        if r.get("ownerAppKey") == app_key
    ]

    deps = _build_deps(args.refs, app_key)

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
        "deps":              deps,
        "inheritedCount":    inherited_entity_count,
    }


if __name__ == "__main__":
    sys.exit(main(sys.argv))
