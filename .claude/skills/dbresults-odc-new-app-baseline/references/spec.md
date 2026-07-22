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

Widget tree — minimal shell; no header, skip-nav, or footer. One Placeholder (WebBlockZone), **never** a plain Container:

```
(unnamed root Container)
  Style: "layout blank"
         + If(not EnableAccessibilityFeatures, "", " has-accessible-features")
         + If(ExtendedClass = "", "", " " + ExtendedClass)
  │
  └── (unnamed Container)
        Style: "content"
        Extended props: role="main"
        └── Content  [Placeholder]
              Style: "main-content"
              EffectiveWidth: UserDefined
              (no default content)
```

> **Key notes:** CSS class is `"blank"` — not `"layout-blank"` (the root already has `"layout"` as first class). `not EnableAccessibilityFeatures` condition: adds `" has-accessible-features"` when the parameter is `True`. No `HasFixedHeader` parameter. The `Content` placeholder style is `"main-content"` (not `"content-middle"`).

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

Widget tree — create every widget in this exact structure. All content zones are `Placeholder` (WebBlockZone) widgets, **never** plain Containers:

```
LayoutWrapper  [Container]
  Style: "layout layout-side"
         + If(HasFixedHeader, " fixed-header", "")
         + " "
         + MenuBehavior
         + If(not EnableAccessibilityFeatures, "", " has-accessible-features")
         + If(ExtendedClass = "", "", " " + ExtendedClass)
  │
  ├── (unnamed Link)
  │     Style: "skip-nav", OnClick → SkipToContentOnClick
  │     Extended props:
  │       aria-label = "Skip to Content (Press Enter)"
  │       data-showskipcontent = If(EnableAccessibilityFeatures, "true", "false")
  │     └── (unnamed Text) — "Skip to Content (Press Enter)"
  │
  ├── (unnamed AdvancedHtml, Tag: aside)
  │     Extended props: role="complementary", class="aside-navigation"
  │     └── Navigation  [Placeholder]
  │           Style: (none)
  │           EffectiveWidth: UserDefined (fill parent)
  │           └── [WebBlock: Menu from Common]   (ActiveItem=null, ActiveSubItem=null)
  │
  └── (unnamed Container)
        Style: "main"
        │
        ├── Header3  [AdvancedHtml, Tag: header]
        │     Extended props: role="banner", class="header"
        │     └── (unnamed Container)
        │           Style: "header-top ThemeGrid_Container"
        │           └── (unnamed Container)
        │                 Style: "header-content display-flex"
        │                 ├── [WebBlock: MenuIcon from Common]   (no params)
        │                 ├── [WebBlock: ApplicationTitle from Common]   (no params)
        │                 └── Header  [Placeholder]
        │                       Style: "header-navigation"
        │                       EffectiveWidth: InlineBlock   ← NOT UserDefined
        │                       (empty — no default content)
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

> **Key differences from LayoutTopMenu:** adds an `<aside>` sidebar before "main" with a `Navigation` placeholder (default: Menu block); the `Header` placeholder has **no default content** (unlike LayoutTopMenu which has Menu as default); the skip-nav link is a direct child of `LayoutWrapper` (not inside the header AdvancedHtml).

#### LayoutBase

Parameters:

| Parameter | Type | Default (block def) | Value on every screen instance |
|---|---|---|---|
| `HasFixedHeader` | Boolean | `True` | `True` |
| `EnableAccessibilityFeatures` | Boolean | null (unset) | `False` |
| `ExtendedClass` | Text | `""` | `""` |

Client Actions: `OnInitialize`, `OnReady`, `OnDestroy`, `SkipToContentOnClick`.

Widget tree — create every widget in this exact structure. Content zones are `Placeholder` (WebBlockZone) widgets, **never** plain Containers:

```
LayoutWrapper  [Container]
  Style: "layout layout-blank"
         + If(HasFixedHeader, " fixed-header", "")
         + " "
         + If(not EnableAccessibilityFeatures, "", " has-accessible-features")
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
              └── MainContentWrapper  [Container]
                    Style: "main-content"   ← NO ThemeGrid_Container (unlike LayoutTopMenu/SideMenu)
                    Extended props: role="main"
                    └── MainContent  [Placeholder]
                          Style: "content-middle"
                          EffectiveWidth: UserDefined
                          └── [WebBlock: LayoutBaseSection from Layouts]   (all params null)
```

> **Key differences from LayoutTopMenu:** CSS class is `layout-blank` not `layout-top`; `MainContentWrapper` has **no** `ThemeGrid_Container` class; only 2 placeholders (`Header` + `MainContent`) — no `Breadcrumbs`, `Title`, `Actions`, or `Footer`; `MainContent` default content is a `LayoutBaseSection` block instance.

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
| `ApplicationNameOnClick` | onclick on wrapper container | Navigates to `RedirectToURL` with `GetOwnerURLPath()`. |

**Widget tree:**

```
[Container] ApplicationTitleWrapper
  Style: "application-name display-flex align-items-center full-height"
  Width: (fill parent)
  Extended: role="button", tabindex="0"
  Event: onclick → ApplicationNameOnClick
  │
  ├─ [Image] AppLogo
  │    Type: Static (local image: Logo)
  │    Style: "app-logo"
  │    CustomStyle: "height: 32px;"
  │    Extended: alt=""
  │
  └─ [Expression] (unnamed)
       Value: GetAppName()
       Example: "Application Title"
```

**Key:** Root is a Container with an `onclick` event — NOT a Link widget. App name is an Expression using `GetAppName()` — NOT a literal Text widget.

---

#### MenuIcon

No input parameters.

| Client Action | Trigger | Logic |
|---|---|---|
| `OnReady` | After first render + on parameter change | Calls `SetMenuIconListeners`. |
| `OnClick` | onclick on container | Calls `ToggleSideMenu`. |

**Widget tree:**

```
[Container] MenuIconContainer
  Style: "menu-icon"
  Width: (fill parent)
  Extended: aria-label="Toggle the Menu", role="button", tabindex="0", aria-haspopup="true"
  Event: onclick → OnClick
  │
  └─ [Icon] (unnamed)
       Icon: list
       Size: 2x
       Weight: regular
       Style: "icon"
       Extended: aria-hidden="true"
```

**Key:** Child is an Icon widget (icon=`list`, 2x, regular) — NOT a Text widget with a hamburger character. Container needs all 4 ARIA extended properties.

---

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

**Widget tree:**

```
[AdvancedHtml] (unnamed)  Tag: nav
  Extended: class="app-menu-content display-flex", role="navigation", aria-label="Main navigation"
  │
  ├─ [Container] (unnamed)  Style: "header-logo placeholder-empty"
  │    Width: (fill parent)
  │    └─ [If] (unnamed)
  │         Condition: False
  │         DesignMode: ShowFalse
  │         True branch: (empty)
  │         False branch:
  │           └─ [BlockInstance] (unnamed) → ApplicationTitle (Common flow)
  │                (no parameter bindings)
  │
  ├─ [Container] PageLinks
  │    Style: "app-menu-links"
  │    Width: (fill parent)
  │    Extended: role="menubar"
  │    (no children — navigation links added by later skills)
  │
  └─ [Container] LoginInfo
       Style: "app-login-info placeholder-empty"
       Width: (fill parent)
       └─ [BlockInstance] (unnamed) → UserInfo (Common flow)
            (no parameter bindings)

[Container] MenuOverlay  (sibling of the nav, NOT a child)
  Style: "app-menu-overlay"
  Width: (fill parent)
  Extended: role="button"
  Event: onclick → HideMenu
  (no children)
```

**Key:** Root is an `AdvancedHtml <nav>` — NOT a Container. The `header-logo` container with Always-False If + ApplicationTitle block is a structural slot that stays hidden at runtime by design. `LoginInfo` style is `"app-login-info placeholder-empty"` — NOT `"login-info"`. `MenuOverlay` style is `"app-menu-overlay"` — NOT `"menu-overlay"`.

---

#### UserInfo

No input parameters.

| Client Action | Trigger | Logic |
|---|---|---|
| `OnReady` | After first render | Calls `GetUsernameAndPhoto`. |
| `GetUsernameAndPhoto` | Called by `OnReady` | If `Client.UserName = "" and GetUserId() <> NullTextIdentifier()` (label: "No username?"): True → calls `GetUserProfile` (System), assigns `Client.UserName = GetUserProfile.UserInfo.Name`, `Client.UserPhotoURL = GetUserProfile.UserInfo.PhotoURL`. False → End. |
| `ClientLogout` | Logout link click | Calls `DoLogout` → navigates to `RedirectToURL` with `URL = DoLogout.RedirectURL` (Fade). |

**Widget tree:**

```
[Container] (unnamed)
  Style: "user-info"
  Width: (fill parent)
  │
  └─ [If] UserIsLogged
       Condition: GetUserId() <> NullTextIdentifier()
       DesignMode: ShowAll
       │
       ├─ True branch:
       │    ├─ [Container] (unnamed)  Style: (none)  Width: (fill parent)
       │    │    └─ [If] HasPhotoURL
       │    │         Condition: Client.UserPhotoURL <> ""
       │    │         DesignMode: ShowAll
       │    │         True branch:
       │    │           └─ [Image] (unnamed)
       │    │                Type: External (URL)
       │    │                URL: Client.UserPhotoURL
       │    │                Style: "avatar avatar-small border-radius-rounded"
       │    │                Extended: title=Client.UserName, alt="User photo"
       │    │         False branch:
       │    │           └─ [BlockInstance] userAvatarInstance → UserAvatar (OutSystemsUI / Content flow)
       │    │                Size = Entities.Size.Small
       │    │                Name = Client.UserName
       │    │                (Shape, Color, IsLight, Image, ExtendedClass = null/default)
       │    │
       │    ├─ [Container] (unnamed)  Style: "margin-left-s"  Width: (fill parent)
       │    │    └─ [Link] (unnamed)
       │    │         Style: (none)  Enabled: True  Transition: Inherited
       │    │         OnClick: navigates to UserProfile screen
       │    │         └─ [Expression] (unnamed)
       │    │              Value: Client.UserName
       │    │              Example: "Username"
       │    │
       │    └─ [Container] (unnamed)  Style: "margin-left-s"  Width: (fill parent)
       │         └─ [Link] (unnamed)
       │              Style: (none)  Width: (fill parent)  Enabled: True  Transition: Fade
       │              OnClick: ClientLogout screen action
       │              ├─ [Icon] Icon3
       │              │    Icon: sign-out  Size: FontSize  Weight: regular  Style: "icon"
       │              └─ [Text] (unnamed)
       │                   Text: "Log out"
       │                   Style: "margin-left-s wcag-hide-text"
       │
       └─ False branch:
            └─ [Link] (unnamed)
                 Style: (none)  Width: (fill parent)  Enabled: True  Transition: Fade
                 OnClick: navigates to Login screen
                 ├─ [Icon] Icon4
                 │    Icon: sign-in  Size: FontSize  Weight: regular  Style: "icon"
                 └─ [Text] (unnamed)
                      Text: "Login"
                      Style: "margin-left-s"
```

**Key:** Root child is `UserIsLogged` If widget (not a flat list of widgets). Username is an Expression inside a Link → UserProfile (not a plain Text). Logout text is `"Log out"` (two words) with style `"margin-left-s wcag-hide-text"`. The False branch shows a Login link for unauthenticated users.

### 8. Screens (in Common flow)

All 6 screens carry the `{App}` role — including the 4 anonymous-access screens. `AnonymousAccess = true` overrides the role check at runtime; the role attachment is harmless and matches the reference implementation. **Do NOT remove the role from any screen.**

Every screen's layout block instance must have all parameter arguments explicitly set (see section 6 call-site rule).

- **`Login`** — `AnonymousAccess = true`, layout `LayoutBlank` (`EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). Title: `"Log in"` (two words, with space). **Not the default screen.**

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

  **Layout** (widget tree inside `LayoutBlank`'s `Content` placeholder, in order):

  - Container `"login-screen"` → Form `LoginForm` `"login-form"`:

    **A — Logo + title** (`"login-logo"`, `CustomStyle: text-align: center`):
    - Container (`CustomStyle: text-align: center`) → Image `Logo` (`CustomStyle: height: 100px`, `alt=""`)
    - AdvancedHtml tag `h1` (extended property `class="margin-y-base"`) → Expression `GetAppName()` (Style `"heading5 text-neutral-8"`, Example `"Application Title"`)

    **B — `BuiltInProvider` If** (`Condition: ShowBuiltInProvider`, `DesignMode: ShowAll`), True branch:

    - Container `"login-inputs"`:
      - Container (no style) → `AnimatedLabelInstance` (`AnimatedLabel` block, OutSystemsUI Interaction):
        - Label placeholder: Label (Target `Input_UsernameVal`) → Text `"Login"`
        - Input placeholder: Input `Input_UsernameVal` (`"form-control"`, InputType **Text**, Variable `UserEmail`, Enabled `ExecutingIndex = -1 and not IsBuiltInExecuting`, Mandatory True, MaxLength 250, tabindex=1)
      - Container `"margin-top-base"` → `AnimatedLabelInstance2` (`AnimatedLabel` block):
        - Label placeholder: Label (Target `Input_Password`) → Text `"Password"`
        - Input placeholder: `InputWithIconInstance` (`InputWithIcon` block, `AlignIconRight = True`):
          - Icon placeholder: Link (OnClick `OnTogglePasswordVisibility`) → If `PasswordVisibile` (`Condition: IsPasswordVisible`, `DesignMode: ShowTrueOrPreview`):
            - True: Icon `eye-slash`, regular, Style `"icon"`, FontSize
            - False: Icon `eye`, regular, Style `"icon"`, FontSize
          - Input placeholder: Input `Input_Password` (Style `"form-control login-password"`, CustomStyle `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;`, InputType Password, Variable `Password`, Enabled `ExecutingIndex = -1 and not IsBuiltInExecuting`, Mandatory True, **MaxLength: null (no limit)**, tabindex=2)
      - Container `"margin-top-l"` → Container (`CustomStyle: text-align: right`) → Link (OnClick → navigate `RecoverPasswordRequest`, tabindex=3, aria-label `"Forgot your password? Click here to recover it"`) → Text `"Forgot your password?"`
    - Container `"login-button margin-top-l"` → `ButtonLoadingInstance` (`ButtonLoading` block, `IsLoading = IsBuiltInExecuting`, `ExtendedClass = "full-width"`):
      - Button placeholder: Button (`"btn btn-primary"`, IsDefault/IsSubmit **True**, Enabled `ExecutingIndex = -1`, OnClick `LoginOnClick` ValidateAndContinue, tabindex=4) → Container `"osui-btn-loading__spinner-animation"` + Text `"Log in"`

    **C — `Separator` If** (`Condition: ShowBuiltInProvider and ShowExternalProvider`, `DesignMode: ShowAll`), True branch:
    - Container `"display-flex justify-content-center align-items-center"`:
      - Container `"full-width"` → `SeparatorInstance` (`Separator` block, all params null)
      - Text `"or"` (Style `"position-absolute padding-x-s background-neutral-0 text-neutral-8-darker font-semi-bold"`)

    **D — `ExternalProviders` If** (`Condition: ShowExternalProvider`, `DesignMode: ShowAll`), True branch:
    - List `ListProviders` (`"list list-group"`, Source `ExternalIdentityProviders`, Tag `div`, AnimateItems True):
      - Container `"margin-bottom-s"` → `ButtonLoadingInstance2` (`ButtonLoading` block, `IsLoading = ExecutingIndex = ExternalIdentityProviders.CurrentRowNumber`, `ShowLabelOnLoading = False`, `ExtendedClass = "full-width"`):
        - Button placeholder: Button (`"btn"`, IsDefault False, Enabled `ExecutingIndex = -1 and not IsBuiltInExecuting`, OnClick `LoginProviderOnClick` with `ProviderIndex = ExternalIdentityProviders.CurrentRowNumber`, `ProviderKey = ExternalIdentityProviders.Current.Key`, tabindex=5) → Container `"osui-btn-loading__spinner-animation"` + Text `"Continue with "` + Expression `ExternalIdentityProviders.Current.Name` (Example `"Apple"`)

  **Validator note:** `Input_UsernameVal` InputType is Text even though `UserEmail` is an Email-typed variable — this produces an "Input Type Mismatch" warning that is expected and acceptable; the reference app uses the same pattern.

- **`RecoverPasswordRequest`** — `AnonymousAccess = true`, layout `LayoutBlank`. Local vars: `IsExecuting` (Boolean, False), `Email` (Email).

  | Action | Trigger | Logic |
  |---|---|---|
  | `ResetPasswordOnClick` | "Reset password" button | (1) If `RecoverPasswordForm.Valid` false → end. (2) `IsExecuting = True`. (3) Call `SendResetPasswordEmail(CustomerEmail = Email)`. (4) Success → `IsExecuting = False` → navigate to `RecoverPasswordReset(Email = Email)` (VerificationCode NOT passed). (5) Failure → show `"An error has occured. Please try again later."` (typo preserved), `IsExecuting = False`. **No `AllExceptions` handler.** |

  **Layout** (widget tree inside `LayoutBlank`'s `Content` placeholder, in order):

  - Container `"login-screen"` → Form `RecoverPasswordForm` `"login-form"`:

    **A — Logo + title** (`"login-logo"`, `CustomStyle: text-align: center`):
    - Container (`CustomStyle: text-align: center`) → Image `Logo` (`CustomStyle: height: 100px`, `alt=""`)
    - AdvancedHtml tag `h5` (extended property `class="margin-top-base text-neutral-8"`) → Text `"Forgot your password?"`
    - Container `"margin-top-s"` → Container → Text `"Don't worry, we'll send you an email with instructions."`

    **B — Email input** (`"login-inputs margin-top-m"`):
    - AnimatedLabel block (OutSystemsUI):
      - Label placeholder: Label (Target `Input_Email`) → Text `"Email"`
      - Input placeholder: Input `Input_Email` (`"form-control"`, InputType Email, Variable `Email`, Mandatory True, MaxLength 250, Enabled True, tabindex=1)

    **C — Submit button** (`"login-button margin-top-l"`):
    - ButtonLoading block (`IsLoading = IsExecuting`, `ExtendedClass = "full-width"`):
      - Button placeholder: Button (`"btn btn-primary"`, IsDefault True, Enabled True, OnClick `ResetPasswordOnClick` ValidateAndContinue, tabindex=2) → Container `"osui-btn-loading__spinner-animation"` + Text `"Reset password"` (lowercase p)

    **D — Footer** (`"margin-top-m"`, `CustomStyle: text-align: center`):
    - Text `"Not in the right place?"`
    - Link (OnClick → navigate `Login`, no validation, tabindex=3, aria-label `"Go to login page"`) → Text `"Go to login."`

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

  **Layout** (widget tree inside `LayoutBlank`'s `Content` placeholder, in order):

  - Container `"login-screen"` → Form `PasswordResetForm` `"login-form"` (Width `""`):

    **A — Logo + title** (`"login-logo"`, `CustomStyle: text-align: center`):
    - Container (`CustomStyle: text-align: center`) → Image `Logo` (`CustomStyle: height: 100px`, `alt=""`)
    - AdvancedHtml tag `h5` (extended property `class="margin-top-base text-neutral-8"`) → Text `"Reset password"`
    - Container `"margin-top-s"` → Container → Text `"If the entered email is correct, we'll send a verification code to that email. Please enter the code below to verify your identity."`

    **B — Fields** (outer Container, no style):

    - **B1 — Email (read-only)** (`"login-inputs margin-top-m"`): AnimatedLabel block:
      - Label placeholder: Label (Target `Input_Email`) → Text `"Email"`
      - Input placeholder: Input `Input_Email` (`"form-control"`, InputType Email, Variable `Email`, Mandatory True, MaxLength 250, **Enabled False**, Placeholder `"mary.smith@acme.com"`, no tabindex)

    - **B2 — Verification code** (`"login-inputs margin-top-m"`): AnimatedLabel block:
      - Label placeholder: Label (Target `Input_Code`) → Text `"Verification code"`
      - Input placeholder: Input `Input_Code` (`"form-control"`, InputType Text, Variable `VerificationCode` (the screen's input parameter), Mandatory True, no MaxLength, Enabled True, OnChange `Input_CodeOnChange`, tabindex=1)

    - **B3 — New password** (`"margin-top-base password-input"`): AnimatedLabel block:
      - Label placeholder: Label (Target `Input_NewPassword`) → Text `"New password"`
      - Input placeholder: InputWithIcon block (`AlignIconRight = True`):
        - Icon placeholder: Link (**no validation**, OnClick `OnToggleNewPasswordVisibility`) → If `"PasswordVisibile"` (Condition `IsPasswordVisible`, ShowTrueOrPreview): True → Icon (eye-slash, `"icon"`, FontSize) / False → Icon (eye, `"icon"`, FontSize)
        - Input placeholder: Input `Input_NewPassword` (`"form-control login-password"`, CustomStyle `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;`, InputType Password, Variable `NewPassword`, Mandatory True, MaxLength 256, Enabled True, tabindex=2)

    - **B4 — PasswordPolicy block**: BlockInstance `PasswordPolicy` (`Password → NewPassword`, `Compliant → PasswordPolicyCompliant` (event), `IsValid → IsValid`)

    - **B5 — Confirm password** (`"margin-top-base password-input"`): AnimatedLabel block:
      - Label placeholder: Label (Target `Input_ConfirmPassword`) → Text `"Confirm password"`
      - Input placeholder: InputWithIcon block (`AlignIconRight = True`):
        - Icon placeholder: Link (**no validation**, OnClick `OnToggleConfirmPasswordVisibility`) → If `"ConfirmPasswordVisibile"` (Condition `IsConfirmPasswordVisible`, ShowTrueOrPreview): True → Icon (eye-slash, `"icon"`, FontSize) / False → Icon (eye, `"icon"`, FontSize)
        - Input placeholder: Input `Input_ConfirmPassword` (`"form-control login-password"`, CustomStyle `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;`, InputType Password, Variable `ConfirmPassword`, Mandatory True, MaxLength 256, Enabled True, OnChange `Input_ConfirmPasswordOnChange`, tabindex=3)

    **C — Submit button** (`"login-button margin-top-l"`):
    - ButtonLoading block (`IsLoading = IsExecuting`, `ExtendedClass = "full-width"`):
      - Button placeholder: Button (`"btn btn-primary"`, IsDefault True, Enabled `IsButtonEnabled`, OnClick `SavePasswordOnClick` ValidateAndContinue, tabindex=4) → Container `"osui-btn-loading__spinner-animation"` + Text `"Save password"` (lowercase p)

    **D — Footer** (`"margin-top-m"`, `CustomStyle: text-align: center`):
    - Text `"Not in the right place?"`
    - Link (OnClick → navigate `Login`, no validation, tabindex=5, aria-label `"Go to login page"`) → Text `"Go to login."`

  **Key builder notes:**
  - Form name is `PasswordResetForm` (not `RecoverPasswordForm`)
  - `Input_Code` binds to the `VerificationCode` input parameter (not a local variable named `Code`)
  - `Input_Email` is `Enabled = False` — it shows the pre-filled email read-only
  - Toggle Links must have **no validation** — eye icons only toggle visibility, they must not fire form validation
  - Button `Enabled = IsButtonEnabled` (not `True`, not `IsButtonEnabled and not IsExecuting` — ButtonLoading handles the loading state display)

- **`ChangePassword`** — requires login, layout `LayoutTopMenu` (`HasFixedHeader = True`, `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). **No screen aggregates.**

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
  | `SetNewPasswordOnClick` | "Set new password" button | (1) If `Form.Valid` false → end. (2) `IsExecuting = True`. (3) If `NewPassword ≠ ConfirmPassword` → `Input_ConfirmPassword.Valid = False`, `ValidationMessage = "Password and Confirm password don't match."`, `IsExecuting = False` → end. (4) Call `GetUserProfile` (system) → Call system `ChangePassword(OldPassword, NewPassword, Username = GetUserProfile.UserInfo.Email)`. (5) Success → show `"Password successfully changed!"` → navigate to `UserProfile`. `InvalidCredentials`: mark `Input_OldPassword.Valid = False`. `PasswordComplexityPolicyFailed`: `Input_NewPassword.Valid = False`, `IsButtonEnabled = False`. `TooManyFailedAttempts`: show timeout message. Other: show unknown error. **No `AllExceptions` handler.** |

  **Layout** (LayoutTopMenu placeholders):

  - **Header placeholder:** `Menu` block instance directly in Header (no wrapper container). `ActiveItem` and `ActiveSubItem`: **not set** (leave both parameters unbound — do NOT bind to `-1`).

  - **Breadcrumbs:** Link (→ UserProfile, no validation) → Icon (caret-left, `"icon"`, FontSize, regular) + Text `"Back to profile"` (CustomStyle: `margin-left: 5px;`)

  - **Title:** Text `"Change your password"`

  - **MainContent:** Columns2 block (all params null) → Column1 → Form `Form` `"form card"`:

    **Child 1** (Container, no style) → AnimatedLabel block:
    - Label placeholder: Label (Target `Input_OldPassword`) → Text `"Current password"`
    - Input placeholder: Input `Input_OldPassword` (`"form-control"`, Password, `OldPassword`, Mandatory True, MaxLength 256, Enabled True, OnChange `Input_OldPasswordOnChange`, autocomplete=`"current-password"`, tabindex=1)

    **Child 2** (Container `"margin-top-base"`) → AnimatedLabel block:
    - Label placeholder: Label (Target `Input_NewPassword`) → Text `"New password"`
    - Input placeholder: InputWithIcon block (`ExtendedClass = "padding-left-none"`, `AlignIconRight = True`):
      - Icon placeholder: Link (no validation, OnClick `OnToggleNewPasswordVisibility`) → If `"PasswordVisible"` (Condition `IsPasswordVisible`, ShowTrueOrPreview): True → Icon (eye-slash, `"icon"`, FontSize, regular) / False → Icon (eye, `"icon"`, FontSize, regular)
      - Input placeholder: Input `Input_NewPassword` (`"form-control login-password padding-left-none"`, CustomStyle `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;`, Password, `NewPassword`, Mandatory True, MaxLength 256, Enabled True, autocomplete=`"new-password"`, tabindex=2)

    **Child 3** — PasswordPolicy block (`Password → NewPassword`, `Compliant → PasswordPolicyCompliant` event, `IsValid → IsValid`)

    **Child 4** (Container `"margin-top-base"`) → AnimatedLabel block:
    - Label placeholder: Label (Target `Input_ConfirmPassword`) → Text `"Confirm password"`
    - Input placeholder: InputWithIcon block (`ExtendedClass = "padding-left-none"`, `AlignIconRight = True`):
      - Icon placeholder: Link (no validation, OnClick `OnToggleConfirmPasswordVisibility`) → If `"PasswordVisible2"` (Condition **`IsPasswordVisible`** — same var as new password field, matches reference), ShowTrueOrPreview): True → Icon (eye-slash) / False → Icon (eye)
      - Input placeholder: Input `Input_ConfirmPassword` (same style + CustomStyle as NewPassword, Password, `ConfirmPassword`, Mandatory True, MaxLength 256, Enabled True, OnChange `Input_ConfirmPasswordOnChange`, tabindex=3)

    **Child 5** (Container, no style) → ButtonLoading block (`IsLoading = IsExecuting`, `ExtendedClass = "full-width"`):
    - Button placeholder: Button (`"btn btn-primary margin-top-l"`, IsDefault True, Enabled `IsButtonEnabled`, OnClick `SetNewPasswordOnClick` ValidateAndContinue, tabindex=4) → Container `"osui-btn-loading__spinner-animation"` + Text `"Set new password"` (lowercase n)

- **`InvalidPermissions`** — `AnonymousAccess = true`, layout `LayoutTopMenu` (`HasFixedHeader = True`, `EnableAccessibilityFeatures = False`, `ExtendedClass = ""`). No local vars, no aggregates, no screen actions.

  **Header placeholder:** Container (unnamed, `"full-height display-flex align-items-center justify-content-flex-end"`, fill parent) → `UserInfo` block only. **No Menu block. Do NOT name this container** (e.g. "MenuPlaceholder") — it must remain unnamed.

  **MainContent:** `BlankSlate` block (`FullHeight = True`, `ExtendedClass = null/default`):
  - **Icon placeholder:** Icon (`lock`, weight `regular`, size `FontSize`, style `"icon text-neutral-4"`)
  - **Content placeholder:**
    - Container (no style, fill parent) → Text `"You don't have the necessary permission to see this screen."` (style `"heading6"`)
    - Container (style `"margin-top-s"`, fill parent) → Text `"Please contact your system administrator."` (no style)
  - **Actions placeholder:** If `NotRegistered` (Condition: `GetUserId() = NullTextIdentifier()`, `ShowTrueOrPreview = True`):
    - True branch: Link (no style, no validation, OnClick → `Login`, Extended property `tabindex = 1`) → Text `"Go to login"`

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

  **Layout (UserProfile widget tree):**

  - **Header placeholder:** `Menu` block instance directly in Header (no wrapper container). Params unset.
  - **Title placeholder:** Text `"Your profile"` (no style).
  - **Actions placeholder:** If (unnamed, Condition: `IsExternal`, DesignMode: ShowFalse) / False branch: Link (unnamed, no style, no validation, OnClick → `ChangePassword`) → Text `"Change your password"`.
  - **MainContent placeholder:** Form `ProfileDetailsForm` (`"form card"`, fill parent) → `Columns2` block (unnamed, `PhoneBehavior = Entities.BreakColumns.All`, all others unset) → **Column1** (Column2 empty):

    1. **divName** (`"margin-top-base"`) → `AnimatedLabel` (unnamed, ExtendedClass unset):
       - Label: `NameLabel` → `NameInput`, Text `"Name"`
       - Input: `NameInput` (Text, `GetUserDetails.List.Current.User.Name`, `Enabled = not IsExternal`, Mandatory: True, MaxLength: null/unset, `"form-control"`, `OnChange → ValidateInputsOnChange` no validation)

    2. **divEmail** (`"margin-top-base"`) → `AnimatedLabel` (unnamed):
       - Label: (unnamed) → `EmailInput`, Text `"Email"`
       - Input: `EmailInput` (Email, `GetUserDetails.List.Current.User.Email`, `Enabled = not IsExternal`, Mandatory: True, MaxLength: 256, `"form-control"`, `OnChange → ValidateInputsOnChange` no validation, Extended: `autocomplete = "new-password"`)

    3. **If `If_ShowGetCodeButton`** (Condition: `ShowGetCodeButton`, ShowAll):
       - True → **If `If_ShowVerificationCode`** (Condition: `ShowVerificationCode`, ShowAll):
         - True → `Columns2` (unnamed, `ExtendedClass = "align-items-center"`, `PhoneBehavior = BreakColumns.All`, `GutterSize = Entities.GutterSize.None`):
           - **Column1:** Container `divVerificationCode` (`"padding-right-base"`, CustomStyle `"text-align: left;"`) → `AnimatedLabel` (unnamed):
             - Label: (unnamed) → `VerificationCodeInput`, Text `"Verification code"`
             - Input: `VerificationCodeInput` (Text, `VerificationCode`, Enabled: True, Mandatory: `ShowGetCodeButton`, MaxLength: 6, `"form-control"`, `OnChange → ValidateInputsOnChange` no validation, Extended: `autocomplete = "new-validationcode"`)
           - **Column2:** Link (unnamed, `Enabled = CountdownValue <= 0`, no style, CustomStyle `"margin-bottom: 0px;"`, `OnClick → SendVerificationCode` no validation) → If `If_HaveRemainingTime` (Condition: `CountdownValue > 0`, ShowAll): True: Expression `"Didn't get it? Resend in " + CountdownValue + "s"` / False: Expression `"Resend verification code"`
         - False → Container `DivGetVerificationCode` (no style) → `ButtonLoading` (unnamed, `IsLoading = IsExecuting_GetCode`, `ShowLabelOnLoading = True`) → Button placeholder: Button (unnamed, `"btn btn-small"`, IsDefault: False, `Enabled = ShowGetCodeButton and not ShowVerificationCode`, fill parent, `OnClick → SendVerificationCode` ValidateAndContinue) → spinner container + Text `"Get verification code"`
       - False → (empty)

    4. **If `If_ExternalUser`** (Condition: `IsExternal`, ShowAll):
       - True → (empty)
       - False → Container `divSaveChanges` (`"margin-top-base"`) → `ButtonLoading` `btnSaveChanges` (`IsLoading = IsExecuting`, `ShowLabelOnLoading = True`) → Button placeholder: Button `btnSave` (`"btn btn-primary"`, IsDefault: False, `Enabled = IsButtonEnabled`, fill parent, `OnClick → SaveChangesOnClick` ValidateAndContinue) → spinner container + Text `"Save changes"`

  **Note:** Reference also has `divPhoto` (photo display with `HasPhotoUrl` If/Images) and `divPhotoURL` (AnimatedLabel → `PhotoUrlInput`, MaxLength 2048, autocomplete `"new-photourl"`) between divName and divEmail. Omit these on tenants where `User.PhotoUrl` does not exist. In the reference they sit between `divName` and `divEmail` in Column1.

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

Both templates share the same four input parameters — **all mandatory**: `ApplicationName` (Text), `CustomerName` (Text), `CustomerEmail` (Email), `VerificationCode` (Text).

Templates inherit theme from the `Emails` flow — do not set explicit template-level theme.

Both templates use the same outer container structure:

```
Container "EmailWrapper"  Style: "email-max-width margin-auto"  Width: fill parent
  └─ Container "Email"  Style: "background-neutral-2 padding-l"  Width: fill parent
       ├─ Container "Content"  Style: "background-neutral-0 padding-l border-radius-medium"  Width: fill parent
       │   ├─ Container "Logo"  Style: "email-logo text-align-left"
       │   │   ├─ Image (unnamed)  Type: Static  Source: Logo  Extended: alt="Company Logo"
       │   │   └─ Expression (unnamed)  Value: ApplicationName  Example: "App name"
       │   ├─ Container "Title"  Style: "margin-bottom-base heading5"  CustomStyle: "text-align: left;"
       │   │   └─ If (unnamed)  Condition: CustomerName <> ""  DesignMode: ShowTrueOrPreview
       │   │        True:  Expression "Hi " + CustomerName + "!"  Example: "Hi, John Smith!"
       │   │        False: Text "Hi!"
       │   ├─ Container "Message"  Style: "margin-bottom-m"
       │   │   └─ Text [template-specific body copy — see below]
       │   ├─ Container (unnamed)  Style: "margin-bottom-m"
       │   │   ├─ Container (unnamed)  Style: "heading2 margin-bottom-s"  [CustomStyle — see below]
       │   │   │   └─ Expression (unnamed)  Value: VerificationCode  [Example — see below]
       │   │   └─ Container (unnamed)  Style: "font-size-xs text-neutral-7"  [CustomStyle — see below]
       │   │       └─ Text "This verification code expires in 1 hour"
       │   ├─ [ResetPassword only — CTA block, see below]
       │   ├─ Container "Instructions"  Style: (none)
       │   │   └─ Container (unnamed)  Style: "margin-bottom-m"
       │   │       └─ Text [template-specific instructions copy — see below]
       │   ├─ Container (unnamed)  Style: (none)
       │   │   └─ Text [template-specific sign-off — see below]
       │   ├─ Container (unnamed)  Style: "email-separator"
       │   └─ Container "Copyright"  Style: "font-size-xs text-neutral-7"
       │       ├─ Text "© "
       │       ├─ Expression  Value: Year(CurrDate())
       │       ├─ Text " "
       │       ├─ Expression  Value: ApplicationName  Example: "App name"
       │       └─ Text ". All Rights Reserved."
       └─ Container "Footer"  Style: "margin-top-m"
```

**`ResetPassword`** — Subject: `"Password Reset for " + ApplicationName`

Template-specific values:
- **Message body:** `"You're receiving this e-mail because you requested a password reset for your user account. To set a new password, use the button below or insert the following verification code in the reset password page. "`
- **VerificationCode block:** heading2 container no CustomStyle; Example: `"yAlFws8Fs3NwIlvc"`; expiry container no CustomStyle
- **CTA block** (between VerificationCode block and Instructions):
  ```
  Container (unnamed)  Style: "margin-bottom-base"
    └─ Container (unnamed)  Style: "margin-bottom-m"
         └─ Link (unnamed)  Style: (none)  Enabled: True
              OnClick: navigate RecoverPasswordReset
                VerificationCode ← VerificationCode
                Email ← CustomerEmail
              └─ Container (unnamed)  Style: "btn btn-primary"
                   └─ Text "Reset password"  (lowercase p)
  ```
- **Instructions:** `"If you don't want to change your password or didn't request this,\nyou can safely disregard this email."`
- **Sign-off:** `"Thanks,\nAdmin"`

**`ChangeEmail`** — Subject: `ApplicationName + ": verification code " + VerificationCode`

Template-specific values:
- **Message body:** `"To complete your request to update the email address, please use the following verification code:"`
- **VerificationCode block:** heading2 container CustomStyle `"text-align: center;"`; Example: `"8475"`; expiry container CustomStyle `"text-align: center;"`
- **No CTA block**
- **Instructions:** `"If you don't want to change your email or didn't request this, you can safely disregard this email."`
- **Sign-off:** `"Thank you,\nAdmin"`
- **If widget name:** `"IF_HasCustomerName"` (ResetPassword's If is unnamed)

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
