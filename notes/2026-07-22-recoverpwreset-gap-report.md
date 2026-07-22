# RecoverPasswordReset — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-22

**Total discrepancies: 20**

## 1. Structural/nesting differences

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Outer wrapper | Container "login-screen" wrapping Form | Absent — Form is first child of placeholder |
| 2 | Form name | PasswordResetForm | RecoverPasswordForm |
| 3 | Form style | "login-form" | "form card" |
| 4 | Logo section | Container "login-logo" → Image + h5 "Reset password" + instructions text | Entirely absent |
| 5 | Email field | Container "login-inputs margin-top-m" → AnimatedLabel (Label "Email", Input_Email disabled, Enabled=False) | Bare Expression + Text nodes directly in Form (not in AnimatedLabel, not in container) |
| 6 | Code input wrapping | Container "login-inputs margin-top-m" → AnimatedLabel (Label "Verification code", Input_Code) | Plain Container "form-group" → bare Input_Code |
| 7 | New password wrapping | Container "margin-top-base password-input" → AnimatedLabel + InputWithIcon (toggle Link/If/Icon) | Plain Container "form-group" → bare Input_NewPassword + Button ToggleNewPwdBtn |
| 8 | Confirm password wrapping | Container "margin-top-base password-input" → AnimatedLabel + InputWithIcon (toggle Link/If/Icon) | Plain Container "form-group" → bare Input_ConfirmPassword + Button ToggleConfirmPwdBtn |
| 9 | Submit button wrapping | Container "login-button margin-top-l" → ButtonLoading (IsLoading=IsExecuting, ExtendedClass="full-width") | Plain Container "form-group" → bare Button SavePasswordBtn |
| 10 | Footer link section | Container "margin-top-m" (text-align center) → Text "Not in the right place?" + Link → Login | Entirely absent |

## 2. Duplicate/extra/wrong widgets

| # | Widget | Reference | Built |
|---|---|---|---|
| 11 | Email display | AnimatedLabel with disabled Input_Email | Bare Expression + separate Text node (2 widgets instead of 1 structured block) |
| 12 | Password toggle | Link → If(IsPasswordVisible) → Icon(eye-slash/eye) inside InputWithIcon | Button with Text "Save"+"Show" (ToggleNewPwdBtn) |
| 13 | Confirm toggle | Link → If(IsConfirmPasswordVisible) → Icon(eye-slash/eye) inside InputWithIcon | Button with Text "Button"+"Show" (ToggleConfirmPwdBtn) |
| 14 | SavePasswordBtn Text nodes | One Text "Save password" | Text "Button" + Text "Save Password" |

## 3. Literal vs bound captions

| # | Widget | Reference | Built |
|---|---|---|---|
| 15 | Button Text | "Save password" (lowercase p) | "Save Password" (uppercase P) |

## 4. Missing/incorrect properties

| # | Widget | Property | Reference | Built |
|---|---|---|---|---|
| 16 | ToggleNewPwdBtn / Button | IsDefault | False | True ← BUG: only save button should be IsDefault |
| 17 | SavePasswordBtn / Button | IsDefault | True | False |
| 18 | SavePasswordBtn / Button | Enabled | IsButtonEnabled | IsButtonEnabled and not IsExecuting |
| 19 | Input_Code | Mandatory | True | False |
| 20 | Input_Code | tabindex | 1 | absent |
| 21 | Input_NewPassword | Mandatory | True | False |
| 22 | Input_NewPassword | MaxLength | 256 | 50 |
| 23 | Input_NewPassword | tabindex | 2 | absent |
| 24 | Input_ConfirmPassword | Mandatory | True | False |
| 25 | Input_ConfirmPassword | MaxLength | 256 | 50 |
| 26 | Input_ConfirmPassword | tabindex | 3 | absent |
| 27 | SavePasswordBtn | tabindex | 4 | absent |

**Count: 27 discrepancies** (items 16-27 expand the structural gaps).

## Fix scope

Rebuild the entire content area. PasswordPolicy block is correctly wired — preserve it in the correct position between NewPassword and ConfirmPassword fields.

Specific actions:
1. Add outer "login-screen" Container wrapping the Form; rename Form to `PasswordResetForm`; change Form style to "login-form"
2. Add logo section: Container "login-logo" (text-align center) → Image Logo (100px) + AdvancedHtml h5 (class="margin-top-base text-neutral-8") "Reset password" + Container "margin-top-s" → "If the entered email is correct, we'll send a verification code to that email. Please enter the code below to verify your identity."
3. Replace bare Email Expression+Text with Container "login-inputs margin-top-m" → AnimatedLabel (Label "Email", Input_Email: Email type, Mandatory True, MaxLength 250, **Enabled False**, Placeholder "mary.smith@acme.com", no tabindex)
4. Replace CodeContainer + bare Input with Container "login-inputs margin-top-m" → AnimatedLabel (Label "Verification code", Input_Code: Text type, Mandatory True, Enabled True, OnChange=Input_CodeOnChange, tabindex=1)
5. Replace NewPwdContainer + bare Input + ToggleNewPwdBtn with Container "margin-top-base password-input" → AnimatedLabel (Label "New password") + InputWithIcon (AlignIconRight=True): Icon=Link→If(IsPasswordVisible)→Icon(eye-slash/eye), Input=Input_NewPassword (form-control login-password, custom padding, Password, Mandatory True, MaxLength 256, tabindex=2)
6. Preserve PasswordPolicy block between new password and confirm password
7. Replace ConfirmPwdContainer + bare Input + ToggleConfirmPwdBtn with Container "margin-top-base password-input" → AnimatedLabel (Label "Confirm password") + InputWithIcon (AlignIconRight=True): Icon=Link→If(IsConfirmPasswordVisible)→Icon(eye-slash/eye), Input=Input_ConfirmPassword (form-control login-password, custom padding, Password, Mandatory True, MaxLength 256, OnChange=Input_ConfirmPasswordOnChange, tabindex=3)
8. Replace SaveBtnContainer + Button with Container "login-button margin-top-l" → ButtonLoading (IsLoading=IsExecuting, ExtendedClass="full-width") → Button (IsDefault True, Enabled **IsButtonEnabled**, tabindex=4, OnClick=ResetPasswordOnClick ValidateAndContinue, Text "Save password")
9. Add footer: Container "margin-top-m" (text-align center) → Text "Not in the right place?" + Link → Login (no validation, tabindex=5, aria-label "Go to login page") → Text "Go to login."
