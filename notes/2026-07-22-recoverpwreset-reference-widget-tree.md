# RecoverPasswordReset — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-22 via Mentor inspection.

---

```
[BlockInstance] LayoutBlank  (block: Layouts/LayoutBlank)
  └─ Placeholder: Content
     └─ [Container] (unnamed)
           Style: "login-screen"
           Visible: True
        └─ [Form] PasswordResetForm
              Style: "login-form"
              Width: ""
           ├─ [Container] (unnamed)                    ← Section A: logo
           │     Style: "login-logo"
           │     CustomStyle: text-align: center;
           │     Visible: True
           │  ├─ [Container] (unnamed)
           │  │     CustomStyle: text-align: center;
           │  │     Visible: True
           │  │  └─ [Image] (unnamed)
           │  │        CustomStyle: height: 100px;
           │  │        Type: Static
           │  │        Image: Logo
           │  │        Extended properties: alt → ""
           │  │
           │  ├─ [AdvancedHtml] (unnamed)   Tag: h5
           │  │     Extended properties: class → "margin-top-base text-neutral-8"
           │  │  └─ [Text] (unnamed)
           │  │        Text: "Reset password"
           │  │
           │  └─ [Container] (unnamed)
           │        Style: "margin-top-s"
           │        Visible: True
           │     └─ [Container] (unnamed)
           │           Visible: True
           │        └─ [Text] (unnamed)
           │              Text: "If the entered email is correct, we'll send a verification code to that email. Please enter the code below to verify your identity."
           │
           ├─ [Container] (unnamed)                    ← Section B: fields (no style)
           │     Visible: True
           │  ├─ [Container] (unnamed)                 ← B1: Email (disabled)
           │  │     Style: "login-inputs margin-top-m"
           │  │     Visible: True
           │  │  └─ [BlockInstance] AnimatedLabel
           │  │        Parameters: ExtendedClass → (default/null)
           │  │     ├─ Placeholder: Label
           │  │     │  └─ [Label] (unnamed)
           │  │     │        TargetWidget: Input_Email
           │  │     │     └─ [Text] (unnamed)
           │  │     │           Text: "Email"
           │  │     │
           │  │     └─ Placeholder: Input
           │  │        └─ [Input] Input_Email
           │  │              InputType: Email
           │  │              Variable: Email
           │  │              Mandatory: True
           │  │              MaxLength: 250
           │  │              Enabled: False              ← read-only display
           │  │              Placeholder: "mary.smith@acme.com"
           │  │              Width: (fill parent)
           │  │              (no tabindex)
           │  │
           │  ├─ [Container] (unnamed)                 ← B2: Verification code
           │  │     Style: "login-inputs margin-top-m"
           │  │     Visible: True
           │  │  └─ [BlockInstance] AnimatedLabel
           │  │     ├─ Placeholder: Label
           │  │     │  └─ [Label] (unnamed)
           │  │     │     └─ [Text] (unnamed)
           │  │     │           Text: "Verification code"
           │  │     │
           │  │     └─ Placeholder: Input
           │  │        └─ [Input] Input_Code
           │  │              InputType: Text
           │  │              Variable: Code
           │  │              Mandatory: True
           │  │              Enabled: True
           │  │              Width: (fill parent)
           │  │              OnChange: Input_CodeOnChange
           │  │              Extended properties: tabindex → 1
           │  │
           │  ├─ [Container] (unnamed)                 ← B3: New password + InputWithIcon
           │  │     Style: "margin-top-base password-input"
           │  │     Visible: True
           │  │  └─ [BlockInstance] AnimatedLabel
           │  │     ├─ Placeholder: Label
           │  │     │  └─ [Label] (unnamed)
           │  │     │     └─ [Text] (unnamed)
           │  │     │           Text: "New password"
           │  │     │
           │  │     └─ Placeholder: Input
           │  │        └─ [BlockInstance] InputWithIcon
           │  │              Parameters: AlignIconRight → True
           │  │           ├─ Placeholder: Icon
           │  │           │  └─ [Link] (unnamed)
           │  │           │        OnClick: ToggleNewPasswordVisibility (no validation)
           │  │           │     └─ [If] PasswordVisibile
           │  │           │           Condition: IsPasswordVisible
           │  │           │           ShowTrueOrPreview: True
           │  │           │        ├─ True: [Icon] (unnamed)  PhosphorIcon: eye-slash  Style: "icon"  Size: FontSize
           │  │           │        └─ False: [Icon] (unnamed)  PhosphorIcon: eye  Style: "icon"  Size: FontSize
           │  │           │
           │  │           └─ Placeholder: Input
           │  │              └─ [Input] Input_NewPassword
           │  │                    Style: "form-control login-password"
           │  │                    CustomStyle: padding-right: var(--space-xl);
           │  │                    InputType: Password
           │  │                    Variable: NewPassword
           │  │                    Mandatory: True
           │  │                    MaxLength: 256
           │  │                    Enabled: True
           │  │                    Width: (fill parent)
           │  │                    Extended properties: tabindex → 2
           │  │
           │  ├─ [BlockInstance] PasswordPolicy       ← B4: Password policy checker
           │  │     Parameters:
           │  │       Password → NewPassword
           │  │       Compliant → PasswordPolicyCompliant
           │  │       IsValid → IsValid
           │  │
           │  └─ [Container] (unnamed)                ← B5: Confirm password + InputWithIcon
           │        Style: "margin-top-base password-input"
           │        Visible: True
           │     └─ [BlockInstance] AnimatedLabel
           │        ├─ Placeholder: Label
           │        │  └─ [Label] (unnamed)
           │        │     └─ [Text] (unnamed)
           │        │           Text: "Confirm password"
           │        │
           │        └─ Placeholder: Input
           │           └─ [BlockInstance] InputWithIcon
           │                 Parameters: AlignIconRight → True
           │              ├─ Placeholder: Icon
           │              │  └─ [Link] (unnamed)
           │              │        OnClick: ToggleConfirmPasswordVisibility (no validation)
           │              │     └─ [If] ConfirmPasswordVisibile
           │              │           Condition: IsConfirmPasswordVisible
           │              │           ShowTrueOrPreview: True
           │              │        ├─ True: [Icon] (unnamed)  PhosphorIcon: eye-slash  Style: "icon"  Size: FontSize
           │              │        └─ False: [Icon] (unnamed)  PhosphorIcon: eye  Style: "icon"  Size: FontSize
           │              │
           │              └─ Placeholder: Input
           │                 └─ [Input] Input_ConfirmPassword
           │                       Style: "form-control login-password"
           │                       CustomStyle: padding-right: var(--space-xl);
           │                       InputType: Password
           │                       Variable: ConfirmPassword
           │                       Mandatory: True
           │                       MaxLength: 256
           │                       Enabled: True
           │                       Width: (fill parent)
           │                       OnChange: Input_ConfirmPasswordOnChange
           │                       Extended properties: tabindex → 3
           │
           ├─ [Container] (unnamed)                   ← Section C: submit button
           │     Style: "login-button margin-top-l"
           │     Visible: True
           │  └─ [BlockInstance] ButtonLoading
           │        Parameters:
           │          IsLoading → IsExecuting
           │          ExtendedClass → "full-width"
           │          ShowLabelOnLoading → (default/null)
           │     └─ Placeholder: Button
           │        └─ [Button] (unnamed)
           │              Style: "btn btn-primary"
           │              IsDefault (IsSubmit): True
           │              Enabled: IsButtonEnabled
           │              Visible: True
           │              Width: (fill parent)
           │              OnClick → ResetPasswordOnClick (ValidateAndContinue)
           │              Extended properties: tabindex → 4
           │           ├─ [Container] (unnamed)
           │           │     Style: "osui-btn-loading__spinner-animation"
           │           │     Visible: True
           │           └─ [Text] (unnamed)
           │                 Text: "Save password"
           │
           └─ [Container] (unnamed)                   ← Section D: footer
                 Style: "margin-top-m"
                 CustomStyle: text-align: center;
                 Visible: True
              ├─ [Text] (unnamed)
              │     Text: "Not in the right place?"
              │
              └─ [Link] (unnamed)
                    Enabled: True
                    Visible: True
                    OnClick → Login (Common/Login, no validation)
                    Extended properties:
                      tabindex → 5
                      aria-label → "Go to login page"
                 └─ [Text] (unnamed)
                       Text: "Go to login."
```
