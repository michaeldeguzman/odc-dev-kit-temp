# Common Blocks — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 31** (ApplicationTitle: 6, MenuIcon: 5, Menu: 8, UserInfo: 12)

---

## ApplicationTitle — 6 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Root widget type | Container "ApplicationTitleWrapper" | Link "AppTitleLink" |
| 2 | Root style | "application-name display-flex align-items-center full-height" | "app-name" |
| 3 | Root extended properties | role="button", tabindex="0" | None |
| 4 | AppLogo Image | Image (local Logo, style="app-logo", CustomStyle="height: 32px;", alt="") | Missing entirely |
| 5 | App name widget + content | Expression GetAppName() (example "Application Title") | Text "Application Name" (literal) |
| 6 | Stray text node | None | Unnamed Text "link" child of AppTitleLink |

### Fix scope:
1. Replace `AppTitleLink` Link with Container `ApplicationTitleWrapper`; set style to `"application-name display-flex align-items-center full-height"`
2. Add Extended: `role="button"`, `tabindex="0"` on the container
3. Change onclick binding: add `onclick` event on the container pointing to `ApplicationNameOnClick`
4. Add Image `AppLogo` as first child: local image `Logo`, style `"app-logo"`, CustomStyle `"height: 32px;"`, Extended `alt=""`
5. Replace Text `AppTitleText` (literal) with Expression widget using `GetAppName()`, example `"Application Title"`
6. Remove the stray unnamed Text "link" child

---

## MenuIcon — 5 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Container extended: aria-label | "Toggle the Menu" | Missing |
| 2 | Container extended: role | "button" | Missing |
| 3 | Container extended: tabindex | "0" | Missing |
| 4 | Container extended: aria-haspopup | "true" | Missing |
| 5 | Child widget | Icon (list, 2x, regular, style="icon", aria-hidden="true") | Text "☰" literal |

### Fix scope:
1. Add Extended on the root Container: `aria-label="Toggle the Menu"`, `role="button"`, `tabindex="0"`, `aria-haspopup="true"`
2. Replace Text `MenuIconText` with Icon widget: icon=`list`, size=`2x`, weight=`regular`, style=`"icon"`, Extended: `aria-hidden="true"`

---

## Menu — 8 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Root widget type | AdvancedHtml `<nav>` tag | Container "NavContainer" |
| 2 | Root class/style | Extended class="app-menu-content display-flex" (no Style) | Style="nav" |
| 3 | Root extended: aria-label | "Main navigation" | Missing |
| 4 | header-logo section | Container "header-logo placeholder-empty" + If(False) + ApplicationTitle block | Missing entirely |
| 5 | PageLinks extended | role="menubar" | Missing |
| 6 | LoginInfo style | "app-login-info placeholder-empty" | "login-info" |
| 7 | Overlay style | "app-menu-overlay" | "menu-overlay" |
| 8 | Overlay extended | role="button" | Missing |

### Fix scope:
1. Change root Container to AdvancedHtml `<nav>` tag; remove Style="nav"; add Extended: `class="app-menu-content display-flex"`, `role="navigation"`, `aria-label="Main navigation"`
2. Add `header-logo placeholder-empty` Container as first child of the nav, containing If(Condition=False, DesignMode=ShowFalse) with True=empty and False=BlockInstance→ApplicationTitle (no params)
3. Add Extended `role="menubar"` to PageLinks
4. Change LoginInfo style from `"login-info"` to `"app-login-info placeholder-empty"`
5. Change MenuOverlay style from `"menu-overlay"` to `"app-menu-overlay"`
6. Add Extended `role="button"` to MenuOverlay

---

## UserInfo — 12 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | UserIsLogged If widget | Present (GetUserId() <> NullTextIdentifier(), ShowAll) | Missing — no auth check |
| 2 | True branch: HasPhotoURL If | Present (Client.UserPhotoURL <> "") | Missing |
| 3 | True branch: photo Image | URL=Client.UserPhotoURL, style="avatar avatar-small border-radius-rounded" | Missing |
| 4 | True branch: UserAvatar block | UserAvatar (OutSystemsUI), Size=Small, Name=Client.UserName | Missing |
| 5 | True branch: username Link | Link → UserProfile (no style, Inherited), Expression Client.UserName | Text widget only, no navigation |
| 6 | True branch: username container | Container style="margin-left-s" wrapping username Link | Missing |
| 7 | True branch: logout container | Container style="margin-left-s" wrapping logout Link | Missing |
| 8 | True branch: logout Link style | No style | "logout-link" |
| 9 | True branch: logout Link children | Icon (sign-out, FontSize, "icon") + Text "Log out" ("margin-left-s wcag-hide-text") | Text "Logout" literal only |
| 10 | True branch: logout transition | Fade | Not set |
| 11 | False branch: Login link | Link → Login (sign-in icon + Text "Login") | Missing entirely |
| 12 | Stray text node | None | Unnamed Text "link" in LogoutLink |

### Fix scope (complete rebuild of UserInfo widget tree):
1. Remove current children (UserNameText Text, LogoutLink Link)
2. Add `UserIsLogged` If widget (Condition: `GetUserId() <> NullTextIdentifier()`, DesignMode: ShowAll)
3. **True branch** — 3 containers:
   a. Container (no style): HasPhotoURL If (`Client.UserPhotoURL <> ""`)
      - True: Image (URL=`Client.UserPhotoURL`, style=`"avatar avatar-small border-radius-rounded"`, Extended: `title=Client.UserName`, `alt="User photo"`)
      - False: BlockInstance `userAvatarInstance` → UserAvatar (OutSystemsUI), Size=`Entities.Size.Small`, Name=`Client.UserName`
   b. Container (style=`"margin-left-s"`): Link (no style, Inherited) → UserProfile
      - Expression `Client.UserName`, Example `"Username"`
   c. Container (style=`"margin-left-s"`): Link (no style, Fade) → `ClientLogout`
      - Icon `Icon3` (sign-out, FontSize, regular, style=`"icon"`)
      - Text (unnamed, `"Log out"`, style=`"margin-left-s wcag-hide-text"`)
4. **False branch**: Link (no style, fill parent, Fade) → Login screen
   - Icon `Icon4` (sign-in, FontSize, regular, style=`"icon"`)
   - Text (unnamed, `"Login"`, style=`"margin-left-s"`)
