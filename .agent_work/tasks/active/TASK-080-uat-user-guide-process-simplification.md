# TASK-080: RC1 UAT User Guide And Setup Process Simplification

**Status**: IN_PROGRESS  
**Priority**: HIGH  
**Type**: B/C (User Testing / Documentation / Release UX)  
**Estimated Effort**: 1-2 days (8-16 hours), plus optional launcher follow-through  
**Target Sprint**: Sprint 06 V1 RC1 external UAT readiness  

## Objective

Revise the first-cohort RC1 UAT process so non-technical testers receive one
clear, start-to-finish user guide instead of several overlapping technical
documents. The revised process should reduce command/path decisions, explain
what the tester is doing and why, preserve the validated Docker Desktop CPU
baseline, and expose Podman/GPU validation only as support-assigned optional
tracks.

The primary deliverable is a Microsoft Word RC1 UAT User Guide that consolidates
the current quick start, pilot checklist, issue-report guidance, and selected
handoff values into a user-facing walkthrough. The guide should be supported by
a smaller issue-report form and any process/script updates needed to make the
instructions genuinely simple.

## Background

Owner review of the current UAT materials found that the package instructions
are technically correct but still assume too much command-line and file-path
knowledge. Specific pain points:

- The tester does not get a simple mental model of the UAT process before
  seeing commands.
- Download and extraction instructions do not clearly distinguish the
  Application Package ZIP, checksum sidecars, and the Model & Data Package ZIP.
- The two-path explanation for package-folder versus Downloads-folder asset ZIP
  handling creates avoidable file-path reasoning.
- Manual checksum verification with `Get-FileHash` or `certutil` is hard to
  justify to non-technical testers unless bootstrap handles it automatically.
- The current guided bootstrap command is still more technical than the desired
  first-cohort experience.
- Optional Podman and GPU validation should be available to assigned testers,
  but should not compete with the required Docker Desktop CPU baseline.

An owner-supplied GPT-generated artifact packet was reviewed as a non-authority
reference. It usefully attempted to consolidate the materials, but it still
largely repackaged the same complexity and moved too quickly into
download/checksum/bootstrap mechanics.

## Requirements (EARS Notation)

**R-080-001**: WHEN the first UAT cohort receives tester materials, THE PROJECT
SHALL provide one primary RC1 UAT User Guide in Microsoft Word format that
walks through the process from start to finish.

**R-080-002**: WHEN the guide introduces UAT, THE PROJECT SHALL explain the
goal, supported baseline path, expected time/effort, files involved, and final
result categories before asking the tester to run commands.

**R-080-003**: WHEN the tester downloads release files, THE GUIDE SHALL explain
the four files using plain terms and SHALL tell the tester to keep them in one
working folder.

**R-080-004**: WHEN the tester extracts files, THE GUIDE SHALL state that only
the Application Package ZIP is extracted for the normal path and that the Model
& Data Package ZIP remains unextracted unless support assigns the manual
fallback.

**R-080-005**: WHEN checksum verification is needed for the normal path, THE
SYSTEM OR GUIDE SHALL prefer automated verification inside the setup/bootstrap
flow and reserve manual `Get-FileHash` or `certutil` checks for support
fallback.

**R-080-006**: WHEN a first-cohort tester starts TowerScout on the required
baseline path, THE GUIDE SHALL present one default path: Docker Desktop,
`-Gpu off`, and the owner-selected public smoke fixture.

**R-080-007**: WHEN Podman or GPU validation is desired, THE GUIDE SHALL expose
those as support-assigned optional validation tracks after the required
baseline succeeds.

**R-080-008**: WHEN the optional Podman track is used, THE GUIDE SHALL capture
Podman version, machine status, Compose provider, selected port, readiness
state, and smoke-test outcome.

**R-080-009**: WHEN the optional GPU track is used, THE GUIDE SHALL capture GPU
mode, Docker/NVIDIA readiness, non-secret `ml_runtime` readiness details,
timing, result counts, and CPU/GPU parity notes.

**R-080-010**: WHEN the tester reports a blocked or failed run, THE MATERIALS
SHALL collect support-safe evidence without asking for API keys, full `.env`
files, raw logs, raw provider responses, tile/map URLs, private AOI screenshots,
or unredacted browser/network traces.

**R-080-011**: WHEN a Word guide is produced, THE PROJECT SHALL render and
visually inspect the `.docx` before treating it as ready for tester send, or
explicitly record why render QA could not be completed.

**R-080-012**: IF process simplification requires launcher/script changes, THEN
THE PROJECT SHALL update package docs, UAT instructions, and validation coverage
before replacing the external tester instructions.

## Acceptance Criteria

- [x] A consolidated RC1 UAT User Guide `.docx` exists and is suitable as the
      primary first-cohort tester artifact.
- [x] The guide starts with a plain-language process overview before technical
      setup steps.
- [x] The guide uses one recommended working-folder model for release files and
      avoids making normal users choose between relative and full-path commands.
- [x] Extraction instructions clearly state which ZIP is extracted and which ZIP
      stays unextracted for the normal path.
- [x] Manual checksum commands are moved to support/fallback context unless
      owner chooses to keep them as an explicit user-facing verification step.
- [x] The required baseline test is Docker Desktop plus CPU mode (`-Gpu off`)
      with the owner-selected public Azure smoke fixture.
- [x] Optional Podman and GPU tracks are included after the baseline path and
      are clearly marked support-assigned.
- [x] Optional Podman/GPU evidence fields are defined without overstating
      validated support claims.
- [x] The issue-report material is reduced to a concise support-safe form or
      appendix.
- [x] Any `setup-towerscout.cmd` / bootstrap auto-discovery changes needed for
      the simplified guide are implemented or explicitly deferred.
- [x] Markdown/HTML/package-local docs are updated to stay consistent with the
      Word guide where they remain tester-facing.
- [x] The Word guide is rendered to page images and visually inspected, or render
      QA limitations are documented.
- [x] `.agent_work` validation passes after task/documentation updates.

## Dependencies

- `TASK-066`: final RC package/image/assets validation and residual support
  caveats.
- `TASK-071`: existing package docs and Settings-linked user guide surfaces.
- `TASK-073`: UAT execution plan, handoff packet, issue workflow, and first
  cohort support boundaries.
- `TASK-074`: bootstrap/preflight behavior and potential follow-up for a simpler
  `setup-towerscout.cmd` entry point or asset ZIP auto-discovery.
- `TASK-075`: optional GPU mode behavior, readiness diagnostics, and support
  claim boundaries.
- `TASK-076`: provider-key exposure/restriction policy, if provider-key wording
  needs owner/legal review before tester send.

## Proposed Deliverables

1. **RC1 UAT User Guide `.docx`**
   - Primary tester-facing guide.
   - Uses a "what you are doing / why it matters / exact action / expected
     result" rhythm.
   - Includes the required baseline path first.
   - Includes optional Podman and GPU validation tracks only after the baseline.

2. **RC1 UAT Issue Report Form `.docx`**
   - Short support-safe form for blocked or failed runs.
   - Can replace or supersede the current long text checklist for external
     testers while preserving detailed internal triage guidance.

3. **UAT Process Source Updates**
   - Update `docs/v1-rc1-quick-start.md` and matching HTML only if still
     tester-facing after the Word guide is introduced.
   - Update `.agent_work/user-testing/instructions/RC1-PILOT-UAT-CHECKLIST.md`
     to point to the Word guide or become the internal checklist behind it.
   - Keep `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md`
     coordinator-facing only.

4. **Optional Launcher Simplification**
   - Evaluate a top-level `setup-towerscout.cmd` wrapper.
   - Default to Docker Desktop and `-Gpu off`.
   - Auto-discover the Model & Data Package ZIP in the package folder or parent
     working folder when exactly one matching asset ZIP is present.
   - Verify checksum sidecars automatically.
   - Stop with plain-language guidance when zero or multiple candidate asset
     ZIPs are found.
   - Keep explicit `-Engine podman`, `-Gpu auto`, and `-Gpu on` options for
     support-assigned validation tracks.

## Proposed User-Facing Flow

1. Tester receives one UAT User Guide, release link, support contact, provider
   key expectations, and assigned validation track.
2. Tester creates one `TowerScoutUAT` folder.
3. Tester downloads all four release files into that folder.
4. Tester extracts only `towerscout-v0.1.0-rc2.zip`.
5. Tester opens the extracted folder and runs the simplified setup command.
6. Setup verifies files, imports assets, starts TowerScout, and opens
   `http://localhost:5000`.
7. Tester completes Setup Wizard with an approved provider key.
8. Tester runs the required public smoke fixture and records the result.
9. If assigned, tester runs optional Podman or GPU validation after the baseline.
10. Tester submits pass/fail/blocker evidence using the support-safe form.

## Implementation Plan

1. **Process Design**
   - Decide whether the first-cohort normal path should require manual checksum
     commands or rely on bootstrap/setup verification.
   - Decide whether to introduce `setup-towerscout.cmd` for UAT.
   - Decide the exact working-folder model and command surface.

2. **Launcher / Bootstrap Follow-Through**
   - If selected, implement the simplified wrapper and asset ZIP auto-discovery.
   - Preserve existing `bootstrap.cmd` for support and advanced usage.
   - Add focused tests for auto-discovery, ambiguity handling, checksum fallback,
     Docker default, Podman override, and GPU mode pass-through.

3. **Guide Authoring**
   - Draft the `.docx` from current authoritative docs, not from the GPT artifact
     packet alone.
   - Use the current handoff values from
     `.agent_work/user-testing/instructions/RC1-PILOT-HANDOFF-PACKET.md`.
   - Use a compact reference-guide design suited to a step-by-step operator
     manual.

4. **Issue Form Simplification**
   - Convert `TESTER-ISSUE-REPORT-CHECKLIST.txt` into a shorter Word form.
   - Keep detailed internal evidence rules in `.agent_work/user-testing/`.

5. **Docs Synchronization**
   - Update Markdown/HTML docs only after process decisions are settled.
   - Keep package-local docs and Word guide aligned on supported/unsupported
     paths.

6. **Validation**
   - Run focused tests for any script changes.
   - Run docs command checks and `.agent_work` validation.
   - Render the `.docx` and inspect every page before delivery.
   - If the simplified setup command changes package behavior, run a package-path
     bootstrap smoke before tester send.

## Boundaries And Support Language

- Docker Desktop with CPU mode remains the required first-cohort baseline.
- Podman is a support-assigned validation track, not the default external
  tester path.
- GPU is a support-assigned validation track after CPU baseline success; GPU
  claims remain bounded until NVIDIA Docker Desktop WSL2 validation, fixed
  fixture parity, and timing evidence pass.
- Do not claim Docker-Desktop-free Podman support beyond recorded evidence.
- Do not claim offline/restricted-network support for the normal UAT path.
- Do not ask testers to use private investigation AOIs for the first smoke test.
- Do not ask testers to send secrets, raw logs, raw screenshots, raw provider
  responses, tile/map URLs, or private AOI evidence without an approved handling
  procedure.

---

## Implementation Log

### 2026-06-01 - Task Created
**Objective**: Record the owner-approved direction for simplifying the RC1 UAT
process and producing a consolidated Word-based UAT User Guide.
**Context**: Owner feedback on the current quick start, UAT checklist, handoff
packet, issue checklist, and GPT-generated artifact packet showed that the
tester materials remain too technical for a typical first-cohort UAT user.
**Decision**: Track the work as a new Sprint 06 task because it may require both
documentation restructuring and launcher/bootstrap follow-through before
external tester send.
**Execution**: Created this task file and registered it in
`.agent_work/current-tasks.md`.
**Output**: Planning task ready for owner review.
**Validation**: Pending `.agent_work` validation.
**Next**: Confirm whether to implement `setup-towerscout.cmd` / asset ZIP
auto-discovery before drafting the final Word guide, then begin the selected
implementation path.

### 2026-06-01 - Setup Wrapper And Docs Alignment Started
**Objective**: Reduce the first-cohort setup path to one normal command while
preserving support-assigned Podman and GPU validation tracks.
**Decision**: Implement `setup-towerscout.cmd` as the normal tester command.
Keep `bootstrap.cmd` as the advanced explicit-path support helper.
**Execution**: Added a setup wrapper that defaults to Docker Desktop and
`-Gpu off`, auto-discovers matching release ZIPs from the extracted package
folder or parent UAT folder, requires checksum sidecars, and delegates to the
existing bootstrap path. Updated package contents, quick start, package guide,
UAT checklist, handoff packet, issue checklist, project overview, OCI docs, and
release asset-bundle contract around the simplified flow.
**Output**: Normal user flow is now: create `TowerScoutUAT`, download all four
files, extract only the Application Package ZIP, open the extracted folder, run
`setup-towerscout.cmd`.
**Validation**: `tests/unit/test_task_074_bootstrap.py`, `.agent_work`
validation, agent-work quick check, docs command check, and `git diff --check`
passed on 2026-06-01. Docs command check retained the pre-existing warning
that `docs/oci-quick-start.md` mentions `127.0.0.1`.
**Next**: Draft and render the consolidated Word UAT User Guide plus concise
issue-report form.

### 2026-06-01 - Consolidated Word UAT Guide Created
**Objective**: Create the first consolidated Word artifact for first-cohort UAT.
**Decision**: Store the guide beside the existing UAT instruction materials at
`.agent_work/user-testing/instructions/TowerScout_V1_RC1_UAT_User_Guide.docx`
and link it from the UAT instructions README.
**Execution**: Generated a compact reference-guide style Word document covering
the UAT purpose, prerequisites, four release files, one-folder setup flow,
`setup-towerscout.cmd`, provider setup, public Azure smoke fixture, optional
Podman/GPU tracks, blocked-run evidence, stop/restart commands, and explicit
ZIP-path fallback.
**Output**: `TowerScout_V1_RC1_UAT_User_Guide.docx` added.
**Validation**: DOCX package XML parsed successfully and a custom OOXML audit
confirmed required setup, Podman, GPU, safety, table, numbering, and heading
content. Render QA was attempted with the Documents renderer, but could not be
completed because this environment is missing `pdf2image`, LibreOffice
`soffice`, and a Word command/COM path. This limitation is recorded instead of
claiming visual render approval.
**Next**: Owner review the Word guide content/layout in Microsoft Word, then
decide whether a separate shorter `.docx` issue form is still needed or whether
the guide appendix plus updated text checklist is sufficient.

### 2026-06-01 - Word Guide Owner Review Edits Promoted
**Objective**: Apply owner review notes to the Files You Download, Default
Setup Steps, and Stop/Restart sections.
**Execution**: The revised copy was promoted over
`.agent_work/user-testing/instructions/TowerScout_V1_RC1_UAT_User_Guide.docx`.
The official guide now bolds the GitHub Code/source ZIP warning, adds a Purpose
column to the release-file table, changes the default working-folder example to
`Documents\TowerScoutUAT`, explains copying files from Downloads into that
working folder, clarifies the expected folder structure after extracting only
the Application Package ZIP, and states where stop/restart commands should be
run.
**Validation**: Revised DOCX XML parsed successfully; structural audit confirmed
the new Purpose column, Documents-path examples, download-copy instruction,
extraction folder-shape wording, stop/restart command location, setup command,
and table count. A targeted OOXML check confirmed the GitHub Code/source ZIP
warning sentence is in a bold run. Render QA was attempted but failed because
the local Documents renderer still cannot import `pdf2image`.
**Next**: Complete Markdown/HTML alignment and run final validation before
image/package refresh.

### 2026-06-01 - Pre-Rebuild UAT Material Alignment Completed
**Objective**: Finalize the UAT guide artifact name and align package-facing
Markdown/HTML docs before rebuilding/publishing image and package artifacts.
**Decision**: Keep the Word UAT guide outside the release package for now. The
official artifact is
`.agent_work/user-testing/instructions/TowerScout_V1_RC1_UAT_User_Guide.docx`.
**Execution**: Replaced the original Word guide with the reviewed copy and
removed the temporary revised copy. Updated the UAT README link back to the
official guide filename. Aligned `docs/v1-rc1-quick-start.md`, its HTML copy,
`docs/v1-rc1-package-guide.md`, the UAT checklist, and the handoff packet to
the `C:\Users\<you>\Documents\TowerScoutUAT` working-folder model with a
copy-from-Downloads step.
**Validation**: Official DOCX structural audit passed; targeted OOXML check
confirmed the GitHub Code/source ZIP warning is bold. Search confirmed no
remaining old Downloads-based `TowerScoutUAT` paths or revised-DOCX references
in user-facing docs/task records. Search confirmed `scripts/package-release.ps1`
does not include the Word guide, so it remains outside the package.
**Next**: Re-run full focused validations, then rebuild/publish image and
regenerate the Application Package ZIP when owner approves the release refresh.

### 2026-06-01 - PR Review Explicit-Path Fix
**Objective**: Address reviewer finding that explicit `-AssetZip` and
`-PackageZip` support paths could fail because setup helpers passed `-Label` to
`Resolve-TowerScoutBootstrapPath` before that parameter existed.
**Execution**: Added optional `Label` support to
`Resolve-TowerScoutBootstrapPath` with a clearer blank-path error and added
unit coverage that calls both `Find-TowerScoutSetupAssetZip -AssetZip` and
`Find-TowerScoutSetupPackageZip -PackageZip`.
**Validation**: `tests/unit/test_task_074_bootstrap.py` and
`tests/unit/test_release_package_script.py` passed with 16 tests. `.agent_work`
validation, agent-work quick check, docs command scan, and `git diff --check`
also passed. Docs command scan retained the existing
`docs\oci-quick-start.md:158` `127.0.0.1` warning.
**Next**: Push the PR fix, then complete owner/reviewer signoff and Word visual
inspection before marking PR #30 ready for merge.

---

## Validation Results

### Test Summary
**Test Date**: 2026-06-01  
**Test Environment**: Windows workspace, Python 3.12.5 virtual environment,
PowerShell helpers  
**Test Status**: PASS for setup-wrapper/docs-alignment slice and structural
DOCX QA; visual render QA blocked by missing local renderer dependencies

### Acceptance Criteria Validation

Partial. Setup wrapper, Markdown/HTML/package-local alignment, and consolidated
Word guide structural QA passed. A separate Word issue form remains optional
pending owner decision.

Commands run:

- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_task_074_bootstrap.py tests\unit\test_release_package_script.py -q`
  - 16 passed.
- `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py`
  - passed.
- `.\.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`
  - passed.
- `.\.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md`
  - passed with the existing `docs\oci-quick-start.md:158` `127.0.0.1`
    warning.
- `git diff --check`
  - passed.
- `python C:\Users\bg90\.codex\plugins\cache\openai-primary-runtime\documents\26.518.11428\skills\documents\render_docx.py .agent_work\user-testing\instructions\TowerScout_V1_RC1_UAT_User_Guide.docx --output_dir .agent_work\user-testing\instructions\rendered\TowerScout_V1_RC1_UAT_User_Guide --emit_pdf`
  - failed because `pdf2image` is not installed.
- Custom DOCX XML/OOXML structural audit
  - passed.

### Issues Identified

- Visual render QA for the Word guide could not be completed in this
  environment because the renderer dependencies are unavailable.
- A separate Word issue-report form has not been created yet; the guide now
  includes a concise blocked-run evidence appendix, and the existing text issue
  checklist was shortened/aligned.
- The published RC package may require a refreshed package if launcher changes
  are selected.

### Remediation Actions

Pending process decision and implementation.

### Sign-off

Not signed off. Owner/reviewer acceptance is required before replacing the
current external tester handoff materials.
