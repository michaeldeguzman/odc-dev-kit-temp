# ChangePassword — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-22

**Total discrepancies: 26**

## 1. Missing placeholders/sections

| # | Placeholder | Reference | Built |
|---|---|---|---|
| 1 | Breadcrumbs | Link (→ UserProfile) → Icon(caret-left) + Text "Back to profile" (margin-left: 5px) | Empty |
| 2 | Title | Text "Change your password" | Empty |
| 3 | MainContent wrapper | Columns2 block → Column1 → Form | Form is direct child (no Columns2) |

## 2. Structural/nesting differences

| # | Element | Reference | Built |
|---|---|---|---|
| 4 | Old password wrapping | Container (no style) → AnimatedLabel (Label "Current password", Input_OldPassword) | Container "form-group" → bare Input_OldPassword |
| 5 | New password wrapping | Container "margin-top-base" → AnimatedLabel + InputWithIcon (AlignIconRight=True, ExtendedClass="padding-left-none") | Container "form-group" → bare Input_NewPassword + Button ToggleNewPwdBtn |
| 6 | Confirm password wrapping | Container "margin-top-base" → AnimatedLabel + InputWithIcon (AlignIconRight=True, ExtendedClass="padding-left-none") | Container "form-group" → bare Input_ConfirmPassword + Button ToggleConfirmPwdBtn |
| 7 | Submit button wrapping | Container (no style) → ButtonLoading (IsLoading=IsExecuting, ExtendedClass="full-width") | Container "form-group" → bare Button SetNewPasswordBtn |
| 8 | Password toggle (new) | Link (no validation, OnClick OnToggleNewPasswordVisibility) → If(IsPasswordVisible) → Icon(eye-slash/eye) inside InputWithIcon | Button ToggleNewPwdBtn (IsDefault True, ValidateAndContinue) |
| 9 | Password toggle (confirm) | Link (no validation, OnClick OnToggleConfirmPasswordVisibility) → If(IsPasswordVisible) → Icon(eye-slash/eye) inside InputWithIcon | Button ToggleConfirmPwdBtn (ValidateAndContinue) |

## 3. Missing/incorrect properties

| # | Widget | Property | Reference | Built |
|---|---|---|---|---|
| 10 | Input_OldPassword | Mandatory | True | False |
| 11 | Input_OldPassword | MaxLength | 256 | 50 |
| 12 | Input_OldPassword | tabindex | 1 | absent |
| 13 | Input_OldPassword | autocomplete | "current-password" | absent |
| 14 | Input_NewPassword | Mandatory | True | False |
| 15 | Input_NewPassword | MaxLength | 256 | 50 |
| 16 | Input_NewPassword | Style | "form-control login-password padding-left-none" | "form-control" |
| 17 | Input_NewPassword | CustomStyle | padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px; | absent |
| 18 | Input_NewPassword | tabindex | 2 | absent |
| 19 | Input_NewPassword | autocomplete | "new-password" | absent |
| 20 | Input_ConfirmPassword | Mandatory | True | False |
| 21 | Input_ConfirmPassword | MaxLength | 256 | 50 |
| 22 | Input_ConfirmPassword | Style | "form-control login-password padding-left-none" | "form-control" |
| 23 | Input_ConfirmPassword | CustomStyle | padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px; | absent |
| 24 | Input_ConfirmPassword | tabindex | 3 | absent |
| 25 | ToggleNewPwdBtn Button | IsDefault | False (should not be a button) | True |
| 26 | SetNewPasswordBtn | IsDefault | True | False |
| 27 | SetNewPasswordBtn | Enabled | IsButtonEnabled | IsButtonEnabled and not IsExecuting |
| 28 | SetNewPasswordBtn | Style | "btn btn-primary margin-top-l" | "btn btn-primary" |
| 29 | SetNewPasswordBtn | tabindex | 4 | absent |

## 4. Literal vs bound captions

| # | Widget | Reference | Built |
|---|---|---|---|
| 30 | Button text | "Set new password" (lowercase n) | "Set New Password" |
| 31 | Old password label | "Current password" | absent (no AnimatedLabel) |
| 32 | New password label | "New password" | absent |
| 33 | Confirm password label | "Confirm password" | absent |

**Count: 33 discrepancies** (numbered items represent distinct property/widget gaps).

## Fix scope

Full widget tree rebuild. PasswordPolicy block correctly positioned and wired — preserve it.

Specific actions:
1. Add Breadcrumbs: Link (→ UserProfile, no validation) → Icon(caret-left, "icon", FontSize, regular) + Text "Back to profile" (CustomStyle: margin-left: 5px)
2. Add Title: Text "Change your password"
3. Replace MainContent Form with: Columns2 block (all params null) → Column1 → Form "form card"
4. Child 1: Container (no style) → AnimatedLabel: Label "Current password" → Input_OldPassword (Password, OldPassword, Mandatory True, MaxLength 256, "form-control", Enabled True, OnChange Input_OldPasswordOnChange, tabindex=1, autocomplete="current-password")
5. Child 2: Container "margin-top-base" → AnimatedLabel: Label "New password" → InputWithIcon (ExtendedClass="padding-left-none", AlignIconRight=True): Icon=Link(no validation, OnClick OnToggleNewPasswordVisibility)→If "PasswordVisible"(IsPasswordVisible)→eye-slash/eye; Input=Input_NewPassword ("form-control login-password padding-left-none", CustomStyle: padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;, Password, NewPassword, Mandatory True, MaxLength 256, Enabled True, tabindex=2, autocomplete="new-password")
6. Child 3: PasswordPolicy block (preserve Password→NewPassword, Compliant→PasswordPolicyCompliant, IsValid→IsValid)
7. Child 4: Container "margin-top-base" → AnimatedLabel: Label "Confirm password" → InputWithIcon (ExtendedClass="padding-left-none", AlignIconRight=True): Icon=Link(no validation, OnClick OnToggleConfirmPasswordVisibility)→If "PasswordVisible2"(IsPasswordVisible)→eye-slash/eye; Input=Input_ConfirmPassword (same style+CustomStyle as NewPassword, Password, ConfirmPassword, Mandatory True, MaxLength 256, Enabled True, OnChange Input_ConfirmPasswordOnChange, tabindex=3)
8. Child 5: Container (no style) → ButtonLoading (IsLoading=IsExecuting, ExtendedClass="full-width") → Button ("btn btn-primary margin-top-l", IsDefault True, Enabled IsButtonEnabled, OnClick SetNewPasswordOnClick ValidateAndContinue, tabindex=4) → spinner container + "Set new password"
