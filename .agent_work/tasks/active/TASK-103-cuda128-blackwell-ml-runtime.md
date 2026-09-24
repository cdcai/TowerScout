# TASK-103: CUDA 12.8 Blackwell ML Runtime

**Status**: IN_PROGRESS - Track L passed and Checkpoint 1 was acknowledged;
Phase 2 implementation/qualification is active; publication waits for
Checkpoint 2
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
- UNTIL Checkpoint 2 is acknowledged, THE PROJECT SHALL NOT dispatch image
  publication, publish a package/release, push `latest`, or close out the task.

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

### Phase 2 - Active

- [x] Rebased the nine pilot commits onto accepted `main` (`10cd13a`) after
  confirming PRs #77-#84 merged.
- [x] Predeclared gates v3 and implemented fail-closed total-footprint and
  interleaved-run comparison rules before Phase 2 measurement.
- [ ] Complete RGB crop conversion, runtime messages, source-build hardening,
  CI/security evidence, documentation, governance, and validation.
- [ ] Qualify a new Podman CPU/GPU machine or record unavailable cells as
  `blocked`, never `pass`.
- [ ] Rehearse source, artifact/volume, and `-Gpu off` recovery paths without
  deleting the eight named volumes.
- [ ] Run rebased final CPU/CUDA qualification with gates v3; preserve every
  run and verdict, including failures.
- [ ] Push `feature/task-103-cuda128-ml-runtime` and open the Task-103 PR with
  links to ADR-022 and the Track L verdict.

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

## Publication Boundary

Checkpoint 2 is the owner authorization boundary for H9 publication and
closeout. Phase 2 authorizes the feature-branch push and PR only.
