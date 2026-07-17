---
name: dbresults-odc-bdd-crud-tests
description: Use when asked to add BDD-style / Gherkin-style backend tests for an ODC entity's CRUD wrapper actions, using OutSystems' official BDD Framework Forge component. Covers generating one BDD scenario per CRUD wrapper action (Validate/Upsert/GetCanRemove/Remove), the required Library-Service-Action wiring for a genuinely separate test app, and the exact ODC-specific gotchas that don't match the public docs. Does NOT replace `outsystems-mentor-copilot`'s lighter `test-generation` task — use that for non-BDD test scaffolds. First step is always an opt-in question — do not assume BDD Framework is wanted just because someone asks for "tests".
---

# ODC BDD Framework Tests — CRUD Wrapper Coverage

## Step 0 — Opt-in gate (always ask first)

The ODC BDD Framework is a Forge component OutSystems marks **non-supported**, with incomplete ODC-specific documentation, an extra `AuthenticationSecretToken`/Setting configuration step, a separate test app per source app, and — per this skill's own derivation — **at least one unresolved bug where a suite can render "ALL SCENARIOS PASSED" regardless of actual assertion outcome** (see Known Issues). That's real overhead and real risk.

**Before generating anything, ask:**

> "Do you want full BDD Framework tests (Gherkin scenarios, separate test app, official pass/fail reporting) or something lighter — e.g. `outsystems-mentor-copilot`'s `test-generation` task?"

Only proceed past this point if the user confirms BDD specifically.

## Overview

Derived from a real, hands-on build against a live tenant — not written from docs alone (the same way `dbresults-odc-crud-wrapper` was derived from `ModelApplication`). Two architecture paths were tried and **failed** before finding the one that works; both failures are documented below because they're the exact traps this skill exists to prevent you from re-walking into.

This skill is **generic** — `{Entity}`, `{App}` (the entity's owning app), and `{TestApp}` (the separate test app) are placeholders. Reference `PROJECT_CONFIG.md` for the active app/tenant the same way `dbresults-odc-catchup` and `dbresults-odc-ship` do — never hardcode a project's specific app/entity names into this file.

## Prerequisites

1. **BDD Framework installed in the tenant.** Check via `app_list {search: "BDD"}` — expect exactly 4 modules:
   - `BDD Framework` (LowCodeLibrary) — the library consuming apps reference directly (`Assert`, `AssertTrue`, `AssertFalse`, `AssertValue`, `AssertFail`, `ExceptionHandler`, `ValidateTestCanBeTriggered`)
   - `BDD Framework API` (WebApplication) — internal, not called directly
   - `BDDFrameworkTestRunLib` (ExternalLibrary) — exposes `TestRun(testURL, executionTimeout)`, an external headless-execution action (not directly invokable via the standard MCP tool surface — no generic "call any action" tool exists there; verifying pass/fail today means opening the suite screen in a real browser)
   - `Template_BDD Framework` (WebApplication) — **template-only**, not usable as a dependency (see Known Issues)

   **If not installed:** stop and tell the user. Installing a Forge component isn't possible through the MCP tools available — it requires Service Studio (Forge tab → search "BDD Framework" → Install) or the Forge portal directly. Wait for confirmation before continuing.

2. **The target entity's CRUD wrapper actions already exist.** If they don't, generate them first via `dbresults-odc-crud-wrapper` — don't write BDD tests against actions that don't exist yet.

3. **`PROJECT_CONFIG.md`** for the active app name/key/tenant.

## Architecture — read this before wiring anything

**The goal:** the BDD test suite must live in a genuinely separate app from `{App}` (the entity's owner), not bundled into it — but `{Entity}`'s CRUD wrapper actions are private Server Actions on `{App}`, and ODC Applications cannot expose private server actions to other apps directly.

**Two paths were tried and empirically confirmed broken. Do not repeat them:**

### ❌ Path 1: Wrap in a Library between `{App}` and `{TestApp}`

Sounds right ("only a Library can expose public Service/Server Actions across app boundaries") but **fails on two independent, unconditional platform rules**, confirmed via live Mentor investigation and an actual failed build attempt:

- **A Library can only reference other Libraries** (or external libraries) — never a web/mobile Application, regardless of whether the Application's actions are marked Public. Attempting to add an Application as a Library's dependency fails with *"The element is not available"* even after marking target actions Public.
- **Libraries cannot own server (database-backed) entities at all** — not a visibility issue, a structural one. If `{Entity}` needs `Create{Entity}`/`Update{Entity}`/`Get{Entity}ForUpdate`, it cannot live in a Library. Attempting this is rejected outright: *"Libraries do not support server entities."*

There is no combination of these two rules that makes "put a wrapping Library in the middle" work when the entity itself must stay in an Application.

### ❌ Path 2: Server Action + `Public = true` on the Application

The obvious next attempt — just mark the existing private `{Entity}_Upsert` etc. Public directly on `{App}`. **This is a removed platform feature.** The model API allows setting `Public = true` on a Server Action and validates clean locally, but the actual **publish/build fails**:

```
Using the feature ModelFeature_ServerActionPublicPropertyApp, a feature
that has been removed. (OS-BLD-40409)
Model features validation failed (OS-DPL-50205)
```

Local validation passing is **not proof of buildability** — this only surfaces at actual publish time. If you hit this, revert the Public flags immediately and republish to restore a working state before trying the real fix below.

### ✅ The mechanism that actually works: Service Actions

ODC has a **distinct action kind** called Service Action (`IServiceAction`, its own collection separate from `IServerAction`) — not "Server Action with Public ticked," a genuinely different object. Confirmed empirically:

- Model API supports `CreateServiceAction` on a plain web Application (`CrossDevice`) — no removed-feature error, builds and publishes clean
- Defaults to `Public = true` automatically — no toggle needed
- Implements the same `IShareable`/`IShareableESpaceObject` interfaces as other cross-app-referenceable elements
- **A separate Application CAN add another Application as a dependency to consume its Service Actions** — confirmed via `app_refs` showing the producer app listed as a live reference after adding, with 0 build errors

**The pattern:**

1. In `{App}`, create 4 thin Service Actions wrapping the existing private CRUD actions — same inputs/outputs, body is just "call the private action, pass through its outputs." Do not duplicate the CRUD logic itself; wrap it.
2. **Naming collision:** the platform enforces unique names across action kinds within one module — you cannot have a Service Action and a Server Action both named `{Entity}_Upsert` in the same app. Suffix the Service Actions, e.g. `{Entity}_Upsert_SA`.
3. **Structure dependencies must also be Public.** If a Service Action returns `EntityActionResult`, that structure (and anything it embeds, like `EntityActionMessage`) must be marked Public too — the platform requires a public action's signature types to also be public. Do this at the same time; the build will otherwise fail even though the action itself is fine.
4. Publish `{App}`.
5. Create `{TestApp}` via `app_create` → `dbresults-odc-new-app-baseline` (see next section) — **not** `outsystems-spec-driven-build` alone, and not a hand-assembled bare module.
6. In `{TestApp}`, add `{App}` as a dependency and reference the 4 `*_SA` Service Actions. This pulls in `{Entity}`, `EntityActionResult`, `EntityActionMessage`, and any static entities (e.g. `MessageType`) as transitive dependencies automatically — you don't need to add them separately.
7. Publish `{TestApp}` and confirm via `app_refs {key: "<TestApp key>"}` that `{App}` is listed as a live reference.

The original private CRUD actions on `{App}` **must remain private** — flag it if a scenario ever tries to reference them directly instead of the `*_SA` wrappers; that will fail to publish (or, worse, hit the removed-feature error if someone tries the Public-toggle shortcut instead).

## Test app creation

**Chain: `app_create` → `dbresults-odc-new-app-baseline`.** Do not substitute `outsystems-spec-driven-build` or `outsystems-design-to-app` for the baseline step — both assume an auth/theme/layout foundation already exists and will not build it. `app_create` alone is a genuinely blank shell (0 screens/actions/themes, 1 auto-generated role).

Run `dbresults-odc-new-app-baseline`'s own pre-flight and verification checklist (theme count, role, 6 auth screens, server/client actions) — don't invent a separate check. **Before adding any BDD screens, confirm the test app is actually usable**: publish it, and be aware that a fresh `(System)` entity reference can be stale out of the box (see Known Issues) — verify via `context_screens`/`context_actions`/`context_themes` that the baseline actually landed, not just that Mentor said so.

If a harness/CRUD-exercise screen is needed for anything beyond the BDD suite screen itself (e.g. a UI to manually poke at the entity), generate it via `dbresults-odc-scaffold-entity` — don't hand-build one.

## The BDD Suite screen

**`New_Suite` / `DataDrivenXlsScenario_Suite` / `DataDrivenDbScenario_Suite`** (in `Template_BDD Framework`'s `ScreenTemplates` flow) are **not public elements** — they cannot be cloned or referenced from another app via the model API. **Recreate the pattern by hand** using the BDD Framework's own blocks, confirmed via direct inspection of a live suite screen:

- **`LayoutBase`** block — takes `AuthToken: Text` (mandatory). Handles the security check (see AuthToken section) and renders the test page chrome.
- **`BDDScenario`** block — no inputs. Visual container grouping one scenario's steps.
- **One `BDDStep` block per step** — no inputs. Exposes a single event, `NotifyRunStepLogic` (no parameters), which must be wired to a screen action containing that step's actual logic.
- **`FinalResult`** block — takes `IsDataDriven: Boolean` (mandatory, set `False` for a hand-written scenario). Renders the pass/fail summary.

**Screen structure:**
- Input parameter: `AuthToken` (Text) — passed through to `LayoutBase`
- **`AnonymousAccess = true`, and NO role attached.** This is a real trap: attaching a role to the screen overrides the anonymous flag regardless of its value — the platform enforces the role if one is present, full stop. If a BDD screen redirects to Login instead of running, this is almost certainly why; remove the role, don't just double check the flag.
- Local variables as needed to pass state between steps (e.g. an identifier created in an early step, consumed in a later one)
- One screen action per step, each wired to its `BDDStep`'s `NotifyRunStepLogic` event — no `OnInitialize` or other lifecycle wiring; the framework drives execution entirely through the step-event chain

**Organize step logic by Given/When/Then**, per the framework's own convention — but note: if step logic ends up as screen actions (which it will, since `NotifyRunStepLogic` is a block event wired to a screen action, not a standalone client action), any Given/When/Then folders you create in the client-action tree will end up empty. That's the correct outcome for a single hand-written scenario, not a mistake — don't try to force step logic into standalone client actions just to populate the folders.

## The 4 scenarios (one per CRUD wrapper action, prioritized)

Cover each of `{Entity}`'s 4 CRUD wrapper actions with at least one scenario:

```gherkin
Scenario: Create, validate, and remove a {Entity} record
Given a {Entity} record with valid required fields
When I call {Entity}_Upsert_SA
Then the record should be created successfully with a valid Id
Given the created {Entity} record
When I call {Entity}_Remove_SA
Then {Entity}_GetCanRemove_SA should report it as already removed
```

**Assert placement — Given/Then only, never When:**
- `AssertTrue`, `AssertFalse`, `Assert`, `AssertValue` calls belong in Given and Then steps
- When steps call the Service Action and store its output (e.g. an `Id`) in a screen variable — no assertions here

**Mechanically important:** `AssertTrue`/`AssertFalse`/etc. have **zero output parameters**. They signal failure by *throwing an exception*, which `BDDStep`'s own internal handler catches. There's no Boolean to check downstream — don't add dead-code branches trying to inspect a return value that doesn't exist.

## AuthenticationSecretToken

`ValidateTestCanBeTriggered(AuthToken)` (in the `BDD Framework` library) matches the URL's `AuthToken` parameter against a secret defined in **the consuming app's own Settings** — not a Site Property on the library (libraries can't have Settings at all). The exact Setting name the framework reads is **not confirmed from the model API alone** — `BDDFramework_AuthToken` was used as a working guess and did resolve the block correctly in one live test, but treat this as unverified convention, not documented fact, until you've confirmed it against ODC Portal → `{TestApp}` → Settings after a publish. If the guessed name doesn't work, the framework may register its own expected name at publish time — check there rather than guessing again blindly.

The screen's `AuthToken` input parameter is populated the same way any screen input parameter is: as a URL query parameter, e.g. `?AuthToken=<value>`.

## Verifying it actually works — do this by eye, every time

`no_changes_detected: true` on `publish_status` is usually harmless here — Mentor's own turn-level saves often already deploy to the environment, making the explicit `publish_start` call a confirmatory no-op rather than a failure signal. Don't treat it as proof nothing happened; verify via `context_actions`/`context_screens`/`app_refs` (allow a short delay — Context Service indexing lags slightly behind a real publish).

**Known unresolved issue — read before claiming a suite "passes":** in this skill's own derivation, a built suite rendered **"ALL SCENARIOS PASSED" regardless of the actual assertion content** — confirmed by inverting a `Then` step's condition to a guaranteed-false expression, republishing, hard-refreshing, and even testing in a fresh incognito window, and still seeing a pass. Node-by-node model inspection ruled out every explanation visible from the Model API: no exception handler anywhere in the app or its flows, correct wiring, correct expression, no caching. The cause is almost certainly inside the BDD Framework library's own compiled logic (invisible to Mentor's introspection) — possibly related to how `BDDStep` awaits (or doesn't await) an async Service Action call before evaluating the next step, but this was never conclusively confirmed.

**Consequence: do not trust a rendered pass as proof the suite is actually exercising your assertions.** For every new suite:
1. Open it in a browser and confirm it renders at all (no `AuthToken` error, no redirect to Login)
2. Deliberately invert one assertion to a guaranteed-false condition, republish, and confirm the rendered result actually changes to a fail
3. If it doesn't change — as happened here — flag this to the user explicitly as the same unresolved framework issue rather than reporting a false success. Don't spend unbounded Mentor cycles chasing it further than one focused investigation pass; it's a known gap, not something to silently work around.

## Mentor Prompt Template

```
--- Service Action wrappers (in {App}) ---

Create 4 Service Actions (the distinct IServiceAction kind — not Server
Action with Public ticked) that each thinly wrap the corresponding
existing private Server Action, passing through its inputs/outputs
unchanged:

1. {Entity}_Validate_SA wraps {Entity}_Validate
2. {Entity}_Upsert_SA wraps {Entity}_Upsert
3. {Entity}_GetCanRemove_SA wraps {Entity}_GetCanRemove
4. {Entity}_Remove_SA wraps {Entity}_Remove

Mark the underlying EntityActionResult and EntityActionMessage structures
Public (required for a public action's signature types). Do not change
the private Server Actions' logic — they stay exactly as-is, still
private.

--- BDD Suite screen (in {TestApp}, after adding {App} as a dependency) ---

Create a screen "{Entity}_Suite" (Common flow, AnonymousAccess = true,
NO role attached) implementing this scenario using the BDD Framework's
LayoutBase / BDDScenario / BDDStep / FinalResult blocks:

Scenario: Create, validate, and remove a {Entity} record
Given a {Entity} record with valid required fields
When I call {Entity}_Upsert_SA
Then the record should be created successfully with a valid Id
Given the created {Entity} record
When I call {Entity}_Remove_SA
Then {Entity}_GetCanRemove_SA should report it as already removed

Input parameter AuthToken (Text) wired to LayoutBase. One BDDStep +
screen action per Given/When/Then line (6 total), each screen action
wired to its BDDStep's NotifyRunStepLogic event. Use AssertTrue in
Given/Then steps only, never in When steps — When steps only call the
Service Action and store its output.
```

## Edge Cases

| Scenario | Handling |
|---|---|
| Entity has multiple mandatory business fields | Cover each in the `Given`/`Validate` scenario, same as `dbresults-odc-crud-wrapper`'s Validate pattern |
| `{App}` already has some `_SA` actions from a prior BDD build | Check via `context_actions` before creating duplicates |
| Stale `(System)` User entity reference on `{TestApp}` (`OS-BEW-CODE-40036`, *"uses entity 'User' that is incompatible with its definition in reference '(System)'"*) | A soft "refresh dependencies" is not sufficient — it must be a hard remove-and-re-add of the `(System)` reference to fully re-pull the entity shape. Also check for now-removed attributes referenced elsewhere (e.g. `ExternalId` was removed from the current platform `User` shape in favor of `PhotoUrl` — any screen built by `dbresults-odc-new-app-baseline` referencing the old shape needs those call sites fixed too) |
| Suite screen redirects to Login instead of running | Check for an attached role on the screen — remove it; `AnonymousAccess = true` alone is not sufficient if a role is also present |
| `AuthToken` "not valid" error | Confirm the Setting exists and matches in ODC Portal → `{TestApp}` → Settings; don't assume the guessed name (`BDDFramework_AuthToken`) is correct without checking |

## Verification Checklist

- [ ] Step 0 opt-in question asked and confirmed BDD specifically (not just "add tests")
- [ ] BDD Framework confirmed installed (4 modules) before building anything
- [ ] Target entity's CRUD wrapper actions exist (built via `dbresults-odc-crud-wrapper` if missing)
- [ ] 4 Service Actions (`*_SA`, `IServiceAction` kind — not Server Action + Public) created wrapping the private CRUD actions
- [ ] `EntityActionResult`/`EntityActionMessage` (and any other signature-referenced structures) marked Public
- [ ] Original private CRUD actions remain private — not converted, not exposed directly
- [ ] `{App}` published clean (0 errors) after adding the Service Actions
- [ ] `{TestApp}` created via `app_create` → `dbresults-odc-new-app-baseline`, baseline verified (not skipped, not substituted with `outsystems-spec-driven-build` alone)
- [ ] `{TestApp}` login/baseline confirmed actually working before adding BDD screens
- [ ] `{TestApp}` has `{App}` listed as a live dependency in `app_refs` — confirms the Service Action reference actually landed
- [ ] BDD Suite screen built from framework blocks (LayoutBase/BDDScenario/BDDStep/FinalResult) — not assumed to be clonable from `Template_BDD Framework`
- [ ] Suite screen is `AnonymousAccess = true` with **no role attached**
- [ ] `AuthToken` Setting configured and confirmed in ODC Portal (name verified, not assumed)
- [ ] Asserts present only in Given/Then steps, never in When
- [ ] Suite opened in a real browser and confirmed to render (not just "0 build errors")
- [ ] Fail-rendering explicitly verified by deliberately breaking one assertion, republishing, and confirming the result actually changes — flagged to the user if it doesn't (known unresolved framework issue, don't silently claim success)
- [ ] Every CRUD wrapper action (Validate/Upsert/GetCanRemove/Remove) covered by at least one scenario

## Related Skills

- `dbresults-odc-crud-wrapper` — generates the CRUD wrapper actions this skill tests; run first if they don't exist
- `dbresults-odc-scaffold-entity` — for any harness screen needed beyond the BDD suite screen itself
- `dbresults-odc-new-app-baseline` — required step when creating `{TestApp}`, run via `app_create` → this skill, never substituted
- `outsystems-mentor-copilot` (`test-generation` task) — lighter, non-BDD test scaffolding; use instead of this skill when the user declines BDD at Step 0
- `odc-action-reviewer` — invoke first if a scenario touches CRUD wrapper actions that were just created/modified; that agent owns CRUD wrapper compliance, this skill's own reviewer (`odc-test-reviewer`) only checks test-specific concerns
