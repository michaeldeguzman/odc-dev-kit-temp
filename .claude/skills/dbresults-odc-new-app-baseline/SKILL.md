---
name: dbresults-odc-new-app-baseline
description: Use right after `app_create` mints a new ODC web app, BEFORE any business build (`outsystems-spec-driven-build`, `outsystems-design-to-app`, or `dbresults-odc-scaffold-entity`). `app_create`'s "blank" shell is genuinely empty — 0 screens, 0 actions, 0 themes, only 1 auto-generated role (verified empirically against a live tenant) — it does NOT include the standard authentication/theme/layout foundation every real ODC web app needs. This skill scaffolds that foundation: 3 UI flows (Common, Layouts, Emails — plus an intentionally empty MainFlow), 2 themes, the app role, client variables, images, layout blocks, common blocks, 6 auth screens, server/client actions, and email templates. Use when asked to "set up a new app", "scaffold the app baseline", "add login/auth to this app", "this app has no login screen", or before starting any greenfield build.
---

# ODC New App Baseline — Authentication / Theme / Layout Scaffold

## Overview

`app_create` mints a genuinely blank shell (0 screens, 0 actions, 0 themes, 1 role). This skill is **generic** — `{App}` below is the target app's name; `{BrandColor}` is the brand hex color. Run **once** per new app, right after `app_create`, before any business build.

## When NOT to use

- **App already has a login screen / theme / role** — run pre-flight first.
- **Adding business entities/screens** — use `dbresults-odc-scaffold-entity` / `dbresults-odc-crud-wrapper` instead.

## Pre-flight Check

1. `context_themes {app}` — if 2 themes exist, baseline likely already scaffolded. Confirm before re-running.
2. `context_screens {app}` — if `Login` exists, skip already-present layers.
3. `context_roles {app}` — note auto-generated role from `app_create`. Confirm reuse or new name with user.
4. Ask for `{BrandColor}` (hex) if not provided.
5. Confirm app `kind` is `CrossDevice`/`WebApplication` — this baseline is web-specific.
6. **`OutSystemsUI` version check:** `Phosphor2.0` requires OutSystemsUI ≥ 2.28.0. Check the version via ODC Portal/Studio's dependency panel (not the Model API enum — it accepts strings regardless of version). If below 2.28.0, request a tenant-level upgrade before publishing. After Batch 1, re-check `GetValidationMessages` for "Icon library compatibility" — do not assume pre-flight was sufficient.
7. **`(System)` reference health:** Have Mentor read the reference's `Hash` field before Batch 1. A zero hash (`00000000-0000-0000-0000-000000000000`) guarantees `OS-BEW-CODE-40036` at publish. Fix via `add_references_to_elements` or `eSpace.RefreshDependency(globalKey, updateSpecificVersion: true)` on the entity's own global key. Confirm the entity's attribute list actually changed after the fix.
8. **Do not hardcode `User` entity attribute names.** Before writing any expression that reads a `User` attribute, have Mentor query the live attribute list from the `(System)` reference — tenant schemas drift.

## Layers to Scaffold

Full parameter tables, widget trees, and wiring logic for each layer live in [`references/spec.md`](references/spec.md). Read the relevant section before starting the batch that builds it — don't rely on memory of a prior read.

1. UI Flows — `spec.md#1-ui-flows`
2. Themes — `spec.md#2-themes`
3. Role & App Identity — `spec.md#3-role--app-identity`
4. Client Variables — `spec.md#4-client-variables`
5. Local Images — `spec.md#5-local-images`
6. Layout Blocks — `spec.md#6-layout-blocks-in-layouts-flow`
7. Common Blocks — `spec.md#7-common-blocks-in-common-flow`
8. Screens — `spec.md#8-screens-in-common-flow`
9. Server Actions — `spec.md#9-server-actions`
10. Client Actions — `spec.md#10-client-actions`
11. Email Templates — `spec.md#11-email-templates-in-emails-flow`
12. External Sites — `spec.md#12-external-sites-in-common-flow`
13. App-Level Exception Handler — `spec.md#13-app-level-exception-handler`

## Required References

See [`references/gotchas.md#required-references`](references/gotchas.md#required-references) for the full reference list — add all of these before Batch 1.

## Mentor Prompt Strategy

Batch into separate `mentor_start`/resumed-session turns — smaller batches isolate failures faster.

1. **Flows + theme + role + `IsUserProvider` + client variables + images.** Create `EmailTheme` as a standalone theme (do NOT extend `OutSystemsUI`); paste `assets/EmailTheme.css` verbatim as its stylesheet; set `Emails` flow `Theme = EmailTheme` in this batch. Create `MainFlow` as empty (no screens/blocks/handler). See `spec.md#1-ui-flows` through `spec.md#5-local-images`.
2. **Layout blocks + common blocks.** Attempt `add_references_to_elements` for `SetIconLibraryClass` (global key `Kn_hixxDWEm4lMd7mIpycQ*l+LGqvnbjEWzX1y8Hxcx+g`) first; create local stub if it fails. For every block parameter, explicitly set: **IsMandatory = False** (Mentor defaults to mandatory), **description** (non-empty), **default value** (per `spec.md#6`), **correct type** (`MenuBehavior` = `SideMenuBehavior Identifier`, not Text). Bind every parameter into a real widget property. For LayoutTopMenu: build the full widget tree from `spec.md#6` exactly — `Placeholder` (WebBlockZone) widgets, never plain Containers; `Header` placeholder `EffectiveWidth = InlineBlock`. See `spec.md#6-layout-blocks-in-layouts-flow` and `spec.md#7-common-blocks-in-common-flow`.
3. **Screens, excluding UserProfile** (Login → RecoverPasswordRequest → RecoverPasswordReset → ChangePassword → InvalidPermissions). Build `LoginOnClick` and `LoginProviderOnClick` to the full spec in `spec.md#8`. TODO-defer only the two Batch-5 calls (`DoLogin`, `DoLogout`). All 5 screens: set layout block arguments explicitly; attach the `{App}` role.
4. **UserProfile screen, on its own.** Disproportionately complex (13 local vars, 10 screen actions, aggregate, countdown timer). See `spec.md#8-screens-in-common-flow` (UserProfile entry). Giving it a dedicated batch and validation pass prevents incomplete wiring from compounding.
5. **Server actions + client actions** (Authentication and UserActions folders). Wire all previously-stubbed screen logic from Batches 3 and 4. Do NOT create a `Check{App}Role`/`Has{App}Role` wrapper — use the platform-generated function directly. Do NOT add SendEmail nodes yet — templates don't exist until Batch 6. See `spec.md#9-server-actions` and `spec.md#10-client-actions`.
6. **Email templates + `RedirectToURL` external site + SendEmail node wiring.** Create `ResetPassword` and `ChangeEmail` templates. After both exist, wire SendEmail nodes via **natural language** (NOT `applyModelApiCode`): *"In the SendResetPasswordEmail server action, remove the Reminder node in the True branch and add a Send Email node wired to the ResetPassword template with: To = CustomerEmail, CustomerEmail = CustomerEmail, VerificationCode = StartResetPassword.StartResetPasswordResult.VerificationCode, ApplicationName = ApplicationName, CustomerName = TryGetNameByEmail.List.Current.User.Name. Repeat for SendChangeEmail → ChangeEmail template using StartUpdateEmail.StartUpdateEmailResult.VerificationCode."* See `spec.md#11-email-templates-in-emails-flow` and `spec.md#12-external-sites-in-common-flow`.
7. **`OnException` handler** per `spec.md#13-app-level-exception-handler` (4 handlers, correct messages, SecurityException branch). Register as both Common flow `OnExceptionHandler` AND app `GlobalExceptionHandler` (`UseDefaultThemeExceptionHandler = False`). Verify "No Exception Handling" warning is **gone** after this batch — if it persists, the wiring landed on the wrong scope.
8. **Wiring Closure & Validation Sweep** — see below. Never skip.

Prompt each batch with the exact names, types, and logic from the relevant spec.md section — Mentor performs worse on vague asks than on the literal spec.

## Mandatory wiring instruction (include in every batch 2–7 prompt)

> For every "X calls Y" / "OnClick triggers Z" / lifecycle-hook phrase in this spec, create an actual node connection — not just the action's internal logic. Every non-lifecycle action created in this batch must have at least one real caller by the end of this batch. A declared, unbound parameter produces the same "Unused Element" warning as an unwired action. Before ending the turn, check `GetValidationMessages` for "Unused Action"/"Unused Element"/"Unused Local Variable" warnings on anything created in this batch specifically, and wire or remove them now. Every named element created in this batch must have a non-empty Description — including all input/output parameters.

## Wiring Closure & Validation Sweep (Batch 8)

Always run as a final dedicated batch. Never treat "some warnings are expected" as a reason to skip.

1. `GetValidationMessages(true)` across the whole eSpace — list every remaining warning.
2. **Screen role audit:** Verify all 6 Common-flow screens have the `{App}` role — including the 4 anonymous ones. Add if missing. Do NOT remove from anonymous screens.
3. Run `python3 scripts/classify_validation.py classify --input <validation.json> --output classified.md` and report its output. See [`references/verification-checklist.md`](references/verification-checklist.md) for the full pass/fail criteria.
4. Report the classified list — what was wired, what's expected and why, what (if anything) was removed. "0 errors" ≠ "0 warnings."

## Post-Crash-Recovery Structural Check

See [`references/gotchas.md#post-crash-recovery-structural-check`](references/gotchas.md#post-crash-recovery-structural-check).

## Pre-Publish Structural Sanity Check

See [`references/gotchas.md#pre-publish-structural-sanity-check`](references/gotchas.md#pre-publish-structural-sanity-check) (includes `OS-DPL-42202` / `OS-BEW-CODE-40036` error-code lookup).

## Known Manual Steps Required After Skill Run

See [`references/gotchas.md#known-manual-steps-required-after-skill-run`](references/gotchas.md#known-manual-steps-required-after-skill-run).

## Key Patterns

- **`app_create` is a truly blank shell** — 0 screens/actions/themes, only an auto-generated role. This entire baseline is additive.
- **Role name conventionally matches the app name** — confirm before assuming.
- **Anonymous vs. authenticated:** `Login`, `RecoverPasswordRequest`, `RecoverPasswordReset`, `InvalidPermissions` = `AnonymousAccess = true`; `ChangePassword`, `UserProfile` = require login.
- **Client variables carry session UI state**, not business data.
- **No business logic here** — auth/theme/layout foundation only. Business entities/screens are `dbresults-odc-scaffold-entity`'s job.
- **MainFlow ships empty on purpose** — 0 screens, 0 blocks, 0 exception handler. Expected end state.
- **Default screen is NOT Login** — set `IsDefaultScreen = true` on the first MainFlow screen when it's added by a later skill.
- **Global exception handler is required** — both Common flow `OnExceptionHandler` and app `GlobalExceptionHandler` must point to `OnException`. See section 13.

## Verification Checklist

See [`references/verification-checklist.md`](references/verification-checklist.md).

## Related Skills

- **Run before:** `outsystems-spec-driven-build`, `outsystems-design-to-app`, `dbresults-odc-scaffold-entity`
- **Chain:** `app_create` → `dbresults-odc-new-app-baseline` → (`outsystems-spec-driven-build` | `outsystems-design-to-app`) → `dbresults-odc-scaffold-entity` (per entity) → `dbresults-odc-ship`
