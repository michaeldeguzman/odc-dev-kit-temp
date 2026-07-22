# LayoutBase — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[WebBlock] LayoutBase  (Layouts flow)
  Input Parameters:
    HasFixedHeader → Boolean, default True
    EnableAccessibilityFeatures → Boolean, default null
    ExtendedClass → Text, default ""

  [Container] LayoutWrapper
    Style: "layout layout-base"               ← BUG #1: should be "layout layout-blank"
           + If(HasFixedHeader, " fixed-header", "")
           + " "
           + If(not EnableAccessibilityFeatures, "", " has-accessible-features")
           + If(ExtendedClass = "", "", " " + ExtendedClass)
    Width: (fill parent)
    │
    ├─ [Container] MainContainer  Style: "main"  Width: (fill parent)
    │  │
    │  ├─ [Container] Header2  Style: "header"   ← BUG #2: should be AdvancedHtml <header> tag
    │  │    Extended: role="banner"              (not a plain Container)
    │  │  │
    │  │  ├─ [Link] SkipNavLink  Style: "skip-nav"
    │  │  │    OnClick → SkipToContentOnClick
    │  │  │    Extended: aria-label="Skip to Content (Press Enter)",
    │  │  │              data-showskipcontent=If(EnableAccessibilityFeatures, "true", "false")
    │  │  │  ├─ [Text] (unnamed)  Text: "link"   ← BUG #3: stray leftover text node
    │  │  │  └─ [Text] SkipText   Text: "Skip to Content (Press Enter)"
    │  │  │
    │  │  └─ [Container] HeaderTop  Style: "header-top ThemeGrid_Container"  Width: (fill parent)
    │  │     └─ [Container] HeaderContent  Style: "header-content display-flex"  Width: (fill parent)
    │  │        │                          ← BUG #4: MenuIcon block instance absent
    │  │        │                          ← BUG #5: ApplicationTitle block instance absent
    │  │        └─ [Placeholder] Header  Style: "header-navigation"  EffectiveWidth: InlineBlock
    │  │              [EMPTY]             ← BUG #6: Menu block default content absent
    │  │
    │  └─ [Container] ContentArea  Style: "content"  Width: (fill parent)
    │     └─ [Container] MainContentWrapper  Style: "main-content ThemeGrid_Container"  ← BUG #7: extra class
    │           Extended: role="main"
    │        └─ [Placeholder] MainContent  Style: "content-middle"  EffectiveWidth: UserDefined
    │           └─ [default] [BlockInstance] LayoutBaseSection  (Layouts flow — correct)
```

**Bug summary:**
1. LayoutWrapper CSS: "layout-base" (built) vs "layout-blank" (reference)
2. Header2 widget type: plain Container (built) vs AdvancedHtml `<header>` tag (reference)
3. SkipNavLink has stray "link" text node (reference has only 1 text child)
4. MenuIcon block instance absent before Header placeholder
5. ApplicationTitle block instance absent before Header placeholder
6. Menu block missing as Header placeholder default content
7. MainContentWrapper extra CSS class "ThemeGrid_Container" (reference has "main-content" only)
