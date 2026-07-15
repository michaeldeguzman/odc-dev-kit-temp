# OutSystems MCP — Project Notes

## Build History

### Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`) — 2026-07-14

| Build | Revision | Start (UTC) | End (UTC) | Duration |
|---|---|---|---|---|
| CRUD server actions (Customer_GetAll, GetById, Create, Update, Delete) | Rev 4 → 5 | 2026-07-14T12:11:22Z | 2026-07-14T12:49:20Z | 37m 58s |
| CRUD screens (CustomerList, CustomerDetail) | Rev 5 → 6 | 2026-07-14T12:49:20Z | 2026-07-14T13:35:47Z | 46m 27s |
| **Total** | | | | **1h 24m 25s** |

Timestamps = revision commit times (includes Mentor AI execution + ODC publish compile). Environment: Development. Runtime URL: https://dbresults-rd-dev.outsystems.app/TestAnything

### Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`) — 2026-07-15

| Build | Revision | Notes |
|---|---|---|
| Employee entity + simple CRUD (Create, GetAll, GetById, Update, Delete) | Rev 6 → 8 | — |
| ODC_PRODUCTS CRUD wrapper (Snowflake entity) | Rev 8 → 10 | — |
| ModelApplication infrastructure + Employee audit fields + Employee CRUD wrapper (Validate, Upsert, GetCanRemove, Remove) | Rev 10 → 12 (OML only) | Publish blocked by Snowflake connection not configured in Development stage (OS-DPL-50205). OML verified clean via context_actions. |

Note: Rev 12 OML contains all Employee CRUD wrapper actions. Publish unblocked by configuring Snowflake connection in ODC Portal → Configurations → Development.

Additional builds continued in this session (revisions 12 → 18) — see 2026-07-16 section.

### Test Anything (`f464e3e1-4a26-4187-9d73-330de60ed791`) — 2026-07-16

| Build | Revision | Notes |
|---|---|---|
| TestEntity entity + TestEntity CRUD wrapper (Validate, Upsert, GetCanRemove, Remove) | Rev 12 → ~16 | Correct ModelApplication SampleEntity pattern; Session_GetNormalizedSessionUserId tagged as Function (IsFunction=True) |
| Employee CRUD wrapper rebuilt with correct pattern | ~Rev 16 → 17 | Prior implementation used wrong pattern (CreateOrUpdate, BuildFromError in Validate, entity Get instead of Aggregate); rebuilt to match SampleEntity exactly |
| Fix TestEntity_Upsert + Employee_Upsert inline function calls | Rev → 18 | Removed separate Session_GetNormalizedSessionUserId call nodes; now called inline in assign expressions (CreatedByUserId / UpdatedByUserId) |
| Organise CRUD wrappers into entity folders | Rev 18 → 19 | TestEntity_* actions moved into `TestEntity` folder; Employee_* actions moved into `Employee` folder |

Environment: Development. Runtime URL: https://dbresults-rd-dev.outsystems.app/TestAnything

**odc-crud-wrapper skill** (`/skills/odc-crud-wrapper/SKILL.md`) updated with:
- Correct ModelApplication SampleEntity pattern (ListAppend + CombineMessages in Validate; separate Create/Update; Aggregate in GetCanRemove; ProcessingException raise in Remove)
- Session_GetNormalizedSessionUserId must be tagged as Function and called inline in assign expressions — no separate call node
- All 4 CRUD wrapper actions must be placed in a folder named after the entity
