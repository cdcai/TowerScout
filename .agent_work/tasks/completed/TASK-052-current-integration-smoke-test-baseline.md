# TASK-052: Current Integration Smoke Test Baseline

**Status**: COMPLETED  
**Priority**: CRITICAL  
**Type**: A (Quality / Validation)  
**Estimated Effort**: 4-8 hours  
**Created**: April 13, 2026  
**Last Updated**: April 13, 2026  
**Target Sprint**: Sprint 05

---

## Objective

Replace the quarantined legacy end-to-end harness with a current smoke baseline that validates the live Flask boot surface and one bounded detection-readiness path on top of the corrected Sprint 05 runtime contract.

This task exists to give `TASK-025` Docker work a stable validation target tied to the current app rather than removed routes, stale mocks, or the retired Torch Hub runtime.

---

## Context

Sprint 05 sequencing puts `TASK-052` directly before `TASK-025`. The prerequisites are now complete:

- `TASK-051` established the corrected runtime dependency contract
- `TASK-055` hardened the YOLO path ahead of Docker planning
- `TASK-056` corrected first-run blockers and deployment-hostile runtime behavior
- `TASK-057` replaced the active Torch Hub load path with a TowerScout-owned local YOLO runtime

The remaining validation problem is test drift:

- `tests/integration/test_end_to_end.py` is still a quarantined module-level skip
- `tests/unit/test_flask_routes.py` still targets removed routes such as `/draw_polygon`, `/get_status`, and `POST /cancel_detection`
- current route smoke exists only as ad hoc host-side evidence in `.agent_work/tasks/active/TASK-057/TASK-057-broader-app-and-host-smoke.md`, not as the maintained automated baseline that Docker can reuse

---

## Scope

### Included

- create a dedicated maintained task record for `TASK-052`
- replace the quarantined legacy integration harness with current smoke tests
- update stale Flask route tests so they match the live Flask route surface
- cover current app boot, provider/config route availability, progress-route behavior, and a bounded `POST /getobjects` readiness path
- keep the detection readiness path bounded so it proves the local YOLO runtime still initializes without turning this task into a full browser suite

### Excluded

- browser workflow coverage already maintained under the Puppeteer smoke harness
- Docker implementation work
- full provider-backed live detection or geocoding E2E coverage
- broad test-architecture refactors outside the stale surfaces directly blocking the smoke baseline

---

## Requirements (EARS Notation)

**R-052-001**: WHEN `TASK-052` begins, THE SYSTEM SHALL create a dedicated task record documenting the live smoke-baseline rebuild.

**R-052-002**: WHEN the legacy smoke baseline is replaced, THE SYSTEM SHALL validate the current Flask boot surface instead of removed legacy endpoints.

**R-052-003**: WHEN the current route smoke runs, THE SYSTEM SHALL cover the maintained setup/provider/config route surface needed by current frontend boot behavior.

**R-052-004**: WHEN the smoke validates detection readiness, THE SYSTEM SHALL exercise the active `POST /getobjects` route deeply enough to catch local YOLO runtime initialization regressions.

**R-052-005**: IF provider keys, model files, or other bounded smoke prerequisites are unavailable, THEN THE SYSTEM SHALL skip the bounded readiness path with an explicit reason rather than failing on unrelated environment drift.

**R-052-006**: WHEN stale route tests are updated, THE SYSTEM SHALL retire assumptions about removed routes and old event-helper APIs.

**R-052-007**: WHEN `TASK-052` validation completes, THE SYSTEM SHALL leave `pytest --collect-only tests -q` clean on the updated smoke baseline.

---

## Acceptance Criteria

- [x] Dedicated task file created for `TASK-052`
- [x] `TASK-052` marked in progress in `.agent_work/current-tasks.md`
- [x] `tests/integration/test_end_to_end.py` no longer remains a module-level quarantine skip
- [x] current smoke exists for current app boot + key live routes
- [x] smoke includes one bounded detection-readiness path on the local YOLO runtime contract
- [x] stale Flask route tests match the live route surface
- [x] focused smoke validation passes
- [x] `pytest --collect-only tests -q` remains clean

---

## Implementation Plan

1. Create the task file and mark `TASK-052` in progress in the sprint tracker.
2. Replace the stale route-test surface with current route and progress/config smoke coverage.
3. Rewrite `tests/integration/test_end_to_end.py` into the maintained current smoke baseline.
4. Run focused pytest validation plus collection to confirm the updated baseline is stable.

---

## Implementation Log

### 2026-04-13 - Discovery and Scope Lock
**Objective**: Confirm whether `TASK-052` is ready to start and identify the exact stale validation surfaces it must replace.  
**Context**: Sprint 05 sequencing requires `TASK-052` after `TASK-056` and `TASK-057` but before `TASK-025`.  
**Decision**: Treat the task as ready to start because the runtime prerequisites are complete and the remaining failures align with the known stale validation boundary.  
**Execution**:
- reviewed `.github/copilot-instructions.md`, `.agent_work/current-tasks.md`, `.agent_work/task-backlog.md`, and `.agent_work/completed-tasks.md`
- confirmed `TASK-052` remained `NOT_STARTED` while `TASK-051`, `TASK-055`, `TASK-056`, and `TASK-057` were completed
- ran `pytest --collect-only tests -q -p no:cacheprovider`
- ran focused stale-surface checks against `tests/unit/test_config.py` and `tests/unit/test_flask_routes.py`  
**Output**:
- collection was clean at `170 tests collected`
- `tests/unit/test_config.py` passed
- `tests/unit/test_flask_routes.py` failed because it still targeted removed routes and old helper APIs  
**Validation**: The failure pattern matched the tracker note that stale route tests and the quarantined integration harness belong to `TASK-052`.  
**Next**: Create the dedicated task file, mark the task in progress, and replace the stale tests with a current smoke baseline.

### 2026-04-13 - Smoke Baseline Rebuild
**Objective**: Replace the stale Flask route tests and quarantined legacy integration harness with a maintained current smoke baseline.  
**Context**: The existing route tests targeted removed endpoints and the legacy `test_end_to_end.py` file was still a module-level skip.  
**Decision**: Rebuild both files against the current Flask contract rather than trying to preserve the old route semantics.  
**Execution**:
- created `tests/unit/test_flask_routes.py` around the live route surface: `/`, `/getproviders`, `/getgooglekey`, `/getazurekey`, `/getengines`, `/api/config/status`, `/api/config/performance`, `/api/config/reset-session`, `/api/detection/progress`, `/abort`, `/api/detection/estimate`, and current `POST /getobjects` validation behavior
- replaced `tests/integration/test_end_to_end.py` with a two-part smoke suite:
  - current app boot + core route surface
  - bounded detection-readiness path that seeds the live engine catalog, loads the real local YOLO runtime, and then fails at a mocked imagery boundary
- aligned the smoke with import-mode test reality by explicitly calling `get_custom_models()` before asserting `/getengines`
- carved out a one-test exception to the global `prevent_model_loading` fixture by restoring the real `torch.load` inside the bounded readiness smoke only  
**Output**:
- stale route assumptions about `/draw_polygon`, `/get_status`, `POST /cancel_detection`, `/incompatible`, `/unauthorized`, and `GET /getobjects` were removed from the active baseline
- the smoke now validates the maintained live route surface and the post-`TASK-057` local YOLO path
- the bounded detection smoke reached real YOLO initialization and returned the expected mocked imagery failure (`502`) instead of dying in stale test scaffolding  
**Validation**:
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py -q -p no:cacheprovider` -> `7 passed`
- `.\.venv\Scripts\python.exe -m pytest tests\integration\test_end_to_end.py -q -p no:cacheprovider` -> `2 passed`
- `.\.venv\Scripts\python.exe -m pytest tests\backend\test_endpoint_contract.py -q -p no:cacheprovider` -> `2 passed`
- `.\.venv\Scripts\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` -> `160 tests collected`  
**Next**: Hand off the current smoke contract to `TASK-025` so Docker validation can reuse it instead of inventing a separate baseline.

---

## Validation Results

### Test Summary
**Test Date**: April 13, 2026  
**Test Environment**: Windows workspace, `.venv`, repo-root pytest invocation with `-p no:cacheprovider`  
**Test Status**: PASS

### Acceptance Criteria Validation
- [x] **Dedicated task file exists** - PASS - `.agent_work/tasks/active/TASK-052-current-integration-smoke-test-baseline.md`
- [x] **Current smoke baseline exists** - PASS - `tests/integration/test_end_to_end.py`
- [x] **Stale Flask route tests updated** - PASS - `tests/unit/test_flask_routes.py`
- [x] **Bounded detection-readiness path exists** - PASS - integration smoke reaches real YOLO initialization before mocked imagery failure
- [x] **Collection remains clean** - PASS - `160 tests collected`

### Notes

- The bounded detection-readiness smoke intentionally stops at a mocked imagery failure after real YOLO initialization so it can catch runtime-regression risk without becoming a provider-backed full detection suite.
- Focused validation still emits pre-existing deprecation warnings from `datetime.utcnow()` usage and vendored YOLO SciPy imports, but those warnings did not block the smoke baseline.
