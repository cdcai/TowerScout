# TASK-103: CUDA 12.8 Blackwell ML Runtime

**Status**: IN_PROGRESS - PR #92 merged as `cbb574f` and PR #93 merged as
`fba9dcb`. Immutable `rc3` CPU/CUDA images and control ZIPs retain their G10,
W05, first-host lifecycle, provider, and reboot evidence, but predate both
fixes and are not the final candidate. New immutable images/packages and
affected W09/W10 requalification are required; remaining profile workflows,
controlled-error, review/export, policy/signing, and independent-host evidence
remain
**Priority**: CRITICAL
**Type**: C (ML Runtime Migration / Release Qualification)
**Owner**: Release owner; active agent executes the authorized implementation
and qualification brief
**Decision**: [ADR-022](../../decisions/022-cuda128-blackwell-ml-runtime.md)
**Implementation Brief**:
[TASK103-IMPLEMENTATION-BRIEF-V3-2026-09-24.md](./TASK-103/TASK103-IMPLEMENTATION-BRIEF-V3-2026-09-24.md)

## Objective

Replace the accepted torch 2.6.0/cu126 runtime with the qualified
torch 2.10.0/torchvision 0.25.0 pair and distinct `cpu`/`cuda128` artifacts,
then qualify the rebased Windows Docker/Podman CPU/NVIDIA release without
weakening model correctness, device, security, persistence, or recovery gates.

## Requirements

- WHEN a GPU profile is qualified, THE PROJECT SHALL prove both YOLO and
  EfficientNet execute on CUDA; CPU fallback is not a GPU pass.
- WHEN relative G8/G9 results are reported under gates v3, THE PROJECT SHALL
  use same-host interleaved runs, at least three run directories per side, and
  no overlapping scans or builds.
- WHEN a CUDA build cannot serve the detected GPU, THE APPLICATION SHALL emit
  the matching newer-GPU, older-GPU, CPU-only, driver/container, or precision
  recovery message without implying a fallback occurred when none did.
- WHEN publishing images, THE WORKFLOW SHALL scan and generate an SBOM for the
  exact published digest and preserve written finding dispositions.
- BEFORE publication, THE PROJECT SHALL inventory the shipped NVIDIA runtime
  components for compliance review without making a legal determination.
- AFTER Checkpoint 2, THE PROJECT SHALL land the required pre-publication
  corrections before dispatching images; package/release publication and
  `latest` remain gated on owner confirmation of the exact digests.

## Execution Record

### Phase 0 / Phase 1 - Completed 2026-09-24

- Package hashes and reconstructed pilot tree verified.
- Track L CUDA verdict: PASS on `sm_120`; both models observed on `cuda:0`;
  torch `2.10.0+cu128`; torchvision `0.25.0+cu128`; CUDA build `12.8`;
  minimum free VRAM 2.89 GiB.
- Explicit CPU profile of the `cuda128` image: PASS after correcting the
  qualification identity contract.
- Negative controls N2/N3: PASS. The old cu126 runtime failed the decisive
  Blackwell kernel path as expected; the cuda128 runtime passed.
- Checkpoint 1 acknowledged by the owner with Track L PASS confirmed.

### Phase 2 - Completed 2026-09-28

- [x] Rebased the nine pilot commits onto accepted `main` (`10cd13a`) after
  confirming PRs #77-#84 merged.
- [x] Predeclared gates v3 and implemented fail-closed total-footprint and
  interleaved-run comparison rules before Phase 2 measurement.
- [x] Complete RGB crop conversion, runtime messages, source-build hardening,
  CI/security evidence, documentation, governance, and validation.
- [x] Qualify a new Podman CPU/GPU machine or record unavailable cells as
  `blocked`, never `pass`.
- [x] Rehearse source, artifact/volume, and `-Gpu off` recovery paths without
  deleting the eight named volumes.
- [x] Run rebased final CPU/CUDA qualification with gates v3; preserve every
  run and verdict, including failures.
- [x] Push `feature/task-103-cuda128-ml-runtime` and open
  [Task-103 PR #86](https://github.com/J-Schulein/TowerScout/pull/86) with links to
  ADR-022 and the Track L verdict.
- [x] Land the accepted-baseline Trivy delta gate, fail-closed comparator
  context validation, corrected/sanitized evidence, and alert #215 disposition
  with green CI before H9 dispatch.
- [x] Dispatch CPU and CUDA 12.8 images with `push_latest=false`, then report
  exact digests and scan/SBOM artifacts before any package publication.

### W09 Package Assembly And First-Host Qualification - Completed 2026-09-28

- [x] Merge package-only Podman spaced-path correction in
  [PR #87](https://github.com/J-Schulein/TowerScout/pull/87) with green CI.
- [x] Build final CPU and CUDA 12.8 control ZIPs from accepted package source
  `99de5595b0d98b67c24909c1f2712f72d8714ab3` and bind them to the
  owner-confirmed image digests and shared asset ZIP.
- [x] Verify outer sidecars, all internal checksums, manifest identities,
  compliance inventory, forbidden-file inventory, and package secret hygiene.
- [x] Run exact-package setup on Docker CPU, Docker CUDA, rootless Podman CPU,
  and rootless Podman CUDA; preserve all eight named volumes for each package.
- [x] Reconfirm real-model and memory gates against the exact image digests and
  run an exact-package CUDA `sm_120` kernel probe.
- [ ] Complete the remaining per-profile provider/recovery/review-export,
  controlled-error, policy/signing, and independent-host W10 acceptance cells
  before claiming release readiness.

### W10 Local First-Host Rehearsal - Started 2026-09-28

- [x] Run an exact-package fresh Docker CPU install from a spaced path with new
  volumes, the frozen CPU ZIP/digest, and the frozen asset ZIP.
- [x] Configure live Azure and Google providers without reading or recording
  credentials; pass normal positive detection on both providers.
- [x] Reproduce `tls_ca_untrusted`, run the packaged dry-run/apply repair with
  certificate identities suppressed, and verify repaired Google TLS.
- [x] Preserve provider config, repaired CA trust, assets, port, and image
  identity across a volume-preserving stop and fresh-shell relaunch.
- [x] Implement and locally validate the bounded TLS helper non-default-port
  preservation fix; replacement-package managed-network repetition remains.
- [x] Implement and locally validate cancel readiness against the shared
  detection slot; the real Google cancel-then-next overlay now passes.
- [x] Merge the lifecycle fixes through
  [PR #89](https://github.com/J-Schulein/TowerScout/pull/89) as `95a3ccc` with
  green exact-head CI.
- [x] Preserve the failed `v0.1.3-rc2` CPU/CUDA dispatches and security
  artifacts after G10 blocked two newly disclosed HIGH `linux-libc-dev`
  findings; neither digest is a replacement candidate.
- [x] Land the bounded removal of the unnecessary runtime development package
  through [PR #90](https://github.com/J-Schulein/TowerScout/pull/90), then
  publish new immutable `rc3` tags with `push_latest=false`; both G10 deltas
  passed with zero new findings.
- [x] Assemble replacement CPU/CUDA control ZIPs from `7a5eedd` and repeat
  exact-package setup plus stop/relaunch across Docker/Podman CPU/CUDA without
  deleting any of the eight named volumes per profile.
- [x] Repeat the managed-TLS cell on the fresh `rc3` Docker CPU package,
  including the non-default-port repair lifecycle and persistent trusted bundle.
- [x] Repeat Google normal, Google cancel-then-next, and Azure normal live-
  provider cells on the fresh `rc3` Docker CPU package without retaining
  credentials, request payloads, provider URLs, or screenshots.
- [x] Reboot the first host and verify exact digests, loopback ports, all eight
  named volumes per profile, health/readiness, persistent Docker CPU provider
  configuration and repaired CA trust, post-reboot Google/Azure requests, and
  real Docker/Podman CUDA `sm_120` kernels. Docker restored automatically;
  Podman required a documented manual start of the retained containers.
- [x] Merge the Podman TLS repair lifecycle fix through
  [PR #92](https://github.com/J-Schulein/TowerScout/pull/92) as `cbb574f` and
  the cancellation retry-readiness fix through
  [PR #93](https://github.com/J-Schulein/TowerScout/pull/93) as `fba9dcb`.
- [ ] Dispatch new immutable CPU/CUDA images from accepted `main`, assemble
  replacement control ZIPs, and repeat every affected W09/W10 cell before
  selecting a final candidate.
- [ ] Complete Docker CUDA, Podman CPU, and Podman CUDA provider/recovery/
  review-export workflows; controlled-error checks remain required in every
  profile, and Docker CPU review/export is also not run.
- [ ] Complete policy/signing and independent-host cells.

## Acceptance Boundary

Unit/static checks and health/readiness are necessary but do not establish
release readiness. Final claims require exact image/package identity, real
models on the required device, providers, persistence/recovery, and the
independent-host evidence required by Task-091. Missing external prerequisites
remain explicit blockers.

## Evidence

- [Track L evidence index](./TASK-103/TRACK-L-EVIDENCE-INDEX.md)
- [T1000 pilot evidence pointer](./TASK-103/T1000-EVIDENCE-POINTER.md)
- [Gates v3](./TASK-103/task103_gates.v3.json)
- [Phase 2 evidence index](./TASK-103/PHASE2-EVIDENCE-INDEX.md)
- [W09 candidate evidence index](./TASK-103/W09-EVIDENCE-INDEX.md)
- [W10 local first-host evidence index](./TASK-103/W10-LOCAL-FIRST-HOST-EVIDENCE-INDEX.md)

## Publication Boundary

Checkpoint 2 and the replacement H9 dispatch are authorized and recorded. W09
replacement assembly and local qualification are authorized. Package
publication, `latest` promotion, and closeout remain explicitly owner-gated.
