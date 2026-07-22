# ChangePassword — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-22 via Mentor inspection.

---

```
[BlockInstance] LayoutTopMenu  (block: Layouts/LayoutTopMenu)
  Parameters: EnableAccessibilityFeatures → (default/null), ExtendedClass → (null), HasFixedHeader → (null)

  ├─ Placeholder: Header
  │  └─ [BlockInstance] Menu  (block: Common/Menu)
  │        Parameters: ActiveItem → (unset), ActiveSubItem → (unset)
  │
  ├─ Placeholder: Breadcrumbs
  │  └─ [Link] (unnamed)
  │        Enabled: True
  │        Visible: True
  │        OnClick → UserProfile (Common/UserProfile, no validation)
  │     ├─ [Icon] (unnamed)
  │     │     PhosphorIcon: caret-left
  │     │     Size: FontSize
  │     │     Style: "icon"
  │     │     Weight: regular
  │     └─ [Text] (unnamed)
  │           Text: "Back to profile"
  │           CustomStyle: margin-left: 5px;
  │
  ├─ Placeholder: Title
  │  └─ [Text] (unnamed)
  │        Text: "Change your password"
  │
  └─ Placeholder: MainContent
     └─ [BlockInstance] Columns2  (block: OutSystemsUI/Adaptive/Columns2)
           Parameters: ExtendedClass → (null), GutterSize → (null), PhoneBehavior → (null), TabletBehavior → (null)
        └─ Placeholder: Column1
           └─ [Form] Form
                 Style: "form card"
                 Width: (fill parent)

              ├─ [Container] (unnamed)                        ← Child 1: Old password
              │     (no style)
              │     Visible: True
              │     Width: (fill parent)
              │  └─ [BlockInstance] AnimatedLabel  (OutSystemsUI/Interaction/AnimatedLabel)
              │        Parameters: ExtendedClass → (null)
              │     ├─ Placeholder: Label
              │     │  └─ [Label] (unnamed)
              │     │        Width: (fill parent)
              │     │        TargetWidget: Input_OldPassword
              │     │     └─ [Text] (unnamed)
              │     │           Text: "Current password"
              │     └─ Placeholder: Input
              │        └─ [Input] Input_OldPassword
              │              Style: "form-control"
              │              InputType: Password
              │              Variable: OldPassword
              │              Mandatory: True
              │              MaxLength: 256
              │              Enabled: True
              │              Width: (fill parent)
              │              OnChange: Input_OldPasswordOnChange
              │              Extended properties:
              │                autocomplete → "current-password"
              │                tabindex → 1
              │
              ├─ [Container] (unnamed)                        ← Child 2: New password
              │     Style: "margin-top-base"
              │     Visible: True
              │     Width: (fill parent)
              │  └─ [BlockInstance] AnimatedLabel  (OutSystemsUI/Interaction/AnimatedLabel)
              │        Parameters: ExtendedClass → (null)
              │     ├─ Placeholder: Label
              │     │  └─ [Label] (unnamed)
              │     │        Width: (fill parent)
              │     │        TargetWidget: Input_NewPassword
              │     │     └─ [Text] (unnamed)
              │     │           Text: "New password"
              │     └─ Placeholder: Input
              │        └─ [BlockInstance] InputWithIcon  (OutSystemsUI/Interaction/InputWithIcon)
              │              Parameters: ExtendedClass → "padding-left-none", AlignIconRight → True
              │           ├─ Placeholder: Icon
              │           │  └─ [Link] (unnamed)
              │           │        Enabled: True
              │           │        Visible: True
              │           │        OnClick: OnToggleNewPasswordVisibility (no validation)
              │           │     └─ [If] PasswordVisible
              │           │           Condition: IsPasswordVisible
              │           │           ShowTrueOrPreview: True
              │           │        ├─ True: [Icon] (unnamed) PhosphorIcon: eye-slash  Style: "icon"  Size: FontSize  Weight: regular
              │           │        └─ False: [Icon] (unnamed) PhosphorIcon: eye  Style: "icon"  Size: FontSize  Weight: regular
              │           └─ Placeholder: Input
              │              └─ [Input] Input_NewPassword
              │                    Style: "form-control login-password padding-left-none"
              │                    CustomStyle: padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;
              │                    InputType: Password
              │                    Variable: NewPassword
              │                    Mandatory: True
              │                    MaxLength: 256
              │                    Enabled: True
              │                    Width: (fill parent)
              │                    Extended properties:
              │                      autocomplete → "new-password"
              │                      tabindex → 2
              │
              ├─ [BlockInstance] PasswordPolicy               ← Child 3: Password policy
              │     Parameters:
              │       Password → NewPassword
              │       Compliant → PasswordPolicyCompliant (event handler)
              │       IsValid → IsValid
              │
              ├─ [Container] (unnamed)                        ← Child 4: Confirm password
              │     Style: "margin-top-base"
              │     Visible: True
              │     Width: (fill parent)
              │  └─ [BlockInstance] AnimatedLabel  (OutSystemsUI/Interaction/AnimatedLabel)
              │        Parameters: ExtendedClass → (null)
              │     ├─ Placeholder: Label
              │     │  └─ [Label] (unnamed)
              │     │        Width: (fill parent)
              │     │        TargetWidget: Input_ConfirmPassword
              │     │     └─ [Text] (unnamed)
              │     │           Text: "Confirm password"
              │     └─ Placeholder: Input
              │        └─ [BlockInstance] InputWithIcon  (OutSystemsUI/Interaction/InputWithIcon)
              │              Parameters: ExtendedClass → "padding-left-none", AlignIconRight → True
              │           ├─ Placeholder: Icon
              │           │  └─ [Link] (unnamed)
              │           │        Enabled: True
              │           │        Visible: True
              │           │        OnClick: OnToggleConfirmPasswordVisibility (no validation)
              │           │     └─ [If] PasswordVisible2
              │           │           Condition: IsPasswordVisible     ← NOTE: reuses IsPasswordVisible (not IsConfirmPasswordVisible)
              │           │           ShowTrueOrPreview: True
              │           │        ├─ True: [Icon] (unnamed) PhosphorIcon: eye-slash  Style: "icon"  Size: FontSize  Weight: regular
              │           │        └─ False: [Icon] (unnamed) PhosphorIcon: eye  Style: "icon"  Size: FontSize  Weight: regular
              │           └─ Placeholder: Input
              │              └─ [Input] Input_ConfirmPassword
              │                    Style: "form-control login-password padding-left-none"
              │                    CustomStyle: padding-bottom: 0px; padding-left: 0px; padding-right: var(--space-xl); padding-top: 0px;
              │                    InputType: Password
              │                    Variable: ConfirmPassword
              │                    Mandatory: True
              │                    MaxLength: 256
              │                    Enabled: True
              │                    Width: (fill parent)
              │                    OnChange: Input_ConfirmPasswordOnChange
              │                    Extended properties:
              │                      tabindex → 3
              │
              └─ [Container] (unnamed)                        ← Child 5: Submit button
                    (no style)
                    Visible: True
                    Width: (fill parent)
                 └─ [BlockInstance] ButtonLoading  (OutSystemsUI/Utilities/ButtonLoading)
                       Parameters:
                         IsLoading → IsExecuting
                         ExtendedClass → "full-width"
                         ShowLabelOnLoading → (null)
                    └─ Placeholder: Button
                       └─ [Button] (unnamed)
                             Style: "btn btn-primary margin-top-l"
                             IsDefault (IsSubmit): True
                             Enabled: IsButtonEnabled
                             Visible: True
                             Width: (fill parent)
                             OnClick → SetNewPasswordOnClick (ValidateAndContinue)
                             Extended properties: tabindex → 4
                          ├─ [Container] (unnamed)
                          │     Style: "osui-btn-loading__spinner-animation"
                          │     Visible: True
                          └─ [Text] (unnamed)
                                Text: "Set new password"
```

**Notes:**
- The `PasswordVisible2` If widget in the Confirm password field also uses `IsPasswordVisible` (not `IsConfirmPasswordVisible`) — matches the reference; not a bug
- LayoutTopMenu parameters are all unset (null/default) in the reference — no explicit HasFixedHeader, ExtendedClass, or EnableAccessibilityFeatures values
- Menu block parameters are unset in the reference — no explicit ActiveItem or ActiveSubItem values
