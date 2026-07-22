#!/usr/bin/env python3
"""
dbresults-odc-new-app-baseline validation helper.

This script does NOT call Mentor or any MCP tool. Claude Code fetches
data from the live tenant via MCP (`GetValidationMessages`, folder/eSpace
enumeration, `(System)` reference info), saves it to a local JSON file,
and hands that file to this script. The script does deterministic
classification only — it replaces the manual, LLM-judgment reclassification
step that (per notes/2026-07-21-newapp-gap-analysis.md) was gotten wrong
three consecutive runs in a row (TestNewWebApp5, 6, 7).

Subcommands:

  classify        — classify GetValidationMessages output into
                    fix-now / known-false-positive / needs-human-review.
  check-folders    — flag duplicate (name, scope) folder pairs from an
                    eSpace.Folders enumeration (Post-Crash Structural Check).
  check-reference  — verify a `(System)` reference Hash is non-zero
                    (pre-flight step 7 / Pre-Publish Sanity Check).

Pure stdlib. No pip install.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# --------------------------------------------------------------- known rules

# Each pattern is matched case-insensitively against the message text.
# Order matters: first match wins. These are derived from
# references/gotchas.md — keep this table in sync if gotchas.md is updated.
FALSE_POSITIVE_PATTERNS: list[tuple[str, str]] = [
    (
        r"LoginProviderOnClick.*ProviderIndex",
        "Known validator false positive. Confirm `ExecutingIndex = ProviderIndex` "
        "assignment exists in the action body; if so, this is not a real bug.",
    ),
    (
        r"ExternalIdentityProviders",
        "Already consumed by OnInitialize's population logic — expected, not a bug.",
    ),
    (
        r"ShowExternalProvider",
        "Already consumed by the container's If(ShowExternalProvider, ...) — expected, not a bug.",
    ),
]

# Messages that MUST be treated as real bugs even though they might look like
# routine/expected warnings at a glance. Prevents the exact misclassification
# documented in the gap-analysis notes (the OnException warning was accepted
# as expected for 3 consecutive runs before it was caught).
FORCE_FIX_NOW_PATTERNS: list[tuple[str, str]] = [
    (
        r"No Exception Handling",
        "This is NOT an expected baseline warning. It means the OnException "
        "handler (section 13) is missing or not wired to both the Common flow "
        "OnExceptionHandler and the app GlobalExceptionHandler. See "
        "references/gotchas.md.",
    ),
    (
        r"ImplicitSelfUserProvider",
        "Set eSpace.IsUserProvider = true. See references/spec.md#3-role--app-identity.",
    ),
    (
        r"Icon library compat",
        "OutSystemsUI version is below 2.28.0 (required for Phosphor2.0). "
        "Request a tenant-level upgrade — see pre-flight step 6.",
    ),
]

UNUSED_PATTERN = re.compile(r"unused (action|element|local variable)", re.IGNORECASE)


def _first_match(message: str, patterns: list[tuple[str, str]]) -> str | None:
    for pattern, reason in patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return reason
    return None


def _extract_messages(raw: Any) -> list[str]:
    """
    Accept several possible shapes for GetValidationMessages output:
      - list[str]
      - list[dict] with a "message" (or "Message"/"text") key
      - dict with a "messages" / "warnings" / "errors" list inside
    Falls back to treating the raw text as newline-separated messages.
    """
    if isinstance(raw, list):
        out = []
        for item in raw:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                msg = item.get("message") or item.get("Message") or item.get("text")
                if msg:
                    out.append(str(msg))
                else:
                    out.append(json.dumps(item))
        return out
    if isinstance(raw, dict):
        for key in ("messages", "warnings", "errors", "validationMessages"):
            if key in raw and isinstance(raw[key], list):
                return _extract_messages(raw[key])
    return []


# ------------------------------------------------------------------ classify


def cmd_classify(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"input not found: {input_path}", file=sys.stderr)
        return 1

    raw_text = input_path.read_text("utf-8")
    messages: list[str]
    try:
        parsed = json.loads(raw_text)
        messages = _extract_messages(parsed)
        if not messages and isinstance(parsed, str):
            messages = [line.strip() for line in parsed.splitlines() if line.strip()]
    except json.JSONDecodeError:
        # Plain text fallback: one message per non-empty line.
        messages = [line.strip() for line in raw_text.splitlines() if line.strip()]

    fix_now: list[tuple[str, str]] = []
    false_positive: list[tuple[str, str]] = []
    needs_review: list[str] = []

    for msg in messages:
        forced_reason = _first_match(msg, FORCE_FIX_NOW_PATTERNS)
        if forced_reason:
            fix_now.append((msg, forced_reason))
            continue

        fp_reason = _first_match(msg, FALSE_POSITIVE_PATTERNS)
        if fp_reason:
            false_positive.append((msg, fp_reason))
            continue

        if UNUSED_PATTERN.search(msg):
            fix_now.append((msg, "Unwired widget/action/variable created in this batch — wire it now."))
            continue

        needs_review.append(msg)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    md: list[str] = []
    md.append("# Validation Message Classification")
    md.append("")
    md.append(f"- **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    md.append(f"- **Source:** `{input_path}`")
    md.append(f"- **Total messages:** {len(messages)}")
    md.append(
        f"- **Fix now:** {len(fix_now)} · "
        f"**Known false positive:** {len(false_positive)} · "
        f"**Needs human review:** {len(needs_review)}"
    )
    md.append("")
    md.append("`0 errors` does not mean `0 warnings` — every item below needs a decision.")
    md.append("")

    md.append("## Fix now")
    md.append("")
    if fix_now:
        for msg, reason in fix_now:
            md.append(f"- **{msg}**")
            md.append(f"  - {reason}")
    else:
        md.append("_(none)_")
    md.append("")

    md.append("## Known false positive")
    md.append("")
    if false_positive:
        for msg, reason in false_positive:
            md.append(f"- **{msg}**")
            md.append(f"  - {reason}")
    else:
        md.append("_(none)_")
    md.append("")

    md.append("## Needs human review")
    md.append("")
    md.append(
        "Not matched against any known pattern. Confirm with the user before "
        "classifying as expected-at-baseline or removing anything."
    )
    md.append("")
    if needs_review:
        for msg in needs_review:
            md.append(f"- {msg}")
    else:
        md.append("_(none)_")
    md.append("")

    output_path.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {output_path} ({len(messages)} message(s) classified)")
    print(
        f"fix-now: {len(fix_now)}  false-positive: {len(false_positive)}  "
        f"needs-review: {len(needs_review)}"
    )

    return 1 if fix_now else 0


# --------------------------------------------------------------- check-folders


def cmd_check_folders(args: argparse.Namespace) -> int:
    """
    Input: JSON list of {"name": str, "scope": str, "objectKey": str} —
    one entry per folder from eSpace.Folders enumeration. `scope` should
    distinguish tree type (e.g. "ServerActions" vs "ClientActions") since
    same-named folders in *different* scopes are correct and expected
    (see references/gotchas.md — Model API Patterns).
    """
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"input not found: {input_path}", file=sys.stderr)
        return 1

    folders = json.loads(input_path.read_text("utf-8"))
    if not isinstance(folders, list):
        print("expected a JSON list of folder objects", file=sys.stderr)
        return 1

    seen: dict[tuple[str, str], list[str]] = {}
    for f in folders:
        name = f.get("name") or f.get("Name")
        scope = f.get("scope") or f.get("Scope") or "unknown-scope"
        key = f.get("objectKey") or f.get("ObjectKey") or "(no key)"
        if not name:
            continue
        seen.setdefault((name, scope), []).append(key)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}

    if duplicates:
        print(f"DUPLICATE FOLDERS FOUND ({len(duplicates)} name/scope pair(s)):")
        for (name, scope), keys in duplicates.items():
            print(f"  - '{name}' in scope '{scope}': {len(keys)} distinct objects -> {keys}")
        print()
        print(
            "Consolidate into one folder per (name, scope) pair and reassign "
            "affected actions before publishing — see references/gotchas.md "
            "(Post-Crash-Recovery Structural Check)."
        )
        return 1

    print(f"OK — {len(seen)} distinct (name, scope) folder pair(s), no duplicates.")
    return 0


# ------------------------------------------------------------- check-reference


def cmd_check_reference(args: argparse.Namespace) -> int:
    """
    Input: JSON object with at least a "hash" (or "Hash") field for the
    `(System)` reference, as read by Mentor before Batch 1 (pre-flight
    step 7).
    """
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"input not found: {input_path}", file=sys.stderr)
        return 1

    data = json.loads(input_path.read_text("utf-8"))
    hash_value = data.get("hash") or data.get("Hash") or ""
    zero_hash = "00000000-0000-0000-0000-000000000000"

    if not hash_value or hash_value == zero_hash:
        print(
            "STALE REFERENCE — (System) reference Hash is zero or missing. "
            "This guarantees OS-BEW-CODE-40036 at publish. Fix via "
            "add_references_to_elements or eSpace.RefreshDependency(globalKey, "
            "updateSpecificVersion: true) on the entity's own global key, then "
            "re-verify the attribute list actually changed. See "
            "references/gotchas.md."
        )
        return 1

    print(f"OK — (System) reference Hash is non-zero ({hash_value}).")
    return 0


# --------------------------------------------------------------- arg dispatch


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="classify_validation.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser(
        "classify", help="Classify GetValidationMessages output into fix-now / false-positive / needs-review"
    )
    sp.add_argument("--input", required=True, help="Path to a JSON (or plain text) dump of validation messages")
    sp.add_argument("--output", required=True, help="Path to write the classified Markdown report")

    sp = sub.add_parser(
        "check-folders", help="Flag duplicate (name, scope) folder pairs from an eSpace.Folders enumeration"
    )
    sp.add_argument("--input", required=True, help="Path to a JSON list of folder objects")

    sp = sub.add_parser(
        "check-reference", help="Verify a (System) reference Hash is non-zero"
    )
    sp.add_argument("--input", required=True, help="Path to a JSON object with a hash/Hash field")

    args = p.parse_args(argv)
    if args.cmd == "classify":
        return cmd_classify(args)
    if args.cmd == "check-folders":
        return cmd_check_folders(args)
    if args.cmd == "check-reference":
        return cmd_check_reference(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
