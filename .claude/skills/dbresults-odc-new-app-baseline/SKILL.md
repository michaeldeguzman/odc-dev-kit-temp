---
name: dbresults-odc-new-app-baseline
description: Use right after `app_create` mints a new ODC web app, BEFORE any business build (`outsystems-spec-driven-build`, `outsystems-design-to-app`, or `dbresults-odc-scaffold-entity`). `app_create`'s "blank" shell is genuinely empty — 0 screens, 0 actions, 0 themes, only 1 auto-generated role (verified empirically against a live tenant) — it does NOT include the standard authentication/theme/layout foundation every real ODC web app needs. This skill scaffolds that foundation: 3 UI flows (Common, Layouts, Emails — plus an intentionally empty MainFlow), 2 themes, the app role, client variables, images, layout blocks, common blocks, 6 auth screens, server/client actions, email templates, and the app-wide OnException handler. Use when asked to "set up a new app", "scaffold the app baseline", "add login/auth to this app", "this app has no login screen", "add a global exception handler", "set up OnException", or before starting any greenfield build.
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
6. **Check `OutSystemsUI` reference version compatibility — and don't
   trust a proxy signal for it.** The `Phosphor2.0` icon library (step 2
   below) requires `OutSystemsUI` version **2.28.0 or later**. A prior
   run tried to confirm this indirectly — checking whether `Phosphor2.0`
   was *accepted* as a valid `IconLibrary` string value — and concluded
   compatibility was fine. It wasn't: the "Icon library compatibility"
   warning still showed up in that app's final warning report. Accepting
   the string is not proof of version compatibility; the enum can list a
   value as syntactically valid across versions independent of whether
   the referenced revision actually contains the feature. Instead: have
   Mentor read the `OutSystemsUI` reference's actual version/revision
   fields directly (same fields used for the `(System)` reference health
   check below — `Revision`, `Version`, `Hash`, `IsFixedVersion`). If a
   definitive version number isn't obtainable via the Model API, default
   to refreshing/bumping the reference to the latest available revision
   in the tenant first (same pattern as "Refreshing a stale `(System)`
   reference" under Model API Patterns), regardless of what the enum
   check suggested — then set `IconLibrary: Phosphor2.0`. If no
   compatible version is available even after refreshing, fall back to
   the default icon library and flag this to the user rather than
   setting Phosphor2.0 anyway. After Batch 1, explicitly re-check
   `GetValidationMessages` for "Icon library compatibility" before moving
   on — don't assume the pre-flight check was sufficient without
   confirming the warning is actually gone.
   **Confirmed live-run finding:** the Model API sandbox cannot reliably
   read the OutSystemsUI reference's true semantic version — a run
   against a real tenant saw a non-empty `Revision` but empty
   `Version`/`Hash` fields, and the "Icon library compatibility" warning
   survived all 8 batches even though `Phosphor2.0` was accepted without
   error. The reliable check lives outside the Model API: open ODC
   Portal (or ODC Studio's dependency panel) and read the OutSystemsUI
   version shown there directly. If it's below 2.28.0, request a
   tenant-level OutSystemsUI dependency upgrade before publishing this
   app — don't just carry the warning forward hoping it resolves itself
   at publish time, and don't rely on the Model API's enum-acceptance
   check as if it were a version check.
7. **Check the `(System)` reference's health before touching anything.**
   Have Mentor read the reference's `Hash` field. A prior run had this
   sitting at an all-zero hash (`00000000-0000-0000-0000-000000000000`)
   from the start — invisible to `GetValidationMessages`, but a guaranteed
   `OS-BEW-CODE-40036` build failure later ("uses entity 'User' that is
   incompatible with its definition in reference '(System)'"). If the hash
   is zero or the reference otherwise looks stale, fix it now (see
   "Refreshing a stale `(System)` reference" under Model API Patterns)
   before Batch 1 — cheaper to catch here than after 8 batches of work.
8. **Do not hardcode assumed `User` entity attribute names.** The skill's
   `UserProfile` spec (section 8) refers to attributes like `Name`,
   `Email`, `PhotoURL`, `IsActive`. A prior run discovered the tenant's
   live `User` entity had actually drifted from this shape (`IsActive`,
   `Phone`, `ExternalId` were gone; `PhotoUrl` — different casing — had
   been added instead). Before writing any expression that reads a `User`
   attribute (Batches 3–5), have Mentor query the *live* attribute list
   from the `(System)` reference and use exactly those names/casing —
   never assume the spec's attribute names are still accurate for this
   tenant.

## Layers to Scaffold

### 1. UI Flows

- **Common** — authentication screens, shared blocks, email templates, the
  app-wide `OnException` handler
- **Layouts** — layout blocks used by all screens
- **Emails** — email templates (nested under Common in some tenants; ask
  if Mentor places it differently)
- **MainFlow** — intentionally **empty** on a fresh scaffold: no screens,
  no blocks, no exception handler. This is where the app's own business
  screens go later (`dbresults-odc-scaffold-entity` or the spec/design
  build skills add to it) — don't add anything here as part of this
  baseline, and don't treat an empty MainFlow as a sign the scaffold is
  incomplete.

### 2. Themes

- **`{App}`** — app-specific theme, extends `OutSystemsUI`
  - Grid type: Fluid
  - Max width: 1280
  - Icon library: Phosphor2.0
  - Default layout: `LayoutTopMenu`
  - Default menu: `Menu`
  - Theme values: `PrimaryColor`, `SecondaryColor`, `AppPrimaryColor` — all
    set to `{BrandColor}`
- **`EmailTheme`** — separate theme used only by the email templates. Apply
  the CSS in [`assets/EmailTheme.css`](assets/EmailTheme.css) as this
  theme's stylesheet (table/list-item widget styles for email-safe
  layouts) — don't leave it as a bare theme with no styles, and don't
  hand-author the CSS from scratch each run.
  **Do NOT extend `OutSystemsUI`** — unlike `{App}`, `EmailTheme` should
  be a standalone/root theme. A prior run created `EmailTheme` as an
  `OutSystemsUI`-derived theme (matching the pattern used for `{App}`),
  which inherits the entire framework CSS bundle and triggers a
  "UI Flow 'Emails' is using a theme that is larger than 14KB" warning
  regardless of how minimal the email-specific CSS is — extending
  `OutSystemsUI` is the actual root cause, not the custom CSS size. Also
  explicitly set the `Emails` **flow's own** `Theme` property to
  `EmailTheme` (a flow-level setting, distinct from each individual email
  template's own `Theme` property in section 11) — a prior run set each
  template's `Theme` correctly but left the flow-level theme on the
  default, and the size warning's `ownerPath` points at the flow
  (`/Emails`, `ownerType: WebFlow`), not at either template.

### 3. Role & App Identity

- **`{App}`** — the single application role. All authenticated screens
  require it. (Reuse the auto-generated role from `app_create` if the
  user agrees it's the right name; otherwise create the confirmed name.)
- **Set `eSpace.IsUserProvider = true`.** This baseline gives the app its
  own full Login/ChangePassword/UserProfile flow against the `(System)`
  `User` entity — it is self-contained, so it should explicitly declare
  itself a User Provider rather than implicitly self-referencing.
  `IsUserProvider` is a genuine, directly-settable Model API property on
  the eSpace (confirmed live: `eSpace.IsUserProvider` reads/writes as a
  plain boolean) — this is the correct, supported fix for the
  `ImplicitSelfUserProvider` performance warning ("Apps that are not set
  as 'Is User Provider' should have a User Provider specified different
  than (Current eSpace)").
  **Do not** attempt to resolve this warning by writing hidden/undocumented
  eSpace metadata keys (e.g. a reflection-discovered `UserProviderESpaceName`
  key) — a prior session went down exactly that path via trial-and-error
  reflection against the Model API, produced no real fix, and risked
  leaving the OML in a bad state. Setting `IsUserProvider = true` directly
  is the whole fix; nothing else is needed.

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

**Use a 1×1 transparent GIF for both placeholders, not a hand-crafted PNG.**
A prior run generated PNG bytes by hand (IHDR/IDAT chunks with manually
computed CRC32 checksums); the Model API's code sandbox disallows `for`
loops and local functions, so a correct CRC32 couldn't even be computed to
verify the bytes, and the malformed-PNG theory ate significant investigation
time chasing a red herring (it turned out not to be the actual build
failure, but it was a real risk and an unforced complexity). GIF89a has no
checksums to get wrong — it's pure length-prefixed blocks — so a 1×1
transparent GIF (~43 bytes) is both simpler to hand-construct correctly and
impossible to get subtly wrong the way a PNG CRC can be.

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

**Every parameter above must be bound to a real widget property on the
block's own root/wrapper container — not just declared and left for a
future screen to pass a value into.** A prior run left `ExtendedClass`,
`EnableAccessibilityFeatures`, `HasFixedHeader`, and `MenuBehavior` all
declared-but-unread inside their own blocks — this is the exact same
"declared but never consumed" defect as an unwired action, just applied
to an input parameter instead of a screen action. Concretely:

- `ExtendedClass` (all three blocks) — bind into the root container's own
  `ExtendedClass`/CSS-class expression, e.g.
  `"layout-blank " + ExtendedClass` (adjust the base class name per
  block). This is a real, permanent binding — it doesn't need any future
  screen to exist first.
- `EnableAccessibilityFeatures` (all three blocks) — bind into the same
  root container's class expression conditionally, e.g.
  `If(EnableAccessibilityFeatures, " a11y-enabled", "")` appended to the
  `ExtendedClass` expression above.
- `HasFixedHeader` (`LayoutTopMenu`, `LayoutSideMenu`) — bind into the
  `Header` placeholder's own container class expression, e.g.
  `If(HasFixedHeader, "fixed-header", "")`.
- `MenuBehavior` (`LayoutSideMenu` only) — bind into the `Navigation`
  placeholder's `<aside>` container class expression (or a data
  attribute consumed by the side-menu JS behavior), e.g.
  `"side-menu-" + MenuBehavior`.

Wire all four bindings while building each block in Batch 2 — this
requires zero business screens or menu items to exist first, unlike
`Menu.ActiveItem`/`ActiveSubItem` below, so there's no reason to defer it.

**Separately — and distinct from the block-definition wiring above —
every screen that places one of these layout blocks must explicitly set
ALL of that block's input parameter arguments on the instance, even
though none are marked `Mandatory`.** A live run found that leaving a
`LayoutTopMenu` argument completely blank on a screen (no expression at
all — not even `False`/`""`) raises a validation error at publish time:
the platform treats a merely-optional block parameter as if it were
required the moment a screen actually instantiates the block, regardless
of the block's own declared default value. This is not limited to this
baseline's own screens — it applies to **any** screen that later places
`LayoutTopMenu`/`LayoutSideMenu`/`LayoutBlank` as its layout, including
business screens added afterward by `dbresults-odc-scaffold-entity` or a
spec/design build. Required values for every `LayoutTopMenu` instance:

| Parameter | Value to set on every screen instance |
|---|---|
| `HasFixedHeader` | `True` |
| `EnableAccessibilityFeatures` | `False` |
| `ExtendedClass` | `""` |

The same rule applies to `LayoutBlank`'s `EnableAccessibilityFeatures`
(`False`) / `ExtendedClass` (`""`), and to `LayoutSideMenu`'s
`HasFixedHeader` (`True`) / `EnableAccessibilityFeatures` (`False`) /
`ExtendedClass` (`""`) / `MenuBehavior` (an explicit value — `""` if the
tenant has no specific side-menu behavior configured). Never leave a
layout-block argument blank on a screen just because the parameter isn't
`Mandatory` — set it explicitly, every time, on every screen instance.

### 7. Common Blocks (in Common flow)

- **`ApplicationTitle`** — displays app logo + app name (via
  `GetAppName()`). `ApplicationNameOnClick` screen action redirects to
  `GetOwnerURLPath()`.
- **`MenuIcon`** — clickable hamburger icon to open/close the side menu
  on small screens.
- **`Menu`** — navigation block with a `PageLinks` container (menu item
  links) and a `LoginInfo` container (embeds `UserInfo`). Lifecycle:
  `OnReady` (calls `MenuReady`, `SetActiveMenuItems`), `OnParametersChanged`
  (calls `SetMenuListeners`), `OnDestroy` (calls `MenuDestroy`).
  `HideMenu` screen action calls `ToggleSideMenu`. **Do not add
  `ActiveItem`/`ActiveSubItem` parameters at baseline stage** — unlike the
  layout parameters above, these have no real container to bind to yet
  (`PageLinks` has zero items until real navigation links exist, and
  `MainFlow` is intentionally empty — see Key Patterns), so declaring them
  now only produces an unfixable "Unused Element" warning that sits there
  until business screens exist. Add them later, at the same time real
  menu item links are added to `PageLinks` (`dbresults-odc-scaffold-entity`
  or a spec/design build), when there's finally something to bind them to.
- **`UserInfo`** — shows logged-in user avatar + name (link to
  `UserProfile`) + logout icon; shows a login link if not logged in.
  `ClientLogout` screen action calls `DoLogout` then redirects.
  `GetUsernameAndPhoto` screen action calls `GetUserProfile`, assigns
  `Client.UserName` and `Client.UserPhotoURL`. `OnReady` calls
  `GetUsernameAndPhoto`.

### 8. Screens (in Common flow)

All screens require the `{App}` role except where noted `AnonymousAccess = true`.
**Every screen below must explicitly set all of its layout block's input
parameters** (see the call-site rule under section 6) — don't leave
`HasFixedHeader`/`EnableAccessibilityFeatures`/`ExtendedClass`/
`MenuBehavior` blank on any screen's layout instance just because the
screen spec below doesn't repeat the values inline.

- **`Login`** — `AnonymousAccess = true`, layout `LayoutBlank`. Local
  vars: `UserEmail`, `Password`, `IsPasswordVisible`,
  `ShowBuiltInProvider`, `ShowExternalProvider`, `IsBuiltInExecuting`,
  `ExecutingIndex` (Integer, default `-1` — not `0`, since `0` is a valid
  list index), `ExternalIdentityProviders`. Screen actions:
  `OnInitialize` (redirect if already logged in; load provider status +
  external providers list), `LoginOnClick`, `LoginProviderOnClick`,
  `OnTogglePasswordVisibility` (toggle `IsPasswordVisible`, call
  `ShowPassword`). UI: email input, password input with show/hide
  toggle, "Forgot password?" link, login button (`ButtonLoading`),
  separator, external provider buttons list.

  **`LoginOnClick`** — the full flow (a prior run implemented only a
  thin version of this — validate, call `DoLogin`, redirect/error — and
  skipped the executing-state management and the role check entirely,
  which is what left `IsBuiltInExecuting` looking unused):
  1. Set `IsBuiltInExecuting = True` (disables inputs, shows the login
     button's loading state).
  2. Validate the form (e.g. `LoginForm.Valid`). If invalid: set
     `IsBuiltInExecuting = False` and end — do not attempt a login. If
     valid: clear any previous feedback message and proceed.
  3. Call `DoLogin`, passing `UserEmail` as username and `Password`.
  4. Call a role-membership check for the `{App}` role — either the
     role's own generated boolean check function (custom Roles are
     directly callable as expressions, e.g. `{App}()`) or a thin wrapper
     client action around it (a live run named this `CheckNewAppRole`,
     but the name should match the app's actual role per the `{App}`
     convention — confirm the real generated function/action name with
     Mentor rather than assuming this exact name).
  5. Branch on the result:
     - `DoLogin` failed → clear `Password`, set
       `IsBuiltInExecuting = False`, show `DoLogin`'s own error message.
     - `DoLogin` succeeded but the role check fails → clear `Password`,
       set `IsBuiltInExecuting = False`, show a "No permissions." error,
       then call `DoLogout` — an authenticated-but-unauthorized session
       must not be left standing.
     - `DoLogin` succeeded and the role check passes → redirect to
       `Client.LastURL` (or the app root if empty), with a fade
       transition.
  6. Exception handler on the whole action — clear `Password`, set
     `IsBuiltInExecuting = False`, show the exception message as an
     error. (This is in addition to, not instead of, the branch-level
     error handling in step 5.)

  **`LoginProviderOnClick(ProviderIndex: Integer, ProviderKey: Text)`**:
  1. Assign `ExecutingIndex = ProviderIndex` — this one assignment is
     what makes `ProviderIndex` a real, consumed input parameter. **A
     prior run's validation still flagged `ProviderIndex` as "Unused
     Element" even after this exact assignment was wired** — this is a
     known false positive in the scaffolding tool's unused-parameter
     check, not a sign the wiring is actually missing. Confirm the
     assignment exists in the action's logic (don't just trust the
     absence of the warning, and don't waste a batch trying to silence
     a false positive that can't be silenced).
  2. Call system action `GetExternalLoginURL`, passing `ProviderKey`.
  3. Redirect to the returned URL.
  4. Exception handler — reset both `IsBuiltInExecuting = False` and
     `ExecutingIndex = -1`, show the exception message as an error.

  **Cross-wiring `IsBuiltInExecuting` and `ExecutingIndex` — this is the
  actual reason both variables exist, and it's why they read as unused
  if only bound one-directionally:** they gate the loading/disabled
  state of *every* login button on the screen together, not just their
  own button:
  - The built-in login button's `Enabled`/`ButtonLoading` expression
    should reference `Not(IsBuiltInExecuting) And ExecutingIndex = -1`
    (or equivalent) — it disables while EITHER the built-in login OR any
    external provider login is executing.
  - Each external-provider list item's `Enabled` expression should
    likewise reference `Not(IsBuiltInExecuting) And ExecutingIndex = -1`,
    and its own loading-spinner expression should be
    `ExecutingIndex = <that list's own item-index expression>` so only
    the clicked button shows as loading, not all of them.
  Wiring only the "obvious" half (e.g. just the clicked button's own
  spinner) leaves the other bindings — and often the variables
  themselves — looking unused to the validator.

  **Batch sequencing note:** `DoLogin` and `DoLogout` are Batch-5
  actions, so in Batch 3 those two specific calls are the ones that get
  the standard TODO-comment deferral (see "Avoiding stub-naming
  collisions across batches"). The `{App}` role-membership check is
  NOT a Batch-5 dependency — the role itself already exists from Batch 1
  — so wire that branch for real in Batch 3; don't defer it just because
  it sits in the same action as two calls that must be deferred.
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
- **`UserProfile`** — requires login, layout `LayoutTopMenu` with
  `HasFixedHeader = True`, `EnableAccessibilityFeatures = False`,
  `ExtendedClass = ""` explicitly set on the instance (see section 6 —
  this is the screen a live run's `LayoutTopMenu` publish-time error was
  actually found on). Screen
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
- **`Check{App}Role()`** → `HasRole: Boolean` — thin wrapper around the
  `{App}` role's own generated boolean check function (custom Roles are
  directly callable as expressions, e.g. `{App}()` returns whether the
  current user holds it). Used by `Login.LoginOnClick` (section 8) right
  after a successful `DoLogin` to decide between redirecting home and
  showing "No permissions." + `DoLogout`. This does not depend on any
  other Batch-5 action and has no `(System)`/external dependency, so it
  can be created and wired in this batch even though the rest of
  `LoginOnClick`'s role-check branch was already wired for real back in
  Batch 3 (the role itself exists from Batch 1) — just confirm this
  action exists by the time Batch 5 wires `DoLogin`/`DoLogout` into the
  same screen action.

### 11. Email Templates (in Emails flow)

- **`ResetPassword`** — input params `CustomerEmail`, `VerificationCode`,
  `ApplicationName`, `CustomerName`. Theme: `EmailTheme`. Content:
  password reset instructions with the verification code.
- **`ChangeEmail`** — input params `CustomerEmail`, `VerificationCode`,
  `ApplicationName`, `CustomerName`. Theme: `EmailTheme`. Content: email
  change verification instructions.

Setting each template's own `Theme` to `EmailTheme` is necessary but not
sufficient — also confirm the `Emails` flow's own `Theme` property is
`EmailTheme` (see section 2's `EmailTheme` note); the "theme larger than
14KB" validation warning is keyed to the flow-level theme, not the
per-template one.

### 12. External Sites (in Common flow)

- **`RedirectToURL`** — client-side URL redirect, used throughout the
  app. Input parameter: `URL` (Text).

### 13. OnException Handler (in Common flow)

The app-wide exception handler — set as the app's exception flow/action,
lives in Common. Four branches, each its own `ExceptionHandler` node:

- **Security Exception** (`AbortTransaction: true`, `LogError: false`) —
  checks `GetUserId() <> NullTextIdentifier()`:
  - Logged in → redirect to `InvalidPermissions`
  - Not logged in → save current URL to `Client.LastURL` (via
    `GetBookmarkableURL()`), then redirect to `Login`
- **Database Exception** (`AbortTransaction: true`, `LogError: true`) —
  show error message *"There was a problem with the database request.
  Please contact the administrator"*, then `End`
- **Communication Exception** (`AbortTransaction: true`, `LogError: true`)
  — show error message *"There was a problem communicating with the
  server. Please try again or contact your administrator"*, then `End`.
  Comment on this branch: fires on no internet connection or server
  timeout.
- **All Exceptions** (catch-all, `AbortTransaction: true`, `LogError:
  true`) — show generic error message *"There was a problem. Please
  contact the administrator"*, then `End`

Order matters: the specific handlers (Security, Database, Communication)
must be checked before the All Exceptions catch-all — a catch-all placed
first would swallow the specific branches before they ever fire.

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

## Model API Patterns (confirmed, don't re-discover these)

These were each found via costly trial-and-error in prior runs — Mentor
burned several minutes rediscovering each one from scratch. Feed them to
Mentor up front (or as targeted troubleshooting hints) instead of letting
it re-explore the API blind.

- **Folders are scoped by tree type, not just name.** A folder created via
  `CreateFolder(ESpaceTreeFolder.ServerActions, "Authentication")` and one
  created via `CreateFolder(ESpaceTreeFolder.ClientActions, "Authentication")`
  are two *different* folder objects that happen to share a display name —
  the API allows this silently. Creating both (e.g. once per action type)
  is correct and expected; the bug is creating a *second* one of the
  *same* scope by accident (see "Post-crash-recovery structural check"
  below) — that's the one that breaks the build.
- **The reactive/mobile SendEmail node is a distinct type from the legacy
  one.** Use `OutSystems.Model.Logic.Mobile.Nodes.ISendEmailNode` (has an
  `Email` reference property) inside server actions for ODC reactive
  apps — not `OutSystems.Model.Logic.Nodes.ISendEmailNode` (the legacy
  traditional-web type, no usable `Email` property in this context).
- **The Model API's code sandbox disallows `for`/`foreach`-with-mutation
  loops, local functions, and sized array creation** (`new Type[]{...}`
  is fine; `new Type[256]` is not). Don't attempt anything requiring a
  hand-rolled algorithm (checksum computation, byte-manipulation loops) —
  restructure the approach instead (see the GIF-over-PNG guidance above).
- **Refreshing a stale `(System)` reference is NOT the same as re-reading
  its attributes.** Calling something like
  `eSpace.References.Named("(System)")` and printing its entities'
  attribute names does not update the reference — it was silently a
  no-op fix in a prior run and the same build error recurred immediately.
  What actually works: re-adding the dependency via `add_references_to_elements`
  (pointing at the current tenant's `System_`/`(System)` asset), or calling
  `eSpace.RefreshDependency(globalKey, updateSpecificVersion: true)` on the
  entity's own global key (not the reference's `ModuleKey`, which is an
  `IKey` and won't satisfy the `IGlobalKey` parameter type). Confirm the
  fix landed by checking the entity's attribute list actually changed
  (schema drift, if any, will show up here) — not just that the call
  didn't throw.
- **A non-`Mandatory` block input parameter still errors at publish time
  if its argument is left completely blank on a screen instance.** This
  was confirmed live on `LayoutTopMenu`: `HasFixedHeader`,
  `EnableAccessibilityFeatures`, and `ExtendedClass` are all declared
  `Mandatory = False` with defaults, yet a screen that places
  `LayoutTopMenu` and leaves any one of the three arguments as no
  expression at all (not `False`, not `""` — genuinely blank) fails
  validation. `Mandatory = False` only means the platform won't force a
  value when editing the block's own definition; it does NOT mean a
  screen can skip supplying an argument when placing an instance of the
  block. Always set every layout-block parameter argument explicitly on
  every screen instance (see section 6 for the exact required values) —
  never rely on the block's own default silently applying at the call
  site.

## Mentor Prompt Strategy

Don't fire this as one giant Mentor call — batch it, same reasoning as
`dbresults-odc-scaffold-entity`: smaller batches isolate failures faster,
and this baseline is large (13 sub-layers). Suggested batching, each a
separate `mentor_start`/resumed-session turn, confirmed working before
moving to the next:

1. **Flows + theme + role + `IsUserProvider` + client variables + images**
   — structural scaffolding with no logic yet. Includes creating the
   empty `MainFlow` (no screens/blocks/handler needed — just the flow
   itself). When creating `EmailTheme`, paste the contents of
   `assets/EmailTheme.css` in this skill's folder into its stylesheet
   verbatim — don't summarize or re-derive it. Create `EmailTheme` as a
   standalone theme (do NOT extend `OutSystemsUI` the way `{App}` does —
   see section 2), and set the `Emails` flow's own `Theme` property to
   `EmailTheme` right away in this batch, not deferred to Batch 6.
2. **Layout blocks + common blocks** — the shared UI chrome.
3. **Screens, excluding UserProfile** (Login → RecoverPasswordRequest →
   RecoverPasswordReset → ChangePassword → InvalidPermissions). Build
   `LoginOnClick`/`LoginProviderOnClick` to the full flow in section 8 —
   executing-state management, form validation, the `{App}` role check
   (wire this for real; it's not a Batch-5 dependency), and the
   cross-wired `Enabled`/loading-state bindings on both button types —
   TODO-deferring only the two actual Batch-5 calls (`DoLogin`,
   `DoLogout`). Don't ship the thin version (validate → call → redirect)
   and don't let `IsBuiltInExecuting`/`ExecutingIndex`/`ProviderIndex`
   slip into the "expected-unused" bucket. Every one of these 5 screens
   uses `LayoutBlank` — explicitly set `EnableAccessibilityFeatures = False`
   and `ExtendedClass = ""` on each screen's layout instance (section 6);
   don't leave either blank.
4. **UserProfile screen, on its own.** Disproportionately complex relative
   to the other five screens combined (13 local vars, 10 screen actions,
   a screen aggregate, a verification-code + countdown-timer flow) — a
   prior run bundled it into the same batch as the other five screens and
   its wiring came out incomplete (aggregate never bound to widgets,
   `SaveChangesOnClick`/`SendVerificationCode` never bound to their save
   button/get-code link). Giving it a dedicated batch and dedicated
   validation pass catches that before it compounds into later batches.
   This screen's layout is `LayoutTopMenu` — explicitly set
   `HasFixedHeader = True`, `EnableAccessibilityFeatures = False`, and
   `ExtendedClass = ""` on the instance; a blank argument here is a
   confirmed publish-time error (section 6), not just a style nit.
5. **Server actions + client actions** (Authentication folder), including
   `Check{App}Role` — wire ALL previously-stubbed screen logic from
   batches 3 and 4, including UserProfile's.
6. **Email templates + external site**.
7. **OnException handler** (Common flow) — all four branches (Security,
   Database, Communication, All Exceptions), then set it as the app's
   exception handler.
8. **Wiring Closure & Validation Sweep** — see below. Always run this as
   its own final batch, never skip it.

Prompt each batch with the exact names, types, and logic from the
relevant section above — Mentor performs worse on vague asks
("add a login flow") than on the literal spec.

### Mandatory wiring instruction (include in every batch 2–7 prompt)

A spec phrase like *"`LoginOnClick` — validate form, call `DoLogin`..."*
or *"`OnReady` calls `LayoutReady`, `SetLang`, `AddFavicon`"* describes a
**required graph edge**, not documentation of intent. In a prior run,
Mentor created the actions with correct internal logic and created the
screen widgets separately, but never connected the two — every button,
link, and icon's click/change event was left unbound to the action that
was supposed to fire it, and every "action calls action" edge inside a
lifecycle hook (`OnReady` → `SetLang`/`AddFavicon`, `ClientLogout` →
`DoLogout`, `SaveChangesOnClick` → `UpdateUser`, etc.) was frequently left
as an unconnected stub too. This produced dozens of "Unused Screen
Action" / "Unused Local Variable" / "Unused Client Action" warnings even
though every individual piece existed and was individually correct.

Append this to every batch prompt that creates or references widgets,
actions, or lifecycle hooks:

> For every "X calls Y" / "OnClick triggers Z" / lifecycle-hook phrase in
> this spec, create an actual node connection (a Call node, an
> Assign-then-navigate, a bound widget event) — not just the action's
> internal logic in isolation. Every non-lifecycle screen/client action
> you create in this batch must have at least one real caller (a widget
> event or another action) by the end of this batch. **The same rule
> applies to every declared input parameter on a block or screen** — a
> parameter is not "done" once declared; it must be bound into a real
> widget property (a CSS class expression, a data attribute, a conditional)
> inside that same block/screen, exactly like the explicit bindings
> specified for layout block parameters in section 6 above. A declared,
> unbound parameter produces the same class of "Unused Element" warning as
> an unwired action. Before ending the turn, check `GetValidationMessages`
> for "Unused Action"/"Unused Element"/"Unused Local Variable" warnings on
> anything created in *this* batch specifically, and wire or remove them
> now — do not defer to a later batch or assume they'll "clear once
> wired," because unless you verify it in this same turn, they won't.

### Avoiding stub-naming collisions across batches

Batch 2 creates blocks (e.g. `UserInfo`) whose logic references actions
that won't exist until Batch 5 (e.g. `ClientLogout` is meant to eventually
call a `DoLogout` client action). If Mentor creates a same-named local
placeholder/stub for that future action now, Batch 5's real
`DoLogout` client action creation collides with it — the platform
auto-suffixes the real one (`DoLogout2`) and Mentor then has to spend a
turn diagnosing and unwinding the collision (delete the stub, rename the
real action back). This happened in a prior run and cost most of a batch's
wall-clock time. Prefer either: leave the future call genuinely
unconnected with a comment node ("TODO: wire to DoLogout in Batch 5")
rather than a same-named stub action, or if a stub action is unavoidable,
name it distinctly (`DoLogout_Stub`, `DoLogout_Pending`) so it can't
collide with the real one later.

### Expected-unused exceptions (don't force-wire these)

A few elements are legitimately unused at baseline stage because the
thing that would consume them doesn't exist yet — don't manufacture fake
wiring to silence these; document them as expected in the report instead.
Note: `Menu.ActiveItem`/`ActiveSubItem` used to be listed here, but the
right fix turned out to be not scaffolding them at all until real menu
items exist (see section 7) — an unfixable-at-this-stage warning is
better avoided than merely documented, whenever avoiding it is actually
possible:

- **`Login`'s `ExternalIdentityProviders`/`ShowExternalProvider`** — the
  underlying data and visibility toggle only becomes visually meaningful
  once the tenant has an external identity provider configured, but both
  are already consumed (by `OnInitialize`'s population logic and the
  container's `If(ShowExternalProvider, ...)` visibility expression), so
  they don't produce "Unused Element" warnings and need no special
  handling either way.
  **Do NOT** also list `IsBuiltInExecuting`/`ExecutingIndex`/
  `ProviderIndex` here — a prior run treated all five as one inert group
  and left three of them permanently unwired as a result. Those three ARE
  wireable at design time regardless of external-IdP configuration; see
  the mandatory wiring note under `Login` in section 8 and fix them in
  Batch 3, don't defer them.
- **`LoginProviderOnClick`'s `ProviderIndex`** — this one is different in
  kind from the rest of this list: it's a **known validator false
  positive**, not a genuinely-deferred consumer. Even with the correct
  `ExecutingIndex = ProviderIndex` assignment wired in as the action's
  first step, `GetValidationMessages` can still report it as "Unused
  Element". Don't spend a batch trying to make this specific warning
  disappear — confirm the assignment exists in the action's logic (that
  is the actual acceptance criterion), and if the warning is still
  present after that, classify it in Batch 8 as a confirmed false
  positive rather than a fix-now item or a business-logic-not-ready
  item.

## Wiring Closure & Validation Sweep (Batch 8)

Always run this as a final, dedicated batch after OnException — never
treat "some warnings are expected at this stage" as a reason to skip it.
A prior run assumed unresolved warnings would "clear once wired" without
ever re-checking, and dozens survived all the way to publish.

1. Have Mentor call `GetValidationMessages(true)` (or equivalent full
   validation) across the whole eSpace and list every remaining warning.
2. Classify each one:
   - **Fix now** — a widget/action/variable that should be connected and
     isn't (the common case per the mandatory wiring instruction above).
     Wire it in this same batch.
   - **Expected-at-baseline** — matches one of the documented exceptions
     above (`ExternalIdentityProviders`/`ShowExternalProvider` with no
     external IdP configured — note this pair is already consumed and
     shouldn't actually be warning), or another case you confirm with the
     user follows the same "the consumer doesn't exist yet" logic.
     `IsBuiltInExecuting`/`ExecutingIndex` do NOT belong in this bucket —
     see section 8's mandatory wiring.
   - **Known false positive** — `LoginProviderOnClick`'s `ProviderIndex`
     specifically: confirm the `ExecutingIndex = ProviderIndex` assignment
     genuinely exists, and if the warning persists anyway, classify it
     here rather than as "Fix now" (there's nothing left to fix) or
     "Expected-at-baseline" (it's not waiting on anything to exist).
   - **Remove** — dead scaffolding that serves no purpose for this app;
     confirm with the user before deleting anything from the documented
     spec (sections 1–13 above) rather than silently trimming it.
3. Report the final classified list to the user: what was wired, what's
   expected-and-why, what (if anything) was removed. Don't report "0
   errors" as equivalent to "0 warnings" or as "done" — the two are
   different signals and both matter here.
4. Only after this sweep is `no_changes_detected` on the subsequent
   publish meaningful as a real "already up to date" signal rather than
   "silently shipped with unwired stubs."

## Post-Crash-Recovery Structural Check

If any batch's Mentor turn crashes mid-way (a transient upstream error) and
you resume/retry — especially a retry that involved creating folders,
renaming actions, or deleting stub objects to resolve a naming collision —
run this check before moving to the next batch. This is NOT optional
cleanup; it's the single highest-value check in this whole skill for
catching build-breaking-but-validation-invisible defects.

A prior run's Batch 5 crashed, and the recovery sequence (folder creation
+ rename + stub deletion) silently left **two distinct folder objects both
named "Authentication"** — one correctly scoped to server actions, one to
client actions, created by two separate recovery attempts. `GetValidationMessages`
never flagged it (both folders are individually valid objects), but the
build compiler failed with a generic `OS-DPL-42202` ("An error has occurred
while building the application") for 9 build attempts across 3 rounds of
unrelated guessing (image format, theme assignment, expression syntax)
before this was found. Checking it directly the moment a crash-recovery
touches folders/objects would have caught it in seconds.

Have Mentor:
1. Enumerate `eSpace.Folders` — list every folder's `Name` and its
   `ObjectKey`. If any name appears more than once, that's the defect:
   consolidate into a single folder per (name, scope) pair and reassign
   every action/element pointing at the duplicate.
2. Enumerate every server action and client action's `.Folder` property —
   confirm none are `null`/unassigned (a crash-recovery loop that touches
   folder assignment can silently drop an action's folder reference
   entirely, not just duplicate the folder).
3. Report the folder count and names — if it doesn't match what this
   batch was supposed to create, treat that as a real defect, not noise.

## Pre-Publish Structural Sanity Check

Run this once, before the *first* publish attempt of the whole baseline —
distinct from Batch 8's warning-classification sweep, because these are
defects `GetValidationMessages` cannot see at all (they're not warnings;
they're consistency issues in objects the validator doesn't cross-check
against the build compiler's assumptions):

1. **Duplicate folder names** — see Post-Crash-Recovery Structural Check
   above; run it even if nothing crashed this session, as a cheap
   insurance check.
2. **`(System)` reference health** — confirm the `Hash` is non-zero (see
   pre-flight step 7). If zero, fix it now via the pattern in Model API
   Patterns — don't discover this only after a failed publish.
3. **No orphaned action-folder assignments** — every server/client action
   has a non-null `.Folder`.

If the first publish attempt still fails, do NOT start guessing broadly
(images, unrelated expressions, unrelated themes) — that consumed most of
a prior run's debugging time on red herrings. Instead, match the error
code to a known cause first:

- **`OS-DPL-42202`** ("An error has occurred while building the
  application") — a generic build-compiler failure. First suspect:
  duplicate folder names or orphaned folder assignments (see checks
  above) — especially if any batch this session involved a crash/retry.
  Only broaden to other areas (SendEmail node structure, exception
  handler wiring, expression syntax) if the folder/reference checks come
  back clean.
- **`OS-BEW-CODE-40036`** ("uses entity 'X' that is incompatible with its
  definition in reference 'Y'") — a stale/schema-mismatched reference.
  Fix via the `(System)` reference refresh pattern in Model API Patterns,
  then re-verify every expression reading an attribute of that entity
  (schema drift is common — see pre-flight step 8).

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
- **MainFlow ships empty on purpose** — a fresh scaffold has 0 screens, 0
  blocks, 0 exception handler in MainFlow. That's the expected end state,
  not a gap to fill in as part of this baseline.
- **OnException is app-wide, not per-flow** — it lives in Common but is
  registered as the whole app's exception handler, so it also covers
  unhandled exceptions raised from MainFlow screens once those exist.
  Specific handlers (Security/Database/Communication) must precede the
  All Exceptions catch-all or they'll never fire.

## Verification Checklist

After each Mentor batch, confirm via the matching context tool:

- [ ] `context_themes`: 2 themes exist (`{App}` extending `OutSystemsUI`,
      `EmailTheme`)
- [ ] `EmailTheme`'s stylesheet matches `assets/EmailTheme.css` (not left
      blank) — check the theme's actual CSS content, not just that the
      theme object exists
- [ ] `context_roles`: the confirmed application role exists
- [ ] `context_screens`: 6 screens exist with correct
      `AnonymousAccess` flags and layouts
- [ ] `context_actions`: 3 server actions + 6 client actions (including
      `Check{App}Role`) exist in an `Authentication` folder
- [ ] Layout blocks and common blocks aren't directly enumerable via
      `context_actions`/`context_screens` in all tenants — if they don't
      surface there, confirm via Mentor's own OML inspection or Service
      Studio instead of assuming absence
- [ ] Email templates exist under the Emails flow, themed with
      `EmailTheme`
- [ ] `RedirectToURL` external site exists
- [ ] `MainFlow` exists and is empty (0 screens, 0 blocks, 0 exception
      handler) — confirm via Mentor/Service Studio, not just
      `context_screens` (an empty flow won't list anything to check)
- [ ] `OnException` in Common has all 4 branches (Security, Database,
      Communication, All Exceptions) in that precedence order, and is
      registered as the app's exception handler
- [ ] 0 errors in validation after each batch before moving to the next
- [ ] `eSpace.IsUserProvider` is `true` — no `ImplicitSelfUserProvider`
      warning
- [ ] Referenced `OutSystemsUI` version supports the chosen `IconLibrary`
      (`Phosphor2.0` needs ≥ 2.28.0) — checked via ODC Portal/Studio's
      dependency panel directly (not the Model API's enum-acceptance
      proxy, which cannot prove version compatibility), and re-confirmed
      as an actual absence of the "Icon library compatibility" warning in
      `GetValidationMessages` after Batch 1; if the version is below
      2.28.0, a tenant-level OutSystemsUI upgrade was requested before
      publish
- [ ] `Login.LoginOnClick` implements the full flow from section 8: sets
      `IsBuiltInExecuting`, validates the form, calls `DoLogin`, calls
      `Check{App}Role` on success, branches to redirect /
      "No permissions." + `DoLogout` / `DoLogin`'s own error message,
      and has an exception handler that resets `IsBuiltInExecuting` and
      clears `Password`
- [ ] `Login.LoginProviderOnClick` assigns `ExecutingIndex = ProviderIndex`
      as its first step, calls `GetExternalLoginURL`, redirects, and its
      exception handler resets both `IsBuiltInExecuting = False` and
      `ExecutingIndex = -1`
- [ ] Both the built-in login button and every external-provider list
      item are cross-wired to `Not(IsBuiltInExecuting) And ExecutingIndex = -1`
      for their `Enabled` state (not just their own individual loading
      spinner) — this cross-wiring, not just each button's own binding,
      is what makes `IsBuiltInExecuting`/`ExecutingIndex` genuinely used
- [ ] `Login.ExecutingIndex` defaults to `-1`, not `0`
- [ ] `ProviderIndex` on `LoginProviderOnClick` is genuinely assigned to
      `ExecutingIndex` — a known false positive can still flag it as
      "Unused Element" even when correctly wired; confirm the assignment
      exists in the action's logic rather than trusting the absence (or
      presence) of that specific warning either way. Only
      `ExternalIdentityProviders`/`ShowExternalProvider` are the
      legitimately-inert (but already-consumed, non-warning) pair
- [ ] `EmailTheme` does NOT extend `OutSystemsUI` (standalone/root theme
      only), and the `Emails` flow's own `Theme` property (not just each
      template's) is set to `EmailTheme` — confirm the "UI Flow 'Emails'
      is using a theme that is larger than 14KB" warning is actually
      absent, not just that each template's `Theme` field looks correct
- [ ] Every layout block parameter (`ExtendedClass`,
      `EnableAccessibilityFeatures`, `HasFixedHeader`, `MenuBehavior`) is
      bound into a real widget property on its own block, per section 6 —
      confirm after Batch 2, don't defer
- [ ] Separately from the above: every screen's layout-block INSTANCE
      (not the block's own definition) has every one of that block's
      parameter arguments explicitly set — `LayoutBlank` screens:
      `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`;
      `LayoutTopMenu` screens (`UserProfile`): `HasFixedHeader = True`,
      `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`. None
      of these are `Mandatory`, but a blank argument on the screen
      instance is a confirmed publish-time error regardless — check
      every screen created in Batches 3-4, don't assume the block's own
      default silently applies
- [ ] `Menu` block has no `ActiveItem`/`ActiveSubItem` parameters at
      baseline (they're deferred until real menu items exist — see
      section 7)
- [ ] After Batch 8 (Wiring Closure & Validation Sweep): 0 "Unused
      Action"/"Unused Element"/"Unused Local Variable"/"Unused Input
      Parameter"/"Unused Aggregate" warnings remain, other than ones
      explicitly classified as expected-at-baseline and reported to the
      user by name
- [ ] Pre-Publish Structural Sanity Check run once before the first
      publish attempt: no duplicate folder names, no orphaned
      action-folder assignments, `(System)` reference hash non-zero
- [ ] If any batch crashed and was retried: Post-Crash-Recovery
      Structural Check run before moving to the next batch, not deferred
      to the end

## Related Skills

- **Run before:** `outsystems-spec-driven-build`, `outsystems-design-to-app`
  — both assume an app shell exists; this skill makes that shell a real
  usable app first.
- **Run before:** `dbresults-odc-scaffold-entity` / `dbresults-odc-crud-wrapper`
  — business entities layer on top of this foundation, not instead of it.
- **Chain:** `app_create` → `dbresults-odc-new-app-baseline` →
  (`outsystems-spec-driven-build` | `outsystems-design-to-app`) →
  `dbresults-odc-scaffold-entity` (per entity) → `dbresults-odc-ship`.
