# LayoutTopMenu — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[WebBlock] LayoutTopMenu  (Layouts flow)
  Input Parameters:
    HasFixedHeader → Boolean, default True
    EnableAccessibilityFeatures → Boolean, default False
    ExtendedClass → Text, default ""

  [Container] LayoutWrapper
    Style: "layout layout-top"
           + If(HasFixedHeader, " fixed-header", "")
           + If(EnableAccessibilityFeatures, " has-accessible-features", "")
           + If(ExtendedClass = "", "", " " + ExtendedClass)
    Width: (fill parent)
    │
    └─ [Container] MainContainer  Style: "main"  Width: (fill parent)
       │
       ├─ [Container] Header2  Style: "header"                           ← BUG #1: should be AdvancedHtml <header> tag
       │     Extended: role="banner"
       │  │
       │  ├─ [Link] SkipNavLink  Style: "skip-nav"
       │  │    OnClick → SkipToContentOnClick
       │  │    Extended: aria-label="Skip to Content (Press Enter)",
       │  │              data-showskipcontent=If(EnableAccessibilityFeatures, "true", "false")
       │  │  ├─ [Text] (unnamed)  Text: "link"                          ← BUG #2: stray text node
       │  │  └─ [Text] SkipText   Text: "Skip to Content (Press Enter)"
       │  │
       │  └─ [Container] HeaderTop  Style: "header-top ThemeGrid_Container"
       │     └─ [Container] HeaderContent  Style: "header-content display-flex"
       │        │
       │        ├─ [Container] MenuIconPlaceholder  Style: "menu-icon-placeholder"   ← BUG #3: wrapper container; MenuIcon should be direct child
       │        │  └─ [BlockInstance] MenuIcon  (Common flow, no params)
       │        │
       │        ├─ [Container] ApplicationTitlePlaceholder  Style: "app-title-placeholder"  ← BUG #4: wrapper container; ApplicationTitle should be direct child
       │        │  └─ [BlockInstance] ApplicationTitle  (Common flow, no params)
       │        │
       │        └─ [Placeholder] Header  Style: "header-navigation"  EffectiveWidth: InlineBlock
       │              Default content:
       │              └─ [Container] MenuPlaceholder  Style: "menu-placeholder"     ← BUG #5: wrapper container; Menu should be direct child of Header placeholder
       │                 └─ [BlockInstance] Menu  (Common flow)
       │                       ActiveItem → -1                                      ← BUG #6: should be null/not set
       │                       ActiveSubItem → -1                                   ← BUG #6: should be null/not set
       │
       └─ [Container] ContentArea  Style: "content"  Width: (fill parent)
          │
          ├─ [Container] MainContentWrapper  Style: "main-content ThemeGrid_Container"
          │     Extended: role="main"
          │  ├─ [Placeholder] Breadcrumbs  Style: "content-breadcrumbs placeholder-empty"
          │  ├─ [Container] ContentTop  Style: "content-top display-flex align-items-center"
          │  │  ├─ [Placeholder] Title  Style: "content-top-title heading1 placeholder-empty"
          │  │  └─ [Placeholder] Actions  Style: "content-top-actions placeholder-empty"
          │  └─ [Placeholder] MainContent  Style: "content-middle"
          │
          └─ [Container] FooterContainer  Style: "content-bottom"                  ← BUG #7: should be AdvancedHtml <footer> tag
                Extended: role="contentinfo"
             └─ [Placeholder] Footer  Style: "footer ThemeGrid_Container placeholder-empty"
                   EffectiveWidth: UserDefined
```

**Bug summary:**
1. Header2: plain Container (built) vs AdvancedHtml `<header>` tag (reference) with Extended class="header", role="banner"
2. SkipNavLink: stray "link" text node
3. MenuIconPlaceholder: wrapper Container around MenuIcon (reference: MenuIcon direct child of HeaderContent)
4. ApplicationTitlePlaceholder: wrapper Container around ApplicationTitle (reference: direct child)
5. MenuPlaceholder: wrapper Container around Menu inside Header placeholder (reference: Menu is direct child of Header placeholder)
6. Menu params: ActiveItem=-1, ActiveSubItem=-1 (reference: null/not set)
7. FooterContainer: plain Container with Style="content-bottom" (reference: AdvancedHtml `<footer>` with Extended class="content-bottom", role="contentinfo")
