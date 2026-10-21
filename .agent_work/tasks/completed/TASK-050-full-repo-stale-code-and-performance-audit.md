# TASK-050: Full-Repo Stale Code and Performance Audit

**Status**: COMPLETED  
**Priority**: HIGH  
**Type**: C (Architecture / Analysis)  
**Estimated Effort**: 6-10 hours  
**Created**: March 23, 2026  
**Completed**: March 23, 2026  
**Target Sprint**: Sprint 04

---

## Objective

Perform a full-repository audit to identify old, unused, orphaned, stale, or generated code/artifacts and capture no-functionality-change performance opportunities. Produce one evidence-backed master report that downstream cleanup and optimization tasks can consume safely.

---

## Context

**Why this task exists**:
- The repo now spans active runtime code, debug/test harnesses, notebooks, synthetic-data tooling, a marketing site, and historical artifacts from multiple refactors.
- Performance has degraded as development continued, but the current cleanup task (`TASK-049`) was scoped as direct removal work without a dedicated discovery pass.
- Existing repo evidence already shows drift signals:
  - tracked generated artifacts despite `.gitignore` rules (`.coverage`, `.DS_Store`, cache files)
  - backup/refactor artifacts (`towerscout_backup.html`, `towerscout.js.stage3.bak`)
  - uncollected debug/test surface under `webapp/tests/`
  - test/runtime drift (`tests/unit/test_event_system.py`, `tests/integration/test_end_to_end.py`)
  - very large active entrypoints (`webapp/towerscout.py`, `webapp/js/src/towerscout.js`, generated `webapp/js/towerscout.js`)

**Scope**:
- Included: `webapp/`, top-level `tests/`, `webapp/tests/`, `Model/`, `SyntheticData/`, `TowerScoutSite/`, `hosting/`, dependency manifests, and build/config files.
- Inventory-only unless linked by active workflow: `.agent_work/context/archive/` and other purely archival documentation.

**Downstream Dependencies**:
- `TASK-049` should use this audit as the input for removal/remediation work.
- `ISSUE-003` should use the performance-opportunity findings relevant to large datasets.
- `TASK-048` should consume the logging/console-noise findings.

---

## Requirements (EARS Notation)

**R-050-001**: WHEN the audit runs, THE SYSTEM SHALL evaluate the full repository rather than only the live webapp runtime surface.

**R-050-002**: WHEN a candidate stale/orphaned item is identified, THE SYSTEM SHALL require at least two independent evidence signals before classifying it as `confirmed stale`.

**R-050-003**: THE SYSTEM SHALL create a master analysis document in `.agent_work/context/analysis/` that records findings using a fixed schema.

**R-050-004**: WHERE a candidate item may still support active workflows, THE SYSTEM SHALL classify it as `legacy-but-active`, `needs runtime verification`, or `high-confidence suspect` instead of recommending blind deletion.

**R-050-005**: WHEN baseline validation commands are run, THE SYSTEM SHALL record their commands, outcomes, and implications in the analysis document.

**R-050-006**: THE SYSTEM SHALL capture performance opportunities separately from stale-code findings and rank them as `quick win`, `safe refactor`, or `defer`.

**R-050-007**: WHEN active served or build-critical surfaces are reviewed, THE SYSTEM SHALL preserve them unless explicit evidence shows they are obsolete.

**R-050-008**: THE SYSTEM SHALL map audit outcomes to downstream tasks so follow-on cleanup does not repeat discovery work.

---

## Acceptance Criteria

- [x] Master report created at `.agent_work/context/analysis/FULL-REPO-STALE-CODE-AND-PERFORMANCE-AUDIT.md`
- [x] Findings recorded with schema fields: `id`, `surface`, `path`, `type`, `status`, `evidence`, `user_risk`, `perf_impact`, `recommended_action`, `validation_needed`
- [x] Full-repo surfaces inventoried and explicitly named
- [x] Baseline command output captured for pytest collection and unused-code scanning
- [x] Confirmed stale/generated artifacts listed with evidence
- [x] High-confidence suspects separated from confirmed stale items
- [x] Performance opportunities documented separately and ranked
- [x] `TASK-049` updated to depend on this audit
- [x] Sprint planning docs updated so cleanup follows audit output
- [x] No runtime code deleted or rewritten as part of the audit pass

---

## Implementation Plan

### Phase 1: Structural Inventory and Reference Tracing
- Build an inventory of executable, auxiliary, archival, and generated surfaces.
- Use `git ls-files`, `rg`, Flask route/template tracing, `pytest.ini`, and `webapp/build.js` to determine what is active vs. unreferenced.
- Cross-check dependency manifests against actual imports/usages.

### Phase 2: Evidence Scoring and Finding Classification
- Record each candidate with evidence, risk, and validation needs.
- Separate:
  - confirmed stale/generated artifacts
  - orphaned debug/test surfaces
  - stale tests / infrastructure drift
  - dependency drift
  - legacy-but-active files

### Phase 3: Performance Opportunity Review
- Use existing `webapp/ts_performance.py` instrumentation and static hotspot analysis.
- Focus on startup cost, import-time side effects, bundle size, rendering scale, cache hygiene, dependency footprint, and console/log noise.

### Phase 4: Handoff
- Update Sprint tracking artifacts.
- Map low-risk removals to `TASK-049`.
- Map performance follow-ups to `ISSUE-003` and related tasks instead of mixing them into one cleanup batch.

---

## Implementation Log

### TYPE C - FULL REPO AUDIT BASELINE AND REPORT CREATION - 2026-03-23
**Objective**: Create the audit task, run the first evidence pass, and publish a master findings report with immediate stale-code and performance-opportunity results.

**Context**: Existing Sprint 04 planning had `TASK-049` as direct legacy cleanup. A dedicated discovery phase was missing even though the repo now contains runtime code, debug surfaces, notebooks, generated artifacts, and multiple historical refactor remnants.

**Decision**: Create `TASK-050` as the analysis gate and treat `TASK-049` as the downstream cleanup/remediation task. Use non-mutating discovery commands and document evidence before any deletion recommendations.

**Execution**:
- Reviewed `current-tasks.md`, `SPRINT-04-PLAN.md`, `pytest.ini`, `webapp/build.js`, Flask route/template usage, and existing analysis/task documents.
- Ran baseline inventory/reference tracing commands:
  - `git ls-files`
  - `rg` reference searches for backup artifacts, templates, test surfaces, and dependency usage
  - `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m pytest --collect-only tests -q`
  - `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m flake8 webapp tests --select=F401,F841 --statistics --jobs 1`
- Captured concrete evidence:
  - `webapp/tests/` contains 20 tracked files but is not in pytest collection scope
  - 25 tracked cache files exist under `webapp/cache/maps/*.cache`
  - tracked generated artifacts include `.coverage` and `.DS_Store`
  - `webapp/templates/towerscout_backup.html` is not rendered by current Flask route flow
  - `tests/unit/test_event_system.py` no longer matches `webapp/ts_events.py`
  - `tests/integration/test_end_to_end.py` fails collection because importing `towerscout` eagerly initializes models
  - major size hotspots are `webapp/js/towerscout.js` (10,560 lines), `webapp/js/src/towerscout.js` (4,239 lines), and `webapp/towerscout.py` (1,979 lines)
- Created the master analysis report and updated Sprint/task planning artifacts.

**Output**:
- New task file created for full-repo audit
- Master report created with stale-code findings, baseline command outcomes, and performance opportunities
- Sprint tracking updated so cleanup depends on audit output

**Validation**:
- Pytest collection baseline: 148 tests collected, 2 collection errors
- Flake8 baseline: 105 `F401` unused-import findings, 14 `F841` unused-local findings
- Reference searches confirm several tracked backup/generated artifacts are not part of active runtime paths

**Next**:
- Use `TASK-049` for removal batches only after validating items marked safe in the audit report
- Feed performance-related findings into `ISSUE-003` and `TASK-048`

---

## Validation Results

### Baseline Validation Summary

**Pytest Collection**:
- Command: `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m pytest --collect-only tests -q`
- Result: 148 tests collected, 2 collection errors
- Errors:
  - `tests/integration/test_end_to_end.py` imports `towerscout` and triggers missing-model initialization
  - `tests/unit/test_event_system.py` imports symbols that no longer exist in `ts_events.py`

**Unused Code Scan**:
- Command: `C:\Users\bg90\TowerScout\.venv\Scripts\python.exe -m flake8 webapp tests --select=F401,F841 --statistics --jobs 1`
- Result:
  - 105 `F401` unused imports
  - 14 `F841` unused locals

### Status

**Current Task Status**: COMPLETED  
**Audit Report Status**: Full-repo findings published  
**Follow-on Work**: Cleanup/remediation deferred to `TASK-049` and related tasks
