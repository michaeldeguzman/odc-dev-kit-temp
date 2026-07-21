# Gap Analysis: NewApp Baseline vs Reference — 2026-07-21

**Thread:** `dbresults-odc-new-app-baseline` skill audit against NewApp reference implementation  
**Apps inspected:**  
- TestNewWebApp7 (scaffolded): `402cb58e-895a-4b97-8494-b7bfa914b667`  
- NewApp (reference): `88f79d25-6cbf-4178-b804-199303656da4`

---

## Gaps Found and Fixed

### 1. Missing `OnException` handler — CRITICAL

**What was wrong:** SKILL.md section 13 said "do not create a global app-level exception handler." That was based on a prior session's incorrect read of NewApp. A direct Mentor OML inspection on 2026-07-21 confirmed NewApp HAS a full `OnException` action.

**Reference spec (confirmed from NewApp):**

| Handler | AbortTransaction | LogError | Next |
|---|---|---|---|
| AllExceptions | True | True | Message "There was a problem. Please contact the administrator" → End |
| DatabaseException | True | True | Message "There was a problem with the database request. Please contact the administrator" → End |
| CommunicationException | True | True | Message "There was a problem communicating with the server. Please try again or contact your administrator" → End |
| SecurityException | True | False | If `GetUserId() <> NullTextIdentifier()` → True: InvalidPermissions / False: Assign `Client.LastURL = GetBookmarkableURL()` → Login |

**Wiring:** Common flow `OnExceptionHandler` = OnException, app `GlobalExceptionHandler` = OnException, `UseDefaultThemeExceptionHandler` = False.

**SKILL.md fix:** Section 13 completely rewritten. Batch 7 now creates this handler. "No Exception Handling" warning on the Common flow is explicitly documented as a defect (not an expected warning).

**TestNewWebApp7 fix:** OnException action created in Common flow, wired to both Common flow and app GlobalExceptionHandler in this session.

---

### 2. Role incorrectly removed from anonymous screens — HIGH

**What was wrong:** Batch 7 prompts said "Anonymous screens: AnonymousAccess=true, NO roles attached." This was wrong and applied in TestNewWebApp6 Batch 7 and TestNewWebApp7 Batch 7.

**Reference spec (confirmed from NewApp):** All 6 Common flow screens have the app role attached — including the 4 anonymous ones (Login, RecoverPasswordRequest, RecoverPasswordReset, InvalidPermissions). `AnonymousAccess = true` overrides role-based access control at runtime, so the role is harmless on anonymous screens.

**SKILL.md fix:**
- Batch 3 prompt now explicitly requires role on all 5 screens created in that batch
- Batch 8 (Wiring Closure) now has screen role audit as step 2 (before warning classification) with explicit "never remove, add if missing" instruction
- Section 8 preamble updated with the rule

**TestNewWebApp7 fix:** Role added back to Login, RecoverPasswordRequest, RecoverPasswordReset, InvalidPermissions in this session.

---

### 3. Parameter descriptions missing — MEDIUM

**What was wrong:** SKILL.md batch prompts enforced descriptions on actions, screens, and blocks but not on their input/output parameters. All 9 actions in TestNewWebApp7 had parameter-level descriptions missing.

**SKILL.md fix:** Mandatory wiring instruction (included in every batch 2–7 prompt) now explicitly calls out parameters:
> "Every named element created in this batch must have a non-empty Description — this includes screens, web blocks, server actions, client actions, AND their input/output parameters."

**TestNewWebApp7 fix:** Descriptions added to all parameters across 9 actions + RecoverPasswordReset screen input parameters in this session.

---

### 4. `CreatedWithoutCustomCSS: "true"` theme value undocumented — LOW

**What was wrong:** NewApp's `{App}` theme has 4 value overrides: `PrimaryColor`, `SecondaryColor`, `AppPrimaryColor` (all brand color), and `CreatedWithoutCustomCSS = "true"`. SKILL.md only documented the 3 color values.

**SKILL.md fix:** `CreatedWithoutCustomCSS: "true"` added to section 2 theme values spec.

---

### 5. `IsUserProvider` reference discrepancy — INFO

**What was wrong:** SKILL.md section 3 says to set `eSpace.IsUserProvider = true`. NewApp has `IsUserProvider = False` with no `ImplicitSelfUserProvider` warning.

**Finding:** The `ImplicitSelfUserProvider` warning is suppressed by the presence of a full built-in Login/auth flow — not by the `IsUserProvider` flag itself. Setting `True` is still correct (explicit declaration), but the flag and the warning are orthogonal.

**SKILL.md fix:** Note added to section 3 explaining the discrepancy and confirming setting `True` is still the right approach.

---

### 6. Login input `Enabled` binding incomplete — LOW

**What was wrong:** SKILL.md said bind `UserEmail`/`Password` inputs' `Enabled` to `Not(IsBuiltInExecuting)`. NewApp uses `ExecutingIndex = -1 and not IsBuiltInExecuting` (both conditions).

**SKILL.md fix:** Section 8 Login spec updated to `ExecutingIndex = -1 and not IsBuiltInExecuting`.

---

## SKILL.md Changes Summary

File: `.claude/skills/dbresults-odc-new-app-baseline/SKILL.md`

| Change | Section |
|---|---|
| Section 13 completely rewritten — OnException spec with exact handler table, message text, SecurityException branch | Section 13 |
| Batch 7 restored as OnException batch; Batch 8 = Wiring Closure | Mentor Prompt Strategy |
| Screen role audit added to Batch 8 step 2 | Wiring Closure & Validation Sweep |
| Role requirement added to Batch 3 prompt | Mentor Prompt Strategy |
| Parameter description requirement added to mandatory wiring instruction | Mandatory wiring instruction |
| `CreatedWithoutCustomCSS: "true"` added to `{App}` theme values | Section 2 |
| `IsUserProvider` reference note added | Section 3 |
| Login input Enabled binding corrected to `ExecutingIndex = -1 and not IsBuiltInExecuting` | Section 8 (Login) |

---

## TestNewWebApp7 Fixes Applied (2026-07-21)

| Fix | Description |
|---|---|
| Role added to 4 anonymous screens | Login, RecoverPasswordRequest, RecoverPasswordReset, InvalidPermissions now have TestNewWebApp7 role |
| OnException handler created | 4 handlers, wired to Common flow OnExceptionHandler + app GlobalExceptionHandler, UseDefaultThemeExceptionHandler=False |
| Parameter descriptions added | All 9 actions + RecoverPasswordReset screen input parameters |

---

## Verification Checklist

After this session's Mentor batch completes, verify:

- [ ] All 6 Common flow screens have `TestNewWebApp7` role in `context_screens` result
- [ ] 0 validation errors
- [ ] "No Exception Handling" warning on Common flow is absent
- [ ] `context_actions` spot-check: parameter descriptions present on DoLogin, DoLogout, SendResetPasswordEmail
- [ ] `env_app` confirms revision incremented after publish

---

## Key Lesson

**Never classify "No Exception Handling" on a Common flow as an expected baseline warning.** It means the OnException handler is missing. The prior SKILL.md version was wrong about this, and it was compounded by the Batch 7 sweep classifying it as "accepted" in 3 consecutive runs (TestNewWebApp5, TestNewWebApp6, TestNewWebApp7) before the NewApp OML inspection caught it.
