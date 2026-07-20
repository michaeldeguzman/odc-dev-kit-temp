# OutSystems MCP — Project Notes

## Conventions

@rules/error-handling.md
@rules/database.md
@rules/testing.md
@rules/organization.md
@rules/screens.md
@rules/descriptions.md

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

### TestNewWebApp3 (`08192363-3cdf-4322-adb1-ed1ef20a293b`) — 2026-07-20

New blank web app (`app_create`), scaffolded via `dbresults-odc-new-app-baseline` (8-batch structure). Brand color `#1E88E5`, reused the auto-generated `TestNewWebApp3` role.

| Build | Notes |
|---|---|
| Batches 1-8 (flows/themes/role/IsUserProvider/client vars/images → layout+common blocks → 5 auth screens → UserProfile → Authentication actions → email templates + RedirectToURL → OnException → validation sweep) | 0 errors every batch; final sweep left only 4 expected warnings (external-provider group inert with no IdP configured, `Emails` theme-size suggestion) |
| Batch 3 self-correction | Mentor added a partial (`AllExceptions`-only) `OnException` handler mid-batch to silence a validation warning; Batch 7 found and extended it in place to the full 4-branch handler rather than creating a duplicate |
| Batch 6 TODO closure | All Batch-2/3/4/5-deferred TODO comment nodes closed and confirmed via exhaustive eSpace-wide search; only 3 environment-limited `SetIconLibraryClass` TODOs remain (OutSystemsUI action not accessible as a reference in this environment — needs manual wiring in ODC Studio) |
| Pre-publish structural check | No duplicate folders (2 distinct `Authentication` folders, one per ServerActions/ClientActions scope, correct); no orphaned action-folder assignments; `(System)` and `OutSystemsUI` reference hashes remained all-zero even after both documented fix attempts (`RefreshDependency`, `add_references_to_elements`) — confirmed as a Model-API-sandbox limitation (cannot reach the tenant's live signature service), not data corruption; flagged as a known `OS-BEW-CODE-40036`-pattern risk |
| Publish | `publish_start` reported `no_changes_detected: true` — Mentor had already auto-published during the batches. Verified via `env_app`: deployed at revision 2, live URL, deployment timestamp matching session time. `context_themes`/`context_screens`/`context_actions` returned 0 results even after retries — Context Service indexing lag on this brand-new app, not a deployment failure |

**Note:** unlike TestNewWebApp2, the `(System)`/`OutSystemsUI` reference hash issue did NOT cause a build failure this time — the publish succeeded (as a no-op) without hitting `OS-BEW-CODE-40036`. Worth revisiting whether the hash check is a reliable predictor of that failure mode, or whether it only bites under specific additional conditions (e.g. the `User` entity schema drift also seen in TestNewWebApp2).

Deployed to Development: https://dbresults-rd-dev.outsystems.app/TestNewWebApp3

### TestNewWebApp4 (`af2af872-e4ee-400d-be87-10c2a95e1e89`) — 2026-07-20

New blank web app (`app_create`), scaffolded via `dbresults-odc-new-app-baseline` (8-batch structure). Brand color `#1E88E5`, created `TestNewWebApp4` role (no auto-generated role from `app_create` on this run — 0 roles returned, role created in Batch 1).

| Build | Notes |
|---|---|
| Batches 1-8 (flows/themes/role/IsUserProvider/client vars/images → layout+common blocks → 5 auth screens → UserProfile → Authentication actions → email templates + RedirectToURL → OnException → validation sweep) | 0 errors every batch; final sweep 0 errors, 1 known false positive (UserProfile OnInitialize aggregate access); Batch 8 proactively removed `TestNewWebApp4` role from `RedirectToURL` (platform default, inconsistent with AnonymousAccess=True) |
| `app_create` returned 0 roles | Unlike prior runs, no auto-generated role — created `TestNewWebApp4` role manually in Batch 1. `CheckTestNewWebApp4Role` name-collided with role's own generated boolean function; platform auto-renamed to `CheckTestNewWebApp4Role2` |
| No `PhotoUrl` on User entity | This tenant's `User` entity has: `Id, Name, Username, IsActive, Email, Phone, ExternalId` — no `PhotoUrl`. UserProfile OldPhotoURL set to `""` always; `Client.UserPhotoURL` never populated from User entity |
| `SetIconLibraryClass` unavailable | Not exposed as public element on this tenant — OnInitialize stubs remain as comment nodes in layout blocks; needs manual wiring in ODC Studio |
| (System) / OutSystemsUI reference hashes all-zero | Same sandbox limitation as TestNewWebApp3 — flagged but did not cause build failure |
| Publish | `publish_start` reported `no_changes_detected: true` — Mentor auto-published during batches. Verified via `env_app`: revision 2, deployed 2026-07-20T10:03:37Z |

Deployed to Development: https://dbresults-rd-dev.outsystems.app/TestNewWebApp4

### TestNewWebApp5 (`9fa47a3a-20a2-4c84-8324-1d0348f857b6`) — 2026-07-20

New blank web app (`app_create`), scaffolded via `dbresults-odc-new-app-baseline` (8-batch structure). Brand color `#1E88E5`, reused the auto-generated `TestNewWebApp5` role. Session was resumed from a compacted prior context — Batch 4 was in-flight at compaction time.

| Build | Notes |
|---|---|
| Batches 1-8 (flows/themes/role/IsUserProvider/client vars/images → layout+common blocks → 5 auth screens → UserProfile → Authentication actions + screen wiring → email templates + RedirectToURL → OnException → validation sweep) | 0 errors every batch; final sweep 0 errors, 4 known-false-positive warnings (SetIconLibraryClass — all 4 layout blocks) |
| Batch 3 crash — Comment node as If-branch target | `UnrecoverableException: Cannot change the target node to [comment text]`. Platform disallows comment nodes as If True/False branch targets. Full transaction rollback (clean state confirmed). Fix: remove all comment nodes from branch positions — omit deferred calls entirely rather than placeholder-comment them; Batch 5 inserts the real call between existing nodes. |
| User entity confirmed attributes | `Id (Text), Name (Text), Email (Email), PhotoUrl (Text), Username (Text)` — this run has `PhotoUrl` (contrast with TestNewWebApp4 notes). `IsActive`/`Phone`/`ExternalId` absent. |
| Platform system actions used | `Login`, `Logout` (auth); `UpdateUserProfile` (profile update); `StartResetPassword`, `StartUpdateEmail` (email flows) — names confirmed live from (System) reference during Batch 5 |
| `CheckTestNewWebApp5Role2` | Platform auto-renamed the CheckTestNewWebApp5Role client action wrapper to avoid collision with the built-in role-check function — same pattern as TestNewWebApp4. Deleted in Batch 8 (Login uses the built-in function directly; wrapper was redundant) |
| `DoLogout` — caller handles redirect | Client action clears vars but does not itself redirect; UserInfo.ClientLogout calls DoLogout then redirects to Login |
| `SetIconLibraryClass` unavailable | Same sandbox limitation — 4 Reminder nodes in layout block OnInitialize; needs manual wiring in ODC Studio |
| `(System)` / OutSystemsUI reference hashes all-zero | Same sandbox limitation as TestNewWebApp3/4 — flagged but did not cause build failure |
| Publish | `publish_start` reported `no_changes_detected: true` — Mentor auto-published during batches. Verified via `env_app`: revision 2, deployed 2026-07-20T11:45:19Z |

Deployed to Development: https://dbresults-rd-dev.outsystems.app/TestNewWebApp5

### TestNewWebApp6 (`9ee7bc33-0108-4b8a-8556-2ce6a7e72c77`) — 2026-07-20

New blank web app (`app_create`), scaffolded via `dbresults-odc-new-app-baseline` (8-batch structure). Brand color `#1E88E5`, reused the auto-generated `TestNewWebApp6` role. Session resumed from a compacted prior context — Batch 3 retry was in-flight at compaction time.

| Build | Revision | Notes |
|---|---|---|
| Batches 1-8 (flows/themes/role/IsUserProvider/client vars/images → layout+common blocks → 5 auth screens → UserProfile → Authentication+UserActions server+client actions + deferred wiring → email templates + RedirectToURL → OnException → validation sweep) | Rev 1 → 2 | 0 errors every batch; final sweep 0 errors, 8 expected-at-baseline warnings |
| Batch 3 crash — Comment node as If-branch target | — | `UnrecoverableException: Cannot change the target node to TODO: ...`. Same pattern as TestNewWebApp5. Fix: retry with explicit no-comment-nodes-in-branch-positions rule. |
| `HasTestNewWebApp6Role` (not `CheckTestNewWebApp6Role`) | — | `CheckTestNewWebApp6Role` is reserved by the platform for the auto-generated role function; wrapper named `HasTestNewWebApp6Role` to avoid collision |
| No `PhotoUrl` on User entity | — | This tenant's `User` entity: `Id, Name, Username, IsActive, Email, Phone, ExternalId` — no `PhotoUrl`. `OldPhotoURL` always `""`, `Client.UserPhotoURL` never populated from User entity |
| `ISendEmailNode` programmatic creation blocked | — | Sandbox throws internal exception regardless of template existence. `TryGetNameByEmail` aggregates and `ApplicationName` params correctly positioned in server actions; SendEmail nodes must be wired manually in ODC Studio for both `SendResetPasswordEmail` and `SendChangeEmail` |
| `SetIconLibraryClass` unavailable | — | Same sandbox limitation — 4 Reminder nodes in layout block OnInitialize; needs manual wiring in ODC Studio |
| `(System)` / OutSystemsUI reference hashes all-zero | — | Same sandbox limitation as TestNewWebApp3/4/5 — flagged but did not cause build failure |
| Batch 8 fixes | — | `EmailTheme.IconLibrary` incorrectly cleared to empty string — restored to `Phosphor2.0`; anonymous screens had `TestNewWebApp6` role attached — removed |
| Publish | — | `publish_start` reported `no_changes_detected: true` — Mentor auto-published during batches. Verified via `env_app`: revision 2, deployed 2026-07-20T13:50:20Z |

Deployed to Development: https://dbresults-rd-dev.outsystems.app/TestNewWebApp6

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
