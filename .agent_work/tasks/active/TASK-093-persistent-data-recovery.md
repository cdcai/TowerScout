# TASK-093: Persistent Data Lifecycle And Recovery Rehearsal

**Status**: IN_PROGRESS - final `rc4` first-host stop/relaunch, controlled
failure, cancellation recovery, and export persistence pass on all four
profiles, including exact-candidate reboot; independent-host recovery remains
**Priority**: HIGH
**Type**: C (Reliability / Recovery)

## Objective

Prove that setup, assets, sessions, review/export inputs, and other intended
state survive normal stop/relaunch, reboot, controlled failure, and rollback.

## Requirements

- WHEN TowerScout stops or its container is replaced, THE SYSTEM SHALL preserve
  all eight named volumes unless a separately confirmed destructive action is
  explicitly requested.
- WHEN detection is cancelled or fails, THE SYSTEM SHALL support a successful
  next request without publishing partial results or deleting successful
  export inputs.
- WHEN rollback/recovery is rehearsed, THE PROJECT SHALL use an isolated target
  and verify restored state before resuming use.

## Acceptance Boundary

Final evidence belongs to the exact W09 candidate. No `down -v`, volume prune,
or broad cleanup is part of this task.

## Implementation Log

### 2026-09-30 - Final `rc4` First-Host Recovery Matrix

**Execution**: Exercised Docker CPU/CUDA and Podman CPU/CUDA final packages on
ports 5231-5234 from source
`541622556fb7999ee4e88fb1e44f7797b9da34f5`. Each profile completed a
volume-preserving stop and fresh-process relaunch. Provider credentials were
entered by the workstation owner and were not copied into evidence.

**Validation**: PASS for the local lifecycle boundary. Every profile restored
`ready` state, its exact image digest, all eight named mounts, configured
Google and Azure providers, repaired provider TLS trust, the required CPU or
CUDA device, and a successful post-relaunch Google detection. Controlled
empty-estimate validation returned HTTP 400 and the next real detection in the
same browser returned HTTP 200. Cancellation returned HTTP 202 while the
shared slot was occupied; the frontend kept retry blocked until progress
reported `retryReady`, after which the immediate next detection passed with no
page errors. Nonempty exports and valid dataset ZIPs confirmed that successful
review inputs remained usable. No destructive volume operation was used.

### 2026-09-30 - Exact-`rc4` Reboot Restoration

**Validation**: PASS on the first host. Docker CPU/CUDA auto-restored after the
verified reboot boundary. The retained Podman machine was running and its two
existing package containers required the documented manual start; neither was
recreated. All four profiles retained exactly eight mounts, provider settings,
repaired TLS trust, exact image identity, and the required device. Post-reboot
Google and Azure detection, controlled-error recovery, review navigation, and
valid dataset ZIP export passed in every profile. Both CUDA profiles completed
a finite `sm_120` kernel on `cuda:0`. No destructive volume operation was
used.

**Remaining**: Independent-host recovery remains required. Rollback rehearsal
remains isolated from the active qualified profiles.
