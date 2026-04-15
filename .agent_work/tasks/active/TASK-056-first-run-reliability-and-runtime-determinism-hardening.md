# TASK-056: First-Run Reliability and Runtime Determinism Hardening

**Status**: COMPLETED  
**Priority**: CRITICAL  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Estimated Effort**: 12-20 hours  
**Created**: April 10, 2026  
**Last Updated**: April 13, 2026  
**Target Sprint**: Sprint 05

---

## Objective

Harden TowerScout's first-run and runtime contract so the application behaves deterministically on a clean machine before the Sprint 05 smoke baseline and Docker work proceed.

This task is the bounded runtime-safety gate between the already-completed dependency audit / pinned-ref hardening work and the smoke-baseline task. It is intended to fix or contain the current confirmed runtime blockers without widening into a full architecture rewrite.

---

## Related Issues

- `UT-002`: Silent partial tile download is treated as success
- `UT-003`: Unreachable duplicate detection code after `get_objects()` early return
- `UT-004`: Default install path yields CPU-only Torch; CUDA requires explicit install choice
- `UT-005`: NumPy 2 compatibility is coupled across Shapely and OpenCV
- `UT-006`: Pinned YOLO Hub autoupdate mutates Pillow/Requests and breaks first detection
- `UT-009`: Production request paths still use `print()` instead of structured logging
- `UT-010`: SSL verification is disabled in multiple runtime network paths
- `UT-013`: Runtime session identity is derived from `id(session)` instead of a stable session token
- `UT-017`: `seaborn` is unpinned in the runtime requirements without clear runtime use
- `UT-007`: Informational only; current `dev` lazy-loading behavior remains unchanged

---

## Context

`TASK-051` made the runtime dependency story more truthful and `TASK-055` reduced YOLO branch/cache drift, but the current first-run contract still has confirmed blockers and deployment-hostile behavior:

- detection can continue after partial imagery download failure
- first detection can mutate core packages in-process
- TLS verification is disabled in runtime code
- runtime identity still depends on `id(session)`
- the dependency baseline is still too loose for a reproducible pre-Docker smoke baseline

This task exists to correct those problems before `TASK-052` defines the Sprint 05 smoke contract. It should preserve current user-facing workflows where possible and explicitly keep current `dev` lazy-loading behavior unchanged.

---

## Scope

### Included

- Fix imagery download failure signaling so any tile failure stops the imagery phase and prevents misleading downstream model errors
- Remove the unreachable dead block below `get_objects()`
- Make the CPU baseline and optional CUDA install path explicit in the runtime contract
- Explicitly pin and validate a NumPy 1 baseline for the current stack
- Prevent first-run in-process package mutation in the current YOLO load path
- Align the runtime manifest with the pinned YOLO minimums needed for deterministic first detection
- Restore TLS verification as the default behavior and narrow any remaining bypass to explicit, documented exceptions only
- Replace `id(session)` with a stable session-persisted identifier
- Audit whether `seaborn` belongs in the runtime manifest and either remove it or pin it intentionally
- Replace raw `print()` logging in the touched runtime paths with structured logger usage
- Update active runtime/setup docs so the resulting contract is documented before `TASK-052`

### Explicitly Excluded

- Vendoring YOLO locally or removing `torch.hub` entirely
- Background-job architecture or worker/queue introduction
- Full session-store redesign
- Large `towerscout.py` decomposition
- Frontend build-system replacement
- Full NumPy 2 migration
- Changing the current `dev` lazy-loading behavior
- Docker implementation work

---

## Requirements (EARS Notation)

**R-056-001**: WHEN any tile download fails during a detection request, THE SYSTEM SHALL fail the imagery phase and SHALL NOT continue into model inference with assumed filenames for missing tiles.

**R-056-002**: WHEN the imagery phase fails, THE SYSTEM SHALL surface the failure as a download-phase error rather than a later image-loading or model error.

**R-056-003**: WHEN `get_objects()` delegates to `_run_detection_request()`, THE SYSTEM SHALL NOT retain unreachable legacy detection code below the return path.

**R-056-004**: WHEN the runtime/install contract is documented, THE SYSTEM SHALL distinguish the validated CPU baseline from the optional CUDA host install path and SHALL NOT imply that the generic requirements install provides CUDA automatically.

**R-056-005**: WHEN the current dependency stack is stabilized for Sprint 05, THE SYSTEM SHALL pin and document a validated NumPy 1 baseline unless a full coordinated NumPy 2 migration is explicitly approved.

**R-056-006**: WHEN TowerScout performs first YOLO initialization, THE SYSTEM SHALL NOT mutate core runtime packages in-process as part of normal detection startup.

**R-056-007**: WHEN runtime package requirements are insufficient for YOLO initialization, THE SYSTEM SHALL fail with a clear dependency/runtime error before continuing detection.

**R-056-008**: WHEN TowerScout performs runtime network calls, THE SYSTEM SHALL verify TLS certificates by default.

**R-056-009**: IF a TLS bypass remains necessary for a narrow development or recovery scenario, THEN THE SYSTEM SHALL scope it explicitly and document it as an exception rather than a blanket runtime default.

**R-056-010**: WHEN TowerScout identifies a user session for progress, cancellation, or performance tracking, THE SYSTEM SHALL use a stable session-persisted identifier rather than `id(session)`.

**R-056-011**: WHEN runtime logging is emitted from the touched first-run and detection paths, THE SYSTEM SHALL use structured logger calls instead of raw `print()` statements.

**R-056-012**: WHEN the runtime manifest is finalized for this task, THE SYSTEM SHALL either remove `seaborn` from the runtime manifest or pin it intentionally with documented justification.

**R-056-013**: WHEN this task completes, THE SYSTEM SHALL preserve the current `dev` lazy-loading behavior and SHALL NOT silently change that startup contract.

---

## Acceptance Criteria

- [x] Type C task artifact exists for `TASK-056`
- [x] Partial imagery download failure produces a download-phase error and does not enter model inference
- [x] Detection progress no longer reports all imagery tiles as downloaded when any tile failed
- [x] The unreachable block below `get_objects()` is removed or archived out of the active path
- [x] The active runtime/install docs describe CPU as the baseline and document the optional CUDA path explicitly
- [x] The Sprint 05 runtime baseline explicitly holds to a validated NumPy 1 contract
- [x] First detection on a clean environment does not perform in-process package upgrades for Pillow/Requests or equivalent core packages
- [x] Runtime dependency mismatch in the YOLO path fails clearly before inference starts
- [x] TLS verification is restored as the default runtime behavior
- [x] No active progress/cancel/performance identity path relies on `id(session)`
- [x] `seaborn` is either removed from `webapp/requirements.txt` or pinned intentionally with updated documentation
- [x] Active detection/runtime paths touched by this task use structured logging instead of raw `print()` statements
- [x] `pytest --collect-only tests -q` remains clean after the task
- [x] A clean-environment first-run proof is recorded against the resulting runtime contract

---

## Dependencies

- `TASK-051` completed dependency audit and runtime-doc cleanup
- `TASK-055` completed pinned-ref YOLO Torch Hub hardening
- current user-testing issue set under `.agent_work/user-testing/issues/`

---

## Implementation Plan

### Phase 1: Runtime Contract Lock
- Confirm the exact dependency deltas needed for deterministic first detection
- Decide the Sprint 05 CPU baseline and optional CUDA install-path wording
- Decide the explicit NumPy 1 pin and `seaborn` disposition

### Phase 2: Detection and First-Run Correctness
- Fix partial-download failure handling and progress reporting
- Remove dead code under `get_objects()`
- Replace `id(session)` with a stable session identifier
- Stop in-process package mutation during first YOLO initialization

### Phase 3: Security and Logging Hardening
- Restore TLS verification by default
- Narrow any remaining bypass paths
- Convert touched runtime paths from `print()` to structured logger calls

### Phase 4: Validation and Documentation
- Re-run clean-environment first-run proof
- Re-run smoke-level startup/import validation and pytest collection
- Update active docs so `TASK-052` inherits the corrected runtime contract

---

## Validation Plan

- Unit coverage for partial imagery download failure and no-inference-on-failure behavior
- Focused validation for the stable session identifier path
- Targeted validation for TLS-verified runtime requests and any retained exception path
- Clean-environment first-detection proof on the CPU baseline
- Documentation verification for CPU/CUDA, NumPy baseline, and runtime dependency expectations
- `pytest --collect-only tests -q`

---

## Non-Goals and Safety Boundaries

- Do not let this task expand into vendoring YOLO locally; that is `TASK-057`
- Do not let this task absorb Docker implementation or smoke-baseline creation
- Do not silently change the current `dev` lazy-loading behavior
- Do not start a full NumPy 2 migration here
- Do not treat large-file decomposition as required for this runtime gate

---

## Initial Planning Log

### TYPE C - TASK-056 PROPOSAL AND SCOPE LOCK - 2026-04-10
**Objective**: Create the Type C task definition for the pre-baseline runtime hardening gate.
**Context**: Post-investigation issue review and senior critique synthesis showed that the Sprint 05 sequence needed an explicit runtime-determinism gate before `TASK-052` and `TASK-025`.
**Decision**: Define `TASK-056` as the bounded first-run reliability and deployment-safety task, keeping YOLO vendoring, Docker work, and broader architecture redesign out of scope.
**Execution**: Drafted this task file with issue mapping, scope, EARS requirements, acceptance criteria, and validation boundaries.
**Output**: `TASK-056` now exists as an explicit Sprint 05 task proposal.
**Validation**: Planning artifact created and ready to be referenced by Sprint 05 planning docs.
**Next**: Sync `current-tasks.md`, `SPRINT-05-PLAN.md`, and the backlog to the revised sequence.

### IMPLEMENTATION PROGRESS - 2026-04-13
**Status**: In progress  
**Summary**: Completed the bounded runtime hardening pass and focused validation for imagery-failure handling, TLS defaults, stable session identity, deterministic YOLO dependency checks, and touched-path logging cleanup.

**Runtime changes completed**:
- `webapp/ts_maps.py` now fails the imagery phase on any tile-download failure and reports successful versus failed tile counts.
- `webapp/towerscout.py` now converts the active detection path to structured logging, uses a stable session-persisted run token, and blocks inference when imagery download or expected tile-file materialization fails.
- The unreachable legacy block below `get_objects()` is archived out of the active path.
- `webapp/ts_yolov5.py` now validates the pinned runtime dependency contract before Hub load and disables upstream YOLO autoinstall during model initialization.
- `webapp/ts_config.py` and `webapp/ts_geocoding.py` now verify TLS by default and keep the explicit env-scoped bypass (`TOWERSCOUT_ALLOW_INSECURE_TLS`) as the only exception path.
- `webapp/requirements.txt` now pins `numpy==1.26.4`, aligns `Pillow` and `Requests` with the validated YOLO minimums, and intentionally pins `seaborn` because the active pinned `torch.hub` YOLO path still imports it on first model load.
- Active runtime/setup guides now document CPU as the validated baseline, keep CUDA as an explicit optional install path, and record the NumPy 1 contract plus the TLS exception path.

**Validation completed**:
- `.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_cache_migration.py tests\\unit\\test_config.py tests\\unit\\test_runtime_hardening.py tests\\unit\\test_geocoding.py -q` -> `40 passed`
- `.venv\\Scripts\\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` -> `173 tests collected`
- same-device clean-environment CPU first-run proof passed and is recorded in `.agent_work/tasks/active/TASK-056/TASK-056-clean-cpu-first-run-proof.md`

**Closeout**:
- Task-056 acceptance criteria are satisfied and the corrected runtime contract is now recorded for follow-on Sprint 05 work.

### TYPE C - POST-PROOF REMEDIATION: RESTORE `seaborn` TO THE ACTIVE RUNTIME CONTRACT - 2026-04-13
**Objective**: Correct the clean-environment first-run regression exposed by the isolated CPU-baseline proof run.
**Context**: The first same-device clean-environment proof reached the first YOLO load and failed with `ModuleNotFoundError: No module named 'seaborn'` after the pinned Torch Hub repo imported `utils.plots.py`. That proved the active pinned `torch.hub` path still requires `seaborn`, so removing it from `webapp/requirements.txt` was premature under `TASK-056`.
**Decision**: Restore `seaborn` to `webapp/requirements.txt` as an intentional pinned runtime dependency and extend the YOLO dependency preflight to check the currently required Hub-path imports before `torch.hub.load(...)`.
**Execution**:
- Restored `seaborn==0.13.2` in `webapp/requirements.txt`.
- Extended `webapp/ts_yolov5.py` runtime dependency preflight to require `packaging`, `pandas`, `opencv-python`, `seaborn`, `tqdm`, and `ultralytics` in addition to the existing NumPy/Pillow/Requests checks.
- Added targeted unit coverage proving `_validate_runtime_dependencies()` now reports missing required Hub-path imports before model load.
- Re-ran focused validation and pytest collection after the fix.
**Output**:
- `webapp/requirements.txt`
- `webapp/ts_yolov5.py`
- `tests/unit/test_yolov5_cache_migration.py`
**Validation**:
- `.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_cache_migration.py tests\\unit\\test_config.py tests\\unit\\test_runtime_hardening.py tests\\unit\\test_geocoding.py -q` -> `40 passed`
- `.venv\\Scripts\\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` -> `173 tests collected`
**Next**: Recreate or refresh the isolated proof environment, then rerun the clean-environment CPU first-run proof against the corrected runtime manifest.

### TYPE C - CLEAN-ENVIRONMENT CPU FIRST-RUN PROOF AND TASK CLOSEOUT - 2026-04-13
**Objective**: Complete the remaining Task-056 acceptance item by recording a successful clean-environment CPU-baseline first-run proof on the corrected runtime manifest.
**Context**: The initial same-device proof exposed that the active pinned `torch.hub` YOLO path still required `seaborn`. After restoring `seaborn` and extending preflight validation, Task-056 still needed a fresh proof run to confirm the corrected runtime contract end-to-end.
**Decision**: Treat the clean-environment proof as the final Task-056 closeout gate and record the result directly in the analysis artifact plus task tracking.
**Execution**:
- Recreated the isolated same-device proof environment from scratch.
- Reinstalled `webapp/requirements.txt` into the proof venv and confirmed `seaborn==0.13.2` was present.
- Recreated an empty `TORCH_HOME` and reran the first detection flow from a private browser session.
- Reviewed the environment facts and terminal logs, then updated the proof artifact.
**Output**:
- `.agent_work/tasks/active/TASK-056/TASK-056-clean-cpu-first-run-proof.md`
- `.agent_work/tasks/active/TASK-056/evidence/TASK-056-clean-cpu-first-run-proof-env.txt`
- `.agent_work/tasks/active/TASK-056/evidence/TASK-056-clean-cpu-first-run-proof-terminal.txt`
**Validation**:
- Clean-environment startup succeeded on the CPU baseline.
- Estimate succeeded for a 4-tile area.
- First pinned-ref YOLO load succeeded on the empty-cache path.
- Full detection completed end-to-end on CPU without in-process package mutation or runtime autoupdate of `Pillow`, `Requests`, or similar core packages.
- The proof artifact is now recorded and Task-056 acceptance criteria are satisfied.
**Next**: Move to `TASK-057` so Sprint 05 can remove the remaining Torch Hub / GitHub dependency before `TASK-052` defines the smoke baseline.
