# LayoutSideMenu — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-23 via Mentor inspection.

---

```
[WebBlock] LayoutSideMenu  (Layouts flow)
  Input Parameters:
    HasFixedHeader → Boolean, default True
    MenuBehavior → SideMenuBehavior Identifier
    EnableAccessibilityFeatures → Boolean
    ExtendedClass → Text, default ""

  [Container] LayoutWrapper
    Style: "layout layout-side"
           + If(HasFixedHeader, " fixed-header", "")
           + If(EnableAccessibilityFeatures, " has-accessible-features", "")     ← BUG #1: missing " " + MenuBehavior between fixed-header and has-accessible-features
           + If(MenuBehavior <> NullTextIdentifier(), " menu-" + MenuBehavior, "")   ← BUG #1: wrong MenuBehavior interpolation
           + If(ExtendedClass = "", "", " " + ExtendedClass)
    Width: (fill parent)
    │
    └─ [Container] MainContainer  Style: "main"  Width: (fill parent)    ← BUG #2: skip-nav should be direct child of LayoutWrapper (before MainContainer); missing <aside> AdvancedHtml
       │
       ├─ [Container] Header2  Style: "header"                           ← BUG #3: should be AdvancedHtml Header3 <header> tag; class="header" should move to Extended
       │     Extended: role="banner"
       │  │
       │  ├─ [Link] SkipNavLink  Style: "skip-nav"                       ← BUG #2 (cont): skip-nav should be outside Header2, direct under LayoutWrapper
       │  │    OnClick → SkipToContentOnClick
       │  │    Extended: aria-label, data-showskipcontent
       │  │  ├─ [Text] (unnamed)  Text: "link"                           ← BUG #4: stray text node
       │  │  └─ [Text] SkipText   Text: "Skip to Content (Press Enter)"
       │  │
       │  └─ [Container] HeaderTop  Style: "header-top ThemeGrid_Container"
       │     └─ [Container] HeaderContent  Style: "header-content display-flex"
       │        │                          ← BUG #5: MenuIcon block instance absent
       │        │                          ← BUG #6: ApplicationTitle block instance absent
       │        └─ [Placeholder] Header  Style: "header-navigation"  EffectiveWidth: InlineBlock
       │              (empty — correct, reference also has empty Header placeholder in SideMenu)
       │
       └─ [Container] ContentArea  Style: "content"  Width: (fill parent)
          │
          ├─ [Placeholder] Navigation  Style: "sidebar-nav"                ← BUG #7: Navigation should be inside <aside>, not ContentArea
          │     EffectiveWidth: UserDefined                                ← BUG #8: Navigation style should be empty (no style)
          │     (no default content)                                       ← BUG #9: Navigation should have Menu block as default content
          │
          ├─ [Container] MainContentWrapper  Style: "main-content ThemeGrid_Container"
          │     Extended: role="main"
          │  ├─ [Placeholder] Breadcrumbs  Style: "content-breadcrumbs placeholder-empty"
          │  ├─ [Container] ContentTop  Style: "content-top display-flex align-items-center"
          │  │  ├─ [Placeholder] Title  Style: "content-top-title heading1 placeholder-empty"
          │  │  └─ [Placeholder] Actions  Style: "content-top-actions placeholder-empty"
          │  └─ [Placeholder] MainContent  Style: "content-middle"
          │
          └─ [Container] FooterContainer  Style: "content-bottom"          ← BUG #10: should be AdvancedHtml <footer> tag
                Extended: role="contentinfo"
             └─ [Placeholder] Footer  Style: "footer ThemeGrid_Container placeholder-empty"
                   EffectiveWidth: UserDefined
```

**Bug summary:**
1. LayoutWrapper style: wrong MenuBehavior interpolation and position
2. Skip-nav Link: inside Header2/MainContainer — should be direct child of LayoutWrapper (before <aside> and MainContainer)
3. Header2: plain Container (built) vs AdvancedHtml Header3 `<header>` tag (reference)
4. SkipNavLink: stray "link" text node
5. MenuIcon block instance absent inside HeaderContent
6. ApplicationTitle block instance absent inside HeaderContent
7. Navigation placeholder in wrong location (inside ContentArea instead of inside <aside> AdvancedHtml)
8. Navigation placeholder has style "sidebar-nav" (reference has no style)
9. Navigation placeholder has no default content (reference has Menu block)
10. FooterContainer: plain Container (built) vs AdvancedHtml `<footer>` tag (reference)
11. Missing entirely: `<aside>` AdvancedHtml (role="complementary", class="aside-navigation") as 2nd child of LayoutWrapper
