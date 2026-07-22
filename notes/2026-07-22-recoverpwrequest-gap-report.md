# RecoverPasswordRequest — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-22

**Total discrepancies: 11**

## 1. Structural/nesting differences

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Outer wrapper | Container "login-screen" wrapping Form | Absent — Form is first child of placeholder |
| 2 | Form style | "login-form" | "form card" |
| 3 | Logo section | Container "login-logo" → Image + h5 "Forgot your password?" + "Don't worry..." text | Entirely absent |
| 4 | Email input wrapping | Container "login-inputs margin-top-m" → AnimatedLabel block (Label "Email", Input_Email) | Plain Container "form-group" with bare Input |
| 5 | Submit button wrapping | Container "login-button margin-top-l" → ButtonLoading (IsLoading=IsExecuting, ExtendedClass="full-width") | Plain Container "form-group" with bare Button |
| 6 | Footer link section | Container "margin-top-m" (text-align: center) → Text "Not in the right place?" + Link → Login | Entirely absent |

## 2. Duplicate/extra widgets

| # | Widget | Reference | Built |
|---|---|---|---|
| 7 | Button caption | One Text "Reset password" | Two Text nodes: "Save" (leftover) + "Reset Password" |

## 3. Literal vs bound captions

| # | Widget | Reference | Built |
|---|---|---|---|
| 8 | Button Text | "Reset password" (lowercase p) | "Reset Password" (uppercase P) |

## 4. Missing/incorrect properties

| # | Widget | Property | Reference | Built |
|---|---|---|---|---|
| 9 | Input_Email | Mandatory | True | False |
| 10 | Input_Email | MaxLength | 250 | 50 |
| 11 | Input_Email | Enabled | True | not IsExecuting |
| 12 | Input_Email | tabindex | 1 | absent |
| 13 | Button | Enabled | True | not IsExecuting |
| 14 | Button | tabindex | 2 | absent |

**Count: 14 discrepancies** (items 9-14 expand the structural gaps).

## Fix scope

Rebuild the entire content area. Specific actions:
1. Add outer "login-screen" Container wrapping the Form
2. Change Form style to "login-form"
3. Add logo section: Container "login-logo" (text-align center) → Image Logo (100px) + AdvancedHtml h5 (class="margin-top-base text-neutral-8") "Forgot your password?" + Container "margin-top-s" → "Don't worry, we'll send you an email with instructions."
4. Replace EmailContainer with Container "login-inputs margin-top-m" → AnimatedLabel block (Label "Email", Input_Email: Email type, Mandatory True, MaxLength 250, Enabled True, tabindex=1)
5. Replace BtnContainer with Container "login-button margin-top-l" → ButtonLoading (IsLoading=IsExecuting, ExtendedClass="full-width") → Button (IsDefault True, Enabled True, tabindex=2, Text "Reset password")
6. Add footer: Container "margin-top-m" (text-align center) → Text "Not in the right place?" + Link → Login (tabindex=3, aria-label "Go to login page") → Text "Go to login."
