# Customer CRUD Screens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two screens in Test Anything — CustomerList (table + delete confirm) and CustomerDetail (shared create/edit form) — wired to the already-deployed Customer_* server actions.

**Architecture:** Both screens live in MainFlow. A single Mentor session is opened for Task 1 and resumed through Task 2 to keep OML state consistent. CustomerDetail uses a single `CustomerId` input parameter to switch between create and edit mode at runtime. Publish happens once after both screens are complete.

**Tech Stack:** OutSystems Developer Cloud (ODC), Mentor MCP tool. Depends on Customer_* server actions deployed at revision 5 of Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`).

---

## OutSystems Locations

| Element | Location |
|---|---|
| CustomerList screen | MainFlow UI flow |
| CustomerDetail screen | MainFlow UI flow |
| Customer_GetAll | Logic > Server Actions > Customer |
| Customer_GetById | Logic > Server Actions > Customer |
| Customer_Create | Logic > Server Actions > Customer |
| Customer_Update | Logic > Server Actions > Customer |
| Customer_Delete | Logic > Server Actions > Customer |

---

### Task 1: Create CustomerList Screen

**Purpose:** List all customers with Edit/Delete per row and a New Customer button.

- [ ] **Load mentor tools**

  Use ToolSearch with query `select:mcp__outsystems__mentor_start,mcp__outsystems__mentor_get_run` to load schemas.

- [ ] **Start new Mentor session**

  Call `mcp__outsystems__mentor_start` with:
  - `app_key`: `f464e3e1-4a26-4187-9d73-330de60ed791`
  - `prompt` (verbatim):

  ```
  Create a new Screen called "CustomerList" in the MainFlow UI flow with the role "TestAnything". Do the following:

  1. Set the screen title to "Customers".

  2. Add a Local Variable named "Customers" of type "List of ODC_CUSTOMER_FINAL".

  3. Add an OnInitialize action with the following logic:
     a. Call the Server Action "Customer_GetAll" (in Logic > Server Actions > Customer).
     b. Assign Customers = Customer_GetAll.Customers
     c. Add an If node: if Customer_GetAll.Success = False, show a Feedback Message with MessageType = Error and Message = Customer_GetAll.ErrorMessage.

  4. Add a Button at the top right of the screen with label "New Customer".
     - On click: navigate to the CustomerDetail screen with no CustomerId argument (leave CustomerId empty).

  5. Add a Table widget below the title, bound to the "Customers" local variable.
     - Columns: CUSTOMER_ID, FIRST_NAME, LAST_NAME, EMAIL, CREATED_AT.
     - Add an extra column at the right with no header for row actions.

  6. In the row actions column, add two Buttons per row:
     a. Edit button (label "Edit"):
        - On click: navigate to CustomerDetail screen, passing CustomerId = ODC_CUSTOMER_FINAL.CUSTOMER_ID (current row value).
     b. Delete button (label "Delete"):
        - On click: run a Client Action with this logic:
          i.  Use a RunJavaScript node to call the browser confirm() function with message "Delete this customer? This cannot be undone." Capture the boolean result in a local Boolean variable named "Confirmed".
          ii. Add an If node: if Confirmed = True:
              - Call Server Action "Customer_Delete" with CustomerId = ODC_CUSTOMER_FINAL.CUSTOMER_ID (current row value).
              - Add an If node: if Customer_Delete.Success = True → call Customer_GetAll again and assign Customers = Customer_GetAll.Customers to refresh the table. If Customer_Delete.Success = False → show Feedback Message with MessageType = Error and Message = Customer_Delete.ErrorMessage.
  ```

- [ ] **Poll until terminal**

  Immediately call `mcp__outsystems__mentor_get_run` with the returned `runId` and `cursor = 0`. Keep polling (advancing cursor) until `status` is `succeeded` or `failed`.

  - If `failed`: stop and report the error.
  - If `succeeded`: continue.

- [ ] **Save session tokens**

  From the terminal `mentor_get_run` result, record:
  - `mentor_session_id`
  - `mentor_session_token` (full value, do not truncate)

---

### Task 2: Create CustomerDetail Screen

**Purpose:** Shared create/edit form. CustomerId empty = create; populated = edit.

- [ ] **Resume Mentor session**

  Call `mcp__outsystems__mentor_start` with:
  - `mentor_session_id` and `mentor_session_token` from Task 1
  - `prompt` (verbatim):

  ```
  Create a new Screen called "CustomerDetail" in the MainFlow UI flow with the role "TestAnything". Do the following:

  1. Add an Input Parameter to the screen:
     - Name: CustomerId
     - Data Type: Text
     - Is Mandatory: No

  2. Add a Local Variable named "Customer" of type "ODC_CUSTOMER_FINAL".

  3. Set the screen title expression to:
     If(CustomerId = "", "New Customer", "Edit Customer")

  4. Add an OnInitialize action with the following logic:
     a. Add an If node: if CustomerId <> "":
        - Call Server Action "Customer_GetById" with CustomerId = CustomerId (the screen input parameter).
        - Add an If node: if Customer_GetById.IsFound = True → Assign Customer = Customer_GetById.Customer.
        - If Customer_GetById.Success = False OR Customer_GetById.IsFound = False → show Feedback Message with MessageType = Error and Message = "Customer not found." → navigate to CustomerList screen.

  5. Add a Form to the screen with the following input fields, all bound to the corresponding attributes of the "Customer" local variable:

     a. CUSTOMER_ID field:
        - Label: "Customer ID"
        - Input widget bound to Customer.CUSTOMER_ID
        - The input is editable only when CustomerId = "" (Create mode).
          In Edit mode (CustomerId <> ""), set the input's Enabled property to False.
        - Mark as mandatory.

     b. FIRST_NAME field:
        - Label: "First Name"
        - Input widget bound to Customer.FIRST_NAME

     c. LAST_NAME field:
        - Label: "Last Name"
        - Input widget bound to Customer.LAST_NAME

     d. EMAIL field:
        - Label: "Email"
        - Input widget bound to Customer.EMAIL

     e. CREATED_AT field (Edit mode only):
        - Label: "Created At"
        - Display as a read-only Expression widget showing Customer.CREATED_AT
        - Set its Visible property to: CustomerId <> ""
          (Hidden in Create mode, shown in Edit mode.)

  6. Add a "Save" button with the following OnClick Client Action logic:
     a. Add an If node: if CustomerId = "" (Create mode):
        - Call Server Action "Customer_Create" with Customer = Customer (the local variable).
        - Add an If node: if Customer_Create.Success = True → navigate to CustomerList. If Customer_Create.Success = False → show Feedback Message with MessageType = Error and Message = Customer_Create.ErrorMessage.
     b. Else (Edit mode):
        - Call Server Action "Customer_Update" with Customer = Customer (the local variable).
        - Add an If node: if Customer_Update.Success = True → navigate to CustomerList. If Customer_Update.Success = False → show Feedback Message with MessageType = Error and Message = Customer_Update.ErrorMessage.

  7. Add a "Cancel" button with OnClick: navigate to CustomerList screen (no parameters).
  ```

- [ ] **Poll until terminal**

  Immediately call `mcp__outsystems__mentor_get_run` with the returned `runId` and `cursor = 0`. Keep polling (advancing cursor) until `status` is `succeeded` or `failed`.

  - If `failed`: stop and report the error.
  - If `succeeded`: continue.

- [ ] **Save refreshed session tokens**

  From the terminal `mentor_get_run` result, record the refreshed:
  - `mentor_session_id`
  - `mentor_session_token` (full value, do not truncate)

---

### Task 3: Publish to Development

**Keys needed:**
- `mentor_session_id` and `mentor_session_token` from Task 2
- `env_key`: `9facfcdc-b502-42cb-b6ad-3457ce5888ae` (Development)
- `application_key`: `f464e3e1-4a26-4187-9d73-330de60ed791`

- [ ] **Load publish tools**

  Use ToolSearch with query `select:mcp__outsystems__publish_start,mcp__outsystems__publish_status,mcp__outsystems__env_app` to load schemas.

- [ ] **Start publish**

  Call `mcp__outsystems__publish_start` with:
  - `mentor_session_id` from Task 2
  - `mentor_session_token` from Task 2
  - `env_key`: `9facfcdc-b502-42cb-b6ad-3457ce5888ae`
  - `message`: `Add CustomerList and CustomerDetail CRUD screens in MainFlow. CustomerList: table bound to Customer_GetAll, Edit/Delete per row with confirm dialog, New Customer button. CustomerDetail: shared create/edit screen with CustomerId input param, form bound to ODC_CUSTOMER_FINAL local variable, calls Customer_Create or Customer_Update on Save.`

  Record the returned `operation_id`.

- [ ] **Poll publish status**

  Call `mcp__outsystems__publish_status` with `publication_id = operation_id` every 10–15 seconds until `state` is `succeeded` or `failed`.

  - If `failed`: load `mcp__outsystems__publish_logs` with `pub_key = operation_id` and report the error details. Stop.
  - If `succeeded` and `no_changes_detected = true`: warn that nothing deployed — the OML matched an already-deployed revision. Do NOT report success.
  - If `succeeded` and no de-dup: continue.

- [ ] **Confirm deployment**

  Call `mcp__outsystems__env_app` with:
  - `key`: `f464e3e1-4a26-4187-9d73-330de60ed791`
  - `env_key`: `9facfcdc-b502-42cb-b6ad-3457ce5888ae`

  Report the runtime URL to the user.

---

## Self-Review Notes

- CustomerList screen: Customer_GetAll on init ✓, Edit navigates with CustomerId ✓, Delete confirm + Customer_Delete + refresh ✓, New Customer navigates empty ✓
- CustomerDetail screen: CustomerId input param ✓, OnInitialize Customer_GetById ✓, CUSTOMER_ID disabled in edit ✓, CREATED_AT hidden in create ✓, Save branches on CustomerId ✓, Cancel navigates to CustomerList ✓
- Error handling: feedback messages on all failure paths ✓
- Session token chain: Task 1 → Task 2 → publish ✓
- Publish message detailed ✓, no_changes_detected handling ✓
- No TBDs or placeholder steps ✓
