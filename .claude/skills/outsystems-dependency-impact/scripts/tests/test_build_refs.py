#!/usr/bin/env python3
"""Unit tests for build.py's app_refs reference parsing.

Runnable two ways:
    python3 test_build_refs.py           # standalone, no deps
    pytest skills/.../scripts/tests/     # discovered as test_* functions

Guards the regression where the schemaVersion-2 / context-service app_refs
shape ({producerAssetKey, producerAssetName, kinds:[...]}, live 2026-07-09)
rendered every target's kind as "?" because the parser only knew the
oml-fallback `importedKind` scalar.
"""
import argparse
import importlib.util
import json
import pathlib
import tempfile

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("dep_build", _SCRIPTS / "build.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)


def test_ref_kind_across_all_shapes():
    assert build._ref_kind({"kind": "AIModelConnection"}) == "AIModelConnection"
    assert build._ref_kind({"importedKind": "eSpace"}) == "eSpace"
    assert build._ref_kind({"kinds": ["entities"]}) == "entities"
    assert build._ref_kind({"kinds": ["entities", "actions"]}) == "entities, actions"
    assert build._ref_kind({"kinds": "entities"}) == "entities"       # tolerate scalar
    assert build._ref_kind({}) == ""


def test_build_bundle_live_context_service_kind_not_question_mark():
    """Full-path regression: a consumer whose refs use the live
    context-service shape must produce a target with the real kind."""
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        refs_dir = td / "refs"
        refs_dir.mkdir()

        consumer_key = "app-1"
        target_key = "lib-1"
        # tenant registry (compact shape): consumer app + a library target
        tenant_assets = [
            {"k": consumer_key, "n": "WBG_PoC", "t": "WebApplication", "r": 135, "d": "2026-07-01", "x": False},
            {"k": target_key, "n": "WorldBankTheme", "t": "LowCodeLibrary", "r": 4, "d": "2026-06-01", "x": False},
        ]
        # live context-service app_refs response for the consumer
        refs_response = {
            "assetKey": consumer_key,
            "schemaVersion": 2,
            "source": "context-service",
            "references": [
                {"kinds": ["entities"], "producerAssetKey": "sys", "producerAssetName": "(System)"},
                {"kinds": ["entities"], "producerAssetKey": target_key, "producerAssetName": "WorldBankTheme"},
            ],
        }
        (refs_dir / f"{consumer_key}.json").write_text(json.dumps(refs_response), encoding="utf-8")
        assets_path = td / "assets.json"
        assets_path.write_text(json.dumps([consumer_key]), encoding="utf-8")
        tenant_path = td / "tenant.json"
        tenant_path.write_text(json.dumps(tenant_assets), encoding="utf-8")

        args = argparse.Namespace(
            assets=assets_path, refs_dir=refs_dir, tenant_assets=tenant_path
        )
        bundle = build._build_bundle(args)

    by_target = bundle["byTarget"]
    # (System) is not filtered here (dependency-impact keeps all targets), but
    # the point is the library target renders a real kind, not "?".
    assert target_key in by_target, list(by_target)
    tgt = by_target[target_key]
    assert tgt["kind"] == "entities", tgt      # was "?" before the fix
    assert tgt["n"] == "WorldBankTheme", tgt   # tenant-name resolution
    assert bundle["stats"]["scannedCount"] == 1
    # the consumer's slimmed deps also carry the real kind
    consumer = next(a for a in bundle["assets"] if a["k"] == "app-1")
    theme_dep = next(dp for dp in consumer["deps"] if dp["k"] == target_key)
    assert theme_dep["kind"] == "entities", theme_dep


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} passed")


if __name__ == "__main__":
    _run()
