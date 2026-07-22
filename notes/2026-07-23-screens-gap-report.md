# Screens — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 15**

---

## Login — 2 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Input_Password MaxLength | null (no limit) | 50 |
| 2 | Screen title | "Log in" | "Login" |

### Fix scope
1. Set `Input_Password` MaxLength to null (no limit)
2. Change screen title from "Login" to "Log in"

---

## RecoverPasswordRequest — 1 discrepancy

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | AnimatedLabel Label placeholders | Label widget only | Label widget + stale unnamed Text "label" node |

### Fix scope
1. In the AnimatedLabel instance for Email input: remove the stale unnamed Text "label" node from the Label placeholder (keep only the Label widget → "Email")

---

## RecoverPasswordReset — 5 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Top-level structure | login-screen Container is direct form root | Extra stray Container (no style) + orphaned AdvancedHtml h5 (no content) before login-screen |
| 2 | First form container | Container Style="login-logo" CustomStyle="text-align: center;" wrapping image+h5+description | Unnamed Container (no style) wrapping same content |
| 3 | AnimatedLabel Label placeholders | Label widget only (3 instances) | Label widget + stale unnamed Text "label" node (3 instances: Email, Verification code, New password, Confirm password) |
| 4 | NewPassword InputWithIcon CustomStyle | `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;` | `padding-right: var(--space-xl);` only |
| 5 | ConfirmPassword InputWithIcon CustomStyle | same as #4 | same abbreviated form |

### Fix scope
1. Remove the stray outer Container + orphaned AdvancedHtml h5 before the login-screen Container
2. Add Style="login-logo" and CustomStyle="text-align: center;" to the unnamed first container inside the form (image+h5+text wrapper)
3. Remove stale unnamed Text "label" nodes from all 4 AnimatedLabel Label placeholders
4. Set NewPassword InputWithIcon (InputWithIconInstance) CustomStyle to full: `padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;`
5. Same for ConfirmPassword InputWithIcon (InputWithIconInstance3)

---

## ChangePassword — 4 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Header placeholder | Menu block instance (direct, no wrapper) | Container "MenuPlaceholder" Style="menu-placeholder" wrapping Menu block |
| 2 | Menu block params | ActiveItem=null, ActiveSubItem=null | ActiveItem=-1, ActiveSubItem=-1 |
| 3 | AnimatedLabel Label placeholders | Label widget only (4 instances) | Label widget + stale unnamed Text "label" node (4 instances) |
| 4 | GetUserDetail aggregate | Absent | Present but unused (no widget binds to its output) |

### Fix scope
1. Remove MenuPlaceholder wrapper Container from Header placeholder; make Menu block instance a direct child of Header placeholder
2. Set Menu block instance params: ActiveItem=null (not set), ActiveSubItem=null (not set)
3. Remove stale unnamed Text "label" nodes from all 4 AnimatedLabel Label placeholders
4. Delete the unused GetUserDetail screen aggregate

---

## InvalidPermissions — 1 discrepancy

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Header container name | Unnamed | Named "MenuPlaceholder" |

### Fix scope
1. Remove name "MenuPlaceholder" from the header container (make unnamed) — style is correct, content is correct

---

## UserProfile — 2 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | NameInput MaxLength | null (no limit) | 50 |
| 2 | Form name | "ProfileDetailsForm" | "ProfileForm" |

**Not discrepancies (intentional):**
- `divPhoto` section (photo display) absent — this tenant's User entity has no PhotoUrl attribute
- `divPhotoURL` section (Photo URL input) absent — same reason

### Fix scope
1. Set NameInput MaxLength to null (no limit)
2. Rename Form from "ProfileForm" to "ProfileDetailsForm"

---

## Notes

**Stale "label" text nodes:** Same pattern as stray "link" text in Link widgets (seen in layout blocks). ODC auto-creates a default text child in placeholders; it survives alongside the real Label widget when a rebuild doesn't explicitly clear the placeholder first.

**Icon naming (phosphor-eye-slash vs eye-slash):** NOT a discrepancy — these are different representations of the same icon from different OutSystemsUI library versions. The pre-existing "Icon library migration" warning covers this; do not attempt to rename.

**ChangePassword GetUserDetail aggregate:** Not in the reference. Likely created by Mentor in a prior session as an unintended side effect. Safe to remove since no widget binds to its outputs.
