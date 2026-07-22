# Login Screen — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-22

**Total discrepancies: 18**

---

## 1. Duplicate widgets

| # | Location | Reference | Built | Symptom |
|---|---|---|---|---|
| 1 | ButtonLoading `Button` placeholder | 1 Button (unnamed, "Log in") | 2 Buttons: unnamed ("text") + `LoginBtnInLoading` ("Log in") | Doubled login button |
| 2 | `LoginBtnContainer` | No button outside ButtonLoading | `LoginBtn` Button outside the ButtonLoading block | Third "Log in" button rendered |

## 2. Literal vs bound captions

| # | Widget | Reference value | Built value |
|---|---|---|---|
| 3 | Unnamed Button (inside ButtonLoading) → Text | `"Log in"` | `"text"` |
| 4 | `LoginBtnInLoading` → unnamed Text | *(does not exist — only 1 button in reference)* | `"Button"` |
| 5 | `LoginBtn` → unnamed Text | *(does not exist)* | `"Button"` |
| 6 | `ExternalProviderBtn` → Text | `"Continue with "` + Expression(`ExternalIdentityProviders.Current.Name`) | `"Button"` |
| 7 | `TogglePasswordBtn` → Text nodes | *(no text; uses Icon widgets inside a Link)* | `"Save"` + `"Show"` (renders "SaveShow") |

## 3. Missing/incorrect CSS classes

| # | Widget | Reference | Built |
|---|---|---|---|
| 8 | Form `LoginForm` Style | `"login-form"` | `"form card"` |
| 9 | Outer wrapper Container Style | `"login-screen"` | *(missing — Form is the first child of placeholder directly)* |
| 10 | Logo+title Container Style | `"login-logo"` | *(entire section missing)* |
| 11 | Input section Container Style | `"login-inputs"` | *(missing — EmailContainer/PasswordContainer are siblings directly)* |
| 12 | Login button Container Style | `"login-button margin-top-l"` | `"form-group"` on LoginBtnContainer |
| 13 | `ButtonLoading` ExtendedClass | `"full-width"` | *(null)* |
| 14 | Password input Style | `"form-control login-password"` + CustomStyle padding | `"form-control"` only; no custom padding |
| 15 | Email label+input wrapping | `AnimatedLabel` WebBlockInstance | Plain Input without label or AnimatedLabel |
| 16 | Password label+input wrapping | `AnimatedLabel` + `InputWithIcon` WebBlockInstances | Plain Input + sibling Button |

## 4. Structural/nesting differences

| # | Element | Reference | Built |
|---|---|---|---|
| 17 | Logo + app title section | Container (`login-logo`) → nested Container → Image + AdvancedHtml h1 with `GetAppName()` Expression | **Entirely absent** |
| 18 | `BuiltInProvider` If block | Wraps all email/password/login-button content with `Condition: ShowBuiltInProvider` | **Absent** — inputs always visible |
| 19 | `Separator` If block | `Condition: ShowBuiltInProvider and ShowExternalProvider` → Container with flex layout + SeparatorInstance + "or" Text | **Absent** |
| 20 | Password toggle | Link → If(`IsPasswordVisible`) → Icon(`eye-slash`) / Icon(`eye`) inside InputWithIcon placeholder | Button with two Text nodes "Save"/"Show" as siblings to Input_Password |
| 21 | Forgot password link | Container(`margin-top-l`) → Container(right-aligned) → Link → Text("Forgot your password?") | **Absent** |
| 22 | Email input | `AnimatedLabel` block with named Label+Input; InputType: Text; MaxLength: 250; Mandatory: True | Plain Input; InputType: Email; MaxLength: 50; Mandatory: False |
| 23 | `ExternalProviderBtn` ProviderIndex arg | `ExternalIdentityProviders.CurrentRowNumber` | `0` (hardcoded) |
| 24 | External provider button outer container | Container (`margin-bottom-s`) wrapping ButtonLoadingInstance2 | Button directly in List (no ButtonLoading wrapping) |

---

**Count: 24 discrepancies** (items 17-24 expand the initial 18 structural gaps).

---

## Fix scope

The built screen is a simplified stub — not a partially-correct layout. The entire content area needs to be replaced to match the reference. Screen actions, local variables, and exception handling are **not** in scope (already correctly specified).

Specific actions required:
1. Replace `"form card"` form style with `"login-form"`; add outer `"login-screen"` Container
2. Add logo+title section (Logo Image + AdvancedHtml h1 + GetAppName() Expression)
3. Wrap email/password/login-button section in `BuiltInProvider` If block (`ShowBuiltInProvider`)
4. Replace EmailContainer + bare Input with AnimatedLabel block (Label="Login", Input_UsernameVal, Text type, MaxLength=250, Mandatory=True)
5. Replace PasswordContainer + bare Input + TogglePasswordBtn with AnimatedLabel + InputWithIcon wrapping: Link → If/Icon(eye-slash/eye); Input_Password with correct style + custom padding
6. Add forgot-password Link (→ RecoverPasswordRequest; right-aligned; tabindex=3)
7. Replace `LoginBtnContainer`'s 3 buttons with single ButtonLoading (`IsLoading=IsBuiltInExecuting`, `ExtendedClass="full-width"`) containing 1 Button (style="btn btn-primary", IsDefault=true, Enabled=`ExecutingIndex = -1`, tabindex=4, Text="Log in")
8. Add Separator If block between BuiltInProvider and ExternalProviders If blocks
9. Fix ExternalProviders section: wrap in If(`ShowExternalProvider`), wrap button in ButtonLoading(`IsLoading=ExecutingIndex = ExternalIdentityProviders.CurrentRowNumber`, ExtendedClass="full-width"), fix ProviderIndex=CurrentRowNumber, fix caption to "Continue with " + Expression
