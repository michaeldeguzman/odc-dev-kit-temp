#!/usr/bin/env python3
"""
build.py — build the tenant-architecture HTML from MCP responses.

Pure stdlib Python. No external dependencies (no jq, no pip installs).

Usage:
    # Fresh build (transforms raw MCP responses + injects into template):
    python3 build.py <cache-dir> <output-path> <raw-apps-path> <tenant-id>

    # Cached re-render (uses existing assets.json/envs.json/tenant.json):
    python3 build.py <cache-dir> <output-path>

Inputs (read):
    <cache-dir>/envs-raw.json          (required in fresh mode)
    <raw-apps-path>                    (required in fresh mode — either the
                                        harness-saved MCP tool-result file or
                                        a Write'd raw response for small tenants)
    <cache-dir>/assets.json            (read in cached mode)
    <cache-dir>/envs.json              (read in cached mode)
    <cache-dir>/tenant.json            (read in cached mode)
    ../assets/template.html            (relative to this script)

Outputs (write):
    <cache-dir>/assets.json            (compact: {k,n,t,r,d,x})
    <cache-dir>/envs.json              (compact: {key,name,purpose,host})
    <cache-dir>/tenant.json            ({id, realm, region, hosting})
    <cache-dir>/meta.json              ({total, fetched_at})
    <output-path>                      (final self-contained HTML)

Design rationale:
    The whole point of this skill is to keep large asset data off the
    model's tokens. By doing transform + inject in one Python pass on
    disk, the data flows MCP → harness disk → this script → output HTML,
    never re-entering the model's output.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import time


PLACEHOLDERS = [
    ("/*__ASSETS__*/null", "assets.json"),
    ("/*__ENVS__*/null",   "envs.json"),
    ("/*__TENANT__*/null", "tenant.json"),
]


def main(argv: list[str]) -> int:
    if not (3 <= len(argv) <= 5):
        print(
            "usage: build.py <cache-dir> <output-path> "
            "[<raw-apps-path> <tenant-id>]",
            file=sys.stderr,
        )
        return 2

    cache_dir = pathlib.Path(argv[1]).resolve()
    out_path  = pathlib.Path(argv[2]).resolve()
    raw_apps  = pathlib.Path(argv[3]).resolve() if len(argv) >= 4 else None
    tenant_id = argv[4] if len(argv) >= 5 else None

    if (raw_apps is None) != (tenant_id is None):
        print(
            "raw-apps-path and tenant-id must be provided together",
            file=sys.stderr,
        )
        return 2

    # Skill root is parent of scripts/
    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    template_path = skill_dir / "assets" / "template.html"

    cache_dir.mkdir(parents=True, exist_ok=True)

    # ---- Fresh mode: build cache files from raw MCP responses ----
    if raw_apps is not None:
        try:
            _build_cache(cache_dir, raw_apps, tenant_id)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
            print(f"cache build failed: {exc}", file=sys.stderr)
            return 1

    # ---- Inject (both modes) ----
    if not template_path.exists():
        print(f"template not found: {template_path}", file=sys.stderr)
        return 1

    html = template_path.read_text(encoding="utf-8")
    for placeholder, fname in PLACEHOLDERS:
        data_path = cache_dir / fname
        if not data_path.exists():
            print(f"missing cache file: {data_path}", file=sys.stderr)
            return 1
        raw = data_path.read_text(encoding="utf-8")
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"{data_path} is not valid JSON: {exc}", file=sys.stderr)
            return 1
        if placeholder not in html:
            print(f"placeholder {placeholder!r} not in template",
                  file=sys.stderr)
            return 1
        html = html.replace(placeholder, raw.strip(), 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    asset_count = len(json.loads((cache_dir / "assets.json").read_text()))
    size_kb = out_path.stat().st_size / 1024
    print(f"wrote {out_path} ({size_kb:.1f} KB; {asset_count} assets)")
    return 0


def _build_cache(cache_dir: pathlib.Path,
                 raw_apps_path: pathlib.Path,
                 tenant_id: str) -> None:
    """Transform raw MCP responses into the compact cache files."""

    # ----- assets.json (compact list with single-letter keys) -----
    apps_raw = json.loads(raw_apps_path.read_text(encoding="utf-8"))
    assets = [
        {
            "k": a["assetKey"],
            "n": a["name"],
            "t": a["assetType"],
            "r": a["revision"],
            "d": a["revisionDateTime"][:10],
            "x": a["isExternal"],
        }
        for a in apps_raw["results"]
    ]
    (cache_dir / "assets.json").write_text(
        json.dumps(assets, separators=(",", ":")), encoding="utf-8")

    # ----- envs.json (compact) + side-data for tenant.json -----
    envs_raw_path = cache_dir / "envs-raw.json"
    if not envs_raw_path.exists():
        raise FileNotFoundError(envs_raw_path)
    envs_raw = json.loads(envs_raw_path.read_text(encoding="utf-8"))
    envs = [
        {
            "key": e["key"],
            "name": e["name"],
            "purpose": e["purpose"],
            "host": e["hostname"],
        }
        for e in envs_raw["results"]
    ]
    (cache_dir / "envs.json").write_text(
        json.dumps(envs, separators=(",", ":")), encoding="utf-8")

    # ----- tenant.json (derive realm/region from envs) -----
    region = "us-east-1"
    realm  = tenant_id[:8] if tenant_id else "tenant"
    if envs_raw.get("results"):
        first = envs_raw["results"][0]
        region = first.get("region", region)
        host   = first.get("hostname", "")
        if host:
            realm = re.sub(r"-(?:dev|test)$", "", host.split(".")[0])
    tenant = {
        "id": tenant_id,
        "realm": realm,
        "region": region,
        "hosting": "oscloud",
    }
    (cache_dir / "tenant.json").write_text(
        json.dumps(tenant, separators=(",", ":")), encoding="utf-8")

    # ----- meta.json (cache fingerprint) -----
    meta = {"total": len(assets), "fetched_at": int(time.time())}
    (cache_dir / "meta.json").write_text(
        json.dumps(meta, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
