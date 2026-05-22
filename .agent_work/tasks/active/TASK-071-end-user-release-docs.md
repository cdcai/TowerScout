# TASK-071: End-User Release Package Documentation

**Status**: COMPLETED - focused validation passed; ready for TASK-066
**Priority**: CRITICAL  
**Type**: B/C (Documentation / User Enablement)  
**Estimated Effort**: 1-2 days (8-16 hours)  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Produce package-based end-user documentation for the TowerScout V1 RC1 `agpl-yolo` release track so a non-technical Windows pilot user can download the release package, place/import required assets, start TowerScout, complete first-run setup, find source/license notices, validate success, understand the main TowerScout workflow, and report problems without project tribal knowledge.

This task should replace or clearly distinguish older source/Conda tester guidance from the V1 RC1 package path. It should also make package-local help discoverable from the running app's Settings Resource Links without weakening the CPU-safe default launch or the GPU validation boundary established by `TASK-075`.

## Requirements (EARS Notation)

**R-071-001**: WHEN a pilot user receives the V1 RC1 release package, THE DOCUMENTATION SHALL explain what files to download and where to extract them.

**R-071-002**: WHEN required assets are supplied separately, THE DOCUMENTATION SHALL explain the asset bundle layout, placement, import command, and verification expectations defined by `TASK-072`.

**R-071-003**: WHEN a user starts TowerScout for the first time, THE DOCUMENTATION SHALL explain how to run `start.bat`, what readiness states mean, and when the browser should open.

**R-071-004**: WHEN no provider key is configured, THE DOCUMENTATION SHALL explain how to use Setup Wizard or Settings to configure at least one supported map provider.

**R-071-005**: WHEN launch or setup fails, THE DOCUMENTATION SHALL tell users what status/log/preflight evidence to collect and what information not to share.

**R-071-006**: WHEN a user's environment includes Docker, Podman, Compose provider, TLS inspection, restricted network, or asset issues, THE DOCUMENTATION SHALL route the user to the appropriate supported V1 RC1 guidance or clearly state the limitation.

**R-071-007**: WHEN older source-install tester guides remain in the repo, THE DOCUMENTATION SHALL make clear whether they are legacy/source-install guidance and not the preferred V1 RC1 pilot package path.

**R-071-008**: WHEN the package docs describe the YOLO-enabled release, THE DOCUMENTATION SHALL state that the package/image is distributed with AGPL-3.0 obligations and is not Apache-2.0-only.

**R-071-009**: WHEN users need source or license information, THE DOCUMENTATION SHALL point to the package compliance files and the running app `/license` page.

**R-071-010**: WHEN the docs mention GPU/CUDA behavior, THE DOCUMENTATION SHALL keep the default V1 RC1 launch path CPU-safe, describe `-Gpu off|auto|on` as optional Docker-first behavior, and state that NVIDIA host validation is required before making broad GPU support claims.

**R-071-011**: WHEN a user opens Settings Resource Links, THE APPLICATION SHALL expose package-local Project Overview, User Guide, and Source/licenses links rather than placeholder documentation links.

**R-071-012**: WHEN a user opens Settings Resource Links, THE APPLICATION SHALL link Video Guides to `https://www.youtube.com/@thaddeussegura8452/videos` and TowerScout Research Article to `https://www.sciencedirect.com/science/article/pii/S2589750024000943?via%3Dihub`.

**R-071-013**: WHEN a user needs workflow help, THE DOCUMENTATION SHALL include a general User Guide covering provider selection, search area definition, tile estimate, detection, review, manual corrections, CSV/KML export, dataset export, and dataset restore.

**R-071-014**: WHEN the User Guide explains drawing workflows, THE DOCUMENTATION SHALL distinguish custom search-area polygons from manual tower detections and SHALL document provider-specific polygon completion behavior.

**R-071-015**: WHEN setup docs explain provider keys, THE DOCUMENTATION SHALL state that one valid Google Maps or Azure Maps key is enough to start, Google keys must support the app's Maps JavaScript, Places/autocomplete, Static Maps imagery, and Geocoding usage, and Azure Maps subscription keys must support the app's Web SDK, imagery, search, and geocoding usage.

**R-071-016**: WHEN setup docs explain provider key safety, THE DOCUMENTATION SHALL state that browser map SDK keys are client-visible, V1 RC1 assumes site/user-owned restricted keys, unrestricted shared project keys are unsupported, and users/sites should configure provider-side restrictions, quotas, billing alerts, monitoring, and rotation.

**R-071-017**: WHEN package-local Markdown docs are updated for user-facing setup, workflow, support, or prerequisite guidance, THE DOCUMENTATION SHALL keep the corresponding HTML docs used by Settings Resource Links synchronized or explicitly document why no HTML counterpart is needed.

## Acceptance Criteria

- [x] A one-page V1 RC1 quick start exists for Windows 11 AMD64 pilot users.
- [x] A fuller V1 RC1 package guide exists for first-line support and testers.
- [x] The docs explain release package download/extraction, asset placement/import, launch, first-run setup, validation, stop/restart, troubleshooting, and issue reporting.
- [x] The docs include sensitive-data handling guidance for `.env`, provider keys, logs, cached provider responses, uploaded files, and exported datasets.
- [x] The docs reflect the `TASK-072` asset bundle contract.
- [x] The docs reflect the `TASK-069` AGPL-compliant YOLO release posture.
- [x] The docs tell users where to find `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `MODEL_LICENSES.md`, `DATA_LICENSES.md`, `PROVIDER_TERMS.md`, `SOURCE.txt`, `SBOM.txt`, and `release-manifest.v1.json`.
- [x] The docs reflect current Podman/Docker support language from `TASK-065`.
- [x] The docs state the V1 RC1 support boundary, including CPU baseline and supported Windows target.
- [x] The docs reflect `TASK-075` GPU language: default CPU-safe launch, optional Docker GPU overlay, no validated Podman GPU claim, and required readiness/status evidence.
- [x] Older source/Conda testing guides are marked or linked in a way that avoids confusing pilot package users.
- [x] A package-local Project Overview exists and is reachable from Settings Resource Links.
- [x] A general User Guide exists and covers end-to-end workflow, custom search areas, manual tower detections, provider-specific drawing completion, export, and restore.
- [x] Setup docs include provider API capability guidance and the provider-key ownership/restriction policy.
- [x] Settings Resource Links include Project Overview, User Guide, Source/licenses, Video Guides, and TowerScout Research Article without placeholder wording.
- [x] Release package and runtime image packaging include any package-local docs needed by Resource Links.
- [x] HTML docs used by Settings Resource Links include the same user-facing prerequisite/setup updates as the Markdown docs.
- [x] `TASK-066` can use these docs as the only user-facing instructions for clean-machine validation.

## Dependencies

- `TASK-069`: AGPL-compliant YOLO release posture and compliance payload.
- `TASK-072`: release asset bundle contract.
- `TASK-065`: release support language and runtime support caveats.
- `TASK-075`: single GPU-capable package implementation, including CPU-safe default launch, optional Docker GPU overlay, and GPU validation boundaries.
- `docs/oci-quick-start.md`: current OCI quick-start baseline.
- `docs/oci-runtime-contract.md`: current runtime contract.
- `docs/release-asset-bundle-contract.md`: `TASK-072` asset bundle contract.
- `webapp/templates/towerscout.html`: current Settings Resource Links and main-page source/license link location.
- `webapp/towerscout.py`: current `/license` route and any package-local documentation route needed for Resource Links.
- `scripts/package-release.ps1` and `Dockerfile`: release package/image inclusion points for package-local docs.
- `.agent_work/context/guides/TowerScout_User_Testing_Guide.txt`: older source/venv tester guide to reconcile or label.
- `.agent_work/context/guides/TowerScout_User_Testing_Guide_Windows_Miniconda.txt`: older source/Conda tester guide to reconcile or label.

## Implementation Plan

1. Review existing OCI docs and older user-testing guides.
2. Decide where V1 RC1 package docs should live, favoring `docs/` for release-package docs and `.agent_work/context/guides/` for internal tester/support handoff if needed.
3. Draft `docs/v1-rc1-quick-start.md` as the one-page quick start for pilot users.
4. Draft `docs/v1-rc1-package-guide.md` as the full package guide for support/testers.
5. Draft `docs/towerscout-user-guide.md` as the general workflow guide.
6. Draft `docs/project-overview.md` as the package-local project overview.
7. Add styled HTML views for package-local Resource Links where practical.
8. Keep Settings-linked HTML docs synchronized with Markdown docs for user-facing setup, workflow, support, and prerequisite changes.
9. Integrate the `TASK-069` AGPL release posture, `TASK-072` asset bundle contract, `TASK-075` GPU boundary, and provider-key ownership/restriction policy.
10. Add troubleshooting and issue-report guidance aligned with `.agent_work/user-testing/`.
11. Update Settings Resource Links and package/runtime inclusion so package-local docs work from the running app.
12. Mark older source/Conda tester guides as legacy/source-install guidance if they remain.
13. Hand off the docs to `TASK-066` for clean-machine validation.

---

## Implementation Log

### 2026-05-11 - Task Created
**Objective**: Create detailed Sprint 06 task documentation for end-user release package documentation.  
**Context**: Sprint 06 planning identified that broad end-user testing should wait until package docs and asset instructions are clear. Existing tester guides target source/Conda flows and do not represent the V1 RC1 release package path.  
**Decision**: Keep this task focused on package-based user documentation, with source-install guidance treated as legacy/support material unless explicitly needed.  
**Execution**: Created `.agent_work/tasks/active/TASK-071-end-user-release-docs.md` and synchronized the task with `current-tasks.md`.  
**Output**: Task file ready for intake.  
**Validation**: Pending `.agent_work` validation after all Sprint 06 task files are created.  
**Next**: Start documentation inventory and draft the V1 RC1 quick start against the `agpl-yolo` compliance payload and completed asset contract.

### 2026-05-20 - Task-075 GPU Documentation Handoff
**Objective**: Record the GPU/CUDA documentation boundary produced by `TASK-075`.
**Context**: `TASK-075` implemented shared ML device policy, a CUDA-capable proof image path, optional `compose.gpu.yaml`, and launcher `-Gpu off|auto|on` handling. Local validation proved CPU fallback and readiness diagnostics on a non-GPU host, but actual GPU execution still needs NVIDIA Docker Desktop WSL2 validation.
**Decision**: User-facing docs must preserve a CPU-safe default and treat GPU as optional Docker-first behavior until GPU-host validation and fixed-fixture parity/timing evidence are complete.
**Execution**: Added `R-071-010`, an acceptance criterion, and a dependency on `TASK-075`.
**Output**: `TASK-071` is ready to consume the Task-075 GPU support boundary.
**Validation**: Pending full Task-071 documentation implementation.
**Next**: When writing the quick start and full package guide, mirror the `docs/oci-quick-start.md` and `docs/oci-runtime-contract.md` GPU language unless later validation changes it.

### 2026-05-21 - Scope Refresh From Stale Task-071 Branch
**Objective**: Bring the Task-071 task record up to date before implementation on current `main`.
**Context**: The previous `docs/task-071-end-user-release-docs` branch contains useful docs and Resource Links patterns, but it predates `TASK-079` reliability work and `TASK-075` GPU-capable package controls. A direct merge would remove or revert current release-critical files.
**Decision**: Reuse the stale branch as a content donor only. Implement Task-071 selectively on current `main`, preserving the current GPU/package/reliability contracts.
**Execution**: Expanded Task-071 requirements, acceptance criteria, dependencies, and implementation plan to include package-local Project Overview/User Guide docs, styled Resource Links, provider API/key-safety policy language, and current `TASK-075` GPU boundaries.
**Output**: Task-071 is marked `IN_PROGRESS` and aligned with the current release plan.
**Validation**: Pending implementation and focused docs/package tests.
**Next**: Draft the package docs and wire them into the running app and release package assembly.

### 2026-05-21 - Package Docs And Resource Links Implemented
**Objective**: Implement the V1 RC1 package documentation set on current `main`.
**Context**: The old Task-071 branch had useful quick-start, package-guide, user-guide, overview, and Resource Links work, but it was stale relative to `TASK-075` and `TASK-079`.
**Decision**: Recreate the useful docs and integration points selectively while preserving current package flavor metadata, CPU-safe GPU defaults, optional Docker GPU overlay behavior, and current reliability changes.
**Execution**: Added `docs/v1-rc1-quick-start.md`, `docs/v1-rc1-package-guide.md`, `docs/towerscout-user-guide.md`, `docs/project-overview.md`, HTML views for Quick Start/User Guide/Project Overview, and `docs/towerscout-docs.css`. Updated Settings Resource Links, added `/docs/` and `/license.txt`, converted `/license` to a styled HTML page, limited `/docs/` serving to an explicit public-doc allowlist, included docs in the runtime image and release package, and marked older source/Conda guides as legacy source-install guidance.
**Output**: Package-local docs are available from the filesystem, running app Resource Links, release package staging, and runtime image assembly.
**Validation**: Focused validation passed; details recorded below.
**Next**: Use these docs during `TASK-066` clean-machine release-candidate validation and record any user-facing friction as validation findings.

### 2026-05-22 - Prerequisite Software Documentation Pass
**Objective**: Make the user-facing docs explicit enough about what software must be installed on a pilot user's computer before launch.
**Context**: The initial Quick Start mentioned a supported container engine but did not clearly tell non-technical users what prerequisite software they needed, what engine choices were supported, or what development tools were not required.
**Decision**: Add prerequisite guidance to the Quick Start, full Package Guide, Project Overview, User Guide, HTML Quick Start, HTML Project Overview, HTML User Guide, and OCI Quick Start. Keep the guidance conservative: Windows 11 AMD64, PowerShell, browser, outbound internet, disk space, one container engine, provider key, and CPU-safe default launch.
**Execution**: Added explicit prerequisites for Podman and Docker Desktop; documented Podman machine and Compose-provider expectations; clarified that Docker can be selected first when both engines are installed; stated that Git, Python, Conda, Node.js, VS Code, and a source checkout are not required for the package path; and added optional GPU workstation prerequisite language in the Package Guide.
**Output**: The user docs now provide a clearer "before you start" path and better distinguish normal package users from developer/source-install users.
**Validation**: Focused route/package/doc checks passed; details recorded below.
**Next**: Use the updated Quick Start as the primary user instruction during `TASK-066`.

### 2026-05-22 - HTML Documentation Parity Guardrail
**Objective**: Ensure updates to user-facing Markdown docs are also reflected in the HTML docs opened from Settings Resource Links.
**Context**: Settings Resource Links open package-local HTML pages, so users may not read the Markdown source files directly. Prerequisite updates must therefore be present in both formats.
**Decision**: Treat Markdown and Settings-linked HTML docs as paired user-facing surfaces for setup, workflow, prerequisite, and support changes. Add focused route assertions for the latest prerequisite text on the Quick Start, Project Overview, and User Guide HTML pages.
**Execution**: Added `R-071-017`, updated the implementation plan and acceptance criteria, and extended Flask route tests to assert that Settings-linked HTML pages include prerequisite/setup content.
**Output**: Future Task-071-style updates have an explicit parity requirement and test coverage for the current HTML docs.
**Validation**: Focused route/license/package tests passed after adding the parity assertions; `.agent_work` validators and `git diff --check` passed.
**Next**: Continue treating Markdown and Settings-linked HTML docs as paired update surfaces during `TASK-066` and later release-doc work.

### 2026-05-22 - PR16 Reviewer Hardening
**Objective**: Address the remaining low-risk PR16 reviewer recommendations before merge.
**Context**: The updated review still flagged three useful hardening items after the broader documentation pass: align `/docs/` validation and serving path handling, add stronger docs-route regression coverage, and make the Quick Start's admin/support prerequisite boundary more explicit.
**Decision**: Make the route and test changes in PR16 because they are small, directly protect the new docs surface, and do not change the release package contract. Keep larger CI/static-analysis and Markdown-to-HTML generation work in `TASK-066`.
**Execution**: Updated `/docs/<path>` to serve the normalized allowlisted path, added parameterized tests for every public doc plus traversal/odd-separator rejection cases, and added the admin/support stop condition to both Markdown and HTML Quick Start docs.
**Output**: PR16 now includes the reviewer hardening that is appropriate before merge while leaving broader automation/governance items tracked for the release-candidate gate.
**Validation**: Focused route/license/package tests passed with 42 passing tests and the existing `datetime.utcnow()` warning.
**Next**: Merge PR16 after review, then execute `TASK-066` against the package docs and decide which remaining checks should become CI gates.

---

## Validation Results

### Test Summary
**Test Date**: 2026-05-22
**Test Environment**: Windows PowerShell, repo `.venv` Python
**Test Status**: PASSED_WITH_WARNINGS

### Acceptance Criteria Validation
- [x] Quick start created - PASSED
- [x] Full package guide created - PASSED
- [x] Asset contract integrated - PASSED
- [x] AGPL release posture and source/license notice location integrated - PASSED
- [x] Troubleshooting guidance included - PASSED
- [x] Older guides reconciled or labeled - PASSED
- [x] Resource Links and package-local docs integration - PASSED
- [x] GPU support boundary language integrated - PASSED

### Issues Identified

- The docs command checker reports one existing `127.0.0.1` reference in `docs/oci-quick-start.md`. This is an internal health/readiness reference; the release browser instructions use `localhost`.
- The sensitive-term scanner completed with expected environment-variable and local ignored env/config matches. No new tracked Task-071 docs introduced provider secrets or real key values.

### Test Results

- `.venv\Scripts\python.exe -m pytest tests\unit\test_flask_routes.py tests\unit\test_license_notices.py tests\unit\test_release_package_script.py -q -p no:cacheprovider` passed: 29 passed, 1 existing `datetime.utcnow()` deprecation warning.
- `.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` completed with the known non-blocking `127.0.0.1` docs warning in `docs/oci-quick-start.md`.
- Re-ran the focused route/license/package tests after the prerequisite pass: 29 passed, 1 existing `datetime.utcnow()` deprecation warning.
- Re-ran the focused route/license/package tests after adding HTML parity assertions: 29 passed, 1 existing `datetime.utcnow()` deprecation warning.
- Re-ran the focused route/license/package tests after PR16 reviewer hardening: 42 passed, existing `datetime.utcnow()` warnings from the parameterized rejection cases.
- Re-ran the docs command checker after the prerequisite pass; it completed with the same known non-blocking `127.0.0.1` docs warning in `docs/oci-quick-start.md`.
- `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` passed.
- `.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed.
- `git diff --check` passed.
- `.venv\Scripts\python.exe .agents\skills\towerscout-secret-and-provider-key-safety\scripts\scan_for_sensitive_terms.py` completed with expected existing environment-variable/local ignored-file matches and no new tracked provider secrets.

### Remediation Actions

- No Task-071 remediation required. `TASK-066` should use the new docs as written and record any clean-machine friction.
- Keep ignored local env/config files out of release evidence and support handoff material.

### Sign-off

Ready for `TASK-066` release-candidate validation.
