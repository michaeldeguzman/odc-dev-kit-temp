# SFTDD Workflow — outsystems-mentor-polling-behavior/scripts/run.py

You are an AI assistant following the Spec-First TDD (SFTDD) methodology
for this project. Read this file at the start of every session and follow
its rules exactly.

---

## Project context

**Script:** `run.py` — session lifecycle, telemetry, config, and HTML rendering
driver for the `outsystems-mentor-polling-behavior` Claude Code skill.

**Language:** Python 3.7+  
**Test framework:** pytest (managed via uv)  
**Test command:** `uv run pytest` (run from `scripts/`)  
**Test directory:** `scripts/tests/`  
**Module import:** `from run import <name>` (tests run with `scripts/` on path)

**Runtime constraint:** `run.py` is pure stdlib. No third-party imports are
ever added to the production code. `pytest` is the only dev dependency.

---

## Three operating modes

**Mode 1 — Feature Development**
Trigger: a new use case is added to `00-use-case.md`.
Announce: `🔧 Entering Feature Development Mode for Use Case #N — <title>`
Sequence: **Red → Green → Enhancement → Refactor**

**Mode 2 — Issue Resolution**
Trigger: a new issue is added to `00-issues.md`.
Announce: `🐛 Entering Issue Resolution Mode for Issue #N — <title>`
Sequence: **Triage → Red → Green → Refactor**

**Mode 3 — Brainstorming**
Trigger: user says "Don't change anything yet" or "Brainstorm with me".
Announce: `💡 Entering Brainstorming Mode`
No code changes. Analysis and proposals only.

---

## The four TDD phases (Feature Development)

### Phase 1 — Red
- Write a minimal, self-contained pytest test that **fails** against the
  current `run.py`.
- The test must be in `scripts/tests/test_run.py`.
- Import only from `run` and stdlib. No third-party imports in tests.
- Show the test code. Wait for the user to run `uv run pytest` and confirm
  it is red before proceeding.

### Phase 2 — Green
- Write the **smallest** change to `run.py` that makes the failing test pass.
- No extra features, no premature abstractions.
- Show the change. Wait for the user to run `uv run pytest` and confirm
  all tests are green before proceeding.

### Phase 3 — Enhancement
- Suggest edge-case tests and minor robustness improvements for the
  **current use case only** — not new features.
- All existing tests must keep passing.
- Wait for user confirmation before each enhancement.

### Phase 4 — Refactor
- Review `run.py` for code quality, PEP-8 compliance, clarity, and
  security (no shell injection, no unsafe file ops).
- No behavior changes — all tests must keep passing after refactor.
- Mark the use case as **Completed** in `00-use-case.md`.

---

## Rules

- Always announce mode and phase transitions explicitly.
- Follow phase order strictly — never skip.
- One use case at a time. Finish all four phases before starting the next.
- Wait for user confirmation (test run result) between phases.
- Never proactively suggest new use cases or issues.
- Never add third-party imports to `run.py`.
- Never modify `pyproject.toml` without asking first.
- `run.py` must remain a single importable module (no splitting into packages).
- Tests must be isolated — use `tmp_path` (pytest fixture) for all file I/O,
  never write to the real cache or skill directories.

---

## How to start a use case

```
Read 00-sftdd-workflow.md and understand its context.
Read 00-use-case.md. Process Use Case #N: <title>.
```
