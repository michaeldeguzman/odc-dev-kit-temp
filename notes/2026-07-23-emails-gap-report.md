# Email Templates — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 25** (ResetPassword: 13, ChangeEmail: 12)

---

## ResetPassword — 13 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Input parameters | All 4 mandatory | All 4 optional (no defaults) |
| 2 | Root structure | EmailWrapper > Email > Content container tree | Flat — no container nesting at all |
| 3 | Logo section | Container "Logo" [email-logo text-align-left] → Image (alt="Company Logo") + Expression ApplicationName | Image only (LogoImage), no alt, no app name |
| 4 | Greeting | Container "Title" [margin-bottom-base heading5, CustomStyle text-align: left] → If (CustomerName <> "", ShowTrueOrPreview): True: Expression "Hi " + CustomerName + "!" / False: Text "Hi!" | Expression "Hi " + CustomerName + "," (no If, no container) |
| 5 | Body text | Container "Message" [margin-bottom-m] → Text "You're receiving this e-mail because you requested a password reset for your user account. To set a new password, use the button below or insert the following verification code in the reset password page. " | Expression widget with different text |
| 6 | VerificationCode | Unnamed [margin-bottom-m] → Unnamed [heading2 margin-bottom-s] → Expression VerificationCode (example "yAlFws8Fs3NwIlvc") | Expression VerificationCodeHeading, style "heading2" only |
| 7 | Expiry text | Unnamed [font-size-xs text-neutral-7] → Text "This verification code expires in 1 hour" | Text "This code expires in 1 hour." (wrong text, no style container) |
| 8 | CTA link | Container [margin-bottom-base] > Container [margin-bottom-m] > Link (no style) > Container [btn btn-primary] > Text "Reset password" (lowercase p) | Link [btn btn-primary] CTALink with stray "link" Text child + Text "Reset Password" (capital P); missing container wrappers |
| 9 | Instructions | Container "Instructions" > Container [margin-bottom-m] > Text "If you don't want to change your password or didn't request this,\nyou can safely disregard this email." | Missing entirely |
| 10 | Sign-off | Container (no style) → Text "Thanks,\nAdmin" | Expression "Kind regards, The " + ApplicationName + " Team" |
| 11 | Email separator | Container [email-separator] | Missing |
| 12 | Copyright | Container "Copyright" [font-size-xs text-neutral-7] → Text "© " + Expression Year(CurrDate()) + Text " " + Expression ApplicationName + Text ". All Rights Reserved." | Expression "© " + ApplicationName only |
| 13 | Footer | Container "Footer" [margin-top-m] | Missing |

### Fix scope
Complete replacement of the ResetPassword email body. Delete all existing widgets, then build the full container tree per reference:
1. Set all 4 input parameters to mandatory
2. Build EmailWrapper > Email > Content > [Logo, Title, Message, VerificationCode block, CTA block, Instructions, Sign-off, Separator, Copyright] > Footer structure

---

## ChangeEmail — 12 discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Input parameters | All 4 mandatory | All 4 optional |
| 2 | Root structure | EmailWrapper > Email > Content container tree | Flat — no container nesting |
| 3 | Logo section | Container "Logo" [email-logo text-align-left] → Image (alt="Company Logo") + Expression ApplicationName | Image only, no alt, no app name |
| 4 | Greeting | Container "Title" [margin-bottom-base heading5, CustomStyle text-align: left] → If "IF_HasCustomerName" (CustomerName <> "", ShowTrueOrPreview): True: Expression "Hi " + CustomerName + "!" / False: Text "Hi!" | Expression "Hi " + CustomerName + "," (no If, no container) |
| 5 | Body text | Container "Message" [margin-bottom-m] → Text "To complete your request to update the email address, please use the following verification code:" | Expression widget with different text |
| 6 | VerificationCode | Unnamed [margin-bottom-m] → Unnamed [heading2 margin-bottom-s, CustomStyle text-align: center;] → Expression VerificationCode (example "8475") | Expression VerificationCodeHeading, style "heading2 text-align-center" |
| 7 | Expiry text | Unnamed [font-size-xs text-neutral-7, CustomStyle text-align: center;] → Text "This verification code expires in 1 hour" | Missing entirely |
| 8 | Instructions | Container "Instructions" > Container [margin-bottom-m] > Text "If you don't want to change your email or didn't request this, you can safely disregard this email." | Missing entirely |
| 9 | Sign-off | Container (no style) → Text "Thank you,\nAdmin" | Expression "Kind regards, The " + ApplicationName + " Team" |
| 10 | Email separator | Container [email-separator] | Missing |
| 11 | Copyright | Container "Copyright" [font-size-xs text-neutral-7] → Text "© " + Expression Year(CurrDate()) + Text " " + Expression ApplicationName + Text ". All Rights Reserved." | Expression "© " + ApplicationName only |
| 12 | Footer | Container "Footer" [margin-top-m] | Missing |

### Fix scope
Complete replacement of the ChangeEmail email body. Delete all existing widgets, then build the full container tree per reference (identical structure to ResetPassword minus the CTA block; different body text and sign-off).

---

## Notes

**Flat vs structured:** Both built templates are simplified stubs with flat widget lists. The reference uses a proper email-safe container hierarchy (EmailWrapper > Email > Content) with named containers for Logo, Title, Message, Instructions, Copyright, Footer.

**Parameters mandatory:** Reference marks all 4 parameters mandatory on both templates. Built has them optional. A Send Email node with a mandatory parameter field left blank is a runtime error.

**CustomerName If widget:** Reference uses `If (CustomerName <> "")` for a "Hi, [Name]!" / "Hi!" fallback. Built uses plain Expression "Hi " + CustomerName + "," which renders "Hi ," if CustomerName is empty.

**Copyright:** Reference uses `Year(CurrDate())` (dynamic year) + ". All Rights Reserved." Built uses only "© " + ApplicationName.

**CTA text case:** Reference: "Reset password" (lowercase p). Built: "Reset Password" (capital P).
