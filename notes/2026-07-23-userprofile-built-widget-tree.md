# UserProfile — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[BlockInstance] LayoutTopMenu  (block: Layouts/LayoutTopMenu)
  Parameters:
    HasFixedHeader → True
    EnableAccessibilityFeatures → False
    ExtendedClass → ""

  ├─ Placeholder: Header
  │  └─ [Container] MenuPlaceholder        ← BUG: wrapper container should not be present
  │        Style: "menu-placeholder"
  │        Width: (fill parent)
  │        Visible: True
  │     └─ [BlockInstance] Menu  (Common/Menu)
  │           Parameters: ActiveItem → -1, ActiveSubItem → -1
  │
  ├─ Placeholder: Title
  │  └─ [Text] TitleText
  │        Text: "Your profile"
  │        Style: (none)
  │
  ├─ Placeholder: Actions                  ← BUG: ABSENT — no If/Link for "Change your password"
  │  (empty)
  │
  └─ Placeholder: MainContent
     └─ [Form] ProfileForm                 ← BUG: missing Columns2 wrapper inside form
           Style: "form card"
           Width: (fill parent)
        │
        ├─ [Container] NameContainer       ← BUG: wrong style ("form-group" vs "margin-top-base"); no AnimatedLabel
        │     Style: "form-group"
        │     Visible: True | Width: (fill parent)
        │  └─ [Input] Input_Name           ← BUG: Mandatory=False (should be True); Enabled=True (should be not IsExternal); MaxLength=256 (should be null/unset)
        │        Type: Text
        │        Variable: GetUserDetails.List.Current.User.Name
        │        Enabled: True
        │        Mandatory: False
        │        MaxLength: 256
        │        Style: "form-control"
        │        OnChange → ValidateInputsOnChange
        │
        ├─ [Container] EmailContainer      ← BUG: wrong style ("form-group" vs "margin-top-base"); no AnimatedLabel
        │     Style: "form-group"
        │     Visible: True | Width: (fill parent)
        │  └─ [Input] Input_Email          ← BUG: Mandatory=False; Enabled=True; no autocomplete
        │        Type: Email
        │        Variable: GetUserDetails.List.Current.User.Email
        │        Enabled: True
        │        Mandatory: False
        │        MaxLength: 256
        │        Style: "form-control"
        │        OnChange → ValidateInputsOnChange
        │
        ├─ [Container] VerifContainer      ← BUG: should be inside If_ShowGetCodeButton→If_ShowVerificationCode True branch (not visibility prop)
        │     Style: (none)
        │     Visible: ShowVerificationCode   ← BUG: visibility prop instead of If widget
        │     Animate: true | Width: (fill parent)
        │  └─ [Input] Input_VerificationCode ← BUG: MaxLength=50 (should be 6); no autocomplete; no AnimatedLabel; Mandatory=False (should be ShowGetCodeButton)
        │        Type: Text
        │        Variable: VerificationCode
        │        Enabled: True
        │        Mandatory: False
        │        MaxLength: 50
        │        Style: "form-control"
        │        OnChange → ValidateInputsOnChange
        │
        ├─ [Container] GetCodeContainer    ← BUG: should be If_ShowGetCodeButton/If_ShowVerificationCode False branch; plain Button→ButtonLoading
        │     Style: (none)
        │     Visible: ShowGetCodeButton      ← BUG: visibility prop instead of If widget
        │     Animate: true | Width: (fill parent)
        │  └─ [Button] GetCodeBtn           ← BUG: should be ButtonLoading wrapper; style "btn btn-secondary" (should be "btn btn-small"); IsDefault=True (should be False); Enabled=not IsExecuting_GetCode (should be ShowGetCodeButton and not ShowVerificationCode)
        │        Style: "btn btn-secondary"
        │        IsDefault: True
        │        Enabled: not IsExecuting_GetCode
        │        Visible: True | Width: (auto)
        │        OnClick → SendVerificationCode (ValidateAndContinue)
        │     ├─ [Text] (unnamed)  Text: "Save"     ← stray leftover text
        │     └─ [Text] GetCodeBtnText  Text: "Get verification code"
        │
        ├─ [Container] CountdownContainer  ← BUG: should be Column2 of inner Columns2 inside If_ShowGetCodeButton/If_ShowVerificationCode True branch; not a sibling container
        │     Style: (none)
        │     Visible: ShowVerificationCode and CountdownValue > 0   ← BUG: wrong structure
        │     Animate: true | Width: (fill parent)
        │  └─ [Expression] CountdownExpr
        │        Value: "Resend in " + CountdownValue + "s"   ← BUG: should be inside If_HaveRemainingTime True:"Didn't get it? Resend in X s" / False:"Resend verification code"
        │
        ├─ [Container] SaveBtnContainer    ← BUG: style "form-group" (should be "margin-top-base"); not wrapped in If_ExternalUser False; no ButtonLoading
        │     Style: "form-group"
        │     Visible: True | Width: (fill parent)
        │  └─ [Button] SaveChangesBtn      ← BUG: should be ButtonLoading; Enabled=IsButtonEnabled and not IsExecuting (should be IsButtonEnabled only); IsDefault=False OK
        │        Style: "btn btn-primary"
        │        IsDefault: False
        │        Enabled: IsButtonEnabled and not IsExecuting
        │        Visible: True | Width: (auto)
        │        OnClick → SaveChangesOnClick (ValidateAndContinue)
        │     ├─ [Text] (unnamed)  Text: "Button"   ← stray leftover text
        │     └─ [Text] SaveChangesBtnText  Text: "Save changes"
        │
        └─ [Container] ChangePwdContainer  ← BUG: entire "Change password" link should be in Actions placeholder, not MainContent
              Style: (none)
              Visible: not IsExternal   ← BUG: should be If_ExternalUser False branch in Actions
              Animate: true | Width: (fill parent)
           └─ [Link] ChangePwdLink        ← BUG: style "link" (should be no style); OnClick ValidateAndContinue (should be no validation); text "Change password" (should be "Change your password")
                 Style: "link"
                 Enabled: True | Visible: True | Width: (auto)
                 OnClick → ChangePassword (ValidateAndContinue)
              ├─ [Text] (unnamed)  Text: "link"    ← stray leftover text
              └─ [Text] ChangePwdText  Text: "Change password"
```

**Missing vs reference:**
- Header: remove MenuPlaceholder container wrapper; Menu block goes directly in Header placeholder
- Actions placeholder: absent → needs If(IsExternal, ShowFalse)/False: Link(no style, no validation)→ChangePassword→"Change your password"
- MainContent: needs Columns2 block wrapping all content → Column1
- divPhoto: absent (reference has photo display If/Images — skip for this tenant, no PhotoUrl field)
- divPhotoURL: absent (reference has AnimatedLabel→PhotoUrlInput — skip for this tenant)
- Name field: container style wrong, missing AnimatedLabel, input Mandatory/Enabled/MaxLength wrong
- Email field: container style wrong, missing AnimatedLabel, input Mandatory/Enabled/autocomplete wrong
- Verification code section: flat visibility-based containers → nested If structure with Columns2
- GetCode button: plain Button → ButtonLoading, style/IsDefault/Enabled wrong
- Countdown: wrong location and structure → Column2 of inner Columns2 with If_HaveRemainingTime
- Save button: container style wrong, missing ButtonLoading, missing If_ExternalUser wrapper, Enabled expression wrong
- ChangePwdContainer+Link: moved to Actions placeholder, style removed, validation removed, text corrected
