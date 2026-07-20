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

### TestNewWebApp (`0ba4fa1f-637a-4432-9274-c934b221046e`) — 2026-07-20

New blank web app (`app_create`), then scaffolded via `dbresults-odc-new-app-baseline` (6 batches). Brand color `#1E88E5`, reused the auto-generated `TestNewWebApp` role.

| Build | Revision | Notes |
|---|---|---|
| Flows (Common/Layouts/Emails/MainFlow) + themes (`TestNewWebApp`, `EmailTheme`) + role + 3 client vars + 2 images | Rev 1 → 2 | Batch 1/6 |
| 5 layout blocks + 4 common blocks; wired theme's default layout/menu to `LayoutTopMenu`/`Menu` | Rev 2 | Batch 2/6 |
| 6 auth screens (Login, RecoverPasswordRequest, RecoverPasswordReset, ChangePassword, InvalidPermissions, UserProfile) — stubbed logic | Rev 2 | Batch 3/6 |
| 3 server + 5 client actions (Authentication folder) + wired the 7 screen stubs to real logic | Rev 2 | Batch 4/6 |
| 2 email templates (ResetPassword, ChangeEmail) + `RedirectToURL` external site | Rev 2 | Batch 5/6 |
| App-wide `OnException` handler (Security/Database/Communication/All Exceptions) registered as the app's exception flow | Rev 2 | Batch 6/6 |

All 6 batches landed in a single revision (Mentor auto-saved/published as it went — `publish_start` afterward correctly reported `no_changes_detected: true`). Verified post-publish via `context_themes`/`context_screens`/`context_actions` against deployed revision 2 — 2 themes, 6 screens, 8 actions all confirmed. 0 validation errors across every batch. Deployed to Development: https://dbresults-rd-dev.outsystems.app/TestNewWebApp

**Note:** initial pre-flight showed a pre-existing "ImplicitSelfUserProvider" performance warning (no explicit User Provider set, since there's no dedicated "Users" identity app in this tenant — each app self-contains its own auth per this baseline convention). Running the baseline resolved it implicitly by giving the app its own real Login/auth flow.

### TestNewWebApp2 (`0b77e8b9-57b5-4a4c-98d5-f947de6e495c`) — 2026-07-20

Test run of the updated `dbresults-odc-new-app-baseline` skill (8-batch structure with `IsUserProvider` fix, OutSystemsUI version pre-flight, mandatory wiring instruction, UserProfile split into its own batch, final validation sweep). Brand color `#1E88E5`, reused auto-generated role.

| Build | Notes |
|---|---|
| Batches 1-8 (flows/themes/role/IsUserProvider → layout+common blocks → screens → UserProfile → Authentication actions → email templates → OnException → validation sweep) | 0 errors every batch; final sweep classified all 11 remaining warnings as expected-at-baseline (Menu nav items, layout customization params) — vs. dozens of unexplained "Unused Action" warnings in the original (pre-fix) skill run on TestNewWebApp |
| Batch 5 crash-and-recovery | First attempt hit a transient upstream 500; state inspection confirmed no partial corruption; retry succeeded after fixing 2 naming collisions (`DoLogout`/`GetExternalLoginURL` clashing with referenced action names) |
| Publish debugging (`OS-DPL-42202`, then `OS-BEW-CODE-40036`) | 9 build failures total across 3 diagnosis rounds. Root causes: (1) the Batch 5 crash-recovery had left **two distinct folders both literally named "Authentication"** (one server-actions-scoped, one client-actions-scoped) — validates clean, fails the build compiler; (2) the `(System)` reference had a genuinely zero hash, and the tenant's live `User` entity schema had actually changed (`IsActive`/`Phone`/`ExternalId` removed, `PhotoUrl` added) vs. what was originally referenced — required re-adding the entity dependency and fixing 3 downstream expressions |

**Skill validation result:** the wiring-instruction and Batch-8-sweep additions worked as intended — 0 unwired actions this run vs. dozens previously. The build-failure debugging surfaced two *new* failure classes worth folding into the skill: (a) crash-recovery sequences that manually recreate folders/rename actions can leave duplicate/orphaned structural objects that pass `GetValidationMessages` but fail the actual build — worth a post-crash-recovery structural sanity check; (b) system entity references can silently drift (zero hash, schema changes) independent of anything the skill does — worth a pre-flight check that the `(System)` reference has a non-zero hash before starting.

Deployed to Development: https://dbresults-rd-dev.outsystems.app/TestNewWebApp2

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
