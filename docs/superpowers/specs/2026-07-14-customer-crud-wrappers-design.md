# Design: ODC_CUSTOMER_FINAL CRUD Server Action Wrappers

**App:** Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`)
**Entity:** `ODC_CUSTOMER_FINAL` (`be98d21d-f22f-4909-bdc8-0907ab8f0549`) from Snowflake connector
**Date:** 2026-07-14

## Entity Schema

| Attribute | Type | Mandatory | PK |
|---|---|---|---|
| `CUSTOMER_ID` | Text(41) | Yes | Yes |
| `FIRST_NAME` | Text(50) | No | No |
| `LAST_NAME` | Text(50) | No | No |
| `EMAIL` | Text(100) | No | No |
| `CREATED_AT` | DateTime | No | No |

## Scope

5 server actions in TestAnything under `Logic > Server Actions > Customer`.
No UI screens. No external module.

## Actions

### Customer_GetById
- **Input:** `CustomerId: Text`
- **Output:** `Customer: ODC_CUSTOMER_FINAL`, `IsFound: Boolean`, `Success: Boolean`, `ErrorMessage: Text`
- **Logic:** Call `Get` entity action by CUSTOMER_ID. Set `IsFound = True` if record found, `IsFound = False` if not found (NullIdentifier). Exception handler sets `Success = False`, `ErrorMessage = AllExceptions.ExceptionMessage`.

### Customer_GetAll
- **Input:** none
- **Output:** `Customers: List of ODC_CUSTOMER_FINAL`, `Success: Boolean`, `ErrorMessage: Text`
- **Logic:** Aggregate over `ODC_CUSTOMER_FINAL` with no filters. Exception handler sets `Success = False`, `ErrorMessage = AllExceptions.ExceptionMessage`.

### Customer_Create
- **Input:** `Customer: ODC_CUSTOMER_FINAL` (caller must supply CUSTOMER_ID — no auto-number)
- **Output:** `CustomerId: Text`, `Success: Boolean`, `ErrorMessage: Text`
- **Logic:** Call `CreateOrUpdate` entity action. Output `CustomerId = CreatedId`. Exception handler sets `Success = False`, `ErrorMessage = AllExceptions.ExceptionMessage`.
- **Caveat:** Fails at runtime if Snowflake connector is read-only.

### Customer_Update
- **Input:** `Customer: ODC_CUSTOMER_FINAL` (must include CUSTOMER_ID)
- **Output:** `Success: Boolean`, `ErrorMessage: Text`
- **Logic:** Call `CreateOrUpdate` entity action. Exception handler sets `Success = False`, `ErrorMessage = AllExceptions.ExceptionMessage`.
- **Caveat:** Fails at runtime if Snowflake connector is read-only.

### Customer_Delete
- **Input:** `CustomerId: Text`
- **Output:** `Success: Boolean`, `ErrorMessage: Text`
- **Logic:** Call `Delete` entity action with CUSTOMER_ID. Exception handler sets `Success = False`, `ErrorMessage = AllExceptions.ExceptionMessage`.
- **Caveat:** Fails at runtime if Snowflake connector is read-only.

## Error Handling Pattern

Every action follows this pattern:
1. `AllExceptions` handler at action root
2. Handler assigns: `Success = False`, `ErrorMessage = AllExceptions.ExceptionMessage`
3. Happy path exits with `Success = True`

## Constraints

- CUSTOMER_ID is Text(41) — not auto-number. Caller is responsible for generating IDs on Create.
- No input validation logic inside wrappers — caller owns that.
- No logging inside wrappers — caller owns that.
- Write operations (Create, Update, Delete) depend on Snowflake connector DML support.
