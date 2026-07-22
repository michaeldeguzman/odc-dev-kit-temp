# ChangePassword — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-22 via Mentor inspection.

---

```
[BlockInstance] LayoutTopMenu  (block: Layouts/LayoutTopMenu)
  Parameters:
    ExtendedClass → ""
    HasFixedHeader → True
    EnableAccessibilityFeatures → False

  ├─ Placeholder: Header
  │  └─ [Container] MenuPlaceholder
  │        Style: "menu-placeholder"
  │        Width: (fill parent)
  │     └─ [BlockInstance] Menu  (block: Common/Menu)
  │           Parameters: ActiveItem → -1, ActiveSubItem → -1
  │
  ├─ Placeholder: Breadcrumbs        ← BUG: empty (no breadcrumb link)
  │
  ├─ Placeholder: Title              ← BUG: empty (no title text)
  │
  └─ Placeholder: MainContent
     └─ [Form] Form                  ← BUG: Form is direct child, should be inside Columns2/Column1
           Style: "form card"
           Width: (fill parent)

        ├─ [Container] OldPwdContainer
        │     Style: "form-group"    ← BUG: should be no-style Container → AnimatedLabel
        │     Visible: True
        │  └─ [Input] Input_OldPassword
        │        Style: "form-control"
        │        InputType: Password
        │        Variable: OldPassword
        │        Mandatory: False    ← BUG: should be True
        │        MaxLength: 50       ← BUG: should be 256
        │        Enabled: True
        │        OnChange: Input_OldPasswordOnChange
        │        (no tabindex)       ← BUG: should be tabindex=1
        │        (no autocomplete)   ← BUG: should be autocomplete="current-password"
        │
        ├─ [Container] NewPwdContainer
        │     Style: "form-group"    ← BUG: should be "margin-top-base" Container → AnimatedLabel → InputWithIcon
        │     Visible: True
        │  ├─ [Input] Input_NewPassword
        │  │     Style: "form-control"  ← BUG: should be "form-control login-password padding-left-none" with CustomStyle
        │  │     InputType: Password
        │  │     Variable: NewPassword
        │  │     Mandatory: False    ← BUG: should be True
        │  │     MaxLength: 50       ← BUG: should be 256
        │  │     Enabled: True
        │  │     (no tabindex)       ← BUG: should be tabindex=2
        │  │     (no autocomplete)   ← BUG: should be autocomplete="new-password"
        │  │
        │  └─ [Button] ToggleNewPwdBtn  ← BUG: should be Link→If→Icon inside InputWithIcon
        │        Style: "btn-icon"
        │        IsDefault: True     ← BUG: no button should have IsDefault except the save button
        │        OnClick: OnToggleNewPasswordVisibility (ValidateAndContinue)  ← BUG: should be no validation
        │     ├─ [Text] (unnamed)    Text: "Save"   ← leftover text node
        │     └─ [Text] ToggleNewPwdBtnText  Text: "Show"
        │
        ├─ [BlockInstance] PasswordPolicy  ← CORRECT: present, wired, position correct relative to other fields
        │     Parameters: Password → NewPassword, Compliant → PasswordPolicyCompliant, IsValid → IsValid
        │
        ├─ [Container] ConfirmPwdContainer
        │     Style: "form-group"    ← BUG: should be "margin-top-base" Container → AnimatedLabel → InputWithIcon
        │     Visible: True
        │  ├─ [Input] Input_ConfirmPassword
        │  │     Style: "form-control"  ← BUG: should be "form-control login-password padding-left-none" with CustomStyle
        │  │     InputType: Password
        │  │     Variable: ConfirmPassword
        │  │     Mandatory: False    ← BUG: should be True
        │  │     MaxLength: 50       ← BUG: should be 256
        │  │     Enabled: True
        │  │     OnChange: Input_ConfirmPasswordOnChange
        │  │     (no tabindex)       ← BUG: should be tabindex=3
        │  │
        │  └─ [Button] ToggleConfirmPwdBtn  ← BUG: should be Link→If→Icon inside InputWithIcon
        │        Style: "btn-icon"
        │        IsDefault: False
        │        OnClick: OnToggleConfirmPasswordVisibility (ValidateAndContinue)  ← BUG: no validation needed
        │     ├─ [Text] (unnamed)    Text: "Button"  ← leftover
        │     └─ [Text] ToggleConfirmPwdBtnText  Text: "Show"
        │
        └─ [Container] SaveBtnContainer
              Style: "form-group"    ← BUG: should be no-style Container → ButtonLoading
              Visible: True
           └─ [Button] SetNewPasswordBtn
                 Style: "btn btn-primary"  ← BUG: should be "btn btn-primary margin-top-l"
                 IsDefault: False    ← BUG: should be True
                 Enabled: IsButtonEnabled and not IsExecuting  ← BUG: should be IsButtonEnabled
                 OnClick: SetNewPasswordOnClick (ValidateAndContinue)
                 (no tabindex)       ← BUG: should be tabindex=4
              ├─ [Text] (unnamed)    Text: "Button"  ← leftover
              └─ [Text] SetNewPasswordBtnText  Text: "Set New Password"  ← BUG: wrong case, should be "Set new password"
```

**Missing vs reference:**
- No Breadcrumbs (link back to UserProfile)
- No Title ("Change your password")
- No Columns2 wrapper in MainContent
- No AnimatedLabel blocks for any of the 3 inputs
- No InputWithIcon blocks for New/Confirm password
- No eye-icon toggle Links (using Buttons instead)
- No ButtonLoading wrapper for submit button
- No autocomplete extended properties on inputs
