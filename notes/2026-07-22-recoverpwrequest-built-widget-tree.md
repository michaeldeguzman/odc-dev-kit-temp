# RecoverPasswordRequest — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-22 via Mentor inspection.

---

```
WebBlockInstance — LayoutBlank
  Block: LayoutBlank (from Layouts flow)
  Input parameters:
    EnableAccessibilityFeatures → "False"
    ExtendedClass → ""

  └── [Placeholder: MainContent]

      └── Form — RecoverPasswordForm
            Style: "form card"                ← BUG: should be "login-form"
            Width: (fill parent)
            (no outer "login-screen" Container)   ← BUG: missing wrapper

          ├── Container — EmailContainer
          │     Style: "form-group"           ← BUG: should be "login-inputs margin-top-m" with AnimatedLabel
          │     Visible: True
          │
          │   └── Input — Input_Email
          │         Style: "form-control"
          │         InputType: Email
          │         Variable: Email
          │         Enabled: not IsExecuting  ← BUG: should be True (ButtonLoading controls loading state)
          │         Mandatory: False          ← BUG: should be True
          │         MaxLength: 50             ← BUG: should be 250
          │         (no tabindex)             ← BUG: should be tabindex=1
          │
          └── Container — BtnContainer
                Style: "form-group"           ← BUG: should be "login-button margin-top-l" with ButtonLoading
                Visible: True

              └── Button — ResetPasswordBtn
                    Style: "btn btn-primary"
                    Enabled: not IsExecuting  ← BUG: should be True (ButtonLoading controls this)
                    IsDefault (IsSubmit): true
                    OnClick: ResetPasswordOnClick (ValidateAndContinue)
                    (no tabindex)             ← BUG: should be tabindex=2

                  ├── Text — (unnamed)
                  │     Text: "Save"          ← BUG: leftover default text node
                  │
                  └── Text — ResetPasswordBtnText
                        Text: "Reset Password" ← BUG: wrong case, should be "Reset password"
```

**Missing sections vs reference:**
- No outer "login-screen" Container wrapping the Form
- No logo section (Logo image + h5 "Forgot your password?" + "Don't worry..." text)
- No AnimatedLabel wrapping for email input
- No ButtonLoading wrapping for button
- No "Not in the right place?" + Link → Login footer section
