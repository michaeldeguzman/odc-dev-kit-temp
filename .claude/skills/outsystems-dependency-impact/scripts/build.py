#!/usr/bin/env python3
r"""
build.py — build the tenant dependency-impact HTML.

Pure stdlib Python. No external dependencies.

Usage (fresh build — after a tenant scan):
    python3 build.py <cache-dir> <output-path> \
        --assets         <path>  \   # filtered scan list (asset keys)
        --refs-dir       <dir>   \   # per-asset app_refs response files
        --tenant-assets  <path>      # full tenant asset list (for revision lookups)

Usage (cached re-render):
    python3 build.py <cache-dir> <output-path>

Reads:
    Fresh mode:
        <assets>              - {"keys": [...]} or list of asset keys
        <refs-dir>/<key>.json - one per scanned asset
                                successful: {assetKey, revision?, references: [...]}
                                failed:     {assetKey, failed: true, reason?: "..."}

                                Reference items are accepted in ALL shapes:
                                  v1 (legacy): {moduleKey, name, kind, revision}
                                  v2 / oml-fallback:
                                       {producerAssetKey, producerAssetName, importedKind}
                                  v2 / context-service (live 2026-07-09):
                                       {producerAssetKey, producerAssetName, kinds: [...]}
                                Schema v2 was discovered live 2026-06-05; the
                                context-service `kinds` list variant 2026-07-09.
                                See CHANGELOG and upstream-work S14.
        <tenant-assets>       - list of assets [{k,n,t,r,d,x}, ...] (tenant skill shape)
    Cached mode:
        <cache-dir>/impact-data.json

Writes:
    <cache-dir>/impact-data.json
    <cache-dir>/meta.json
    <output-path>  - injected HTML

Template placeholder: /*__IMPACT_DATA__*/null
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


PLACEHOLDER = "/*__IMPACT_DATA__*/null"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cache_dir", type=pathlib.Path)
    p.add_argument("out_path",  type=pathlib.Path)
    p.add_argument("--assets",        type=pathlib.Path, default=None)
    p.add_argument("--refs-dir",      type=pathlib.Path, default=None)
    p.add_argument("--tenant-assets", type=pathlib.Path, default=None)
    return p.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    template_path = skill_dir / "assets" / "template.html"

    cache_dir = args.cache_dir.resolve()
    out_path  = args.out_path.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    fresh_inputs = [args.assets, args.refs_dir, args.tenant_assets]
    fresh_mode = any(x is not None for x in fresh_inputs)

    if fresh_mode:
        if not all(x is not None for x in fresh_inputs):
            print("fresh mode requires --assets, --refs-dir, --tenant-assets",
                  file=sys.stderr)
            return 2
        try:
            bundle = _build_bundle(args)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            print(f"build failed: {exc}", file=sys.stderr)
            return 1
        (cache_dir / "impact-data.json").write_text(
            json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
        (cache_dir / "meta.json").write_text(json.dumps({
            "scanned_at":         int(time.time()),
            "consumer_count":     bundle["stats"]["consumerAssetCount"],
            "scanned_count":      bundle["stats"]["scannedCount"],
            "failed_count":       bundle["stats"]["failedCount"],
            "target_count":       bundle["stats"]["targetCount"],
            "edge_count":         bundle["stats"]["edgeCount"],
        }, separators=(",", ":")), encoding="utf-8")

    # Render
    data_path = cache_dir / "impact-data.json"
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

    b = json.loads(payload)
    s = b["stats"]
    size_kb = out_path.stat().st_size / 1024
    print(f"wrote {out_path} ({size_kb:.1f} KB)")
    print(f"  scanned: {s['scannedCount']}/{s['consumerAssetCount']} "
          f"consumer assets ({s['failedCount']} failed)")
    print(f"  catalogued: {s['targetCount']} unique targets, "
          f"{s['edgeCount']} dependency edges")
    return 0


# =====================================================================
# Build (fresh mode)
# =====================================================================

def _ref_kind(d: dict) -> str:
    """Best scalar 'kind' for a reference across every app_refs shape.

    Prefers the scalar producer kind when present (`kind` legacy /
    `importedKind` oml-fallback); otherwise joins the schemaVersion-2
    context-service `kinds` LIST of imported element kinds
    (e.g. ["entities"]). Returns "" when no kind is available (callers
    apply their own "?" sentinel).
    """
    scalar = d.get("kind") or d.get("importedKind")
    if scalar:
        return scalar
    kinds = d.get("kinds")
    if isinstance(kinds, list):
        return ", ".join(str(k) for k in kinds if k)
    if isinstance(kinds, str):
        return kinds
    return ""


def _build_bundle(args: argparse.Namespace) -> dict:
    # Load tenant assets (the canonical asset registry) — used for
    # name/type/revision lookups for both consumers and targets.
    tenant = json.loads(args.tenant_assets.read_text(encoding="utf-8"))
    # Accept multiple shapes: list of {k,n,t,r,d,x} OR {"results":[{assetKey,...}]}
    tenant_assets = _normalize_tenant_assets(tenant)
    by_key = {a["k"]: a for a in tenant_assets}

    # Load the scan list (consumer asset keys)
    scan_input = json.loads(args.assets.read_text(encoding="utf-8"))
    if isinstance(scan_input, list):
        consumer_keys = scan_input
    elif isinstance(scan_input, dict) and "keys" in scan_input:
        consumer_keys = scan_input["keys"]
    else:
        raise ValueError("--assets file must be a list of keys "
                         "or {keys: [...]}")

    refs_dir = args.refs_dir.resolve()

    consumer_assets: list[dict] = []   # forward index entries
    by_target: dict[str, dict] = {}    # reverse index
    scanned_count = 0
    failed_count = 0
    edge_count = 0

    for key in consumer_keys:
        meta = by_key.get(key)
        if not meta:
            continue
        ref_path = refs_dir / f"{key}.json"
        if not ref_path.exists():
            # Treat missing file as "not scanned yet"
            consumer_assets.append({
                "k": key, "n": meta["n"], "t": meta["t"],
                "r": meta["r"], "d": meta["d"], "scanned": False,
            })
            failed_count += 1
            continue

        try:
            refs_response = json.loads(ref_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            consumer_assets.append({
                "k": key, "n": meta["n"], "t": meta["t"],
                "r": meta["r"], "d": meta["d"], "scanned": False,
            })
            failed_count += 1
            continue

        if refs_response.get("failed"):
            consumer_assets.append({
                "k": key, "n": meta["n"], "t": meta["t"],
                "r": meta["r"], "d": meta["d"], "scanned": False,
            })
            failed_count += 1
            continue

        # Successful scan
        deps_raw = refs_response.get("references", []) or []
        deps_slim = []
        for d in deps_raw:
            # Multi-schema support — accept every app_refs reference shape:
            # v1 legacy {moduleKey,name,kind}, v2/oml-fallback
            # {producerAssetKey,producerAssetName,importedKind}, and
            # v2/context-service {producerAssetKey,producerAssetName,kinds:[...]}
            # (live 2026-07-09). See SKILL.md "Data shape contract" and
            # upstream-work S14.
            mk = d.get("moduleKey") or d.get("producerAssetKey")
            if not mk:
                continue
            ref_name = d.get("name") or d.get("producerAssetName") or "?"
            ref_kind = _ref_kind(d) or "?"
            used_rev_raw = d.get("revision")  # v2 doesn't carry per-ref revision
            try:
                used_rev = int(used_rev_raw) if used_rev_raw is not None else None
            except (TypeError, ValueError):
                used_rev = None
            deps_slim.append({
                "k":    mk,
                "n":    ref_name,
                "kind": ref_kind,
                "r":    used_rev,
            })
            # Reverse index
            tgt = by_target.setdefault(mk, {
                "n":           ref_name,
                "kind":        ref_kind,
                "currentRev":  None,
                "users":       [],
            })
            # Resolve currentRev from tenant assets if available
            if tgt["currentRev"] is None:
                target_meta = by_key.get(mk)
                if target_meta:
                    tgt["currentRev"] = target_meta.get("r")
                    # Prefer the real tenant name
                    if target_meta.get("n"):
                        tgt["n"] = target_meta["n"]
            gap = None
            if tgt["currentRev"] is not None and used_rev is not None:
                gap = tgt["currentRev"] - used_rev
            tgt["users"].append({
                "k":       key,
                "n":       meta["n"],
                "t":       meta["t"],
                "usedRev": used_rev,
                "gap":     gap,
            })
            edge_count += 1

        consumer_assets.append({
            "k": key, "n": meta["n"], "t": meta["t"],
            "r": meta["r"], "d": meta["d"],
            "scanned": True, "deps": deps_slim,
        })
        scanned_count += 1

    # Sort users within each target by gap desc (most outdated first), then name
    for tgt in by_target.values():
        tgt["users"].sort(key=lambda u: (-(u["gap"] or 0), u["n"].lower()))

    return {
        "tenant": {
            "id":         _try_tenant_id_from(by_key),
            "scannedAt":  int(time.time()),
        },
        "stats": {
            "consumerAssetCount": len(consumer_keys),
            "scannedCount":       scanned_count,
            "failedCount":        failed_count,
            "targetCount":        len(by_target),
            "edgeCount":          edge_count,
        },
        "assets":   consumer_assets,
        "byTarget": by_target,
    }


def _normalize_tenant_assets(raw) -> list[dict]:
    """Accept either tenant-skill shape (compact list) or raw MCP shape."""
    if isinstance(raw, list):
        return raw  # Already compact list
    if isinstance(raw, dict) and "results" in raw:
        # Raw MCP shape from app_list
        out = []
        for a in raw["results"]:
            out.append({
                "k": a["assetKey"],
                "n": a["name"],
                "t": a["assetType"],
                "r": a.get("revision"),
                "d": (a.get("revisionDateTime") or "")[:10],
                "x": bool(a.get("isExternal", False)),
            })
        return out
    raise ValueError("--tenant-assets must be a list or {results: [...]}")


def _try_tenant_id_from(by_key: dict) -> str:
    """Best-effort tenant ID — we don't have it on hand. Return empty.

    Build.py is invoked without the tenant ID directly; the HTML doesn't
    strictly need it for functionality.
    """
    return ""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
