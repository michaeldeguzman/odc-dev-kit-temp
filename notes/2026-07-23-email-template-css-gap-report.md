# Email Template CSS — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 0** — Reference and built match on all three CSS dimensions.

---

## Findings

### 1. EmailTheme StyleSheet

Reference EmailTheme StyleSheet (full verbatim):
```css
/* Widgets */
.table { background: #fff; border: 1px solid #dee2e6; border-radius: 4px; ... }
.table-header th { ... }
.table-row td { ... }
.table-row-small td { height: 48px; }
...
.list-item { border-bottom: 1px solid #dee2e6; padding: 24px; ... }
.list-item:last-of-type { border-bottom: none; }
.list .list-item { background-color: #fff; }
```

**Match: assets/EmailTheme.css is verbatim correct ✓**

Built EmailTheme StyleSheet: identical content (same table/list widget CSS).

### 2. Per-template StyleSheet (ResetPassword)

Reference: **NOT SET** — property is null/empty at the template level.
Built: **NOT SET** — same.
**Match ✓ — no discrepancy.**

### 3. Per-template StyleSheet (ChangeEmail)

Reference: **NOT SET** — property is null/empty at the template level.
Built: **NOT SET** — same.
**Match ✓ — no discrepancy.**

### 4. Emails flow Theme property

Reference: `EmailTheme` ✓
Built: `EmailTheme` ✓
**Match ✓**

---

## Asset File Corrections Required

### assets/ResetPasswordStyle.css — INCORRECT CONTENT

The file contains a full email CSS bundle (html, body, heading classes, btn-primary, email-logo, margin utilities, etc.) that is NOT the per-template StyleSheet property in ODC. That property is null on both templates in the reference.

**Source of the CSS classes used in widget trees** (heading2, margin-bottom-m, btn-primary, email-logo, text-neutral-7, font-size-xs, etc.): these are injected by OutSystemsUI at email send time as part of its own email CSS bundle. They do not need to be set on any ODC model property — they are available automatically when OutSystemsUI is a dependency.

**Correction:** clear `assets/ResetPasswordStyle.css` — per-template CSS is null in the reference.

### assets/ChangeEmailStyle.css — CORRECT

Already empty. Per-template CSS is null in the reference. No change needed.

---

## No Fixes Required in TestNewWebApp9

Built app already matches reference on all CSS dimensions. No Mentor run needed.

---

## Spec.md Update Required (Section 11)

Add documentation:
- Per-template StyleSheet: leave empty (null) — do NOT set it
- EmailTheme StyleSheet: table/list widget CSS only (see assets/EmailTheme.css) — set at Batch 1 theme creation
- Utility CSS classes used in template widget trees (heading2, btn, email-logo, margin-*, text-neutral-*, etc.) come from OutSystemsUI's email CSS injection at send time — no ODC property to set
