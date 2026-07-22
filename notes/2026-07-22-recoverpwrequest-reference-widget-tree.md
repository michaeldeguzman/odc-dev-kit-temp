# RecoverPasswordRequest — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-22 via Mentor inspection.

---

```
[BlockInstance] LayoutBlank  (block: Layouts/LayoutBlank)
  Parameters:
    EnableAccessibilityFeatures → (default/null)
    ExtendedClass → (null)
  └─ Placeholder: Content
     └─ [Container] (unnamed)
           Style: "login-screen"
           Visible: True
        └─ [Form] RecoverPasswordForm
              Style: "login-form"
              Width: ""
           ├─ [Container] (unnamed)
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
           │  │        Text: "Forgot your password?"
           │  │
           │  └─ [Container] (unnamed)
           │        Style: "margin-top-s"
           │        Visible: True
           │     └─ [Container] (unnamed)
           │           Visible: True
           │        └─ [Text] (unnamed)
           │              Text: "Don't worry, we'll send you an email with instructions."
           │
           ├─ [Container] (unnamed)
           │     Style: "login-inputs margin-top-m"
           │     Visible: True
           │  └─ [BlockInstance] AnimatedLabel  (block: OutSystemsUI/Interaction/AnimatedLabel)
           │        Parameters: ExtendedClass → (default/null)
           │     ├─ Placeholder: Label
           │     │  └─ [Label] (unnamed)
           │     │        Width: (fill parent)
           │     │        TargetWidget: Input_Email
           │     │     └─ [Text] (unnamed)
           │     │           Text: "Email"
           │     │
           │     └─ Placeholder: Input
           │        └─ [Input] Input_Email
           │              Style: "form-control"
           │              InputType: Email
           │              Variable: Email
           │              Mandatory: True
           │              MaxLength: 250
           │              Enabled: True
           │              Width: (fill parent)
           │              Extended properties: tabindex → 1
           │
           ├─ [Container] (unnamed)
           │     Style: "login-button margin-top-l"
           │     Visible: True
           │  └─ [BlockInstance] ButtonLoading  (block: OutSystemsUI/Utilities/ButtonLoading)
           │        Parameters:
           │          ExtendedClass → "full-width"
           │          IsLoading → IsExecuting
           │          ShowLabelOnLoading → (default/null)
           │     └─ Placeholder: Button
           │        └─ [Button] (unnamed)
           │              Style: "btn btn-primary"
           │              IsDefault (IsSubmit): True
           │              Enabled: True
           │              Visible: True
           │              Width: (fill parent)
           │              OnClick → ResetPasswordOnClick (ValidateAndContinue)
           │              Extended properties: tabindex → 2
           │           ├─ [Container] (unnamed)
           │           │     Style: "osui-btn-loading__spinner-animation"
           │           │     Visible: True
           │           └─ [Text] (unnamed)
           │                 Text: "Reset password"
           │
           └─ [Container] (unnamed)
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
                      tabindex → 3
                      aria-label → "Go to login page"
                 └─ [Text] (unnamed)
                       Text: "Go to login."
```
