# ODC_CUSTOMER_FINAL CRUD Server Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create 5 server actions in TestAnything wrapping CRUD operations on ODC_CUSTOMER_FINAL from the Snowflake connector.

**Architecture:** All 5 actions live in Logic > Server Actions > Customer folder in TestAnything. Each action follows the same error pattern: AllExceptions handler sets Success=False + ErrorMessage, happy path sets Success=True. Built via a single reused Mentor session across all 5 actions, then published to Development.

**Tech Stack:** OutSystems Developer Cloud (ODC), Mentor MCP tool, Snowflake connector entity ODC_CUSTOMER_FINAL (key: `be98d21d-f22f-4909-bdc8-0907ab8f0549`), App key: `f464e3e1-4a26-4187-9d73-330de60ed791`

---

### Task 0: Resolve Environment Key

**Purpose:** Get the Development env_key needed for publish in Task 6.

- [ ] Call `env_list` MCP tool
- [ ] Identify the Development environment row
- [ ] Record its `env_key` — used verbatim in Task 6

---

### Task 1: Create Customer_GetById

**OutSystems path:** Logic > Server Actions > Customer > Customer_GetById

- [ ] Call `mentor_start` with:
  - `app_key`: `f464e3e1-4a26-4187-9d73-330de60ed791`
  - `prompt`:
    ```
    Create a folder called "Customer" under Server Actions in the Logic tab if it does not already exist.

    Inside that folder, create a new Server Action called "Customer_GetById" with:

    Input parameters:
    - CustomerId (Text, Mandatory: Yes)

    Output parameters:
    - Customer (ODC_CUSTOMER_FINAL record type, Mandatory: No)
    - IsFound (Boolean, default: False)
    - Success (Boolean, default: False)
    - ErrorMessage (Text)

    Logic flow:
    1. Add an AllExceptions exception handler at the action root level.
       In the handler flow: Assign Success = False, Assign ErrorMessage = AllExceptions.ExceptionMessage.
    2. On the main flow, add an Aggregate that fetches from ODC_CUSTOMER_FINAL
       with the filter: ODC_CUSTOMER_FINAL.CUSTOMER_ID = CustomerId. Max records = 1.
    3. Assign Customer = GetCustomerById.List.Current.ODC_CUSTOMER_FINAL
    4. Assign IsFound = (GetCustomerById.Count > 0)
    5. Assign Success = True
    ```
- [ ] Immediately poll `mentor_get_run` with the returned `runId` and `cursor = 0`
- [ ] Keep polling (advancing cursor) until `status` is terminal (`succeeded` or `failed`)
- [ ] If `failed`: surface the error message and stop
- [ ] Save `mentor_session_id` and `mentor_session_token` from `result` in the terminal response

---

### Task 2: Create Customer_GetAll

**OutSystems path:** Logic > Server Actions > Customer > Customer_GetAll

- [ ] Call `mentor_start` with:
  - `mentor_session_id` and `mentor_session_token` from Task 1
  - `prompt`:
    ```
    Create a new Server Action called "Customer_GetAll" inside the Customer folder with:

    Input parameters: none

    Output parameters:
    - Customers (List of ODC_CUSTOMER_FINAL)
    - Success (Boolean, default: False)
    - ErrorMessage (Text)

    Logic flow:
    1. Add an AllExceptions exception handler at the action root level.
       In the handler flow: Assign Success = False, Assign ErrorMessage = AllExceptions.ExceptionMessage.
    2. On the main flow, add an Aggregate that fetches all records from ODC_CUSTOMER_FINAL with no filters.
    3. Assign Customers = GetAllCustomers.List
    4. Assign Success = True
    ```
- [ ] Immediately poll `mentor_get_run` with returned `runId` and `cursor = 0`
- [ ] Keep polling until terminal
- [ ] If `failed`: surface error and stop
- [ ] Save refreshed `mentor_session_token` from terminal `result`

---

### Task 3: Create Customer_Create

**OutSystems path:** Logic > Server Actions > Customer > Customer_Create

- [ ] Call `mentor_start` with:
  - `mentor_session_id` and refreshed `mentor_session_token` from Task 2
  - `prompt`:
    ```
    Create a new Server Action called "Customer_Create" inside the Customer folder with:

    Input parameters:
    - Customer (ODC_CUSTOMER_FINAL record type, Mandatory: Yes)
      Note: Caller must supply CUSTOMER_ID (Text, 41 chars). There is no auto-number on this entity.

    Output parameters:
    - CustomerId (Text)
    - Success (Boolean, default: False)
    - ErrorMessage (Text)

    Logic flow:
    1. Add an AllExceptions exception handler at the action root level.
       In the handler flow: Assign Success = False, Assign ErrorMessage = AllExceptions.ExceptionMessage.
    2. On the main flow, call the CreateOrUpdate built-in entity action for ODC_CUSTOMER_FINAL,
       passing the Customer input record.
    3. Assign CustomerId = Customer.CUSTOMER_ID
    4. Assign Success = True
    ```
- [ ] Immediately poll `mentor_get_run` with returned `runId` and `cursor = 0`
- [ ] Keep polling until terminal
- [ ] If `failed`: surface error and stop
- [ ] Save refreshed `mentor_session_token` from terminal `result`

---

### Task 4: Create Customer_Update

**OutSystems path:** Logic > Server Actions > Customer > Customer_Update

- [ ] Call `mentor_start` with:
  - `mentor_session_id` and refreshed `mentor_session_token` from Task 3
  - `prompt`:
    ```
    Create a new Server Action called "Customer_Update" inside the Customer folder with:

    Input parameters:
    - Customer (ODC_CUSTOMER_FINAL record type, Mandatory: Yes)
      Must include a valid CUSTOMER_ID identifying the record to update.

    Output parameters:
    - Success (Boolean, default: False)
    - ErrorMessage (Text)

    Logic flow:
    1. Add an AllExceptions exception handler at the action root level.
       In the handler flow: Assign Success = False, Assign ErrorMessage = AllExceptions.ExceptionMessage.
    2. On the main flow, call the CreateOrUpdate built-in entity action for ODC_CUSTOMER_FINAL,
       passing the Customer input record.
    3. Assign Success = True
    ```
- [ ] Immediately poll `mentor_get_run` with returned `runId` and `cursor = 0`
- [ ] Keep polling until terminal
- [ ] If `failed`: surface error and stop
- [ ] Save refreshed `mentor_session_token` from terminal `result`

---

### Task 5: Create Customer_Delete

**OutSystems path:** Logic > Server Actions > Customer > Customer_Delete

- [ ] Call `mentor_start` with:
  - `mentor_session_id` and refreshed `mentor_session_token` from Task 4
  - `prompt`:
    ```
    Create a new Server Action called "Customer_Delete" inside the Customer folder with:

    Input parameters:
    - CustomerId (Text, Mandatory: Yes)

    Output parameters:
    - Success (Boolean, default: False)
    - ErrorMessage (Text)

    Logic flow:
    1. Add an AllExceptions exception handler at the action root level.
       In the handler flow: Assign Success = False, Assign ErrorMessage = AllExceptions.ExceptionMessage.
    2. On the main flow, call the Delete built-in entity action for ODC_CUSTOMER_FINAL,
       passing CUSTOMER_ID = CustomerId.
    3. Assign Success = True
    ```
- [ ] Immediately poll `mentor_get_run` with returned `runId` and `cursor = 0`
- [ ] Keep polling until terminal
- [ ] If `failed`: surface error and stop
- [ ] Save refreshed `mentor_session_token` from terminal `result`

---

### Task 6: Publish to Development

- [ ] Call `publish_start` with:
  - `mentor_session_id` from Task 1 (same session throughout)
  - `mentor_session_token` (refreshed — from Task 5 terminal result)
  - `env_key` from Task 0
- [ ] Record the returned `operation_id`
- [ ] Poll `publish_status` with `operation_id` every 10–15 seconds until `state` is `succeeded` or `failed`
- [ ] If `failed`: call `publish_logs` with `pub_key = operation_id` and surface the error messages
- [ ] If `succeeded` and `no_changes_detected = true`: warn that nothing deployed (ODC de-duped the revision) — do not report as success
- [ ] If `succeeded` and no de-dup: call `env_app` with `env_key` (Task 0) and `application_key = f464e3e1-4a26-4187-9d73-330de60ed791` to get runtime URL and confirm deployment

---

## Self-Review Notes

- All 5 actions from spec covered: GetById, GetAll, Create, Update, Delete ✓
- AllExceptions pattern applied in every action ✓
- Customer folder creation included in Task 1 ✓
- Snowflake write-op caveat: Create/Update/Delete will fail at runtime if connector is read-only — documented in spec ✓
- mentor_session_token chain: Task 1 → 2 → 3 → 4 → 5 → publish, each step saves refreshed token ✓
- GetById uses Aggregate (safer for external Snowflake entities than Get entity action) ✓
- No TBDs, no placeholder steps ✓
