# New App Baseline — Verification Checklist

## Verification Checklist

- [ ] `context_themes`: 2 themes (`{App}` extending `OutSystemsUI`, `EmailTheme` standalone); `EmailTheme.IconLibrary = Phosphor2.0`; `Emails` flow `Theme = EmailTheme`; no "UI Flow 'Emails' is using a theme that is larger than 14KB" warning
- [ ] `context_roles`: confirmed application role exists
- [ ] `context_screens`: 6 screens with correct `AnonymousAccess` flags and layouts; **all 6 have the `{App}` role** — verify `roles` field non-empty for every screen
- [ ] `context_actions`: 3 server + 5 client actions in correct folders. Server: `SendResetPasswordEmail` (Authentication), `SendChangeEmail` (UserActions), `UpdateUser` (UserActions). Client: `DoLogin`, `DoLogout`, `SendResetPasswordEmail` (Authentication), `SendChangeEmail`, `UpdateUser` (UserActions). No `Check{App}Role`/`Has{App}Role` wrapper.
- [ ] `OnException` action in Common flow with 4 handlers per section 13; Common flow `OnExceptionHandler` → `OnException`; app `GlobalExceptionHandler` → `OnException`; `UseDefaultThemeExceptionHandler = False`; "No Exception Handling" warning absent
- [ ] `eSpace.IsUserProvider = true`; no `ImplicitSelfUserProvider` warning
- [ ] OutSystemsUI version ≥ 2.28.0; "Icon library compatibility" warning absent after Batch 1
- [ ] `MainFlow` exists and is empty — 0 screens, 0 blocks, 0 exception handler
- [ ] `SendResetPasswordEmail` and `SendChangeEmail` server actions have real `SendEmail` nodes (not Reminders) — confirm after Batch 6
- [ ] Every layout block parameter bound into a real widget property (not declared-but-unread); `Menu.ActiveItem`/`ActiveSubItem` included at baseline with default `-1`
- [ ] Every screen layout-block instance has all parameter arguments explicitly set
- [ ] `Login.LoginOnClick` implements the full flow: `IsBuiltInExecuting`, form validation, `FeedbackMessageClose`, `DoLogin`, `Check{App}Role` (unconditional, platform-generated), role branch, `AllExceptions` handler
- [ ] `Login.LoginProviderOnClick` has `ExecutingIndex = ProviderIndex` as first step — confirm assignment exists regardless of validator warning
- [ ] Both login button and every external-provider list item cross-wired to `Not(IsBuiltInExecuting) And ExecutingIndex = -1` for `Enabled`; `UserEmail`/`Password` inputs likewise
- [ ] `Login.ExecutingIndex` defaults to `-1` (not `0`)
- [ ] Pre-Publish Structural Sanity Check run: no duplicate folder names, no orphaned folder assignments, `(System)` hash non-zero
- [ ] After Batch 8: 0 unwired "Unused Action/Element/Variable" warnings except documented exceptions; classified list reported to user
