# LayoutBase — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[WebBlock] LayoutBase  (Layouts flow)
  Input Parameters:
    HasFixedHeader → Boolean, default True
    EnableAccessibilityFeatures → Boolean, default null
    ExtendedClass → Text, default ""

  [Container] LayoutWrapper
    Style: "layout layout-blank"
           + If(HasFixedHeader, " fixed-header", "")
           + " "
           + If(not EnableAccessibilityFeatures, "", " has-accessible-features")
           + If(ExtendedClass = "", "", " " + ExtendedClass)
    Width: (fill parent)
    │
    ├─ [Container] (unnamed)  Style: "main"  Width: (fill parent)
    │  │
    │  ├─ [AdvancedHtml] Header2  Tag: <header>
    │  │    Extended: role="banner", class="header"
    │  │  │
    │  │  ├─ [Link] (unnamed)  Style: "skip-nav"
    │  │  │    OnClick → SkipToContentOnClick (passes MainContentWrapper.Id as TargetId)
    │  │  │    Extended: aria-label="Skip to Content (Press Enter)",
    │  │  │              data-showskipcontent=If(EnableAccessibilityFeatures, "true", "false")
    │  │  │  └─ [Text] (unnamed)  Text: "Skip to Content (Press Enter)"
    │  │  │
    │  │  └─ [Container] (unnamed)  Style: "header-top ThemeGrid_Container"  Width: (fill parent)
    │  │     └─ [Container] (unnamed)  Style: "header-content display-flex "  Width: (fill parent)
    │  │        ├─ [BlockInstance] MenuIcon  (Common flow, no params)
    │  │        ├─ [BlockInstance] ApplicationTitle  (Common flow, no params)
    │  │        └─ [Placeholder] Header  Style: "header-navigation"  EffectiveWidth: InlineBlock
    │  │           └─ [default] [BlockInstance] Menu  (Common flow)
    │  │                 ActiveItem → null, ActiveSubItem → null
    │  │
    │  └─ [Container] Content  Style: "content"  Width: (fill parent)
    │     └─ [Container] MainContentWrapper  Style: "main-content"  Width: (fill parent)
    │           Extended: role="main"
    │        └─ [Placeholder] MainContent  Style: "content-middle"  EffectiveWidth: UserDefined
    │           └─ [default] [BlockInstance] LayoutBaseSection  (Layouts flow)
    │                 all params null
```

**Notes:**
- LayoutWrapper uses "layout-blank" (not "layout-base") — counterintuitive name
- Header2 is AdvancedHtml (`<header>` tag), NOT a plain Container
- MenuIcon + ApplicationTitle block instances sit BEFORE the Header placeholder inside header-content
- Header placeholder has Menu block as default content
- MainContentWrapper style is "main-content" (no ThemeGrid_Container suffix)
- Only two placeholders: Header (InlineBlock) and MainContent (UserDefined)
- No Breadcrumbs / Title / Actions / Footer zones (those are LayoutSideMenu / LayoutTopMenu features)
