#!/usr/bin/env python3
"""
build.py — build the AI agent landscape HTML.

Pure stdlib Python. No external dependencies.

Usage (fresh build):
    python3 build.py <cache-dir> <output-path> \
        --agents      <path>       \
        --connections <path>       \
        --tenant-id   <uuid>

Usage (cached re-render):
    python3 build.py <cache-dir> <output-path>

Inputs (fresh mode):
    --agents       context_agents response (typical: harness-saved file)
    --connections  context_connections response (typical: inline-Write'd)
    --tenant-id    the tenant UUID

Output:
    <cache-dir>/landscape-data.json  (compact bundle)
    <cache-dir>/meta.json
    <output-path>: final HTML

Template placeholder: /*__LANDSCAPE_DATA__*/null
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys
import time


PLACEHOLDER = "/*__LANDSCAPE_DATA__*/null"

# Heuristic: agent names matching this pattern look like test/demo throwaways
TEST_DEMO_PATTERN = re.compile(
    r"(?:^|[\s_-])(test|tmp|temp|demo|untitled|xxx|123|sample|scratch|wip)(?:$|[\s_-])",
    re.IGNORECASE,
)

# Provider ID → human label fallback (in case providerName is missing)
PROVIDER_LABELS = {
    "amazonbedrock":    "Amazon Bedrock",
    "azureopenai":      "Azure OpenAI",
    "openai":           "OpenAI",
    "anthropic":        "Anthropic",
    "googlevertex":     "Google Vertex AI",
    "customconnection": "Custom connection",
}

# Stale threshold: agents not updated in N days
STALE_DAYS = 180


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cache_dir", type=pathlib.Path)
    p.add_argument("out_path",  type=pathlib.Path)
    p.add_argument("--agents",      type=pathlib.Path, default=None)
    p.add_argument("--connections", type=pathlib.Path, default=None)
    p.add_argument("--tenant-id",   type=str,          default=None)
    return p.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    template_path = skill_dir / "assets" / "template.html"

    cache_dir = args.cache_dir.resolve()
    out_path  = args.out_path.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    fresh = any(x is not None for x in
                [args.agents, args.connections, args.tenant_id])
    if fresh:
        if not all(x is not None for x in
                   [args.agents, args.connections, args.tenant_id]):
            print("fresh mode requires --agents, --connections, --tenant-id",
                  file=sys.stderr)
            return 2
        try:
            bundle = _build_bundle(args)
        except (FileNotFoundError, KeyError, json.JSONDecodeError, ValueError) as exc:
            print(f"build failed: {exc}", file=sys.stderr)
            return 1
        (cache_dir / "landscape-data.json").write_text(
            json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
        (cache_dir / "meta.json").write_text(json.dumps({
            "total_agents":      len(bundle["agents"]),
            "total_connections": len(bundle["connections"]),
            "fetched_at":        int(time.time()),
        }, separators=(",", ":")), encoding="utf-8")

    # Inject
    data_path = cache_dir / "landscape-data.json"
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
    print(f"  agents:      {s['totalAgents']} "
          f"({s['testDemoAgents']} test/demo, {s['staleAgents']} stale)")
    print(f"  connections: {s['totalConnections']} "
          f"({s['trialConns']} Trial, {s['customerConns']} Customer)")
    print(f"  providers:   " +
          ", ".join(f"{p['name']}:{p['count']}" for p in s["providers"]))
    return 0


# =====================================================================
# Transform & analyze
# =====================================================================

def _build_bundle(args: argparse.Namespace) -> dict:
    agents_raw      = json.loads(args.agents.read_text(encoding="utf-8"))
    connections_raw = json.loads(args.connections.read_text(encoding="utf-8"))

    # ----- Connections -----
    connections = []
    for c in connections_raw.get("data", []):
        ad = c.get("additionalData", {}) or {}
        provider_id = ad.get("providerId", "unknown")
        connections.append({
            "k":          c.get("key", ""),
            "n":          c.get("name", "—"),
            "desc":       (c.get("description") or "")[:280],
            "provider":   c.get("providerName") or PROVIDER_LABELS.get(provider_id, provider_id),
            "providerId": provider_id,
            "entitlement": ad.get("entitlement", "—"),
            "date":       (ad.get("revisionDateTime") or c.get("timestamp") or "")[:10],
        })
    connections.sort(key=lambda c: c["provider"] + c["n"])

    # ----- Agents -----
    now = datetime.datetime.now(datetime.timezone.utc)
    agents = []
    for a in agents_raw.get("data", []):
        name = a.get("name", "—")
        is_test = bool(TEST_DEMO_PATTERN.search(name))
        ad = a.get("additionalData", {}) or {}
        rev_date_str = ad.get("revisionDateTime") or a.get("timestamp") or ""
        is_stale = False
        if rev_date_str:
            try:
                rev_date = datetime.datetime.fromisoformat(
                    rev_date_str.replace("Z", "+00:00"))
                if rev_date.tzinfo is None:
                    rev_date = rev_date.replace(tzinfo=datetime.timezone.utc)
                age_days = (now - rev_date).days
                is_stale = age_days > STALE_DAYS
            except ValueError:
                pass
        agents.append({
            "k":          a.get("key", ""),
            "n":          name,
            "desc":       (a.get("description") or "")[:240],
            "owner":      a.get("ownerAppKey", ""),
            "pub":        bool(a.get("isPublic", False)),
            "date":       rev_date_str[:10],
            "isTestDemo": is_test,
            "isStale":    is_stale,
        })
    agents.sort(key=lambda a: a["n"].lower())

    # ----- Stats -----
    trial_count    = sum(1 for c in connections if c["entitlement"] == "Trial")
    customer_count = sum(1 for c in connections if c["entitlement"] == "Customer")
    public_agents  = sum(1 for a in agents if a["pub"])
    test_demo      = sum(1 for a in agents if a["isTestDemo"])
    stale          = sum(1 for a in agents if a["isStale"])

    # Provider breakdown for connections
    provider_counts: dict[str, int] = {}
    for c in connections:
        provider_counts[c["provider"]] = provider_counts.get(c["provider"], 0) + 1
    providers = [{"name": n, "count": c}
                 for n, c in sorted(provider_counts.items(),
                                    key=lambda x: -x[1])]

    return {
        "tenant": {"id": args.tenant_id},
        "agents": agents,
        "connections": connections,
        "stats": {
            "totalAgents":      len(agents),
            "totalConnections": len(connections),
            "trialConns":       trial_count,
            "customerConns":    customer_count,
            "publicAgents":     public_agents,
            "internalAgents":   len(agents) - public_agents,
            "testDemoAgents":   test_demo,
            "staleAgents":      stale,
            "providers":        providers,
        },
    }


if __name__ == "__main__":
    sys.exit(main(sys.argv))
