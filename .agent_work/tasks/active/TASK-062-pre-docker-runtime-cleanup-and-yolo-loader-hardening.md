# TASK-062: Pre-Docker Runtime Cleanup and YOLO Loader Hardening

**Status**: COMPLETED  
**Priority**: HIGH  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Estimated Effort**: 6-10 hours  
**Created**: April 14, 2026  
**Last Updated**: April 14, 2026  
**Target Sprint**: Sprint 05

---

## Objective

Address the bounded April 13 senior-review follow-up items that should land on
the host runtime before `TASK-025` turns the current contract into the Docker
baseline.

This task intentionally combines a few semi-unrelated cleanup items, but keeps
them narrowly scoped so it does not turn into the broader backend or frontend
follow-on work already tracked elsewhere.

---

## Context

Sprint 05 runtime hardening already corrected the first-run blockers and
replaced the active Torch Hub path:

- `TASK-056` resolved the active runtime issues behind `UT-010`, `UT-013`, and
  the original `UT-017` concern
- `TASK-057` replaced the active YOLO load path with a vendored local runtime
- `TASK-052` established the maintained smoke baseline that Docker will reuse

The remaining pre-Docker gaps are narrower:

- `UT-003`: archived legacy `get_objects()` code still lives in
  `webapp/towerscout.py`
- `UT-009`: bounded active runtime paths still use raw `print()` instead of the
  structured TowerScout logging layer
- `UT-018`: the vendored YOLO tree still carries obvious non-runtime upstream
  surface
- `UT-019`: the active local loader still depends on temporary `sys.path`
  mutation instead of an explicit import contract

---

## Scope

### Included

- create a dedicated active task record and support document for `TASK-062`
- delete the archived legacy `get_objects()` block from `webapp/towerscout.py`
- replace raw `print()` calls only in the active custom-upload, model-upload,
  dataset export/write, manual-addition, dataset-restore, startup, and
  `ts_imgutil` polygon-parse paths
- convert the vendored YOLO runtime to explicit packaged imports under
  `vendor.yolov5_local`
- trim obvious non-runtime vendored surfaces without changing the caller-facing
  `load_local_yolov5_model(...)` contract
- update the affected unit and smoke tests plus the user-testing issue records

### Excluded

- background jobs, durable run state, or filesystem-session redesign
- broad `towerscout.py` decomposition and repo-wide logging consolidation
- frontend build modernization and `UT-012` follow-through unless a required
  edit unexpectedly touches the served JS tree
- opportunistic runtime dependency pruning unless the packaged-runtime trim
  makes a removal obviously safe

---

## Requirements (EARS Notation)

**R-062-001**: WHEN `TASK-062` begins, THE SYSTEM SHALL create task-local
documentation capturing the runtime scope and vendored-loader contract.

**R-062-002**: WHEN `webapp/towerscout.py` is cleaned up, THE SYSTEM SHALL
remove the archived legacy `get_objects()` block instead of keeping it as an
in-module string literal.

**R-062-003**: WHEN the touched active runtime paths log diagnostics, THE SYSTEM
SHALL use the existing structured TowerScout logging helpers instead of raw
`print()` calls.

**R-062-004**: WHEN the local YOLO runtime is imported, THE SYSTEM SHALL use an
explicit packaged import contract under `vendor.yolov5_local` instead of
temporary `sys.path` mutation.

**R-062-005**: WHEN the vendored YOLO snapshot is trimmed, THE SYSTEM SHALL keep
the inference import closure and provenance files while removing obvious
non-runtime upstream surfaces.

**R-062-006**: WHEN validation completes, THE SYSTEM SHALL keep the maintained
`TASK-052` smoke contract green and keep pytest collection clean.

---

## Acceptance Criteria

- [x] Dedicated task file exists for `TASK-062`
- [x] Support document exists under `.agent_work/tasks/active/TASK-062/`
- [x] `TASK-062` status is tracked in `.agent_work/current-tasks.md`
- [x] Archived legacy `get_objects()` block removed from `webapp/towerscout.py`
- [x] Touched active runtime paths no longer rely on raw `print()` calls
- [x] `ts_yolov5_local.py` uses packaged vendored imports without temporary
      `sys.path` mutation
- [x] Obvious non-runtime vendored surfaces removed
- [x] Focused unit and smoke validation passes
- [x] `UT-003`, `UT-009`, `UT-018`, and `UT-019` issue docs plus tracker are
      updated with implementation results

---

## Implementation Plan

1. Create the task-local docs and mark `TASK-062` in progress in the sprint
   tracker.
2. Remove the archived legacy detection block and migrate the bounded active
   runtime `print()` calls to structured logging.
3. Convert the vendored YOLO runtime to explicit packaged imports and trim
   obvious non-runtime surfaces.
4. Update focused tests and rerun the maintained smoke contract.
5. Record validation results and update the related UT issue docs and tracker.

---

## Implementation Log

### 2026-04-14 - Scope Lock and Task Setup
**Objective**: Start `TASK-062` with task-local documentation and a bounded
implementation contract.  
**Context**: The task combines semi-unrelated cleanup items, so scope control is
required before runtime edits begin.  
**Decision**: Keep the work bounded to the approved active-path logging cleanup
and the packaged vendored-runtime contract; defer broader decomposition and
logging consolidation to the existing follow-on tasks.  
**Execution**:
- reviewed the active tracker, `TASK-052` smoke contract, and `UT-003`,
  `UT-009`, `UT-018`, and `UT-019`
- created this active task file
- created the task-local support folder and loader-contract note
- updated the current sprint tracker to mark `TASK-062` `IN_PROGRESS`  
**Output**: Task-local documentation now exists before runtime mutations.  
**Validation**: Documentation paths are present under
`.agent_work/tasks/active/`.  
**Next**: Implement the bounded runtime cleanup and vendored-loader hardening.

### 2026-04-14 - Runtime Cleanup, Packaged Loader, and Validation
**Objective**: Finish the bounded pre-Docker cleanup and verify the corrected
host runtime contract.  
**Context**: `UT-003`, `UT-009`, `UT-018`, and `UT-019` all had to land before
 `TASK-025` fixes the Docker baseline around the current host behavior.  
**Decision**: Keep the loader explicitly packaged under
`vendor.yolov5_local`, add targeted legacy `sys.modules` aliases only while
loading pickled YOLO weights, and trim the vendored tree only to the retained
inference subset plus provenance.  
**Execution**:
- deleted the archived `get_objects()` string-literal block from
  `webapp/towerscout.py`
- replaced bounded active-path `print()` calls in `webapp/towerscout.py` and
  `webapp/ts_imgutil.py` with structured TowerScout logging
- moved the startup server message to a reachable structured log call before
  `serve(...)`
- converted `webapp/ts_yolov5_local.py` from temporary `sys.path` mutation to
  packaged `vendor.yolov5_local` imports
- rewired retained vendored YOLO modules to package-relative imports
- added explicit package markers under `webapp/vendor/`
- added targeted legacy module aliasing during model load so existing `.pt`
  checkpoints that still reference `models.*` / `utils.*` unpickle cleanly
- trimmed the vendored snapshot from 39 Python files plus samples/helpers down
  to a 23-file retained runtime plus provenance assets
- updated focused unit tests for the packaged loader contract and added Flask
  route coverage for model upload, dataset export, and dataset restore  
**Output**: The host runtime now uses an explicit packaged vendored-loader
contract, keeps existing checkpoint compatibility, and no longer carries the
targeted dead code / active-path logging debt.  
**Validation**:
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_local_loader.py -q -p no:cacheprovider`
  → `6 passed`
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_flask_routes.py -q -p no:cacheprovider`
  → `10 passed`
- `.\\.venv\\Scripts\\python.exe -m pytest tests\\integration\\test_end_to_end.py -q -p no:cacheprovider`
  → `2 passed`
- `.\\.venv\\Scripts\\python.exe -m pytest --collect-only tests -q -p no:cacheprovider`
  → `164 tests collected`
- residual warnings were limited to pre-existing `datetime.utcnow()` and
  SciPy `gaussian_filter1d` deprecation notices outside this task's scope  
**Next**: Mark `TASK-062` complete in the active tracker and leave Docker work
to build on this corrected host baseline.

---

## Validation Results

### Test Summary
**Test Date**: 2026-04-14  
**Test Environment**: Windows host repo checkout using
`.\\.venv\\Scripts\\python.exe`  
**Test Status**: PASS

### Acceptance Criteria Validation

- [x] **Task-local docs created**
- [x] **Tracker updated**
- [x] **Legacy block removed**
- [x] **Bounded logging cleanup landed**
- [x] **Packaged vendored-loader contract landed**
- [x] **Vendored tree trimmed**
- [x] **Focused validation passed**
- [x] **UT issue docs updated**
