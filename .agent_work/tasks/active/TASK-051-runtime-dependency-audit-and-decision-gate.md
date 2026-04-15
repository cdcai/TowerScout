# TASK-051: Runtime Dependency Audit and Decision Gate

**Status**: COMPLETED  
**Priority**: CRITICAL  
**Type**: C (Architecture / Deployment Readiness)  
**Estimated Effort**: 12-18 hours across Phase 1 audit plus selected Phase 2 cleanup  
**Created**: April 8, 2026  
**Last Updated**: April 9, 2026  
**Target Sprint**: Sprint 05

---

## Objective

Execute a proof-based runtime dependency audit, select the safest post-audit path, and complete the approved cleanup needed before Docker work proceeds.

This task is intentionally split:

- **Phase 1**: Audit, validation, and documentation only
- **Decision Gate**: Review findings and choose the next path
- **Phase 2**: Option 2 selected on April 8, 2026:
  - manifest cleanup for verified explicit runtime gaps only
  - runtime-doc cleanup for the now-verified install/runtime truth
  - no runtime hardening, Torch Hub redesign, or Docker work inside `TASK-051`

This is a deployment-readiness and architecture-accuracy task, not a user-facing feature task.

---

## Context

Sprint 05 sequencing requires `TASK-051` to complete before `TASK-025` Docker work begins. The current repo already contains evidence that the runtime dependency story is not fully explicit:

- `webapp/requirements.txt` mixes obvious runtime packages with at least one likely notebook-only candidate (`seaborn`)
- `webapp/ts_yolov5.py` loads YOLO through `torch.hub.load('ultralytics/yolov5', 'custom', ...)`, which creates an indirect runtime surface not visible from TowerScout's direct imports alone
- the local environment already has a populated Torch Hub cache, which can mask missing first-run requirements
- existing Windows user-testing guidance documents manual installs for `tqdm` and `setuptools<82` to restore `pkg_resources`
- current runtime code auto-detects CUDA, but it is not yet documented whether CUDA-capable users must take installation/setup steps before TowerScout can use it

Because Docker image scope and dependency truthfulness are tightly coupled, this task must establish what is truly required at runtime, what is only transitively present today, what is research-only, and what the docs currently say that the manifests do not.

The post-close stale-cache finding also made one limitation explicit: proving the current empty-cache upstream path is not enough while TowerScout still executes mutable Torch Hub cache state from earlier downloads.

---

## Current Status Snapshot

- `TASK-049` explicitly handed runtime dependency verification to `TASK-051`
- `TASK-025` and `TASK-052` are blocked on a credible runtime/dependency baseline
- the Phase 1 decision gate is complete
- Option 2 was selected and executed for Phase 2 on April 8, 2026
- a post-close user terminal log on April 8, 2026 proved that stale cached `ultralytics_yolov5_master` snapshots can still import `pkg_resources` and fail under newer setuptools even though the fresh-cache upstream path no longer does
- a short-term stale-cache recovery path now exists in `webapp/ts_yolov5.py` to clear `pkg_resources`-era Hub snapshots and retry once with a fresh load
- that short-term mitigation has now been superseded by `TASK-055`, which pins the YOLOv5 Hub ref to a tested commit SHA
- `TASK-051` now hands off to `TASK-055`, then `TASK-052`
- current local machine facts already known at task start:
  - `torch 2.2.1+cpu`
  - `torch.cuda.is_available() == False`
  - `torch.cuda.device_count() == 0`
- current local machine also has an existing Torch Hub cache at `C:\Users\bg90\.cache\torch\hub\ultralytics_yolov5_master`
- `towerscout.py` can require `PYTHONIOENCODING=utf-8` for import/startup verification on Windows PowerShell because of emoji startup output
- this task document is now the completed source of truth for `TASK-051` audit, cleanup, and handoff

---

## Scope

### Included in Phase 1

#### 1. Runtime dependency truth audit
- Build a package matrix for `webapp/requirements.txt`
- Classify each package as:
  - direct runtime
  - indirect runtime through current YOLO Torch Hub behavior
  - dev/test only
  - research/notebook/training only
  - unresolved
- Audit `webapp/`, `tests/`, `Model/`, and `SyntheticData/` separately
- Treat Torch Hub cache behavior and hidden requirement checks as part of the real current runtime

#### 2. Missing-dependency gap audit
- Investigate runtime or setup dependencies not currently declared in `webapp/requirements.txt`
- Explicitly verify:
  - `tqdm`
  - `pkg_resources` via `setuptools`
  - any additional gaps surfaced by YOLO/Torch Hub proof runs or active docs
- For every missing dependency candidate, determine whether the correct outcome is:
  - add to runtime manifest
  - document as a prerequisite
  - leave as transitive
  - defer until runtime-hardening decisions are made

#### 3. CUDA and packaging audit
- Document TowerScout's current Torch packaging reality for:
  - CPU-only installs
  - CUDA-capable installs
  - runtime fallback when CUDA is unavailable
- Investigate whether CUDA-specific Python dependencies belong in `webapp/requirements.txt` or only in documentation
- Audit whether any `nvidia-*` Python packages need direct mention or are purely Torch-wheel/transitive concerns
- Determine whether a user must take action to enable CUDA on a CUDA-capable machine, including:
  - alternate Torch install command or index URL
  - external driver/runtime prerequisites
  - environment-variable or app-config steps
  - whether TowerScout auto-uses CUDA once a compatible Torch build is installed

#### 4. Documentation reconciliation
- Audit dependency/setup/runtime instructions in active docs, including:
  - `README.md`
  - `.agent_work/context/guides/TowerScout_Development_Setup_Guide.txt`
  - `.agent_work/context/guides/TowerScout_User_Testing_Guide.txt`
  - `.agent_work/context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt`
  - any active guide that describes runtime install behavior
- Reconcile documented guidance for:
  - `tqdm`
  - `pkg_resources`
  - `setuptools<82`
  - Torch Hub first-load behavior
  - CUDA expectations and whether user action is needed

#### 5. Decision-gate outputs
- Produce a concise decision memo at the end of Phase 1
- Stop for review before any manifest edits or runtime hardening work

### Included in Phase 2

#### 1. Runtime manifest cleanup
- Update `webapp/requirements.txt` to add the two verified explicit runtime gaps from Phase 1:
  - `psutil`
  - `tqdm`
- Keep current YOLO-adjacent runtime packages in place:
  - `ultralytics`
  - `opencv-python`
  - `seaborn`
- Do not expand this phase into a broader package-pruning pass unless validation proves an additional correction is required.

#### 2. Runtime documentation cleanup
- Update the active runtime/setup guides so they match the Phase 1 proof:
  - `.agent_work/context/guides/TowerScout_Development_Setup_Guide.txt`
  - `.agent_work/context/guides/TowerScout_User_Testing_Guide.txt`
  - `.agent_work/context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt`
- Document first-run YOLO/Torch Hub behavior explicitly:
  - first model load may require GitHub/network access unless the Hub repo is already cached
  - this is a real runtime characteristic of the current TowerScout path, not a tester mistake
- Document CUDA enablement clearly:
  - TowerScout auto-uses CUDA if a compatible CUDA-enabled PyTorch build is installed
  - users still must choose a CUDA-enabled PyTorch install path on compatible machines
  - CPU-only installs remain supported
- Remove stale runtime guidance that treats `pkg_resources` or `setuptools<82` as a required workaround for the current audited path.

#### 3. Phase 2 validation
- Re-run app import/startup smoke after manifest and doc changes
- Re-run clean-environment install proof using the updated `webapp/requirements.txt`
- Re-run empty-cache YOLO smoke to confirm the updated manifest covers the verified `tqdm` gap without extra manual installs
- Verify the updated docs no longer require a separate `tqdm` or `pkg_resources` step for the current runtime contract

### Explicitly Excluded From Phase 1

- editing `webapp/requirements.txt`
- editing `requirements-dev.txt`
- adding a research/notebook manifest
- changing Torch Hub loading behavior
- changing Ultralytics requirement-check behavior
- changing runtime CUDA behavior
- changing Dockerfiles, compose config, or volume plans
- folding this work into `TASK-025`

### Explicitly Excluded From Phase 2

- replacing or redesigning the current `torch.hub` load path
- removing `ultralytics`, `opencv-python`, or `seaborn` without new proof that the current runtime path no longer needs them
- adding CUDA-specific `nvidia-*` package pins to `webapp/requirements.txt`
- changing app runtime behavior, model-loading order, or cache strategy
- performing Docker build, image, or compose work

---

## Requirements (EARS Notation)

**R-051-001**: WHEN Phase 1 begins, THE SYSTEM SHALL audit `webapp/requirements.txt` against direct runtime imports, indirect YOLO/Torch Hub behavior, research-only surfaces, and active setup documentation.

**R-051-002**: WHEN Phase 1 audits dependency usage, THE SYSTEM SHALL classify each runtime-manifest package as direct runtime, indirect runtime, dev/test only, research/notebook/training only, or unresolved.

**R-051-003**: WHEN Phase 1 audits missing dependencies, THE SYSTEM SHALL explicitly verify `tqdm`, `pkg_resources` via `setuptools`, and any other undeclared packages required by the active runtime or documented setup flow.

**R-051-004**: WHEN Phase 1 evaluates YOLO behavior, THE SYSTEM SHALL treat Torch Hub cache use and hidden requirement checks as part of the current runtime contract rather than ignoring them as implementation detail.

**R-051-005**: WHEN Phase 1 evaluates CUDA support, THE SYSTEM SHALL document current CPU fallback behavior, CUDA-capable packaging expectations, and whether user action is needed to enable CUDA on compatible machines.

**R-051-006**: WHEN CUDA packaging is evaluated, THE SYSTEM SHALL distinguish Python-manifest requirements from external driver/runtime prerequisites.

**R-051-007**: WHEN Phase 1 validation runs, THE SYSTEM SHALL include app import/startup smoke, clean-environment install checks, an isolated YOLO dependency proof path, and focused checks for `tqdm` and `pkg_resources` failure modes.

**R-051-008**: IF Phase 1 cannot prove that a package is removable or movable without changing runtime behavior, THEN THE SYSTEM SHALL classify it conservatively and carry it into the decision memo as unresolved or keep-for-now.

**R-051-009**: WHEN Phase 1 completes, THE SYSTEM SHALL stop at a decision gate and SHALL NOT edit dependency manifests or runtime behavior until the findings are reviewed.

**R-051-010**: WHEN the decision memo is produced, THE SYSTEM SHALL include verified keeps, verified move/remove candidates, verified missing dependencies, CUDA enablement conclusions, unresolved items, and the smallest safe next-step options.

**R-051-011**: WHEN Option 2 is selected for Phase 2, THE SYSTEM SHALL update `webapp/requirements.txt` to add only the verified explicit runtime gaps proved by Phase 1 unless additional proof during Phase 2 validation requires a narrowly scoped correction.

**R-051-012**: WHEN Option 2 documentation cleanup is executed, THE SYSTEM SHALL remove stale guidance that treats `pkg_resources` and `setuptools<82` as required for the current audited runtime path.

**R-051-013**: WHEN Option 2 documentation cleanup is executed, THE SYSTEM SHALL document first-run YOLO Torch Hub / GitHub dependence and CUDA install-time enablement requirements in the active runtime/setup guides.

**R-051-014**: WHEN Phase 2 validation runs, THE SYSTEM SHALL prove that the updated runtime manifest installs the verified `tqdm` gap without requiring an extra manual install step.

**R-051-015**: WHEN Phase 2 completes, THE SYSTEM SHALL preserve current runtime behavior and SHALL NOT fold Torch Hub hardening or Docker implementation work into `TASK-051`.

---

## Acceptance Criteria

### Phase 1

- [x] `TASK-051` marked `IN_PROGRESS` in `.agent_work/current-tasks.md`
- [x] Dedicated task file created for `TASK-051`
- [x] Runtime dependency matrix created and stored under `.agent_work/`
- [x] Documentation truth table created for manifest state vs doc state vs actual need
- [x] Static import map completed for `webapp/`, `tests/`, `Model/`, and `SyntheticData/`
- [x] App import/startup smoke completed with `TOWERSCOUT_LAZY_MODEL_INIT=1`
- [x] Clean-environment install proof completed for the declared runtime set
- [x] Isolated YOLO dependency smoke completed with a temporary `TORCH_HOME`
- [x] `tqdm` and `pkg_resources` gap analysis completed
- [x] CUDA packaging and enablement analysis completed
- [x] Decision memo written and Phase 1 stopped for review
- [x] No manifest edits, runtime behavior changes, or Docker work performed during Phase 1

### Phase 2

- [x] Option 2 selection recorded in task tracking and decision artifacts
- [x] `webapp/requirements.txt` updated to include `psutil` and `tqdm`
- [x] Active runtime/setup guides updated to reflect first-run Torch Hub/GitHub behavior
- [x] Active runtime/setup guides updated to reflect CUDA wheel-selection requirements and auto-use behavior
- [x] Windows Miniconda guide no longer requires `pkg_resources` / `setuptools<82` for the current audited runtime path
- [x] Clean-environment install proof rerun against the updated runtime manifest
- [x] Empty-cache YOLO smoke rerun after Phase 2 manifest changes
- [x] No Torch Hub redesign, runtime hardening, or Docker work performed as part of `TASK-051` Phase 2

---

## Dependencies

- `TASK-049` closeout and handoff notes
- `.agent_work/context/analysis/FULL-REPO-STALE-CODE-AND-PERFORMANCE-AUDIT.md`
- `.agent_work/current-tasks.md`
- `.agent_work/context/status/SPRINT-05-PLAN.md`
- active dependency/setup guides under `.agent_work/context/guides/`
- official runtime behavior evidence from installed metadata and primary-source package documentation

---

## Planned Supporting Artifacts

These are expected task outputs. Create or update them as Phase 1 evidence and Phase 2 execution require.

- `.agent_work/context/analysis/TASK-051-runtime-dependency-matrix.md`
- `.agent_work/context/analysis/TASK-051-dependency-doc-truth-table.md`
- `.agent_work/context/analysis/TASK-051-cuda-packaging-and-enablement-audit.md`
- `.agent_work/tasks/active/TASK-051/TASK-051-phase-1-decision-memo.md`
- updated `webapp/requirements.txt`
- updated active runtime/setup guides under `.agent_work/context/guides/`

If one artifact cleanly subsumes another, prefer fewer documents with clearer structure over unnecessary fragmentation.

---

## Post-Phase-2 Handoff

Once `TASK-051` Phase 2 is complete, the recommended Sprint 05 sequence is:

1. Close `TASK-051` with the manifest and runtime-doc cleanup complete.
2. Complete `TASK-055` so the YOLO Torch Hub runtime is pinned and no longer tied to the mutable default branch.
3. Move to `TASK-052` to establish the host-side smoke baseline for the current app surface on top of that hardened runtime.
4. Reuse that `TASK-052` smoke contract during `TASK-025` so Docker validation proves the containerized app against the same baseline instead of inventing a separate ad hoc check.

The intent is:

- `TASK-051` makes the runtime contract truthful enough to test
- `TASK-055` hardens the YOLO runtime contract so `TASK-052` does not baseline the earlier mutable-branch behavior
- `TASK-052` defines the reusable validation target
- `TASK-025` proves the containerized app against that target

This sequence is preferred over jumping straight from `TASK-051` to Docker because it reduces the risk of mixing validation design problems with containerization problems.

---

## Implementation Plan

### Phase 0: Task Setup
- Create the `TASK-051` task file
- Mark `TASK-051` in progress in live tracking
- Lock the Phase 1 boundary before execution begins

### Phase 1A: Baseline Manifest and Doc Inventory
- Record current contents of `webapp/requirements.txt` and `requirements-dev.txt`
- Inventory active dependency/setup docs
- Capture current local environment facts relevant to runtime/package analysis

### Phase 1B: Static Dependency Classification
- Build direct import map from active runtime code
- Build separate import maps for tests and research/training surfaces
- Identify obvious mismatches between imports and declared runtime packages

### Phase 1C: Runtime Proof Checks
- Run app import/startup smoke with test env vars and lazy secondary-model init
- Run clean-environment install proof for the current runtime manifest
- Run isolated YOLO proof path with temporary Torch Hub cache
- Investigate whether missing packages are masked by current local environment state

### Phase 1D: Missing Dependency and CUDA Audit
- Investigate `tqdm` and `pkg_resources` / `setuptools`
- Audit Torch/Ultralytics package metadata and official guidance
- Determine whether CUDA-capable users must take setup action before TowerScout can actually use CUDA
- Distinguish:
  - automatic runtime selection
  - manual install/setup prerequisites
  - external system prerequisites

### Phase 1E: Documentation Reconciliation
- Compare runtime truth to current setup/user-testing guides
- Record every place where docs currently imply extra manual installs or omit required ones

### Phase 1F: Decision Gate
- Write a short Phase 1 decision memo with:
  - verified runtime keeps
  - verified move/remove candidates
  - verified missing dependencies
  - CUDA packaging and enablement conclusions
  - unresolved items
  - smallest safe next-step options
- Stop for review

### Phase 2A: Selected Path Lock
- Record the selected Phase 2 path as Option 2 in task tracking and decision artifacts
- Convert the task from "stopped at decision gate" to "approved for manifest cleanup plus runtime-doc cleanup"

### Phase 2B: Manifest Truthfulness Cleanup
- Add `psutil` and `tqdm` to `webapp/requirements.txt`
- Leave `packaging` and `pandas` implicit for now because they remain satisfied transitively and were not selected for explicit pinning in Option 2
- Keep current YOLO-adjacent packages until a separate hardening task changes the model-loading contract

### Phase 2C: Runtime-Doc Cleanup
- Update the development and user setup guides so they:
  - no longer require separate `tqdm` installation outside the runtime manifest
  - no longer require `pkg_resources` verification for the current runtime path
  - clearly state first-run GitHub/Torch Hub dependence
  - clearly explain CUDA install-time wheel choice versus automatic runtime use

### Phase 2D: Validation and Closeout
- Re-run the selected startup/install/YOLO smokes against the updated manifest
- Record final results in the implementation log and acceptance criteria
- Keep Docker and runtime-hardening work out of this task
- Hand off to `TASK-052` after Phase 2 completion so the updated runtime contract is captured in a reusable host-side smoke baseline before Docker implementation begins

---

## Validation Plan

### Required Proof Runs
- Static import map for direct and indirect dependency surfaces
- App import/startup smoke with `TOWERSCOUT_LAZY_MODEL_INIT=1`
- Clean-environment install smoke for the declared runtime set
- Isolated YOLO dependency smoke using temporary `TORCH_HOME`
- Focused `tqdm` and `pkg_resources` failure-mode verification
- CPU-path verification on the current machine
- CUDA packaging/enablement analysis from installed metadata and primary-source guidance

### Expected Local Constraints
- The current machine is CPU-only, so live CUDA execution validation is not expected in Phase 1 unless a CUDA host is later provided
- Windows PowerShell import/startup validation may need `PYTHONIOENCODING=utf-8`
- clean-install or first-run YOLO proof may reveal network/cache assumptions currently hidden by the existing Torch Hub cache

### Required Phase 2 Re-Validation
- Clean install proof after `webapp/requirements.txt` updates
- Empty-cache YOLO load proof after `tqdm` is made explicit in the manifest
- Updated-guide review to confirm:
  - no stale `pkg_resources` requirement remains
  - first-run GitHub/Torch Hub behavior is documented
  - CUDA install-path guidance is documented

---

## Decision Gate Output Format

Phase 1 will stop with a decision memo that covers:

1. **Verified runtime keeps**
2. **Verified move/remove candidates**
3. **Verified missing dependencies**
4. **CUDA packaging and enablement conclusions**
5. **Whether user action is required to enable CUDA on compatible systems**
6. **Unresolved items and why they remain unresolved**
7. **Smallest safe next-step options**

Expected option shapes:

1. Manifest cleanup only
2. Manifest cleanup plus runtime-doc cleanup
3. Runtime hardening first, then manifest cleanup
4. Document current truth only and defer changes

---

## Non-Goals and Safety Boundaries

- Do not let Phase 1 silently expand into `TASK-025`
- Do not rewrite model loading just to make dependency classification cleaner
- Do not remove a package purely because the TowerScout repo does not import it directly if the current YOLO runtime path still depends on it
- Do not force CUDA-specific Python packages into `webapp/requirements.txt` unless Phase 1 proves that is the correct contract
- Do not treat `pkg_resources` as a standalone package; evaluate it as a `setuptools` compatibility requirement
- Do not let Option 2 drift into a larger runtime-hardening effort just because the current Torch Hub contract is imperfect
- Do not use Phase 2 to resolve the first-run GitHub dependence itself; document it and defer any hardening to later work

---

## Implementation Log

### TYPE C - TASK-051 TASK FILE CREATION AND PHASE-1 BOUNDARY LOCK - 2026-04-08
**Objective**: Create the dedicated `TASK-051` task artifact before Phase 1 execution begins.
**Context**: `TASK-051` was defined in Sprint 05 planning but did not yet have its own Type C task file. The audit scope was refined to include missing-dependency analysis, CUDA packaging/enablement analysis, and an explicit mid-task decision gate.
**Decision**: Create a task-specific document in `.agent_work/tasks/` first, keep Phase 1 audit-only, and require review before any dependency-manifest or runtime changes are made.
**Execution**: Drafted this task file with objective, scope, EARS requirements, validation expectations, decision-gate outputs, and planned supporting artifacts.
**Output**: `TASK-051` now has a task-specific source-of-truth document before audit execution begins.
**Validation**: Task file creation complete; live tracker synchronization pending.
**Next**: Update `.agent_work/current-tasks.md` to reflect `TASK-051` as in progress, then begin Phase 1 evidence collection.

### TYPE C - PHASE 1 AUDIT, PROOF RUNS, AND DECISION-GATE ARTIFACTS - 2026-04-08
**Objective**: Execute the full Phase 1 audit and stop at the review checkpoint with evidence-backed findings.
**Context**: The task required proof-based dependency classification, missing-dependency analysis for `tqdm` and `pkg_resources`, CUDA packaging/enablement analysis, and documentation reconciliation before any Phase 2 manifest changes could be discussed.
**Decision**: Use a layered Phase 1 approach: static import scanning, app startup smoke, clean install proof, empty-cache YOLO proof, focused import-blocker probes, and official PyTorch/setuptools guidance review. Use an isolated `pip --target` install after local Windows `venv` creation hit an `ensurepip` temp-permissions issue unrelated to the repo manifest.
**Execution**:
- Scanned `webapp/`, `tests/`, `Model/`, and `SyntheticData/` imports to separate runtime, test, and research surfaces.
- Verified startup with `TOWERSCOUT_LAZY_MODEL_INIT=1`, test provider keys, and `PYTHONIOENCODING=utf-8`.
- Completed a clean manifest install into `.agent_work/tmp/task051-target-audit`.
- Proved the first-run YOLO path with a temporary `TORCH_HOME`, including the empty-cache failure without network and success after network was allowed.
- Ran blocker probes to determine whether `tqdm`, `pkg_resources`, `seaborn`, and `packaging` were truly on the current inference/load path.
- Wrote the Phase 1 matrix, doc truth table, CUDA audit, and decision memo artifacts.
**Output**:
- `.agent_work/context/analysis/TASK-051-runtime-dependency-matrix.md`
- `.agent_work/context/analysis/TASK-051-dependency-doc-truth-table.md`
- `.agent_work/context/analysis/TASK-051-cuda-packaging-and-enablement-audit.md`
- `.agent_work/tasks/active/TASK-051/TASK-051-phase-1-decision-memo.md`
**Validation**:
- Startup smoke passed.
- Clean install proof passed.
- Empty-cache YOLO proof passed once network access was allowed.
- `tqdm` was verified as a real missing runtime dependency on the current YOLO path.
- `pkg_resources` was verified as not part of the current runtime truth.
- CUDA was verified as an install-time/user-choice concern with automatic runtime use once a compatible torch build is present.
**Next**: Stop for user review at the decision gate before making any manifest or runtime changes.

### TYPE C - PHASE 2 PATH SELECTION: OPTION 2 MANIFEST + RUNTIME-DOC CLEANUP - 2026-04-08
**Objective**: Record the approved post-audit path before Phase 2 execution begins.
**Context**: Phase 1 completed with a clear smallest-safe-next-step recommendation: Option 2, meaning targeted manifest cleanup plus runtime-doc cleanup without Torch Hub hardening.
**Decision**: Proceed with Option 2 only. Phase 2 will add the verified explicit runtime gaps (`psutil`, `tqdm`) and update active setup/runtime guides to remove stale `pkg_resources` guidance and document first-run Torch Hub/GitHub plus CUDA install-time requirements.
**Execution**: Updated the task document, decision memo, and active sprint tracker to reflect that Phase 2 is now authorized on the narrowed Option 2 path.
**Output**: `TASK-051` no longer sits at an ambiguous decision gate; the approved Phase 2 scope is documented and bounded before implementation begins.
**Validation**: Task planning artifacts now consistently describe Option 2 as the selected path.
**Next**: Execute the manifest and runtime-doc cleanup described in this task file, then rerun the scoped validation proofs.

### TYPE C - PHASE 2 EXECUTION, VALIDATION, AND TASK CLOSEOUT - 2026-04-08
**Objective**: Complete the approved Option 2 manifest/runtime-doc cleanup and close `TASK-051` without expanding scope.
**Context**: The approved Phase 2 scope was intentionally narrow: make the runtime manifest truthful for the two verified explicit gaps, update active setup/runtime guides, and preserve the current `torch.hub` runtime contract. When execution began, the approved Phase 2 edits were already present in the worktree and matched the selected Option 2 scope, so Phase 2 focused on validating that candidate set and syncing the task artifacts to the results.
**Decision**: Treat the existing worktree changes in `webapp/requirements.txt` and the three active runtime/setup guides as the Phase 2 candidate set, validate them against the scoped proof plan, and close the task only if the proofs still held.
**Execution**:
- Verified that `webapp/requirements.txt` now explicitly includes `psutil==7.1.3` and `tqdm==4.67.1`.
- Verified that the active guides now remove the stale `pkg_resources` / `setuptools<82` workaround and document first-run Torch Hub / GitHub plus CUDA wheel-selection behavior:
  - `.agent_work/context/guides/TowerScout_Development_Setup_Guide.txt`
  - `.agent_work/context/guides/TowerScout_User_Testing_Guide.txt`
  - `.agent_work/context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt`
- Re-ran startup/import validation with `TOWERSCOUT_LAZY_MODEL_INIT=1`, test provider keys, and `PYTHONIOENCODING=utf-8`; result: `app_import_ok True`, `torch_cuda_available False`.
- Re-ran `python -m pytest --collect-only tests -q`; result: `159 tests collected`.
- Re-ran clean-manifest install proof:
  - sandboxed install still failed without network access
  - networked `pip install --target .agent_work/tmp/task051-target-phase2-net2 -r webapp/requirements.txt` succeeded
  - isolated `python -S` import against that target proved `psutil`, `tqdm`, and `flask` loaded from the clean target path rather than the active `.venv`
- Re-ran empty-cache YOLO proof:
  - offline empty-cache `torch.hub.load(...)` failed with `RuntimeError` stating the repo could not be found in cache without internet
  - networked empty-cache `torch.hub.load(...)` succeeded and downloaded `https://github.com/ultralytics/yolov5/zipball/master`
- Confirmed that no Torch Hub redesign, runtime-hardening changes, or Docker work were performed.
**Output**:
- `webapp/requirements.txt` now explicitly carries the two verified runtime gaps
- the three active setup/runtime guides now match the audited runtime truth
- `TASK-051` execution artifacts are updated to reflect completed Option 2 follow-through
**Validation**:
- Startup/import smoke passed
- Pytest collection gate remained clean at `159 tests collected`
- Clean-manifest install proof passed once network access was allowed for the temporary install target
- Empty-cache YOLO proof reproduced the documented offline failure and networked success path
- Stale `pkg_resources` / `setuptools<82` guidance was removed from the active runtime/setup guides
**Next**: Close `TASK-051` and move to `TASK-052` so the host-side smoke baseline captures the now-truthful runtime contract before Docker work begins.

### TYPE C - POST-CLOSE FINDING: STALE TORCH HUB CACHE DRIFT AND SHORT-TERM MITIGATION - 2026-04-08
**Objective**: Correct the `TASK-051` runtime record after a real user hit a stale-cache YOLO failure that the original Phase 1 proof did not expose.
**Context**: A user testing the Phase 2 setup hit `ModuleNotFoundError: No module named 'pkg_resources'` during YOLO load. Their terminal log showed `torch.hub` loading a cached `ultralytics_yolov5_master` snapshot from `C:\Users\iek4/.cache\torch/hub/ultralytics_yolov5_master`, and that cached snapshot still imported `pkg_resources` in `utils/general.py`. This contradicted the earlier fresh-cache proof, which had used a newly downloaded upstream snapshot whose `utils/general.py` no longer imported `pkg_resources`.
**Decision**: Treat this as a stale Torch Hub cache drift issue, not as evidence that `pkg_resources` belongs back in `webapp/requirements.txt`. Amend the `TASK-051` findings to distinguish fresh-cache upstream behavior from stale cached Hub snapshots, and land a short-term code-side recovery path in `webapp/ts_yolov5.py`.
**Execution**:
- Reviewed the user terminal log and confirmed the failure was happening inside the cached Hub repo, not inside TowerScout code before model initialization.
- Compared the stale-cache failure path to the current upstream/fresh-cache `utils/general.py`, which now imports `packaging` and `pandas` instead of `pkg_resources`.
- Implemented a narrow recovery path in `webapp/ts_yolov5.py`:
  - detect the `pkg_resources` failure mode
  - inspect the cached YOLOv5 Hub repo for the stale `import pkg_resources as pkg` signature
  - clear only those stale cached repo directories plus Hub zip artifacts
  - retry once with `force_reload=True`
- Added focused unit coverage for successful stale-cache recovery and refresh-failure reporting.
- Updated the `TASK-051` artifacts so the runtime truth is now recorded as cache-dependent until the broader Torch Hub loading strategy is hardened.
**Output**:
- `webapp/ts_yolov5.py` now contains a short-term stale-cache migration path
- `tests/unit/test_yolov5_cache_migration.py` proves the targeted recovery behavior
- `TASK-051` artifacts now distinguish fresh-cache upstream behavior from stale cached Hub snapshots
**Validation**:
- The stale-cache recovery path is covered by new unit tests
- The new finding matches the user-provided terminal log and the current upstream YOLOv5 `utils/general.py`
- `pkg_resources` remains a stale-cache compatibility surface, not a fresh-manifest add candidate
**Next**: Keep `TASK-051` closed as a documented audit-plus-mitigation task, complete `TASK-055` to pin and harden the YOLO Torch Hub runtime path, and then let `TASK-052` include a bounded detection-readiness path that catches regressions against that hardened baseline.

### TYPE C - POST-CLOSE FOLLOW-UP: TASK-055 SUPERSEDED THE SHORT-TERM HUB MITIGATION - 2026-04-09
**Objective**: Record the follow-up runtime hardening that replaced the earlier short-term `pkg_resources` cache-migration workaround as the preferred Sprint 05 baseline.
**Context**: After `TASK-051` closed, the user approved a separate follow-up task for YOLO Torch Hub pinned-ref hardening. Live validation showed that published YOLOv5 release tags still imported `pkg_resources`, so the follow-up task pinned TowerScout to a tested commit SHA instead.
**Decision**: Keep `TASK-051` closed and record `TASK-055` as the authoritative follow-up for YOLO runtime hardening instead of reopening the dependency-audit task.
**Execution**:
- Updated the `TASK-051` cross-reference notes and handoff sequence to point to `TASK-055` before `TASK-052`.
- Preserved the historical record that `TASK-051` landed the short-term mitigation, but marked that mitigation as superseded by the pinned-ref hardening task.
**Output**: `TASK-051` remains the source of truth for the dependency audit, while `TASK-055` now owns the hardened YOLO Torch Hub runtime contract.
**Validation**: The live Sprint tracker and the new `TASK-055` task artifact now agree on the post-`TASK-051` sequence.
**Next**: Proceed with `TASK-052` on top of the hardened runtime path from `TASK-055`.
