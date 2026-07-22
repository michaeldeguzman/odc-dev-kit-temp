# UserProfile — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Note:** Reference has divPhoto + divPhotoURL sections referencing User.PhotoUrl. TestNewWebApp9's User entity has no PhotoUrl field — these sections are omitted from the fix scope.

## 1. Header placeholder

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Header structure | Menu block directly in Header placeholder (no wrapper container) | Container "menu-placeholder" wrapping Menu block |

## 2. Actions placeholder

| # | Element | Reference | Built |
|---|---|---|---|
| 2 | Actions placeholder content | If (IsExternal, ShowFalse) / False: Link (no style, no validation, OnClick→ChangePassword) → "Change your password" | Absent — the "Change password" link lives in MainContent instead |

## 3. MainContent structure

| # | Element | Reference | Built |
|---|---|---|---|
| 3 | Columns2 wrapper | Columns2 block (PhoneBehavior=BreakColumns.All) inside form → Column1 contains all content | Absent — all children are direct form children |

## 4. Name field

| # | Element | Reference | Built |
|---|---|---|---|
| 4 | Container style | "margin-top-base" | "form-group" |
| 5 | AnimatedLabel | Present (unnamed, ExtendedClass not set) | Absent — bare Input |
| 6 | Label | NameLabel → NameInput, Text "Name" | Absent |
| 7 | NameInput.Mandatory | True | False |
| 8 | NameInput.Enabled | not IsExternal | True |
| 9 | NameInput.MaxLength | (not set / null) | 256 |

## 5. Email field

| # | Element | Reference | Built |
|---|---|---|---|
| 10 | Container style | "margin-top-base" | "form-group" |
| 11 | AnimatedLabel | Present (unnamed) | Absent — bare Input |
| 12 | Label | (unnamed) → EmailInput, Text "Email" | Absent |
| 13 | EmailInput.Mandatory | True | False |
| 14 | EmailInput.Enabled | not IsExternal | True |
| 15 | EmailInput.autocomplete | "new-password" | Absent |

## 6. Verification code section structure

| # | Element | Reference | Built |
|---|---|---|---|
| 16 | Outer If widget | If_ShowGetCodeButton (ShowGetCodeButton, ShowAll) → entire verification section | Absent — flat sibling containers |
| 17 | Inner If widget | If_ShowVerificationCode (ShowVerificationCode, ShowAll) inside True branch | Absent |
| 18 | VerifContainer.Visible | Not a visibility prop — governed by If_ShowVerificationCode True branch | Visible=ShowVerificationCode (property-based) |
| 19 | VerificationCodeInput.MaxLength | 6 | 50 |
| 20 | VerificationCodeInput.Mandatory | ShowGetCodeButton | False |
| 21 | VerificationCodeInput.autocomplete | "new-validationcode" | Absent |
| 22 | AnimatedLabel on verification input | Present (Label "Verification code", divVerificationCode "padding-right-base", CustomStyle "text-align: left;") | Absent |

## 7. Countdown / resend section

| # | Element | Reference | Built |
|---|---|---|---|
| 23 | Countdown location | Column2 of inner Columns2 (inside If_ShowGetCodeButton True / If_ShowVerificationCode True) | CountdownContainer — sibling of other containers |
| 24 | Countdown structure | Link (Enabled=CountdownValue<=0, CustomStyle "margin-bottom: 0px;", OnClick→SendVerificationCode no validation) → If_HaveRemainingTime: True: "Didn't get it? Resend in " + CountdownValue + "s" / False: "Resend verification code" | Expression "Resend in " + CountdownValue + "s" (no link, no If, no resend text) |

## 8. Get code button

| # | Element | Reference | Built |
|---|---|---|---|
| 25 | ButtonLoading wrapper | ButtonLoading (IsLoading=IsExecuting_GetCode, ShowLabelOnLoading=True) inside If_ShowVerificationCode False branch | Plain Button directly |
| 26 | Button.Style | "btn btn-small" | "btn btn-secondary" |
| 27 | Button.IsDefault | False | True |
| 28 | Button.Enabled | ShowGetCodeButton and not ShowVerificationCode | not IsExecuting_GetCode |
| 29 | Stray text node | Absent | Text "Save" (leftover) |

## 9. Save changes button

| # | Element | Reference | Built |
|---|---|---|---|
| 30 | If_ExternalUser wrapper | If_ExternalUser (IsExternal, ShowAll) / False: divSaveChanges | Absent — SaveBtnContainer always visible |
| 31 | Container style | "margin-top-base" | "form-group" |
| 32 | ButtonLoading wrapper | ButtonLoading (btnSaveChanges, IsLoading=IsExecuting, ShowLabelOnLoading=True) | Absent — plain Button |
| 33 | Button.Enabled | IsButtonEnabled | IsButtonEnabled and not IsExecuting |
| 34 | Stray text node | Absent | Text "Button" (leftover) |

## 10. Change password link (moved to Actions)

| # | Element | Reference | Built |
|---|---|---|---|
| 35 | Location | Actions placeholder (If_ExternalUser False branch) | MainContent (ChangePwdContainer) |
| 36 | Link.Style | (no style) | "link" |
| 37 | Link.OnClick validation | No validation | ValidateAndContinue |
| 38 | Link text | "Change your password" | "Change password" |
| 39 | Stray text node | Absent | Text "link" (leftover) |

**Count: 39 discrepancies**

## Fix scope

This tenant has no User.PhotoUrl — skip divPhoto and divPhotoURL sections entirely.

Specific actions:
1. **Header**: Remove MenuPlaceholder container; put Menu block directly in Header placeholder (params unset)
2. **Actions**: Add If (unnamed, Condition: IsExternal, ShowFalse) → False: Link (no style, no validation, OnClick→ChangePassword) → Text "Change your password"
3. **MainContent**: Add Columns2 block (PhoneBehavior=BreakColumns.All, all others unset) inside ProfileDetailsForm; move all form children into Column1; Column2 stays empty
4. **Name field**: Change NameContainer style to "margin-top-base"; add AnimatedLabel (NameLabel→NameInput, "Name"); fix NameInput: Mandatory=True, Enabled=not IsExternal, MaxLength=null/unset
5. **Email field**: Change EmailContainer style to "margin-top-base"; add AnimatedLabel (Label→EmailInput, "Email"); fix EmailInput: Mandatory=True, Enabled=not IsExternal, autocomplete="new-password"
6. **Verification + GetCode section**: Replace VerifContainer+GetCodeContainer+CountdownContainer with:
   - If_ShowGetCodeButton (ShowGetCodeButton, ShowAll) / True:
     - If_ShowVerificationCode (ShowVerificationCode, ShowAll) / True:
       - Columns2 (ExtendedClass="align-items-center", PhoneBehavior=BreakColumns.All, GutterSize=None) / Column1: divVerificationCode ("padding-right-base", CustomStyle "text-align: left;") → AnimatedLabel (Label "Verification code" → VerificationCodeInput) → VerificationCodeInput (Text, VerificationCode, Enabled=True, Mandatory=ShowGetCodeButton, MaxLength=6, "form-control", OnChange→ValidateInputsOnChange no validation, autocomplete="new-validationcode") / Column2: Link (unnamed, Enabled=CountdownValue<=0, no style, CustomStyle "margin-bottom: 0px;", OnClick→SendVerificationCode no validation) → If_HaveRemainingTime (CountdownValue>0, ShowAll) / True: Expression "Didn't get it? Resend in " + CountdownValue + "s" / False: Expression "Resend verification code"
     - If_ShowVerificationCode / False: DivGetVerificationCode (no style) → ButtonLoading (unnamed, IsLoading=IsExecuting_GetCode, ShowLabelOnLoading=True) → Button (unnamed, "btn btn-small", IsDefault=False, Enabled=ShowGetCodeButton and not ShowVerificationCode, fill parent, ValidateAndContinue→SendVerificationCode) → spinner container + Text "Get verification code"
   - False: (empty)
7. **Save button**: Replace SaveBtnContainer+SaveChangesBtn with If_ExternalUser (IsExternal, ShowAll) / False: divSaveChanges ("margin-top-base") → ButtonLoading (btnSaveChanges, IsLoading=IsExecuting, ShowLabelOnLoading=True) → btnSave ("btn btn-primary", IsDefault=False, Enabled=IsButtonEnabled, fill parent, ValidateAndContinue→SaveChangesOnClick) → spinner container + Text "Save changes"
8. **ChangePwdContainer**: Remove from MainContent entirely (link is now in Actions placeholder)
