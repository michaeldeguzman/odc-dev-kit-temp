# Email Templates — Built Widget Trees (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

## ResetPassword

**Input Parameters** (all optional, no defaults):
- `ApplicationName` — Text
- `CustomerName` — Text
- `CustomerEmail` — Email
- `VerificationCode` — Text

**Subject:** `"Password Reset for " + ApplicationName`

**Widget Tree** (flat — no container nesting):

```
[Image] LogoImage  Type: Static  Source: Logo  (no alt, no style)

[Expression] Greeting  Value: "Hi " + CustomerName + ","  (no style)

[Expression] BodyExpr  Value: "You have requested to reset your password for " + ApplicationName + ". Use the verification code below to reset your password."  (no style)

[Expression] VerificationCodeHeading  Value: VerificationCode  Style: "heading2"

[Text] ExpiryText  Text: "This code expires in 1 hour."  (no style)

[Link] CTALink  Style: "btn btn-primary"  Enabled: True
  OnClick → RecoverPasswordReset (VerificationCode ← VerificationCode, Email ← CustomerEmail)
  ├─ [Text] (unnamed)  Text: "link"    ← BUG: stray default text node
  └─ [Text] CTAText  Text: "Reset Password"   ← BUG: capital P (should be "Reset password")

[Expression] SignOff  Value: "Kind regards, The " + ApplicationName + " Team"  (no style)

[Expression] Copyright  Value: "© " + ApplicationName  (no style)
```

**Bugs:**
- No container structure (flat — missing EmailWrapper/Email/Content/Logo/Title/Message/Instructions/Copyright hierarchy)
- Parameters not mandatory
- Logo: no alt text, no ApplicationName expression alongside it
- Greeting: plain Expression (no If widget for CustomerName fallback)
- Body text: wrong content, Expression widget not Text widget
- VerificationCode: wrong style ("heading2" only vs "heading2 margin-bottom-s" in container)
- Expiry: wrong text ("expires in 1 hour." vs "expires in 1 hour"), no style container
- CTA: stray "link" Text child; "Reset Password" (capital P) vs "Reset password"; missing outer container wrappers
- Sign-off: "Kind regards, The [App] Team" vs "Thanks,\nAdmin"
- Copyright: missing Year(CurrDate()), missing ". All Rights Reserved."
- Missing: Instructions section, email-separator, Footer container

---

## ChangeEmail

**Input Parameters** (all optional, no defaults):
- `ApplicationName` — Text
- `CustomerName` — Text
- `CustomerEmail` — Email
- `VerificationCode` — Text

**Subject:** `ApplicationName + ": verification code " + VerificationCode`

**Widget Tree** (flat — no container nesting):

```
[Image] LogoImage  Type: Static  Source: Logo  (no alt, no style)

[Expression] Greeting  Value: "Hi " + CustomerName + ","  (no style)

[Expression] BodyExpr  Value: "You have requested to update your email address for " + ApplicationName + ". Use the verification code below to confirm your new email."  (no style)

[Expression] VerificationCodeHeading  Value: VerificationCode  Style: "heading2 text-align-center"

[Expression] SignOff  Value: "Kind regards, The " + ApplicationName + " Team"  (no style)

[Expression] Copyright  Value: "© " + ApplicationName  (no style)
```

**Bugs:**
- No container structure (flat — missing EmailWrapper/Email/Content hierarchy)
- Parameters not mandatory
- Logo: no alt text, no ApplicationName expression alongside it
- Greeting: plain Expression (no If widget for CustomerName fallback)
- Body text: wrong content, Expression widget not Text widget
- VerificationCode: wrong style ("heading2 text-align-center" vs container with "heading2 margin-bottom-s" + customStyle)
- Missing: expiry text "This verification code expires in 1 hour" with center alignment
- Sign-off: "Kind regards, The [App] Team" vs "Thank you,\nAdmin"
- Copyright: missing Year(CurrDate()), missing ". All Rights Reserved."
- Missing: Instructions section, email-separator, Footer container
