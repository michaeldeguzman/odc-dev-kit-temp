# Design: ODC_CUSTOMER_FINAL CRUD Screens

**App:** Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`)
**Date:** 2026-07-14
**Depends on:** `docs/superpowers/specs/2026-07-14-customer-crud-wrappers-design.md`

## Scope

2 new screens in MainFlow: `CustomerList` and `CustomerDetail`.
No new server actions (wraps already-deployed Customer_* actions).

## Entity Reference

`ODC_CUSTOMER_FINAL` attributes:
| Attribute | Type | Notes |
|---|---|---|
| CUSTOMER_ID | Text(41) | PK, user-supplied, no auto-number |
| FIRST_NAME | Text(50) | Optional |
| LAST_NAME | Text(50) | Optional |
| EMAIL | Text(100) | Optional |
| CREATED_AT | DateTime | Snowflake-managed, read-only |

## Screen 1 — CustomerList

**UI Flow:** MainFlow
**Input parameters:** none
**Role:** TestAnything (matches existing screens)

### Layout

- Page title: "Customers"
- Top-right: "New Customer" button → navigates to CustomerDetail (no CustomerId)
- Table columns: CUSTOMER_ID, FIRST NAME, LAST NAME, EMAIL, CREATED AT, (actions)
- Per row: Edit button → navigates to CustomerDetail with CUSTOMER_ID; Delete button → confirm dialog → Customer_Delete

### Behaviours

| Event | Action |
|---|---|
| OnInitialize | Call `Customer_GetAll`. Bind result list to table. If `Success = False`, show feedback message with `ErrorMessage`. |
| Edit button click | Navigate to CustomerDetail with `CustomerId = row.CUSTOMER_ID` |
| Delete button click | Show ODC confirm dialog: "Delete this customer? This cannot be undone." On confirm → call `Customer_Delete(CustomerId = row.CUSTOMER_ID)`. If `Success = True` → re-call `Customer_GetAll` and refresh. If `Success = False` → show feedback message with `ErrorMessage`. |
| New Customer button click | Navigate to CustomerDetail (no CustomerId argument) |

## Screen 2 — CustomerDetail

**UI Flow:** MainFlow
**Input parameters:** `CustomerId` (Text, optional)
**Role:** TestAnything

Mode is determined at runtime: `CustomerId = ""` → Create mode; `CustomerId ≠ ""` → Edit mode.

### Local variable

`Customer` of type `ODC_CUSTOMER_FINAL` — holds the form data. Bound bidirectionally to all form inputs.

### Layout

- Page title expression: `If(CustomerId = "", "New Customer", "Edit Customer")`
- Form fields (2-column grid):
  - CUSTOMER_ID — editable input in Create; disabled display in Edit
  - FIRST_NAME — editable input
  - LAST_NAME — editable input
  - EMAIL — editable input
  - CREATED_AT — shown read-only only in Edit mode; hidden in Create mode
- Save button
- Cancel button → navigate to CustomerList

### Behaviours

| Event | Action |
|---|---|
| OnInitialize | If `CustomerId ≠ ""`: call `Customer_GetById(CustomerId)`. If `IsFound = True` → assign `Customer = result`. If `IsFound = False` or `Success = False` → show feedback message, navigate back to CustomerList. |
| Save button click (Create mode) | Set `Customer.CUSTOMER_ID = CustomerId input value`. Call `Customer_Create(Customer)`. If `Success = True` → navigate to CustomerList. If `Success = False` → show feedback message with `ErrorMessage`. |
| Save button click (Edit mode) | Call `Customer_Update(Customer)`. If `Success = True` → navigate to CustomerList. If `Success = False` → show feedback message with `ErrorMessage`. |
| Cancel button click | Navigate to CustomerList |

### Field visibility rules

| Field | Create mode | Edit mode |
|---|---|---|
| CUSTOMER_ID input | Visible, editable | Visible, disabled |
| FIRST_NAME | Visible, editable | Visible, editable |
| LAST_NAME | Visible, editable | Visible, editable |
| EMAIL | Visible, editable | Visible, editable |
| CREATED_AT | Hidden | Visible, read-only text |

## Error Handling

All server action errors surface via ODC feedback message widget on the screen.
No custom error styling beyond standard ODC feedback message.

## Navigation Map

```
CustomerList  ──[New Customer]──→  CustomerDetail (no CustomerId)
              ──[Edit]──────────→  CustomerDetail (CustomerId = row.CUSTOMER_ID)
CustomerDetail ──[Save/Cancel]──→  CustomerList
```

## Out of Scope

- Search / filter on CustomerList
- Pagination (Customer_GetAll returns all rows)
- Field-level validation (caller responsibility per wrapper design)
- Role-based access beyond existing TestAnything role
