# LayoutBlank — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-23

**Total discrepancies: 4**

## Discrepancies

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Root Container CSS (2nd class) | "blank" → full: "layout blank" + conditionals | "layout-blank" → full: "layout layout-blank" + conditionals |
| 2 | Container "content" wrapper | Present between root and placeholder (role="main") | Absent — placeholder is direct child of root |
| 3 | Content placeholder style | "main-content" | "content-middle" |
| 4 | Content placeholder name | "Content" | "MainContent" |

## Fix scope

1. **Root CSS**: Change style expression from `"layout layout-blank" + ...` to `"layout blank" + ...`
2. **Add Container**: Add unnamed Container with Style="content", Extended role="main" between root and the placeholder; move the placeholder inside it
3. **Placeholder style**: Change from "content-middle" to "main-content"
4. **Placeholder name**: Rename from "MainContent" to "Content"
