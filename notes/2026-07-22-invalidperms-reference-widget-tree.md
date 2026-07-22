# InvalidPermissions — Reference Widget Tree (NewApp `88f79d25-6cbf-4178-b804-199303656da4`)

Extracted 2026-07-22 via Mentor inspection.

---

```
[BlockInstance] LayoutTopMenu  (block: Layouts/LayoutTopMenu)
  Parameters: all null/default (EnableAccessibilityFeatures, ExtendedClass, HasFixedHeader all unset)

  ├─ Placeholder: Header
  │  └─ [Container] (unnamed)
  │        Style: "full-height display-flex align-items-center justify-content-flex-end"
  │        Width: (fill parent)
  │        Visible: True
  │     └─ [BlockInstance] UserInfo  (block: Common/UserInfo)
  │           Parameters: (none set)
  │
  └─ Placeholder: MainContent
     └─ [BlockInstance] BlankSlate  (block: OutSystemsUI/Content/BlankSlate)
           Parameters:
             ExtendedClass → (null/default)
             FullHeight → True

        ├─ Placeholder: Icon
        │  └─ [Icon] Icon1
        │        PhosphorIcon: lock
        │        Weight: regular
        │        IconSize: FontSize
        │        Style: "icon text-neutral-4"
        │        Visible: True
        │
        ├─ Placeholder: Content
        │  ├─ [Container] (unnamed)
        │  │     (no style)
        │  │     Width: (fill parent)
        │  │     Visible: True
        │  │  └─ [Text] (unnamed)
        │  │        Text: "You don't have the necessary permission to see this screen."
        │  │        Style: "heading6"
        │  │
        │  └─ [Container] (unnamed)
        │        Style: "margin-top-s"
        │        Width: (fill parent)
        │        Visible: True
        │     └─ [Text] (unnamed)
        │           Text: "Please contact your system administrator."
        │           (no style)
        │
        └─ Placeholder: Actions
           └─ [If] NotRegistered
                 Condition: GetUserId() = NullTextIdentifier()
                 ShowTrueOrPreview: True
              └─ True branch:
                 └─ [Link] (unnamed)
                       (no style)
                       Enabled: True
                       Visible: True
                       OnClick → Login (Common/Login, no validation)
                       Extended properties: tabindex → 1
                    └─ [Text] (unnamed)
                          Text: "Go to login"
```

**Notes:**
- Header only has UserInfo block — no Menu block (unlike other screens with LayoutTopMenu)
- The "Go to login" link is conditional — only shown when user is not logged in
- LayoutTopMenu params are all null/default in the reference
- BlankSlate Content placeholder has container structure (two containers with heading6 + subtext), not bare sibling Text nodes
