# Email Templates — Reference Widget Trees (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-23 via Mentor inspection.

---

## ResetPassword

**Input Parameters** (all mandatory):
- `ApplicationName` — Text
- `CustomerName` — Text
- `CustomerEmail` — Email
- `VerificationCode` — Text

**Subject:** `"Password Reset for " + ApplicationName`

**Widget Tree:**

```
[Container] EmailWrapper  Style: "email-max-width margin-auto"  Width: fill parent
  └─ [Container] Email  Style: "background-neutral-2 padding-l"  Width: fill parent
       ├─ [Container] Content  Style: "background-neutral-0 padding-l border-radius-medium"  Width: fill parent
       │   ├─ [Container] Logo  Style: "email-logo text-align-left"  Width: fill parent
       │   │   ├─ [Image] (unnamed)  Type: Static  Source: Logo  Extended: alt="Company Logo"
       │   │   └─ [Expression] (unnamed)  Value: ApplicationName  Example: "App name"
       │   │
       │   ├─ [Container] Title  Style: "margin-bottom-base heading5"  CustomStyle: "text-align: left;"  Width: fill parent
       │   │   └─ [If] (unnamed)  Condition: CustomerName <> ""  DesignMode: ShowTrueOrPreview
       │   │        True:  [Expression] "Hi " + CustomerName + "!"  Example: "Hi, John Smith!"
       │   │        False: [Text] "Hi!"
       │   │
       │   ├─ [Container] Message  Style: "margin-bottom-m"  Width: fill parent
       │   │   └─ [Text] "You're receiving this e-mail because you requested a password reset for your user account. To set a new password, use the button below or insert the following verification code in the reset password page. "
       │   │
       │   ├─ [Container] (unnamed)  Style: "margin-bottom-m"  Width: fill parent
       │   │   ├─ [Container] (unnamed)  Style: "heading2 margin-bottom-s"  Width: fill parent
       │   │   │   └─ [Expression] (unnamed)  Value: VerificationCode  Example: "yAlFws8Fs3NwIlvc"
       │   │   └─ [Container] (unnamed)  Style: "font-size-xs text-neutral-7"  Width: fill parent
       │   │       └─ [Text] "This verification code expires in 1 hour"
       │   │
       │   ├─ [Container] (unnamed)  Style: "margin-bottom-base"  Width: fill parent
       │   │   └─ [Container] (unnamed)  Style: "margin-bottom-m"  Width: fill parent
       │   │        └─ [Link] (unnamed)  Enabled: True  OnClick: navigate RecoverPasswordReset
       │   │             VerificationCode ← VerificationCode
       │   │             Email ← CustomerEmail
       │   │             └─ [Container] (unnamed)  Style: "btn btn-primary"
       │   │                  └─ [Text] "Reset password"
       │   │
       │   ├─ [Container] Instructions  Style: (none)  Width: fill parent
       │   │   └─ [Container] (unnamed)  Style: "margin-bottom-m"  Width: fill parent
       │   │       └─ [Text] "If you don't want to change your password or didn't request this,\nyou can safely disregard this email."
       │   │
       │   ├─ [Container] (unnamed)  Style: (none)  Width: fill parent
       │   │   └─ [Text] "Thanks,\nAdmin"
       │   │
       │   ├─ [Container] (unnamed)  Style: "email-separator"  Width: fill parent
       │   │
       │   └─ [Container] Copyright  Style: "font-size-xs text-neutral-7"  Width: fill parent
       │       ├─ [Text] "© "
       │       ├─ [Expression] Year(CurrDate())
       │       ├─ [Text] " "
       │       ├─ [Expression] ApplicationName  Example: "App name"
       │       └─ [Text] ". All Rights Reserved."
       │
       └─ [Container] Footer  Style: "margin-top-m"  Width: fill parent
```

---

## ChangeEmail

**Input Parameters** (all mandatory):
- `ApplicationName` — Text
- `CustomerName` — Text
- `CustomerEmail` — Email
- `VerificationCode` — Text

**Subject:** `ApplicationName + ": verification code " + VerificationCode`

**Widget Tree:**

```
[Container] EmailWrapper  Style: "email-max-width margin-auto"  Width: fill parent
  └─ [Container] Email  Style: "background-neutral-2 padding-l"  Width: fill parent
       ├─ [Container] Content  Style: "background-neutral-0 padding-l border-radius-medium"  Width: fill parent
       │   ├─ [Container] Logo  Style: "email-logo text-align-left"  Width: fill parent
       │   │   ├─ [Image] (unnamed)  Type: Static  Source: Logo  Extended: alt="Company Logo"
       │   │   └─ [Expression] (unnamed)  Value: ApplicationName  Example: "App name"
       │   │
       │   ├─ [Container] Title  Style: "margin-bottom-base heading5"  CustomStyle: "text-align: left;"  Width: fill parent
       │   │   └─ [If] IF_HasCustomerName  Condition: CustomerName <> ""  DesignMode: ShowTrueOrPreview
       │   │        True:  [Expression] "Hi " + CustomerName + "!"  Example: "Hi, John Smith!"
       │   │        False: [Text] "Hi!"
       │   │
       │   ├─ [Container] Message  Style: "margin-bottom-m"  Width: fill parent
       │   │   └─ [Text] "To complete your request to update the email address, please use the following verification code:"
       │   │
       │   ├─ [Container] (unnamed)  Style: "margin-bottom-m"  Width: fill parent
       │   │   ├─ [Container] (unnamed)  Style: "heading2 margin-bottom-s"  CustomStyle: "text-align: center;"  Width: fill parent
       │   │   │   └─ [Expression] (unnamed)  Value: VerificationCode  Example: "8475"
       │   │   └─ [Container] (unnamed)  Style: "font-size-xs text-neutral-7"  CustomStyle: "text-align: center;"  Width: fill parent
       │   │       └─ [Text] "This verification code expires in 1 hour"
       │   │
       │   ├─ [Container] Instructions  Style: (none)  Width: fill parent
       │   │   └─ [Container] (unnamed)  Style: "margin-bottom-m"  Width: fill parent
       │   │       └─ [Text] "If you don't want to change your email or didn't request this, you can safely disregard this email."
       │   │
       │   ├─ [Container] (unnamed)  Style: (none)  Width: fill parent
       │   │   └─ [Text] "Thank you,\nAdmin"
       │   │
       │   ├─ [Container] (unnamed)  Style: "email-separator"  Width: fill parent
       │   │
       │   └─ [Container] Copyright  Style: "font-size-xs text-neutral-7"  Width: fill parent
       │       ├─ [Text] "© "
       │       ├─ [Expression] Year(CurrDate())
       │       ├─ [Text] " "
       │       ├─ [Expression] ApplicationName  Example: "App name"
       │       └─ [Text] ". All Rights Reserved."
       │
       └─ [Container] Footer  Style: "margin-top-m"  Width: fill parent
```
