# TASK-084: GA Packaging Hardening And Podman Provider Onboarding

**Status**: PLANNED - selected after RC5 candidate 3 runtime validation split GA packaging/distribution decisions out of `TASK-083`
**Priority**: HIGH
**Type**: C (Release Packaging / Distribution / First-Run Support)
**Estimated Effort**: 1-3 days (8-24 hours), depending on one-package versus two-package image selection
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
- `.agent_work/context/analysis/towerscout-rc5-candidate3-validation-evidence-2026-06-15/`
- `TASK-083` implementation and validation history

## Requirements

**R-084-001**: WHEN GA packages are assembled, THE PROJECT SHALL choose and
document whether CPU and CUDA users receive separate pinned packages or one
package that selects between pinned image digests.

**R-084-002**: IF separate CPU and CUDA packages are selected, THEN THE RELEASE
SHALL publish both image flavors, generate separate control ZIPs, and publish
checksum sidecars for each artifact.

**R-084-003**: IF one package with both digests is selected, THEN THE LAUNCHER
SHALL select the correct image based on the requested GPU mode without requiring
users to edit `.env`.

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

## Acceptance Criteria

- [ ] Owner decision recorded for image/package strategy: two packages, one
      package with both digests, or documented CUDA-only waiver.
- [ ] CPU image is published and digest-pinned, or the CUDA-only approach is
      explicitly accepted for GA.
- [ ] Package generation supports the selected image strategy without mutable
      tags.
- [ ] Podman provider auto-detect and/or fetch-and-verify helper is implemented
      and tested, or a documented owner waiver keeps support-installed provider
      setup for GA.
- [ ] Docker Desktop's bundled Compose provider remains fail-closed for the
      Podman support path.
- [ ] Final package evidence includes `-AssetBundleSha256`,
      `release-manifest.v1.json`, package checksum sidecars, image digest(s),
      and sanitized runtime validation summaries.
- [ ] User/support docs explain the selected package and Podman-provider path in
      plain language.

## Implementation Plan

1. **Decision Lock**
   - Confirm two pinned packages versus one auto-selecting package.
   - Confirm provider strategy: auto-detect plus fetch-and-verify helper, or a
     bounded waiver for support-installed providers.

2. **Image And Package Work**
   - Publish the CPU image flavor if selected.
   - Update package generation and manifest fields for the selected package
     strategy.
   - Keep CUDA package behavior compatible with the RC5 candidate 3 validation
     boundary.

3. **Podman Provider Onboarding**
   - Add approved provider discovery when `PODMAN_COMPOSE_PROVIDER` is blank.
   - Add a fetch-and-verify helper if network-assisted setup is approved.
   - Preserve fail-closed Docker Desktop provider detection.

4. **Docs And Evidence**
   - Update support and user docs to match the final package strategy.
   - Sanitize public evidence packets so no provider-key previews remain.
   - Capture final package validation evidence.

## Validation Strategy

- Focused tests for image selection and package manifest generation.
- PowerShell parser checks for edited launcher/provider scripts.
- Compose config validation for selected package modes.
- Package summary and release-manifest checker.
- Docker CPU validation against CPU package or CPU-selected digest.
- Docker GPU validation against CUDA package or CUDA-selected digest.
- Podman CPU validation with approved provider auto-detect or helper output.
- Podman GPU CDI smoke if launcher/provider behavior changes the validated path.
- Secret/provider-key safety scan over any public evidence packet.

## Non-Goals

- Do not reopen `TASK-083` runtime implementation unless GA packaging changes
  break validated behavior.
- Do not make model, detector, threshold, or TF32 changes.
- Do not bundle third-party binaries until license, checksum, source, and update
  ownership are explicitly approved.
- Do not claim broad air-gapped install support unless offline provider/toolkit
  delivery is designed and validated.

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
