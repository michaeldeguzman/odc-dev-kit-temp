# New App Baseline — Known Failure Modes & Gotchas

Field-tested debugging knowledge from prior baseline runs (see
notes/2026-07-21-newapp-gap-analysis.md for the session that produced
most of these). Read this BEFORE Batch 1 and again if any batch produces
unexpected validation warnings or a publish failure.

## Required References

Add all references before Batch 1 — missing references cause mid-batch expression failures.

### Interface

**Web Blocks — Referenced from `OutSystemsUI`:**
`AnimatedLabel`, `BlankSlate`, `ButtonLoading`, `Columns2`, `InputWithIcon`, `PasswordPolicy`, `Separator`, `UserAvatar`

### Logic

**Server Actions — Referenced from `(System)`:** `StartResetPassword`, `StartUpdateEmail`, `UpdateUserProfile`

**Client Actions — Referenced from `(System)`:**
`Login`, `Logout`, `ChangePassword`, `FinishResetPassword`, `FinishUpdateEmail`, `GetExternalIdentityProviders`, `GetExternalLoginURL`, `GetExternalLogoutURL`, `GetUserProfile`, `IsBuiltinIdentityProviderActive`, `IsExternalUser`

**Client Actions — Referenced from `OutSystemsUI`:**
`AddFavicon`, `SetLang`, `SetIconLibraryClass`, `LayoutReady`, `LayoutDestroy`, `MenuReady`, `MenuDestroy`, `SetActiveMenuItems`, `SetMenuIconListeners`, `SetMenuListeners`, `ToggleSideMenu`, `SkipToContent`, `FeedbackMessageClose`, `ShowPassword`

### Data

**Server Entities — Referenced from `(System)`:** `User`, `Role`, `ActivityInstance`, `ProcessInstance`

**Static Entities — Referenced from `OutSystemsUI`:** `BreakColumns`, `Color`, `GutterSize`, `Shape`, `SideMenuBehavior`, `Size`, `Space`

**Structures — Referenced from `(System)`:**
`UserLoginResult`, `UserLoginFailureReason`, `UpdateUserResult`, `UpdateUserFailureReason`, `UserUpdateInfo`, `UserInfo`, `ChangePasswordResult`, `ChangePasswordFailureReason`, `StartResetPasswordResult`, `FinishResetPasswordResult`, `FinishResetPasswordFailureReason`, `StartUpdateEmailResult`, `StartUpdateEmailFailureReason`, `FinishUpdateEmailResult`, `FinishUpdateEmailFailureReason`, `ExternalIdentityProvider`

**Structures — Referenced from `OutSystemsUI`:** `ErrorMessage_OSUI`

## Model API Patterns (confirmed — don't re-discover)

- **Folders are scoped by tree type.** `CreateFolder(ESpaceTreeFolder.ServerActions, "Authentication")` and `CreateFolder(ESpaceTreeFolder.ClientActions, "Authentication")` are two different objects that share a display name — this is correct. The bug is creating a *second* folder of the *same* scope accidentally — that breaks the build compiler while passing validation.
- **`ISendEmailNode` cannot be created via `applyModelApiCode`** (sandbox execution exception, confirmed across TestNewWebApp3–7). **CAN** be created via Mentor's natural language editing path. Two requirements: (1) email template must exist before requesting the SendEmail node; (2) prompt must be natural language, NOT `applyModelApiCode`.
- **`SetIconLibraryClass` is not in the Model API's OutSystemsUI surface** (only 20 elements exposed). Attempt `add_references_to_elements` with global key `Kn_hixxDWEm4lMd7mIpycQ*l+LGqvnbjEWzX1y8Hxcx+g` first. If it fails, create a local client action stub named `SetIconLibraryClass` with no parameters and no body — 0 errors, 0 warnings.
- **Model API code sandbox disallows `for`/`foreach`-with-mutation loops, local functions, sized array creation.** Use 1×1 transparent GIF instead of hand-rolled PNG (no CRC to compute).
- **Refreshing a stale `(System)` reference:** Re-add via `add_references_to_elements` or call `eSpace.RefreshDependency(globalKey, updateSpecificVersion: true)` on the entity's own global key (not the reference's `ModuleKey`). Confirm by checking the attribute list actually changed.
- **Non-`Mandatory` block parameters still error at publish if left blank on a screen instance.** Always set every layout-block argument explicitly on every screen.

## Post-Crash-Recovery Structural Check

Run this if any batch crashed mid-way and was retried (especially if folders, actions, or stubs were created/renamed/deleted). A prior crash left two distinct folder objects both named "Authentication" — both individually valid, but the build compiler failed for 9 consecutive attempts before this was found.

1. Enumerate `eSpace.Folders` — list every folder's `Name` and `ObjectKey`. Any name appearing more than once → consolidate into one per (name, scope) pair and reassign affected actions.
2. Enumerate every server/client action's `.Folder` property — confirm none are null.

## Pre-Publish Structural Sanity Check

Run once before the first publish attempt:

1. **Duplicate folder names** — run Post-Crash check above even if nothing crashed.
2. **`(System)` reference health** — Hash non-zero (pre-flight step 7). Fix now if zero.
3. **No orphaned action-folder assignments** — every action has a non-null `.Folder`.

If first publish fails, match the error code before guessing broadly:
- **`OS-DPL-42202`** — first suspect: duplicate folder names or orphaned assignments.
- **`OS-BEW-CODE-40036`** — stale/schema-mismatched reference. Fix via `(System)` refresh pattern, then re-verify every expression reading that entity's attributes.

## Known Manual Steps Required After Skill Run

### SendEmail nodes — AUTOMATED

Mentor CAN create `ISendEmailNode` via natural language editing. Do NOT use `applyModelApiCode`. Templates must exist before the request. See Batch 6.

### `SetIconLibraryClass` — stub wired; real action needs ODC Studio

Skill creates a local stub and wires it in all 4 layout block `OnInitialize` — 0 errors, 0 warnings. After the skill run, in ODC Studio:
1. Manage Dependencies → OutSystemsUI → enable `SetIconLibraryClass`.
2. Delete the local stub `SetIconLibraryClass` client action.
3. Update all 4 layout block `OnInitialize` callers to point to the OutSystemsUI reference action.

## Avoiding stub-naming collisions across batches

When a block in Batch 2 references a future Batch-5 action (`DoLogout`, etc.), use a comment/Reminder node instead of a same-named stub action — a stub collides with the real action at creation time and the platform auto-suffixes it, requiring a rename/delete cleanup turn.

## Expected-unused exceptions (don't force-wire)

- **`LoginProviderOnClick.ProviderIndex`** — known validator false positive. Confirm `ExecutingIndex = ProviderIndex` assignment exists in the action; if warning persists anyway, classify as confirmed false positive, not a fix-now item.
- **`ExternalIdentityProviders`/`ShowExternalProvider`** — already consumed by `OnInitialize`'s population logic and the container's `If(ShowExternalProvider, ...)` — should not produce warnings.
