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

## Pre-UAT Approval Follow-Up Requests

Owner review on 2026-06-09 identified the following changes to address before
approving the first external UAT cohort. These stay under `TASK-080` unless the
runtime work grows large enough to split into a separate stale-container task.

- [x] **Setup-step engine reminder**: Add a clear note in the Word UAT User
      Guide's Default Setup Steps between steps 4 and 5 telling testers to
      confirm Docker Desktop or Podman is open and running before setup. Include
      the nearby note: see the "Docker GPU Track" section below for the Docker
      GPU setup command.
- [x] **Command appendix**: Add a command-reference appendix to the Word UAT
      User Guide and mirror it in `docs/v1-rc1-quick-start.md`. Include setup,
      start/reopen, stop, restart, status, and logs commands for Docker CPU,
      Docker GPU, and Podman CPU. Keep Podman and GPU language
      support-assigned, with GPU defaulting to Docker-only unless new evidence
      expands support.
- [x] **UAT session lifetime and stale-container handling**: Implement a
      launch-time stale-container guard for first-cohort UAT. Reuse/open a
      healthy TowerScout container younger than 12 hours; stop/remove and start
      fresh when the existing container is stopped, unhealthy, or older than 12
      hours. Preserve named volumes by default so saved setup, imported assets,
      and support logs are not deleted. Provide a support/admin override for
      longer validation sessions.
- [x] **Settings research article link**: Replace the Settings Resource Links
      "TowerScout Research Article" URL with
      `https://pubmed.ncbi.nlm.nih.gov/38906615/`.
- [x] **Google first-launch verification**: Re-test the Setup Wizard first-load
      Google Maps key path with a support-approved key after the validation UX
      patch, without recording key material, raw provider responses, browser
      network traces, or screenshots that expose sensitive data.
- [x] **In-app status/output panel review**: Review the messages visible in the
      TowerScout in-app status/output panel with debug mode disabled. Ensure the
      messages are concise, useful to non-technical testers, and do not create
      confusion between map imagery, geocoding, and local detection. When both
      providers are configured, messages should identify the provider used for
      the relevant action.
- [x] **Tester feedback form**: Replace or supplement the long issue checklist
      with a short email/Teams-friendly tester form. Collect pass/fail/blocker
      status, guide step, command or button used, exact error text, safe
      screenshot availability, engine, port, provider, setup-save status, and
      optional fixture details without asking for secrets, raw logs, private
      AOIs, raw provider responses, or browser network traces.

Supplemental GIF/video guidance is intentionally not tracked here. The owner may
provide a short demo video separately if the client wants one.

## Pre-UAT Coverage Additions

The 2026-06-09 follow-up work should add focused coverage for the higher-risk
changes instead of broad new end-to-end test scope.

- [x] **Stale-container decision tests**: Cover no existing container,
      healthy container younger than 12 hours, healthy container older than 12
      hours, stopped/created container, unhealthy container, non-TowerScout port
      conflict, and support/admin override behavior without requiring a live
      Docker or Podman engine.
- [x] **Runtime command safety tests**: Confirm the stale-container path does
      not remove named volumes by default and does not invoke destructive volume
      cleanup such as `down -v` or `volume rm`.
- [x] **DOCX structural tests**: Extend or add a Word-guide audit that confirms
      the Docker/Podman-running note, Docker GPU cross-reference, command
      appendix, PubMed URL, tester feedback fields, and support-safe evidence
      restrictions are present.
- [x] **Quick-start command scan**: Run the docs command checker after mirroring
      the command appendix in `docs/v1-rc1-quick-start.md`.
- [x] **In-app status/output panel contract test**: Add focused frontend
      coverage that verifies normal debug-off user messages remain concise and
      provider-aware where the message is shown in the in-app output panel.
- [x] **Settings link test**: Add a route/template assertion that the Research
      Article resource link points to
      `https://pubmed.ncbi.nlm.nih.gov/38906615/`.
- [x] **Package-path smoke**: After launcher/runtime changes, run a focused
      Docker CPU setup/start/status/stop validation if the local runtime
      environment allows it. This complements unit tests by checking script
      wiring.
- [x] **TLS CA helper persistence test**: Confirm the TLS CA import helper
      persists the safe `REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` paths in the
      local `.env` after successful import so support users do not need to
      remember session-only environment variables.

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

### 2026-06-02 - RC2 Package Generated And Local Docker Path Checked
**Objective**: Move the corrected UAT package to `v0.1.0-rc2` after
`v0.1.0-rc1` had already been published from an older source ref.
**Execution**: Updated package-facing UAT references to `v0.1.0-rc2`, pushed
source ref `4e8054d27faa1f956998f85b665a4ea28fc01ed9`, published the
`v0.1.0-rc2-cuda121` GHCR image, generated the rc2 Application Package ZIP,
and copied the unchanged asset bundle under an rc2-matching filename with a new
checksum sidecar.
**Output**:
- Application Package ZIP: `dist\towerscout-v0.1.0-rc2.zip`
- Application Package SHA-256:
  `f3ec4eef0b47c4276d671bac1cf75fa85e515ce386cfa38976daba070cc3f51c`
- Model & Data Package ZIP:
  `dist\towerscout-v0.1.0-rc2-assets-towerscout-v1-assets-2026-05-05.zip`
- Model & Data Package SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
- Image:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc2-cuda121@sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`
**Validation**: Package summary found 47 expected files. Release-manifest
check passed with the known non-blocking recommended-field warnings. Both ZIP
checksum sidecars matched. A clean `TowerScoutUAT` folder setup run found both
rc2 ZIPs, verified both checksum sidecars, confirmed the rc2 release manifest,
pulled the pinned image, staged and imported assets with hash verification,
started TowerScout on isolated port `5011`, reached `setup_required` with
assets `ok`, served package-local docs and `/license`, and was stopped after
evidence capture.
**Gap**: Detection smoke was not run in the isolated stack because no provider
key was configured; readiness correctly reported setup-required mode.
**Next**: Superseded by the uploaded/downloaded release-validation entry below;
complete bounded Azure smoke after support-approved provider setup.

### 2026-06-02 - RC2 GitHub Release Uploaded And Download-Validated
**Objective**: Validate the actual GitHub release assets, not only the local
`dist` package files.
**Execution**: Created the GitHub prerelease
`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc2` at source
ref `4e8054d27faa1f956998f85b665a4ea28fc01ed9`, uploaded the four expected rc2
assets, downloaded those release assets into
`dist\release-download-validation-rc2-20260602`, verified both downloaded
checksum sidecars, extracted only the downloaded Application Package ZIP, and
ran the simplified setup command from the downloaded files.
**Output**:
- GitHub release: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc2`
- Downloaded Application Package SHA-256:
  `f3ec4eef0b47c4276d671bac1cf75fa85e515ce386cfa38976daba070cc3f51c`
- Downloaded Model & Data Package SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
**Validation**: Downloaded-release setup used isolated
`COMPOSE_PROJECT_NAME=towerscout-task080-rc2-download` on port `5012`, found
both downloaded rc2 ZIPs, verified both sidecars, confirmed the rc2 release
manifest, reused the pinned image, imported assets with hash verification,
reached readiness `setup_required` with assets `ok`, served package-local docs
and `/license`, and was stopped after evidence capture.
**Gap**: Superseded by the provider-smoke entry below. Owner/reviewer signoff
and tester/cohort selection remain pending before external handoff.
**Next**: Record provider setup and bounded Azure smoke evidence, then record
owner/reviewer approval before sending the UAT materials.

### 2026-06-02 - RC2 Provider Setup And Bounded Azure Smoke Passed
**Objective**: Complete the remaining rc2 release-path validation gate by
proving provider setup and a bounded Azure detection smoke on the downloaded
GitHub release assets.
**Execution**: Started the downloaded rc2 package with isolated
`COMPOSE_PROJECT_NAME=towerscout-task080-rc2-provider` on port `5013`, imported
assets with hash verification, had the release owner enter the Azure Maps key
through the browser Setup Wizard, verified readiness without recording key
material, and ran the owner-selected public Azure smoke fixture.
**Output**:
- Fixture: `RC1 Azure 200 West Street 150 m smoke`
- Provider: Azure Maps
- Search/location: `200 west st, New York, NY 10282`
- Shape/radius: circle, `150 meters`
- Tile estimate: `8` tiles, expected time `44` seconds
- Detection result: completed successfully with `48` detection records and
  `8` tile records
- Address result: address/provider metadata appeared in the right-hand panel
- Elapsed time: about `56.38` seconds
**Validation**: `/api/readiness` returned `state=ready`, `assets.status=ok`,
`config.status=ok`, Azure configured, default provider `azure`,
`runtime.device_policy=cpu`, `runtime.pytorch_flavor=cuda121`,
`runtime.selected_device=cpu`, and image digest
`sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`.
The isolated provider-smoke stack was stopped after evidence capture.
**Secret handling**: The Azure Maps key was entered only in the browser Setup
Wizard. No key value, `.env`, raw logs, screenshots, tile/map URLs, browser
traces, or raw provider responses were recorded.
**Gap**: Owner/reviewer signoff and tester/cohort selection remain pending
before external handoff.
**Next**: Record owner/reviewer approval and tester/cohort, then update
`Approved for tester use` when the release owner approves the handoff packet.

### 2026-06-03 - First-Cohort Google Setup Validation Feedback Hardened
**Objective**: Triage first-cohort UAT feedback where a tester following the UAT
guide entered a Google Maps key on first launch and the Setup Wizard reported a
generic provider-validation 502.
**Context**: The browser showed repeated `/api/config/validate-key` `502`
responses and the user-facing message `Could not reach the provider validation
service.` No backend logs, provider responses, screenshots, raw network traces,
or key material were added to the task evidence.
**Decision**: Keep live provider validation required for normal setup, but make
local runtime network/TLS failures actionable and support-safe. Also avoid
letting one failed provider check block validation of another entered provider.
**Execution**: Added provider-specific network, timeout, and TLS validation
messages in `webapp/ts_config.py`; updated the Setup Wizard to validate Google
and Azure independently and save only keys that validated in that wizard run;
removed provider-key previews from key-serving route logs and Azure browser
format warnings; rebuilt `webapp/js/towerscout.js`; added route/config/frontend
contract coverage.
**Validation**: Passed `.venv\Scripts\python.exe -m pytest
tests/unit/test_config.py tests/unit/test_flask_routes.py
tests/unit/test_error_sanitization.py tests/unit/test_logging_sanitization.py
-q -p no:cacheprovider`; `node
tests/frontend/test_setup_wizard_validation_contract.js`; `node
tests/frontend/test_global_contract.js`; `node
tests/frontend/test_debug_logging_contract.js`; `node
tests/frontend/test_task_079_frontend_contract.js`; frontend bundle consistency
check; and `git diff --check`.
**Secret handling**: The fix and tests use synthetic keys only. The task did not
store raw screenshots, provider responses, `.env` contents, raw browser network
traces, or real provider key values.
**Next**: Superseded by the 2026-06-09 Google TLS support-path verification
entry below.

### 2026-06-09 - Pre-UAT Approval Follow-Up Plan Recorded
**Objective**: Capture owner follow-up requests that must be addressed before
approving the first external UAT cohort.
**Decision**: Keep the work under `TASK-080` because the requests are primarily
UAT guide, quick-start, status-message, setup-verification, and tester-feedback
readiness items. Split stale-container handling into a new task only if the
launcher change grows beyond a focused UAT session-lifetime guard.
**Plan**: Add the setup-step engine reminder, command appendix in both the Word
guide and markdown quick start, a 12-hour UAT stale-container guard that
preserves named volumes, the corrected PubMed research link, live Google
first-launch verification, in-app status/output panel review, and a concise
email/Teams-friendly tester feedback form.
**Out of scope**: A GIF or demo video is not tracked in this task. The owner may
provide supplemental video guidance separately if the client requests it.
**Validation**: Pending implementation.
**Next**: Implement the pre-UAT follow-up checklist, refresh any affected
package-facing docs, validate launcher/docs behavior, and record evidence before
owner/reviewer signoff.

### 2026-06-09 - Pre-UAT Follow-Up Implementation Slice Completed
**Objective**: Implement the owner-approved follow-up requests that reduce
first-run confusion before external UAT approval.
**Execution**: Updated the Word UAT guide, Markdown/HTML quick start, UAT
checklist, handoff packet, and tester issue form. Added the Docker/Podman
running reminder, Docker GPU cross-reference, command appendix, 12-hour UAT
session guidance, corrected PubMed research link, concise email/Teams issue
form, and provider-aware in-app status/output messages. Implemented a
launch-time stale-container guard for `launch.ps1`, `bootstrap.ps1`,
`setup-towerscout.ps1`, and `import-assets.ps1`; it reuses healthy containers
younger than 12 hours, restarts stopped/unhealthy/stale containers, and avoids
named-volume removal by default.
**Coverage Added**: Added unit coverage for stale-container decisions and
runtime safety, DOCX/quick-start structural coverage for the guide changes, a
route/template assertion for the PubMed link, and a frontend status/output
contract test for provider-aware normal-mode messages.
**Validation**: Rebuilt `webapp/js/towerscout.js`. Focused unit/frontend/docs
checks passed, `.agent_work` validation passed, `git diff --check` passed, and
an isolated Docker CPU package-path start/status/stop smoke on port `5014`
reached the expected `setup_required` state with the validation container
stopped afterward.
**Secret Handling**: The implementation and tests use synthetic placeholder
values only. No real provider key values, `.env` contents, raw provider
responses, browser network traces, tile URLs, or sensitive screenshots were
recorded.
**Gap**: Superseded by the Google TLS support-path entry below. The current RC
package still needs to be regenerated before external tester handoff because
launcher/docs/frontend files changed after the published rc2 package was built.
**Next**: Complete the Google first-launch verification record, then
rebuild/package the approved RC artifact set before external UAT send.

### 2026-06-09 - Google First-Launch TLS Support Path Verified
**Objective**: Determine whether the repeated first-launch Google Setup Wizard
failure was a Google key issue, an application issue, or a managed-network TLS
trust issue.
**Evidence**: An isolated Docker validation stack on port `5015` initially
failed Google provider validation with `CERTIFICATE_VERIFY_FAILED` against
Google APIs. The exported website certificate was an end-entity certificate,
not a CA. The matching Windows CA was `CDC-G2-ZSH`. After importing that CA
with `scripts\import-tls-ca.cmd`, the helper verified Google TLS with an
invalid test key and returned the expected invalid-key provider response rather
than a certificate failure.
**Execution**: The release owner then entered the support-approved Google Maps
key through Setup Wizard. Google setup saved successfully; readiness showed
Google configured and the default provider set to Google. No key material, raw
provider response, browser network trace, `.env` contents, or sensitive
screenshot was recorded.
**Follow-Up Fix**: Updated `scripts\import-tls-ca.ps1` so a successful CA
import also writes the safe, non-secret `REQUESTS_CA_BUNDLE` and
`SSL_CERT_FILE` paths into the local `.env`. Updated the Word UAT guide, UAT
quick start, package guide, and OCI docs to explain the managed-network TLS
case and the support CA-import path.
**Validation**: Added static coverage for TLS CA helper `.env` persistence,
quick-start TLS support guidance, and Word guide TLS support content. Passed
focused TLS/docs tests, provider/log safety tests, docs command scan,
`.agent_work` validation, and `git diff --check`.
**Assessment**: The Google first-launch path is functionally verified. UAT
testers on managed networks with TLS inspection may still encounter provider
validation failures until support imports the site CA. This is now a known,
documented support path rather than an unresolved Google key defect.
**Gap**: The RC package still needs to be regenerated so testers receive the
key-log hardening, stale-container guard, provider-aware messages, TLS helper
persistence, and updated docs.
**Next**: Rebuild/package the approved RC artifact set before external UAT
send, then complete owner/reviewer signoff and tester/cohort selection.

### 2026-06-10 - Owner-Edited Word Guide Integrated
**Objective**: Incorporate the owner-edited Word UAT guide with formatting and
readability improvements while preserving command, TLS, and support-safe
evidence content.
**Input**: Owner-provided
`TowerScout_V1_RC1_UAT_User_Guide_Edited.docx` and
`Word UAT User guide changes made_2026.06.10.md`.
**Execution**: Replaced the repository Word guide with the owner-edited copy.
An attempted low-level heading correction caused Microsoft Word to report
unreadable content, so the repository copy was restored byte-for-byte from the
Word-authored edited file. The first section heading is retained exactly as
saved by Word: `Purpose of User Acceptance Testing`. Preserved the command
appendix, managed-network TLS note, provider-key safety language,
issue-report form, and support-safe evidence restrictions.
**Validation**: Updated the structural DOCX contract to read paragraph text
rather than XML run fragments, then confirmed the edited guide contains the
required setup, Docker GPU, Podman, TLS CA import, command appendix, PubMed,
issue-form, and support-safe evidence content. The restored repository DOCX
SHA-256 matches the owner-edited source DOCX:
`D3493B46D021CEF3021E3756544161A711CE526F08C5A893F6877965A2583D61`.
The focused DOCX/quick-start structural test passed.
**Render QA**: Automated DOCX render was attempted with the Documents renderer
but failed because `pdf2image` is not installed in this environment. Owner
completed human visual review in Microsoft Word on 2026-06-11 and confirmed the
guide looks good for lock/final validation.
**Next**: Run final validation, then rebuild/package the approved RC artifact
set before external UAT send.

### 2026-06-11 - Pre-Package Final Validation Passed
**Objective**: Lock the owner-reviewed Word UAT guide and run final focused
validation before refreshing release package artifacts.
**Execution**: Owner confirmed the Word guide looks good in Microsoft Word and
approved locking it for final validation. Ran focused runtime, docs, provider
validation, release packaging, frontend contract, bundle consistency,
agent-work, whitespace, and secret-safety checks.
**Validation**:
- `tests\unit\test_task_074_bootstrap.py`,
  `tests\unit\test_import_assets_script.py`,
  `tests\unit\test_task_080_uat_followups.py`,
  `tests\unit\test_flask_routes.py`, `tests\unit\test_config.py`,
  `tests\unit\test_error_sanitization.py`, and
  `tests\unit\test_logging_sanitization.py`: 81 passed.
- `tests\unit\test_release_package_script.py`,
  `tests\unit\test_release_manifest_schema.py`,
  `tests\unit\test_license_notices.py`, and
  `tests\unit\test_container_publish_workflow.py`: 12 passed.
- Frontend contracts passed:
  `test_status_output_contract.js`,
  `test_setup_wizard_validation_contract.js`,
  `test_debug_logging_contract.js`, `test_global_contract.js`, and
  `test_task_079_frontend_contract.js`.
- Frontend bundle consistency check passed; both source and generated bundle are
  changed and consistent.
- Docs command scan passed with the existing non-blocking
  `docs\oci-quick-start.md:158` `127.0.0.1` warning.
- `.agent_work` validation passed.
- `git diff --check` passed.
- Targeted changed-file secret scan found only synthetic test placeholders used
  by redaction tests; a stricter non-test source/docs scan found no key-like
  matches. The Word guide text scan found zero Google key, Azure key, or
  `FLASK_SECRET_KEY` matches.
**Result**: PASS for final pre-package validation.
**Remaining Gate**: Regenerate and validate refreshed RC package artifacts so
external testers receive the locked Word guide, stale-container guard,
provider-key/TLS hardening, provider-aware status messages, corrected PubMed
link, and updated UAT support materials.

---

## Validation Results

### Test Summary
**Test Date**: 2026-06-01 baseline; 2026-06-09 follow-up validation added;
2026-06-11 final pre-package validation passed
**Test Environment**: Windows workspace, Python 3.12.5 virtual environment,
PowerShell helpers  
**Test Status**: PASS for setup-wrapper/docs-alignment slice, structural DOCX
QA, 2026-06-09 follow-up changes, owner Word visual QA, and 2026-06-11 final
pre-package validation; automated visual render remains blocked by missing
local renderer dependencies

### Acceptance Criteria Validation

Partial. Setup wrapper, Markdown/HTML/package-local alignment, consolidated
Word guide structural QA, command appendix, stale-container guard, corrected
research link, concise issue form, and in-app status/output panel follow-up
passed focused validation. Live Google first-launch verification passed after
the managed-network TLS CA support path was applied.

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
- `.\scripts\package-release.cmd -Version v0.1.0-rc2 -OutputDir dist -Image ghcr.io/j-schulein/towerscout:v0.1.0-rc2-cuda121 -ImageDigest sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946 -PytorchFlavor cuda121 -Force`
  - generated the rc2 Application Package ZIP and checksum.
- `.\.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\summarize_release_package.py dist\towerscout-v0.1.0-rc2.zip`
  - passed; 47 files found.
- `.\.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\check_release_manifest.py dist\towerscout-v0.1.0-rc2\release-manifest.v1.json dist\towerscout-v0.1.0-rc2`
  - passed with known recommended-field warnings.
- `.\setup-towerscout.cmd -Engine docker -Gpu off -Port 5011 -NoBrowser -TimeoutSeconds 240 -RestartWaitSeconds 180`
  - passed from the clean rc2 UAT folder with isolated
    `COMPOSE_PROJECT_NAME=towerscout-task080-rc2`; found both rc2 ZIPs,
    verified sidecars, imported assets with hash verification, pulled the
    pinned image, and reached readiness `setup_required` with assets `ok`.
- `Invoke-RestMethod http://localhost:5011/api/health`
  - returned `status=ok`.
- `Invoke-RestMethod http://localhost:5011/api/readiness`
  - returned `state=setup_required`, `assets.status=ok`,
    `runtime.device_policy=cpu`, `runtime.pytorch_flavor=cuda121`,
    `runtime.selected_device=cpu`, and image digest
    `sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`.
- `Invoke-WebRequest` for `/docs/project-overview.html`,
  `/docs/towerscout-user-guide.html`, `/docs/v1-rc1-quick-start.html`, and
  `/license`
  - all returned HTTP `200`.
- `.\scripts\status.cmd -Engine docker -Port 5011`
  - reported the isolated container healthy on
    `0.0.0.0:5011->5000/tcp` and readiness `setup_required`.
- `.\scripts\stop.cmd -Engine docker -Port 5011`
  - stopped the isolated validation stack.
- `gh release create v0.1.0-rc2 ... --repo J-Schulein/TowerScout --target 4e8054d27faa1f956998f85b665a4ea28fc01ed9 --prerelease --latest=false`
  - created the GitHub prerelease at
    `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc2` with
    the four expected rc2 assets.
- `gh release view v0.1.0-rc2 --repo J-Schulein/TowerScout`
  - confirmed the release is a prerelease and lists the Application Package
    ZIP/checksum plus Model & Data Package ZIP/checksum.
- `gh release download v0.1.0-rc2 --repo J-Schulein/TowerScout --dir dist\release-download-validation-rc2-20260602 --pattern 'towerscout-v0.1.0-rc2*'`
  - downloaded the four uploaded assets for final release-asset validation.
- Downloaded checksum sidecar verification
  - confirmed the Application Package checksum
    `f3ec4eef0b47c4276d671bac1cf75fa85e515ce386cfa38976daba070cc3f51c` and
    Model & Data Package checksum
    `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- `.\setup-towerscout.cmd -Engine docker -Gpu off -Port 5012 -NoBrowser -TimeoutSeconds 240 -RestartWaitSeconds 180`
  - passed from the downloaded release files with isolated
    `COMPOSE_PROJECT_NAME=towerscout-task080-rc2-download`; found both
    downloaded rc2 ZIPs, verified sidecars, imported assets with hash
    verification, reused the pinned image, and reached readiness
    `setup_required` with assets `ok`.
- `Invoke-RestMethod http://localhost:5012/api/health`
  - returned `status=ok`.
- `Invoke-RestMethod http://localhost:5012/api/readiness`
  - returned `state=setup_required`, `assets.status=ok`,
    `runtime.device_policy=cpu`, `runtime.pytorch_flavor=cuda121`,
    `runtime.selected_device=cpu`, and image digest
    `sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`.
- `Invoke-WebRequest` for the package docs and `/license` on port `5012`
  - all returned HTTP `200`.
- `.\scripts\status.cmd -Engine docker -Port 5012`
  - reported the downloaded-release validation container healthy on
    `0.0.0.0:5012->5000/tcp` and readiness `setup_required`.
- `.\scripts\stop.cmd -Engine docker -Port 5012`
  - stopped the downloaded-release validation stack.
- `.\start.bat -Engine docker -Gpu off -Port 5013 -NoBrowser -TimeoutSeconds 240`
  - started the isolated provider-smoke stack with
    `COMPOSE_PROJECT_NAME=towerscout-task080-rc2-provider`; first readiness was
    `setup_required` with empty engine-specific asset volumes, as expected for
    a fresh Compose project.
- `.\scripts\import-assets.cmd -Engine docker -Source assets -Port 5013 -VerifyHashes -RestartWaitSeconds 180`
  - imported the package-local assets into the isolated provider-smoke stack,
    restarted TowerScout, and verified `asset_status=ok`, `verify_hashes=True`,
    no missing assets, and no corrupt assets.
- Browser Setup Wizard on `http://localhost:5013`
  - release owner entered the approved Azure Maps key directly in the browser,
    selected Azure as the default provider, validated the key, and saved the
    configuration. The key value was not recorded.
- `Invoke-RestMethod http://localhost:5013/api/readiness`
  - returned `state=ready`, `assets.status=ok`, `config.status=ok`, Azure
    configured, default provider `azure`, `runtime.device_policy=cpu`,
    `runtime.pytorch_flavor=cuda121`, `runtime.selected_device=cpu`, and image
    digest
    `sha256:f3caa7915f7a8d70326b2fa84d62ec86e142c38c7d22615106e192d7f7821946`.
- User-recorded bounded Azure smoke result for `200 west st, New York, NY
  10282`, 150 m circle
  - estimate `8` tiles / `44` seconds; detection completed; processed `48`
    detection records and `8` tile records; address/provider metadata appeared
    in the right-hand panel; elapsed time about `56.38` seconds.
- `.\scripts\stop.cmd -Engine docker -Port 5013`
  - stopped the isolated provider-smoke stack.
- `python C:\Users\bg90\.codex\plugins\cache\openai-primary-runtime\documents\26.518.11428\skills\documents\render_docx.py .agent_work\user-testing\instructions\TowerScout_V1_RC1_UAT_User_Guide.docx --output_dir .agent_work\user-testing\instructions\rendered\TowerScout_V1_RC1_UAT_User_Guide --emit_pdf`
  - failed because `pdf2image` is not installed.
- Custom DOCX XML/OOXML structural audit
  - passed.
- `node webapp\build.js`
  - rebuilt `webapp/js/towerscout.js` with provider-aware status/output
    messages.
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_task_074_bootstrap.py tests\unit\test_task_080_uat_followups.py tests\unit\test_flask_routes.py -q -p no:cacheprovider`
  - 52 passed.
- `node tests\frontend\test_status_output_contract.js`
  - passed.
- `node tests\frontend\test_setup_wizard_validation_contract.js`
  - passed.
- `node tests\frontend\test_debug_logging_contract.js`
  - passed.
- `node tests\frontend\test_global_contract.js`
  - passed.
- `node tests\frontend\test_task_079_frontend_contract.js`
  - passed.
- `.\.venv\Scripts\python.exe -m pytest tests\unit\test_config.py tests\unit\test_error_sanitization.py tests\unit\test_logging_sanitization.py -q -p no:cacheprovider`
  - 26 passed.
- `.\.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md`
  - passed with the existing `docs\oci-quick-start.md:158` `127.0.0.1`
    warning.
- Targeted changed-file secret-pattern scan
  - found no literal provider keys in the changed docs, scripts, tests, or
    source files. A broad workspace scan was not useful because it hit known
    historical/config artifacts outside this slice.
- Isolated Docker CPU package-path start/status/stop smoke on port `5014`
  - passed script wiring checks and reached expected `setup_required`
    readiness with no provider/assets configured in the isolated stack; the
    validation container was stopped afterward.
- `.\.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py`
  - passed.
- `git diff --check`
  - passed.

### Issues Identified

- Visual render QA for the Word guide could not be completed in this
  environment because the renderer dependencies are unavailable.
- The separate Word issue-report form remains optional; the current follow-up
  replaced the long text checklist with an email/Teams-friendly issue form and
  mirrored the short form in the Word guide.
- Live Google first-launch setup passed after the managed-network TLS CA was
  imported. UAT testers on similar managed networks may still need the
  documented CA-import support step.
- The published RC package needs a refreshed package build before external
  tester handoff because launcher/docs/frontend files changed after rc2 was
  built.
- Owner/reviewer signoff and tester/cohort selection remain pending before
  external handoff.

### Remediation Actions

Refresh the RC package after owner approval of this slice, then record
owner/reviewer signoff and tester/cohort selection before external handoff.

### Sign-off

Not signed off. Owner/reviewer acceptance and tester/cohort selection are
required before replacing the current external tester handoff materials.
