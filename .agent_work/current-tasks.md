# Current Tasks - Active Sprint

**Sprint Period**: April 7 - April 25, 2026 (Sprint 05 - 19 days)  
**Last Updated**: April 14, 2026  
**Focus**: Runtime determinism, local YOLO runtime ownership, smoke-baseline validation, pre-Docker cleanup, and Docker readiness  
**Status**: 🆕 **SPRINT 05 PLANNING** - Sprint 05 officially starts April 7, 2026

---

## 🎉 Sprint 04 Completion (March 19 - April 6, 2026)

**Sprint Status**: ✅ **COMPLETE - ALL CORE OBJECTIVES ACHIEVED**  
**Sprint Duration**: 19 days (extended from 16 days to absorb TASK-053)  
**Task Completion Rate**: 7 of 7 core tasks + 1 added closeout task (100%)  
**Bundle Evolution**: 412.8 KB → 446.1 KB (+33.3 KB)

**Sprint 04 Achievements**:
- ✅ Setup Wizard and Settings implemented (TASK-046)
- ✅ Large dataset performance investigation completed (ISSUE-003)
- ✅ Performance quick wins delivered (debug image gating, hydration cleanup)
- ✅ Console logging audit completed (TASK-048)
- ✅ Full-repo stale code audit completed (TASK-050)
- ✅ Legacy code cleanup with pytest gate repair (TASK-049)
- ✅ UI formatting and progress overlay (TASK-047)
- ✅ Detection workflow stabilization with browser validation (TASK-053)
- ✅ Browser smoke harness established
- ✅ Pytest collection gate: 154 collected / 0 collection errors

**Sprint 04 Retrospective**: See [SPRINT-04-RETROSPECTIVE.md](./context/status/SPRINT-04-RETROSPECTIVE.md)  
**Completed Tasks**: See [completed-tasks.md](./completed-tasks.md) for full Sprint 04 task details

---

## Pre-Sprint 05 Closeout Gate

These are current-branch closeout items for `feature-sprint-04-closeout`. Complete them before merging to `main` and creating the Sprint 05 branch so Sprint 05 delivery work starts from a cleaner baseline.

### **PRE-SPRINT-05-01: Runtime Path Normalization**
**Status**: COMPLETED  
**Type**: A (Closeout / Runtime Consistency)  
**Priority**: CRITICAL  
**Estimated Effort**: 6-10 hours  
**Branch Context**: `feature-sprint-04-closeout`  

**Objective**: Normalize TowerScout runtime path handling so logs, uploads, cache, sessions, temp files, and model-relative assets resolve consistently regardless of launch mode.

**Key Activities**:
- Choose and document a canonical runtime root for persistent and temp artifacts
- Replace mixed `cwd`-relative and app-relative path usage with centralized path definitions
- Normalize high-risk areas first: logs, uploads, map cache, filesystem sessions, and model paths
- Verify behavior remains consistent for local dev, pytest, and CI launch modes

**Validation**:
- App startup succeeds from the supported dev workflow
- Pytest collection and targeted smoke paths still pass from repo root
- No new duplicate runtime directories are created by mixed launch modes during validation

**Progress Update**:
- Added shared runtime path helpers in `webapp/ts_paths.py` anchored to `webapp/`
- Normalized `towerscout.py` runtime paths for map cache, uploads, model directories, Flask session storage, temp dataset export, and `send_from_directory` path resolution
- Updated supporting modules (`ts_en.py`, `ts_validation.py`, `ts_geocache.py`, `ts_logging.py`, `ts_performance.py`) to use shared app-anchored path helpers
- Updated `tests/test_performance_metrics.py` so it no longer changes `cwd` to `webapp/` just to find logs
- Verified repo-root import/app smoke, `cd webapp` import/app smoke, and targeted config/path tests

**Notes**:
- This is a closeout prerequisite, not Sprint 05 feature delivery work
- Final Docker volume decisions should be derived only after this task is complete
- Pre-push hygiene note: `.agent_work/tasks/completed/TASK-053/evidence/browser-runs/` remains local-only and ignored because its `summary.json` artifacts can contain live provider request URLs and should not be committed without sanitization
- Transitional compatibility note: `ts_config.get_recent_performance_stats()` still falls back to `cwd/logs/performance.log` if the normalized `webapp/logs/performance.log` is absent
- Remaining `cwd` references are intentional diagnostics (`towerscout.py`, `ts_logging.py`), the temporary log-reader compatibility fallback in `ts_config.py`, and non-active helper/archive surfaces outside the runtime write path
- Remaining stale validation blockers are tracked under `TASK-052`, not under this closeout task

**Validation Results**:
- Repo-root and `cd webapp` launch-mode smokes both resolved uploads, map cache, model directories, session storage, and temp session paths under `webapp/`
- Both smokes returned `GET /` status `200`
- `webapp/flask_session/` was updated by the smoke runs while repo-root `flask_session/` retained its older April 6 timestamp, which confirms the normalized session target was used
- Targeted `tests/unit/test_config.py` path/log-reader cases passed (`4 passed`)

### **PRE-SPRINT-05-02: Post-Normalization Cleanup + Validation**
**Status**: COMPLETED  
**Type**: A (Closeout / Cleanup)  
**Priority**: HIGH  
**Estimated Effort**: 2-4 hours  
**Branch Context**: `feature-sprint-04-closeout`  

**Objective**: Remove or reclassify only confirmed dead runtime artifacts after normalization and validate the repo is ready to merge into `main`.

**Key Activities**:
- Re-check root-level runtime directories and confirm which ones are now obsolete
- Clean up only artifacts that are proven unused after normalization
- Update docs and task tracking to reflect the normalized runtime path behavior
- Confirm deferred items stay deferred: `TowerScoutSite/`, `Model/`, `SyntheticData/`, and `hosting/`
- Confirm no API key values will be included or exposed during the commit process

**Validation**:
- Smoke checks confirm the normalized runtime paths are the only active write targets
- Documentation and task notes consistently describe current behavior, future target state, and deferred cleanup
- Branch is ready for merge review without ambiguous runtime-path cleanup risk

**Notes**:
- Do not treat this as blanket repo pruning
- Archive or defer anything that still has rollback, operational, or product-surface value

**Progress Update**:
- Re-checked repo-root runtime-looking directories after normalization and removed confirmed stale local leftovers: repo-root `cache/`, `uploads/`, `flask_session/`, random `pytest-cache-files-*`, and `webapp/tmp*` temp dirs
- Kept repo-root `logs/` only as a transitional compatibility surface because `ts_config.get_recent_performance_stats()` still falls back to `cwd/logs/performance.log` if `webapp/logs/performance.log` is absent
- Updated path-sensitive docs and task tracking to use the canonical `webapp/` runtime contract for Sprint 05 planning and Docker follow-through
- Tightened `.gitignore` for random pytest/temp artifacts and local browser-run captures so secret-bearing analysis artifacts stay out of commits

**Validation Results**:
- Repo-root and `cd webapp` launch-mode smokes both returned `GET /` status `200`
- Deleted repo-root `cache/`, `uploads/`, and `flask_session/` stayed absent after both smokes, which confirms they are no longer active write targets
- `webapp/flask_session/` and `webapp/logs/` advanced during the smokes while repo-root `logs/` retained its pre-smoke April 7 timestamp, which confirms the canonical `webapp/` write targets were used
- `pytest --collect-only tests -q` collected `159` tests with no collection errors
- `pytest tests/unit/test_config.py -q` still reports the two known stale Google-validation test failures already scoped under `TASK-052`; they were not folded into this cleanup task

**Closeout Decision**:
- Deferred repo surfaces remain deferred: `TowerScoutSite/`, `Model/`, `SyntheticData/`, and `hosting/`
- Docker planning should now use the canonical `webapp/config/`, `webapp/flask_session/`, `webapp/logs/`, `webapp/temp/`, `webapp/uploads/`, and `webapp/cache/` mount set
- Repo-root `logs/` is transitional/local-only and should not be treated as a Docker persistence target

---

## 🎯 SPRINT 05 GOALS

**Sprint Period**: April 7 - April 25, 2026 (19 days)  
**Planning Completed**: April 6, 2026  
**Sprint Focus**: Runtime hardening, reproducible inference, Docker readiness, and bounded local-launch follow-through  
**Target Capacity**: 70-80 hours (with Docker now contingent on additional runtime hardening gates)  
**Expected Bundle Growth**: +10-20 KB (infrastructure-heavy sprint unless TASK-054 expands into frontend warm-start UX)  

### Sprint 05 Objectives

**Primary Goal**: Deliver a reliable and reproducible runtime baseline, then containerize that corrected baseline rather than containerizing known first-run instability.

**Secondary Goals**:
1. Keep `TASK-051` and `TASK-055` as the completed foundation for Sprint 05 runtime work
2. Complete `TASK-056` first-run reliability and runtime determinism hardening
3. Complete `TASK-057` local YOLO runtime ownership and Torch Hub independence
4. Establish the current integration smoke-test baseline on that corrected runtime (`TASK-052`)
5. Deliver Docker containerization (`TASK-025`) only after the corrected baseline exists
6. Keep `TASK-054` as a post-Docker stretch goal and defer `TASK-029` / `TASK-026` unless meaningful Sprint 05 capacity remains

**Key Principle**: Keep `TASK-025` focused on container build/run behavior. Use `TASK-056`, `TASK-057`, and `TASK-052` as explicit prerequisites so Docker acceptance criteria stay clear and runtime-risk changes remain isolated. Treat launcher/browser UX as follow-on work under `TASK-054` rather than silently expanding Docker scope.

---

## 📋 SPRINT 05 ACTIVE TASKS

### **TASK-051: Runtime Dependency Verification and Split** ✅
**Status**: COMPLETED  
**Type**: C (Architecture / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 6-10 hours  
**Target Sprint**: Sprint 05  
**Task File**: `.agent_work/tasks/active/TASK-051-runtime-dependency-audit-and-decision-gate.md`  

**Objective**: Make the runtime manifest and setup docs truthful enough for Docker preparation without changing current runtime behavior.

**Key Activities**:
- Add the verified explicit runtime gaps `psutil` and `tqdm` to `webapp/requirements.txt`
- Update active runtime/setup guides to remove stale `pkg_resources` guidance
- Document first-run Torch Hub / GitHub behavior and CUDA install-time requirements
- Preserve current user workflow, appearance, and runtime behavior

**Validation**:
- Clean-environment install test
- App startup verification
- CPU-only verification path
- CUDA-available verification path where hardware is available

**Dependencies**:
- TASK-049 stale-code audit findings ✅ COMPLETED

**Notes**: Recommended as pre-containerization gate. Do not fold into TASK-025 - different risks, acceptance criteria, and rollback needs.

**Completion Summary**:
- Phase 1 audit artifacts and decision memo are complete
- Option 2 Phase 2 follow-through is complete
- `webapp/requirements.txt` now explicitly includes `psutil` and `tqdm`
- Active runtime/setup guides now remove the stale `pkg_resources` / `setuptools<82` workaround and document first-run Torch Hub / GitHub plus CUDA install-time requirements
- Post-close correction recorded: stale cached Torch Hub snapshots can still import `pkg_resources`, and a short-term cache-migration recovery path now exists in `webapp/ts_yolov5.py`
- Validation rerun completed:
  - startup/import smoke passed
  - `pytest --collect-only tests -q` collected `159` tests
  - clean-manifest install proof passed
  - empty-cache YOLO proof reproduced offline failure and networked success
- No Torch Hub redesign or Docker work was folded into this task
- Recommended handoff: complete `TASK-055`, then move to `TASK-052`

**User Value**: Ensures Docker container has minimal, verified runtime dependencies

---

### **TASK-055: YOLO Torch Hub Pinned-Ref Hardening** ✅
**Status**: COMPLETED  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 6-10 hours  
**Target Sprint**: Sprint 05  
**Task File**: `.agent_work/tasks/active/TASK-055-yolo-torch-hub-pinned-ref-hardening.md`  

**Objective**: Replace the mutable YOLO `torch.hub` default-branch load with a tested pinned ref and ref-specific cache handling so TowerScout no longer depends on whatever `ultralytics_yolov5_master` happens to be in a user's Hub cache.

**Key Activities**:
- Validate published YOLOv5 release refs against TowerScout's current weights and reject any ref that reintroduces the stale `pkg_resources` runtime problem
- Pin TowerScout to a tested YOLOv5 commit SHA instead of the moving default branch
- Refresh only the pinned-ref cache when a cached pinned repo becomes invalid, while keeping a narrow legacy cleanup path for `pkg_resources`-era `master` caches
- Make first-run and refresh failures mention the pinned ref and the GitHub/network dependency clearly
- Update runtime docs and task tracking so the hardened Hub contract is documented before `TASK-052`

**Validation**:
- Targeted unit coverage for pinned-ref load, pinned-cache refresh, legacy-cache cleanup, and first-run offline failure messaging
- Live empty-cache Torch Hub validation against the selected pinned commit
- Offline valid-cache proof using the pinned cache
- Startup/import smoke and pytest collection gate rerun after the hardening change

**Dependencies**:
- ✅ TASK-051 completed dependency audit and documented the stale-cache limitation

**Completion Summary**:
- Published release-tag validation was rejected as the primary fix path because YOLOv5 `v7.0` and earlier release tags still imported `pkg_resources`
- TowerScout now pins YOLOv5 to commit `1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`, which was live-validated against `webapp/model_params/yolov5/newest.pt`
- `webapp/ts_yolov5.py` now loads the pinned ref with `trust_repo=True`, refreshes only the pinned cache on cache-corruption/import failures, and preserves a narrow legacy cleanup path for stale `master` caches
- `webapp/requirements.txt` now explicitly includes `packaging`, `pandas`, and a pinned `ultralytics==8.3.249` version to match the hardened runtime path
- Active setup/runtime guides now describe the pinned Hub ref behavior and first-run GitHub dependency accurately
- `TASK-051` remains closed; this task superseded the short-term mitigation without reopening the dependency-audit task

**User Value**: Removes YOLO default-branch cache drift and gives Docker/Sprint 05 validation work a more deterministic runtime baseline

---

### **TASK-056: First-Run Reliability and Runtime Determinism Hardening** ✅
**Status**: COMPLETED  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 12-20 hours  
**Target Sprint**: Sprint 05  
**Task File**: `.agent_work/tasks/active/TASK-056-first-run-reliability-and-runtime-determinism-hardening.md`  

**Objective**: Correct the confirmed first-run blockers and deployment-hostile runtime behavior before the Sprint 05 smoke baseline and Docker work proceed.

**Key Activities**:
- Fail the imagery phase on any tile-download failure and prevent inference from starting on partial downloads (`UT-002`)
- Remove the unreachable legacy block below `get_objects()` (`UT-003`)
- Lock the Sprint 05 runtime to a validated CPU baseline plus an explicitly documented optional CUDA path (`UT-004`)
- Explicitly contain the current stack on a validated NumPy 1 baseline and document the deferred NumPy 2 migration (`UT-005`)
- Stop first-run in-process package mutation and align the YOLO runtime contract with the actual minimum dependency set (`UT-006`)
- Restore TLS verification as the default runtime behavior and remove blanket bypasses (`UT-010`)
- Replace `id(session)` with a stable session identifier (`UT-013`)
- Remove or intentionally pin `seaborn` and replace raw `print()` usage in the touched runtime paths with structured logging (`UT-017`, scoped `UT-009`)

**Validation**:
- Partial-download failure path proves detection stops during imagery phase
- Clean-environment first-run proof succeeds on the CPU baseline without runtime package mutation
- `pytest --collect-only tests -q` remains clean
- Updated runtime/setup docs reflect CPU/CUDA, NumPy, TLS, and first-run expectations

**Dependencies**:
- ✅ TASK-051 runtime dependency audit and decision gate
- ✅ TASK-055 YOLO Torch Hub pinned-ref hardening

**Notes**:
- Preserve the current `dev` lazy-loading behavior; this task does not change that startup contract.
- Keep this task bounded. Do not absorb vendoring YOLO locally, Docker work, or background-job architecture here.
- Progress update (April 13): imagery failures now stop before inference, active session identity is stable, YOLO dependency checks/autoinstall hardening are in place, TLS now verifies by default, and the touched runtime paths were moved to structured logging.
- Validation update (April 13): focused Task-056 coverage passed (`40 passed`) and pytest collection remained clean with `.venv\\Scripts\\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` (`173 tests collected`).
- Proof follow-up (April 13): the first isolated CPU-baseline proof failed because the active pinned `torch.hub` YOLO path still imported `seaborn`; `seaborn==0.13.2` was restored to the runtime manifest and the YOLO dependency preflight now checks the current Hub-path imports before model load.
- Closeout update (April 13): the rerun same-device clean-environment CPU proof passed and is recorded in `.agent_work/tasks/active/TASK-056/TASK-056-clean-cpu-first-run-proof.md`.
- Senior review follow-up (April 14): the original `UT-010`, `UT-013`, and `UT-017` concerns are resolved on `a2160dc`, but `UT-003` and the remaining active `UT-009` logging cleanup were only partially addressed and are routed to `TASK-062` rather than reopening this completed task.

**User Value**: Makes the current app install and first detection materially more reliable before the team locks the smoke baseline or starts containerization.

---

### **TASK-057: Local YOLO Runtime Ownership and Torch Hub Independence** ✅
**Status**: COMPLETED  
**Type**: C (Runtime Architecture / Deployment Readiness)  
**Priority**: CRITICAL  
**Estimated Effort**: 12-20 hours  
**Target Sprint**: Sprint 05  
**Task File**: `.agent_work/tasks/active/TASK-057-local-yolo-runtime-ownership-and-offline-readiness.md`  

**Objective**: Remove the remaining Torch Hub / GitHub dependency from the active YOLO load path so the Sprint 05 smoke baseline and Docker work are built on a TowerScout-owned local inference contract.

**Key Activities**:
- Vendor the validated YOLO source snapshot locally and replace the active `torch.hub` load path (`UT-014`)
- Revalidate the current YOLO weights against the local loader and confirm the interface TowerScout expects remains intact
- Reconfirm the CPU baseline and optional CUDA compatibility on the new local loader path (`UT-004`)
- Eliminate first-run Torch Hub / GitHub bootstrap dependence for model initialization and revalidate the earlier first-run mutation/failure surfaces on the local loader contract (`UT-006`, `UT-001`)
- Update runtime/setup docs so `TASK-052` and `TASK-025` inherit the local-loader contract rather than the Hub-based one

**Validation**:
- Clean-runtime first-run proof shows YOLO initialization no longer depends on Torch Hub cache state or GitHub / Torch Hub runtime fetches
- `webapp/model_params/yolov5/newest.pt` loads successfully through the local loader
- CPU baseline validation passes and CUDA path expectations are documented or validated where hardware is available
- `pytest --collect-only tests -q` remains clean

**Dependencies**:
- ✅ TASK-056 runtime hardening complete

**Notes**:
- This is the structural follow-on to the immediate runtime hardening task, not a broad architecture rewrite.
- This is not a full-app offline-readiness task; provider-backed imagery and geocoding remain network-dependent.
- Do not expand this task into ONNX/TensorRT migration, Docker work, or queue-based detection redesign.
- Senior review follow-up (April 14): the original `UT-014` concern is resolved on `a2160dc`, but the vendored-tree scope and temporary `sys.path` loader contract are now tracked separately as `UT-018` and `UT-019` before Docker work begins.

**Completion Summary**:
- Vendored the validated YOLOv5 runtime snapshot locally under `webapp/vendor/yolov5_local/` with provenance documented from `ultralytics/yolov5@1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c`
- Added `webapp/ts_yolov5_local.py` and switched `webapp/ts_yolov5.py` from `torch.hub` to a TowerScout-owned local loader path
- Patched the vendored runtime to fail fast on missing `ultralytics` instead of attempting in-process package mutation
- Updated active setup/runtime guides so they no longer describe first-run GitHub dependence as part of normal YOLO initialization
- Validation passed:
  - `.venv\\Scripts\\python.exe -m pytest tests\\unit\\test_yolov5_local_loader.py -q -p no:cacheprovider` -> `5 passed`
  - `.venv\\Scripts\\python.exe -m pytest --collect-only tests -q -p no:cacheprovider` -> `170 tests collected`
  - direct `YOLOv5_Detector` load against `webapp/model_params/yolov5/newest.pt` succeeded
  - direct `YOLOv5_Detector` load also succeeded with `torch.hub.load` and `torch.hub.download_url_to_file` patched to fail, which proved the active loader no longer depends on Torch Hub
- Clean first-run proof recorded in `.agent_work/tasks/active/TASK-057/TASK-057-clean-local-yolo-first-run-proof.md` with companion env and terminal logs
- Broader app and host-side smoke recorded in `.agent_work/tasks/active/TASK-057/TASK-057-broader-app-and-host-smoke.md` with companion live-server stdout/stderr and probe logs

**User Value**: Removes the last major runtime nondeterminism before Docker by ensuring TowerScout owns the inference code it depends on.

---

### **TASK-052: Current Integration Smoke Test Baseline** ✅
**Status**: COMPLETED  
**Type**: A (Quality / Validation)  
**Priority**: CRITICAL  
**Estimated Effort**: 4-8 hours  
**Target Sprint**: Sprint 05  
**Task File**: `.agent_work/tasks/active/TASK-052-current-integration-smoke-test-baseline.md`  

**Objective**: Replace the quarantined legacy end-to-end harness with a current smoke test that validates the live Flask route surface and core app boot flow on top of the corrected Sprint 05 runtime contract.

**Key Activities**:
- Replace skipped legacy `tests/integration/test_end_to_end.py` coverage
- Establish the smoke first on the host/non-containerized app so it becomes the baseline before Docker work begins
- Validate application boot with current configuration/setup flow
- Exercise core live routes and confirm expected response behavior
- Add one bounded detection-readiness path that is strong enough to catch model-load/runtime regressions without turning `TASK-052` into a full browser E2E suite
- Make the smoke reusable by `TASK-025` so Docker validation runs the same contract against the containerized app
- Provide stable regression target for containerization work
- Keep test lightweight for regular Sprint 05 runs
- Triage or replace stale tests and mocks discovered during pre-sprint closeout so validation reflects the live route surface

**Success Criteria**:
- `pytest --collect-only tests -q` remains clean
- Current smoke test exists for host-side app boot + core route availability
- Smoke covers one bounded detection-readiness path or explicitly documents why a narrower substitute was required
- Smoke prerequisites and intentional skips are documented for provider keys, model files, and the post-`TASK-057` local YOLO runtime contract
- Containerization work has concrete validation target beyond import/collection
- `TASK-025` can reuse the same smoke contract against Docker instead of defining a different validation baseline
- Stale validation surfaces are either updated to current behavior or explicitly retired from the active baseline

**Dependencies**:
- TASK-056 first-run reliability and runtime determinism hardening ✅ COMPLETED
- TASK-057 local YOLO runtime ownership and Torch Hub independence ✅ COMPLETED
- TASK-046 setup wizard/settings implementation ✅ COMPLETED
- TASK-049 validation-gate repair ✅ COMPLETED
- TASK-055 YOLO Torch Hub pinned-ref hardening ✅ COMPLETED

**Notes**:
- Recommended before TASK-025 so Docker work validates against current, supported app surface.
- This smoke should validate the corrected post-`TASK-056` runtime contract and the local post-`TASK-057` YOLO loader path, not the earlier Hub-based runtime.
- This task should define the validation contract once, on the host app first, and let `TASK-025` reuse it for container validation.
- Keep the smoke broad enough to catch setup/config/model-loading regressions, but bounded enough that it remains practical for repeated Sprint 05 runs.
- Current stale-test findings from PRE-SPRINT-05-01 include outdated Google API validation mocks in `tests/unit/test_config.py` and `GET /getobjects` assumptions in `tests/unit/test_flask_routes.py`.
- Unless one of those blocks additional closeout work earlier, handle them under TASK-052 rather than folding them into runtime-path normalization.
- Completion update (April 13): dedicated task file created, `tests/unit/test_flask_routes.py` rebuilt against the live route surface, and `tests/integration/test_end_to_end.py` now provides the maintained current smoke baseline with a bounded real-YOLO readiness path.

**Validation Results**:
- `pytest tests/unit/test_flask_routes.py -q -p no:cacheprovider` -> `7 passed`
- `pytest tests/integration/test_end_to_end.py -q -p no:cacheprovider` -> `2 passed`
- `pytest tests/backend/test_endpoint_contract.py -q -p no:cacheprovider` -> `2 passed`
- `pytest --collect-only tests -q -p no:cacheprovider` -> `160 tests collected`

**User Value**: Provides regression protection during containerization and proves the intended post-hardening runtime contract before Docker begins.

---

### **TASK-062: Pre-Docker Runtime Cleanup And YOLO Loader Hardening** ✅
**Status**: COMPLETED  
**Type**: C (Runtime Hardening / Deployment Readiness)  
**Priority**: HIGH  
**Estimated Effort**: 6-10 hours  
**Target Sprint**: Sprint 05  
**Task File**: `.agent_work/tasks/active/TASK-062-pre-docker-runtime-cleanup-and-yolo-loader-hardening.md`

**Objective**: Address the April 13 senior-review follow-up items that are narrower than `TASK-058`, `TASK-059`, and `TASK-060`, but should land before `TASK-025` fixes the Docker baseline around the current runtime contract.

**Key Activities**:
- Delete the archived legacy `get_objects()` block from `webapp/towerscout.py` (`UT-003`)
- Replace the remaining active `print()` usage in export, upload, dataset restore, startup, and manual-addition paths with structured logging (`UT-009`)
- Trim `webapp/vendor/yolov5_local/` to an inference-only runtime footprint and remove obvious non-runtime artifacts (`UT-018`)
- Replace the temporary `sys.path` YOLO loader contract with an explicit long-lived import contract (`UT-019`)
- If the JS backup file is touched anyway, remove or relocate `webapp/js/towerscout.original.js` from the served tree without turning this task into full build-system modernization (`UT-012` quick cleanup only)

**Validation**:
- `pytest tests/unit/test_yolov5_local_loader.py -q -p no:cacheprovider`
- Reuse the `TASK-052` smoke contract rather than reopening `TASK-052`
- Focused route and loader smoke remain green after the cleanup

**Dependencies**:
- ✅ TASK-057 local YOLO runtime ownership and Torch Hub independence
- ✅ TASK-052 current integration smoke-test baseline

**Notes**:
- Keep background jobs, filesystem-session redesign, and broad backend decomposition out of this task; those belong to `TASK-058` and `TASK-059`.
- Do not reopen `TASK-052`. Use its smoke suite as regression coverage for this task and later for `TASK-025`.
- If Sprint 05 tightens, prioritize `UT-018`, `UT-019`, and `UT-003` before the broader remaining `UT-009` print cleanup.

**User Value**: Reduces pre-Docker risk without muddying `TASK-025` or reopening broader architecture work.

---

### **TASK-025: Docker Containerization** 🔴
**Status**: NOT_STARTED  
**Type**: A (Infrastructure)  
**Priority**: HIGH  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 05  

**Objective**: Create Docker configuration for one-command local deployment on top of the corrected Sprint 05 runtime and smoke baseline.

**Requirements**:
- Multi-stage Dockerfile with model weights
- Docker Compose configuration
- Environment variable management
- Platform-specific optimization (AMD64/ARM64)
- Volume mount strategy for persistent state

**Current Runtime Persistence Surfaces**:
Runtime-path normalization is complete. Docker work should treat the following as the active persistence contract:

1. **`webapp/config/`**
2. **`webapp/flask_session/`**
3. **`webapp/logs/`**
4. **`webapp/temp/`**
5. **`webapp/uploads/`**
6. **`webapp/cache/`**

**Transitional Compatibility Note**:
`ts_config.get_recent_performance_stats()` still falls back to `cwd/logs/performance.log` if `webapp/logs/performance.log` is absent. Treat repo-root `logs/` as a temporary local compatibility surface, not a Docker mount target.

**Environment Variables Required**:
- `GOOGLE_API_KEY`
- `AZURE_MAPS_SUBSCRIPTION_KEY`
- `DEFAULT_MAP_PROVIDER`
- `FLASK_SECRET_KEY` (must be stable across restarts)

**Dependencies**:
- ✅ TASK-056 - first-run reliability and runtime determinism hardening
- ✅ TASK-057 - local YOLO runtime ownership and Torch Hub independence
- ✅ TASK-046 (completed) - setup wizard/settings volume-mount behavior
- 🟡 TASK-051 - runtime dependency verification and split
- ✅ TASK-055 - YOLO Torch Hub pinned-ref hardening
- 🟡 TASK-052 - current integration smoke-test baseline
- ✅ TASK-062 - pre-Docker runtime cleanup and loader hardening

**Notes**:
- Keep focused on container build/run behavior
- Do NOT absorb runtime hardening, YOLO ownership redesign, or smoke-test replacement into this task
- Reuse the `TASK-052` smoke contract against the containerized app rather than inventing a separate Docker-only validation path
- Current app uses filesystem-backed Flask sessions and writes to `webapp/config/.env`
- Final Docker volume decisions should use the normalized `webapp/` runtime contract, not historical folder duplication
- Docker delivery must provide writable session storage, stable `FLASK_SECRET_KEY`, and persistent writable mount for `webapp/config/`
- TASK-025 Phase 1 must explicitly choose and document the model-weight strategy (image layer vs runtime download vs host volume)
- Treat the current filesystem-session and temp-path contract as an explicit containment requirement for the first Docker milestone, not as a solved architecture problem
- Without these, first-launch setup may fail or saved configuration lost on container replacement

**User Value**: Enables one-command deployment for non-technical users

---

### **TASK-054: Local Launch UX** 🟡
**Status**: NOT_STARTED  
**Type**: B (Deployment UX / Local Launch Flow)  
**Priority**: MEDIUM  
**Estimated Effort**: 1-2 days (8-12 hours)  
**Target Sprint**: Sprint 05 (post-Docker stretch goal)  

**Objective**: Deliver a user-friendly local launch flow for Docker deployments so users can start TowerScout with a click, have the browser open automatically, and receive a clear startup experience while the application becomes ready.

**Requirements**:
- Host-side launcher flow for supported local deployment targets (`start.bat` first, cross-platform launcher follow-up if capacity allows)
- Browser auto-open only after the app shell is reachable on the configured localhost port
- Clear separation between "container is up" and "application is ready for user interaction"
- User-facing startup experience that works with the existing Setup Wizard flow instead of bypassing it
- Troubleshooting path for common launch failures (Docker not running, port conflict, startup timeout)

**Proposed Delivery Phases**:
1. **Phase 1 - Launcher MVP**
   - Add launcher script(s) for local Docker startup
   - Wait for reachable app shell before opening the browser
   - Add companion stop/logs guidance or scripts so users are not forced into raw Docker CLI usage for routine support
2. **Phase 2 - Readiness + Browser Orchestration**
   - Add or formalize a lightweight startup/readiness endpoint for launcher polling
   - Ensure browser launch targets the correct localhost port and only happens once per launch attempt
   - Document expected behavior for first launch, repeat launch, and failure modes
3. **Phase 3 - Deferred Warm-Initialization UX**
   - Evaluate whether model/ZIP warm initialization can happen after the app shell is served
   - If feasible within Sprint 05 capacity, expose startup status to the frontend so setup/loading UI can distinguish "page is available" from "runtime is fully warm"
   - Defer this phase to Sprint 06 if Docker baseline or launcher MVP consumes available capacity

**Dependencies**:
- 🟡 TASK-052 - current integration smoke-test baseline
- 🔴 TASK-025 - Docker containerization baseline complete enough to support a stable local launcher target

**Notes**:
- Do NOT absorb this task into TASK-025. The launcher/browser UX is a separate user-experience layer with different failure modes and rollback concerns.
- Container code should not be responsible for opening the host browser; browser launch should be driven by the host-side launcher.
- If Sprint 05 tightens, ship Phase 1 first and defer background warm-initialization redesign.

**User Value**: Reduces or eliminates command-line interaction for local users while keeping Setup Wizard and startup behavior understandable.

---

### **TASK-029: Multi-Provider Fallback** 🟡
**Status**: NOT_STARTED  
**Type**: B (Reliability)  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 days (16-24 hours)  
**Target Sprint**: Sprint 05 (stretch goal)  

**Objective**: Implement automatic fallback between map providers for reliability

**Requirements**:
- Automatic provider switching on API failures
- Quality comparison and provider selection logic
- Rate limit handling and quota management
- Transparent failover for users

**Dependencies**:
- Provider abstraction layer ✅ COMPLETED

**Notes**: May be deferred to Sprint 06 if Docker work requires more time

**User Value**: Improved reliability when one provider experiences issues

---

### **Optional Quick Wins from Sprint 04** 🟢
**Status**: NOT_STARTED  
**Priority**: LOW-MEDIUM  
**Total Estimated Effort**: 4-6 hours

**Browser Refresh Warning Fix** (2-3 hours)
- Debug `window.onbeforeunload` inconsistencies
- Cross-browser compatibility testing
- Implement reliable solution

**Error Handling Pattern Standardization** (2-3 hours)
- Remove deprecated `fatalError()` references
- Standardize on `TowerScoutErrorHandler`
- Update documentation

**Notes**: Include only if Sprint 05 capacity allows after TASK-056, TASK-057, TASK-052, and TASK-025

---

## 📊 Sprint 05 Execution Plan

**Sprint Duration**: 19 days (April 7 - April 25, 2026)  
**Target Capacity**: 70-80 hours  
**Sprint Pace**: Medium-to-high complexity work with explicit runtime hardening gates before Docker

### Week 1: April 7-13 (Runtime Contract Correction)
**Focus**: Finish the dependency and YOLO pinning foundation, then complete the first-run hardening gate  
**Estimated Effort**: 26-34 hours

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 7-9 | TASK-051: Runtime dependency verification and split | 8-12h |
| Apr 9 | TASK-055: YOLO pinned-ref hardening | 6-10h |
| Apr 10-13 | TASK-056: First-run reliability and runtime determinism hardening | 12-20h |

**Week 1 Note**:
- `PRE-SPRINT-05-02` closeout validation is complete; continue using the canonical `webapp/` runtime contract rather than the old mixed-path folder duplication.

### Week 2: April 14-20 (Local YOLO Runtime Ownership + Host Baseline)
**Focus**: Remove the remaining Hub/GitHub runtime dependency and lock the host smoke baseline  
**Estimated Effort**: 18-28 hours

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 14-17 | TASK-057: Local YOLO runtime ownership and Torch Hub independence | 12-20h |
| Apr 18-20 | TASK-052: Current integration smoke-test baseline | 6-10h |

**Week 2 Replan Update (April 14)**:
- Insert `TASK-062` between `TASK-052` and `TASK-025` so the senior-review cleanup lands on the host baseline before Docker work starts.

### Week 3: April 21-25 (Docker Baseline + Stretch Decision)
**Focus**: Containerize the corrected baseline, then decide whether any launch-UX stretch capacity remains  
**Estimated Effort**: 18-28 hours

| Date | Tasks | Hours |
|------|-------|-------|
| Apr 21 | TASK-062: Pre-Docker runtime cleanup and loader hardening | 6-10h |
| Apr 22-23 | TASK-025 Phase 1-2: Docker strategy, Dockerfile, and compose config | 10-16h |
| Apr 23-24 | TASK-025 Phase 3-4: volume mounts, validation, and documentation | 8-12h |
| Apr 24-25 | Stretch decision: TASK-054 Phase 1 only if Docker baseline lands cleanly | 0-8h |
| Apr 25 | Sprint 05 Retrospective | 2-4h |

**Total Sprint Effort**: 64-94 hours (planning target remains 70-80h)

---

## 🎯 Sprint 05 Definition of Done

### Must-Have (Primary Goals)
- [x] TASK-051 complete: Runtime dependencies verified and split documented
- [x] TASK-055 complete: YOLO Torch Hub pinned-ref hardening landed
- [x] TASK-056 complete: First-run blockers and deployment-hostile runtime defaults corrected
- [x] TASK-057 complete: Active YOLO load path no longer depends on Torch Hub / GitHub at runtime
- [x] TASK-052 complete: Current integration smoke test in place on the corrected runtime contract
- [x] TASK-062 complete: Senior-review cleanup landed on the host baseline before Docker starts
- [ ] TASK-025 Phase 1-3 complete: Docker container builds and runs on the corrected baseline
- [ ] Setup Wizard functional in Docker environment
- [ ] Settings save/load works with volume mounts
- [ ] Detection workflow validated in container
- [ ] All volume mounts tested and documented
- [ ] Docker Compose configuration validated
- [ ] Zero regressions from Sprint 04 functionality

### Should-Have (Secondary Goals)
- [ ] TASK-025 Phase 4 complete: Full Docker documentation
- [ ] Multi-platform support (AMD64 at minimum)
- [ ] TASK-054 Phase 1 complete: launcher MVP for local Docker startup
- [ ] Browser Refresh Warning Fix (if capacity allows)
- [ ] Error Handling Standardization (if capacity allows)

### Nice-to-Have (Stretch Goals)
- [ ] TASK-054 Phase 2 complete or cleanly deferred with documented readiness approach
- [ ] ARM64 platform support
- [ ] Docker Hub image publishing
- [ ] Performance optimization in containerized environment
- [ ] TASK-029 investigation started only if all runtime and Docker gates land early

### Sprint Health Metrics
- TASK-051, TASK-055, TASK-056, TASK-057, TASK-052, and TASK-062 complete before TASK-025 starts
- Clean-environment first detection succeeds without in-process package mutation
- YOLO initialization no longer depends on first-run GitHub access
- Docker container starts successfully on first attempt
- All TASK-046 features work in containerized environment
- Documentation includes troubleshooting guide
- All automated tests passing in container
- Container image size reasonable (<2GB with models)

---

## 📅 Sprint 05 Planning Notes

**Key Decisions**:
1. **Sequencing is critical**: `TASK-051` and `TASK-055` are already complete, `TASK-056`, `TASK-057`, and `TASK-052` are complete, and the new `TASK-062` cleanup should land before `TASK-025`
2. **`TASK-025` scope discipline**: Do NOT absorb runtime hardening, YOLO ownership redesign, or smoke-baseline work into the Docker task
3. **`TASK-054` stays separate**: Launcher/browser UX work starts only after the Docker baseline is stable enough to target
4. **Current `dev` lazy-loading behavior remains intentional**: do not expand Sprint 05 scope to "fix" that
5. **Volume mount testing remains mandatory**: explicitly test Setup Wizard save/load in Docker against the current filesystem-session contract
6. **Model-weight strategy is a Phase 1 Docker decision**: do not defer layer/download/volume treatment until late Docker validation
7. **Fallback plan**: If the added runtime gates consume Sprint 05 capacity, defer `TASK-054` and `TASK-029` rather than compressing `TASK-025`

**Risk Mitigation**:
- `TASK-056` corrects first-run failures before the smoke baseline is defined
- `TASK-057` prevents Docker from being built on top of a runtime contract that still depends on Torch Hub / GitHub
- `TASK-052` provides regression protection during Docker work
- Keep `TASK-025` phases separate for easier rollback if needed
- Keep `TASK-054` phased so launcher MVP can ship without forcing startup-pipeline redesign into the same sprint
- Use a conservative planning pace around 3.5-4.0 hrs/day instead of Sprint 03 peak velocity
- Document all Docker-specific configuration decisions

**Success Indicators**:
- A new user can install and run a first detection without in-process package upgrades
- YOLO initialization works on the validated host baseline without first-run GitHub dependence
- A new user can run `docker compose up` and complete Setup Wizard
- Configuration persists across container restarts
- Detection workflow works end-to-end in container
- A user can launch the local Docker deployment with minimal or no manual CLI interaction once `TASK-054` lands
- No manual `.env` editing required

---

## 🔗 Related Documentation

- [Sprint 05 Planning](./context/status/SPRINT-05-PLAN.md) - Detailed sprint plan synchronized with this tracker
- [Sprint 04 Retrospective](./context/status/SPRINT-04-RETROSPECTIVE.md)
- [Task Backlog](./task-backlog.md)
- [Completed Tasks](./completed-tasks.md)
- [Docker Requirements Analysis](./context/analysis/REMOVAL-CANDIDATES-CONTAINERIZATION.md)

---

## 📝 Notes

**Sprint 04 Learnings Applied**:
- Keep sprint plans synced with live task status
- Update definition-of-done checklists as work completes
- Perform mid-sprint resync if scope changes
- Mark optional items as optional everywhere

**Sprint 05 Focus**:
- This sprint is about deployment readiness, not feature development
- Emphasis on validation, testing, and infrastructure
- Conservative approach to containerization
- Document everything for non-technical deployment

**Next Sprint Preview (Sprint 06)**:
- TASK-058: Background detection jobs and durable run state
- TASK-059: Backend layer decomposition and logging consolidation
- TASK-026: CPU Optimization
- TASK-027: Enhanced Error Handling
- TASK-060 / TASK-061 and remaining stretch work depending on Sprint 05 closeout
