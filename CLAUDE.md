# OutSystems MCP — Project Notes

## Conventions

@rules/error-handling.md
@rules/database.md
@rules/testing.md
@rules/organization.md

## Build History

Record each session's builds here. Timestamps = revision commit times (includes Mentor AI execution + ODC publish compile).

### Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`) — 2026-07-17

| Build | Revision | Start (UTC) | End (UTC) | Duration |
|---|---|---|---|---|
| TestEntity CRUD wrapper (shared infra + 4 actions) via `dbresults-odc-crud-wrapper` | Rev 26 → 33 | 02:15 | 02:42 | ~27 min |
| 4 `TestEntity_*_SA` Service Actions wrapping the CRUD actions for cross-app BDD test access (after a `Server Action + Public=true` attempt failed — removed platform feature `OS-BLD-40409`, reverted) | Rev 33 → 36 | 02:55 | 03:19 | ~24 min |

### TestAnythingTests (`cc6af207-dbab-44b6-987b-f2fe16203ed1`) — 2026-07-17

New app, created to pilot `dbresults-odc-bdd-crud-tests`. Test-suite app for `Test Anything`'s `TestEntity`.

| Build | Revision | Start (UTC) | End (UTC) | Duration |
|---|---|---|---|---|
| Full auth/theme/layout baseline via `dbresults-odc-new-app-baseline` (5 batches) + fix stale `(System)` User entity reference (`OS-BEW-CODE-40036`) | Rev 1 → 3 | 03:39 | 04:13 | ~34 min |
| Wired `Test Anything` as a dependency, confirmed cross-app Service Action reference works (`app_refs` verified) | Rev 3 → 4 | 04:20 | 04:22 | ~2 min |
| `TestEntity_Suite` BDD screen (6-step Gherkin scenario, `LayoutBase`/`BDDScenario`/`BDDStep`/`FinalResult`) — required 3 follow-up fixes: role blocking `AnonymousAccess`, guessed `BDDFramework_AuthToken` Setting, deliberate fail-rendering test (inconclusive — see below) | Rev 4 → 11 | 04:14 | 05:15 | ~1 hr |

**Known open issue:** the suite rendered "ALL SCENARIOS PASSED" regardless of assertion content in this session's testing — confirmed not caching (fresh incognito), not exception-swallowing, not mis-wiring (all verified node-by-node against the live model). Root cause is inside the BDD Framework library's own compiled logic, not visible via Mentor's Model API. Documented in `dbresults-odc-bdd-crud-tests`'s Known Issues / Verification Checklist — treat any future BDD suite's "pass" as unverified until fail-rendering is explicitly confirmed by deliberately breaking an assertion.

---

_Add a new dated section for each session. Two formats are used:_

**With timing (when you want to track duration):**
```markdown
### [App Name] (`[app-key]`) — YYYY-MM-DD

| Build | Revision | Start (UTC) | End (UTC) | Duration |
|---|---|---|---|---|
| [description] | Rev N → N+1 | [start] | [end] | [duration] |
```

**Without timing (quick log):**
```markdown
### [App Name] (`[app-key]`) — YYYY-MM-DD

| Build | Revision | Notes |
|---|---|---|
| [description] | Rev N → N+1 | [notes] |
```
