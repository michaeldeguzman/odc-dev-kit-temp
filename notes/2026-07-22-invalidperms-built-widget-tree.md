# InvalidPermissions — Built Widget Tree (TestNewWebApp9 `48387023-1192-4dd6-87f8-9456df0f7964`)

Extracted 2026-07-22 via Mentor inspection.

---

```
[BlockInstance] LayoutTopMenu  (block: Layouts/LayoutTopMenu)
  Parameters:
    HasFixedHeader → True
    ExtendedClass → ""
    EnableAccessibilityFeatures → False

  ├─ Placeholder: Header
  │  └─ [Container] MenuPlaceholder
  │        Style: "menu-placeholder"      ← BUG: should be "full-height display-flex align-items-center justify-content-flex-end"
  │        Width: (fill parent)
  │        Visible: True
  │     ├─ [BlockInstance] Menu  (Common/Menu)    ← BUG: Menu should not be in Header for this screen
  │     │     Parameters: ActiveItem → -1, ActiveSubItem → -1
  │     └─ [BlockInstance] UserInfo  (Common/UserInfo)   ← CORRECT: UserInfo present
  │           Parameters: (none set)
  │
  └─ Placeholder: MainContent
     └─ [BlockInstance] BlankSlate  (OutSystemsUI/Content/BlankSlate)
           Parameters:
             ExtendedClass → (null)
             FullHeight → True

        ├─ Placeholder: Icon
        │  └─ [Icon] (unnamed)
        │        PhosphorIcon: chats-circle    ← BUG: should be "lock"; also a pre-existing "Non Existing Icon" warning
        │        Style: "icon"                 ← BUG: should be "icon text-neutral-4"
        │        IconSize: Twotimes            ← BUG: should be FontSize
        │        Visible: True
        │
        ├─ Placeholder: Content
        │  ├─ [Text] MessageText               ← BUG: bare Text node, not inside a Container; missing "heading6" style
        │  │     Text: "You don't have the necessary permission to see this screen."
        │  │     (no style)
        │  └─ [Text] SubText                   ← BUG: bare Text node, not inside "margin-top-s" Container
        │        Text: "Please contact your system administrator."
        │        (no style)
        │
        └─ Placeholder: Actions
           └─ [Link] GoToLoginLink             ← BUG: no If wrapper (link always visible, not conditional)
                 Style: "btn btn-primary"      ← BUG: should be no style (plain link)
                 Enabled: True
                 Visible: True
                 OnClick → Login (no validation)
                 (no tabindex)                 ← BUG: should be tabindex=1
              ├─ [Text] (unnamed)  Text: "link"     ← leftover default text node
              └─ [Text] GoToLoginText  Text: "Go to login"
```

**Missing vs reference:**
- Header container has wrong style class and contains Menu block (should have only UserInfo in the correctly-styled container)
- Icon wrong: name, size, style
- Content texts need container structure and "heading6" style on the main message
- Actions link needs If wrapper (GetUserId() = NullTextIdentifier()), no style, tabindex=1, and the leftover "link" text removed
