# LayoutBlank — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[WebBlock] LayoutBlank  (Layouts flow)
  Input Parameters:
    EnableAccessibilityFeatures → Boolean, default null (unset)
    ExtendedClass → Text, default ""
    (NO HasFixedHeader — LayoutBlank has no header)

  [Container] (unnamed root)
    Style: "layout blank"
           + If(not EnableAccessibilityFeatures, "", " has-accessible-features")
           + If(ExtendedClass = "", "", " " + ExtendedClass)
    Width: (fill parent)
    │
    └─ [Container] (unnamed)  Style: "content"  Width: (fill parent)
          Extended: role="main"
       └─ [Placeholder] Content  Style: "main-content"  EffectiveWidth: UserDefined
             (no default content)
```

**Notes:**
- Only 2 input params: EnableAccessibilityFeatures + ExtendedClass (no HasFixedHeader)
- CSS class is "blank" (not "layout-blank") — the root already has "layout" as the first class
- Wrapping Container with role="main" sits between root and placeholder
- Placeholder name is "Content" (not "MainContent") and style is "main-content" (not "content-middle")
- No header, no skip-nav, no footer — truly minimal shell
