# LayoutBlank — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[WebBlock] LayoutBlank  (Layouts flow)
  Input Parameters:
    EnableAccessibilityFeatures → Boolean
    ExtendedClass → Text

  [Container] LayoutWrapper
    Style: "layout layout-blank"              ← BUG #1: second class should be "blank" not "layout-blank"
           + If(EnableAccessibilityFeatures, " has-accessible-features", "")
           + If(ExtendedClass = "", "", " " + ExtendedClass)
    Width: (fill parent)
    │
    └─ [Placeholder] MainContent              ← BUG #2: missing Container("content", role="main") layer
          Style: "content-middle"             ← BUG #3: style should be "main-content"
          EffectiveWidth: UserDefined
          (no default content)
          Name: MainContent                   ← BUG #4: name should be "Content"
```

**Bug summary:**
1. Root CSS: second class is "layout-blank" (built) vs "blank" (reference)
2. Missing intermediate Container "content" with Extended role="main" between root and placeholder
3. Placeholder style: "content-middle" (built) vs "main-content" (reference)
4. Placeholder name: "MainContent" (built) vs "Content" (reference)
