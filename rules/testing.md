---
description: ODC BDD Framework testing conventions. Apply when generating or reviewing BDD-style test scenarios for ODC entity CRUD wrapper actions.
---

# ODC BDD Testing Conventions

## Opt-in

- BDD Framework tests are never the default response to "add tests" — always ask whether the user wants full BDD Framework (Gherkin, separate test app, official reporting) or a lighter option (`outsystems-mentor-copilot`'s `test-generation` task) before generating anything

## Cross-App Access

- `{Entity}`'s CRUD wrapper actions stay **private** Server Actions on their owning app — never
- Cross-app test access goes through **Service Actions** (`IServiceAction`, a distinct action kind) — thin wrappers around the private actions, suffixed `_SA` to avoid name collision
- Never mark a Server Action `Public = true` directly on an Application to expose it cross-app — `ModelFeature_ServerActionPublicPropertyApp` is a removed platform feature (`OS-BLD-40409`); it validates locally but fails at publish
- Never route cross-app CRUD test access through a Library — a Library cannot depend on an Application (only Library-to-Library), and cannot own server (database-backed) entities at all

## Test App

- The test app is created via `app_create` → `dbresults-odc-new-app-baseline` — never `outsystems-spec-driven-build`/`outsystems-design-to-app` alone, and never hand-assembled
- Confirm the test app's baseline (auth, theme, layout) is genuinely working before adding any BDD screens
- Confirm the test app has the source app listed as a live dependency (`app_refs`) after wiring — don't assume the reference landed just because Mentor said so

## Suite Screen

- BDD Suite screens are built from the framework's own blocks (`LayoutBase`, `BDDScenario`, `BDDStep`, `FinalResult`) — the template screens (`New_Suite` etc.) are not public elements and cannot be cloned
- Suite screens are `AnonymousAccess = true` with **no role attached** — an attached role overrides anonymous access regardless of the flag's value
- One `BDDStep` + one screen action per Given/When/Then line, wired via the `NotifyRunStepLogic` block event — no `OnInitialize`/lifecycle wiring

## Assert Placement

- `Assert`/`AssertTrue`/`AssertFalse`/`AssertValue` calls only in Given and Then steps — never in When
- When steps call the Service Action under test and store its output; they do not assert
- `AssertTrue`/`AssertFalse` have no output parameters — they signal failure by throwing an exception, caught internally by `BDDStep`; there is no return value to branch on

## Reusable Steps

- Organize step logic by Given/When/Then intent — but for a single hand-written scenario, step logic correctly lives as screen actions (wired to `BDDStep` events), not standalone client actions; empty Given/When/Then folders in the client-action tree are the expected result, not a mistake

## Coverage

- Every CRUD wrapper action (`_Validate`, `_Upsert`, `_GetCanRemove`, `_Remove`) gets at least one scenario

## Verification Discipline

- `no_changes_detected: true` on publish is often harmless here (Mentor's own turn saves frequently already deploy) — confirm actual state via `context_actions`/`context_screens`/`app_refs`, allowing for brief Context Service indexing lag, rather than trusting the publish response alone
- Never claim a suite "passes" from a rendered result alone — deliberately invert one assertion, republish, and confirm the rendered result actually changes before trusting it
- If a suite reports pass regardless of assertion content, that's a known unresolved BDD Framework issue (traced to the library's own compiled logic, not visible from the Model API) — flag it explicitly to the user rather than reporting false success or chasing it indefinitely
