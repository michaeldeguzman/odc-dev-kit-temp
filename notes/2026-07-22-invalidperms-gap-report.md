# InvalidPermissions — Gap Report

Reference: NewApp (`88f79d25-6cbf-4178-b804-199303656da4`)
Built: TestNewWebApp9 (`48387023-1192-4dd6-87f8-9456df0f7964`)
Date: 2026-07-22

**Total discrepancies: 10**

## 1. Header placeholder

| # | Element | Reference | Built |
|---|---|---|---|
| 1 | Header container style | "full-height display-flex align-items-center justify-content-flex-end" | "menu-placeholder" |
| 2 | Menu block in Header | Absent (InvalidPermissions shows UserInfo only, no navigation) | Menu block present (ActiveItem=-1, ActiveSubItem=-1) |

## 2. Icon placeholder

| # | Property | Reference | Built |
|---|---|---|---|
| 3 | Icon name | lock | chats-circle (also triggers "Non Existing Icon" warning) |
| 4 | Icon style | "icon text-neutral-4" | "icon" (missing text-neutral-4) |
| 5 | Icon size | FontSize | Twotimes |

## 3. Content placeholder structure

| # | Element | Reference | Built |
|---|---|---|---|
| 6 | Main message | Container (no style) → Text "You don't have..." with style "heading6" | Bare Text node "MessageText" with no style |
| 7 | Sub-message | Container "margin-top-s" → Text "Please contact..." | Bare Text node "SubText" directly in Content placeholder |

## 4. Actions placeholder

| # | Element | Reference | Built |
|---|---|---|---|
| 8 | Conditional If widget | If "NotRegistered" (Condition: GetUserId() = NullTextIdentifier(), ShowTrueOrPreview) wrapping the link | Absent — link always visible |
| 9 | Link style | (no style — plain link) | "btn btn-primary" |
| 10 | Stray text node | Absent | Text "link" (leftover default) alongside "Go to login" |
| 11 | tabindex | tabindex=1 on Link | Absent |

**Count: 11 discrepancies** (items re-counted; row 10-11 are combined in the table above).

## Fix scope

Specific actions:
1. Replace Header container: change style to "full-height display-flex align-items-center justify-content-flex-end"; remove Menu block, keep only UserInfo block
2. Fix Icon: name→lock, style→"icon text-neutral-4", size→FontSize
3. Fix Content: replace bare Text nodes with Container(no style) → Text("heading6") + Container("margin-top-s") → Text(no style)
4. Fix Actions: wrap GoToLoginLink in If widget (Condition: GetUserId() = NullTextIdentifier(), ShowTrueOrPreview); remove "btn btn-primary" style from Link; remove stray "link" text node; add tabindex=1
