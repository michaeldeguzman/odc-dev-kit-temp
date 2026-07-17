# TableRecords with an empty List — "no records" despite a structurally-correct table

**The trap:** Source HTML has a `<table>` with real `<tr>` data rows (e.g., 5 client records, 12 transactions). The spec creates a TableRecords widget with the right columns, the right styling, the right header — but its `Source` / `List` is never populated. Published table renders ZERO rows. User sees the empty-state ("No records to display") even though the structure looks correct.

**Why it happens at the runtime level:** TableRecords doesn't auto-populate from the source HTML. It needs a real data source — either a Server Action returning records (`add_aggregate` → entity query) or a Local Variable of type `List<Entity>` seeded explicitly. Without that, the source is empty and the widget renders the empty-state.

## The fix — seed the List from the source `<tr>` rows

For static-demo / non-persisted tables (the common case when porting a design with hardcoded rows):

1. **Create a Local Variable** of type `List<EntityX>` (or a structure if you don't have entities yet).
2. **In the screen's OnInitialize action,** append one record per source `<tbody><tr>` via the `ListAppend` / `List_Append` action. Copy the cell values verbatim from the source — so the demo data matches the design.
3. **Bind the TableRecords' `Source` property** to that Local Variable.

For data-backed tables (entity exists, real CRUD):

- Create a real `add_aggregate` against the entity (recommended path when you need persistence).
- Bind the TableRecords' `Source` to the aggregate's output.

In both cases: **no rows = no render**. The widget's apparent structure (columns, header, styling) is irrelevant if Source is empty.

## How to detect during source inspection

For each `<table>` in the source HTML:

```bash
grep -nE '<tbody>|<tr>' source.html
```

Count the `<tbody><tr>` rows. If > 0, you have demo data. Make sure the spec.json's section for that table includes a `seed_records` array with one entry per source row.

In the spec.json, for any TableRecords section that needs static demo data:

```json
{
  "outsystems_hints": {
    "block": "TableRecords",
    "source_kind": "local_var_list",
    "seed_records": [
      { "Name": "Maria Garcia", "Status": "Active", "Balance": 4287.42, "OpenedAt": "2025-12-14" },
      { "Name": "John Smith", "Status": "Pending", "Balance": 12500.00, "OpenedAt": "2026-01-08" },
      ...
    ]
  }
}
```

Mentor's instructions then say: "for any section with `source_kind: local_var_list`, create the Local Variable, append each record in OnInitialize, bind TableRecords.Source to the variable."

## How to prevent (Mentor instructions)

Spec preamble:

> *"Every TableRecords widget MUST have a non-empty Source. For static-demo tables (no entity yet), seed via a Local Variable of List<Entity> populated in OnInitialize using ListAppend, one append per source `<tr>` row, copying cell values verbatim. For data-backed tables, bind to an aggregate. NEVER ship a TableRecords with an unset Source — the published table renders 'no records'."*

In the design-to-app's Step 3d (polish-checklist acceptance items), add:

- *"Every TableRecords' Source is bound to a non-empty List or aggregate. Verify post-publish by checking the published table has the expected row count."*

## One append per source `<tr>`

Not an invented count. If the source has 7 rows, append 7 records. If the source has 23 rows, append 23. Don't truncate to "5 for the demo" — the source is the spec.

## Field-test evidence

APP1387 / APP1388 / APP1420 (2026-06-02): three different "admin iterates" all had the same complaint — *"no records in the table."* In each case, the source HTML had a populated `<table>` but the spec created a TableRecords with no seeded data. Adding the `add_list_append_node` ops per row fixed it on all three.

## Attribution

- [`claude-oml-tool/oml-tool/skills/odc/validated/tablerecords-non-empty-source.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/tablerecords-non-empty-source.md) — validated 2026-06-02 (APP1387 / APP1388 / APP1420)
- See also: [`claude-oml-tool/oml-tool/skills/odc/validated/static-demo-table-records-v2.md`](https://github.com/OutSystems/claude-oml-tool/blob/main/oml-tool/skills/odc/validated/static-demo-table-records-v2.md) — canonical static-demo recipe, validated 2026-05-18 via `Probe_TableRecordsV2`
