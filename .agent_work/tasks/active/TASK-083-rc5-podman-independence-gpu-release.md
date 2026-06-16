# TASK-083: RC5 Podman Independence, GPU CDI, And Release Validation

**Status**: REVIEW_READY - Source implementation, Podman 5.8.2 blocker fixes, rc5 candidate image/package assembly, local Docker CPU smoke, live Docker GPU, Docker-Desktop-free Podman CPU, Podman GPU CDI, and fixed-fixture runtime parity are validated for RC5 candidate 3. PR #33 closure remains; GA package distribution polish is split to `TASK-084`.
**Priority**: CRITICAL
**Type**: C (Runtime Support / Podman GPU / Release Validation)
**Estimated Effort**: 3-6 days (24-48 hours), split across CPU-dev-able implementation, GPU-host validation, and package release validation
**Target Sprint**: Sprint 06 V1 RC1 / post-rc4 to rc5 readiness

## Objective

Implement the RC4 follow-up fixes and Podman independence work needed before the
next release-candidate package, then build and validate an `rc5` release artifact
from the resulting branch.

This task deliberately joins the related runtime/release work into one gate:
setup rerun resilience, Docker-Desktop-free Podman CPU, Podman GPU via NVIDIA CDI,
release manifest polish, fixed-fixture parity evidence, and next-package
validation. The goal is not just to make Podman GPU work once; the goal is to
ship a supportable release candidate whose Podman path does not rely on Docker
Desktop and whose GPU support claim is bounded by evidence.

## Background

RC4 passed its release validation matrix and did not expose a model or TF32
correctness issue. The remaining release-relevant findings are runtime and
supportability issues:

- `setup-towerscout.cmd` can fail on rerun when staged assets already exist and
  the asset ZIP is auto-discovered.
- RC4 Podman CPU validation proved independence from the Docker engine, but not
  independence from the Docker Desktop installation, because `podman compose`
  selected Docker Desktop's bundled `docker-compose.exe`.
- The Podman GPU reference packet proves a CDI-based implementation can reach
  `selected_device=cuda` on real NVIDIA T1000 hardware, but that implementation
  is not present in this checkout.
- Release parity evidence needs fixed replay fixtures and summaries so future
  RC comparisons can distinguish imagery/provider drift from runtime/model drift.
- Release manifest generation should carry package and asset checksum metadata
  cleanly.

Supporting analysis:

- `.agent_work/context/analysis/RC4-APPLICATION-FOLLOWUPS-2026-06-15.md`
- `.agent_work/context/analysis/PODMAN-GPU-IMPLEMENTATION-REVIEW-2026-06-15.md`
- `.agent_work/context/analysis/Podman-GPU-Implementation-Reference/`

## Requirements (EARS Notation)

**R-083-001**: WHEN setup is rerun with valid staged assets already present,
THE SYSTEM SHALL reuse the staged assets and continue importing them into the
selected engine instead of failing because an asset ZIP was auto-discovered.

**R-083-002**: IF staged assets are incomplete, corrupt, or incompatible with
the control manifest, THEN THE SYSTEM SHALL fail before launch/import with clear
guidance and SHALL NOT delete or overwrite user assets silently.

**R-083-003**: WHEN Podman CPU is selected for the supported package path,
THE SYSTEM SHALL use an approved Compose provider that does not require Docker
Desktop to be installed.

**R-083-004**: WHEN `PODMAN_COMPOSE_PROVIDER` is configured, THE SYSTEM SHALL
validate the provider path/version early and report the selected provider in
support-safe setup, launch, and status output.

**R-083-005**: WHERE Podman GPU support is included, THE SYSTEM SHALL require a
WSL2 Podman machine, a compatible Podman version, host NVIDIA visibility,
machine NVIDIA visibility, NVIDIA Toolkit/CDI registration, a container GPU
smoke, and TowerScout readiness `selected_device=cuda`.

**R-083-006**: WHEN Podman GPU prerequisites are missing and `-Gpu on` is
requested, THE SYSTEM SHALL fail closed with a rung-specific message and SHALL
not start a misleading CPU container.

**R-083-007**: WHEN Podman GPU prerequisites are missing and `-Gpu auto` is
requested, THE SYSTEM SHALL remain CPU-safe unless the explicit Podman GPU gate
is satisfied.

**R-083-008**: WHEN `enable-podman-gpu.ps1 -DryRun` is executed, THE SYSTEM
SHALL print the intended provisioning plan and SHALL make no machine changes.

**R-083-009**: WHEN `enable-podman-gpu.ps1 -VerifyOnly` is executed, THE SYSTEM
SHALL run only read-only checks and SHALL fail cleanly when CDI is missing.

**R-083-010**: WHEN Podman GPU provisioning runs, THE SYSTEM SHALL install or
verify NVIDIA Container Toolkit, generate or refresh a CDI spec, verify
`nvidia.com/gpu`, run a GPU container smoke, and record host/runtime versions.

**R-083-011**: WHEN launch/import would reuse an existing container with a
different engine, image, port, GPU mode, or selected ML device policy,
THE SYSTEM SHALL recreate or stop with guidance rather than silently reusing the
wrong runtime state.

**R-083-012**: WHEN release manifests are generated, THE SYSTEM SHALL include
release version/posture, source ref, image digest, application package checksum,
and model/data asset checksum in fields accepted by the manifest checker.

**R-083-013**: WHEN release parity evidence is captured, THE PROJECT SHALL
preserve a fixed fixture or support-safe equivalent plus a parity summary
covering counts, flips, deltas, image digest, model manifest hash, provider,
engine, and selected device.

**R-083-014**: WHEN the next release image/package is built, THE PACKAGE SHALL
pin the GHCR image by digest and SHALL include current docs, Compose overlays,
launch scripts, manifests, checksums, and support notices consistent with the
validated runtime support boundary.

**R-083-015**: WHEN `rc5` validation completes, THE PROJECT SHALL have evidence
for Docker CPU, Docker GPU, Podman CPU without Docker Desktop provider
selection, Podman GPU with CDI, setup rerun staged-asset reuse, asset import,
readiness, health, and fixed-fixture parity.

## Acceptance Criteria

- [x] Valid staged asset reuse is implemented and covered by focused tests.
- [x] Invalid staged assets still fail safely before import/launch.
- [x] Podman CPU setup/import/start/status succeeds with an approved provider
      that is not Docker Desktop's bundled `docker-compose.exe`.
- [x] Provider selection and version are visible in support-safe output.
- [x] `compose.gpu.podman.yaml` is added and validated through `compose config`.
- [x] `scripts/enable-podman-gpu.ps1` and a testable helper module are added.
- [x] Podman GPU hard blocks in `TowerScoutCompose.ps1` are replaced with a
      gated CDI decision tree.
- [x] `-Gpu on` remains fail-closed unless readiness reports
      `selected_device=cuda`.
- [x] `-Gpu auto` remains CPU-safe unless the explicit Podman GPU gate is ready.
- [x] Windows PowerShell 5.1 unit tests cover preflight rungs, provider
      resolution, image-reference splitting, provisioner scenarios, and stale
      CDI self-heal.
- [x] Release manifest/package checksum metadata validates without known
      recommended-field warnings, or the checker is updated to accept the
      canonical schema fields.
- [x] Fixed-fixture parity evidence is preserved for the next RC.
- [x] The next image/package is generated only after implementation validation
      passes.
- [x] The final candidate package release matrix passes or records bounded,
      owner-accepted caveats.
- [x] Documentation support language does not claim Docker-Desktop-free Podman or
      Podman GPU beyond evidence.
- [x] `.agent_work` validation passes after task and evidence updates.

## Dependencies

- `TASK-066`: release-candidate package validation gate.
- `TASK-074`: bootstrap/preflight and asset ZIP staging/import flow.
- `TASK-075`: GPU-capable package and readiness diagnostics.
- `TASK-080`: simplified setup path and UAT guide assumptions.
- `TASK-081`: runtime hardening, Podman CPU groundwork, stale-container guard,
  and fail-closed GPU behavior.
- `TASK-082`: stable package docs and app docs routing.
- RC4 analysis and Podman GPU reference packet listed in Background.
- A Windows 11 WSL2 Podman host with NVIDIA GPU for final Podman GPU validation.

## Implementation Plan

1. **Phase 0 - Scope Lock And Branch Prep**
   - Confirm whether this task starts from latest `main` after `TASK-082` lands
     or from a stacked branch.
   - Confirm the approved Compose provider strategy for Docker-Desktop-free
     Podman.
   - Decide whether provider binary vendoring is in scope or whether the first
     implementation uses documented support-installed provider placement.

2. **Phase 1 - RC4 Application Follow-ups**
   - Implement staged-asset reuse on setup rerun.
   - Fix release manifest checksum/recommended metadata generation.
   - Add or document fixed-fixture parity artifact handling.
   - Keep reviewer-audit hardening outside this phase unless release-critical.

3. **Phase 2 - Docker-Desktop-Free Podman CPU**
   - Implement or finish provider resolution and integrity/version reporting.
   - Validate setup/import/start/status without Docker Desktop provider
     selection.
   - Keep direct `podman cp` fallback behavior intact.

4. **Phase 3 - Podman GPU CDI Enablement**
   - Add Podman GPU overlay.
   - Add `enable-podman-gpu.ps1` and helper module.
   - Replace the current Podman GPU hard block with the gated preflight ladder.
   - Preserve fail-closed readiness assertion for `-Gpu on`.
   - Add focused Windows PowerShell tests.

5. **Phase 4 - Docs, Tests, And CI Hooks**
   - Update runtime/support docs to describe the gated Podman GPU path.
   - Add compose-overlay validation and provider-resolution tests.
   - Keep support language bounded until Phase 6 evidence is complete.

6. **Phase 5 - Build Next Release Candidate**
   - Publish or select the next GHCR image digest.
   - Generate the next application package and checksum sidecars.
   - Confirm manifest, `IMAGE.txt`, `SOURCE.txt`, docs, overlays, and scripts
     match the intended release state.

7. **Phase 6 - Release Matrix Validation**
   - Validate Docker CPU and Docker GPU.
   - Validate Podman CPU with approved non-Docker-Desktop provider.
   - Validate Podman GPU after CDI provisioning.
   - Validate setup rerun with staged assets.
   - Validate asset import and readiness/health on both engines.
   - Run fixed-fixture parity and record support-safe evidence.

8. **Phase 7 - Handoff**
   - Summarize final support claims and caveats.
   - Record release-blocking findings, non-blocking follow-ups, and exact
     artifact identities.
   - Prepare PR/release notes with evidence links.

## Validation Strategy

Initial planning validation:

- `python .agent_work/scripts/validate_agent_work.py`
- `python .agents/skills/towerscout-agent-work-hygiene/scripts/check_agent_work_quick.py .`
- `git diff --check`

Implementation validation should include:

- Focused unit tests for bootstrap/staged asset reuse.
- Focused PowerShell tests for `TowerScoutCompose.ps1`, provider resolution, and
  Podman GPU preflight/provisioner behavior under Windows PowerShell 5.1.
- Compose config validation for base, Docker GPU, Podman GPU, and build-overlay
  combinations.
- Release manifest/schema tests.
- Package-release tests.
- Docker CPU and Docker GPU package smokes on a GPU-capable Windows host.
- Podman CPU package smoke with Docker Desktop absent or not selected.
- Podman GPU provisioning and launch evidence on a WSL2 NVIDIA Podman host.
- Fixed-fixture parity comparison across validated engine/device cells.

## Non-Goals

- Do not make model, threshold, TF32, or detector pipeline changes unless new
  evidence proves a model/runtime correctness issue.
- Do not claim Podman GPU beyond the RC5 support-assigned CDI boundary proved
  by the gated hardware evidence.
- Do not claim Docker-Desktop-free Podman beyond the approved-provider path
  proved without Docker Desktop selection.
- Do not broaden release scope to Mac, ARM64, VDI, shared deployment, native
  installer behavior, or air-gapped GPU toolkit installation.
- Do not delete or reorganize broad repo-root research/legacy folders as part of
  this runtime/release task.

## Risks And Open Questions

- Vendoring or blessing a standalone Compose provider creates license,
  checksum, update, and CVE-response obligations.
- Earlier Podman GPU evidence used the wrong provider family; the later RC5
  sign-off packet superseded it with an approved standalone provider.
- WSL2 Podman memory/resource guidance must be validated before publishing exact
  `podman machine set` commands.
- NVIDIA Toolkit installation requires network egress inside the Podman machine
  unless an offline RPM side-load path is designed later.
- Hosted CI cannot prove GPU/CDI; CI can only cover syntax and decision logic.
- The release matrix may require coordination across one GPU-capable host and
  one Docker-Desktop-free Podman host if a single machine cannot represent both.

## Evidence Handling

Keep raw logs, screenshots, provider responses, `.env` files, private AOIs,
tile/map URLs, provider keys, and user-identifying paths out of project-wide
status files. Store sanitized task-local evidence under a `TASK-083/` support
folder if needed, and summarize only non-secret commands, versions, hashes,
counts, readiness fields, and pass/fail outcomes in the task file.

---

## Implementation Log

### 2026-06-15 - Task Documentation Created
**Objective**: Create a dedicated active task for implementing RC4 follow-ups,
Docker-Desktop-free Podman, Podman GPU CDI support, and next release-candidate
validation.
**Context**: RC4 passed validation, but follow-up analysis identified setup
rerun asset reuse, true Podman provider independence, gated Podman GPU CDI,
release manifest metadata, fixed-fixture evidence, and next package validation
as the correct next work before building another release image.
**Decision**: Track this as `TASK-083` instead of expanding `TASK-081` or
`TASK-082`. `TASK-081` delivered the first runtime hardening slice; `TASK-082`
covers documentation/package organization. This task owns the next runtime and
release validation gate.
**Execution**: Added this task file and linked it from `current-tasks.md`.
**Output**: `TASK-083` is ready for owner review and implementation approval.
**Validation**: `.agent_work` structural validation, agent-work quick check, and
whitespace validation passed.
**Next**: Confirm approved Compose provider strategy and branch base before
implementation begins.

### 2026-06-15 - Branch Prep And RC4 Baseline Lock
**Objective**: Start Task-083 from the landed rc4 baseline and remove stale Task-082 status language before implementation.
**Context**: `TASK-082` landed on `main` as `v0.1.0-rc4` in commit `32074a7`, so Task-083 no longer needs to stack on a docs branch.
**Decision**: Use short-lived branch `feature/task-083-rc5-podman-independence-gpu-release` from current `main` and checkpoint planning/task hygiene before touching runtime code.
**Execution**: Created the Task-083 feature branch, marked Task-082 as landed in the task tracker, and updated Task-083 status from pending approval to branch-prep in progress.
**Output**: Task-083 now starts from the exact rc4 baseline and the active task tracker no longer implies PR #32 is still open.
**Validation**: `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py`, `.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`, and `git diff --check` passed.
**Next**: Commit the planning checkpoint, then begin Phase 1 implementation.

### 2026-06-15 - Phase 1 Staged Assets And Manifest Metadata
**Objective**: Implement the RC4 application follow-ups that can be completed before the larger Podman provider/GPU work.
**Context**: RC4 UAT found that rerunning setup after a successful asset extraction fails because the setup wrapper auto-discovers the asset ZIP and `bootstrap.ps1` tries to extract over valid staged assets. RC4 manifest review also flagged blank checksum metadata that needed a canonical sidecar-aware schema.
**Decision**: Reuse staged assets only after `Test-TowerScoutStagedAssets` validates them against the control manifest, then continue engine import. Keep invalid or partial staged assets fail-closed with clearer rerun guidance. For manifest metadata, record checksum sidecar fields and accept an `-AssetBundleSha256` input instead of embedding the control ZIP's own checksum inside the ZIP manifest.
**Execution**: Updated `scripts/bootstrap.ps1`, `scripts/lib/TowerScoutBootstrap.ps1`, `scripts/package-release.ps1`, `release-manifest.v1.json`, and focused bootstrap/release-manifest tests.
**Output**: Valid staged assets are reused and still imported into Docker/Podman volumes on rerun. Partial staged assets still fail before import. Generated manifests now name checksum sidecars, package contents checksum file, asset bundle artifact name, and optional asset bundle checksum.
**Validation**: `.venv\Scripts\python.exe -m pytest tests\unit\test_task_074_bootstrap.py tests\unit\test_release_manifest_schema.py tests\unit\test_release_package_script.py -q -p no:cacheprovider` passed with 21 tests. Line-length scan over edited Python tests and `git diff --check` passed.
**Next**: Begin Phase 2 provider-resolution work for Docker-Desktop-free Podman CPU.

### 2026-06-15 - Phase 2 Podman Compose Provider Guardrails
**Objective**: Prevent the Podman path from silently relying on Docker Desktop's bundled Compose provider and make provider selection visible in support evidence.
**Context**: RC4 Podman CPU proved Podman-engine operation, but the evidence showed `podman compose` delegated to Docker Desktop's `docker-compose.exe`, which does not satisfy the no-Docker-Desktop reliance requirement.
**Decision**: Use the support-installed `PODMAN_COMPOSE_PROVIDER` strategy for this source slice. Do not vendor a Compose provider yet because that needs owner decisions for binary source, checksum, license, and CVE lifecycle. Fail early if the override is missing, invalid, or resolves to Docker Desktop's bundled provider, and inspect `podman compose version` before invoking Podman Compose.
**Execution**: Updated `scripts/lib/TowerScoutCompose.ps1`, `scripts/lib/TowerScoutBootstrap.ps1`, `.env.example`, `scripts/status.ps1`, and focused runtime tests.
**Output**: Launch/status/preflight now report the Podman Compose provider path/version when available, `PODMAN_COMPOSE_PROVIDER` can be loaded from `.env`, and Docker Desktop provider paths or version banners are rejected for the Podman support path.
**Validation**: Focused provider tests passed under Windows PowerShell 5.1 as part of the 36-test runtime/package suite.
**Next**: Validate Podman CPU setup/import/start/status on a host with the approved non-Docker-Desktop provider selected and Docker Desktop unavailable or not selected.

### 2026-06-15 - Phase 3 Podman GPU CDI Source Implementation
**Objective**: Implement the CPU-testable Podman GPU CDI path from the
reference packet while keeping support claims bounded pending the later live
GPU evidence captured by this task.
**Context**: The current checkout hard-blocked Podman GPU, while the reference evidence showed Podman GPU could reach `selected_device=cuda` after NVIDIA Toolkit/CDI provisioning on a WSL2 Podman machine.
**Decision**: Add the Podman CDI overlay and provisioner, replace the hard block with a gated decision tree, keep `-Gpu auto` CPU-safe, keep `-Gpu on` fail-closed, and leave final support claims pending live validation.
**Execution**: Added `compose.gpu.podman.yaml`, `scripts/enable-podman-gpu.ps1`, `scripts/lib/TowerScoutPodmanGpu.ps1`, `tests/unit/test_podman_gpu_enablement.py`, and release-package wiring. Updated `scripts/lib/TowerScoutCompose.ps1`, `scripts/launch.ps1`, `scripts/start.ps1`, package manifest generation, and package tests.
**Output**: Podman GPU now uses `compose.gpu.podman.yaml` only after the explicit Podman overlay gate and CDI readiness pass. `enable-podman-gpu.ps1 -DryRun` prints the non-mutating plan, `-VerifyOnly` is read-only and fails when CDI is missing, normal provisioning installs/verifies NVIDIA Toolkit/CDI, runs a transient GPU smoke, retries once after stale CDI, and records runtime evidence.
**Validation**: The 36-test focused suite passed; Docker Compose `config` passed for base, Docker GPU, Podman GPU, and build+Podman GPU combinations; `enable-podman-gpu.ps1 -DryRun` passed. Local `podman compose config` and `-VerifyOnly` could not prove live Podman readiness because this workstation's configured Podman machine connection was unavailable.
**Next**: Run the live validation ladder on the GPU Podman host: approved provider, negative `-Gpu on`, `-DryRun`, `-VerifyOnly`, provisioning, `-VerifyOnly`, container smoke, TowerScout readiness `selected_device=cuda`, fixed-fixture parity, and release evidence capture.

### 2026-06-15 - Branch Publish, Rollback Checkpoint, And Validation Package
**Objective**: Preserve a rollback checkpoint, publish the Task-083 branch for review, and build a local package for validation before final rc5 release work.
**Context**: The owner requested a pre-Task-083 checkpoint before pushing and testing the implementation.
**Decision**: Preserve the rc4 baseline as `checkpoint/pre-task-083-rc4` at `32074a7`, publish the Task-083 branch, and create a draft PR while keeping generated packages out of git. Use the rc4 CUDA image digest for a source/package validation build until a final rc5 image is built.
**Execution**: Pushed `feature/task-083-rc5-podman-independence-gpu-release`, pushed `checkpoint/pre-task-083-rc4`, opened draft PR #33, and generated `dist\towerscout-v0.1.0-rc5-task083-validation.zip` plus a version-matched asset ZIP sidecar.
**Output**: Draft PR #33 tracks source review. The validation package pins `ghcr.io/j-schulein/towerscout:v0.1.0-rc4-cuda121@sha256:d686d8556443ead03e257e4abb2d04f97dece3e04c228963c6f65201a308161e` and source ref `839ab00a35bd3b997179d504752e66fa71545b77`. Package SHA-256 is `d25a7fc4980f4893e8794608450258563bd50154a28886eb6be766cf60d1728c`; asset ZIP SHA-256 is `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Validation**: Release package summary passed with 55 files and included `compose.gpu.podman.yaml`. Manifest checker exited 0, but still emitted recommended-key warnings for `checksums`, `releasePosture`, `releaseVersion`, and `sourceRef`; resolve the checker/schema naming mismatch or record an owner-accepted waiver before final rc5.
**Next**: Run live Docker-Desktop-free Podman CPU and Podman GPU validation from the package, then build/publish the final rc5 image/package if the matrix passes.

### 2026-06-15 - Podman 5.8.2 Live Validation Fixes
**Objective**: Incorporate live Windows 11 + Podman 5.8.2 + NVIDIA T1000 validation findings that blocked the two Task-083 headline capabilities.
**Context**: The sanitized validation packet under `.agent_work/context/analysis/towerscout-rc5-podman-gpu-evidence-2026-06-15/` proved Docker-Desktop-free Podman CPU and Podman GPU CDI only after two source fixes. Before the fixes, `podman compose version` exposed Docker Desktop's provider path with doubled backslashes that the guardrail missed, and Podman 5.8.2 `machine inspect` omitted top-level `VMType`, causing the GPU ladder to reject a valid WSL2 machine.
**Decision**: Treat both findings as rc5 blockers. Keep the fix narrow to Podman-only logic: collapse repeated path separators before Docker Desktop provider matching, and infer the Podman machine backend from `ConfigDir.Path` when `VMType` is absent. Add regression fixtures matching the live Podman 5.8.2 output so the green test suite covers the real failure shapes.
**Execution**: Updated `scripts/lib/TowerScoutCompose.ps1`, `scripts/lib/TowerScoutPodmanGpu.ps1`, `tests/unit/test_task_081_runtime_hardening.py`, and `tests/unit/test_podman_gpu_enablement.py`.
**Output**: Podman provider guardrails now detect Docker Desktop's escaped provider banner, and both the launch preflight and GPU provisioner accept Podman 5.8.x WSL machines whose backend is represented by `ConfigDir.Path`.
**Validation**: Focused tests passed: `.venv\Scripts\python.exe -m pytest tests\unit\test_podman_gpu_enablement.py tests\unit\test_task_081_runtime_hardening.py -q -p no:cacheprovider` returned 14 passed.
**Next**: Run the full Task-083 focused suite and hygiene checks, then rebuild final rc5 artifacts only after image/default, manifest, asset checksum, Docker matrix, and parity decisions are closed.

### 2026-06-15 - RC5 Candidate Image Publish And Package Assembly
**Objective**: Build a digest-pinned rc5 candidate package that can be moved to
the GPU Podman validation host.
**Context**: The first local Buildx image build succeeded, but direct GHCR push
failed until GitHub CLI authentication was restored. Final package generation
needed a pullable image digest, clean source-ref capture, and the Model & Data
Package checksum recorded in the generated manifest.
**Decision**: Publish the image through the manual GitHub Actions container
workflow, then assemble the package from a clean detached worktree at the PR
branch head instead of using `-AllowDirtySource` in the main worktree.
**Execution**: Dispatched `TowerScout Container Publish` run `27571265547` for
`tag=v0.1.0-rc5-candidate.1`, `pytorch_flavor=cuda121`, and
`push_latest=false`. Downloaded `image-metadata.json`, generated
`dist\towerscout-v0.1.0-rc5-candidate.1.zip`, copied the unchanged Model & Data
Package ZIP to the matching rc5 candidate filename, and wrote checksum
sidecars.
**Output**: Published image
`ghcr.io/j-schulein/towerscout:v0.1.0-rc5-candidate.1-cuda121@sha256:ae917be0c2541be152e73c0b379698c53e980dcb34575e1d079d5822556b7c72`.
Application Package SHA-256:
`de7c628b9c83877668b17f833c2de36242f4e989aa3d7a50408ed234981b958c`.
Model & Data Package SHA-256:
`00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
**Validation**: Package summary passed with 55 files. Manifest checker passed
without known canonical-field warnings. Control and asset ZIP sidecars matched
their computed hashes. `docker manifest inspect` resolved the pinned GHCR
digest and reported a Linux AMD64 manifest. A local Docker CPU package rerun
from the generated package reused staged assets, verified the package and asset
checksums, imported assets with hash verification, reached readiness
`setup_required`, and reported `device_policy=cpu`, `selected_device=cpu`,
`pytorch_flavor=cuda121`, and the expected image digest. The isolated stack on
port `5020` was stopped and removed.
**Next**: Move the rc5 candidate package to the Windows 11 + Podman 5.8.2 +
NVIDIA host for Docker-Desktop-free Podman CPU, Podman GPU CDI, Docker GPU, and
fixed-fixture parity validation before promoting `v0.1.0-rc5`.

---

### 2026-06-15 - RC5 Sign-Off Evidence Review And Documentation Alignment
**Objective**: Incorporate the RC5 sign-off packet findings into the release
support boundary and remove stale package documentation language.
**Context**: The sanitized packet under
`.agent_work/context/analysis/towerscout-rc5-signoff-evidence-2026-06-15/`
proved Docker CPU, Docker GPU, Docker-Desktop-free Podman CPU, Podman GPU CDI,
and fixed-fixture parity on the Windows 11 + Podman 5.8.2 + NVIDIA T1000 host.
The packet also showed that the tested package pinned the earlier rc4 CUDA
digest as a stand-in, while the later clean `rc5-candidate.1` package pins the
real rc5 candidate image digest. A second review found package docs still
carried the prior unsupported Podman GPU boundary.
**Decision**: Include Podman GPU in RC5 as a support-assigned path, not as the
default first-run path. Keep Docker Desktop CPU as the primary pilot path and
require workstation-specific validation for Docker GPU and Podman GPU. Document
the Podman GPU boundary as Windows 11 WSL2 Podman, approved
non-Docker-Desktop Compose provider, NVIDIA Toolkit/CDI, and readiness
`selected_device=cuda`.
**Execution**: Updated `README.md`, `docs/quick-start.*`,
`docs/package-guide.md`, `docs/project-overview.*`, `docs/user-guide.*`,
`docs/support/oci-quick-start.md`, `docs/support/oci-runtime-contract.md`,
`docs/release/release-asset-bundle-contract.md`, and compatibility stubs to
remove stale RC4 and unsupported-Podman-GPU wording while recording the RC5
support boundary.
**Output**: Current docs now treat Podman CPU, Docker GPU, and Podman GPU as
support-assigned RC5 paths after selected-engine, Compose-provider, and NVIDIA
validation. The support docs record the validated standalone Docker Compose
v5.1.4 `PODMAN_COMPOSE_PROVIDER` strategy and Podman CDI overlay.
**Validation**: Stale-doc search no longer finds the old unsupported GPU
boundary, Docker-prioritized GPU wording, superseded provider-version wording,
or superseded RC-label wording in `README.md` or `docs/`.
**Next**: Run docs/package validation, rebuild the final RC5 candidate package,
resolve or explicitly waive the SBOM reference warning, and rerun the release
matrix against the final pinned rc5 digest.

---

### 2026-06-16 - RC5 Candidate 3 Review And GA Packaging Split
**Objective**: Review the RC5 candidate 3 validation packet and decide whether
remaining image/provider polish belongs in Task-083 or a new task.
**Context**: The packet under
`.agent_work/context/analysis/towerscout-rc5-candidate3-validation-evidence-2026-06-15/`
validated the published pre-release `v0.1.0-rc5-candidate.3` at source ref
`ef6904fc` with image digest
`sha256:841bc196c753654d359ff399e5ac5a547d4b2ab01150c7cc20eb2b7be73852ad`.
Docker CPU, Docker GPU, Podman CPU, and Podman GPU CDI all reached readiness,
and fixed-fixture parity was byte-identical at 45 detections over 25 tiles.
**Decision**: Treat Task-083 runtime work as review-ready after PR #33 metadata
is updated and the PR leaves draft. Split remaining GA packaging/distribution
polish into `TASK-084`, specifically CPU/CUDA package strategy, Podman Compose
provider onboarding, and public evidence sanitization.
**Output**: Task-083 status updated to `REVIEW_READY`; `TASK-084` created and
linked from the sprint tracker.
**Validation**: The evidence packet's `SHA256SUMS.txt` verified locally during
review, and the parity JSONs had identical per-tile detection counts across all
four cells.
**Next**: Update PR #33 body/draft state, complete review/merge, then pursue
GA packaging hardening under Task-084.

---

## Validation Results

### Planning Validation
**Test Date**: 2026-06-15
**Test Environment**: Local TowerScout workspace on Windows
**Test Status**: PASS for planning/task-tracker validation

### Acceptance Criteria Validation

- [x] Task tracker entry created in `current-tasks.md`.
- [x] Active task file created under `.agent_work/tasks/active/`.
- [x] Phase 1 RC4 setup/manifest source fixes implemented and unit-tested.
- [x] Phase 2 Podman provider guardrails implemented and unit-tested.
- [x] Phase 3 Podman GPU CDI source gating/provisioner implemented and unit-tested.
- [x] Live Docker-Desktop-free Podman CPU setup/import/start/status validation passed on Windows 11 + Podman 5.8.2 after the Podman 5.8.2 guardrail fix.
- [x] Live Podman GPU CDI provisioning and TowerScout `selected_device=cuda` validation passed on Windows 11 + Podman 5.8.2 + NVIDIA T1000 after the Podman 5.8.2 backend-detection fix.
- [x] RC5 candidate image/package build passed with a pinned GHCR digest and
      `-AssetBundleSha256` recorded in the generated manifest.
- [x] Local Docker CPU package smoke passed from the rc5 candidate package with
      staged-asset reuse, asset hash verification, readiness
      `setup_required`, and `selected_device=cpu`.
- [x] Live Docker GPU, Docker-Desktop-free Podman CPU, Podman GPU CDI, and
      fixed-fixture runtime parity passed in the RC5 sign-off evidence packet.
- [x] RC5 candidate 3 package validation passed against the published rc5 image
      digest and current source ref; GA package-distribution polish is tracked
      separately in `TASK-084`.
- [x] Rollback checkpoint branch and draft PR created.
- [x] Local Task-083 validation package created for package-content inspection.

### Test Results

- [x] `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` - PASS.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` - PASS.
- [x] `git diff --check` - PASS.
- [x] Branch-prep rerun after Task-082 status cleanup and Task-083 status update:
      `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py`,
      `.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .`,
      and `git diff --check` - PASS.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_task_074_bootstrap.py tests\unit\test_release_manifest_schema.py tests\unit\test_release_package_script.py -q -p no:cacheprovider` - PASS, 21 tests.
- [x] Edited Python test line-length scan - PASS, no lines over 127 characters.
- [x] `git diff --check` - PASS after Phase 1 edits.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py -q -p no:cacheprovider` - PASS, 24 tests after provider-guardrail edits.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_podman_gpu_enablement.py -q -p no:cacheprovider` - PASS, 6 tests.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_podman_gpu_enablement.py tests\unit\test_task_075_launcher_gpu.py tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py tests\unit\test_release_manifest_schema.py tests\unit\test_release_package_script.py -q -p no:cacheprovider` - PASS, 36 tests.
- [x] `docker compose -f compose.yaml config` - PASS.
- [x] `docker compose -f compose.yaml -f compose.gpu.yaml config` - PASS.
- [x] `docker compose -f compose.yaml -f compose.gpu.podman.yaml config` - PASS.
- [x] `docker compose -f compose.yaml -f compose.build.yaml -f compose.gpu.podman.yaml config` - PASS.
- [x] `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\enable-podman-gpu.ps1 -DryRun -Image test:image` - PASS.
- [x] Edited Python test line-length scan after Phase 3 - PASS, no lines over 127 characters.
- [x] `git diff --check` - PASS after Phase 3 edits.
- [x] PowerShell parser pass over edited runtime/package scripts - PASS.
- [x] `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` - PASS after Phase 3 task updates.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` - PASS after Phase 3 task updates.
- [x] `git push -u origin feature/task-083-rc5-podman-independence-gpu-release` - PASS.
- [x] `git push -u origin checkpoint/pre-task-083-rc4` - PASS.
- [x] Draft PR #33 created against `main` - PASS.
- [x] `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package-release.ps1 -Version v0.1.0-rc5-task083-validation ... -AllowDirtySource -Force` - PASS; package generated under `dist\`.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\summarize_release_package.py dist\towerscout-v0.1.0-rc5-task083-validation.zip` - PASS, 55 files.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\check_release_manifest.py dist\towerscout-v0.1.0-rc5-task083-validation\release-manifest.v1.json dist\towerscout-v0.1.0-rc5-task083-validation` - PASS with recommended-key warnings.
- [x] Sanitized evidence packet scan:
      `.venv\Scripts\python.exe .agents\skills\towerscout-secret-and-provider-key-safety\scripts\scan_for_sensitive_terms.py .agent_work\context\analysis\towerscout-rc5-podman-gpu-evidence-2026-06-15` - PASS, 0 matches.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_podman_gpu_enablement.py tests\unit\test_task_081_runtime_hardening.py -q -p no:cacheprovider` - PASS, 14 tests after Podman 5.8.2 blocker fixes.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_podman_gpu_enablement.py tests\unit\test_task_075_launcher_gpu.py tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py tests\unit\test_release_manifest_schema.py tests\unit\test_release_package_script.py -q -p no:cacheprovider` - PASS, 36 tests after Podman 5.8.2 blocker fixes.
- [x] PowerShell parser pass over `scripts\lib\TowerScoutCompose.ps1` and `scripts\lib\TowerScoutPodmanGpu.ps1` - PASS.
- [x] Edited Python test line-length scan after Podman 5.8.2 fixture updates - PASS, no lines over 127 characters.
- [x] `.venv\Scripts\python.exe .agent_work\scripts\validate_agent_work.py` - PASS after Podman 5.8.2 task updates.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-agent-work-hygiene\scripts\check_agent_work_quick.py .` - PASS after Podman 5.8.2 task updates.
- [x] `git diff --check` - PASS after Podman 5.8.2 blocker fixes.
- [x] `.venv\Scripts\python.exe -m pytest tests\unit\test_release_manifest_schema.py -q -p no:cacheprovider` - PASS, 2 tests after manifest checker canonical-field update.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\check_release_manifest.py ...\release-manifest.v1.json ...\evidence` - PASS for canonical snake_case fields; remaining `SHA256SUMS.txt` warning is expected when checking the sanitized evidence folder instead of the full package root.
- [x] `docker buildx build ... --tag ghcr.io/j-schulein/towerscout:v0.1.0-rc5-candidate.1-cuda121 --push ...` - IMAGE BUILD PASS locally; GHCR push blocked by authentication. Local image ID: `sha256:15da2bebff3d131ba2e274e6cf9564126abde0c31902d06454be51533991033b`.
- [x] `gh workflow run container-publish.yml --ref feature/task-083-rc5-podman-independence-gpu-release -f tag=v0.1.0-rc5-candidate.1 -f push_latest=false -f pytorch_flavor=cuda121` - PASS; workflow run `27571265547`.
- [x] `gh run download 27571265547 --name image-metadata-v0.1.0-rc5-candidate.1-cuda121` - PASS; `containerimage.digest` is `sha256:ae917be0c2541be152e73c0b379698c53e980dcb34575e1d079d5822556b7c72`.
- [x] Clean detached worktree package generation without `-AllowDirtySource` - PASS; generated `dist\towerscout-v0.1.0-rc5-candidate.1.zip`.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\summarize_release_package.py dist\towerscout-v0.1.0-rc5-candidate.1.zip` - PASS, 55 files.
- [x] `.venv\Scripts\python.exe .agents\skills\towerscout-release-candidate-gate\scripts\check_release_manifest.py dist\towerscout-v0.1.0-rc5-candidate.1\release-manifest.v1.json dist\towerscout-v0.1.0-rc5-candidate.1` - PASS.
- [x] Control ZIP checksum verification - PASS; `de7c628b9c83877668b17f833c2de36242f4e989aa3d7a50408ed234981b958c  towerscout-v0.1.0-rc5-candidate.1.zip`.
- [x] Model & Data Package checksum verification - PASS; `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb  towerscout-v0.1.0-rc5-candidate.1-assets-towerscout-v1-assets-2026-05-05.zip`.
- [x] `docker manifest inspect ghcr.io/j-schulein/towerscout:v0.1.0-rc5-candidate.1-cuda121@sha256:ae917be0c2541be152e73c0b379698c53e980dcb34575e1d079d5822556b7c72` - PASS; digest resolves and includes a Linux AMD64 manifest.
- [x] `.\setup-towerscout.cmd -Engine docker -Gpu off -Port 5020 -NoBrowser ...` from the rc5 candidate package - PASS on rerun; staged assets reused, package and asset checksums verified, assets imported with hash verification, readiness reached `setup_required`, and runtime reported `device_policy=cpu`, `selected_device=cpu`, `pytorch_flavor=cuda121`, and the expected image digest.
- [x] `.\scripts\stop.cmd -Engine docker -Port 5020` from the rc5 candidate package - PASS; isolated smoke stack removed.

### Issues Identified

Live Podman validation identified two source-level rc5 blockers that were not
covered by the original synthetic fixtures:

- Docker Desktop provider banners with doubled backslashes were not detected.
- Podman 5.8.x `machine inspect` does not expose top-level `VMType`, so valid
  WSL2 machines were rejected by the Podman GPU ladder.

Both issues are remediated in source with regression fixtures.

Earlier local live Podman validation remains limited on this development host:
`podman compose -f compose.yaml -f compose.gpu.podman.yaml config` failed because
the configured Podman machine connection was unavailable, and
`enable-podman-gpu.ps1 -VerifyOnly` failed cleanly at machine inspection because
the local `podman-machine-default` lock/connection was not usable in this
workspace context. This does not validate or invalidate the GPU CDI path; it
means the remaining evidence must be collected on the intended GPU Podman host.

The manifest checker warning for canonical snake_case release metadata has been
resolved in source. Older sanitized evidence folders may still warn when checked
outside the full package root because they do not include `SHA256SUMS.txt`.

The first direct local Buildx push attempt failed with
`unauthorized: unauthenticated: User cannot be authenticated with the token
provided.` This was resolved by restoring GitHub CLI authentication and
publishing through the repository's manual container workflow, which produced
the immutable rc5 candidate image digest recorded above.

### Remediation Actions

- Update PR #33 body to replace stale "live validation pending" language with
  the RC5 candidate 3 evidence summary.
- Remove draft status from PR #33 when the owner is ready for normal review.
- Keep Task-083 runtime scope closed unless PR review identifies a source
  defect.
- Continue CPU/CUDA package strategy, Podman provider onboarding, and public
  evidence sanitization under `TASK-084`.

### Sign-off

Runtime sign-off is complete for the RC5 candidate 3 support boundary: Docker
CPU, Docker GPU, Docker-Desktop-free Podman CPU, Podman GPU CDI, and
fixed-fixture parity are validated. Task-083 remains open only for PR #33
review/merge closure. GA packaging and first-run distribution hardening are
tracked in `TASK-084`.
