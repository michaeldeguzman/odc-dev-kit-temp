# LayoutTopMenu — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 7**

## Discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Header2 widget type | AdvancedHtml `<header>` tag with Extended: class="header", role="banner" | Plain Container with Style="header", Extended: role="banner" |
| 2 | SkipNavLink children | 1 Text child only | 2 Text children — stray "link" + SkipText |
| 3 | MenuIcon in HeaderContent | Direct BlockInstance child of HeaderContent | Wrapped in Container "menu-icon-placeholder" |
| 4 | ApplicationTitle in HeaderContent | Direct BlockInstance child of HeaderContent | Wrapped in Container "app-title-placeholder" |
| 5 | Header placeholder default content | Menu block directly inside Header placeholder (no wrapper) | Menu wrapped in Container "menu-placeholder" |
| 6 | Menu parameter bindings | ActiveItem=null (not set), ActiveSubItem=null (not set) | ActiveItem=-1, ActiveSubItem=-1 |
| 7 | Footer widget type | AdvancedHtml `<footer>` tag with Extended: class="content-bottom", role="contentinfo" | Plain Container with Style="content-bottom", Extended: role="contentinfo" |

## Fix scope

1. **Header2**: Change from Container to AdvancedHtml `<header>` tag; move class from Style="header" to Extended class="header"; keep role="banner" as Extended
2. **SkipNavLink**: Remove the stray unnamed "link" Text node
3. **MenuIcon**: Remove MenuIconPlaceholder wrapper Container; make MenuIcon block instance a direct child of HeaderContent
4. **ApplicationTitle**: Remove ApplicationTitlePlaceholder wrapper Container; make ApplicationTitle block instance a direct child of HeaderContent
5. **Header default content**: Remove MenuPlaceholder wrapper Container; make Menu block instance a direct child of the Header placeholder
6. **Menu params**: Set ActiveItem and ActiveSubItem to null/not set (remove the -1 values)
7. **Footer**: Change FooterContainer from Container to AdvancedHtml `<footer>` tag; move class from Style="content-bottom" to Extended class="content-bottom"; keep role="contentinfo" as Extended
