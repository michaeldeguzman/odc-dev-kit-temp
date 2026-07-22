# LayoutBase — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 7**

## Discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | LayoutWrapper CSS class | "layout layout-blank" | "layout layout-base" |
| 2 | Header2 widget type | AdvancedHtml (`<header>` tag) with Extended: class="header", role="banner" | Plain Container with Style="header", Extended: role="banner" |
| 3 | SkipNavLink children | 1 Text child only | 2 Text children — stray "link" node + real SkipText |
| 4 | MenuIcon block instance | Present (before Header placeholder, inside header-content) | Absent |
| 5 | ApplicationTitle block instance | Present (before Header placeholder, inside header-content) | Absent |
| 6 | Header placeholder default content | Menu block (Common flow, ActiveItem=null, ActiveSubItem=null) | Empty (no default content) |
| 7 | MainContentWrapper CSS class | "main-content" | "main-content ThemeGrid_Container" |

## Fix scope

Specific actions:
1. **LayoutWrapper**: Change style expression from `"layout layout-base"` to `"layout layout-blank"` (keep rest of expression intact)
2. **Header2**: Change widget type from Container to AdvancedHtml with HTML tag `<header>`; move Extended `class="header"` (currently it's in Style="header", move to Extended); keep role="banner" as Extended; remove Style field from widget
3. **SkipNavLink**: Remove the stray "link" Text node child; keep only SkipText
4. **MenuIcon**: Add BlockInstance for MenuIcon (Common flow) inside header-content Container, before ApplicationTitle and Header placeholder; no params
5. **ApplicationTitle**: Add BlockInstance for ApplicationTitle (Common flow) inside header-content Container, after MenuIcon and before Header placeholder; no params
6. **Header placeholder default content**: Add Menu block instance (Common flow) as default content of Header placeholder; ActiveItem=null, ActiveSubItem=null
7. **MainContentWrapper**: Remove "ThemeGrid_Container" from style; set style to "main-content" only
