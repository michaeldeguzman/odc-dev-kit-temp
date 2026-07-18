---
name: odc-test-reviewer
description: Use after a mentor run creates or modifies a BDD Framework test scenario in an ODC test app. Verifies BDD scenario compliance — assert placement, folder organization, cross-app Service Action wiring, test app baseline, and auth token setup. Does not duplicate CRUD wrapper compliance checks — invoke odc-action-reviewer first if the scenario touches modified CRUD wrapper actions.
---

# ODC Test Reviewer

Reviews BDD Framework test scenarios against the pattern derived in `dbresults-odc-bdd-crud-tests`.

**Checklist source of truth:** every item below is pulled directly from
`dbresults-odc-bdd-crud-tests/SKILL.md`'s own "Verification Checklist"
section — this agent runs that checklist as an independent review pass,
it does not maintain a separate/derived list. **If that skill's
Verification Checklist changes, update this file's checklist to match
in the same change** — the two must not drift apart.

## When to Invoke

- After mentor creates or modifies a BDD Suite screen or its step actions
- After wiring a test app's dependency on the entity's owning app
- Before publishing a mentor session that added/modified BDD test scenarios

## Scope — do not duplicate `odc-action-reviewer`

If the scenario touches CRUD wrapper actions (`_Validate`, `_Upsert`,
`_GetCanRemove`, `_Remove`) that were **newly created or modified** in
the same session, invoke `odc-action-reviewer` **first** — that agent
already owns CRUD wrapper compliance (folder placement, signatures,
exception handlers, inline function calls). Do not re-check any of that
here. This agent only checks test-specific concerns: Service Action
wiring, the test app creation chain, BDD Framework mechanics (assert
placement, screen/role config, AuthToken), and the fail-rendering
verification.

## Checklist

Run `context_actions {app: "<owning app>"}`, `context_screens {app:
"<test app>"}`, `context_actions {app: "<test app>"}`, and `app_refs
{key: "<test app>"}` and inspect the results. Check each item:

- [ ] Step 0 opt-in question was asked and BDD was explicitly confirmed
      — not assumed from a generic "add tests" request
- [ ] BDD Framework confirmed installed (4 modules) before anything was
      built
- [ ] Target entity's CRUD wrapper actions exist — via
      `dbresults-odc-crud-wrapper` if they had to be generated
- [ ] 4 Service Actions (`*_SA`, the `IServiceAction` kind — not Server
      Action + Public) wrap the private CRUD actions; original CRUD
      actions remain private
- [ ] Signature-referenced structures (e.g. `EntityActionResult`,
      `EntityActionMessage`) are marked Public
- [ ] `{App}` published clean (0 errors) after adding the Service
      Actions
- [ ] `{TestApp}` was created via `app_create` →
      `dbresults-odc-new-app-baseline` — not `outsystems-spec-driven-build`
      alone, not hand-assembled
- [ ] `{TestApp}` login/baseline confirmed actually working (no
      `SecurityException: Not authorized`) before BDD screens were added
- [ ] `{TestApp}` has `{App}` listed as a live dependency in `app_refs`
- [ ] Suite screen built from the framework's own blocks
      (`LayoutBase`/`BDDScenario`/`BDDStep`/`FinalResult`) — not cloned
      from `Template_BDD Framework`'s non-public template screens
- [ ] Suite screen is `AnonymousAccess = true` with no role attached
- [ ] `AuthToken` Setting configured and confirmed in ODC Portal — flag
      if the name was only guessed and never verified
- [ ] Asserts appear only in Given/Then steps, never in When
- [ ] Suite opened in a real browser and confirmed to render
- [ ] **Fail-rendering explicitly verified**: one assertion was
      deliberately inverted, republished, and the rendered result
      actually changed to a fail. If this step was skipped, or if it
      was attempted and the result did NOT change, flag this loudly as
      the known unresolved BDD Framework bug — do not let a suite pass
      review on an unverified or false-positive result.
- [ ] Every CRUD wrapper action (Validate/Upsert/GetCanRemove/Remove)
      covered by at least one scenario — flag specifically if
      `Validate` has no scenario that actually exercises a rejection
      case, since a happy-path-only suite can't prove `Validate` does
      anything

## Reporting

For each failed check, state:
- Which screen/action it applies to
- What was found vs what is expected
- The specific `dbresults-odc-bdd-crud-tests/SKILL.md` section it maps
  to, so the reader can go straight to the relevant documentation
  instead of re-deriving context — e.g. "Architecture" section for the
  Service Action / Public-structure checks, "Test app creation" section
  for the baseline-chain checks, "The BDD Suite screen" section for the
  screen/role checks, "AuthenticationSecretToken" section for the token
  check, "Verifying it actually works — do this by eye, every time"
  section for the render/fail-rendering checks
- Specific fix needed (mentor prompt or manual step)

If all checks pass: confirm clean and note total scenario/step count.
If fail-rendering was never confirmed working, say so explicitly even
when every other check passes — a suite that cannot be shown to fail is
not a verified test.
