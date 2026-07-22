# Common Blocks — Reference Widget Trees (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-23 via Mentor inspection.

---

## ApplicationTitle

**Input Parameters:** None

**Screen Actions:**
- `ApplicationNameOnClick` — Redirects to home via `RedirectToURL` passing `GetOwnerURLPath()`

**Widget Tree:**

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

---

## MenuIcon

**Input Parameters:** None

**Screen Actions:**
- `OnClick` — Calls `ToggleSideMenu` (OutSystemsUI)
- `OnReady` — Calls `SetMenuIconListeners` (OutSystemsUI); also bound to `OnParametersChanged`

**Widget Tree:**

```
[Container] (unnamed)
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

---

## Menu

**Input Parameters:**

| Name | Type | Default | Mandatory |
|---|---|---|---|
| `ActiveItem` | Integer | `-1` | No |
| `ActiveSubItem` | Integer | `-1` | No |

**Screen Actions:**
- `OnReady` — Calls `MenuReady`, then `SetActiveMenuItems(ActiveItem, ActiveSubItem)`; also bound to `OnRender` and `OnParametersChanged`
- `OnDestroy` — Calls `MenuDestroy`
- `HideMenu` — Calls `ToggleSideMenu`

**Widget Tree:**

```
[AdvancedHtml] (<nav> tag)
  Extended: class="app-menu-content display-flex", role="navigation", aria-label="Main navigation"
  │
  ├─ [Container] (unnamed)
  │    Style: "header-logo placeholder-empty"
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
  │    (no children)
  │
  └─ [Container] LoginInfo
       Style: "app-login-info placeholder-empty"
       Width: (fill parent)
       └─ [BlockInstance] (unnamed) → UserInfo (Common flow)
            (no parameter bindings)

[Container] (unnamed)
  Style: "app-menu-overlay"
  Width: (fill parent)
  Extended: role="button"
  Event: onclick → HideMenu
  (no children)
```

**Note:** The `header-logo` container with the always-false If + ApplicationTitle block is intentional — it's a structural slot that is permanently in the False/hidden state by design (Condition: `False`). The ApplicationTitle shown in the header comes from the layout blocks, not from Menu itself.

---

## UserInfo

**Input Parameters:** None

**Screen Actions:**
- `OnReady` — Calls `GetUsernameAndPhoto`
- `GetUsernameAndPhoto` — If `Client.UserName = "" and GetUserId() <> NullTextIdentifier()` (label: "No username?"):
  - True: Calls `GetUserProfile` (System), assigns `Client.UserName = GetUserProfile.UserInfo.Name`, `Client.UserPhotoURL = GetUserProfile.UserInfo.PhotoURL`
  - False: End
- `ClientLogout` — Calls `DoLogout`, then navigates to `RedirectToURL` passing `DoLogout.RedirectURL`

**Widget Tree:**

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
       │    ├─ [Container] (unnamed)
       │    │    Style: (none)
       │    │    Width: (fill parent)
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
       │    ├─ [Container] (unnamed)
       │    │    Style: "margin-left-s"
       │    │    Width: (fill parent)
       │    │    └─ [Link] (unnamed)
       │    │         Style: (none)
       │    │         Enabled: True
       │    │         OnClick: navigates to UserProfile screen (Transition: Inherited)
       │    │         └─ [Expression] (unnamed)
       │    │              Value: Client.UserName
       │    │              Example: "Username"
       │    │
       │    └─ [Container] (unnamed)
       │         Style: "margin-left-s"
       │         Width: (fill parent)
       │         └─ [Link] (unnamed)
       │              Style: (none)
       │              Width: (fill parent)
       │              Enabled: True
       │              OnClick: ClientLogout (Transition: Fade)
       │              ├─ [Icon] Icon3
       │              │    Icon: sign-out
       │              │    Size: FontSize
       │              │    Weight: regular
       │              │    Style: "icon"
       │              └─ [Text] (unnamed)
       │                   Text: "Log out"
       │                   Style: "margin-left-s wcag-hide-text"
       │
       └─ False branch:
            └─ [Link] (unnamed)
                 Style: (none)
                 Width: (fill parent)
                 Enabled: True
                 OnClick: navigates to Login screen (Transition: Fade)
                 ├─ [Icon] Icon4
                 │    Icon: sign-in
                 │    Size: FontSize
                 │    Weight: regular
                 │    Style: "icon"
                 └─ [Text] (unnamed)
                      Text: "Login"
                      Style: "margin-left-s"
```
