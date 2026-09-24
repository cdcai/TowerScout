# ADR-022: CUDA 12.8 Blackwell ML Runtime Bridge

**Status**: Accepted
**Date**: September 24, 2026
**Task**: `TASK-103: CUDA 12.8 Blackwell ML Runtime`
**Scope**: PyTorch/torchvision pair, CUDA image identity, supported GPU boundary,
qualification method, recovery behavior, and bridge ownership

## Decision

1. Adopt `torch==2.10.0` with `torchvision==0.25.0` for the next candidate.
   Keep distinct `cpu` and `cuda128` image/package flavors; `cuda128` uses the
   PyTorch `cu128` wheel index.
2. Treat the CUDA package as a Volta-or-newer expectation, while qualifying
   only combinations actually tested. Maxwell and Pascal are unsupported by
   this CUDA package and must use the CPU package or `-Gpu off`.
3. Amend G8 before Phase 2 measurement: GPU profiles compare the median of
   each run's peak host `VmHWM` plus `torch.cuda.max_memory_reserved` against
   the same-host reference total at the unchanged `1.10` limit. CPU profiles
   remain host-only. G8 and G9 require interleaved same-window runs with at
   least three run directories per side and no concurrent scans or builds.
4. Include the owner-approved CUDA synchronization before vendored YOLOv5 NMS
   timing (D-P2) and the lossless RGB expansion of the historical fixture
   (D-P3). These preserve inference semantics while correcting measurement and
   production-input mismatches found by the pilot.
5. Require PR #78 / W06 secondary-classifier failure propagation as a release
   dependency (D10). It merged as `f51d401`; a secondary failure must not
   publish partial results.
6. Use the merged Task-091/PR #83 combined-flow contract as the single
   acceptance contract. The historical out-of-repository
   `v012-validation\harness\` detection harness is formally retired for ML
   acceptance because it lacks the current offline, hash, device, secondary,
   and enforced-comparison contract.

## Context

The accepted torch 2.6.0/cu126 image cannot execute on this laptop's Blackwell
`sm_120` GPU. The Task-103 pilot on the owner's T1000 and Track L on this
Blackwell laptop demonstrated native `sm_75` and `sm_120` coverage with the
selected pair. The pilot also showed that GPU host RSS alone increased while
the combined host-plus-reserved-device footprint decreased, so the old
host-only G8 judgment was misleading for GPU profiles.

## Bridge Exit Plan

This is a time-limited compatibility bridge, not a permanent dependency
freeze. Review it on **2027-01-31** or at the first evaluation of torch
`>=2.14.1`, whichever occurs first. Exit or requalify earlier when any of these
triggers occurs:

1. a HIGH or CRITICAL advisory affects the shipped pair and is not evidenced
   unreachable;
2. the review date passes;
3. another dependency requires a newer torch;
4. the supported fleet drops its pre-Turing need and `cu130` becomes viable;
5. the `cu128` line loses security support.

The TowerScout project closes on **2026-10-31**. At handover, this review and
exit obligation transfers to whoever assumes TowerScout maintenance ownership.

## Consequences

- Image/package names, build arguments, launcher guidance, tests, and release
  evidence must distinguish `cpu` from `cuda128`.
- GPU support claims name exact qualified GPU/driver/Windows/WSL/engine/toolkit
  combinations. Architectural coverage alone is not a qualification claim.
- CUDA fallback remains observable. A CPU fallback never passes a required-GPU
  cell.
- Publication remains owner-gated at Task-103 Checkpoint 2.

## Validation And Review

Track L passed the predeclared v2 correctness gates on an NVIDIA RTX PRO 500
Blackwell Laptop GPU (`sm_120`): both models ran on CUDA, the decisive kernel
probe passed, outputs stayed within tolerance, and minimum free VRAM was 2.89
GiB. The explicit CPU profile of the same CUDA image also passed after the
qualification harness separated device profile from image flavor. Gates v3
were committed before any Phase 2 comparison measurements.
