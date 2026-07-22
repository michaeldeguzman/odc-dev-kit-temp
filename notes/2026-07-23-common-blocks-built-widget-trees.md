# Common Blocks — Built Widget Trees (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

## ApplicationTitle

**Input Parameters:** None

**Screen Actions:**
- `ApplicationNameOnClick` — Navigates to app root URL via JavaScript (`window.location.href = GetOwnerURLPath();`)

**Widget Tree:**

```
[Link] AppTitleLink                                      ← BUG #1: should be Container "ApplicationTitleWrapper"
  Style: "app-name"                                     ← BUG #2: should be "application-name display-flex align-items-center full-height"
  OnClick → ApplicationNameOnClick
  (missing Extended: role="button", tabindex="0")       ← BUG #3
  │
  ├─ [Text] (unnamed)  Text: "link"                    ← BUG #4: stray default text node
  └─ [Text] AppTitleText  Text: "Application Name"     ← BUG #5: literal string; should be Expression GetAppName()
                                                        ← BUG #6: missing AppLogo Image entirely
```

---

## MenuIcon

**Input Parameters:** None

**Screen Actions:**
- `OnReady` — Calls `OutSystemsUI.SetMenuIconListeners`
- `OnClick` — Calls `OutSystemsUI.ToggleSideMenu`

**Widget Tree:**

```
[Container] MenuIconContainer
  Style: "menu-icon"
  Width: (fill parent)
  Event: click → OnClick
  (missing Extended: aria-label, role, tabindex, aria-haspopup)  ← BUG #1
  │
  └─ [Text] MenuIconText  Text: "☰"                   ← BUG #2: should be Icon widget (list, 2x, regular, style="icon", aria-hidden="true")
```

---

## Menu

**Input Parameters:**

| Name | Type | Default | Mandatory |
|---|---|---|---|
| `ActiveItem` | Integer | `-1` | No |
| `ActiveSubItem` | Integer | `-1` | No |

**Screen Actions:**
- `OnReady` — Calls `MenuReady`, then `SetActiveMenuItems`; bound to `OnRender` + `OnParametersChanged`
- `OnDestroy` — Calls `MenuDestroy`
- `HideMenu` — Calls `ToggleSideMenu`

**Widget Tree:**

```
[Container] NavContainer                               ← BUG #1: should be AdvancedHtml <nav> tag
  Style: "nav"                                        ← BUG #2: should be Extended class="app-menu-content display-flex" (no Style)
  Extended: role="navigation"
  (missing Extended: aria-label="Main navigation")    ← BUG #3
  │
  ├─ (missing header-logo container + If + ApplicationTitle block)  ← BUG #4
  │
  ├─ [Container] PageLinks
  │    Style: "app-menu-links"
  │    Width: (fill parent)
  │    (missing Extended: role="menubar")             ← BUG #5
  │    (no children)
  │
  └─ [Container] LoginInfo
       Style: "login-info"                            ← BUG #6: should be "app-login-info placeholder-empty"
       Width: (fill parent)
       └─ [BlockInstance] UserInfo → UserInfo (Common flow)
            (no parameter bindings)

[Container] MenuOverlay
  Style: "menu-overlay"                              ← BUG #7: should be "app-menu-overlay"
  Width: (fill parent)
  Event: click → HideMenu
  (missing Extended: role="button")                  ← BUG #8
  (no children)
```

---

## UserInfo

**Input Parameters:** None

**Screen Actions:**
- `OnReady` → calls `GetUsernameAndPhoto`
- `GetUsernameAndPhoto` — If `Client.UserName = "" and GetUserId() <> NullTextIdentifier()`:
  - True: Calls `GetUserProfile`, assigns `Client.UserName` and `Client.UserPhotoURL`
  - False: End
- `ClientLogout` — Calls `DoLogout`, then JS redirect

**Widget Tree:**

```
[Container] UserInfoWrapper
  Style: "user-info"
  Width: (fill parent)
  │
  ├─ [Text] UserNameText                              ← BUG: entire conditional structure missing
  │    Text: Client.UserName                         ← should be inside UserIsLogged If → True branch
  │    (no style)                                    ← should be Expression in a Link → UserProfile
  │
  └─ [Link] LogoutLink
       Style: "logout-link"                          ← BUG: should have no style
       OnClick → ClientLogout
       │
       ├─ [Text] (unnamed)  Text: "link"             ← BUG: stray default text node
       └─ [Text] LogoutText  Text: "Logout"          ← BUG: should be Icon (sign-out) + Text "Log out"

(Missing entirely: UserIsLogged If wrapper, HasPhotoURL If, photo Image,
 UserAvatar block, username Link → UserProfile, proper logout Icon+Text,
 False branch Login link)
```

**Bug summary:**
- Missing "UserIsLogged" If widget (entire conditional auth check)
- Missing True branch: HasPhotoURL If (photo Image or UserAvatar fallback)
- Missing True branch: username Link → UserProfile with Expression widget
- Missing True branch: logout Link with sign-out Icon + "Log out" text (correct styles)
- Missing False branch: Login Link with sign-in icon for unauthenticated users
- LogoutLink has wrong style "logout-link" (should be no style)
- LogoutLink children wrong: stray "link" Text + literal "Logout" Text
