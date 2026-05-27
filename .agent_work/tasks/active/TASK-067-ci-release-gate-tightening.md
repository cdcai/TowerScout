# TASK-067: CI Release Gate Tightening

**Status**: VALIDATED - ready for focused PR review
**Priority**: HIGH
**Type**: C (CI / Release Engineering / Test Reliability)
**Estimated Effort**: 0.5-1 day (4-8 hours)
**Target Sprint**: Sprint 06 V1 RC1

## Objective

Tighten the release validation baseline where `TASK-066` exposed avoidable fragility: broad pytest commands could hang without useful diagnostics, Flask route tests could import real local runtime config, and stale legacy agent guidance could confuse future work.

## Requirements (EARS Notation)

**R-067-001**: WHEN pytest runs locally or in CI, THE TEST SUITE SHALL have timeout safeguards so a collection-time or test-time hang fails with diagnostics instead of waiting indefinitely.

**R-067-002**: WHEN Flask route tests import the TowerScout app, THE TEST BOOTSTRAP SHALL isolate config, logs, cache, uploads, temporary session paths, Torch cache, and provider key values from the developer's real local runtime.

**R-067-003**: WHEN CI workflow timeouts are added, THE WORKFLOW SHALL keep currently advisory checks advisory unless this task explicitly promotes a gate.

**R-067-004**: WHEN legacy agent guidance is obsolete, THE REPOSITORY SHALL remove or archive it after preserving current-value guidance in `.github/copilot-instructions.md` and `.github/instructions/`.

**R-067-005**: WHEN validation completes, THE TASK SHALL record which checks passed and which release-gate ratchets remain follow-up work.

## Acceptance Criteria

- [x] Pytest timeout dependency and configuration are present.
- [x] GitHub Actions jobs or long-running test steps have explicit timeout limits.
- [x] Flask app imports during unit tests use isolated test runtime paths and fake provider keys.
- [x] Focused Flask route tests complete without relying on Docker Desktop, Podman, or local provider config.
- [x] Stale `AGENTS.md/` guidance is removed or archived after `.github` guidance is current.
- [x] `.agent_work` and diff validation pass.
- [x] Follow-up release-gate work remains documented if not implemented here.

## Dependencies

- `TASK-066`: release-candidate validation evidence and route-test isolation finding.
- `TASK-068`: adjacent Windows/script portability follow-up if deeper Windows-only test harness work remains.
- `.github/workflows/ci.yml`: current CI baseline.
- `tests/unit/test_flask_routes.py`: route-test smoke and contract coverage.

## Implementation Plan

1. Add pytest timeout dependency/configuration and CI timeout limits.
2. Add test-runtime path overrides before app import.
3. Extend runtime path helpers where test isolation needs supported overrides.
4. Run focused Flask route and runtime path tests.
5. Remove stale `AGENTS.md/` guidance after confirming `.github` guidance is authoritative.
6. Update task and sprint documentation.
7. Validate and prepare a focused PR.

---

## Implementation Log

### 2026-05-27 - Task Started
**Objective**: Address the `TASK-066` test-harness confidence gap before broad `TASK-073` pilot prep.
**Context**: `TASK-066` package validation passed with boundaries, but broad pytest review commands stalled around Flask route-test collection. Review also found stale legacy agent guidance under `AGENTS.md/`.
**Decision**: Keep this task focused on test reliability and guidance cleanup, without promoting broader release-package smoke checks to blocking CI yet.
**Execution**: Created the active task file and began implementing timeout safeguards, runtime path overrides, and legacy guidance removal.
**Output**: Task is active and scoped.
**Validation**: Pending focused tests.
**Next**: Run route-test validation, update task status, and prepare the PR.

### 2026-05-27 - Focused Reliability Slice Validated
**Objective**: Confirm the timeout and route-test isolation fixes close the `TASK-066` test-harness confidence gap without broad CI policy churn.
**Execution**:
- Added `pytest-timeout` as a dev dependency and configured a 120-second default pytest timeout.
- Added explicit GitHub Actions job and long-running test-step timeouts while keeping historical advisory checks advisory.
- Added pre-import test runtime path overrides for config, logs, cache, temp/session paths, uploads, Torch cache, YOLO config, and fake provider keys.
- Extended runtime path helpers so tests can redirect config/cache/session/temp paths without touching a developer's real local runtime.
- Removed stale legacy `AGENTS.md/` guidance and updated active `.github` / `.agent_work` references so `.github/copilot-instructions.md` and `.github/instructions/` remain authoritative.
**Output**: Focused branch is ready for PR review.
**Validation**: Passed focused route/config/runtime tests and task-work validation; see validation results below.
**Next**: Open PR, review CI, then start `TASK-073` after merge.

---

## Validation Results

### Test Summary
**Test Date**: May 27, 2026
**Test Environment**: Windows local venv, no Docker Desktop or Podman dependency for focused unit validation
**Test Status**: PASSED

### Acceptance Criteria Validation
- [x] Timeout safeguards present - `pytest-timeout` dependency, `pytest.ini` timeout settings, and CI timeout limits are present.
- [x] Route-test runtime isolation present - `tests/conftest.py` sets isolated runtime paths and fake provider keys before Flask app import.
- [x] Focused route tests pass - `tests/unit/test_flask_routes.py` passed without runtime engines or local provider config.
- [x] Legacy guidance cleanup complete - `AGENTS.md/` removed; active guidance points to `.github/copilot-instructions.md` and `.github/instructions/`.
- [x] Task/worktree validation passes - `.agent_work` validator and `git diff --check` passed.
- [x] Syntax-focused lint check passes - `flake8 --jobs=1 --select=E9,F63,F7,F82` passed on touched Python files.

### Issues Identified

- `git diff --check` reported line-ending normalization warnings for `pytest.ini` and `requirements-dev.txt`; no whitespace errors were found.
- `rg` can hit access-denied generated directories under `.agent_work/pytest-temp`; future repository-wide searches should exclude generated pytest runtime directories.
- Local Black validation is blocked by the installed Python `3.12.5` safety guard; CI uses the configured Python matrix and Black remains advisory.

### Remediation Actions

- Installed and verified `pytest-timeout` locally before rerunning focused tests.
- Excluded generated pytest runtime directories during stale-reference searches.
- Reran flake8 single-process because default multiprocessing hit a Windows permission error in the local sandbox.

### Sign-off

Implementation and focused validation are complete. PR review and CI remain the merge gate.
