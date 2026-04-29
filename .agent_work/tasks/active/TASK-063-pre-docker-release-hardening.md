# TASK-063: Pre-Docker Release Hardening And CI Reproducibility Gate

**Status**: COMPLETED
**Priority**: CRITICAL  
**Type**: C (Security / Release Engineering / Deployment Readiness)  
**Estimated Effort**: 1-2 days (8-16 hours)

## Objective

Resolve or owner-approve the April 24 senior-review release-hardening findings and the April 28 plan-sufficiency execution gates before `TASK-025` turns the current host runtime into the Docker baseline.

This task exists because the senior reviews found release-quality risks that are adjacent to Docker but should not be folded into Docker implementation itself. The latest sufficiency review confirmed that the plan is sound, but only if the v1 release boundary, CI/security posture, persistence expectations, support diagnostics, and unsupported environments are explicit before Docker work proceeds.

## Requirements (EARS Notation)

**R-063-001**: WHEN TowerScout prepares for Docker baseline work, THE SYSTEM SHALL use dependency versions that have been reviewed for currently flagged security findings.

**R-063-002**: WHEN frontend dependencies are installed for validation or release packaging, THE PROJECT SHALL have an explicit lockfile/reproducibility policy reflected in tracked files or documented as a deliberate exception.

**R-063-003**: WHEN CI security scanning runs, THE WORKFLOW SHALL NOT reference `aquasecurity/trivy-action` through a floating branch such as `@master`.

**R-063-004**: WHEN CI results are used to support release readiness, THE PROJECT SHALL identify which checks are advisory and which checks must block release candidates.

**R-063-005**: WHEN the application is packaged for local users, THE SYSTEM SHALL either disable `.pt` model upload or clearly gate/document it as a trusted local-admin/developer workflow.

**R-063-006**: WHEN TLS verification is disabled through `TOWERSCOUT_ALLOW_INSECURE_TLS`, THE SYSTEM SHALL treat that mode as an explicit local troubleshooting exception, not a normal supported runtime default.

**R-063-007**: WHEN performance metrics are written or read, THE SYSTEM SHALL use one authoritative file-format contract for each performance log file.

**R-063-008**: WHEN third-party GitHub Actions are used in release-relevant workflows, THE WORKFLOW SHALL pin them to reviewed immutable references or record owner-approved explicit risk acceptance.

**R-063-009**: WHEN workflow permissions are evaluated for release readiness, THE PROJECT SHALL document whether permissions are minimal enough for the current CI jobs or record follow-up hardening.

**R-063-010**: WHEN the active YOLO runtime is audited before Docker, THE PROJECT SHALL prove that no supported runtime path falls back to Torch Hub, GitHub bootstrap, or stale legacy inference behavior.

**R-063-011**: WHEN v1 local release scope is documented, THE PROJECT SHALL state the supported and unsupported environments before Docker packaging begins.

**R-063-012**: WHEN support readiness is evaluated, THE PROJECT SHALL define the minimum v1 support contract for log locations, asset/version visibility, startup diagnostics, and sensitive-data handling.

**R-063-013**: WHEN third-party GitHub Actions are pinned to immutable references, THE PROJECT SHALL define a recurring review/update cadence so pinned actions do not silently drift out of maintenance.

**R-063-014**: WHEN provider API keys are documented for v1, THE PROJECT SHALL describe provider-side restriction guidance, including separation of browser-exposed and server-side key usage where applicable.

**R-063-015**: WHEN upload surfaces remain enabled, THE PROJECT SHALL align Flask upload limits, Waitress request-body limits, and the `.pt` upload support boundary.

**R-063-016**: WHEN dependency repeatability is documented, THE PROJECT SHALL decide the immediate Python, frontend, and runtime-asset repeatability policy rather than relying only on top-level version pins.

**R-063-017**: WHEN an unresolved pre-Docker finding is risk-accepted, THE PROJECT SHALL document the issue, deferral rationale, expected user/release impact, mitigation or workaround, review timing, follow-up owner/task, and owner approval before `TASK-025` starts.

## Acceptance Criteria

- [x] `webapp/requirements.txt` has been reviewed and patched for the currently flagged Pillow/Requests findings, or an explicit risk-acceptance note exists.
- [x] `package-lock.json` is either committed and used as the frontend install contract, or the repo documents why it remains untracked and what replaces it.
- [x] `.github/workflows/ci.yml` no longer uses `aquasecurity/trivy-action@master`.
- [x] Release-relevant third-party GitHub Actions are pinned to reviewed immutable references, or each exception has owner-approved explicit risk acceptance.
- [x] A recurring review/update cadence exists for pinned third-party GitHub Actions.
- [x] Workflow permissions have been reviewed and documented for release readiness.
- [x] The CI workflow has a documented release-candidate interpretation for advisory versus blocking checks.
- [x] Dependency repeatability policy is documented for Python dependencies, frontend dependencies, and large runtime assets.
- [x] Residual YOLO/Torch Hub audit proves no supported runtime path falls back to Torch Hub, GitHub bootstrap, or stale legacy inference behavior.
- [x] The `.pt` model upload route has a documented first-release support boundary and, if needed, a code-side gate or disable path.
- [x] Flask upload limits, Waitress request-body limits, and `.pt` upload support boundary are aligned or owner-approved as a follow-up risk.
- [x] Provider API key restriction guidance is documented for Google and Azure, including client/server separation where applicable.
- [x] Insecure TLS flags remain off by default and are documented as local troubleshooting exceptions.
- [x] `performance.log` is no longer both a structured logging target and a CSV metrics target.
- [x] V1 supported and unsupported environments are documented for release planning.
- [x] Minimum support diagnostics contract is documented for log locations, startup failures, asset/version visibility, and sensitive-data handling.
- [x] Any unresolved `TASK-063` item has an owner-approved risk note covering impact, mitigation, follow-up timing, and owning task before `TASK-025` starts.
- [x] Focused validation is recorded in this task file before `TASK-025` starts.

## Dependencies

- `TASK-052`: Current integration smoke-test baseline
- `TASK-062`: Pre-Docker runtime cleanup and YOLO loader hardening

## Implementation Plan

1. Audit the current repo state for the review findings: dependency versions, frontend lockfile policy, dependency repeatability, CI action pinning, pinned-action review cadence, workflow permissions, advisory gates, residual YOLO/Torch Hub behavior, model upload and upload-size limits, provider-key restriction guidance, TLS bypass, performance-log file contract, v1 support boundary, and support diagnostics.
2. Apply minimal fixes where the fix is low risk and clearly bounded.
3. For any item that cannot be fixed safely before Docker work, document the owner-approved risk acceptance, impact, mitigation, follow-up timing, and follow-up task owner.
4. Run focused validation for touched areas.
5. Update `current-tasks.md` / Sprint 05 planning if any acceptance item changes Docker scope or timing.

---

## Implementation Log

### 2026-04-28 - Task Creation
**Objective**: Add a bounded pre-Docker release-hardening gate based on the second senior-engineer review.  
**Context**: The review agreed with Docker-first sequencing but identified release-quality risks around dependency freshness, frontend reproducibility, CI action pinning, advisory CI gates, `.pt` model upload, TLS bypass behavior, and performance-log file ownership.  
**Decision**: Track these as `TASK-063` before `TASK-025` so Docker remains focused on container build/run behavior while release-hardening risks are handled deliberately.  
**Execution**: Created this task file and linked it from `current-tasks.md`, `task-backlog.md`, and the Sprint 05 plan.  
**Output**: `TASK-063` now gates Docker start.  
**Validation**: Planning artifact review pending.  
**Next**: Execute the audit/fix pass and record validation evidence here.

### 2026-04-28 - Sufficiency Review Gate Expansion
**Objective**: Incorporate the April 28 plan sufficiency assessment into the pre-Docker gate.  
**Context**: The sufficiency assessment concluded that the plan is strong enough to proceed if v1 scope stays narrow and operational contracts are explicit before implementation hardens into release artifacts.  
**Decision**: Expand `TASK-063` to include third-party action pinning beyond Trivy, workflow permission review, residual YOLO/Torch Hub audit, v1 supported/unsupported environment documentation, and minimum support diagnostics.  
**Execution**: Updated requirements, acceptance criteria, and implementation plan in this task file.  
**Output**: `TASK-063` now captures the release, security, and support gates that must clear before Docker starts.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Execute the audit/fix pass and record concrete validation evidence here.

### 2026-04-28 - Final Path-Forward Review Expansion
**Objective**: Capture the final review's release-engineering and supportability constraints.  
**Context**: The reviewer agreed with the roadmap but identified four additional pre-Docker contract details: pinned-action review cadence, upload-limit alignment, provider-key restriction guidance, and stronger dependency repeatability decisions.  
**Decision**: Keep these in `TASK-063` because they are release/security/support gates, not Docker implementation.  
**Execution**: Added requirements and acceptance criteria for action update cadence, provider-key restrictions, upload limit alignment, and dependency repeatability.  
**Output**: `TASK-063` now reflects the final review's release gate refinements.  
**Validation**: `.agent_work` validation passed after synchronized planning updates.  
**Next**: Execute the audit/fix pass and record concrete validation evidence here.

### 2026-04-28 - Owner Approval Rule
**Objective**: Make pre-Docker risk acceptance governance explicit.  
**Context**: The project owner confirmed they will approve risk acceptances when given enough context to understand the decision and consequences.  
**Decision**: Require owner-approved risk notes for unresolved `TASK-063` findings before Docker starts.  
**Execution**: Added an EARS requirement, acceptance criterion, and implementation-plan language requiring issue, deferral rationale, impact, mitigation, review timing, follow-up owner/task, and owner approval.  
**Output**: `TASK-063` can no longer proceed through implicit risk acceptance.  
**Validation**: Pending `.agent_work` validation after synchronized planning updates.  
**Next**: Apply this rule during the audit/fix pass.

### 2026-04-29 - Task Start And Audit Kickoff
**Objective**: Start the pre-Docker release-hardening gate and begin the evidence-backed audit pass.
**Context**: `TASK-052` and `TASK-062` are complete with passing validation, the active branch is `feature/task-063-pre-docker-release-hardening`, and `.agent_work` structure validation passes.
**Decision**: Mark `TASK-063` in progress and begin with a full acceptance-criteria audit before applying bounded fixes.
**Execution**: Updated this task file and `.agent_work/current-tasks.md` from `NOT_STARTED` to `IN_PROGRESS`; confirmed required planning prerequisites and validation state.
**Output**: `TASK-063` is now the active Sprint 05 release-hardening task.
**Validation**: `python .agent_work\scripts\validate_agent_work.py` passed before task start.
**Next**: Audit dependency versions, lockfile policy, CI action pinning/permissions, upload/TLS/performance surfaces, provider-key guidance, release boundary, support diagnostics, and residual YOLO/Torch Hub behavior.

### 2026-04-29 - Audit And First Hardening Pass
**Objective**: Resolve the concrete release-hardening findings that can be fixed before Docker without broad redesign.
**Context**: The audit found `Pillow==10.3.0`, `Requests==2.32.2`, ignored local `package-lock.json`, floating GitHub Actions refs, `aquasecurity/trivy-action@master`, no explicit workflow permissions, model upload exposed as a normal route, Flask/Waitress upload limits not aligned, insecure TLS lacking release-boundary documentation, and structured performance events sharing `performance.log` with CSV metrics.
**Decision**: Apply bounded fixes and document policy-only contracts in one active guide instead of expanding `TASK-063` into Docker implementation or frontend build modernization.
**Execution**:
- patched `webapp/requirements.txt` to `Pillow==12.1.1` and `Requests==2.32.4`
- updated YOLO runtime dependency preflight and related tests to match patched minimums
- unignored `package-lock.json`, updated Node engine policy to `>=18.0.0`, and aligned the lockfile root package engine
- pinned release-relevant GitHub Actions in `.github/workflows/ci.yml` to immutable SHAs and added minimal workflow permissions
- disabled `.pt`/`.pth` browser model upload by default behind `TOWERSCOUT_ENABLE_MODEL_UPLOAD`
- aligned Flask `MAX_CONTENT_LENGTH`, Waitress `max_request_body_size`, and validator upload size through `TOWERSCOUT_MAX_REQUEST_BODY_BYTES`
- moved structured performance-event logging from `webapp/logs/performance.log` to `webapp/logs/performance_events.jsonl`
- added `.agent_work/context/guides/Pre-Docker-Release-Hardening-Contract.md`
**Output**: Dependency, lockfile, CI, upload, TLS, provider-key, metrics-log, v1 boundary, and support diagnostics contracts now have code or documentation coverage.
**Validation**: Focused validation passed; see Validation Results.
**Next**: Review diff, include `package-lock.json` in the eventual commit, and run broader CI/full test coverage if required before marking the task complete in the sprint tracker.

### 2026-04-29 - Broader Unit Validation And Closeout
**Objective**: Validate the release-hardening changes against the broader unit baseline before closing `TASK-063`.
**Context**: Focused validation passed for touched upload, dependency, CI, performance-log, and YOLO-local-loader surfaces. The remaining recommended closeout gate was the broader unit suite.
**Decision**: Treat the task as complete after the full unit suite passed because all `TASK-063` acceptance criteria are satisfied and no unresolved `TASK-063` finding requires owner risk acceptance.
**Execution**: Ran `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider`.
**Output**: `65 passed, 74 skipped, 17 warnings, 5 subtests passed`.
**Validation**: PASS. Warnings are existing UTC deprecation warnings in `ts_config.py` and `ts_errors.py`; no failures or new release-hardening blockers were identified.
**Next**: Commit the completed `TASK-063` change set, including the newly tracked `package-lock.json`, then proceed to `TASK-064`.

### 2026-04-29 - PR Code Scanning Follow-Up
**Objective**: Resolve the GitHub Advanced Security / Trivy findings reported on PR #5.
**Context**: Code scanning flagged `Pillow==12.1.1` for `CVE-2026-40192` with fixed version `12.2.0`, and `Requests==2.32.4` for `CVE-2026-25645` with fixed version `2.33.0`.
**Decision**: Patch both runtime pins and keep the YOLO runtime dependency preflight aligned with the stricter security baseline.
**Execution**: Updated `webapp/requirements.txt`, `webapp/ts_yolov5.py`, and `tests/unit/test_yolov5_local_loader.py` to `Pillow==12.2.0` and `Requests==2.33.0`.
**Output**: PR #5 now targets the fixed versions requested by code scanning.
**Validation**: Local dependency smoke, `pip check`, YOLO local-loader tests, and full unit suite passed; see Validation Results.
**Next**: Push the follow-up commit to PR #5 and confirm code scanning clears.

### 2026-04-29 - Review Follow-Up For Requests Pin And Model Asset Contract
**Objective**: Address reviewer feedback on the Requests exact pin and clarify how disabled browser model upload relates to Docker model-weight packaging.
**Context**: The reviewer agreed the PR was approvable, noted that `Requests==2.33.0` clears the reviewed CVE but `2.33.1` is already the latest PyPI patch release, and asked that model upload not be confused with the normal model-weight update path.
**Decision**: Bump Requests to the latest reviewed patch release and make the release contract explicit that model updates should use the persistent model asset directory or Docker volume rather than browser upload.
**Execution**: Updated `webapp/requirements.txt`, `webapp/ts_yolov5.py`, `tests/unit/test_yolov5_local_loader.py`, and `.agent_work/context/guides/Pre-Docker-Release-Hardening-Contract.md`.
**Output**: The PR now uses `Requests==2.33.1`, keeps the YOLO runtime dependency preflight aligned, and documents that `TASK-025` still owns the initial model-weight delivery and persistent asset strategy.
**Validation**: Local dependency smoke, `pip check`, YOLO local-loader tests, full unit suite, `.agent_work` validation, and diff checks passed; see Validation Results.
**Next**: Push the review follow-up to PR #5 and mark the PR ready for review once CI remains green.

---

## Validation Results

### Test Summary
**Test Date**: 2026-04-29
**Test Environment**: Windows local workspace, `.venv` Python 3.12.5
**Test Status**: PASS for focused and broader unit `TASK-063` validation

### Acceptance Criteria Validation
- [x] **Dependency findings**: PASS - `webapp/requirements.txt` now pins `Pillow==12.2.0` and `Requests==2.33.1`; local venv dependency smoke reports `Pillow 12.2.0` and `Requests 2.33.1`.
- [x] **Frontend lockfile policy**: PASS - `package-lock.json` is present and no longer ignored; `package.json` and lockfile root package require Node `>=18.0.0`.
- [x] **CI action pinning**: PASS - `rg -n "uses: [^\s]+@(master|main|v[0-9]+|[0-9]+\.[0-9])" .github\workflows` returned no matches.
- [x] **Trivy floating ref**: PASS - `aquasecurity/trivy-action@master` replaced with immutable SHA `57a97c7e7821a5776cebc9bb87c984fa69cba8f1` reviewed from `v0.35.0`.
- [x] **Workflow permissions**: PASS - workflow default is `contents: read`; security job adds `security-events: write`.
- [x] **CI gate interpretation and action cadence**: PASS - documented in `Pre-Docker-Release-Hardening-Contract.md`.
- [x] **Dependency repeatability**: PASS - documented for Python, frontend, and runtime assets in `Pre-Docker-Release-Hardening-Contract.md`.
- [x] **YOLO/Torch Hub audit**: PASS - active loader remains `ts_yolov5_local.load_local_yolov5_model`; `tests\unit\test_yolov5_local_loader.py` passed `6 passed`.
- [x] **Model upload and upload limits**: PASS - model upload disabled by default behind `TOWERSCOUT_ENABLE_MODEL_UPLOAD`; request-body limits align through `TOWERSCOUT_MAX_REQUEST_BODY_BYTES`; focused route tests passed.
- [x] **Provider keys and insecure TLS**: PASS - provider-key restrictions and TLS troubleshooting boundary documented in `Pre-Docker-Release-Hardening-Contract.md` and `.env.example`.
- [x] **Performance log contract**: PASS - CSV metrics keep `performance.log`; structured events now use `performance_events.jsonl`; performance-summary tests passed.
- [x] **V1 release boundary and support diagnostics**: PASS - documented in `Pre-Docker-Release-Hardening-Contract.md`.
- [x] **Risk acceptance**: PASS - no unresolved `TASK-063` finding was left for owner risk acceptance in this pass.

### Test Results
- `python .agent_work\scripts\validate_agent_work.py` - PASS
- `.venv\Scripts\python.exe -m pip install Pillow==12.1.1 Requests==2.32.4` - PASS after approved network access
- `.venv\Scripts\python.exe -c "from importlib import metadata; ..."` - PASS, reported `Pillow 12.1.1` and `Requests 2.32.4`
- `.venv\Scripts\python.exe -m pip check` - PASS, `No broken requirements found.`
- `.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py::test_uploadmodel_saves_valid_model_into_runtime_directory tests\unit\test_flask_routes.py::test_uploadmodel_disabled_by_default_blocks_model_upload tests\unit\test_config.py::test_get_recent_performance_stats_uses_existing_log tests\unit\test_config.py::test_get_recent_performance_stats_supports_headerless_log_format tests\unit\test_yolov5_local_loader.py::test_validate_runtime_dependencies_reports_missing_required_local_loader_imports -q -p no:cacheprovider` - PASS, `5 passed`
- `.venv\Scripts\python.exe -m pytest tests\unit\test_yolov5_local_loader.py -q -p no:cacheprovider` - PASS, `6 passed`
- `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider` - PASS, `65 passed, 74 skipped, 17 warnings, 5 subtests passed`
- `.venv\Scripts\python.exe -m pip install Pillow==12.2.0 Requests==2.33.0` - PASS after approved network access
- `.venv\Scripts\python.exe -c "from importlib import metadata; ..."` - PASS after PR code-scanning fix, reported `Pillow 12.2.0` and `Requests 2.33.0`
- `.venv\Scripts\python.exe -m pip check` - PASS after PR code-scanning fix, `No broken requirements found.`
- `.venv\Scripts\python.exe -m pytest tests\unit\test_yolov5_local_loader.py -q -p no:cacheprovider` - PASS after PR code-scanning fix, `6 passed`
- `.venv\Scripts\python.exe -m pytest tests\unit -q -p no:cacheprovider` - PASS after PR code-scanning fix, `65 passed, 74 skipped, 17 warnings, 5 subtests passed`
- `.venv\Scripts\python.exe -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml', encoding='utf-8')); print('ci yaml parse ok')"` - PASS
- `node -e "const p=require('./package-lock.json'); console.log(p.packages[''].engines.node); console.log(p.packages['node_modules/@puppeteer/browsers'].engines.node)"` - PASS, reported `>=18.0.0` and `>=18`
- `node webapp\build.js` - PASS; generated bundle had timestamp-only drift, reverted to keep the diff scoped
- `git check-ignore -q package-lock.json` - PASS, reported not ignored
- `git diff --check` - PASS with only a line-ending warning for `webapp/.env.example`

### Issues Identified
- `package-lock.json` is newly unignored and still untracked until the eventual commit includes it.
- `webapp/.env.example` reports a CRLF-to-LF warning from Git after the edit; content diff is limited to the intended settings and final newline.
- Unit suite warnings remain for existing `datetime.utcnow()` deprecations in `ts_config.py` and `ts_errors.py`; these are not `TASK-063` blockers.

### Remediation Actions
- `TASK-063` is complete. Include `package-lock.json` in the eventual commit and carry remaining pre-Docker gating into `TASK-064`.
