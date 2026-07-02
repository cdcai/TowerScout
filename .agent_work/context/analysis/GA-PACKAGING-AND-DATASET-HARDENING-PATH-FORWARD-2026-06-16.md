# GA Packaging And Dataset Hardening Path Forward

**Date**: 2026-06-16
**Scope**: Recommended path for `TASK-084` and `TASK-085`
**Primary task**: `.agent_work/tasks/completed/TASK-084-ga-packaging-hardening-and-podman-provider-onboarding.md`
**Follow-on task**: `TASK-085 Dataset ZIP Restore Path Traversal Hardening`
**Status update**: PR #34 (`TASK-084`) and PR #35 (`TASK-085`) merged on
2026-06-16. The dataset ZIP restore traversal gate is closed; remaining
`TASK-084` work is final CPU/CUDA image publication, control package assembly,
runtime validation, docs, and sanitized evidence.

## Executive Summary

RC5 candidate 3 proved the runtime matrix: Docker CPU, Docker GPU, Docker-Desktop-free Podman CPU, Podman GPU CDI, and fixed-fixture parity all passed. The remaining work is not a model or detection change. It is release packaging, Podman first-run support, and a separate dataset restore security hardening item.

Recommended sequencing after reviewer feedback, with current state:

1. Completed: `TASK-084` RC5 runtime-defect cleanup slice.
2. Completed: `TASK-084` package guardrails and Podman-provider onboarding
   implementation slice.
3. Completed: `TASK-085` dataset ZIP restore path traversal hardening.
4. Next: cut and publish final GA/pilot packages only after image, package,
   evidence, docs, and runtime-validation gates are complete.
5. Next: run final artifact validation across CPU Docker, CPU Podman, CUDA Docker
   GPU, CUDA Podman GPU CDI, manifest/env/image/checksum/source/SBOM
   consistency, and shared asset ZIP compatibility.

The recommended `TASK-084` path is now narrower because air-gapped/offline install is no longer a requirement. GA should optimize for a connected, supportable release path:

- two digest-pinned package variants, one CPU and one CUDA 12.1
- one shared Model & Data Package ZIP used by both variants unless assets
  actually diverge
- no bundled third-party Compose provider binary
- no silent provider download during normal launch
- approved Podman provider auto-detect
- explicit online fetch-and-verify helper for support/setup use, printing by
  default and writing `.env` only with an explicit apply flag

## Locked Decisions

### Image And Package Strategy

Decision: publish two GA control ZIP variants:

- `towerscout-<version>-cpu.zip`
- `towerscout-<version>-cuda121.zip`

Decision: publish one shared Model & Data Package ZIP for both variants unless
assets truly differ:

- `towerscout-<version>-assets-<asset-version>.zip`

Both control package manifests should identify the same asset bundle filename
and SHA-256. If a future release needs variant-specific assets, that should be
an explicit manifest-level decision rather than an accidental filename side
effect.

Rationale:

- CPU users avoid pulling the large CUDA image.
- Readiness output is less confusing because CPU users see a CPU PyTorch flavor.
- Support instructions are straightforward: "No validated NVIDIA GPU or unsure? Use the CPU package."
- Each release package can contain one pinned image reference, reducing launcher complexity.
- This keeps mutable tags out of the release runtime path.

Rejected alternatives:

- CUDA-only GA package: simplest, but keeps CPU users on a large CUDA image and creates misleading readiness output.
- One package with both digests: viable, but adds launcher selection complexity and a harder support story.
- Runtime torch selection inside one image: not recommended because it adds cold-start complexity without solving image size cleanly.

### Podman Compose Provider Strategy

Decision: do not bundle a third-party provider binary. Use auto-detect plus explicit online helper.

Expected behavior:

1. If `PODMAN_COMPOSE_PROVIDER` is set, validate it.
2. If it is blank, search for an approved standalone provider on `PATH`.
3. Reject Docker Desktop's bundled Compose provider.
4. If no approved provider is found, fail with clear next action.
5. Provide an explicit helper such as `scripts/install-podman-compose-provider.ps1` for connected setup.

The helper should:

- use a machine-readable provider allowlist containing provider id, display
  name, version, Windows AMD64 SHA-256, allowed executable names, disallowed
  path patterns, and required commands
- download a pinned provider version
- verify SHA-256 before use
- install to a supportable package-local or user-local path
- avoid Docker Desktop paths
- print the needed `.env` setting by default
- write `.env` only with an explicit apply flag, backing up `.env` first and
  updating only `PODMAN_COMPOSE_PROVIDER`
- avoid modifying unrelated host configuration

Normal `start.bat` and `scripts/launch.ps1` should not silently download or install executables.

Ambiguous auto-detection should fail with candidate details unless
`PODMAN_COMPOSE_PROVIDER` is set explicitly. Silent selection between multiple
approved executables is harder to support than a clear failure.

Rationale:

- Connected setup is allowed; offline setup is not a requirement.
- Avoiding bundled binaries reduces package size, endpoint-security friction, redistribution obligations, SBOM burden, and update/CVE ownership.
- Explicit setup keeps enterprise/government workstation behavior auditable.

### Dataset ZIP Path Traversal

Decision: keep dataset ZIP restore path traversal hardening in `TASK-085`, but
make it a hard pre-final-package gate.

Rationale:

- It is a real security issue, but it is separate from GA container/package distribution mechanics.
- It touches Flask dataset restore behavior rather than release packaging.
- It can be implemented and validated as a focused security task after `TASK-084`.
- It does not need to block the start of `TASK-084`.
- It should block final GA/pilot package publication unless dataset restore is
  disabled or explicitly excluded from that package.

## TASK-084 Recommended Implementation Outline

### Phase 1: RC5 Runtime Defect Cleanup

Fix the source-level issues found during RC5 package review before changing package shape.

Work items:

- Fix Podman `cp` fallback container lookup for dotted package/project names.
- Fix Podman GPU helper image resolution so package-pinned image/digest data is honored before `.env` exists.
- Enforce timeout parameters for Podman helper commands.
- Ensure timeout helpers work under Windows PowerShell 5.1 and PowerShell 7,
  capture stdout/stderr where practical, and avoid orphaned podman/ssh child
  processes.
- Enumerate all stopped containers using a requested host port, not just the first conflict.

Expected files:

- `scripts/lib/TowerScoutCompose.ps1`
- `scripts/lib/TowerScoutPodmanGpu.ps1`
- `scripts/lib/TowerScoutBootstrap.ps1`
- focused unit tests under `tests/unit/`

Validation:

- PowerShell parser checks for edited scripts.
- Focused pytest coverage for the four regressions.
- Existing launcher/package helper tests.

### Phase 2: Two-Package Image And Manifest Work

Work items:

- Ensure both CPU and CUDA image flavors are publishable through the existing container workflow.
- Publish or record the CPU digest.
- Publish or record the CUDA 12.1 digest.
- Update package generation to emit separate CPU and CUDA control ZIPs.
- Ensure each control ZIP carries a single pinned image identity.
- Ensure `.env.example`, `IMAGE.txt`, `release-manifest.v1.json`, and checksum sidecars agree.
- Ensure both package manifests point to the same shared Model & Data Package
  filename and SHA-256.
- Add stale `.env` image/digest mismatch detection with a package-aware
  "image mismatch" message and documented repair path.
- Reject CPU package launch with `-Gpu on` and direct the user/support tech to
  use the CUDA package for GPU validation.
- Keep CUDA `-Gpu on` fail-closed unless readiness reports
  `selected_device=cuda`.
- Keep release package runtime paths digest-pinned.
- Include `SOURCE.txt`, exact source ref, and SBOM/provenance entries in the
  package/evidence contract.

Expected files:

- `.github/workflows/container-publish.yml` if workflow behavior needs adjustment
- `scripts/package-release.*`
- `release-manifest.v1.json`
- `.env.example`
- docs under `docs/`
- release package tests

Validation:

- package summary for CPU ZIP
- package summary for CUDA ZIP
- release manifest checker for both variants
- checksum sidecar verification for both variants
- stale `.env` mismatch regression coverage
- CPU package `-Gpu on` rejection coverage
- shared asset ZIP filename/hash consistency across both manifests
- Docker CPU smoke against CPU package
- Podman CPU smoke against CPU package
- Docker GPU smoke against CUDA package
- Podman GPU CDI smoke against CUDA package
- if the GPU host is unavailable, hold the CUDA package or mark it as a
  pre-release/support candidate rather than final GA

### Phase 3: Podman Provider Onboarding

Work items:

- Auto-detect approved standalone Compose provider when `PODMAN_COMPOSE_PROVIDER` is blank.
- Store the approved-provider contract in machine-readable form.
- Fail ambiguous provider detection with candidate details instead of choosing
  silently.
- Preserve fail-closed Docker Desktop provider rejection.
- Add explicit online install helper for connected support/setup use.
- Make helper output support-safe and clear.
- Make helper default behavior print the `.env` setting without mutating files.
- Require `-Apply` before writing `.env`; back up `.env`, update only
  `PODMAN_COMPOSE_PROVIDER`, and preserve all other settings.
- Avoid silent install during normal launch.

Expected files:

- `scripts/lib/TowerScoutCompose.ps1`
- new helper such as `scripts/install-podman-compose-provider.ps1`
- possible `.cmd` wrapper if current package conventions require it
- `.env.example`
- docs under `docs/`
- PowerShell tests

Validation:

- blank provider with approved provider on `PATH` selects approved provider
- blank provider with multiple approved providers fails with candidates listed
- blank provider with no provider fails with clear next action
- Docker Desktop provider path remains rejected
- helper verifies hash and prints the expected provider configuration by default
- helper `-Apply` backs up `.env` and updates only `PODMAN_COMPOSE_PROVIDER`
- normal launch does not download or install provider binaries

### Phase 4: Docs And Evidence

Work items:

- Update package guide and quick-start language:
  - CPU package is the default for non-GPU or unsure users.
  - CUDA package is for support-validated NVIDIA GPU workstations.
  - Podman requires a running Podman machine and an approved provider.
  - Provider helper requires internet and explicit invocation.
- Remove or qualify stale CUDA-only and Docker Desktop-only assumptions.
- Ensure public evidence excludes provider-key previews, raw local AOIs, and personal local paths where possible.
- Document final image digests, package checksums, manifest validation, and runtime validation.
- Document shared asset ZIP identity, source ref, SBOM/provenance references,
  and the `TASK-085` pre-final-package gate.
- Treat final CUDA package validation as mandatory for both Docker GPU and
  Podman GPU CDI. Without that evidence, hold the CUDA package or label it as
  pre-release/support-only.

Validation:

- docs tests, if touched
- release package inclusion checks
- secret/provider-key safety scan over public evidence
- package-local docs smoke where available

### Follow-Up: Dockerfile And Base Image Lifecycle

The reviewer correctly noted Dockerfile/base-image hardening, including the
Node 18 lifecycle risk. This should remain a separate follow-up unless a
security scan makes it a release blocker during `TASK-084`. Mixing base-image
upgrades into the packaging/provider task would expand validation risk across
CI, frontend build, container build, and runtime smoke paths.

## TASK-085 Recommended Implementation Outline

### Objective

Harden `/uploaddataset` so a malicious dataset ZIP cannot write outside the intended session temp directory.

### Phase 1: Restore Flow Inspection

Work items:

- Inspect `webapp/towerscout.py` `/uploaddataset`.
- Inspect dataset export/restore tests.
- Identify filename adaptation behavior and session temp root ownership.

### Phase 2: Safe ZIP Member Handling

Required behavior:

- Normalize ZIP member paths before writing.
- Reject parent traversal such as `../evil.jpg`.
- Reject nested traversal such as `folder/../../evil.jpg`.
- Reject absolute paths.
- Reject Windows drive-prefixed paths such as `C:\temp\evil.jpg`.
- Reject UNC-style paths.
- Reject backslash traversal such as `..\evil.jpg`.
- Resolve target paths and verify they remain under the intended session temp root.
- Preserve valid exported dataset restore behavior.
- Avoid broad `extractall`; use controlled writes only.

Expected files:

- `webapp/towerscout.py`
- dataset restore tests under `tests/unit/`

### Phase 3: Regression Tests

Test cases:

- valid exported dataset ZIP restores successfully
- `../evil.jpg` is rejected
- `folder/../../evil.jpg` is rejected
- `/absolute/path.jpg` is rejected
- `C:\temp\evil.jpg` is rejected
- `..\evil.jpg` is rejected
- mixed slash/backslash traversal is rejected
- rejected restore does not create files outside the session temp root

Validation:

- dataset route tests
- focused Flask route tests
- upload/security validation tests

## Sequencing Recommendation

Run `TASK-084` implementation before `TASK-085` because `TASK-084` affects GA
release packaging and first-run install support. `TASK-085` should follow
immediately as a focused security hardening task and should block the final
GA/pilot package cut.

The final publication gate should be:

1. `TASK-084` RC5 runtime-defect cleanup complete.
2. `TASK-084` two-package and Podman provider onboarding complete.
3. `TASK-085` dataset ZIP traversal hardening complete, or dataset restore
   disabled/explicitly excluded.
4. Artifact validation complete:
   - CPU Docker and CPU Podman package validation
   - CUDA Docker GPU and CUDA Podman GPU CDI package validation
   - manifest, `.env.example`, `IMAGE.txt`, checksum, source, SBOM, image
     digest, and shared asset ZIP consistency
5. Public evidence/docs pass the provider-key and local-path redaction checks.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| CPU image digest is not published in time | CPU package cannot be finalized | Implement package support with test digests, then swap to published digest during release validation |
| `TASK-085` is delayed | Final package publication is blocked | Start `TASK-085` immediately after `TASK-084` implementation or explicitly disable/exclude dataset restore from the final package |
| Existing `.env` points at the wrong package image | Users may unknowingly launch the wrong CPU/CUDA image | Detect mismatch against `.env.example` and manifest, then fail closed or warn with documented repair |
| CPU package accepts `-Gpu on` | CPU users see misleading GPU behavior | Reject `-Gpu on` in the CPU package with package-aware guidance |
| Provider helper download source changes | Setup helper fails or checksum mismatch blocks install | Pin version and SHA-256, fail closed with clear message |
| Multiple approved providers are present | Auto-detect may choose the wrong provider | Fail ambiguous detection and list candidates unless `PODMAN_COMPOSE_PROVIDER` is explicit |
| Endpoint security flags downloaded provider | Podman support friction remains | Keep helper explicit, document source/checksum, and preserve manual provider configuration path |
| Package docs drift from actual artifacts | User confusion or failed validation | Validate both package summaries and release manifests before publication |
| Dataset ZIP hardening rejects valid legacy exports | Restore workflow regression | Add valid export fixture tests before adding malicious ZIP tests |
| Base-image or Node lifecycle work expands scope | Packaging task validation becomes harder to finish | Track base-image lifecycle separately unless Trivy/security review promotes it to a blocker |

## Reviewer Disposition

- Accepted: two GA package variants are preferred.
- Accepted: provider binaries should not be bundled.
- Accepted: explicit online provider setup is appropriate for the Podman support path.
- Accepted: provider helper should print by default and write only with `-Apply`.
- Accepted: `TASK-085` does not need to block the start of `TASK-084`, but it
  should block final package publication.
- Accepted: RC5 runtime-defect cleanup can stay in `TASK-084` unless RC5 itself
  is being reissued or promoted.
- Added: shared Model & Data Package contract for both control ZIP variants.
- Added: stale `.env` package mismatch detection.
- Added: CPU-package GPU guardrail.
- Added: provider allowlist and ambiguous-detection behavior.
- Added: final CUDA package validation must include Docker GPU and Podman GPU
  CDI.
- Added: SBOM/provenance acceptance criteria.
- Deferred: Dockerfile/base-image lifecycle hardening remains follow-up unless
  scan results make it release-blocking.

## Recommended Next Step

Use this revised memo plus
`.agent_work/tasks/completed/TASK-084/final-package-gate-checklist-2026-06-16.md`
as the working package-publication gate. Finalize release inputs, capture CPU
and CUDA image digests, generate the CPU/CUDA control ZIPs, and run the
validation/evidence matrix before publishing any final GA/pilot package.
