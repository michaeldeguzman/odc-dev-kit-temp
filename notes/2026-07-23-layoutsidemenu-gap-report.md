# LayoutSideMenu — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 11**

## Discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | LayoutWrapper style expression | `"layout layout-side" + If(HasFixedHeader, " fixed-header", "") + " " + MenuBehavior + If(not EnableAccessibilityFeatures, "", " has-accessible-features") + If(ExtendedClass = "", "", " " + ExtendedClass)` | `"layout layout-side" + If(HasFixedHeader, " fixed-header", "") + If(EnableAccessibilityFeatures, " has-accessible-features", "") + If(MenuBehavior <> NullTextIdentifier(), " menu-" + MenuBehavior, "") + ...` |
| 2 | Skip-nav Link location | Direct child of LayoutWrapper (1st child, before <aside> and "main") | Inside Header2 Container (wrong structural level) |
| 3 | `<aside>` AdvancedHtml | Present as 2nd child of LayoutWrapper (role="complementary", class="aside-navigation") | Absent entirely |
| 4 | Navigation placeholder location | Inside <aside> AdvancedHtml | Inside ContentArea Container |
| 5 | Navigation placeholder style | No style (empty) | "sidebar-nav" |
| 6 | Navigation default content | Menu block (Common flow, ActiveItem=null, ActiveSubItem=null) | Empty |
| 7 | Header2 widget type | AdvancedHtml `<header>` tag (named Header3 in reference) with Extended: class="header", role="banner" | Plain Container with Style="header", Extended: role="banner" |
| 8 | SkipNavLink children | 1 Text child only | 2 Text children — stray "link" node + real SkipText |
| 9 | MenuIcon block instance | Present (inside HeaderContent, before Header placeholder) | Absent |
| 10 | ApplicationTitle block instance | Present (inside HeaderContent, before Header placeholder) | Absent |
| 11 | Footer widget type | AdvancedHtml `<footer>` tag (Extended: class="content-bottom", role="contentinfo") | Plain Container with Style="content-bottom", Extended: role="contentinfo" |

## Fix scope

Target structure for LayoutWrapper children (top level):
1. (unnamed Link) "skip-nav" — move out of Header2, make direct child of LayoutWrapper
2. (unnamed AdvancedHtml <aside>) — ADD, role="complementary", class="aside-navigation"
   - Navigation [Placeholder] (no style, EffectiveWidth=UserDefined) — MOVE here from ContentArea
   - Add Menu block as default content of Navigation
3. (unnamed Container) "main" — existing MainContainer (keep)
   - Header: change to AdvancedHtml <header> (Header3), remove stray text, add MenuIcon + ApplicationTitle
   - ContentArea: remove Navigation placeholder; change FooterContainer to AdvancedHtml <footer>

Specific actions:
1. Fix LayoutWrapper style expression: `" " + MenuBehavior` between fixed-header and has-accessible-features; `If(not EnableAccessibilityFeatures, "", " has-accessible-features")` (invert condition)
2. Move SkipNavLink to be 1st child of LayoutWrapper (currently inside Header2)
3. Add <aside> AdvancedHtml as 2nd child of LayoutWrapper (after skip-nav, before "main" Container); Extended: role="complementary", class="aside-navigation"
4. Move Navigation placeholder from ContentArea into <aside>; remove style; add Menu block as default content
5. Change Header2 to AdvancedHtml <header> tag; move style="header" to Extended class="header"; keep role="banner" as Extended
6. Remove stray "link" Text from SkipNavLink
7. Add MenuIcon block instance (Common flow) before Header placeholder inside HeaderContent
8. Add ApplicationTitle block instance (Common flow) before Header placeholder inside HeaderContent
9. Change FooterContainer to AdvancedHtml <footer> tag; move style="content-bottom" to Extended class="content-bottom"
