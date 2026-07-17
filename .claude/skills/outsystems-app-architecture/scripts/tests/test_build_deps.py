#!/usr/bin/env python3
"""Unit tests for build.py's app_refs dependency parser (_build_deps).

Runnable two ways:
    python3 test_build_deps.py          # standalone, no deps
    pytest skills/.../scripts/tests/    # discovered as test_* functions

Fixtures are real app_refs payloads captured live from the
professionalservices.outsystems.dev tenant on 2026-07-09 (schemaVersion 2,
source context-service) plus the legacy and oml-fallback shapes the parser
must stay tolerant of.
"""
import importlib.util
import json
import pathlib
import tempfile

# Load build.py by path so the test runs regardless of cwd / packaging.
_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("arch_build", _SCRIPTS / "build.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)


def _deps_for(payload: dict) -> list[dict]:
    """Write payload to a temp file and run _build_deps against it."""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(payload, fh)
        path = pathlib.Path(fh.name)
    try:
        return build._build_deps(path, payload.get("assetKey", "app"))
    finally:
        path.unlink(missing_ok=True)


# Real WBG_PoC (c09f99d4) app_refs response, 2026-07-09 live capture.
LIVE_CONTEXT_SERVICE = {
    "assetKey": "c09f99d4-c8fa-42d9-b82f-7a30546e6564",
    "schemaVersion": 2,
    "source": "context-service",
    "references": [
        {"kinds": ["entities"], "producerAssetKey": "38b70e23-50fc-4710-80cf-3682a9dc998a", "producerAssetName": "OutSystemsCharts"},
        {"kinds": ["entities"], "producerAssetKey": "478870b9-2d60-4f73-9eb3-7cd8b994a737", "producerAssetName": "(System)"},
        {"kinds": ["entities"], "producerAssetKey": "47a79537-db1b-4dab-bfba-354f95935ad0", "producerAssetName": "OutSystemsSampleData"},
        {"kinds": ["entities"], "producerAssetKey": "5be86d03-32b8-4d45-b8c8-b87a417f1574", "producerAssetName": "UltimatePDF"},
        {"kinds": ["entities"], "producerAssetKey": "8be17f2a-431c-4958-b894-c77b988a7271", "producerAssetName": "OutSystemsUI"},
        {"kinds": ["entities"], "producerAssetKey": "c1abdbd8-650f-43de-a2c0-cc06a51ef3b7", "producerAssetName": "WorldBankTheme"},
        {"kinds": ["entities"], "producerAssetKey": "f5cf7f7e-ca26-43e4-b584-cc124298fd0b", "producerAssetName": "OutSystemsDataGrid"},
    ],
}


def test_live_context_service_shape_yields_nonbuiltin_deps():
    """The headline bug: live producerAssetName/producerAssetKey/kinds shape
    must NOT be dropped. WBG_PoC has 3 non-builtin refs after filtering."""
    deps = _deps_for(LIVE_CONTEXT_SERVICE)
    names = sorted(d["n"] for d in deps)
    assert names == ["OutSystemsDataGrid", "UltimatePDF", "WorldBankTheme"], names
    by_name = {d["n"]: d for d in deps}
    pdf = by_name["UltimatePDF"]
    assert pdf["k"] == "5be86d03-32b8-4d45-b8c8-b87a417f1574", pdf
    assert pdf["kind"] == "entities", pdf           # kinds[] mapped to scalar
    assert pdf["cat"] == "Library", pdf             # entity-import → Library
    # builtins filtered out
    assert "(System)" not in by_name and "OutSystemsUI" not in by_name


def test_legacy_shape_still_parses_and_categorizes_aimodel():
    """Legacy {moduleKey,name,kind,revision} must still work, including the
    AIModelConnection → AIModel categorization."""
    deps = _deps_for({
        "assetKey": "legacy",
        "references": [
            {"moduleKey": "mk-ai", "name": "MyGPT", "kind": "AIModelConnection", "revision": 4},
            {"moduleKey": "mk-lib", "name": "SomeLib", "kind": "eSpace", "revision": 2},
            {"moduleKey": "mk-sys", "name": "(System)", "kind": "eSpace", "revision": 1},
        ],
    })
    by_name = {d["n"]: d for d in deps}
    assert set(by_name) == {"MyGPT", "SomeLib"}
    assert by_name["MyGPT"]["cat"] == "AIModel"
    assert by_name["MyGPT"]["kind"] == "AIModelConnection"
    assert by_name["MyGPT"]["rev"] == "4"
    assert by_name["MyGPT"]["k"] == "mk-ai"
    assert by_name["SomeLib"]["cat"] == "Library"


def test_oml_fallback_importedkind_shape():
    """schemaVersion 2 / oml-fallback uses producerAsset* + importedKind."""
    deps = _deps_for({
        "assetKey": "oml",
        "schemaVersion": 2,
        "source": "oml-fallback",
        "references": [
            {"producerAssetKey": "pk1", "producerAssetName": "SomeLib", "importedKind": "eSpace"},
        ],
    })
    assert len(deps) == 1
    assert deps[0]["n"] == "SomeLib"
    assert deps[0]["k"] == "pk1"
    assert deps[0]["kind"] == "eSpace"
    assert deps[0]["cat"] == "Library"


def test_builtins_only_yields_empty():
    deps = _deps_for({
        "assetKey": "b",
        "references": [
            {"kinds": ["entities"], "producerAssetKey": "k1", "producerAssetName": "(System)"},
            {"kinds": ["entities"], "producerAssetKey": "k2", "producerAssetName": "OutSystemsUI"},
        ],
    })
    assert deps == []


def test_failed_scan_yields_empty():
    deps = _deps_for({"assetKey": "f", "failed": True})
    assert deps == []


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} passed")


if __name__ == "__main__":
    _run()
