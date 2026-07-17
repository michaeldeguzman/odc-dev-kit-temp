---
name: dbresults-odc-new-app-baseline
description: Use right after `app_create` mints a new ODC web app, BEFORE any business build (`outsystems-spec-driven-build`, `outsystems-design-to-app`, or `dbresults-odc-scaffold-entity`). `app_create`'s "blank" shell is genuinely empty — 0 screens, 0 actions, 0 themes, only 1 auto-generated role (verified empirically against a live tenant) — it does NOT include the standard authentication/theme/layout foundation every real ODC web app needs. This skill scaffolds that foundation: 3 UI flows, 2 themes, the app role, client variables, images, layout blocks, common blocks, 6 auth screens, server/client actions, and email templates. Use when asked to "set up a new app", "scaffold the app baseline", "add login/auth to this app", "this app has no login screen", or before starting any greenfield build.
---

# ODC New App Baseline — Authentication / Theme / Layout Scaffold

## Overview

`app_create` mints a genuinely blank shell. Verified against a live tenant
(`context_screens`/`context_actions`/`context_themes`/`context_roles` on a
fresh `app_create`-minted app returned **0 screens, 0 actions, 0 themes, 1
role**). Neither `outsystems-spec-driven-build` nor `outsystems-design-to-app`
builds this baseline — they assume an app shell exists and drive Mentor
straight to business screens/entities. Without this skill, a "new app" built
by either of those has no login, no password recovery, no user profile
screen, no app-specific theme, and no client-side session state.

This skill is **generic** — it applies to any new ODC web app, not a specific
one. `{App}` below is the target app's name (the reference pattern names the
theme and role after the app itself — e.g. an app called `Acme` gets an
`Acme` theme and an `Acme` role — but confirm the desired theme/role name
with the user rather than assuming). `{BrandColor}` is the brand hex color —
ask the user if not already known; do not invent one.

Run **once** per new app, right after `app_create`, before any business
build. Idempotent by design — the pre-flight check detects and skips layers
that already exist.

## When NOT to use

- **App already has a login screen / theme / role** — check pre-flight
  first; don't re-scaffold an app that already has this baseline.
- **Adding business entities/screens to an app that already has this
  baseline** — use `dbresults-odc-scaffold-entity` / `dbresults-odc-crud-wrapper`
  instead; this skill only covers the auth/theme/layout foundation, not
  business data.

## Pre-flight Check

1. Call `context_themes {app: "<app>"}` — if 2 themes already exist (an
   app theme extending `OutSystemsUI` + an email theme), the baseline is
   likely already scaffolded. Confirm with the user before re-running.
2. Call `context_screens {app: "<app>"}` — if a `Login` screen already
   exists, skip straight to whichever layers are actually missing rather
   than regenerating everything.
3. Call `context_roles {app: "<app>"}` — note the auto-generated role
   `app_create` already creates (named after the app). Decide with the
   user whether to reuse it as the baseline's single application role or
   create a differently-named one.
4. Ask the user for `{BrandColor}` (hex) if not provided.
5. Confirm the app's `kind` is a web app (`CrossDevice`/`WebApplication`) —
   this baseline is web-specific; a `Mobile` app shell needs a different
   (not-yet-covered) baseline.

## Layers to Scaffold

### 1. UI Flows

- **Common** — authentication screens, shared blocks, email templates
- **Layouts** — layout blocks used by all screens
- **Emails** — email templates (nested under Common in some tenants; ask
  if Mentor places it differently)

### 2. Themes

- **`{App}`** — app-specific theme, extends `OutSystemsUI`
  - Grid type: Fluid
  - Max width: 1280
  - Icon library: Phosphor2.0
  - Default layout: `LayoutTopMenu`
  - Default menu: `Menu`
  - Theme values: `PrimaryColor`, `SecondaryColor`, `AppPrimaryColor` — all
    set to `{BrandColor}`
- **`EmailTheme`** — separate theme used only by the email templates

### 3. Role

- **`{App}`** — the single application role. All authenticated screens
  require it. (Reuse the auto-generated role from `app_create` if the
  user agrees it's the right name; otherwise create the confirmed name.)

### 4. Client Variables

| Name | Type | Purpose |
|---|---|---|
| `LastURL` | Text | Last visited URL (post-login redirect) |
| `UserName` | Text | Logged-in user's display name |
| `UserPhotoURL` | Text | Logged-in user's photo URL |

### 5. Local Images

| Name | Purpose |
|---|---|
| `Logo` | App logo shown on login screen and header |
| `User` | Placeholder avatar for users without a photo |

### 6. Layout Blocks (in Layouts flow)

- **`LayoutBlank`** — single `Content` placeholder. Lifecycle:
  `OnInitialize` (calls `SetIconLibraryClass`), `OnReady` (calls
  `LayoutReady`, `SetLang`, `AddFavicon`), `OnDestroy` (calls
  `LayoutDestroy`). Parameters: `EnableAccessibilityFeatures` (Boolean),
  `ExtendedClass` (Text).
- **`LayoutTopMenu`** — placeholders: `Header`, `Breadcrumbs`, `Title`,
  `Actions`, `MainContent`, `Footer`. Embeds `MenuIcon`,
  `ApplicationTitle`, `Menu` blocks in the header. Lifecycle: same as
  `LayoutBlank` plus a `SkipToContentOnClick` screen action. Parameters:
  `HasFixedHeader` (Boolean, default True), `EnableAccessibilityFeatures`,
  `ExtendedClass`.
- **`LayoutSideMenu`** — same placeholders as `LayoutTopMenu` plus a
  `Navigation` placeholder in an `<aside>` element. Parameters:
  `HasFixedHeader`, `MenuBehavior` (`SideMenuBehavior` identifier),
  `EnableAccessibilityFeatures`, `ExtendedClass`. Same lifecycle as
  `LayoutTopMenu`.
- **`LayoutBase` / `LayoutBaseSection`** — utility layouts for fully
  custom page structures.

### 7. Common Blocks (in Common flow)

- **`ApplicationTitle`** — displays app logo + app name (via
  `GetAppName()`). `ApplicationNameOnClick` screen action redirects to
  `GetOwnerURLPath()`.
- **`MenuIcon`** — clickable hamburger icon to open/close the side menu
  on small screens.
- **`Menu`** — navigation block with a `PageLinks` container (menu item
  links) and a `LoginInfo` container (embeds `UserInfo`). Parameters:
  `ActiveItem` (Integer, default -1), `ActiveSubItem` (Integer, default
  -1). Lifecycle: `OnReady` (calls `MenuReady`, `SetActiveMenuItems`),
  `OnParametersChanged` (calls `SetMenuListeners`), `OnDestroy` (calls
  `MenuDestroy`). `HideMenu` screen action calls `ToggleSideMenu`.
- **`UserInfo`** — shows logged-in user avatar + name (link to
  `UserProfile`) + logout icon; shows a login link if not logged in.
  `ClientLogout` screen action calls `DoLogout` then redirects.
  `GetUsernameAndPhoto` screen action calls `GetUserProfile`, assigns
  `Client.UserName` and `Client.UserPhotoURL`. `OnReady` calls
  `GetUsernameAndPhoto`.

### 8. Screens (in Common flow)

All screens require the `{App}` role except where noted `AnonymousAccess = true`.

- **`Login`** — `AnonymousAccess = true`, layout `LayoutBlank`. Local
  vars: `UserEmail`, `Password`, `IsPasswordVisible`,
  `ShowBuiltInProvider`, `ShowExternalProvider`, `IsBuiltInExecuting`,
  `ExecutingIndex`, `ExternalIdentityProviders`. Screen actions:
  `OnInitialize` (redirect if already logged in; load provider status +
  external providers list), `LoginOnClick` (validate form, call
  `DoLogin`, check `{App}` role, redirect or show error),
  `LoginProviderOnClick(ProviderIndex, ProviderKey)` (call
  `GetExternalLoginURL`, redirect), `OnTogglePasswordVisibility` (toggle
  `IsPasswordVisible`, call `ShowPassword`). UI: email input, password
  input with show/hide toggle, "Forgot password?" link, login button
  (`ButtonLoading`), separator, external provider buttons list.
- **`RecoverPasswordRequest`** — `AnonymousAccess = true`, layout
  `LayoutBlank`. Local vars: `IsExecuting`, `Email`. Screen action
  `ResetPasswordOnClick` — validate form, call `SendResetPasswordEmail`
  client action, navigate to `RecoverPasswordReset`. UI: email input,
  "Reset password" button, "Go to login" link.
- **`RecoverPasswordReset`** — `AnonymousAccess = true`, layout
  `LayoutBlank`. Input parameters: `Email`, `VerificationCode` (Text).
  Handles step 2 of password reset: verification code + new password,
  calls `FinishResetPassword`.
- **`ChangePassword`** — requires login, layout `LayoutBlank`. Lets
  logged-in users change their password via the `ChangePassword` system
  client action.
- **`InvalidPermissions`** — `AnonymousAccess = true`, layout
  `LayoutBlank`. Shown when a user lacks the required role.
- **`UserProfile`** — requires login, layout `LayoutTopMenu`. Screen
  aggregate `GetUserDetails` (queries `User` filtered by `GetUserId()`).
  Local vars: `OldName`, `OldEmail`, `OldPhotoURL`, `IsExternal`,
  `VerificationCode`, `ShowVerificationCode`, `ShowGetCodeButton`,
  `CountdownValue`, `TimerIntervalHandle`, `IsButtonEnabled`,
  `IntervalDuration`, `IsExecuting`, `IsExecuting_GetCode`. Screen
  actions: `OnInitialize`, `GetUserDetailsOnAfterFetch`,
  `ValidateUserDetails`, `ValidateInputsOnChange`,
  `CheckIsButtonEnabled`, `SaveChangesOnClick`, `SendVerificationCode`,
  `UpdateCountdown`, `StopCountdown`, `OnDestroy`. UI: profile photo,
  name input, photo URL input, email input, verification-code flow (get
  code → code input + resend countdown), save button.

### 9. Server Actions (folder: Authentication)

- **`SendResetPasswordEmail(ApplicationName: Text, CustomerEmail: Email)`**
  → `Success: Boolean` — calls system action `StartResetPassword`; on
  success, queries user name and sends the `ResetPassword` email.
- **`SendChangeEmail(ApplicationName: Text, CustomerEmail: Email)`** →
  `Success: Boolean` — calls system action `StartUpdateEmail`, sends the
  `ChangeEmail` email with a verification code.
- **`UpdateUser(UserUpdateInfo: UserUpdateInfo)`** →
  `UpdateUserResult: UpdateUserResult` — wraps the system server action
  `UpdateUserProfile`.

### 10. Client Actions (folder: Authentication)

- **`DoLogin(Username: Text, Password: Text)`** → `Success: Boolean`,
  `ErrorMessage: Text` — calls system action `Login`, maps failure
  reasons to human-readable messages.
- **`DoLogout()`** → `RedirectURL: Text` — checks external user →
  `GetExternalLogoutURL` or `Logout`; clears `Client.UserName`,
  `Client.UserPhotoURL`, `Client.LastURL`.
- **`SendResetPasswordEmail(CustomerEmail: Email)`** → `Success: Boolean`
  — calls the server action of the same name with `GetAppName()`.
- **`SendChangeEmail(CustomerEmail: Email)`** → `Success: Boolean` —
  calls the server action of the same name with `GetAppName()`.
- **`UpdateUser(UserUpdateInfo: UserUpdateInfo)`** →
  `UpdateUserResult: UpdateUserResult` — calls the server action.

### 11. Email Templates (in Emails flow)

- **`ResetPassword`** — input params `CustomerEmail`, `VerificationCode`,
  `ApplicationName`, `CustomerName`. Theme: `EmailTheme`. Content:
  password reset instructions with the verification code.
- **`ChangeEmail`** — input params `CustomerEmail`, `VerificationCode`,
  `ApplicationName`, `CustomerName`. Theme: `EmailTheme`. Content: email
  change verification instructions.

### 12. External Sites (in Common flow)

- **`RedirectToURL`** — client-side URL redirect, used throughout the
  app. Input parameter: `URL` (Text).

## Required References

This baseline depends on assets outside the app itself — confirm they're
referenced (not rebuilt):

- **`OutSystemsUI`** — theme, layout blocks, UI patterns, and utility
  client actions (`LayoutReady`, `MenuReady`, `FeedbackMessageShow`,
  `SetIconLibraryClass`, etc.)
- **`(System)`** — system entity `User`; system server actions
  `StartResetPassword`, `StartUpdateEmail`, `UpdateUserProfile`; system
  client actions `Login`, `Logout`, `GetUserProfile`,
  `IsBuiltinIdentityProviderActive`, `GetExternalIdentityProviders`,
  `GetExternalLoginURL`, `GetExternalLogoutURL`, `FinishResetPassword`,
  `FinishUpdateEmail`, `IsExternalUser`

## Mentor Prompt Strategy

Don't fire this as one giant Mentor call — batch it, same reasoning as
`dbresults-odc-scaffold-entity`: smaller batches isolate failures faster,
and this baseline is large (12 sub-layers). Suggested batching, each a
separate `mentor_start`/resumed-session turn, confirmed working before
moving to the next:

1. **Flows + theme + role + client variables + images** — structural
   scaffolding with no logic yet.
2. **Layout blocks + common blocks** — the shared UI chrome.
3. **Screens** (Login → RecoverPasswordRequest → RecoverPasswordReset →
   ChangePassword → InvalidPermissions → UserProfile).
4. **Server actions + client actions** (Authentication folder).
5. **Email templates + external site**.

Prompt each batch with the exact names, types, and logic from the
relevant section above — Mentor performs worse on vague asks
("add a login flow") than on the literal spec.

## Key Patterns

- **`app_create` is a truly blank shell** — 0 screens/actions/themes,
  only an auto-generated role. This entire baseline is additive scaffold
  work, not something to assume already exists.
- **Role name conventionally matches the app name** in the reference
  pattern (`{App}` theme + `{App}` role) — but this is a naming
  convention, not a platform requirement; confirm before assuming.
- **Anonymous vs. authenticated screens** — `Login`,
  `RecoverPasswordRequest`, `RecoverPasswordReset`, `InvalidPermissions`
  are `AnonymousAccess = true`; `ChangePassword` and `UserProfile`
  require login.
- **Client variables carry session UI state**, not business data —
  don't conflate with entity-level session helpers like
  `Session_GetNormalizedSessionUserId` from `dbresults-odc-crud-wrapper`.
- **No business logic here** — this skill only produces the
  authentication/theme/layout foundation. Business entities/screens are
  `dbresults-odc-scaffold-entity`'s job, run afterward.

## Verification Checklist

After each Mentor batch, confirm via the matching context tool:

- [ ] `context_themes`: 2 themes exist (`{App}` extending `OutSystemsUI`,
      `EmailTheme`)
- [ ] `context_roles`: the confirmed application role exists
- [ ] `context_screens`: 6 screens exist with correct
      `AnonymousAccess` flags and layouts
- [ ] `context_actions`: 3 server actions + 5 client actions exist in an
      `Authentication` folder
- [ ] Layout blocks and common blocks aren't directly enumerable via
      `context_actions`/`context_screens` in all tenants — if they don't
      surface there, confirm via Mentor's own OML inspection or Service
      Studio instead of assuming absence
- [ ] Email templates exist under the Emails flow, themed with
      `EmailTheme`
- [ ] `RedirectToURL` external site exists
- [ ] 0 errors in validation after each batch before moving to the next

## Related Skills

- **Run before:** `outsystems-spec-driven-build`, `outsystems-design-to-app`
  — both assume an app shell exists; this skill makes that shell a real
  usable app first.
- **Run before:** `dbresults-odc-scaffold-entity` / `dbresults-odc-crud-wrapper`
  — business entities layer on top of this foundation, not instead of it.
- **Chain:** `app_create` → `dbresults-odc-new-app-baseline` →
  (`outsystems-spec-driven-build` | `outsystems-design-to-app`) →
  `dbresults-odc-scaffold-entity` (per entity) → `dbresults-odc-ship`.
