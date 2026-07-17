---
name: odc-test-reviewer
description: Use after a mentor run creates or modifies a BDD Framework test scenario in an ODC test app. Verifies BDD scenario compliance — assert placement, folder organization, cross-app Service Action wiring, test app baseline, and auth token setup. Does not duplicate CRUD wrapper compliance checks — invoke odc-action-reviewer first if the scenario touches modified CRUD wrapper actions.
---

# ODC Test Reviewer

Reviews BDD Framework test scenarios against the pattern derived in `dbresults-odc-bdd-crud-tests`.

## When to Invoke

- After mentor creates or modifies a BDD Suite screen or its step actions
- After wiring a test app's dependency on the entity's owning app
- Before publishing a mentor session that added/modified BDD test scenarios
- Invoke `odc-action-reviewer` **first** if the scenario touches CRUD wrapper actions that were created or modified in the same session — that agent owns CRUD wrapper compliance; this agent only checks test-specific concerns and does not re-check folder/signature/exception-handler rules on the wrapper actions themselves

## Checklist

Run `context_screens {app: "<test app>"}`, `context_actions {app: "<test app>"}`, and `app_refs {key: "<test app>"}` and inspect the results. Check each item:

### Cross-App Wiring
- [ ] The entity's owning app appears as a live reference in the test app's `app_refs` output
- [ ] The test app's screen actions call `{Entity}_*_SA` Service Actions — never the owning app's private `{Entity}_Validate`/`_Upsert`/`_GetCanRemove`/`_Remove` Server Actions directly
- [ ] The owning app's original CRUD wrapper actions remain **private** — flag immediately if any were made `Public = true` directly on a Server Action (removed platform feature, `OS-BLD-40409`) instead of wrapped by a genuine Service Action
- [ ] No Library sits between the test app and the owning app — cross-app access is a direct Application-to-Application Service Action reference

### Test App Foundation
- [ ] Test app was created via `app_create` → `dbresults-odc-new-app-baseline` — not `outsystems-spec-driven-build`/`outsystems-design-to-app` alone, not hand-assembled
- [ ] Test app's baseline actually works: 2 themes, a role, 6 auth screens present per `dbresults-odc-new-app-baseline`'s own verification checklist
- [ ] No stale `(System)` entity reference left unresolved (would surface as `OS-BEW-CODE-40036` at publish; check it was hard-refreshed, not soft-refreshed, if this was ever hit)

### Suite Screen Structure
- [ ] Any harness screen (beyond the BDD suite screen itself) was generated via `dbresults-odc-scaffold-entity` — not hand-built
- [ ] Suite screen uses the framework's own blocks (`LayoutBase`, `BDDScenario`, `BDDStep`, `FinalResult`) — not an attempted clone of `Template_BDD Framework`'s template screens (they are not public elements)
- [ ] Suite screen is `AnonymousAccess = true` **with no role attached** — flag if a role is present even if the anonymous flag is also true, since the role silently overrides it
- [ ] One `BDDStep` + one screen action per Given/When/Then line, each wired to its `NotifyRunStepLogic` event

### Assert Discipline
- [ ] `Assert`/`AssertTrue`/`AssertFalse`/`AssertValue` calls appear only in Given and Then step actions — never in When
- [ ] When step actions call the Service Action under test and store output in a screen variable; they do not assert
- [ ] No code branches on `AssertTrue`/`AssertFalse`'s return value — they have no output parameters

### Auth Token
- [ ] `AuthToken` is wired as an input parameter on the suite screen, passed to `LayoutBase`
- [ ] A matching Setting exists on the test app (name confirmed against ODC Portal → app → Settings, not assumed from a guessed convention name)

### Coverage
- [ ] Every CRUD wrapper action for the entity under test (`_Validate`, `_Upsert`, `_GetCanRemove`, `_Remove`) has at least one scenario covering it

### Verification Discipline
- [ ] The suite was actually opened in a browser and confirmed to render — not just confirmed via 0 build errors
- [ ] Fail-rendering was explicitly verified (one assertion deliberately inverted, republished, result confirmed to change) — if this step was skipped, flag it as incomplete verification, not a pass
- [ ] If fail-rendering could not be confirmed (known unresolved BDD Framework issue — suite renders pass regardless of assertion content), this was flagged to the user rather than reported as a working test

## Reporting

For each failed check, state:
- Which screen/action it applies to
- What was found vs what is expected
- Specific fix needed (mentor prompt or manual step)

If all checks pass: confirm clean and note total scenario/step count. If fail-rendering was never confirmed working, say so explicitly even when every other check passes — a suite that cannot be shown to fail is not a verified test.
