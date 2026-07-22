# Login Screen — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-22 via Mentor inspection.

---

```
WebBlockInstance — LayoutBlank
  Style/ExtendedClass: (none / CustomStyle: null)
  Block: LayoutBlank (from Layouts flow)
  Input parameters:
    EnableAccessibilityFeatures → "False"
    ExtendedClass → ""

  └── [Placeholder: MainContent]

      ├── Form — LoginForm
      │     Style: "form card"
      │     Width: (fill parent)
      │
      │   ├── Container — EmailContainer
      │   │     Style: "form-group"
      │   │     Visible: True
      │   │     Width: (fill parent)
      │   │
      │   │   └── Input — Input_Email
      │   │         Style: "form-control"
      │   │         InputType: Email
      │   │         Variable: UserEmail
      │   │         Placeholder: (none)
      │   │         Enabled: ExecutingIndex = -1 and not IsBuiltInExecuting
      │   │         Mandatory: False
      │   │         MaxLength: 50
      │   │         Width: (fill parent)
      │   │         OnChange: (none)
      │   │
      │   ├── Container — PasswordContainer
      │   │     Style: "form-group"
      │   │     Visible: True
      │   │     Width: (fill parent)
      │   │
      │   │   ├── Input — Input_Password
      │   │   │     Style: "form-control"
      │   │   │     InputType: Password
      │   │   │     Variable: Password
      │   │   │     Placeholder: (none)
      │   │   │     Enabled: ExecutingIndex = -1 and not IsBuiltInExecuting
      │   │   │     Mandatory: False
      │   │   │     MaxLength: 50
      │   │   │     Width: (fill parent)
      │   │   │     OnChange: (none)
      │   │   │
      │   │   └── Button — TogglePasswordBtn
      │   │         Style: "btn-icon"
      │   │         Enabled: True
      │   │         Visible: True
      │   │         IsDefault (IsSubmit): true         ← BUG: should be false; triggers form submit
      │   │         Width: (default/empty)
      │   │         OnClick: OnTogglePasswordVisibility (ValidateAndContinue)
      │   │
      │   │       ├── Text — (unnamed)
      │   │       │     Text: "Save"                  ← BUG: literal "Save" (should be eye icon)
      │   │       │
      │   │       └── Text — TogglePwdText
      │   │             Text: "Show"                  ← BUG: literal "Show" (should be eye icon)
      │   │             (renders as "SaveShow" with no spacing)
      │   │
      │   └── Container — LoginBtnContainer
      │         Style: "form-group"
      │         Visible: True
      │         Width: (fill parent)
      │
      │       ├── WebBlockInstance — ButtonLoading
      │       │     Block: ButtonLoading (from OutSystemsUI / Utilities flow)
      │       │     Input parameters:
      │       │       ShowLabelOnLoading → (null)
      │       │       IsLoading → IsBuiltInExecuting
      │       │       ExtendedClass → (null)
      │       │
      │       │   └── [Placeholder: Button]
      │       │
      │       │       ├── Button — (unnamed)                ← BUG: duplicate button #1
      │       │       │     Style: "btn btn-primary"
      │       │       │     Enabled: True
      │       │       │     Visible: True
      │       │       │     IsDefault (IsSubmit): false
      │       │       │     Width: (fill parent)
      │       │       │     OnClick: LoginOnClick (ValidateAndContinue)
      │       │       │
      │       │       │   ├── Container — (unnamed)
      │       │       │   │     Style: "osui-btn-loading__spinner-animation"
      │       │       │   │     Visible: True
      │       │       │   │     Width: (fill parent)
      │       │       │   │
      │       │       │   └── Text — (unnamed)
      │       │       │         Text: "text"           ← BUG: literal "text" caption
      │       │       │
      │       │       └── Button — LoginBtnInLoading         ← BUG: duplicate button #2
      │       │             Style: "btn btn-primary"
      │       │             Enabled: True
      │       │             Visible: True
      │       │             IsDefault (IsSubmit): false
      │       │             Width: (default/empty)
      │       │             OnClick: LoginOnClick (ValidateAndContinue)
      │       │
      │       │           ├── Text — (unnamed)
      │       │           │     Text: "Button"         ← BUG: literal "Button"
      │       │           │
      │       │           └── Text — LoginBtnInLoadingText
      │       │                 Text: "Log in"
      │       │
      │       └── Button — LoginBtn                        ← BUG: third standalone button outside ButtonLoading
      │             Style: "btn btn-primary"
      │             Enabled: not IsBuiltInExecuting and ExecutingIndex = -1
      │             Visible: True
      │             IsDefault (IsSubmit): false
      │             Width: (default/empty)
      │             OnClick: LoginOnClick (ValidateAndContinue)
      │
      │           ├── Text — (unnamed)
      │           │     Text: "Button"                 ← BUG: literal "Button"
      │           │
      │           └── Text — LoginBtnText
      │                 Text: "Log in"
      │
      └── Container — ExternalProvidersContainer
            Style: (none)
            Visible: ShowExternalProvider
            Animate: true
            Width: (fill parent)

          └── List — ExternalProvidersList
                Style: "list list-group"
                Source: ExternalIdentityProviders
                AnimateItems: true
                Tag: div
                Width: (fill parent)

              └── Button — ExternalProviderBtn
                    Style: "btn"
                    Enabled: ExecutingIndex = -1 and not IsBuiltInExecuting
                    Visible: True
                    IsDefault (IsSubmit): false
                    Width: (default/empty)
                    OnClick: LoginProviderOnClick (no built-in validation)
                      ProviderIndex → 0                ← BUG: hardcoded 0, not CurrentRowNumber
                      ProviderKey → ExternalIdentityProviders.Current.Key

                  └── Text — (unnamed)
                        Text: "Button"                 ← BUG: literal "Button"
```
