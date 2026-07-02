# TASK-073: Clean-Machine Pilot / UAT Execution Plan

**Status**: COMPLETED - RC7.1 handoff packet approved for tester use with exact CPU/CUDA
package values, public-safe evidence boundary, support contacts, default smoke
fixture, official RC7.1 publication, and downloaded-artifact CPU/GPU validation;
no named tester/cohort, approver, or approval-date gate is required before
tester send
**Priority**: HIGH  
**Type**: B/C (User Testing / Release Validation)  
**Estimated Effort**: 0.5-1 day (4-8 hours)  
**Target Sprint**: Sprint 06 V1 RC1  

## Objective

Define the controlled external pilot / UAT workflow for TowerScout V1 RC1 after the internal clean-machine release-candidate gate has passed or produced owner-accepted residual risks.

This task should make external testing repeatable, bounded, and evidence-producing.

## Requirements (EARS Notation)

**R-073-001**: WHEN external pilot/UAT begins, THE PROJECT SHALL provide tester instructions that match the validated V1 RC1 package/docs/assets path.

**R-073-002**: WHEN testers report results, THE PROJECT SHALL capture environment details, package version, asset bundle version, runtime engine, Compose provider, provider used, network/TLS context, and test flow outcome.

**R-073-003**: WHEN testers hit a problem, THE PROJECT SHALL route the report through `.agent_work/user-testing/` using the established issue and artifact workflow.

**R-073-004**: WHEN a pilot test is considered successful, THE PROJECT SHALL have evidence that install, launch, provider setup, bounded detection, and issue reporting are usable under the supported V1 RC1 environment.

**R-073-005**: IF external testers find blockers in install, launch, setup, detection, export, assets, or documentation, THEN THE PROJECT SHALL classify those blockers as V1 fix work unless explicitly owner-accepted.

**R-073-006**: WHEN pilot/UAT completes, THE PROJECT SHALL decide whether V1 is complete, needs V1 patch work, or requires another release candidate.

**R-073-007**: BEFORE broad external pilot/UAT prep begins, THE PROJECT SHALL confirm that the `TASK-066` Flask route-test timeout/isolation gap is fixed or explicitly accepted as an internal-only validation risk.

**R-073-008**: WHEN pilot instructions are provided, THE PROJECT SHALL keep GPU acceleration, Docker-Desktop-free Podman, and Podman source-build support language bounded to the evidence recorded in `TASK-066` and `TASK-075`.

**R-073-009**: WHEN pilot evidence is collected, THE PROJECT SHALL avoid storing API keys, full `.env` files, private AOIs, screenshots with secrets, or raw provider responses unless explicitly approved and redacted.

**R-073-010**: WHEN pilot instructions are provided to non-command-line users, THE PROJECT SHALL explain prerequisite software, where to run commands, what each required command does, and the expected outcome after each command.

**R-073-011**: WHEN install-UX review identifies first-launch friction that cannot be solved by documentation alone, THE PROJECT SHALL route that work to a dedicated runtime prerequisite preflight task before broad external UAT if the owner selects it.

## Acceptance Criteria

- [x] Pilot/UAT start criteria are documented.
- [x] Pilot/UAT stop criteria are documented.
- [x] Tester instructions are aligned with `TASK-071` docs and `TASK-066` findings.
- [x] Acceptance checklist covers package extraction, guided bootstrap, asset import, provider setup, bounded detection, status/log collection, and issue reporting.
- [x] Environment capture checklist is ready.
- [x] Issue-reporting workflow links to `.agent_work/user-testing/`.
- [x] Support escalation path is documented.
- [x] Blocker triage rules distinguish V1 blockers, V1 patch candidates, and V2 backlog items.
- [x] V1 completion gate after pilot/UAT is documented.
- [x] `TASK-066` route-test timeout/isolation gap is fixed or explicitly accepted before pilot launch.
- [x] User-facing docs and UAT instructions explain Docker Desktop/WSL 2 readiness, PowerShell command execution, command outcomes, and first-launch recovery tips.
- [x] Low-risk documentation hardening from the install-UX review is applied without claiming unimplemented bootstrap behavior.
- [x] Runtime prerequisite preflight/bootstrap work is routed to `TASK-074`.
- [x] UAT checklist is updated to use the implemented `TASK-074` bootstrap path for first setup.
- [x] Reviewer documentation feedback is incorporated into the pilot handoff instructions.
- [x] UAT handoff packet template captures exact release URL/tag, artifact filenames, smoke fixture, and support contact before tester launch.
- [x] Official RC7.1 GitHub Release assets are published and match the accepted release source ref.
- [x] RC7.1 package/image pairs are generated from the Task-086 release source ref and replace the original RC7 tester-facing artifacts.
- [x] Official RC7.1 downloaded-artifact CPU and support-assigned GPU package paths are verified after publication.
- [x] Owner/reviewer accepts the pilot/UAT plan before external testers start.

## Dependencies

- `TASK-066`: release candidate validation gate.
- `TASK-071`: end-user release package documentation.
- `TASK-072`: release asset bundle contract.
- `TASK-067`: completed route-test timeout/isolation fix and CI timeout safeguards.
- `TASK-068`: possible follow-up home for deeper Windows/script portability work if pilot prep exposes it.
- `TASK-074`: completed bootstrap/preflight work that automates the most error-prone first-launch checks before broad external UAT.
- `.agent_work/user-testing/README.md`: existing user-testing workspace rules.
- `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md`: pre-send packet for exact release, artifact, fixture, and support values.
- `.agent_work/user-testing/issue-tracker.md`: issue tracking surface.
- `.agent_work/user-testing/instructions/TESTER-ISSUE-REPORT-CHECKLIST.txt`: existing tester issue report checklist.

## Implementation Plan

1. Review the user-testing workspace and existing tester report checklist.
2. Pull relevant clean-machine findings from `TASK-066`.
3. Confirm the `TASK-066` Flask route-test timeout/isolation gap is fixed or explicitly accepted.
4. Define pilot start criteria and stop criteria.
5. Draft a bounded acceptance checklist for testers.
6. Draft environment capture and support evidence collection instructions.
7. Define issue triage rules for V1 blockers, V1 patch candidates, and V2 backlog items.
8. Link the UAT plan to the Sprint 06 plan and user-testing workspace.
9. Prepare handoff guidance for pilot testers and first-line support.
10. Incorporate the implemented `TASK-074` bootstrap flow into pilot/UAT instructions while keeping manual launch/import as a support-directed fallback.

---

## Pilot / UAT Execution Plan

### Pilot Start Criteria

Pilot/UAT may start only when all of the following are true:

- The exact GitHub release URL or release tag, release package ZIP, pinned GHCR image digest, exact Model & Data Package filename, and matching checksum instructions are available to testers.
- The final Application Package, GHCR image digest, and Settings-linked docs are generated from the accepted release source ref, or any image/package docs drift is explicitly owner/reviewer accepted.
- `TASK-071` package docs are available from the package and from Settings Resource Links.
- User-facing docs explain Docker Desktop/WSL 2 prerequisites, PowerShell command location, expected command outcomes, and support-safe recovery steps for first launch.
- `TASK-066` CPU-default Docker Desktop package path has passed with assets imported and one bounded detection smoke, `TASK-084` RC6 CPU/CUDA package gates have passed, and RC7.1 downloaded-artifact CPU/GPU validation has passed.
- `TASK-066` residual caveats are explicitly included in pilot support language:
  - Docker Desktop is the primary pilot engine.
  - Podman is qualified only as a package-runtime path when the machine has a working Podman machine and Compose provider.
  - Docker-Desktop-free Podman and Podman source-build/base-image-pull support are not claimed.
  - CUDA GPU support is support-assigned only; RC6 Docker GPU and Podman GPU CDI evidence passed on the support GPU host, and the RC7.1 Docker GPU process was validated by a teammate.
- `TASK-067` route-test timeout/isolation fix is merged.
- A provider key is available to the tester and has been restricted/managed according to the provider-key release policy chosen for the pilot.
- The tester has an owner-provided public smoke-test fixture with provider, public/non-sensitive location, expected tile range, and whether zero detections is acceptable.

### Pilot Stop Criteria

Pause or stop pilot/UAT if any of the following occur:

- More than one tester cannot install, launch, or reach Setup Wizard using the documented package path.
- Asset import fails with verified package/assets on a supported engine.
- Provider setup cannot be completed with a valid key and supported network/TLS context.
- A bounded detection cannot complete on the owner-provided fixture after one supported retry.
- Logs or support diagnostics expose secrets or private data.
- The same HIGH or BLOCKER issue is reported by multiple testers.
- The release package, image digest, asset bundle, or docs are found to be mismatched.

### Supported Pilot Path

- **OS**: Windows 11 AMD64.
- **Runtime**: Docker Desktop is the primary pilot engine.
- **Launch mode**: CPU-default launch with `-Gpu off`.
- **Provider**: Azure Maps or Google Maps, with the provider used recorded in the report.
- **Assets**: Package-local `assets/` import using the documented asset bundle and hash verification.
- **Detection smoke**: Owner-provided public fixture with provider, public/non-sensitive location, expected tile range, and zero-detection acceptability rule. The default RC1 fixture is about 8 tiles.
- **Out of scope unless explicitly approved**: broad GPU acceleration claims beyond the support-validated CUDA package path, source-build validation, restricted-network/offline preload, large AOIs, and private/sensitive screenshot collection.

### Tester Acceptance Checklist

Each tester should complete the package path in this order:

1. Confirm prerequisites: Windows 11 AMD64, Docker Desktop running with WSL 2 support, browser, outbound internet, disk space, PowerShell access, provider key.
2. Download or receive the exact GitHub release URL/tag, release package ZIP, Model & Data Package filename, checksum/digest instructions, and smoke-test fixture.
3. Place the four release files in a new empty folder and compare each ZIP to its matching `.sha256` file before extraction.
4. Extract the Application Package ZIP to a local folder without spaces or special characters if possible.
5. Open Windows PowerShell in the extracted package folder.
6. Run the CPU-default Docker Desktop setup path:
   - `.\setup-towerscout.cmd`
   - If the ZIPs remain in Downloads or automatic discovery is ambiguous, use full paths with `-PackageZip` and `-AssetZip`.
   - Expected outcome: setup reports disk, port, engine, Compose, checksum, and asset-layout checks; imports assets with hash verification; starts TowerScout; and opens `http://localhost:5000` or allows the tester to open that address manually.
7. Use the manual fallback only when support directs it:
   - Extract the Model & Data Package entries into the package-local `assets\` folder.
   - Launch with `.\start.bat -Engine docker -Gpu off`.
   - Import with `.\scripts\import-assets.cmd -Engine docker -Source assets -VerifyHashes -RestartWaitSeconds 180`.
   - Expected outcome: the importer initializes `.env` if needed, completes without missing/corrupt asset errors, and waits for TowerScout after restart.
8. Complete Setup Wizard with Azure or Google provider key.
9. Open Settings Resource Links and confirm the package-local docs and source/license page load.
10. Run the owner-provided bounded public detection smoke. If support did not provide a fixture, stop and ask for one before choosing an AOI.
11. Confirm:
    - Detection completes without a crash.
    - Results appear in the map and right-hand review panel.
    - Detected tower addresses/provider metadata appear when geocoding succeeds or show a clear fallback when unavailable.
    - CSV or KML export can be generated if included in the pilot script.
12. Collect status/log evidence requested below.
13. Stop TowerScout using `.\scripts\stop.cmd -Engine docker` unless support explicitly selected another engine.

### Environment Capture

Capture these details for every pilot run:

- Tester name or role.
- Date/time and time zone.
- Windows version and CPU architecture.
- Runtime engine: Docker Desktop or Podman.
- Engine version and whether Docker Desktop was running.
- Compose provider/version if visible.
- TowerScout package version and folder name.
- Release URL or release tag used.
- Image tag and digest from the package manifest or launch output.
- Asset bundle version/checksum status and asset import result.
- Bootstrap or launch command and port.
- GPU mode requested (`off`, `auto`, or `on`); expected pilot default is `off`.
- Provider used: Azure Maps or Google Maps.
- Whether the machine is behind a proxy, custom TLS inspection, VPN, or restricted network.
- Detection fixture/AOI name, requested provider, tile count estimate, whether zero detections is acceptable, and whether the AOI is public/non-sensitive.
- Final outcome: PASS, PASS_WITH_NOTES, BLOCKED, or FAIL.

### Evidence Collection

Collect only the minimum useful evidence:

- Bootstrap or launcher output showing image digest, engine, port, and readiness result.
- `IMAGE.txt` contents or equivalent image line copied from bootstrap output.
- Asset import output showing `VerifyHashes` success or exact failure.
- `/api/health` and `/api/readiness` summary if available.
- Screenshot of the failing step only when it does not expose secrets or sensitive AOIs.
- Browser-visible error text.
- Sanitized logs when requested by support.

Do not collect API keys, full `.env` files, private AOI screenshots, raw provider responses, or unredacted logs with secrets.

### Issue Reporting Workflow

Use `.agent_work/user-testing/` for pilot reports:

1. Save raw evidence under `.agent_work/user-testing/artifacts/YYYY-MM-DD-ut-###-short-slug/`.
2. Create or update `.agent_work/user-testing/issues/UT-###-short-slug.md` using `ISSUE-TEMPLATE.md`.
3. Update `.agent_work/user-testing/issue-tracker.md`.
4. Link each issue to the owning task:
   - Install/launch/runtime prerequisite issues -> `TASK-074` candidate.
   - Package/docs/assets mismatch -> `TASK-066` or `TASK-071`.
   - Provider key or exposure policy -> `TASK-076`.
   - GPU-specific findings -> `TASK-075`.
   - Detection correctness/performance -> `TASK-079`, `TASK-026`, or a new V1 patch task depending on severity.
5. Move issues through the existing status lifecycle: `NEW`, `WAITING-FOR-ARTIFACTS`, `TRIAGED`, `IN-PROGRESS`, `READY-FOR-RETEST`, `CLOSED`.

### Triage Rules

- **V1 blocker**: prevents package extraction, launch, asset import, provider setup, bounded detection, or safe support evidence collection on the supported pilot path.
- **V1 patch candidate**: core path works, but a defect requires a documented workaround, affects multiple testers, or undermines confidence in the first release.
- **Documentation fix**: behavior is acceptable but tester instructions are unclear, missing, or easy to misread.
- **V2 backlog**: enhancement, large-AOI performance improvement, non-default GPU path, Docker-Desktop-free Podman path, advanced workflow, or architecture improvement not needed for the first controlled pilot.
- **Accepted risk**: residual caveat explicitly approved by owner/reviewer and documented in release notes or pilot support language.

### Support Escalation

First-line support should triage in this order:

1. Confirm the tester is using the supported package path and current package/assets.
2. Confirm Docker Desktop is running and the package used CPU-default `-Gpu off`.
3. Confirm WSL 2 is available and Docker commands print version information.
4. Confirm the tester opened PowerShell in the extracted package folder.
5. Confirm bootstrap passed preflight checks or, for support-directed fallback, assets imported with hash verification.
6. Confirm provider key setup succeeded without asking the tester to send the key.
7. Confirm `/api/health` and `/api/readiness` state.
8. Collect sanitized bootstrap/launcher/import/readiness evidence.
9. Create or update the matching `UT-###` issue and route by triage rules.

Escalate to engineering when the issue is a V1 blocker, repeats across testers, affects security/privacy, or contradicts `TASK-066` validation evidence.

### V1 Completion Gate After Pilot

After pilot/UAT, V1 may be considered ready only if:

- Supported package path succeeds for the selected pilot cohort.
- No open BLOCKER issues remain.
- HIGH issues are fixed, explicitly accepted, or converted into a bounded V1 patch plan.
- User-facing docs match the tested package path.
- Release notes list accepted caveats and unsupported paths.
- Provider-key handling and support language are approved.
- Remaining GPU, Podman, and restricted-network claims are bounded to validated evidence.

---

## Implementation Log

### 2026-05-11 - Task Created
**Objective**: Create detailed Sprint 06 task documentation for clean-machine pilot / UAT execution planning.  
**Context**: Sprint 06 planning separates internal release-candidate validation from external pilot/UAT. External testing should start only after `TASK-066` validates or dispositiones the package/docs/assets path.  
**Decision**: Keep this task focused on UAT planning and evidence workflow, not on fixing release-candidate defects. Defects found by `TASK-066` should be routed before pilot start.  
**Execution**: Created `.agent_work/tasks/completed/TASK-073-clean-machine-uat-plan.md` and synchronized the task with `current-tasks.md`.
**Output**: Task file ready for intake.  
**Validation**: Pending `.agent_work` validation after all Sprint 06 task files are created.  
**Next**: Wait for `TASK-066` findings, then build the pilot/UAT checklist and handoff flow.

### 2026-05-27 - Pre-Pilot Test-Harness Dependency Added
**Objective**: Carry forward the `TASK-066` route-test timeout/isolation finding before starting UAT planning.
**Context**: `TASK-066` package-runtime validation passed with boundaries, but repeated broad pytest review commands isolated a test-harness gap in `tests/unit/test_flask_routes.py`: the module can stall during collection because it imports the full production Flask app and local `.env` path before fixtures isolate config.
**Decision**: `TASK-073` should not start broad external pilot prep until this gap is fixed or the owner explicitly accepts it as an internal-only validation risk. The issue does not require Docker Desktop or Podman to reproduce and should be routed to `TASK-067` and/or `TASK-068` if fixed before pilot prep.
**Output**: Added a requirement, acceptance criterion, dependency note, and implementation-plan step for the route-test gap disposition.
**Validation**: Pending `.agent_work` validation.
**Next**: Complete `TASK-066` review disposition, then either fix the route-test isolation/timeout issue or explicitly accept the risk before drafting the pilot/UAT workflow.

### 2026-05-27 - Package-Path Pilot/UAT Plan Drafted
**Objective**: Start `TASK-073` after the route-test timeout/isolation dependency was closed by `TASK-067` / PR #19.
**Context**: `TASK-066` validated the CPU-default Docker Desktop and qualified Podman package-runtime paths with bounded caveats. `TASK-067` merged pytest timeout safeguards and route-test runtime isolation, removing the main pre-pilot test-harness blocker.
**Decision**: Draft the pilot/UAT plan around the validated package path, with Docker Desktop as the primary pilot engine, CPU-default launch, package-local asset import, and explicit boundaries around GPU, Docker-Desktop-free Podman, source-build validation, restricted-network support, and private AOI evidence.
**Execution**: Added start/stop criteria, supported pilot path, tester acceptance checklist, environment capture, evidence collection, issue reporting, triage rules, support escalation, and V1 completion gate.
**Output**: `TASK-073` now contains a reviewable package-path UAT plan and points to the user-testing workspace for evidence handling.
**Validation**: Pending owner/reviewer acceptance and `.agent_work` validation.
**Next**: Validate `.agent_work`, review the draft with the owner/reviewer, and identify the final package/assets/checksum inputs before tester launch.

### 2026-05-27 - Non-Command-Line User Documentation Pass
**Objective**: Reduce first-launch confusion for external pilot users who may not have prior command-line or container-runtime experience.
**Context**: The initial UAT plan was directionally correct but some user-facing docs still described the runtime path as generic Podman-or-Docker, and several commands did not explain where to run them or what success should look like.
**Decision**: Keep Docker Desktop with WSL 2 as the primary RC1 pilot path, keep Podman as a qualified support-directed path, and require docs/checklists to show PowerShell location, Docker/WSL readiness checks, command purpose, and expected outcomes.
**Execution**: Updated the Task-073 plan and UAT checklist; synchronized user-facing package docs and Settings-linked HTML docs so default pilot commands use `-Engine docker -Gpu off` and expected outcomes are explicit.
**Output**: External pilot instructions now include Docker Desktop/WSL 2 readiness checks, PowerShell basics, launch/import/status/stop command outcomes, and clearer support escalation checks.
**Validation**: `python .agent_work\scripts\validate_agent_work.py` passed; `python .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed.
**Next**: Prepare the PR update summary and request owner/reviewer acceptance before external pilot testers start.

### 2026-05-27 - Install-UX Review Follow-Through And TASK-074 Selection
**Objective**: Apply low-risk install-documentation hardening and route implementation-level first-launch automation to a dedicated task.
**Context**: The install-UX review recommended clearer release asset naming, checksum handling, first-run expectations, asset ZIP handling, and a future bootstrap/preflight script. The owner agreed with the path forward and specifically asked to preserve Podman support as a qualified path rather than diminishing it.
**Decision**: Harden current docs only where they reflect existing behavior, and create `TASK-074` for bootstrap/preflight implementation. Docker Desktop remains the primary RC1 pilot path; Podman remains support-directed with explicit prerequisites and validation boundaries.
**Execution**: Updated Quick Start, Package Guide, Project Overview, Settings-linked HTML, and the UAT checklist to clarify Application Package versus Model & Data Package, GitHub Release asset selection, checksum verification, disk-space expectations, nested asset layout mistakes, first image-pull delay, stop/contact-support conditions, and smoke-test expectations. Created `TASK-074` for the bootstrap/preflight implementation plan.
**Output**: `TASK-073` now points remaining first-launch automation to `TASK-074` and avoids promising behavior that does not exist yet.
**Validation**: `python .agent_work\scripts\validate_agent_work.py` passed; `python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed; `python .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed.
**Next**: Commit the hardening updates, then start `TASK-074` implementation planning.

### 2026-05-27 - UAT Checklist Aligned To Bootstrap Implementation
**Objective**: Keep pilot/UAT instructions aligned after `TASK-074` implemented a real bootstrap path.
**Context**: Earlier Task-073 docs intentionally avoided promising bootstrap behavior before it existed. Task-074 now provides `bootstrap.cmd`, checksum/asset ZIP validation, engine preflight, verified asset import, and launch orchestration.
**Decision**: Make the UAT checklist use `bootstrap.cmd -Engine docker -Gpu off -AssetZip ...` as the recommended first setup path while retaining manual `start.bat` plus `scripts\import-assets.cmd` steps as a support-directed fallback.
**Execution**: Updated `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md` with bootstrap commands, full-path examples, expected output, and manual fallback boundaries.
**Validation**: Superseded by final Task-074 validation and the May 28 Task-073 alignment pass.
**Next**: Owner/reviewer should evaluate the updated bootstrap-first UAT path before external testers start.

### 2026-05-28 - Post-TASK-074 UAT Plan Alignment
**Objective**: Remove remaining task/doc drift after `TASK-074` follow-up patches made bootstrap and importer behavior final for RC1 pilot prep.
**Context**: The standalone UAT checklist already used bootstrap as the first setup path, but this task file still described the older direct-launch/import sequence. The Quick Start and Package Guide also retained a stale statement that the launcher had to create `.env` before manual asset import.
**Decision**: Keep bootstrap as the recommended first setup path, keep manual `start.bat` plus `scripts\import-assets.cmd` as a support-directed fallback, and document that the importer initializes `.env` from `.env.example` when needed.
**Execution**: Updated the Task-073 tester checklist, support escalation path, evidence labels, Quick Start Markdown/HTML, Package Guide manual import wording, and tester issue-report checklist.
**Validation**: `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed.
**Next**: Commit the Task-073 bootstrap-alignment update and request owner/reviewer acceptance before external testers start.

### 2026-05-29 - Reviewer Handoff Clarity Fixes
**Objective**: Address reviewer-identified confusion points before external testers receive the UAT package.
**Context**: Reviewer feedback rated the docs close to controlled UAT readiness but requested clearer GitHub Release navigation, exact release/asset handoff values, fixture requirements, placeholder guidance, checksum folder hygiene, Podman-scoped Docker stop wording, direct-launch boundaries, and support metadata instructions.
**Decision**: Treat the feedback as documentation/handoff hardening, not a product-path change. Keep Docker Desktop plus bootstrap as the primary path, keep Podman support-directed, and require support to provide final release URL/tag, exact asset filename, and a public smoke fixture before pilot launch.
**Execution**: Updated Quick Start Markdown/HTML, Package Guide, UAT checklist, issue-report checklist, and this task file with the final handoff details and support-safe evidence instructions.
**Validation**: `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed.
**Next**: Push the PR update, then request owner/reviewer acceptance.

### 2026-05-29 - UAT Handoff Packet Template
**Objective**: Convert the remaining pre-pilot handoff values into a single fillable packet before external tester instructions are sent.
**Context**: PR #25 merged the bootstrap-first UAT documentation and reviewer clarity fixes. The remaining pre-pilot gate is not another broad docs pass; it is filling in exact release URL/tag, artifact filenames, smoke-test fixture, and support contact values.
**Decision**: Add a dedicated handoff packet template under `.agent_work/user-testing/instructions/` and link it from the user-testing workspace instructions.
**Execution**: Added `RC1-PILOT-HANDOFF-PACKET.md`, updated user-testing README files, and updated sprint/task state to reflect that final values and owner/reviewer acceptance are still pending.
**Validation**: `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md` passed with the known intentional `127.0.0.1` warning in `docs\oci-quick-start.md`; `git diff --check` passed.
**Next**: Fill the packet with final RC artifact values and run one final package-path validation before sending to testers.

### 2026-05-29 - Final Handoff Readiness Check
**Objective**: Determine whether the handoff packet can be filled with final release artifact values.
**Context**: After PR #26 merged, local `main` was synced and the repository release/package state was inspected.
**Findings**: `gh release list --repo J-Schulein/TowerScout --limit 10` returned no published releases. The local `dist\towerscout-v0.1.0-rc1.zip` was generated before the latest Task-073 documentation updates. The most recent validated image digest still points to the earlier package-validation source ref, while current `main` is `815e8cda77fb5a0679372a0cacd5f6cf8e3c5a32`. Because the image serves Settings Resource Links docs from `/app/docs`, a final tester package should use a newly built/published image digest from the accepted release source ref, or the owner/reviewer should explicitly accept image-docs drift.
**Decision**: Do not fill or send the handoff packet yet. Treat final GitHub Release publication, current source-ref image digest, exact artifact filenames, smoke fixture, support contact, and final package-path validation as the remaining Task-073 gate.
**Execution**: Updated the handoff packet readiness notes, Task-073 status, acceptance criteria, and sprint current-state summary.
**Validation**: `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` passed; `.\.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` passed; `git diff --check` passed.
**Next**: Generate/publish final RC artifacts from the accepted source ref, fill the handoff packet, and run one final package-path validation.

### 2026-05-29 - PR27 Reviewer Follow-Up Notes
**Objective**: Preserve the reviewer-confirmed post-merge release handoff checks before final UAT materials are sent.
**Context**: The PR27 reviewer agreed the readiness note should merge, but emphasized that it is not approval to launch external UAT.
**Decision**: After PR27 merges, the next release handoff step must record the post-merge accepted source ref, rebuild/publish the final GHCR image from that ref, regenerate the Application Package with that digest, publish both package ZIPs plus checksums under the same GitHub Release, and verify the published artifact path before changing the handoff packet approval state.
**Follow-Up Checks**:
- Verify Settings-linked docs from the running final image, because the image serves `/app/docs`.
- Keep GPU acceleration out of tester-facing claims unless NVIDIA Docker Desktop WSL2 validation, CPU/GPU fixture parity, and timing evidence are complete.
- Keep Podman language qualified to the validated package-runtime path.
- Treat green CI as necessary but not sufficient; final published artifact validation remains the release authority.
- Remove or quarantine stale local `dist` artifacts before uploading final release assets.
- Keep the handoff packet's explicit accepted source ref aligned with `SOURCE.txt`, `release-manifest.v1.json`, image digest, and release tag.
**Next**: Merge PR27 if checks pass, then run the final release build/publish/validation sequence before external tester handoff.

### 2026-05-29 - Draft Release Package Validation Passed
**Objective**: Validate the actual draft-release artifact path before external UAT handoff.
**Context**: PR27 was merged, `main` was synced, and the post-merge source ref was selected as the release source ref.
**Execution**: Published the CUDA-capable GHCR image from source ref `baa5ccc053184d4a24389a436f6d7c2168238c1e`, generated the final Application Package with that digest, uploaded all four assets to a draft prerelease, downloaded those release assets into a separate validation folder, verified both ZIP checksums, and ran `bootstrap.cmd` from the downloaded package with Docker Desktop and `-Gpu off`.
**Validation Evidence**:
- Draft release tag: `v0.1.0-rc1`.
- Accepted source ref: `baa5ccc053184d4a24389a436f6d7c2168238c1e`.
- Published image: `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121@sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`.
- Application Package: `towerscout-v0.1.0-rc1.zip`, SHA-256 `ff7a2c997fe0678c1133847a56e1d2f21c7935732b1103841313a2b404cd3344`.
- Model & Data Package: `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`, SHA-256 `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Bootstrap verified the package and asset ZIP checksum sidecars, rejected no asset-layout issues, pulled the pinned GHCR image, created `.env` from `.env.example`, imported assets with hash verification, and reached readiness `setup_required` with `asset_status=ok`.
- Runtime readiness reported `pytorch_flavor=cuda121`, `torch_version=2.2.1+cu121`, `torch_cuda_build=12.1`, `device_policy=cpu`, `selected_device=cpu`, and image digest `sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746` under `-Gpu off`.
- `status.cmd`, `/api/health`, `/api/readiness`, `/docs/project-overview.html`, `/docs/towerscout-user-guide.html`, and `/license` passed.
**Decision**: The package/image/docs/assets drift risk identified in PR27 is resolved for the draft-release artifact path. Keep the UAT packet approval at `NO` until the release owner fills the smoke fixture and support contact, confirms provider-key expectations, and accepts or completes the provider setup plus bounded detection smoke gate.
**Next**: Fill owner-controlled handoff values, optionally run provider setup plus bounded detection smoke on the selected public fixture, then decide whether to publish the draft prerelease and approve the UAT packet.

### 2026-05-29 - UAT Handoff Values Filled And Prerelease Published
**Objective**: Close the owner-controlled handoff values that remained after draft-release package validation.
**Context**: The release owner provided a public Azure Maps smoke fixture, support contacts, provider-key handling expectations, and approval to internally rerun provider setup plus bounded detection smoke before publishing the prerelease.
**Decision**: Use Azure Maps at `200 west st, New York, NY 10282` with a `150 meter` circle as the default public RC1 smoke fixture. Ask testers for support-safe environment, package, command, checksum, readiness, provider, and detection outcome details. Do not ask testers to send API keys, `.env` files, raw detection JSON, tile/map URLs, raw logs, browser network traces, provider portal screenshots, private AOI screenshots, or named-volume contents unless an approved redaction/handling procedure exists.
**Execution**:
- Filled the UAT handoff packet with the public release URL, support contacts, smoke fixture, provider-key guidance, and support-safe evidence instructions.
- Copied local ignored provider config into the downloaded validation container for internal smoke only, without committing or recording the key.
- Queried Azure Maps directly inside the container to resolve the fixture location to `40.7148641, -74.0141981` without printing provider credentials.
- Ran the final-digest Docker Desktop `-Gpu off` detection smoke inside the RC container because this workstation had a conflicting host process on `localhost:5000`.
- Published the `v0.1.0-rc1` prerelease for the selected controlled tester path.
**Validation Evidence**:
- Published prerelease URL: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc1`.
- Accepted source ref: `baa5ccc053184d4a24389a436f6d7c2168238c1e`.
- Published image digest: `sha256:36f452a5da0d9f3fa17f5b0f90802873cb40b1a433596048e4e9437e6f51d746`.
- Application Package: `towerscout-v0.1.0-rc1.zip`, SHA-256 `ff7a2c997fe0678c1133847a56e1d2f21c7935732b1103841313a2b404cd3344`.
- Model & Data Package: `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`, SHA-256 `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Smoke estimate: `8` tiles and `48.23` seconds.
- Smoke result: HTTP `200`, `55` total records, `8` tile records, `47` cooling-tower records, `47` records with address data, and elapsed time about `43` seconds.
**Finding**: Backend `/api/geocode/forward` returned HTTP `500` after Azure forward geocoding succeeded because the route-level `provider_used` field exposed a `GeocodingProvider` enum. This did not block the selected fixture smoke, because the fixture coordinates were resolved separately and detection completed with address data.
**Follow-Up Resolution**: PR #28 follow-up investigation confirmed the tester-visible Azure search path uses `/api/maps/azure/search`, not `/api/geocode/forward`. The backend forward-geocode route was still fixed to serialize `provider_used` from `GeocodingResult.to_dict()` output, and regression coverage now proves Azure forward-geocode route responses are JSON-safe.
**Next**: Select tester/cohort, get owner/reviewer packet approval, and start controlled external UAT with the published prerelease.

### 2026-05-29 - Post-PR28 Final Artifact Refresh And Smoke
**Objective**: Refresh the published RC1 Application Package and image after PR #28 merged runtime and package-doc changes.
**Context**: PR #28 changed `webapp/towerscout.py` and package-included documentation after the first `v0.1.0-rc1` prerelease publication. The release package, image digest, `SOURCE.txt`, `release-manifest.v1.json`, and handoff packet therefore needed to be realigned to the merged source ref before external UAT.
**Execution**:
- Synced `main` to `e6495d14bd642eda81f7a70d6fe2e93d4b15097a`.
- Published the CUDA-capable GHCR image from `main` through the `TowerScout Container Publish` workflow.
- Regenerated `dist\towerscout-v0.1.0-rc1.zip` with the refreshed image digest and `PytorchFlavor=cuda121`.
- Replaced the Application Package ZIP and checksum on the published `v0.1.0-rc1` prerelease.
- Downloaded the refreshed app ZIP and checksum into a fresh validation folder, copied the unchanged Model & Data Package into that folder, verified both ZIP checksums, extracted the downloaded Application Package, and ran Docker Desktop validation on port `5006`.
- Copied local ignored provider config into the validation container for internal smoke only, without printing or committing provider secrets.
- Ran the owner-selected Azure fixture through Azure search, tile estimate, and detection.
**Validation Evidence**:
- Published prerelease URL: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc1`.
- Accepted source ref: `e6495d14bd642eda81f7a70d6fe2e93d4b15097a`.
- Published image: `ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda121@sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`.
- Application Package: `towerscout-v0.1.0-rc1.zip`, SHA-256 `e071f1ac773f993b3a8636cab4be0e476ee95086dfec6ff24beda8b8a6fb3142`.
- Model & Data Package: `towerscout-v0.1.0-rc1-assets-towerscout-v1-assets-2026-05-05.zip`, SHA-256 `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Bootstrap verify-only passed; the first full bootstrap attempt reached the image pull path and exceeded the outer validation timeout because the refreshed CUDA-capable image was not yet local. Explicit `docker pull` of the pinned digest then completed successfully, and the package stack reached health/readiness on port `5006`.
- Runtime readiness reported `pytorch_flavor=cuda121`, `torch_version=2.2.1+cu121`, `torch_cuda_build=12.1`, `device_policy=cpu`, `selected_device=cpu`, image digest `sha256:e90524870a279c04f941147fc30328636ac97f75be200fd06c929df83c49d158`, and assets `ok` under `-Gpu off`.
- In-container asset hash verification returned `asset_status=ok`, `verify_hashes=True`, no missing assets, no corrupt assets, and no optional missing assets.
- `/api/health`, `/api/readiness`, `/docs/project-overview.html`, `/docs/towerscout-user-guide.html`, `/docs/v1-rc1-quick-start.html`, and `/license` passed.
- Smoke fixture: Azure Maps, `200 west st, New York, NY 10282`, `150 meter` circle, estimated `8` tiles and `44.0` seconds.
- Detection result: Azure search HTTP `200` with one result; detection HTTP `200`, elapsed time about `59` seconds, `55` result records, and `47` records with address data.
**Decision**: The post-PR28 package/image/docs drift is resolved for the published prerelease. Keep the UAT packet approval at `NO` until tester/cohort selection and owner/reviewer approval are filled.
**Next**: Commit the refreshed evidence update, open a review PR if desired, then request owner/reviewer approval for tester send.

### 2026-06-02 - RC2 Release Path And Smoke Evidence Updated
**Objective**: Replace the superseded rc1 prerelease handoff basis with the
corrected rc2 release path after UAT setup simplification and package refresh.
**Execution**:
- Published the corrected rc2 GHCR image and created the GitHub prerelease at
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc2`.
- Uploaded and downloaded the four rc2 release assets, verified both checksum
  sidecars, extracted only the Application Package ZIP, and validated setup
  from the downloaded release files.
- Ran provider setup through the browser Setup Wizard without recording the
  Azure Maps key value.
- Ran the owner-selected public Azure fixture through tile estimate and
  detection.
**Validation Evidence**:
- Release tag: `v0.1.0-rc2`.
- Accepted source ref: `4e8054d27faa1f956998f85b665a4ea28fc01ed9`.
- Image:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc2-cuda121@sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`.
- Downloaded-release validation reached `setup_required` with assets `ok` on
  port `5012` after checksum verification and asset import.
- Provider-smoke validation reached `ready` with assets `ok`, config `ok`,
  Azure configured, default provider `azure`, CPU mode, and the expected image
  digest on port `5013`.
- Smoke fixture: Azure Maps, `200 west st, New York, NY 10282`, `150 meter`
  circle, estimated `8` tiles and `44` seconds.
- Detection result: completed successfully, processed `48` detection records
  and `8` tile records, address/provider metadata appeared in the right-hand
  panel, and elapsed time was about `56.38` seconds.
**Decision**: The rc2 release path is validated through download, setup,
provider setup, and bounded Azure smoke. Keep the UAT packet approval at `NO`
until tester/cohort selection and owner/reviewer approval are filled.
**Next**: Select tester/cohort and record owner/reviewer approval before
external tester launch.

### 2026-06-17 - RC6 Pilot Handoff Packet Refreshed
**Objective**: Replace the rc2/rc3-era tester handoff values with the current
RC6 package identities and support boundaries.
**Context**: `TASK-084` completed RC6 CPU/CUDA package generation, CPU Docker
and Podman validation, CUDA Docker GPU and Podman GPU CDI validation, and
public-safe evidence preparation. The external tester handoff packet still
contained rc2-specific release evidence and needed to be reset around official
`v0.1.0-rc6` publication.
**Decision**: Keep the tester-facing default path as Docker Desktop plus the
CPU Application Package. Treat CUDA and Podman as support-assigned tracks.
Keep the UAT packet approval at `NO` until the official `v0.1.0-rc6` GitHub
release is published, downloaded-release verification passes, a tester/cohort
is selected, and the owner/reviewer approves the packet.
**Execution**:
- Rewrote `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md`
  with exact RC6 source ref, CPU/CUDA package names, checksum sidecars, image
  digests, shared Model & Data Package identity, default smoke fixture,
  support contacts, and public-safe evidence boundary.
- Updated this task's status and acceptance criteria so official RC6
  publication and downloaded-release validation are correctly shown as pending
  rather than inherited from older rc2/rc3 validation.
- Updated the tester acceptance checklist language in this task to use
  `setup-towerscout.cmd` as the normal first setup path.
**Output**:
- RC6 handoff packet is ready for owner/reviewer review but not approved for
  tester send.
- Official RC6 publication and downloaded-release validation remain the next
  release-control gates.
**Validation**: Pending final post-edit `.agent_work` validation and diff
checks in the current handoff slice.
**Next**: Publish official `v0.1.0-rc6` only after owner approval, then verify
the downloaded release assets before changing the packet approval state.

### 2026-06-17 - Official RC6 Publication Gates Closed
**Objective**: Bring `TASK-073` back in sync after the official RC6 release
publication and post-publication downloaded-asset validation were recorded
through `TASK-084`.
**Context**: `TASK-084` is complete and PR #40 merged the official
`v0.1.0-rc6` publication evidence. The UAT handoff packet now has the final
release URL, exact artifact values, and downloaded CPU package validation
state, while tester/cohort selection and owner/reviewer packet approval remain
outside the release packaging lane.
**Decision**: Mark the official RC6 release asset publication and downloaded
release package path criteria complete in `TASK-073`, but keep the UAT packet
approval at `NO` until the selected tester/cohort, official tester-path
provider setup / bounded Azure smoke, and owner/reviewer approval are recorded.
**Execution**:
- Updated this task's status to show official RC6 publication and
  downloaded-release validation as complete.
- Checked off the official GitHub Release publication and downloaded-release
  package-path acceptance criteria.
- Left tester/cohort selection, official tester-path provider smoke, and
  owner/reviewer acceptance pending.
**Output**: `TASK-073` now points at the remaining UAT approval gates rather
than completed `TASK-084` publication work.
**Validation**: Superseded by the later RC7.1 validation and approval entries.
**Next**: Select the tester/cohort, perform or explicitly schedule the
provider setup / bounded Azure smoke in the official tester path, then fill
approver, approval date, and tester/cohort before changing the UAT handoff
packet to approved.

### 2026-07-02 - RC7.1 Validation And Handoff Refresh
**Objective**: Replace the RC6 tester handoff basis with the validated RC7.1
release package after post-publication CPU and GPU downloaded-artifact checks.
**Context**: `v0.1.0-rc7.1` replaces the original RC7 artifacts for
tester-facing validation. The live GitHub prerelease targets source ref
`1152c16fede6e852e37603a90d4ec9d9626c0e71` and includes the expected six
release assets: CPU ZIP/checksum, CUDA ZIP/checksum, and shared Model & Data
Package ZIP/checksum.
**Decision**: Treat RC7.1 as the validated tester-facing package set based on
release-owner Docker CPU validation and teammate Docker GPU validation from
downloaded release artifacts. Keep `TASK-087` out of the RC7.1 critical path.
At this checkpoint, the UAT packet approval state remained `NO`; the following
2026-07-02 approval entry supersedes that gate.
**Execution**:
- Updated the UAT handoff packet with RC7.1 artifact names, hashes, source ref,
  image digests, and validation basis.
- Updated this task's status, acceptance criteria, validation summary, and
  sign-off wording from RC6 to RC7.1.
- Kept evidence support-safe: no provider keys, `.env`, raw logs, screenshots,
  certificate subjects, thumbprints, provider responses, or local environment
  details were recorded.
**Validation**:
- Official release state was verified from GitHub: `v0.1.0-rc7.1` is a
  prerelease, targets `1152c16fede6e852e37603a90d4ec9d9626c0e71`, and exposes
  the six expected assets.
- Local package ZIP structure summaries passed for CPU and CUDA packages.
- Secret-term scans reported `matches: 0` for the CPU and CUDA package ZIPs.
**Next**: Superseded by the following 2026-07-02 handoff approval entry; route
one-click host-side repair UX to `TASK-087` only if the team explicitly selects
it.

### 2026-07-02 - Handoff Packet Approved And Task Completed
**Objective**: Close the remaining Task-073 approval gate after RC7.1
downloaded-artifact validation passed.
**Context**: The packet already contains the final RC7.1 release URL, package
filenames, checksums, source ref, image digests, support contacts, smoke
fixture, and support-safe evidence boundaries. Project-owner direction
clarified that tester/cohort, approver, and approval date do not need to be
filled before marking the packet approved.
**Decision**: Mark the RC7.1 handoff packet approved for tester use and close
Task-073. Runtime prerequisites remain a per-tester outreach check rather than
a packet approval blocker.
**Execution**:
- Changed the handoff packet approval state to `YES`.
- Marked tester/cohort, approver, and approval-date fields as not required for
  RC7.1 packet approval.
- Checked the remaining Task-073 owner/reviewer acceptance criterion and
  updated the task status, validation summary, and sign-off to completed.
**Validation**: `python .agent_work\scripts\validate_agent_work.py` passed;
`python .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`
passed; targeted sensitive-term scan of the changed handoff/task files reported
`matches: 0`; `git diff --check` passed.
**Next**: Keep Task-073 in `tasks/active/` until Sprint 6 closeout; handle
actual tester assignment during outreach; keep `TASK-087` as the follow-on TLS
repair UX plan unless promoted.

---

## Validation Results

### Test Summary
**Test Date**: May 27-July 2, 2026
**Test Environment**: Documentation/task-state validation and internal release
package validation; no external pilot run yet
**Test Status**: COMPLETE - RC7.1 package identities and UAT handoff packet are
prepared, official RC7.1 publication and downloaded-artifact CPU/GPU validation
have passed, and the handoff packet is approved for tester use without requiring
named tester/cohort, approver, or approval-date fields.

### Acceptance Criteria Validation
- [x] Start/stop criteria documented - PASS - See Pilot Start Criteria and Pilot Stop Criteria.
- [x] Tester acceptance checklist ready - PASS - See Tester Acceptance Checklist; it now uses bootstrap as the first setup path and manual import only as a support-directed fallback.
- [x] Environment capture checklist ready - PASS - See Environment Capture.
- [x] Issue-report workflow linked - PASS - See Issue Reporting Workflow and `.agent_work/user-testing/`.
- [x] Tester-facing handoff artifacts updated - PASS - See `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md` and `TESTER-ISSUE-REPORT-CHECKLIST.txt`.
- [x] Non-command-line first-launch guidance added - PASS - User docs and UAT checklist now include PowerShell location, Docker Desktop/WSL 2 checks, default Docker commands, expected outcomes, and support-safe recovery instructions.
- [x] Low-risk install-UX hardening added - PASS - Quick Start, Package Guide, Project Overview, Settings-linked HTML, and UAT checklist now clarify Application Package versus Model & Data Package naming, GitHub Release asset selection, checksums, disk-space targets, nested asset layout mistakes, first image-pull delay, support stop points, and smoke-test expectations.
- [x] Runtime prerequisite preflight completed - PASS - `TASK-074` created, implemented, validated, and incorporated into the bootstrap-first UAT path.
- [x] UAT checklist aligned to implemented setup path - PASS - The checklist now uses `setup-towerscout.cmd` for first setup and keeps manual import as fallback.
- [x] UAT handoff packet template ready - PASS - See `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md`; final release, fixture, support contact, and provider-key guidance are filled.
- [x] V1 completion gate documented - PASS - See V1 Completion Gate After Pilot.
- [x] RC7.1 package/image pairs generated and published from accepted source ref - PASS - `v0.1.0-rc7.1` targets `1152c16fede6e852e37603a90d4ec9d9626c0e71` and replaces original RC7 tester-facing artifacts.
- [x] Official RC7.1 release published - PASS - `v0.1.0-rc7.1` is published as a prerelease with CPU, CUDA, shared asset, and checksum assets.
- [x] Official RC7.1 downloaded-artifact validation - PASS - release-owner Docker CPU validation and teammate Docker GPU validation passed from downloaded release artifacts.
- [x] Default public smoke fixture selected - PASS - Azure Maps, `200 west st, New York, NY 10282`, `150 meter` circle, about `8` tiles; zero detections is not acceptable.
- [x] Owner/reviewer acceptance - PASS - RC7.1 handoff packet is approved for tester use.

### Issues Identified

- No pilot execution issues yet; this task has only drafted the plan.
- Actual tester/cohort assignment remains an outreach step, not a Task-073
  completion blocker.
- Backend `/api/geocode/forward` serialization was fixed after the final-digest smoke uncovered a JSON-unsafe `provider_used` enum field. Tester-visible Azure search was confirmed to use `/api/maps/azure/search`.

### Remediation Actions

- Keep GPU, Docker-Desktop-free Podman, source-build, restricted-network, and large-AOI scenarios out of external pilot instructions unless owner-approved evidence is added.
- Keep the forward-geocode regression test in the RC validation set so future route refactors do not reintroduce enum serialization failures.

### Sign-off

The RC7.1 handoff packet, default public smoke fixture, support contacts, and
support-safe evidence boundaries are approved for tester use. Task-073 is
complete; keep the task file in `tasks/active/` until Sprint 6 closeout.
