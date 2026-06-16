# TASK-084: GA Packaging Hardening And Podman Provider Onboarding

**Status**: IN_PROGRESS - implementation slice completed on June 16, 2026 for RC5 runtime cleanup, shared asset bundle identity, package guardrails, and Podman provider onboarding; `TASK-085` is merged/validated, and final image publication, package evidence, and docs remain
**Priority**: HIGH
**Type**: C (Release Packaging / Distribution / First-Run Support)
**Estimated Effort**: 2-4 days (16-32 hours), including runtime-defect cleanup, two-package generation, Podman provider onboarding, docs, and validation
**Target Sprint**: Sprint 06 V1 RC1 / RC5-to-GA hardening

## Objective

Turn the RC5 runtime-valid package path into a cleaner GA distribution path by
settling image flavor delivery and making Podman Compose provider setup easier
for Docker-Desktop-free users.

`TASK-083` proved the runtime boundary for Docker CPU, Docker GPU, Podman CPU,
and Podman GPU CDI. This task owns the remaining packaging/product decisions:
whether CPU users should receive a CPU image instead of the CUDA image, how the
release package selects image digests, and how Podman users obtain or select an
approved non-Docker-Desktop Compose provider.

## Background

RC5 candidate 3 validation passed all four runtime cells with fixed-fixture
parity:

- Docker CPU
- Docker GPU
- Podman CPU with an approved non-Docker-Desktop provider
- Podman GPU CDI with readiness `selected_device=cuda`

The runtime is not blocked. The remaining issues are GA packaging and first-run
support polish:

- RC5 candidate 3 ships only the `cuda121` image. CPU-only users can run it, but
  they download CUDA libraries they do not use and readiness reports
  `pytorch_flavor=cuda121`.
- The Podman path requires an approved Compose provider. The guardrail correctly
  rejects Docker Desktop's bundled provider, but the package does not yet
  auto-detect, fetch, verify, or bundle an approved provider.

Supporting analysis:

- `.agent_work/context/analysis/RC5-GA-PACKAGING-DECISIONS.md`
- `.agent_work/context/analysis/GA-PACKAGING-AND-DATASET-HARDENING-PATH-FORWARD-2026-06-16.md`
- `.agent_work/context/analysis/towerscout-rc5-candidate3-validation-evidence-2026-06-15/`
- `TASK-083` implementation and validation history

## Owner Decisions Locked On 2026-06-16

- GA packaging shall use two digest-pinned control ZIP variants:
  - a CPU package for normal/non-GPU users
  - a CUDA 12.1 package for support-validated NVIDIA GPU users
- Both control ZIP variants shall use one shared Model & Data Package ZIP
  unless a future asset change proves variant-specific assets are required.
- The normal GA path remains a connected install path. Air-gapped/offline
  provider installation is not a requirement for this task.
- The release package shall not bundle a third-party Compose provider binary.
- The Podman path shall auto-detect approved non-Docker-Desktop providers when
  possible.
- If no approved provider is present, TowerScout shall fail with a clear next
  action and point to an explicit online fetch-and-verify helper.
- The provider helper shall print the recommended `.env` setting by default and
  shall write it only when invoked with an explicit apply flag.
- Normal `start.bat` / `scripts/launch.ps1` execution shall not silently
  download or install provider executables.
- `TASK-085` owns dataset ZIP path traversal hardening and was merged/validated
  before final GA/pilot package publication.

## Requirements

**R-084-001**: WHEN GA packages are assembled, THE PROJECT SHALL publish
separate CPU and CUDA 12.1 control ZIP variants with one pinned image identity
per package.

**R-084-002**: WHEN CPU and CUDA control ZIPs are generated, THE RELEASE SHALL
publish both image flavors, generate separate control ZIPs, and publish
checksum sidecars for each artifact.

**R-084-003**: WHEN the two control ZIPs are generated, THE RELEASE SHALL use
one shared Model & Data Package ZIP unless asset contents differ, and both
release manifests SHALL identify the same asset bundle filename and SHA-256.

**R-084-004**: WHEN Podman is selected and `PODMAN_COMPOSE_PROVIDER` is blank,
THE SYSTEM SHALL either auto-detect an approved non-Docker-Desktop provider or
fail with a clear next action.

**R-084-005**: WHEN a helper downloads a Compose provider, THE HELPER SHALL use
a pinned version, verify SHA-256, avoid Docker Desktop paths, and write
support-safe setup output.

**R-084-006**: IF provider bundling is selected later, THEN THE PACKAGE SHALL
record provider source, license, version, checksum, and CVE/update ownership
before redistribution.

**R-084-007**: WHEN final GA evidence is prepared, THE PACKET SHALL strip even
masked provider-key previews before any public attachment.

**R-084-008**: WHEN no approved Podman Compose provider is present, THE SYSTEM
SHALL report the missing prerequisite with a support-safe next action instead of
falling back to Docker Desktop's bundled provider.

**R-084-009**: WHEN a provider-install helper is used, THE HELPER SHALL require
explicit user/support invocation, use a pinned provider version, verify SHA-256,
avoid Docker Desktop paths, and avoid modifying unrelated host configuration.

**R-084-010**: WHEN runtime helper commands are bounded by timeout parameters,
THE SYSTEM SHALL enforce those timeouts rather than treating them as advisory
output only.

**R-084-011**: WHEN a stopped-container port conflict is reported, THE SYSTEM
SHALL enumerate all known stopped containers using the requested host port so
the user/support action is complete.

**R-084-012**: WHEN a package-local `.env` already exists, THE SETUP OR LAUNCH
PATH SHALL detect image/package mismatches between `.env`, `.env.example`, and
the release manifest, then fail closed or warn with an explicit repair action
rather than silently reusing the wrong image.

**R-084-013**: WHEN the CPU package is launched with `-Gpu on`, THE LAUNCHER
SHALL reject the request with package-aware guidance to use the CUDA package for
GPU validation.

**R-084-014**: WHEN the CUDA package is launched with `-Gpu on`, THE FINAL
VALIDATION SHALL fail closed unless readiness reports `selected_device=cuda`.

**R-084-015**: WHEN approved Podman Compose providers are detected, THE SYSTEM
SHALL use a machine-readable allowlist contract containing provider id, display
name, version, Windows AMD64 SHA-256, allowed executable names, disallowed path
patterns, and required commands.

**R-084-016**: WHEN multiple approved providers are detected and no explicit
`PODMAN_COMPOSE_PROVIDER` is set, THE SYSTEM SHALL fail with the candidate list
instead of silently choosing one.

**R-084-017**: WHEN the provider helper is invoked without apply semantics, THE
HELPER SHALL print the recommended `.env` setting and make no `.env` changes.

**R-084-018**: WHEN the provider helper is invoked with apply semantics, THE
HELPER SHALL back up `.env`, update only `PODMAN_COMPOSE_PROVIDER`, and
preserve all unrelated settings.

**R-084-019**: WHEN final CPU and CUDA package evidence is prepared, THE
EVIDENCE SHALL include SBOM artifacts or SBOM references for both images,
`SOURCE.txt`, exact source ref, image digest, package checksum, asset checksum,
and release-manifest consistency.

**R-084-020**: WHEN the connected `podman-compose` helper installs a Python
provider, THE HELPER SHALL install it into a package-local isolated environment
with pinned runtime dependencies instead of relying on global Python packages.

## Acceptance Criteria

- [x] Owner decision recorded for image/package strategy: two digest-pinned
      packages, one CPU and one CUDA 12.1.
- [x] Owner decision recorded that air-gapped/offline install is not a GA
      requirement for this task.
- [x] Owner decision recorded that third-party Compose provider binaries shall
      not be bundled in the GA control package.
- [ ] CPU image is published and digest-pinned.
- [ ] Package generation emits separate CPU and CUDA control ZIPs without
      mutable tags in release runtime paths.
- [x] Both package manifests identify the same shared Model & Data Package
      filename and SHA-256 unless a documented asset difference exists.
- [x] Package setup/launch detects stale `.env` image or digest mismatches and
      gives a clear repair action instead of silently reusing the wrong image.
- [x] CPU package `-Gpu on` fails with a package-aware "use CUDA package"
      message.
- [ ] CUDA package `-Gpu on` remains fail-closed unless readiness reports
      `selected_device=cuda`.
- [x] Podman provider auto-detect is implemented and tested for blank
      `PODMAN_COMPOSE_PROVIDER`.
- [x] Provider auto-detect uses a machine-readable allowlist contract and fails
      with candidate details when detection is ambiguous.
- [x] Explicit fetch-and-verify provider helper is implemented and tested for
      connected support/setup use.
- [x] Provider helper installs `podman-compose` into a package-local `.venv`
      with pinned `python-dotenv` and `PyYAML` dependency requirements instead
      of extracting only `podman_compose.py` and depending on global packages.
- [x] Provider helper prints the `.env` setting by default; `-Apply` backs up
      `.env`, updates only `PODMAN_COMPOSE_PROVIDER`, and preserves other
      settings.
- [x] Normal launch does not silently download or install provider binaries.
- [x] Docker Desktop's bundled Compose provider remains fail-closed for the
      Podman support path.
- [x] Podman `cp` fallback, Podman GPU image resolution, command timeout, and
      stopped-port-conflict reporting fixes from RC5 review are implemented and
      covered by focused regression tests.
- [ ] Final package evidence includes `-AssetBundleSha256`,
      `release-manifest.v1.json`, package checksum sidecars, image digest(s),
      `SOURCE.txt`, SBOM artifacts or references, and sanitized runtime
      validation summaries.
- [ ] Final CPU package evidence includes Docker CPU and Podman CPU validation.
- [ ] Final CUDA package evidence includes Docker GPU and Podman GPU CDI
      validation, or the CUDA package is held from final publication.
- [x] `TASK-085` dataset ZIP restore hardening is merged and validated before
      final GA/pilot package publication.
- [ ] User/support docs explain the selected package and Podman-provider path in
      plain language.

## Implementation Plan

1. **Decision Lock**
   - Completed on 2026-06-16: two pinned packages, no bundled provider binary,
     no offline install requirement, auto-detect plus explicit
     fetch-and-verify helper, shared Model & Data Package, helper print-by
     default behavior, and `TASK-085` as a hard pre-final-package gate.
   - Carry the decision into the review analysis memo and package docs.

2. **RC5 Runtime Defect Cleanup**
   - Fix Podman `cp` fallback container lookup for dotted package/project
     names by using provider-consistent `compose ps` container IDs.
   - Fix Podman GPU helper image resolution so package-pinned image and digest
     values are honored before `.env` exists.
   - Enforce timeout parameters for Podman helper commands.
   - Ensure timeout execution works under Windows PowerShell 5.1 and
     PowerShell 7, captures stdout/stderr where possible, and avoids orphaned
     child processes.
   - Enumerate all stopped containers using the requested host port instead of
     reporting only the first conflict.
   - Add focused regression tests before broader packaging work.

3. **Image And Package Work**
   - Publish the CPU image flavor if selected.
   - Publish or reuse the CUDA 12.1 image flavor validated by RC5 evidence.
   - Update package generation and manifest fields to emit separate CPU and
     CUDA control ZIPs.
   - Keep one shared Model & Data Package ZIP and record the same asset bundle
     filename/hash in both manifests unless assets actually differ.
   - Ensure each package has matching `.env.example`, `IMAGE.txt`,
     `release-manifest.v1.json`, checksum sidecar, `SOURCE.txt`, SBOM
     reference or artifact, and docs.
   - Add stale `.env` image/digest mismatch detection with documented repair
     guidance.
   - Add the CPU-package guardrail that rejects `-Gpu on` with guidance to use
     the CUDA package.
   - Keep CUDA package behavior compatible with the RC5 candidate 3 validation
     boundary.

4. **Podman Provider Onboarding**
   - Add approved provider discovery when `PODMAN_COMPOSE_PROVIDER` is blank.
   - Define the provider allowlist as machine-readable data containing provider
     identity, version, SHA-256, executable names, disallowed paths, and
     required commands.
   - Fail ambiguous detection with candidate details unless the user/support
     tech sets `PODMAN_COMPOSE_PROVIDER` explicitly.
   - Add an explicit online fetch-and-verify helper for support/setup use when
     no approved provider is present.
   - Make the helper print the required `.env` setting by default, and require
     `-Apply` before it backs up `.env` and updates only
     `PODMAN_COMPOSE_PROVIDER`.
   - Keep normal launch free of silent downloads or executable installation.
   - Preserve fail-closed Docker Desktop provider detection.

5. **Docs And Evidence**
   - Update support and user docs to match the final package strategy.
   - Document CPU package as the default for non-GPU/unsure users and CUDA
     package as support-validated GPU path.
   - Document Podman provider auto-detect and explicit helper usage.
   - Sanitize public evidence packets so no provider-key previews remain.
   - Capture final package validation evidence.
   - Tie the evidence summary to source ref, image digest, package checksum,
     shared asset checksum, manifest, and SBOM/provenance entries.

6. **TASK-085 Gate Closure**
   - Keep dataset ZIP restore path traversal hardening out of `TASK-084` source
     implementation scope.
   - Treat `TASK-085` as closed for the final package gate after PR #35 merged
     on June 16, 2026 with focused validation.
   - Keep dataset restore enabled in the final package path, backed by the
     `TASK-085` traversal regression coverage.

## Validation Strategy

- Focused tests for image selection and package manifest generation.
- Focused tests for Podman `cp` fallback, provider detection, helper timeout,
  GPU helper image resolution, and stale port-conflict reporting.
- Focused tests for stale `.env` image/digest mismatch detection.
- Focused tests for CPU-package `-Gpu on` rejection.
- Focused tests for provider allowlist parsing, ambiguous detection, default
  helper output, and `-Apply` `.env` backup/update behavior.
- PowerShell parser checks for edited launcher/provider scripts.
- Connected scratch install validation for the Podman provider helper:
  download pinned wheel, verify SHA-256, create package-local `.venv`, install
  pinned provider dependencies, and run `podman-compose.cmd version`.
- Compose config validation for selected package modes.
- Package summary and release-manifest checker for both CPU and CUDA packages.
- CPU package validation: Docker CPU and Podman CPU.
- CUDA package validation: Docker GPU and Podman GPU CDI. If the GPU host is
  unavailable, hold the CUDA final package or label it as a pre-release/support
  candidate rather than final GA.
- Artifact consistency validation for both packages: manifest, `.env.example`,
  `IMAGE.txt`, checksum sidecars, `SOURCE.txt`, SBOM/provenance, image digest,
  package checksum, and shared asset ZIP checksum.
- Secret/provider-key safety scan over any public evidence packet.

## Non-Goals

- Do not reopen `TASK-083` runtime implementation unless GA packaging changes
  break validated behavior.
- Do not make model, detector, threshold, or TF32 changes.
- Do not bundle third-party Compose provider binaries in the GA control
  package.
- Do not implement or claim broad air-gapped/offline provider installation in
  this task. Restricted-network support remains separate follow-up work.
- Do not silently download or install provider executables during normal launch.
- Do not perform the Dockerfile/base-image lifecycle update in this task unless
  a release security scan promotes it to a blocker; track Node/base-image
  lifecycle hardening as a separate follow-up.

## Implementation Log

### 2026-06-16 - Task Created From RC5 Candidate 3 Review
**Objective**: Split GA packaging and first-run provider decisions out of
`TASK-083`.
**Context**: RC5 candidate 3 validated the runtime matrix, while review of
`.agent_work/context/analysis/RC5-GA-PACKAGING-DECISIONS.md` identified two
non-blocking GA distribution decisions: CUDA-only image delivery and blank
`PODMAN_COMPOSE_PROVIDER` onboarding.
**Decision**: Keep `TASK-083` focused on PR #33 and RC5 runtime validation.
Create `TASK-084` for CPU/CUDA package strategy, Podman provider auto-detect or
fetch-and-verify support, and public evidence sanitization.
**Output**: Active task file created.
**Next**: Lock owner decisions for image/package strategy and approved provider
onboarding before implementation.

### 2026-06-16 - Owner Decisions And Recommended Path Locked
**Objective**: Convert the RC5 review follow-up discussion into a concrete
`TASK-084` implementation path.
**Context**: Follow-up review confirmed that air-gapped/offline install is no
longer a requirement and that GA should optimize for a connected, supportable
release path.
**Decision**: Use two digest-pinned GA control ZIP variants (`cpu` and
`cuda121`), do not bundle a third-party Compose provider binary, add approved
provider auto-detect, add an explicit online fetch-and-verify helper for
Podman provider setup, and keep dataset ZIP path traversal hardening in
`TASK-085`.
**Execution**: Updated the task requirements, acceptance criteria,
implementation plan, validation strategy, and non-goals to reflect the locked
decisions and RC5 review defect cleanup.
**Output**: Task file now has a concrete implementation outline ready for
review and execution.
**Next**: Create a cross-task analysis memo for second-review feedback, then
start `TASK-084` implementation after owner approval to proceed.

### 2026-06-16 - Reviewer Gate Revisions Incorporated
**Objective**: Tighten the `TASK-084` plan after second-review feedback.
**Context**: The reviewer agreed with the main decisions but identified release
gates that needed to be explicit before implementation starts.
**Decision**: Keep `TASK-084` first for implementation, but make `TASK-085` a
hard pre-final-package gate. Use one shared Model & Data Package for both CPU
and CUDA control ZIPs unless assets differ. Add stale `.env` mismatch
detection, CPU-package GPU rejection, provider allowlist semantics, helper
print-by-default plus `-Apply`, final CUDA Docker GPU and Podman GPU CDI
validation, and SBOM/provenance evidence.
**Execution**: Updated requirements, acceptance criteria, implementation plan,
validation strategy, and non-goals.
**Output**: Task file now reflects the reviewed GA packaging gate order.
**Next**: Start implementation with the RC5 runtime defect cleanup slice, then
move through package generation and Podman provider onboarding before selecting
`TASK-085`.

### 2026-06-16 - Runtime Cleanup, Package Guardrails, And Provider Onboarding Implemented
**Objective**: Execute the first implementation slice before final image
publication and `TASK-085`.
**Context**: RC5 review left several GA-blocking polish issues that were safe
to implement before cutting final CPU/CUDA package artifacts.
**Execution**:
- Added bounded Podman helper command execution with timeout enforcement and
  Windows child-process cleanup.
- Changed Podman `cp` fallback lookup to prefer provider-consistent
  `compose ps` service container IDs before label-based fallback.
- Updated Podman GPU enablement image resolution to honor package
  `.env.example` image/digest values before `.env` exists.
- Expanded stale stopped-container port reporting to enumerate all known
  conflicts for the requested host port.
- Added release-package `.env` image/digest mismatch detection that fails
  closed with repair guidance instead of silently reusing stale image values.
- Added CPU package guardrail that rejects `-Gpu on` outside build mode and
  points users/support to the CUDA package.
- Updated package generation so CPU and CUDA control ZIP variants share one
  asset bundle release identity while retaining separate image/digest metadata.
- Added a machine-readable Podman Compose provider allowlist, approved-provider
  auto-detection, ambiguous-provider failure with candidate details, and
  Docker Desktop provider rejection.
- Added an explicit connected `scripts\install-podman-compose-provider.cmd`
  helper that downloads the pinned PyPI `podman-compose` wheel, verifies
  SHA-256, installs a package-local wrapper, prints the `.env` setting by
  default, and updates only `PODMAN_COMPOSE_PROVIDER` with backup when `-Apply`
  is used.
- Included the provider catalog/helper files in release package staging and
  updated package-facing Podman setup text.
**Validation**:
- PowerShell parser checks passed for
  `scripts\lib\TowerScoutCompose.ps1`,
  `scripts\lib\TowerScoutPodmanComposeProvider.ps1`,
  `scripts\install-podman-compose-provider.ps1`, and
  `scripts\package-release.ps1`.
- `git diff --check` passed.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_task_075_launcher_gpu.py tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py tests\unit\test_podman_gpu_enablement.py tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py -q -p no:cacheprovider`
  passed with `46 passed`.
**Open Gates**: CPU/CUDA image publication and digest capture, final package
assembly/evidence, broader docs pass, and public evidence sanitization remain
open. The `TASK-085` dataset ZIP path traversal gate is now closed.

### 2026-06-16 - PR 34 Merge-Readiness Blockers Remediated
**Objective**: Address the two blocking findings from the PR #34
merge-readiness review before moving the parent Task-084 PR out of draft.
**Context**: Review feedback identified that the connected
`podman-compose` helper extracted only `podman_compose.py` and therefore
depended on global `python-dotenv`/`PyYAML` availability, and that Podman GPU
image resolution could combine `TOWERSCOUT_IMAGE` from `.env` with
`TOWERSCOUT_IMAGE_DIGEST` from `.env.example`.
**Decision**: Keep the connected helper, but install the approved
`podman-compose` wheel into a package-local `.venv` with pinned runtime
dependency requirements. Resolve GPU image/digest values as same-source pairs:
explicit argument, process environment pair, `.env` pair, then
`.env.example` pair.
**Execution**:
- Updated `scripts\install-podman-compose-provider.ps1` to enforce Python
  `>=3.9`, create an isolated provider `.venv`, install the verified provider
  wheel plus pinned `python-dotenv==1.1.1` and `PyYAML==6.0.2`, and generate a
  wrapper that calls the venv-installed `podman-compose.exe`.
- Added provider catalog metadata for `requires_python` and pinned dependency
  requirements.
- Updated `scripts\lib\TowerScoutPodmanGpu.ps1` to parse image/digest values
  per file and avoid borrowing a digest from a lower-precedence source.
- Added regression coverage for the installer isolation contract, `.env` image
  override with blank digest, and process-environment image/digest pairing.
**Validation**:
- PowerShell parser checks passed for
  `scripts\install-podman-compose-provider.ps1` and
  `scripts\lib\TowerScoutPodmanGpu.ps1`.
- `git diff --check` passed.
- Focused regression tests passed:
  `.venv\Scripts\python.exe -m pytest tests\unit\test_task_081_runtime_hardening.py tests\unit\test_podman_gpu_enablement.py -q -p no:cacheprovider`
  with `20 passed`.
- Connected scratch install validation passed: the helper downloaded the
  approved PyPI wheel, verified SHA-256, created a scratch provider `.venv`,
  installed pinned runtime dependencies, and
  `podman-compose.cmd version` reported `podman-compose version 1.5.0`.
- Broader Task-084 regression set passed:
  `.venv\Scripts\python.exe -m pytest tests\unit\test_task_075_launcher_gpu.py tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py tests\unit\test_podman_gpu_enablement.py tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py -q -p no:cacheprovider`
  with `47 passed`.
**Next**: Commit and push the remediation to PR #34, then keep PR #35 stacked
until PR #34 merges and can become the base for the dataset ZIP restore
hardening PR.

### 2026-06-16 - PR 34 And PR 35 Merged; Final Package Gate Opened
**Objective**: Update task state after the GA packaging implementation slice and
dataset ZIP restore hardening both landed on `main`.
**Context**: PR #34 merged the `TASK-084` runtime cleanup, package guardrails,
and Podman provider onboarding work. PR #35 then merged the `TASK-085`
dataset ZIP restore traversal hardening after rebasing onto the merged
`TASK-084` baseline.
**Decision**: Treat the `TASK-085` pre-final-package gate as satisfied for
`TASK-084`. Do not publish final GA/pilot packages until the remaining
artifact gates are complete: CPU/CUDA image digests, package ZIP generation,
manifest/checksum/source/SBOM consistency, CPU Docker/Podman validation, CUDA
Docker GPU/Podman GPU CDI validation or hold decision, docs, and sanitized
evidence.
**Output**: Active task status and acceptance criteria updated; final package
gate checklist created at
`.agent_work/tasks/active/TASK-084/final-package-gate-checklist-2026-06-16.md`.
**Next**: Finalize release inputs, capture image digests, generate the CPU and
CUDA control packages, and run the package validation matrix.
