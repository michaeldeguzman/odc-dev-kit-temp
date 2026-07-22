# New App Baseline — Reference Spec

Ground-truth spec for the auth/theme/layout scaffold. Referenced by
`SKILL.md` batch-by-batch — do not read this file end-to-end unless
auditing the full spec. Anchors below match the batch numbers in
`SKILL.md`'s Mentor Prompt Strategy.

## Layers to Scaffold

### 1. UI Flows

- **Common** — auth screens, shared blocks, email templates; `OnExceptionHandler` → `OnException`
- **Layouts** — layout blocks used by all screens
- **Emails** — email templates; flow `Theme` = `EmailTheme`
- **MainFlow** — intentionally **empty** on a fresh scaffold. Do not add anything here. **Default screen:** do NOT set any Common-flow screen as default — the default screen is the first screen created in MainFlow by whatever skill runs after this one.

### 2. Themes

- **`{App}`** — extends `OutSystemsUI`
  - Description: `"Application theme."`
  - Grid type: Fluid, Max width: 1280, Icon library: `Phosphor2.0`
  - Default layout: `LayoutTopMenu`, Default menu: `Menu`
  - Theme values: `PrimaryColor`, `SecondaryColor`, `AppPrimaryColor` → `{BrandColor}`; `CreatedWithoutCustomCSS` → `"true"`
- **`EmailTheme`** — standalone theme (do **NOT** extend `OutSystemsUI` — that inherits the full CSS bundle and triggers a "UI Flow 'Emails' is using a theme that is larger than 14KB" warning). Apply CSS from [`assets/EmailTheme.css`](assets/EmailTheme.css) verbatim.
  - Description: `"Application emails theme."`
  - Grid type: Fluid (12 columns, 20px gutter, no min/max width) — explicitly set, not `Inherited`
  - Icon library: `Phosphor2.0`
  - Set the `Emails` **flow's own** `Theme` property to `EmailTheme` at creation time (not just each template's property).

### 3. Role & App Identity

- **`{App}`** — the single application role. All 6 screens carry it (including anonymous ones).
- **`eSpace.IsUserProvider = true`** — correct fix for the `ImplicitSelfUserProvider` warning. This is a directly-settable Model API boolean on the eSpace. Do not attempt workarounds via reflection-discovered metadata keys.

### 4. Client Variables

| Name | Type | Purpose |
|---|---|---|
| `LastURL` | Text | Last visited URL — for post-login redirect. Written by `OnException` SecurityException handler; cleared by `DoLogout`; read by `Login.LoginOnClick`. |
| `UserName` | Text | Display name of logged-in user. Written by `UserInfo.GetUsernameAndPhoto` and `UserProfile.SaveChangesOnClick`; cleared by `DoLogout`. |
| `UserPhotoURL` | Text | Photo URL. Written by `UserInfo.GetUsernameAndPhoto` and `UserProfile.SaveChangesOnClick`; cleared by `DoLogout`. |

`DoLogin`, `SendResetPasswordEmail`, `SendChangeEmail` — none touch any client variable.

### 5. Local Images

| Name | Purpose |
|---|---|
| `Logo` | App logo on login screen and header |
| `User` | Placeholder avatar for users without a photo |

Use a 1×1 transparent GIF (not PNG — no CRC to get wrong).

### 6. Layout Blocks (in Layouts flow)

All four lifecycle-having blocks share: `OnInitialize` → `SetIconLibraryClass`, `OnReady` → `LayoutReady` + `SetLang` + `AddFavicon("favicon.png")`, `OnDestroy` → `LayoutDestroy`. `LayoutBaseSection` has no lifecycle actions.

**Parameter rules (apply to all blocks):**
- All parameters `IsMandatory = False` — Mentor creates mandatory by default; this causes hard errors when screens use the block.
- All parameters need non-empty descriptions.
- Every parameter must be **bound into a real widget property** inside the block definition (not left declared-but-unread). Unbound parameters produce "Unused Element" warnings identical to unwired actions.
- Every **screen instance** of a layout block must explicitly set ALL arguments even though none are mandatory — leaving an argument blank (not `False`/`""` — genuinely blank) is a confirmed publish-time error.

#### LayoutBlank

Parameters:

| Parameter | Type | Default (block def) | Value on every screen instance |
|---|---|---|---|
| `EnableAccessibilityFeatures` | Boolean | null (unset) | `False` |
| `ExtendedClass` | Text | null (unset) | `""` |

Client Actions: `OnInitialize`, `OnReady`, `OnDestroy`.

#### LayoutTopMenu

Description: `"Adds a layout with the menu on the header, most used in applications with few menu items."`

Parameters:

| Parameter | Type | Default (block def) | IsMandatory | Value on every screen instance |
|---|---|---|---|---|
| `HasFixedHeader` | Boolean | `True` | No | `True` |
| `EnableAccessibilityFeatures` | Boolean | `False` | No | `False` |
| `ExtendedClass` | Text | `""` | No | `""` |

> `EnableAccessibilityFeatures`: NewApp reference leaves default null (implicitly False). Set `False` explicitly so callers omitting the argument don't get publish errors — behavior is identical.

Client Actions:

| Action | Trigger | Steps |
|---|---|---|
| `OnInitialize` | Block init | Calls `SetIconLibraryClass` (local stub — ODC Studio: replace with real `OutSystemsUI.SetIconLibraryClass`). |
| `OnReady` | After first render | `LayoutReady` → `SetLang(Lang: null)` → `AddFavicon(URL: "favicon.png")` (all OutSystemsUI). |
| `OnDestroy` | Block destroy | `LayoutDestroy` (OutSystemsUI). |
| `SkipToContentOnClick` | Skip-nav link OnClick | Description: `"Handles the skip to content."` Calls `SkipToContent(TargetId: MainContentWrapper.Id)` (OutSystemsUI). |

Widget tree — create every widget in this exact structure. The 6 content zones are `Placeholder` (WebBlockZone) widgets, **never** plain Containers — screens cannot inject content into plain Containers:

```
LayoutWrapper  [Container]
  Style: "layout layout-top"
         + If(HasFixedHeader, " fixed-header", "")
         + If(EnableAccessibilityFeatures, " has-accessible-features", "")
         + If(ExtendedClass = "", "", " " + ExtendedClass)
  │
  └── (unnamed Container)
        Style: "main"
        │
        ├── Header2  [AdvancedHtml, Tag: header]
        │     Extended props: role="banner", class="header"
        │     │
        │     ├── (unnamed Link)
        │     │     Style: "skip-nav", OnClick → SkipToContentOnClick
        │     │     Extended props:
        │     │       aria-label = "Skip to Content (Press Enter)"
        │     │       data-showskipcontent = If(EnableAccessibilityFeatures, "true", "false")
        │     │     └── (unnamed Text) — "Skip to Content (Press Enter)"
        │     │
        │     └── (unnamed Container)
        │           Style: "header-top ThemeGrid_Container"
        │           └── (unnamed Container)
        │                 Style: "header-content display-flex"
        │                 ├── [WebBlock: MenuIcon from Common]   (no params)
        │                 ├── [WebBlock: ApplicationTitle from Common]   (no params)
        │                 └── Header  [Placeholder]
        │                       Style: "header-navigation"
        │                       EffectiveWidth: InlineBlock   ← NOT UserDefined
        │                       └── [WebBlock: Menu from Common]   (ActiveItem=null, ActiveSubItem=null)
        │
        └── Content  [Container]
              Style: "content"
              │
              ├── MainContentWrapper  [Container]
              │     Style: "main-content ThemeGrid_Container"
              │     Extended props: role="main"
              │     │
              │     ├── Breadcrumbs  [Placeholder]
              │     │     Style: "content-breadcrumbs placeholder-empty"
              │     │     EffectiveWidth: UserDefined (fill parent)
              │     │
              │     ├── (unnamed Container)
              │     │     Style: "content-top display-flex align-items-center"
              │     │     ├── Title  [Placeholder]
              │     │     │     Style: "content-top-title heading1 placeholder-empty"
              │     │     │     EffectiveWidth: UserDefined
              │     │     └── Actions  [Placeholder]
              │     │           Style: "content-top-actions placeholder-empty"
              │     │           EffectiveWidth: UserDefined
              │     │
              │     └── MainContent  [Placeholder]
              │           Style: "content-middle"
              │           EffectiveWidth: UserDefined
              │
              └── (unnamed AdvancedHtml, Tag: footer)
                    Extended props: role="contentinfo", class="content-bottom"
                    └── Footer  [Placeholder]
                          Style: "footer ThemeGrid_Container placeholder-empty"
                          EffectiveWidth: UserDefined
```

> **`Header` placeholder `EffectiveWidth = InlineBlock`** — allows the nav menu to shrink to content width. All other placeholders use `UserDefined` (fill parent). Mentor defaults all to `UserDefined`; `Header` is the only exception that must be corrected.

#### LayoutSideMenu

Parameters:

| Parameter | Type | Default (block def) | Value on every screen instance |
|---|---|---|---|
| `HasFixedHeader` | Boolean | `True` | `True` |
| `MenuBehavior` | SideMenuBehavior Identifier | null (unset) | `""` if no specific behavior |
| `EnableAccessibilityFeatures` | Boolean | null (unset) | `False` |
| `ExtendedClass` | Text | `""` | `""` |

`MenuBehavior` type must be `SideMenuBehavior Identifier` (from OutSystemsUI static entity) — Mentor defaults to `Text`, which breaks the binding.

Client Actions: `OnInitialize`, `OnReady`, `OnDestroy`, `SkipToContentOnClick`.

Placeholders: `Navigation`, `Header` (header-navigation), `Breadcrumbs`, `Title`, `Actions`, `MainContent`, `Footer`.

#### LayoutBase

Parameters:

| Parameter | Type | Default (block def) | Value on every screen instance |
|---|---|---|---|
| `HasFixedHeader` | Boolean | `True` | `True` |
| `EnableAccessibilityFeatures` | Boolean | null (unset) | `False` |
| `ExtendedClass` | Text | `""` | `""` |

Client Actions: `OnInitialize`, `OnReady`, `OnDestroy`, `SkipToContentOnClick`.

Placeholders: `Header` (header-navigation), `MainContent` (content-middle — contains a `LayoutBaseSection` instance by default).

#### LayoutBaseSection

No lifecycle actions. All three parameters (`BackgroundColor`, `Padding`, `ExtendedClass`) should be left null/unset on screen instances — identifier-typed or optional; empty means "no override."

| Parameter | Type | Default |
|---|---|---|
| `BackgroundColor` | Color Identifier | null |
| `Padding` | Space Identifier | null |
| `ExtendedClass` | Text | null |

Placeholders: `BackgroundImage` (section-background), `Content` (section-content).

### 7. Common Blocks (in Common flow)

#### ApplicationTitle

No input parameters.

| Client Action | Trigger | Logic |
|---|---|---|
| `ApplicationNameOnClick` | onclick on wrapper | Navigates to `RedirectToURL` with `GetOwnerURLPath()`. |

#### MenuIcon

No input parameters.

| Client Action | Trigger | Logic |
|---|---|---|
| `OnReady` | After first render + on parameter change | Calls `SetMenuIconListeners`. |
| `OnClick` | onclick on icon container | Calls `ToggleSideMenu`. |

#### Menu

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ActiveItem` | Integer | `-1` | Index of active menu item. -1 = none. |
| `ActiveSubItem` | Integer | `-1` | Index of active submenu item. -1 = none. |

Include `ActiveItem`/`ActiveSubItem` at baseline stage with default `-1` — the NewApp reference includes both; the `-1` default suppresses the "Unused Element" warning. Explicitly pass both arguments on every `Menu` instance in layout blocks (either `-1` or a computed page index).

| Client Action | Trigger | Logic |
|---|---|---|
| `OnReady` | After first render | Calls `MenuReady` → `SetActiveMenuItems(ActiveItem, ActiveSubItem)`. |
| `OnRender` | `OnParametersChanged` event | Re-runs `SetMenuListeners`. **The lifecycle event is `OnParametersChanged`; the action is named `OnRender`** — do not name it `OnParametersChanged` (collides with the event). |
| `OnDestroy` | On removal | Calls `MenuDestroy`. |
| `HideMenu` | onclick on overlay | Calls `ToggleSideMenu`. |

Widget: `<nav>` with `PageLinks` container (navigation links added here by later skills) and `LoginInfo` container containing `UserInfo` block. Plus an overlay container wired to `HideMenu`.

#### UserInfo

No input parameters.

| Client Action | Trigger | Logic |
|---|---|---|
| `OnReady` | After first render | Calls `GetUsernameAndPhoto`. |
| `GetUsernameAndPhoto` | Called by `OnReady` | If `Client.UserName` empty and user logged in: calls system `GetUserProfile`, assigns `Client.UserName` and `Client.UserPhotoURL`. |
| `ClientLogout` | Logout link click | Calls `DoLogout` → navigates to `RedirectToURL` with `URL = DoLogout.RedirectURL` (fade). |

### 8. Screens (in Common flow)

All 6 screens carry the `{App}` role — including the 4 anonymous-access screens. `AnonymousAccess = true` overrides the role check at runtime; the role attachment is harmless and matches the reference implementation. **Do NOT remove the role from any screen.**

Every screen's layout block instance must have all parameter arguments explicitly set (see section 6 call-site rule).

- **`Login`** — `AnonymousAccess = true`, layout `LayoutBlank` (`EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). **Not the default screen.**

  Local vars: `UserEmail`, `Password`, `IsPasswordVisible`, `ShowBuiltInProvider`, `ShowExternalProvider`, `IsBuiltInExecuting` (Boolean), `ExecutingIndex` (Integer, default **`-1`** — not `0`), `ExternalIdentityProviders`.

  | Action | Trigger | Logic |
  |---|---|---|
  | `OnInitialize` | Screen init | (1) If already logged in → redirect to app root. (2) `IsBuiltInExecuting = False`, `ExecutingIndex = -1`. (3) Call `IsBuiltinIdentityProviderActive` → assign `ShowBuiltInProvider`. (4) Call `GetExternalIdentityProviders` → assign `ExternalIdentityProviders`, `ShowExternalProvider`. |
  | `LoginOnClick` | Login button | (1) `IsBuiltInExecuting = True`. (2) If `LoginForm.Valid` false → `IsBuiltInExecuting = False`, end. (3) `FeedbackMessageClose`. (4) Call `DoLogin(UserEmail, Password)`. (5) Call `Check{App}Role` (platform-generated, outputs `HasRole: Boolean`) — runs **unconditionally** after `DoLogin`. (6) Branch on `DoLogin.Success` + `HasRole`: success+role → navigate to `RedirectToURL(If(Client.LastURL="", GetOwnerURLPath(), Client.LastURL))`; success+no role → show "No permissions.", `DoLogout`, `IsBuiltInExecuting = False`; failure → clear `Password`, show `DoLogin.ErrorMessage`, `IsBuiltInExecuting = False`. AllExceptions handler: clear `Password`, `IsBuiltInExecuting = False`, show exception. |
  | `LoginProviderOnClick(ProviderIndex: Integer, ProviderKey: Text)` | External provider button | (1) `ExecutingIndex = ProviderIndex` (this assignment is the real consumer of `ProviderIndex` — a validator false positive can flag it as unused even when correctly wired; confirm the assignment exists and ignore the warning). (2) Call `GetExternalLoginURL(IdentityProvider = ProviderKey)`. (3) Navigate to `RedirectToURL(URL = GetExternalLoginURL.ExternalLoginURL)`. Exception handler: `IsBuiltInExecuting = False`, `ExecutingIndex = -1`. |
  | `OnTogglePasswordVisibility` | Eye icon | Toggles `IsPasswordVisible`, calls `ShowPassword` with **no WidgetId** (unlike ChangePassword/RecoverPasswordReset). |

  **Cross-wiring `IsBuiltInExecuting` / `ExecutingIndex`:** Both gate the lock state of every interactive element together:
  - `UserEmail` and `Password` inputs: `Enabled = ExecutingIndex = -1 and not IsBuiltInExecuting`
  - Built-in login button `Enabled`/`ButtonLoading`: `Not(IsBuiltInExecuting) And ExecutingIndex = -1`
  - Each external-provider list item `Enabled`: same expression; loading spinner: `ExecutingIndex = CurrentRowNumber`

  **Do NOT create a `Check{App}Role`/`Has{App}Role` wrapper client action** — the platform-generated `Check{App}Role` IS the check; wrappers collide with its name and get auto-suffixed.

- **`RecoverPasswordRequest`** — `AnonymousAccess = true`, layout `LayoutBlank`. Local vars: `IsExecuting` (Boolean, False), `Email` (Email).

  | Action | Trigger | Logic |
  |---|---|---|
  | `ResetPasswordOnClick` | "Reset password" button | (1) If `RecoverPasswordForm.Valid` false → end. (2) `IsExecuting = True`. (3) Call `SendResetPasswordEmail(CustomerEmail = Email)`. (4) Success → `IsExecuting = False` → navigate to `RecoverPasswordReset(Email = Email)` (VerificationCode NOT passed). (5) Failure → show `"An error has occured. Please try again later."` (typo preserved), `IsExecuting = False`. **No `AllExceptions` handler.** |

- **`RecoverPasswordReset`** — `AnonymousAccess = true`, layout `LayoutBlank`. Input params: `Email` (Email, mandatory), `VerificationCode` (Text, optional).

  Local vars: `NewPassword`, `ConfirmPassword`, `IsPasswordVisible` (Boolean, False), `IsConfirmPasswordVisible` (Boolean, False), `IsButtonEnabled` (Boolean, False), `IsExecuting` (Boolean, False), `IsNewPasswordCompliant` (Boolean).

  | Action | Trigger | Logic |
  |---|---|---|
  | `SetIsButtonEnabled` | Called by input handlers | All fields non-empty + `IsNewPasswordCompliant` → sets `IsButtonEnabled`. |
  | `Input_CodeOnChange` | Code input change | Calls `SetIsButtonEnabled`; clears validation errors if empty. |
  | `Input_ConfirmPasswordOnChange` | Confirm password change | Calls `SetIsButtonEnabled`; clears validation errors if empty. |
  | `PasswordPolicyCompliant` | `PasswordPolicy` block `Compliant` event | `IsNewPasswordCompliant = IsValid` → `SetIsButtonEnabled`. |
  | `OnToggleNewPasswordVisibility` | Eye icon | Toggles `IsPasswordVisible` → `ShowPassword(Input_NewPassword.Id)`. |
  | `OnToggleConfirmPasswordVisibility` | Eye icon | Toggles `IsConfirmPasswordVisible` → `ShowPassword(Input_ConfirmPassword.Id)`. |
  | `SavePasswordOnClick` | "Save password" button | (1) If `RecoverPasswordForm.Valid` false → end. (2) If `NewPassword ≠ ConfirmPassword` → `Input_ConfirmPassword.Valid = False`, `ValidationMessage = "Passwords doesn't match."` (typo preserved), end. (3) `IsExecuting = True`. (4) Call `FinishResetPassword(Email, NewPassword, VerificationCode)`. (5) `ComplexityFailed`: mark `Input_NewPassword.Valid = False`, `IsButtonEnabled = False`, `IsExecuting = False`. `InvalidVerificationCode`: `Input_Code.Valid = False`, `IsExecuting = False`. Unknown: show `"An unknown error occured. Please try again later."` (typo), `IsExecuting = False`. (6) Success: call `DoLogin(Email, NewPassword)` → success → navigate to `RedirectToURL(GetOwnerURLPath())`; failure → navigate to `Login`. AllExceptions handler: show `ExceptionMessage`, `IsExecuting = False`. |

- **`ChangePassword`** — requires login, layout `LayoutTopMenu` (`HasFixedHeader = True`, `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). Aggregate: `GetUserDetail` (Source: User, Filter: `User.Id = GetUserId()`, MaxRecords: 1).

  Local vars: `OldPassword`, `NewPassword`, `ConfirmPassword`, `IsPasswordVisible` (Boolean, False), `IsConfirmPasswordVisible` (Boolean, False), `IsButtonEnabled` (Boolean, False), `IsExecuting` (Boolean, False), `IsNewPasswordCompliant` (Boolean).

  | Action | Trigger | Logic |
  |---|---|---|
  | `OnInitialize` | Screen init | If `IsExternalUser()` → redirect to `InvalidPermissions`. |
  | `SetIsButtonEnabled` | Called by handlers | `OldPassword`, `NewPassword`, `IsNewPasswordCompliant`, `ConfirmPassword` all non-empty → `IsButtonEnabled`. |
  | `Input_OldPasswordOnChange` | Old password change | Calls `SetIsButtonEnabled`. |
  | `Input_ConfirmPasswordOnChange` | Confirm change | Calls `SetIsButtonEnabled`; clears validation errors if empty. |
  | `PasswordPolicyCompliant` | `PasswordPolicy` `Compliant` event | `IsNewPasswordCompliant = IsValid` → `SetIsButtonEnabled`. |
  | `OnToggleNewPasswordVisibility` | Eye icon | Toggles `IsPasswordVisible` → `ShowPassword(Input_NewPassword.Id)`. |
  | `OnToggleConfirmPasswordVisibility` | Eye icon | Toggles `IsConfirmPasswordVisible` → `ShowPassword(Input_ConfirmPassword.Id)`. |
  | `SetNewPasswordOnClick` | "Set new password" button | (1) If `Form.Valid` false → end. (2) `IsExecuting = True`. (3) If `NewPassword ≠ ConfirmPassword` → `Input_ConfirmPassword.Valid = False`, `ValidationMessage = "Password and Confirm password don't match."`, `IsExecuting = False` → end. (4) Call system `ChangePassword(OldPassword, NewPassword, Username = GetUserDetail.List.Current.User.Email)`. (5) Success → show `"Password successfully changed!"` → navigate to `UserProfile`. `InvalidCredentials`: mark `Input_OldPassword.Valid = False`. `PasswordComplexityPolicyFailed`: `Input_NewPassword.Valid = False`, `IsButtonEnabled = False`. `TooManyFailedAttempts`: show timeout message. Other: show unknown error. **No `AllExceptions` handler.** |

  Layout: `Breadcrumbs` placeholder has "← Back to profile" link → `UserProfile`. `Title` = "Change your password". `MainContent` has `Columns2` with form in `Column1`.

- **`InvalidPermissions`** — `AnonymousAccess = true`, layout `LayoutTopMenu` (`HasFixedHeader = True`, `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). No local vars, no aggregates, no screen actions. `MainContent`: `BlankSlate` (full height) — Icon: lock, text: "You don't have the necessary permission to see this screen.", sub-text: "Please contact your system administrator.", action (if not logged in): "Go to login" link → `Login`. `Header` placeholder: `UserInfo` block.

- **`UserProfile`** — requires login, layout `LayoutTopMenu` (`HasFixedHeader = True`, `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). Title: `"Your profile"`. Description: `"Screen where the users can see and edit the user profile."`.

  Screen aggregate: `GetUserDetails` (Source: User, Filter: `User.Id = GetUserId()`, MaxRecords: 1, Fetch: At Start). `OnAfterFetch` → `GetUserDetailsOnAfterFetch`.

  Local vars: `OldName` (Text), `OldEmail` (Email), `OldPhotoURL` (Text), `IsExternal` (Boolean), `VerificationCode` (Text), `ShowVerificationCode` (Boolean, False), `ShowGetCodeButton` (Boolean, False), `CountdownValue` (Integer), `TimerIntervalHandle` (JavaScript object), `IsButtonEnabled` (Boolean), `IntervalDuration` (Integer, 1000), `IsExecuting` (Boolean, False), `IsExecuting_GetCode` (Boolean, False).

  | Action | Trigger | Key logic |
  |---|---|---|
  | `OnInitialize` | Screen init | `IsExecuting = False`, `IsExecuting_GetCode = False`. Call `IsExternalUser()` → `IsExternal = IsExternalUser.IsExternalUser`. |
  | `GetUserDetailsOnAfterFetch` | `GetUserDetails.OnAfterFetch` | If `GetUserId() <> NullTextIdentifier()`: assign `OldName`, `OldPhotoURL`, `OldEmail` from `GetUserDetails.List.Current.User`. |
  | `ValidateUserDetails` | Called by change/save | Validates email (non-empty + valid format) + name (non-empty). If `ShowGetCodeButton and ShowVerificationCode`: validates `VerificationCode` non-empty. |
  | `ValidateInputsOnChange` | Input change events | `ShowGetCodeButton = (OldEmail <> User.Email and Email non-empty and valid)`. Calls `ValidateUserDetails` → `CheckIsButtonEnabled`. |
  | `CheckIsButtonEnabled` | Called by `ValidateInputsOnChange` | `IsButtonEnabled = True` if: (name or photo changed, email unchanged) OR (email changed + `ShowVerificationCode = True` + `Length(VerificationCode) = 6`). |
  | `SaveChangesOnClick` | "Save" button | (1) `IsExecuting = True`. (2) `ValidateUserDetails`. (3) If invalid: `IsExecuting = False`, end. (4) If email changed: `FinishUpdateEmail(VerificationCode)` — on `InvalidVerificationCode` set `VerificationCodeInput.Valid = False`. (5) Call `UpdateUser(mapTo{Name, PhotoURL})`. (6) Success: write `Client.UserName`, `Client.UserPhotoURL`; clear `VerificationCode`, `IsButtonEnabled`, `ShowVerificationCode`, `ShowGetCodeButton`; show success message; redirect to `UserProfile`. (7) Failure: show specific message per `UpdateUserFailureReason`; `IsExecuting = False`. AllExceptions handler: show `ExceptionMessage`, `IsExecuting = False`. |
  | `SendVerificationCode` | "Get verification code" button | If email unchanged: end. `IsExecuting_GetCode = True`. `ValidateUserDetails`. Call `SendChangeEmail(User.Email)`. Failure: `IsExecuting_GetCode = False`, show error. Success: show "A verification code was sent to your email"; `ShowVerificationCode = True`, `CountdownValue = 5`; run `JsSetInterval` JS node (`setInterval(() => { $actions.UpdateCountdown && $actions.UpdateCountdown(); }, $parameters.IntervalDuration)` → output: `TimerHandle`); `TimerIntervalHandle = JsSetInterval.TimerHandle`; `IsExecuting_GetCode = False`. AllExceptions handler: show `ExceptionMessage`, `IsExecuting_GetCode = False`. |
  | `UpdateCountdown` | Called by timer | Decrement `CountdownValue`. If `CountdownValue <= 0`: call `StopCountdown`. |
  | `StopCountdown` | Called by `UpdateCountdown`, `OnDestroy` | JS node: `if ($parameters.TimerHandle) { clearInterval($parameters.TimerHandle); }` (input: `TimerHandle` ← `TimerIntervalHandle`). |
  | `OnDestroy` | Screen destroy | Call `StopCountdown`. |

### 9. Server Actions

Folder structure: `Authentication` → `SendResetPasswordEmail`; `UserActions` → `SendChangeEmail`, `UpdateUser`.

**`SendResetPasswordEmail(ApplicationName: Text, CustomerEmail: Email)`** → `Success: Boolean`

```
Start → StartResetPassword(Email = CustomerEmail) [system]
  → If StartResetPassword.Success AND Length(VerificationCode) > 0:
      False → Assign: Success = True (security: don't reveal whether email exists) → End
      True  → Aggregate TryGetNameByEmail (User, Email = CustomerEmail, MaxRecords 1)
               → SendEmail: ResetPassword (To=CustomerEmail, CustomerEmail, VerificationCode, ApplicationName, CustomerName=TryGetNameByEmail.List.Current.User.Name)
               → Assign: Success = True → End
AllExceptions handler → Assign: Success = False → End
```

**`SendChangeEmail(ApplicationName: Text, CustomerEmail: Email)`** → `Success: Boolean`

```
Start → StartUpdateEmail(Email = CustomerEmail) [system]
  → If StartUpdateEmail.Success AND Length(VerificationCode) > 0:
      False → Assign: Success = False → End
      True  → Aggregate TryGetNameByEmail (User, Email = CustomerEmail, MaxRecords 1)
               → SendEmail: ChangeEmail (To=CustomerEmail, CustomerEmail, VerificationCode, ApplicationName, CustomerName)
               → Assign: Success = True → End
AllExceptions handler → Assign: Success = False → End
```

`SendChangeEmail` false branch returns `Success = False` (no fake success — only reachable by an authenticated user).

**`UpdateUser(UserUpdateInfo: UserUpdateInfo)`** → `UpdateUserResult: UpdateUserResult`

```
Start → UpdateUserProfile(UserUpdateInfo) [system] → Assign: UpdateUserResult = UpdateUserProfile.UpdateUserResult → End
```

No exception handler — exceptions propagate to the client action wrapper.

### 10. Client Actions

Folder structure: `Authentication` → `DoLogin`, `DoLogout`, `SendResetPasswordEmail`; `UserActions` → `SendChangeEmail`, `UpdateUser`.

**`DoLogin(Username: Text, Password: Text)`** → `Success: Boolean`, `ErrorMessage: Text`

```
Start → Login(Username, Password) [system]
  → If Login.UserLoginResult.Success:
      True  → Success = True → End
      False → If InvalidCredentials → ErrorMessage = "Invalid credentials." → End
               → If TooManyFailedLoginAttempts → ErrorMessage = "Too many failed login attempts. Please try again in " + RetryAfterSeconds + " seconds." → End
               → ErrorMessage = "Login operation failed." → End
```

**`DoLogout()`** → `RedirectURL: Text`

```
Start → If IsExternalUser():
    True  → GetExternalLogoutURL [system] → RedirectURL = GetExternalLogoutURL.ExternalLogoutURL → (merge)
    False → Logout [system] → RedirectURL = GetOwnerURLPath() → (merge)
→ Assign: Client.UserName = "", Client.UserPhotoURL = "", Client.LastURL = "" → End
```

Caller (`UserInfo.ClientLogout`) navigates to `RedirectURL` after this returns.

**`SendResetPasswordEmail(CustomerEmail: Email)`** → `Success: Boolean`

```
Start → Server SendResetPasswordEmail(ApplicationName = GetAppName(), CustomerEmail) → Success = SendResetPasswordEmail.Success → End
AllExceptions handler → Success = False → End
```

**`SendChangeEmail(CustomerEmail: Email)`** → `Success: Boolean`

```
Start → Server SendChangeEmail(ApplicationName = GetAppName(), CustomerEmail) → Success = SendChangeEmail.Success → End
AllExceptions handler → Success = False → End
```

**`UpdateUser(UserUpdateInfo: UserUpdateInfo)`** → `UpdateUserResult: UpdateUserResult`

```
Start → Server UpdateUser(UserUpdateInfo) → UpdateUserResult = UpdateUserProfile.UpdateUserResult → End
AllExceptions handler → UpdateUserResult.Success = False → End
```

### 11. Email Templates (in Emails flow)

Both templates share the same four input parameters (none mandatory): `ApplicationName` (Text), `CustomerName` (Text), `CustomerEmail` (Email), `VerificationCode` (Text).

- **`ResetPassword`** — Subject: `"Password Reset for " + ApplicationName`. Content: logo, personalized greeting, reset instructions, `VerificationCode` (heading2) + "expires in 1 hour", CTA button → `RecoverPasswordReset(VerificationCode, CustomerEmail)`, sign-off, copyright.
- **`ChangeEmail`** — Subject: `ApplicationName + ": verification code " + VerificationCode`. Content: same outer structure; email-change instructions; `VerificationCode` (heading2, centered); **no CTA button**; sign-off, copyright.

Templates inherit theme from the `Emails` flow — do not set explicit template-level theme.

### 12. External Sites (in Common flow)

- **`RedirectToURL`** — client-side URL redirect. Input: `URL` (Text).

### 13. App-Level Exception Handler

Create an `OnException` action on the Common flow. Register it as:
1. Common flow's `OnExceptionHandler` → `OnException`
2. App's `GlobalExceptionHandler` → `OnException`
3. App's `UseDefaultThemeExceptionHandler` = `False`

The "No Exception Handling" warning on the Common flow is **not** an expected baseline warning — it means this handler is missing. Do NOT classify it as accepted.

| Handler | AbortTransaction | LogError | Next node |
|---|---|---|---|
| `AllExceptions` | True | True | Message (Error): `"There was a problem. Please contact the administrator"` → End |
| `DatabaseException` | True | True | Message (Error): `"There was a problem with the database request. Please contact the administrator"` → End |
| `CommunicationException` | True | True | Message (Error): `"There was a problem communicating with the server. Please try again or contact your administrator"` → End |
| `SecurityException` | True | **False** | If `GetUserId() <> NullTextIdentifier()` → `InvalidPermissions`; else → Assign `Client.LastURL = GetBookmarkableURL()` → `Login` |
