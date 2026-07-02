# TASK-084: GA Packaging Hardening And Podman Provider Onboarding

**Status**: COMPLETED - implementation, package rebuild, Docker CPU,
Docker CUDA CPU-fallback, Podman CPU, CPU-package `-Gpu on` guardrail,
Docker GPU, Podman GPU CDI, public-safe evidence, official `v0.1.0-rc6`
publication, and post-publication downloaded-release verification passed on
June 17, 2026; remaining external tester launch gates belong to `TASK-073`.
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
- [x] CPU image is published and digest-pinned.
- [x] Package generation emits separate CPU and CUDA control ZIPs without
      mutable tags in release runtime paths.
- [x] Both package manifests identify the same shared Model & Data Package
      filename and SHA-256 unless a documented asset difference exists.
- [x] Package setup/launch detects stale `.env` image or digest mismatches and
      gives a clear repair action instead of silently reusing the wrong image.
- [x] CPU package `-Gpu on` fails with a package-aware "use CUDA package"
      message.
- [x] CUDA package `-Gpu on` remains fail-closed unless readiness reports
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
- [x] Final package evidence includes `-AssetBundleSha256`,
      `release-manifest.v1.json`, package checksum sidecars, image digest(s),
      `SOURCE.txt`, SBOM artifacts or references, and sanitized runtime
      validation summaries.
- [x] Final CPU package evidence includes Docker CPU and Podman CPU validation.
- [x] Final CUDA package evidence includes Docker GPU and Podman GPU CDI
      validation, or the CUDA package is held from final publication.
- [x] `TASK-085` dataset ZIP restore hardening is merged and validated before
      final GA/pilot package publication.
- [x] User/support docs explain the selected package and Podman-provider path in
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
`.agent_work/tasks/completed/TASK-084/final-package-gate-checklist-2026-06-16.md`.
**Next**: Finalize release inputs, capture image digests, generate the CPU and
CUDA control packages, and run the package validation matrix.

### 2026-06-16 - User-Facing CPU/CUDA Package Docs Updated
**Objective**: Update package-facing and UAT-facing documentation before
recreating final CPU/CUDA package artifacts.
**Context**: After PR #36 merged the final-package checklist, the remaining
user-facing docs still assumed a single Application Package ZIP in several
places.
**Execution**:
- Updated README, quick-start, package-guide, project-overview, user-guide,
  release asset bundle contract, OCI support quick start, and OCI runtime
  contract docs to explain the default CPU Application Package, the
  support-assigned CUDA 12.1 Application Package, the shared Model & Data
  Package, and the Podman Compose provider helper path.
- Updated UAT tester materials:
  `RC1-PILOT-UAT-CHECKLIST.md`,
  `RC1-PILOT-HANDOFF-PACKET.md`,
  `TESTER-ISSUE-REPORT-CHECKLIST.txt`,
  `README.md`, and
  `TowerScout_V1_RC1_UAT_User_Guide.docx`.
- Updated package-local route test expectations for the new package wording.
**Validation**:
- `git diff --check` passed.
- `.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md`
  passed.
- `.venv\Scripts\python.exe -m pytest tests/unit/test_release_package_script.py tests/unit/test_task_080_uat_followups.py`
  passed with `8 passed`.
- `.venv\Scripts\python.exe -m pytest tests/unit/test_flask_routes.py`
  passed with `49 passed`.
- DOCX OOXML text extraction confirmed required CPU/CUDA package,
  Podman-provider helper, and `selected_device=cuda` wording.
- Added a static Table of Contents to
  `TowerScout_V1_RC1_UAT_User_Guide.docx`, kept the normal Docker CPU path in
  the main body, and moved support-assigned Podman/GPU tracks into Appendix A.
**Render Note**: Full DOCX page rendering now passed through the direct
LibreOffice plus Poppler fallback. The final rendered guide is 11 pages; every
PNG page was visually inspected for clipping, overlap, table breakage, and
stale TOC page numbers. The packaged `render_docx.py` helper still fails on
this Windows host because its LibreOffice profile URI is not Windows-safe, so
the direct renderer command is the documented local workaround for this pass.
**Next**: Commit/push the docs slice, open the docs PR, then proceed to final
CPU/CUDA image digest capture and package validation.

### 2026-06-16 - PR 37 Asset Bundle Lookup Review Remediated
**Objective**: Address PR #37 review feedback that variant control packages
could generate `release_version` values with `-cpu` or `-cuda121` while sharing
one unsuffixed Model & Data Package ZIP.
**Context**: `scripts/package-release.ps1` records the shared asset ZIP name in
`release_artifacts.asset_bundle`, but setup/bootstrap discovery and filename
validation still derived the asset ZIP candidate from `release_version`. That
would make a CPU package look for
`towerscout-<release-version>-cpu-assets-...zip` instead of the documented
shared `towerscout-<release-version>-assets-...zip`.
**Execution**:
- Updated `scripts/lib/TowerScoutBootstrap.ps1` so setup discovery and asset
  ZIP filename validation prefer the exact
  `release_artifacts.asset_bundle` value when present, with the existing
  `release_version` fallback preserved for source/local packages.
- Added PowerShell-backed bootstrap regression coverage for variant packages
  sharing a manifest-declared unsuffixed asset ZIP.
- Updated the release asset bundle contract to state that setup enforces the
  filename from `release_artifacts.asset_bundle`.
**Validation**:
- `.venv\Scripts\python.exe -m pytest tests/unit/test_task_074_bootstrap.py tests/unit/test_release_package_script.py tests/unit/test_release_manifest_schema.py -q -p no:cacheprovider`
  passed with `27 passed`.
- `git diff --check` passed.
- `.venv\Scripts\python.exe .agents\skills\towerscout-end-user-docs-check\scripts\check_doc_commands.py . docs README.md`
  passed.
**Next**: PR #37 is merged; sync local `main`, refresh the final package gate
baseline, then collect final release inputs before image publication.

### 2026-06-16 - PR 37 Merged And Final Package Baseline Refreshed
**Objective**: Move from the user/support docs PR into the final Task-084
package gate using the actual merged source baseline.
**Context**: PR #37 merged after adding CPU/CUDA package docs, the Word UAT
Guide TOC/appendix restructuring, and the asset lookup remediation for
variant control packages sharing one unsuffixed Model & Data Package ZIP.
**Execution**:
- Fetched/pruned GitHub refs and fast-forwarded local `main` to
  `be67e67382e437b36fd1851fb89bc44e6f590200`.
- Updated the final package gate checklist source baseline from the older
  `ff01c10f6b45` placeholder to the post-PR #37 `main` ref.
- Marked the final package gate docs items complete for CPU/CUDA package
  selection and Podman approved-provider helper guidance.
**Output**: Task state now points at the current post-PR #37 `main` baseline.
**Next**: Select the final release version/name, capture the shared asset ZIP
filename and SHA-256, then publish/capture CPU and CUDA image digests before
generating final control ZIPs.

### 2026-06-16 - RC6 CPU/CUDA Images And Control Packages Cut
**Objective**: Generate both RC6 package variants from the post-PR #37 source
baseline so runtime validation can proceed against actual release artifacts.
**Context**: The selected release name is `v0.1.0-rc6`. Air-gapped/offline
install is out of scope, and both package variants intentionally share the same
Model & Data Package ZIP.
**Execution**:
- Reused the validated asset bundle bytes as
  `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-assets-towerscout-v1-assets-2026-05-05.zip`.
- Published CPU and CUDA 12.1 images from `main` at
  `be67e67382e437b36fd1851fb89bc44e6f590200`.
- Generated `towerscout-v0.1.0-rc6-cpu.zip` and
  `towerscout-v0.1.0-rc6-cuda121.zip` with `-AssetBundleVersion v0.1.0-rc6`
  and the shared asset SHA-256.
**Output**:
- Shared asset ZIP SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- CPU image:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu@sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`.
- CUDA image:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121@sha256:98a9843d3e07abd6d93d19b4fae89d7db3aab319baeb85115dd0508368401b41`.
- CPU control ZIP SHA-256:
  `65b0595de84934347ccec7e156da7e2e101f6588d4fa18cca45424dce3caae5e`.
- CUDA control ZIP SHA-256:
  `99af4a53f2044a96715a2def10ac11407ad4eef9ce550b66c9e007bed1faacd0`.
**Validation**:
- `git diff --check` passed before package generation.
- Static release manifest checks passed for both package directories.
- Package summaries showed both ZIPs contain expected top-level files,
  compliance notices, docs, scripts, `release-manifest.v1.json`, and
  `webapp/asset_manifest.v1.json`.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py tests\unit\test_task_074_bootstrap.py -q -p no:cacheprovider`
  passed with `27 passed`.
- CPU and CUDA `setup-towerscout.cmd -VerifyOnly` reached package ZIP and
  shared asset ZIP checksum verification before host engine preflight failed.
- CPU package `start.bat -Gpu on` failed closed with package-aware guidance to
  use the CUDA 12.1 package.
**Open Runtime Gates**:
- Docker runtime validation is blocked on this local host because Docker
  Desktop is not running or reachable.
- Podman runtime validation is blocked on this local host because no approved
  Compose provider is configured and `podman compose` reports a Podman machine
  connection mismatch.
**Next**: Start Docker Desktop or repair Podman provider/machine state, then
run CPU Docker/Podman setup smokes and CUDA Docker GPU/Podman GPU CDI smokes
against these RC6 artifacts.

### 2026-06-16 - RC6 Docker CPU And CUDA Fallback Smokes
**Objective**: Validate the generated RC6 package artifacts against Docker
Desktop after the host was restarted and Docker became reachable.
**Context**: The initial local package cut could only run static checks because
Docker Desktop was not reachable. After restart, Docker Desktop reported server
version `29.5.3`.
**Execution**:
- Attempted CPU package setup on port `5005`; package and asset checks passed,
  but startup failed because an existing unrelated `towerscout-towerscout-1`
  container already owned host port `5005`.
- Cleaned up only the failed RC6 CPU compose container/network and retried on
  port `5015`.
- Ran the CPU package through
  `setup-towerscout.cmd -Engine docker -Port 5015 -Gpu off -NoBrowser
  -TimeoutSeconds 240 -RestartWaitSeconds 240`.
- Captured CPU package status, then stopped the RC6 CPU package container.
- Ran the CUDA package through
  `setup-towerscout.cmd -Engine docker -Port 5016 -Gpu on -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`; the image pulled, but Docker's
  NVIDIA prestart hook failed before app startup because no WSL-visible NVIDIA
  adapters were found.
- Cleaned up the failed CUDA GPU compose attempt.
- Ran the CUDA package CPU-fallback path through
  `setup-towerscout.cmd -Engine docker -Port 5016 -Gpu off -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`.
- Captured CUDA package status, then stopped the RC6 CUDA package container.
**Output**:
- CPU Docker package smoke passed with readiness `setup_required`,
  `asset_status=ok`, `runtime.container_engine=docker`,
  `device_policy=cpu`, `selected_device=cpu`, `pytorch_flavor=cpu`, and image
  digest
  `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`.
- CPU status snapshot reported Docker Compose v5.1.4, a healthy container, all
  nine asset entries `ok`, `torch_version=2.2.1+cpu`, and
  `torch_cuda_available=false`.
- CUDA Docker GPU launch failed closed with NVIDIA runtime error
  `WSL environment detected but no adapters were found`; Docker GPU release
  evidence remains open until a WSL-visible NVIDIA adapter is available, or the
  CUDA package is held/labeled support-candidate.
- CUDA CPU-fallback package smoke passed with readiness `setup_required`,
  `asset_status=ok`, `runtime.container_engine=docker`,
  `device_policy=cpu`, `selected_device=cpu`, `pytorch_flavor=cuda121`, and
  image digest
  `sha256:98a9843d3e07abd6d93d19b4fae89d7db3aab319baeb85115dd0508368401b41`.
- CUDA status snapshot reported Docker Compose v5.1.4, a healthy container,
  all nine asset entries `ok`, `torch_version=2.2.1+cu121`,
  `torch_cuda_build=12.1`, and `torch_cuda_available=false` while GPU mode was
  off.
**Validation**: Docker CPU and CUDA CPU-fallback package paths are validated.
Docker GPU remains blocked by host NVIDIA adapter exposure, and Podman CPU/GPU
remain pending.
**Next**: Either validate Docker GPU and Podman GPU on a host with WSL-visible
NVIDIA adapters plus a ready approved Podman Compose provider, or make an
explicit hold/support-candidate decision for the CUDA package before final
publication.

### 2026-06-16 - RC6 Podman CPU Smoke And Rebuild Blocker
**Objective**: Answer the open Podman validation question against the generated
RC6 CPU package.
**Context**: Docker validation passed after host restart, but Podman had not
yet been exercised against the RC6 artifacts. The host reported Podman
`5.8.2`; `podman info` was reachable, while the default `podman compose`
connection still had a stale machine/provider URI.
**Execution**:
- Ran the package-local
  `scripts\install-podman-compose-provider.cmd -Apply -Force` helper against
  `dist\v0.1.0-rc6\towerscout-v0.1.0-rc6-cpu`; the connected helper downloaded
  the approved PyPI `podman-compose` 1.5.0 wheel, verified SHA-256, created the
  package-local provider `.venv`, installed pinned `python-dotenv==1.1.1` and
  `PyYAML==6.0.2`, and updated only package `.env`
  `PODMAN_COMPOSE_PROVIDER` after backup.
- Ran
  `setup-towerscout.cmd -Engine podman -Port 5017 -Gpu off -NoBrowser
  -TimeoutSeconds 300 -RestartWaitSeconds 300`.
- The first run started the container but failed during asset import because
  direct `podman cp` fallback could not find the service container.
- Diagnosed that `podman-compose` labels the package project as
  `towerscout-v010-rc6-cpu`, while the helper searched for the raw dotted
  folder name `towerscout-v0.1.0-rc6-cpu`.
- Updated source `Get-TowerScoutComposeProjectName` to normalize non
  `[a-z0-9_-]` characters out of the inferred package folder name while still
  honoring explicit `COMPOSE_PROJECT_NAME`.
- Changed Podman asset copy to use provider `compose ps` for service container
  identity, then direct `podman cp`, instead of first invoking unsupported
  provider `cp`; label lookup remains as a fallback and now honors
  `COMPOSE_PROJECT_NAME` from package `.env`.
- Added focused regression coverage for dotted release-package project-name
  normalization and direct Podman copy.
- Applied the same source fix locally to the ignored generated CPU package for
  validation only; the existing RC6 ZIPs were cut before the fix and must be
  rebuilt before publication.
**Output**:
- Locally patched Podman CPU package smoke passed on port `5017` with
  readiness `setup_required`, `asset_status=ok`,
  `runtime.container_engine=podman`, `device_policy=cpu`,
  `selected_device=cpu`, `pytorch_flavor=cpu`, and image digest
  `sha256:2c21e8cc6b65b1b15a82e8d679a6e13781d29b1664515b8236a5529d6385ed9a`.
- Status snapshot showed the approved package-local provider path, a healthy
  Podman container, all nine asset entries `ok`, and the expected CPU PyTorch
  runtime.
- The RC6 Podman validation container was stopped and removed after evidence
  capture.
**Validation**:
- `.venv\Scripts\python.exe -m pytest tests\unit\test_task_081_runtime_hardening.py -q -p no:cacheprovider`
  passed with `15 passed`.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_task_081_runtime_hardening.py tests\unit\test_task_074_bootstrap.py tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py -q -p no:cacheprovider`
  passed with `42 passed`.
- `git diff --check` passed.
**Next**: Commit this Podman source fix, rebuild CPU and CUDA control ZIPs
from the updated source ref, then rerun CPU Podman validation against the
rebuilt publishable CPU ZIP. CUDA GPU and Podman GPU CDI remain gated on a
WSL-visible NVIDIA host or an explicit hold/support-candidate decision.

### 2026-06-16 - PR 38 Merged; RC6 Packages Rebuilt And CPU Gates Passed
**Objective**: Refresh the RC6 release artifacts after the Podman
release-package asset import fix landed on `main`.
**Context**: PR #38 fixed package-local Podman asset import by keeping
provider-backed `compose ps` lookup ahead of direct `podman cp` and by reading
`COMPOSE_PROJECT_NAME` from the package `.env` before label fallback. The prior
RC6 ZIPs were pre-fix validation artifacts only.
**Execution**:
- Fast-forwarded local `main` to
  `12daa5536f580f76d063559e86b9a474451bc54b`.
- Re-published CPU and CUDA 12.1 images from that source ref so OCI revision
  metadata matches the rebuilt control packages.
- Rebuilt `towerscout-v0.1.0-rc6-cpu.zip` and
  `towerscout-v0.1.0-rc6-cuda121.zip` with the shared Model & Data Package
  ZIP and its SHA-256.
- Expanded the rebuilt ZIPs beside the shared asset ZIP and validated the
  package setup path from those expanded artifacts.
**Output**:
- CPU image:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cpu@sha256:d2b4f668e62ecbcdc0e0b5a5db4d8fbf2865651f5854484ada5db042956a75bd`.
- CUDA image:
  `ghcr.io/j-schulein/towerscout:v0.1.0-rc6-cuda121@sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`.
- CPU control ZIP SHA-256:
  `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d`.
- CUDA control ZIP SHA-256:
  `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603`.
**Validation**:
- `git diff --check` passed.
- Package summaries for both rebuilt ZIPs found expected runtime files,
  compliance notices, docs, scripts, `release-manifest.v1.json`, and
  `webapp/asset_manifest.v1.json`.
- `.venv\Scripts\python.exe -m pytest tests\unit\test_release_package_script.py tests\unit\test_release_manifest_schema.py tests\unit\test_task_074_bootstrap.py -q -p no:cacheprovider`
  passed with `27 passed`.
- Rebuilt CPU package Docker smoke passed on port `5015` with readiness
  `setup_required`, `asset_status=ok`, `selected_device=cpu`,
  `pytorch_flavor=cpu`, and the final CPU image digest.
- Rebuilt CUDA package Docker CPU-fallback smoke passed on port `5016` with
  readiness `setup_required`, `asset_status=ok`, `selected_device=cpu`,
  `pytorch_flavor=cuda121`, `torch_version=2.2.1+cu121`, and the final CUDA
  image digest.
- Rebuilt CPU package Podman smoke passed on port `5017` after the package
  helper installed the approved `podman-compose` 1.5.0 provider into a
  package-local `.venv` with pinned `python-dotenv` and `PyYAML` dependencies.
- Rebuilt CPU package `start.bat -Gpu on` failed closed with package-aware
  guidance to use the CUDA package.
- Docker and Podman smoke containers were stopped and removed after status
  capture; only the unrelated pre-existing `towerscout-towerscout-1` Docker
  container remained on port `5005`.
**Next**: Decide whether to run GPU validation on a WSL-visible NVIDIA host or
hold/label the CUDA package as support-candidate, then prepare a sanitized
final evidence summary.

### 2026-06-16 - Unofficial GPU Validation Prerelease Published
**Objective**: Make the rebuilt RC6 candidate artifacts available to the GPU
machine without consuming the official `v0.1.0-rc6` release tag.
**Context**: Local transfer of the six RC6 artifacts to the GPU machine was not
practical. The official `v0.1.0-rc6` release name should remain reserved until
the CUDA Docker GPU and Podman GPU CDI gates are resolved.
**Decision**: Publish an unofficial GitHub prerelease using tag
`gpu-validation-2026-06-16`, title
`Unofficial GPU Validation Build - v0.1.0-rc6 Candidate`, and target commit
`12daa5536f580f76d063559e86b9a474451bc54b`.
**Execution**:
- Uploaded the rebuilt CPU Application Package ZIP and checksum sidecar.
- Uploaded the rebuilt CUDA 12.1 Application Package ZIP and checksum sidecar.
- Uploaded the shared Model & Data Package ZIP and checksum sidecar.
- Uploaded `README-GPU-VALIDATION.md` and used it as the release notes so the
  GPU-machine tester has commands, pass criteria, and evidence-capture
  expectations at the download source.
**Output**:
- Prerelease URL:
  `https://github.com/J-Schulein/TowerScout/releases/tag/gpu-validation-2026-06-16`.
- The prerelease is marked as prerelease and targets
  `12daa5536f580f76d063559e86b9a474451bc54b`.
- Uploaded release asset digests reported by GitHub match the expected ZIP
  SHA-256 values for the CPU ZIP, CUDA ZIP, and shared asset ZIP.
**Next**: Use this prerelease on the GPU machine for Docker GPU and Podman GPU
CDI validation. Keep the official `v0.1.0-rc6` release unpublished until those
results are accepted or a CUDA hold/support-candidate decision is made.

### 2026-06-17 - RC6 GPU Host Evidence Accepted And Evidence Packet Hardened
**Objective**: Close the final CUDA runtime evidence gate and convert the
email-safe GPU evidence packet into a standalone, public-safe handoff summary.
**Context**: The GPU host evidence folder contained Docker GPU, Podman GPU CDI,
Google, Azure, and CPU-package guardrail artifacts from the unofficial
`gpu-validation-2026-06-16` prerelease. Review found the runtime evidence was
strong enough to accept the CUDA package, but the packet needed standalone
provenance and a public-safe summary that omits raw AOI/local context.
**Execution**:
- Reviewed the GPU validation evidence folder:
  `.agent_work/tasks/completed/TASK-084/evidence/TowerScout-rc6-gpu-validation-evidence-emailsafe/TowerScout-rc6-gpu-validation-evidence/`.
- Accepted Docker GPU and Podman GPU CDI readiness because both reached
  `ready` with `device_policy=cuda`, `selected_device=cuda`,
  `pytorch_flavor=cuda121`, `torch_cuda_available=true`,
  `cuda_device_name="NVIDIA T1000 8GB"`, assets `ok`, and the final CUDA image
  digest
  `sha256:392b162b2ebe5f94126e8d7db9b75c4fbcc1652449f8376d0a7a5a5979eec3b0`.
- Accepted end-to-end detection because Google and Azure both ran on CUDA for
  Docker GPU and Podman GPU CDI, with YOLOv5 primary inference and EfficientNet
  secondary classification reporting CUDA execution.
- Kept the Podman/Google summary conservative: the included Podman/Google log
  captures the matching `49` selected high-mode run; Docker/Google supplies
  repeated high/low evidence.
- Added `ARTIFACT-PROVENANCE.md` so the packet records source ref, prerelease
  tag, CPU/CUDA package checksums, shared asset checksum, image digests, and
  the runtime evidence index.
- Added `PUBLIC-SUMMARY.md` as the public-safe external attachment and kept the
  local internal evidence summary ignored with the raw evidence artifacts.
**Output**:
- Final CUDA package evidence now includes Docker GPU and Podman GPU CDI
  validation.
- The CPU package guardrail evidence remains accepted: `-Gpu on` exits `1`
  before container startup with package-aware guidance to use the CUDA package.
- The final package gate checklist now marks the CUDA GPU, Podman GPU CDI,
  provenance, and public-safe evidence gates complete.
**Validation**:
- `python .agent_work\scripts\validate_agent_work.py` passed.
- `git diff --check` passed.
- `python .agents\skills\towerscout-secret-and-provider-key-safety\scripts\scan_for_sensitive_terms.py .agent_work\tasks\completed\TASK-084\evidence\TowerScout-rc6-gpu-validation-evidence-emailsafe\TowerScout-rc6-gpu-validation-evidence\PUBLIC-SUMMARY.md .agent_work\tasks\completed\TASK-084\evidence\TowerScout-rc6-gpu-validation-evidence-emailsafe\TowerScout-rc6-gpu-validation-evidence\ARTIFACT-PROVENANCE.md`
  returned `matches: 0`.
- Targeted grep over `PUBLIC-SUMMARY.md` and `ARTIFACT-PROVENANCE.md` found no
  raw AOI, local user paths, key-preview strings, or common provider-key
  patterns.
**Next**: Prepare the official `v0.1.0-rc6` release handoff/publication step
using the CPU package as the default user path and the CUDA package as the
support-validated NVIDIA GPU path.

### 2026-06-17 - Official RC6 Release Handoff Drafted
**Objective**: Convert the accepted RC6 package and GPU evidence into an
owner-reviewable official GitHub release handoff.
**Context**: The repository is public, so raw email-safe GPU artifacts with AOI
and local validation context must not be staged or attached publicly. The
official release needs exact assets, checksums, image digests, release notes,
and a command template without publishing before owner approval.
**Execution**:
- Added `.gitignore` inside the local RC6 GPU evidence folder so only
  `ARTIFACT-PROVENANCE.md` and `PUBLIC-SUMMARY.md` are tracked; the local
  internal evidence summary and raw evidence artifacts remain ignored.
- Added `.agent_work/tasks/completed/TASK-084/official-rc6-release-notes.md` as
  public-safe release notes.
- Added `.agent_work/tasks/completed/TASK-084/official-rc6-release-handoff-2026-06-17.md`
  with required release assets, checksums, image digests, release settings,
  publication command template, and post-publication checks.
- Refreshed the RC1 Pilot / UAT handoff packet with exact RC6 artifact values
  while keeping approval set to `NO`.
**Output**:
- Official release publication is ready for owner/reviewer approval.
- Release publication itself remains intentionally unexecuted.
**Validation**: Pending final post-edit validation in the current handoff slice.
**Next**: After approval, publish the official `v0.1.0-rc6` prerelease, verify
downloaded release assets, then mark TASK-084 complete and hand off to
TASK-073 tester/cohort approval.

### 2026-06-17 - Official RC6 Release Published And Post-Validated
**Objective**: Execute the approved official release publication and validate
the assets exactly as external testers will download them.
**Context**: PR #39 merged the public-safe release handoff and evidence
tracking. The remaining `TASK-084` gate was official `v0.1.0-rc6` publication
followed by downloaded-release checksum and runtime validation.
**Execution**:
- Published the official GitHub prerelease:
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.0-rc6`.
- Verified the release metadata: tag `v0.1.0-rc6`, title
  `TowerScout v0.1.0-rc6`, prerelease `true`, target commit
  `12daa5536f580f76d063559e86b9a474451bc54b`, and published timestamp
  `2026-06-17T16:15:03Z`.
- Downloaded only the official `towerscout-v0.1.0-rc6*` release assets into a
  fresh validation folder:
  `.agent_work/tmp/rc6-post-publication-20260617-121723`.
- Verified downloaded CPU, CUDA, and shared Model & Data Package ZIP SHA-256
  values against both expected release values and their downloaded sidecars.
- Extracted the downloaded CPU package and ran the package setup flow with the
  downloaded CPU ZIP and shared Model & Data Package ZIP on Docker Desktop
  port `5006`.
**Output**:
- CPU package SHA-256:
  `fc32112935d4b7d32e9a9d24272648692e6362cecbd99fd3f3b748ec9757f83d`.
- CUDA package SHA-256:
  `79800f2ca0af4b274e07878c8ba69cdcc1ba1822618c9a5661bfab004980c603`.
- Shared Model & Data Package SHA-256:
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`.
- Downloaded CPU setup verified package and asset sidecars, staged assets,
  imported assets with hash verification, started TowerScout, and returned
  readiness `state=setup_required` with `components.assets.status=ok`,
  `runtime.container_engine=docker`, `runtime.device_policy=cpu`,
  `runtime.selected_device=cpu`, and `runtime.pytorch_flavor=cpu`.
- The app root returned HTTP `200`; the temporary validation container was
  stopped and removed after evidence capture.
**Validation**:
- Official release metadata and uploaded-asset digests verified through
  `gh release view`.
- Downloaded release ZIP hashes and sidecars matched the expected release
  handoff values.
- Downloaded CPU package setup/readiness smoke passed on Docker Desktop.
**Next**: `TASK-084` is complete. Continue with `TASK-073` tester/cohort
selection, provider setup / bounded Azure smoke for the official tester path
when credentials and tester environment are available, and owner/reviewer UAT
packet approval before external tester send.
