# RecoverPasswordReset — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-22 via Mentor inspection.

---

```
WebBlockInstance — LayoutBlank
  Block: LayoutBlank (from Layouts flow)

  └── [Placeholder: MainContent]

      └── Form — RecoverPasswordForm            ← BUG: wrong name (should be PasswordResetForm)
            Style: "form card"                  ← BUG: should be "login-form"
            Width: (fill parent)
            (no outer "login-screen" Container)  ← BUG: missing wrapper

          ├── Expression — EmailExpression       ← BUG: bare expression (not in AnimatedLabel/container)
          │     Value: Email
          │
          ├── Text — EmailText                  ← BUG: stray text node
          │     Text: (caption of Email field)
          │
          ├── Container — CodeContainer
          │     Style: "form-group"             ← BUG: should be "login-inputs margin-top-m" with AnimatedLabel
          │     Visible: True
          │   └── Input — Input_Code
          │         InputType: Text
          │         Variable: Code
          │         Mandatory: False            ← BUG: should be True
          │         MaxLength: 50              ← BUG: should be unset/null
          │         Enabled: True
          │         OnChange: (custom event)   ← BUG: should be Input_CodeOnChange
          │         (no tabindex)              ← BUG: should be tabindex=1
          │
          ├── Container — NewPwdContainer
          │     Style: "form-group"            ← BUG: should be "margin-top-base password-input" with AnimatedLabel+InputWithIcon
          │     Visible: True
          │   ├── Input — Input_NewPassword
          │   │     Style: "form-control"
          │   │     InputType: Password
          │   │     Variable: NewPassword
          │   │     Mandatory: False           ← BUG: should be True
          │   │     MaxLength: 50             ← BUG: should be 256
          │   │     Enabled: True
          │   │     (no tabindex)             ← BUG: should be tabindex=2
          │   │
          │   └── Button — ToggleNewPwdBtn
          │         Style: "btn-icon"
          │         IsDefault: True           ← BUG: should be False (only save button is IsDefault)
          │         (no tabindex)
          │       ├── Text: "Save"            ← BUG: leftover text node
          │       └── Text: "Show"
          │
          ├── BlockInstance — PasswordPolicy   ← CORRECT: present and wired
          │     Parameters:
          │       Password → NewPassword
          │       Compliant → PasswordPolicyCompliant
          │       IsValid → IsValid
          │
          ├── Container — ConfirmPwdContainer
          │     Style: "form-group"           ← BUG: should be "margin-top-base password-input" with AnimatedLabel+InputWithIcon
          │     Visible: True
          │   ├── Input — Input_ConfirmPassword
          │   │     Style: "form-control"
          │   │     InputType: Password
          │   │     Variable: ConfirmPassword
          │   │     Mandatory: False          ← BUG: should be True
          │   │     MaxLength: 50            ← BUG: should be 256
          │   │     Enabled: True
          │   │     (no tabindex)            ← BUG: should be tabindex=3
          │   │   (OnChange wired to Input_ConfirmPasswordOnChange — CORRECT)
          │   │
          │   └── Button — ToggleConfirmPwdBtn
          │         (no tabindex)
          │       ├── Text: "Button"         ← BUG: wrong text
          │       └── Text: "Show"
          │
          └── Container — SaveBtnContainer
                Style: "form-group"          ← BUG: should be "login-button margin-top-l" with ButtonLoading
                Visible: True
              └── Button — SavePasswordBtn
                    Style: "btn btn-primary"
                    IsDefault: False         ← BUG: should be True
                    Enabled: IsButtonEnabled and not IsExecuting  ← BUG: should be just IsButtonEnabled
                    OnClick: ResetPasswordOnClick (ValidateAndContinue)
                    (no tabindex)            ← BUG: should be tabindex=4
                  ├── Text: "Button"         ← BUG: leftover default text
                  └── Text: "Save Password" ← BUG: wrong case, should be "Save password"
```

**Missing sections vs reference:**
- No outer "login-screen" Container wrapping the Form
- Form name wrong: "RecoverPasswordForm" instead of "PasswordResetForm"
- No logo section (Logo image + h5 "Reset password" + instructions text)
- Email field: bare Expression+Text instead of disabled AnimatedLabel Input_Email
- No AnimatedLabel wrapping for Code, NewPassword, ConfirmPassword inputs
- No InputWithIcon wrapping (toggle visibility Links/Icons) for password inputs
- No ButtonLoading wrapping for submit button
- No "Not in the right place?" + Link → Login footer section
- Two toggle buttons (ToggleNewPwdBtn, ToggleConfirmPwdBtn) instead of Icon-based Links
