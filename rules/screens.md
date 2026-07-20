---
description: ODC screen lifecycle and data-access conventions. Apply when creating or modifying screens in OutSystems Developer Cloud apps.
---

# ODC Screen Conventions

## Screen Lifecycle Order

ODC screens execute in this order:
1. `OnInitialize` — runs synchronously before the screen is visible; Aggregates and Data Actions have **not** run yet
2. Screen becomes visible
3. Aggregates and Data Actions run asynchronously
4. `OnAfterFetch` of each Aggregate/Data Action runs once that source finishes loading

## OnInitialize — What Is Allowed

- Setting local variable defaults
- Reading Client Variables, Session Variables, input parameters
- Redirecting based on already-known state (e.g. `GetUserId() = NullIdentifier()`)
- Calling Server Actions or Client Actions that do **not** depend on Aggregate/Data Action results

## OnInitialize — What Is Forbidden

- Reading the `.List`, `.Count`, or any output of an Aggregate or Data Action
- Any logic that depends on data from an Aggregate or Data Action result
- Violation raises: *"OnInitialize accesses Aggregates or Data Actions, but the data might not be available at this time"*

## Fix: Move Data-Dependent Logic to OnAfterFetch

If initialization logic needs Aggregate/Data Action results, move it to the `OnAfterFetch` event of that Aggregate or Data Action — not `OnInitialize`. `OnAfterFetch` only runs once the data is guaranteed available.

**Pattern:**
- `OnInitialize`: set defaults, redirect if unauthenticated, set up non-data-dependent state
- `OnAfterFetch` of `GetUserDetails` (for example): read `GetUserDetails.List.Current.*`, assign to local variables, set `OldName`/`OldEmail` snapshot values

## Snapshotting "Old" Values

When a screen needs to snapshot the current DB value of a record for comparison on save (e.g. `OldName`, `OldEmail`), set those snapshots in `OnAfterFetch` of the relevant Aggregate — not `OnInitialize`.
