# UserProfile — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[BlockInstance] LayoutTopMenu  (block: Layouts/LayoutTopMenu)
  Parameters: all null/default (ExtendedClass, HasFixedHeader, EnableAccessibilityFeatures all unset)

  ├─ Placeholder: Header
  │  └─ [BlockInstance] (unnamed)  Menu  (block: Common/Menu)
  │        Parameters: ActiveSubItem → not set, ActiveItem → not set
  │
  ├─ Placeholder: Title
  │  └─ [Text] (unnamed)
  │        Text: "Your profile"
  │        Style: (none)
  │
  ├─ Placeholder: Actions
  │  └─ [If] (unnamed)
  │        Condition: IsExternal
  │        DesignMode: ShowFalse
  │     ├─ True branch: (empty)
  │     └─ False branch:
  │        └─ [Link] (unnamed)
  │              Style: (none)
  │              Enabled: True
  │              Visible: True
  │              OnClick → ChangePassword screen (no validation)
  │           └─ [Text] (unnamed)  Text: "Change your password"
  │
  └─ Placeholder: MainContent
     └─ [Form] ProfileDetailsForm
           Style: "form card"
           Width: (fill parent)
        └─ [BlockInstance] Columns2  (unnamed)
              PhoneBehavior → Entities.BreakColumns.All
              TabletBehavior → not set
              GutterSize → not set
              ExtendedClass → not set
           │
           ├─ Placeholder: Column1
           │  ├─ [Container] divPhoto
           │  │     Style: (none)
           │  │     CustomStyle: "height: 150px; margin-bottom: var(--space-m); text-align: center;"
           │  │     Visible: True
           │  │     Width: (fill parent)
           │  │  └─ [If] HasPhotoUrl
           │  │        Condition: GetUserDetails.List.Current.User.PhotoUrl <> ""
           │  │        DesignMode: ShowTrueOrPreview
           │  │     ├─ True branch:
           │  │     │  └─ [Image] (unnamed)
           │  │     │        Type: External URL
           │  │     │        URL: GetUserDetails.List.Current.User.PhotoUrl
           │  │     │        Width: 150px
           │  │     │        Style: "img-circle img-cover"
           │  │     │        CustomStyle: "height: 150px;"
           │  │     │        Extended: title=Client.UserName, alt="User photo"
           │  │     └─ False branch:
           │  │        └─ [Image] (unnamed)
           │  │              Type: Static, Image: User (static resource)
           │  │              Style: "img-circle img-cover"
           │  │              CustomStyle: "height: 150px;"
           │  │              Extended: alt="User photo placeholder"
           │  │
           │  ├─ [Container] divName  (style: "margin-top-base")
           │  │  └─ [BlockInstance] AnimatedLabel  (unnamed)
           │  │        ExtendedClass → not set
           │  │     ├─ Placeholder Label:
           │  │     │  └─ [Label] NameLabel → NameInput
           │  │     │        Text: "Name"
           │  │     └─ Placeholder Input:
           │  │        └─ [Input] NameInput
           │  │              Type: Text
           │  │              Variable: GetUserDetails.List.Current.User.Name
           │  │              Enabled: not IsExternal
           │  │              Mandatory: True
           │  │              MaxLength: (not set / null)
           │  │              Style: "form-control"
           │  │              OnChange → ValidateInputsOnChange (no built-in validation)
           │  │
           │  ├─ [Container] divPhotoURL  (style: "margin-top-base", CustomStyle: "margin-top: 10px;")
           │  │  └─ [BlockInstance] AnimatedLabel  (unnamed)
           │  │     ├─ Placeholder Label:
           │  │     │  └─ [Label] (unnamed) → PhotoUrlInput
           │  │     │        Text: "Photo URL"
           │  │     └─ Placeholder Input:
           │  │        └─ [Input] PhotoUrlInput
           │  │              Type: Text
           │  │              Variable: GetUserDetails.List.Current.User.PhotoUrl
           │  │              Enabled: not IsExternal
           │  │              Mandatory: False
           │  │              MaxLength: 2048
           │  │              Style: "form-control"
           │  │              onblur → ValidateInputsOnChange
           │  │              Extended: autocomplete="new-photourl"
           │  │
           │  ├─ [Container] divEmail  (style: "margin-top-base")
           │  │  └─ [BlockInstance] AnimatedLabel  (unnamed)
           │  │     ├─ Placeholder Label:
           │  │     │  └─ [Label] (unnamed) → EmailInput
           │  │     │        Text: "Email"
           │  │     └─ Placeholder Input:
           │  │        └─ [Input] EmailInput
           │  │              Type: Email
           │  │              Variable: GetUserDetails.List.Current.User.Email
           │  │              Enabled: not IsExternal
           │  │              Mandatory: True
           │  │              MaxLength: 256
           │  │              Style: "form-control"
           │  │              OnChange → ValidateInputsOnChange (no built-in validation)
           │  │              Extended: autocomplete="new-password"
           │  │
           │  ├─ [If] If_ShowGetCodeButton
           │  │     Condition: ShowGetCodeButton
           │  │     DesignMode: ShowAll
           │  │  ├─ True branch:
           │  │  │  └─ [If] If_ShowVerificationCode
           │  │  │        Condition: ShowVerificationCode
           │  │  │        DesignMode: ShowAll
           │  │  │     ├─ True branch:
           │  │  │     │  └─ [BlockInstance] Columns2  (unnamed)
           │  │  │     │        ExtendedClass → "align-items-center"
           │  │  │     │        PhoneBehavior → Entities.BreakColumns.All
           │  │  │     │        GutterSize → Entities.GutterSize.None
           │  │  │     │        TabletBehavior → not set
           │  │  │     │     ├─ Placeholder Column1:
           │  │  │     │     │  └─ [Container] divVerificationCode  (style: "padding-right-base", CustomStyle: "text-align: left;")
           │  │  │     │     │     └─ [BlockInstance] AnimatedLabel  (unnamed)
           │  │  │     │     │        ├─ Placeholder Label:
           │  │  │     │     │        │  └─ [Label] (unnamed) → VerificationCodeInput
           │  │  │     │     │        │        Text: "Verification code"
           │  │  │     │     │        └─ Placeholder Input:
           │  │  │     │     │           └─ [Input] VerificationCodeInput
           │  │  │     │     │                 Type: Text
           │  │  │     │     │                 Variable: VerificationCode
           │  │  │     │     │                 Enabled: True
           │  │  │     │     │                 Mandatory: ShowGetCodeButton
           │  │  │     │     │                 MaxLength: 6
           │  │  │     │     │                 Style: "form-control"
           │  │  │     │     │                 OnChange → ValidateInputsOnChange (no built-in validation)
           │  │  │     │     │                 Extended: autocomplete="new-validationcode"
           │  │  │     │     └─ Placeholder Column2:
           │  │  │     │        └─ [Link] (unnamed)
           │  │  │     │              Enabled: CountdownValue <= 0
           │  │  │     │              Style: (none)
           │  │  │     │              CustomStyle: "margin-bottom: 0px;"
           │  │  │     │              OnClick → SendVerificationCode (no validation)
           │  │  │     │           └─ [If] If_HaveRemainingTime
           │  │  │     │                 Condition: CountdownValue > 0
           │  │  │     │                 DesignMode: ShowAll
           │  │  │     │              ├─ True branch:
           │  │  │     │              │  └─ [Expression] (unnamed)
           │  │  │     │              │        Value: "Didn't get it? Resend in " + CountdownValue + "s"
           │  │  │     │              └─ False branch:
           │  │  │     │                 └─ [Expression] (unnamed)
           │  │  │     │                       Value: "Resend verification code"
           │  │  │     └─ False branch:
           │  │  │        └─ [Container] DivGetVerificationCode  (no style)
           │  │  │              Visible: True
           │  │  │              Width: (fill parent)
           │  │  │           └─ [BlockInstance] ButtonLoading  (unnamed)
           │  │  │                 IsLoading → IsExecuting_GetCode
           │  │  │                 ShowLabelOnLoading → True
           │  │  │                 ExtendedClass → not set
           │  │  │              └─ Placeholder Button:
           │  │  │                 └─ [Button] (unnamed)
           │  │  │                       Style: "btn btn-small"
           │  │  │                       IsDefault: False
           │  │  │                       Enabled: ShowGetCodeButton and not ShowVerificationCode
           │  │  │                       Visible: True
           │  │  │                       Width: (fill parent)
           │  │  │                       OnClick → SendVerificationCode (ValidateAndContinue)
           │  │  │                    ├─ [Container] (unnamed)  Style: "osui-btn-loading__spinner-animation"
           │  │  │                    └─ [Text] (unnamed)  Text: "Get verification code"
           │  │  └─ False branch: (empty)
           │  │
           │  └─ [If] If_ExternalUser
           │        Condition: IsExternal
           │        DesignMode: ShowAll
           │     ├─ True branch: (empty)
           │     └─ False branch:
           │        └─ [Container] divSaveChanges  (style: "margin-top-base")
           │              Visible: True
           │              Width: (fill parent)
           │           └─ [BlockInstance] ButtonLoading  btnSaveChanges
           │                 IsLoading → IsExecuting
           │                 ShowLabelOnLoading → True
           │                 ExtendedClass → not set
           │              └─ Placeholder Button:
           │                 └─ [Button] btnSave
           │                       Style: "btn btn-primary"
           │                       IsDefault: False
           │                       Enabled: IsButtonEnabled
           │                       Visible: True
           │                       Width: (fill parent)
           │                       OnClick → SaveChangesOnClick (ValidateAndContinue)
           │                    ├─ [Container] (unnamed)  Style: "osui-btn-loading__spinner-animation"
           │                    └─ [Text] (unnamed)  Text: "Save changes"
           │
           └─ Placeholder: Column2
              (empty — no widgets)
```

**Notes:**
- Header has Menu block directly (no wrapper container) — unlike InvalidPermissions which has a styled container + UserInfo
- Actions placeholder has the "Change your password" link (conditional on IsExternal=False) — NOT in MainContent
- divPhoto and divPhotoURL reference User.PhotoUrl — absent from some tenants (TestNewWebApp9 has no PhotoUrl field)
- LayoutTopMenu params all unset in reference (contrast: spec.md says HasFixedHeader=True)
- Verification code section uses nested If widgets, not visibility-based containers
- Save button is ButtonLoading (IsLoading=IsExecuting) inside If_ExternalUser/False branch
- Get code button is ButtonLoading (IsLoading=IsExecuting_GetCode) inside If_ShowGetCodeButton/If_ShowVerificationCode False branch
- Both ButtonLoading have ShowLabelOnLoading=True
