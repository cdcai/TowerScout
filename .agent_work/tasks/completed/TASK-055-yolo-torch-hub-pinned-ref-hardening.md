# TASK-055: YOLO Torch Hub Pinned-Ref Hardening

**Status**: COMPLETED  
**Priority**: CRITICAL  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Estimated Effort**: 6-10 hours  
**Created**: April 9, 2026  
**Last Updated**: April 9, 2026  
**Target Sprint**: Sprint 05

---

## Objective

Replace TowerScout's mutable YOLO `torch.hub` default-branch load with a tested pinned ref and ref-specific cache handling so the runtime no longer depends on whatever `ultralytics_yolov5_master` snapshot happens to exist in a user's Torch Hub cache.

This task is a focused runtime-hardening follow-up to `TASK-051`. It does not reopen the dependency audit, Docker work, or the broader smoke-baseline task.

---

## Context

`TASK-051` proved two things:

1. TowerScout's current YOLO runtime path was still dependent on `torch.hub` and GitHub/network access on first load.
2. A real user hit `ModuleNotFoundError: No module named 'pkg_resources'` because `torch.hub` loaded a stale cached `ultralytics_yolov5_master` snapshot rather than the current upstream path that TowerScout had audited.

The short-term `TASK-051` mitigation cleared stale `pkg_resources`-era caches and retried once, but it still left TowerScout tied to the mutable default branch. That was not strong enough for Sprint 05 deployment-readiness goals.

This task hardens that runtime contract without widening into vendoring YOLO locally:

- pin the YOLOv5 Hub source to a tested upstream commit SHA
- refresh only the pinned cache when that cache becomes invalid
- keep first-run GitHub dependence explicit
- preserve a narrow compatibility path for old `master` caches

---

## Scope

### Included

- Validate published YOLOv5 release refs against TowerScout's current YOLO weights
- Reject published release refs if they reintroduce `pkg_resources` or otherwise fail the live validation set
- Select and pin a tested YOLOv5 commit SHA
- Update `webapp/ts_yolov5.py` to:
  - load the pinned ref
  - use ref-specific cache recovery
  - preserve the legacy `pkg_resources` cleanup path as compatibility hygiene only
  - surface clearer first-run and refresh-failure messages
- Update `webapp/requirements.txt` to match the hardened runtime path
- Update active runtime/setup guides so the pinned Hub behavior is documented
- Record the task and sequencing in live Sprint 05 tracking

### Excluded

- Vendoring YOLO code into the repo
- Replacing `torch.hub` with a local loader
- Docker or compose changes
- `TASK-052` smoke implementation work
- Broader dependency cleanup unrelated to the hardened YOLO path

---

## Requirements (EARS Notation)

**R-055-001**: WHEN TowerScout loads YOLOv5 through `torch.hub`, THE SYSTEM SHALL load a tested pinned upstream ref instead of the mutable default branch.

**R-055-002**: WHEN the pinned Hub ref is already cached and valid, THE SYSTEM SHALL reuse that cache without forcing a redownload.

**R-055-003**: IF the cached pinned Hub ref fails due to an import/setup/cache-corruption error, THEN THE SYSTEM SHALL clear only the pinned cache and retry once with a fresh download.

**R-055-004**: IF a legacy `ultralytics_yolov5_master` cache still triggers `pkg_resources`, THEN THE SYSTEM SHALL treat it as compatibility hygiene only and SHALL NOT use it as the normal runtime path.

**R-055-005**: WHEN no cached pinned ref is available and GitHub/network access is unavailable, THE SYSTEM SHALL surface a clear first-run failure message that mentions the pinned ref and the GitHub/network requirement.

**R-055-006**: WHEN this hardening task updates the runtime contract, THE SYSTEM SHALL update `webapp/requirements.txt` and the active setup/runtime guides so the documented dependency story matches the hardened load path.

**R-055-007**: IF published YOLOv5 release tags do not satisfy the live validation set, THEN THE SYSTEM SHALL use a validated pinned commit SHA rather than falling back to the mutable default branch.

---

## Acceptance Criteria

- [x] New Type C task artifact created for `TASK-055`
- [x] `.agent_work/current-tasks.md` updated to track `TASK-055` before `TASK-052`
- [x] Published YOLOv5 release-tag validation run against TowerScout's current weights
- [x] Release-tag path rejected because it still reintroduced `pkg_resources`
- [x] A pinned YOLOv5 commit SHA selected and validated against `webapp/model_params/yolov5/newest.pt`
- [x] `webapp/ts_yolov5.py` loads the pinned ref instead of the mutable default branch
- [x] `webapp/ts_yolov5.py` refreshes only the pinned cache on refreshable cache failures
- [x] Legacy `pkg_resources` cleanup path preserved as compatibility hygiene
- [x] `webapp/requirements.txt` updated to match the hardened runtime path
- [x] Active runtime/setup guides updated to describe the pinned ref and first-run GitHub behavior
- [x] Targeted unit tests added or updated for the hardened loader behavior
- [x] Startup/import smoke rerun successfully
- [x] Pytest collection gate rerun successfully

---

## Dependencies

- `TASK-051` completed dependency audit and post-close stale-cache findings
- `webapp/model_params/yolov5/newest.pt` available locally for live validation
- GitHub/network access available for one-time pinned-ref validation

---

## Implementation Plan

### Phase 1: Live Ref Validation
- Test `v7.0` first because it is the latest published YOLOv5 release
- If `v7.0` fails, test older published releases only long enough to confirm whether the release-tag approach is viable
- If published releases still reintroduce `pkg_resources` or extra unstable behavior, switch to a tested commit-SHA pin instead of using `master`

### Phase 2: Loader Hardening
- Define explicit constants for:
  - YOLO repo
  - pinned ref
  - composed Hub spec
  - pinned cache directory
  - pinned archive filename
- Replace the mutable Hub load with the pinned spec and `trust_repo=True`
- Refresh only the pinned cache on import/cache-corruption failures
- Preserve the existing legacy stale-cache cleanup path for `pkg_resources` as a fallback compatibility cleanup only
- Improve failure text for:
  - first-run offline/no-cache failures
  - pinned-cache refresh failures

### Phase 3: Runtime Contract and Tracking
- Add any newly direct runtime imports required by the hardened path to `webapp/requirements.txt`
- Update the active runtime/setup guides so they describe:
  - pinned YOLOv5 Hub behavior
  - first-run GitHub dependence
  - current non-requirement of `pkg_resources`
- Update live Sprint 05 tracking and the `TASK-051` cross-reference notes

### Phase 4: Validation
- Update targeted unit coverage
- Re-run startup/import smoke
- Re-run `pytest --collect-only tests -q`
- Re-run live empty-cache pinned-ref load proof
- Re-run offline valid-cache proof
- Re-run offline no-cache proof and verify the clearer error message

---

## Validation Results

### Live Ref Validation
- `ultralytics/yolov5:v7.0` was rejected as the primary fix path:
  - it still imported `pkg_resources`
  - it also expected `IPython` at import time in this environment
- `ultralytics/yolov5:v6.2` was also rejected:
  - it still imported `pkg_resources`
  - it triggered extra runtime autoinstall behavior
- TowerScout instead validated commit `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`:
  - empty-cache load succeeded against `webapp/model_params/yolov5/newest.pt`
  - that commit's `utils/general.py` imported `packaging`, `pandas`, and `ultralytics`, not `pkg_resources`

### Runtime Hardening Validation
- Targeted unit coverage updated for:
  - pinned-ref load path
  - pinned-cache refresh and retry
  - legacy `pkg_resources` cleanup path
  - first-run offline/no-cache failure messaging
- `python -m pytest tests/unit/test_yolov5_cache_migration.py -q` passed: `5 passed`
- Startup/import smoke rerun after the loader change: `app_import_ok True`, `torch_cuda_available False`
- `python -m pytest --collect-only tests -q` rerun after the test update: `164 tests collected`
- Empty-cache pinned-ref load succeeded with temporary `TORCH_HOME`
- Offline cached reuse succeeded with the pinned cache present
- Offline no-cache load failed with the intended GitHub/network requirement message

---

## Non-Goals and Safety Boundaries

- Do not reintroduce the mutable default-branch Hub target
- Do not silently vendor YOLO locally under this task
- Do not fold Docker or smoke-baseline implementation into this hardening work
- Do not claim the first-run GitHub dependency is removed; only the branch/cache drift is reduced

---

## Implementation Log

### TYPE C - TASK-055 PINNED-REF HARDENING AND VALIDATION - 2026-04-09
**Objective**: Replace TowerScout's mutable YOLO Torch Hub runtime with a tested pinned ref and ref-specific cache handling before `TASK-052` defines the next smoke baseline.
**Context**: `TASK-051` closed with a short-term stale-cache mitigation, but a real user failure proved that mutable `master` cache drift was still part of the runtime contract. The user approved a follow-up hardening task rather than reopening `TASK-051`.
**Decision**: Validate published YOLOv5 release tags first, reject them if they still reintroduced `pkg_resources`, and pin a tested commit SHA instead of defaulting back to `master`.
**Execution**:
- Validated `v7.0`, `v6.2`, and the current YOLOv5 HEAD commit against `webapp/model_params/yolov5/newest.pt`.
- Rejected the release-tag path because the tested release tags still imported `pkg_resources`.
- Selected commit `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c` after live validation passed.
- Updated `webapp/ts_yolov5.py` to load the pinned ref, refresh only the pinned cache, retain legacy stale-cache cleanup, and improve GitHub/offline error text.
- Updated `webapp/requirements.txt` to carry the hardened runtime's direct dependency surface.
- Updated the active runtime/setup guides and live Sprint tracker.
**Output**:
- `webapp/ts_yolov5.py`
- `webapp/requirements.txt`
- active setup/runtime guides under `.agent_work/context/guides/`
- `.agent_work/current-tasks.md`
- this task file
**Validation**:
- Published release tags were tested and rejected on evidence
- The selected commit SHA loaded successfully with TowerScout's current weights
- The hardened loader now has targeted test coverage
**Next**: Keep `TASK-055` closed and move to `TASK-052` so the smoke baseline validates the hardened YOLO runtime path.
