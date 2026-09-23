# ADR-021: Main-Based Windows Deployment Delivery Window

**Status**: Accepted
**Date**: September 22, 2026

## Decision

TowerScout's immediate delivery work starts from accepted `main` at
`9276084d91807906c53e00060670692b27e38483` and follows the September 21 v2
prioritization and implementation plan. The delivery target is a downloadable
Windows 11 application proven on Docker and Podman, CPU and NVIDIA GPU, with
successful independent-computer reproduction.

PR #67 and the Task-087 launcher redesign are deferred outside this delivery
window. They are not prerequisites for packaging or qualification. Preserve
their branches, commits, review records, and unique evidence; do not merge,
reconcile, extend, or repeatedly review them as part of this effort. Closing
PR #67 unmerged is recommended but remains a separately authorized external
action.

## Consequences

- The existing PowerShell/Compose package path remains the delivery path.
- W00-W10 in the v2 plan control the bounded implementation sequence.
- `v0.1.2` remains immutable; new artifacts require new identities.
- CPU and CUDA 12.6 use distinct image/package identities pinned by digest.
- Missing hardware, assets, provider access, policy approval, or observed test
  failures remain blockers; the one-week target does not convert them to passes.
- Task-101's security remediation remains completed. Its former PR #67
  integration gate is superseded, not passed.
- Task-087/096 launcher and browser-exit work remains preserved and deferred.

## Sources

- `../context/status/Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md`
- `../context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md`
- `../context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2-verification.md`
