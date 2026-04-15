# Full-Repo Stale Code and Performance Audit

**Created**: 2026-03-23  
**Status**: Full-repo audit complete; partially refreshed on 2026-03-31 for TASK-049 batch-1 intake and validation  
**Related Tasks**: TASK-050, TASK-049, ISSUE-003, TASK-048

---

## Executive Summary

This audit covered the full repository, not just `webapp/`. The current repo state already contains multiple categories of stale or drifted assets:

- **Confirmed generated/stale artifacts**: tracked `.coverage`, tracked `.DS_Store`, 25 tracked `webapp/cache/maps/*.cache` files, `webapp/templates/towerscout_backup.html`, and `webapp/js/src/towerscout.js.stage3.bak`
- **High-confidence orphaned/debug surfaces**: the 20-file `webapp/tests/` tree and stage-specific refactor helper scripts in `webapp/js/src/`
- **Confirmed test/runtime drift**: `tests/unit/test_event_system.py` no longer matches the `ts_events.py` API, and `tests/integration/test_end_to_end.py` fails collection because importing `towerscout` triggers missing model initialization
- **Likely dependency drift**: `seaborn` appears notebook-only, and `ultralytics` does not appear as a direct runtime import in `webapp/`

Performance-wise, the repo shows three immediate pressure points:

- **Large frontend footprint**: `webapp/js/towerscout.js` is 456,092 bytes and 10,560 lines
- **Large source orchestrator**: `webapp/js/src/towerscout.js` is 174,235 bytes and 4,239 lines
- **Monolithic backend entrypoint**: `webapp/towerscout.py` is 91,530 bytes and 1,979 lines, and its import-time side effects already break test collection

The cleanup recommendation is to remove only the low-risk confirmed artifacts first, then use targeted follow-on tasks for uncertain/manual/debug surfaces and performance refactors.

---

## 2026-03-31 Refresh Addendum

This audit is still directionally useful, but it is no longer fully current without a March 31 refresh pass. The following points supersede the March 23 state when using this document for `TASK-049` planning:

- **Validation baseline rerun (2026-03-31)**:
  - `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m pytest --collect-only tests -q --basetemp .agent_work\pytest-basetemp-plan -o cache_dir=.agent_work\.pytest_cache_plan`
    - **Result**: 149 tests collected, 2 collection errors
    - **Same failures still confirmed**:
      1. `tests/integration/test_end_to_end.py` still fails collection because importing `towerscout` eagerly initializes `EN_Classifier` and raises `ModelLoadError` when local weights are absent
      2. `tests/unit/test_event_system.py` still imports removed `ts_events` functions that are no longer exposed by `webapp/ts_events.py`
  - `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m flake8 webapp tests --select=F401,F841 --statistics --jobs 1`
    - **Result**: unchanged at 105 `F401` unused imports and 14 `F841` unused locals
- **Already-consumed performance/logging findings**:
  - `TASK-048` is now complete, so `P-008` should be treated as partially consumed rather than a fresh queue item
  - the March 31 `ISSUE-003` quick-win tranche is complete, so this audit should not be read as if the secondary-classifier debug-image writes and metadata-only tile overlay allocation are still unresolved
  - `webapp/ts_en.py` now gates EfficientNet debug image writes behind `TOWERSCOUT_SAVE_EN_DEBUG_IMAGES`
  - metadata-only tile records now skip provider overlay allocation by default through the `PlaceRect(..., renderOnMap=false)` path used by `Tile`
- **Current working-tree size metrics (replace the March 23 values when reasoning about current bloat)**:
  - `webapp/js/towerscout.js`: 471,771 bytes / 10,687 lines
  - `webapp/js/src/towerscout.js`: 179,477 bytes / 4,244 lines
  - `webapp/towerscout.py`: 91,156 bytes / 1,970 lines
- **Tracking correction for `towerscout.js.stage3.bak`**:
  - `webapp/js/src/towerscout.js.stage3.bak` still exists locally and is referenced by `webapp/js/src/comment_providers.sh`
  - it is **not** currently present in the tracked-file inventory returned by `git ls-files`
  - it is therefore excluded from `TASK-049` batch 1 and should only be revisited in a later helper-script / manual-artifact cleanup pass
- **TASK-049 batch-1 scope lock**:
  - include only `.coverage`, `.DS_Store`, tracked `webapp/cache/maps/*.cache`, and `webapp/templates/towerscout_backup.html`
  - explicitly exclude `webapp/js/src/towerscout.js.stage3.bak`, `webapp/js/src/comment_providers.sh`, `webapp/js/src/temp_extract_providers.sh`, `webapp/tests/`, `tests/unit/test_event_system.py`, `tests/integration/test_end_to_end.py`, `webapp/requirements.txt` dependency cleanup, and `webapp/js/towerscout.original.js`
- **TASK-049 batch-1 execution and validation (2026-03-31)**:
  - `.coverage` and `.DS_Store` were removed from tracked git state with `git rm --cached`
  - the 25 tracked `webapp/cache/maps/*.cache` files were removed from tracked git state with `git rm --cached`
  - `webapp/templates/towerscout_backup.html` was removed from the repo
  - `git ls-files` returned no matches for the batch-1 targets after cleanup
  - `rg -n "towerscout_backup\\.html" webapp tests .github -S` returned no runtime/build/test references
  - post-cleanup validation remained at `149 collected / 2 errors` for pytest collection and `105 F401 / 14 F841` for flake8
  - pytest emitted a non-blocking `PytestCacheWarning` because `.agent_work\.pytest_cache_task049` could not create `lastfailed` cache output due `WinError 5`
- **Validation-gate repair after batch 1 (2026-03-31)**:
  - `tests/unit/test_event_system.py` was rebuilt to the current `ExitEvents` API
  - `tests/integration/test_end_to_end.py` was quarantined with a module-level skip because it targets removed routes (`/draw_polygon`, `/get_status`, `/cancel_detection`) and the old event-helper API
  - `webapp/towerscout.py` now supports test-only lazy secondary-classifier initialization through `TOWERSCOUT_LAZY_MODEL_INIT=1`, while eager initialization remains the default runtime behavior
  - `pytest tests/unit/test_event_system.py -q` now passes at `5 passed`
  - `pytest --collect-only tests -q` now completes at `154 collected / 0 collection errors`
  - pytest still emits non-blocking cache warnings for local `.pytest_cache_*` directories due `WinError 5`
- **Medium-risk stale-surface triage after the clean collection gate (2026-03-31)**:
  - `webapp/js/src/comment_providers.sh` and `webapp/js/src/temp_extract_providers.sh` were archived to `.agent_work/context/archive/2026-03-task-049-stale-surfaces/js-refactor-helpers/`
  - the full `webapp/tests/` tree was archived to `.agent_work/context/archive/2026-03-task-049-stale-surfaces/webapp-tests/`
  - the old active paths no longer exist in the working tree
  - `webapp/towerscout.py` had its scoped `F401/F841` findings removed while preserving default runtime/CUDA behavior
  - `flake8 webapp tests --select=F401,F841 --statistics --jobs 1` improved from `105 F401 / 14 F841` to `73 F401 / 6 F841`
  - `flake8 webapp/towerscout.py --select=F401,F841 --statistics --jobs 1` is now clean

---

## Audit Method

### Structural Inventory
- Reviewed runtime surfaces: `webapp/`, top-level `tests/`, build/config files, Flask route/template flow, and `webapp/build.js`
- Reviewed auxiliary surfaces: `webapp/tests/`, `Model/`, `SyntheticData/`, `TowerScoutSite/`, `hosting/`
- Reviewed existing planning and analysis artifacts under `.agent_work/`

### Reference Tracing
- `git ls-files` for tracked file inventory
- `rg` searches for route/template/build/test references
- `pytest.ini` to confirm automated test scope
- dependency-to-import tracing for `webapp/requirements.txt`

### Baseline Validation Commands
- `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m pytest --collect-only tests -q`
- `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m flake8 webapp tests --select=F401,F841 --statistics --jobs 1`

### Evidence Standard
A candidate is only marked `confirmed stale` when at least two independent signals align, for example:
- tracked file is ignored by `.gitignore`
- no route/template/build/test references exist
- file naming/content clearly identifies it as generated/backup/refactor-only

---

## Baseline Validation

### Pytest Collection
- **Command**: `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m pytest --collect-only tests -q`
- **Result**: 148 tests collected, 2 collection errors
- **Implications**:
  - the test suite is not a clean validation baseline yet
  - test infrastructure drift itself is now part of the stale-code audit

**Collection errors found**:
1. `tests/integration/test_end_to_end.py`
   - importing `towerscout` eagerly initializes `EN_Classifier`
   - collection fails if model weights are absent
2. `tests/unit/test_event_system.py`
   - imports `set_event`, `get_event`, `clear_events`, `create_exit_event`
   - current `webapp/ts_events.py` exposes only the `ExitEvents` class

### Flake8 Unused Code Scan
- **Command**: `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m flake8 webapp tests --select=F401,F841 --statistics --jobs 1`
- **Result**:
  - 105 `F401` unused imports
  - 14 `F841` unused locals
- **Implications**:
  - dead-code and drift signals are widespread across both runtime and tests
  - cleanup work should start with the highest-signal buckets rather than one blanket pass

---

## Finding Schema

Each finding in this report uses the following fields:

- `id`
- `surface`
- `path`
- `type`
- `status`
- `evidence`
- `user_risk`
- `perf_impact`
- `recommended_action`
- `validation_needed`

### Status Meanings
- `confirmed stale`: safe to treat as obsolete/generated based on current evidence
- `generated/backup artifact`: tracked output or rollback material that may still have process value
- `orphaned debug/test surface`: not connected to current automated/runtime flow
- `legacy-but-active`: still used by active runtime or build process
- `dependency drift`: dependency list no longer aligned with actual runtime usage
- `needs runtime verification`: plausible stale candidate but deletion still needs proof

---

## Findings

| id | surface | path | type | status | evidence | user_risk | perf_impact | recommended_action | validation_needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | repo root | `.coverage` | generated artifact | confirmed stale | tracked by git; `.gitignore` explicitly ignores `.coverage` | low | none | remove from git index and keep ignored | none |
| F-002 | repo root | `.DS_Store` | generated artifact | confirmed stale | tracked by git; `.gitignore` explicitly ignores `.DS_Store` | low | none | remove from git index and keep ignored | none |
| F-003 | webapp cache | `webapp/cache/maps/*.cache` (25 tracked files) | generated artifact | confirmed stale | tracked by git; `.gitignore` ignores `*.cache` and `webapp/cache/**/*.cache` | low | low | remove tracked cache files and keep cache dir untracked | none |
| F-004 | templates | `webapp/templates/towerscout_backup.html` | backup artifact | confirmed stale | route audit renders `towerscout.html`; no runtime reference found | low | none | archive or remove in cleanup batch | browser smoke after deletion |
| F-005 | JS source | `webapp/js/src/towerscout.js.stage3.bak` | backup artifact | confirmed stale | stage-specific backup filename; not in `webapp/build.js` module order | low | none | remove in cleanup batch | none |
| F-006 | JS source | `webapp/js/src/comment_providers.sh`, `webapp/js/src/temp_extract_providers.sh` | refactor helper scripts | high-confidence suspect | stage-specific extraction/comment scripts; no runtime/build references found | low | low | archive or delete after confirming no future refactor reuse | maintainer confirmation |
| F-007 | test surface | `webapp/tests/` (20 tracked files) | orphaned debug/test surface | high-confidence suspect | `pytest.ini` limits collection to top-level `tests`; repo reference search found no active workflow references | medium | low | split into archived manual harnesses or delete after triage | confirm whether any files are still used manually |
| F-008 | unit tests | `tests/unit/test_event_system.py` | stale test contract | confirmed drift | imports removed/nonexistent `ts_events` API while current module only exposes `ExitEvents` class | low | none | rewrite test to current API or archive it | rerun pytest collection |
| F-009 | integration tests | `tests/integration/test_end_to_end.py` | test infrastructure drift | confirmed drift | test import path triggers model initialization and fails without local weights | medium | medium | decouple app import from model initialization or guard with fixtures/mocks | rerun pytest collection |
| F-010 | dependencies | `webapp/requirements.txt` (`seaborn`) | dependency drift | high-confidence suspect | `seaborn` appears in notebooks, not in runtime `webapp/` imports | low | low | move notebook-only dependency out of runtime requirements | fresh install smoke |
| F-011 | dependencies | `webapp/requirements.txt` (`ultralytics`) | dependency drift | needs runtime verification | runtime `webapp/` code uses `torch.hub.load('ultralytics/yolov5', ...)` but does not import `ultralytics` directly | medium | low | verify install/runtime requirement before removal | app startup smoke |
| F-012 | build output | `webapp/js/towerscout.original.js` | generated backup artifact | legacy-but-active | `webapp/build.js` explicitly uses it as backup/rollback material; TASK-038 docs reference the strategy | medium | low | preserve for now; revisit only after rollback strategy changes | update build process first |

---

## Performance Opportunities

| id | area | evidence | rank | recommended direction |
| --- | --- | --- | --- | --- |
| P-001 | frontend bundle size | `webapp/js/towerscout.js` is 456,092 bytes / 10,560 lines; `webapp/js/src/towerscout.js` is 174,235 bytes / 4,239 lines | safe refactor | trim dead/backup/refactor-only paths first, then reevaluate bundle structure and startup parse cost |
| P-002 | backend startup side effects | importing `webapp/towerscout.py` triggers eager model initialization and breaks test collection when weights are absent | safe refactor | move to app-factory style startup and lazy model initialization |
| P-003 | unused-code noise | flake8 reports 105 unused imports and 14 unused locals across `webapp` and `tests` | quick win | remove unused imports/locals in small batches so future audits and refactors have cleaner signal |
| P-004 | test validation reliability | pytest collection is not clean even before execution | quick win | repair or quarantine broken tests so cleanup work has a trustworthy regression gate |
| P-005 | cache/artifact hygiene | tracked cache, coverage, and OS files create repo churn and false-positive "activity" | quick win | remove tracked generated artifacts and rely on ignore rules |
| P-006 | large dataset UI scale | Sprint 04 already has ISSUE-003 for 500+ detections; provider switching and detection rendering remain known stress areas | defer | use existing `ts_performance.py` plus browser profiling to size list virtualization, marker clustering, and event debouncing work |
| P-007 | dependency footprint | runtime requirements likely include notebook-only packages | safe refactor | split runtime vs notebook/training dependencies to reduce install size and environment complexity |
| P-008 | console/log noise | Sprint 04 already includes TASK-048; verbose logging exists across JS and backend workflow paths | quick win | standardize logs, reduce noise, and improve profiling clarity before deeper perf tuning |

---

## Active Surfaces to Preserve for Now

These should **not** be treated as stale just because they look auxiliary:

- `TowerScoutSite/`
  - Flask routes `/site/` and `/site/<path:path>` actively serve this directory
- `webapp/js/towerscout.js`
  - generated, but active runtime bundle
- `webapp/js/towerscout.original.js`
  - currently part of the documented rollback strategy
- `webapp/tests/`
  - likely orphaned, but manual-use confirmation is still needed before deletion

---

## Recommended Cleanup Ordering

### Low-Risk Batch 1
- `.coverage`
- `.DS_Store`
- tracked `webapp/cache/maps/*.cache`
- `webapp/templates/towerscout_backup.html`

### Verification Batch 2
- `webapp/js/src/towerscout.js.stage3.bak`
- `webapp/js/src/comment_providers.sh`
- `webapp/js/src/temp_extract_providers.sh`
- `webapp/tests/`
- notebook-only dependency candidates

### Structural Refactor Batch 3
- app startup/model initialization behavior in `webapp/towerscout.py`
- broken test collection paths
- large dataset rendering/perf work from `ISSUE-003`

---

## Task Mapping

- **TASK-049 batch 1**: execute only the low-risk tracked removals from findings F-001 through F-004
- **Later TASK-049 or follow-on cleanup**: revisit F-005 through F-010 only after the low-risk batch is validated and the scope is re-decided
- **ISSUE-003**: consume P-006 plus any frontend rendering/provider-switch findings that need browser profiling
- **TASK-048**: consume P-008 logging-noise findings
- **Future dependency cleanup task**: handle runtime vs notebook dependency split if `ultralytics` and other packages prove non-runtime

---

## Recommended Next Step

`TASK-049` batch 1 is complete, and the pytest collection gate is now clean. The next decision is whether findings F-005 through F-010 remain in `TASK-049` or split into follow-on work.

If cleanup continues under `TASK-049`, the remaining recommended order is:

- decide whether to keep or remove the local-only `webapp/js/src/towerscout.js.stage3.bak`
- keep dependency cleanup last
- treat `ultralytics` as runtime/CUDA-sensitive until verified in a clean environment
