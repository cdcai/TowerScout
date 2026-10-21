# TowerScout Project-End Planning Artifacts

**Prepared:** October 1, 2026
**Operational closeout:** October 30, 2026
**Hard project end:** October 31, 2026

## Artifacts

- `TowerScout-Comprehensive-Backlog-and-Next-Steps-2026-10-01.xlsx`
  contains the curated open-action table, W00-W10 crosswalk, task registry,
  raw unchecked-item inventory, and reviewed-source register.
- `TowerScout-Project-End-Plan-2026-10-01-to-2026-10-31.xlsx`
  contains the prioritized weekly plan, weekday calendar, milestones, capacity
  allocation, risks/decisions, and source mapping.
- `TowerScout-Comprehensive-Backlog-source-snapshot-2026-10-01.json.gz.b64`
  is the immutable, compressed source-table snapshot for the dated backlog
  workbook. It contains the original 70 task-registry rows, 711 raw unchecked
  items, and 122 source-register rows.

## Interpretation Boundary

`.agent_work/current-tasks.md` and `.agent_work/task-backlog.md` remain the
authoritative assignment sources. These workbooks are planning and review
artifacts. Historical files under `tasks/completed/` contain old unchecked
boxes and stale status text; those entries are retained in the backlog
workbook for traceability but do not become current work unless the owner
selects them again.

The project-end plan assumes 22 Monday-Friday dates from October 1 through
October 30. If October 12 is a non-working holiday for the actual team, the
available count is 21. Publication, cdcai changes, account changes, and signing
remain owner-controlled actions.

## Regeneration

Run:

```powershell
.venv\Scripts\python.exe .agent_work\scripts\generate_project_end_spreadsheets.py
```

The generator validates the snapshot identity, row counts, compressed
SHA-256, and JSON SHA-256 before use. It also validates ZIP integrity and
parses every generated Open XML part. It does not read the live task tree.
The decoded snapshot JSON SHA-256 is
`d7a23d4961e8e9e90da01e0270ad2f9b1f205470e650fc8a445502b210dbf1db`.
Changing the source inventory requires a new as-of date and new artifact and
snapshot filenames rather than overwriting the October 1 historical inventory.
The October 1 artifacts were also opened successfully in Microsoft Excel.
