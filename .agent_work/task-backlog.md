# Task Backlog - Main-Based Windows Delivery

**Last Updated**: October 7, 2026
**Current Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**ML Runtime Amendment**: [ADR-022](./decisions/022-cuda128-blackwell-ml-runtime.md)
**Windows Package Policy**: [ADR-023](./decisions/023-unsigned-windows-package-support-boundary.md)
**RC5 Security Boundary**: [ADR-024](./decisions/024-rc5-security-gate-and-residual-boundary.md)
**Immediate Plan**: [September 21 v2 implementation plan](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)

The active board controls selected work. This backlog holds deferred,
conditional, and follow-on work. Task-087/096 launcher work is preserved but is
not a delivery prerequisite and has no automatic restart date. Task-087 PRs
#64/#67 are closed without merge; any restart begins from then-current `main`.

## Selected On The Active Board

| Task | Current outcome |
| --- | --- |
| `TASK-104` | Remove unused Debian GDAL, enforce the exact four-key expiring residual policy, and make local security qualification precede registry publication |
| `TASK-103` | CUDA 12.8 Blackwell bridge; rebuild documentation-aligned artifacts and complete final browser-download/independent-host qualification |
| `TASK-095` | W00 direction, task-control, evidence, and eventual handoff alignment |
| `TASK-091` | W01/W05/W09/W10 owner-runnable package and model qualification |
| `TASK-097` | Podman CPU/GPU target, provider, CDI, and independent-host qualification |
| `TASK-092` | Frozen/merged content; validate packaged, running-image, Wiki, and exact-artifact documentation surfaces |
| `TASK-093` | Persistence, cancellation/error recovery, reboot, rollback, and repeated-run evidence |

Tasks 068, 099, and 101 are completed and moved to the completed-task record.
Task-101's former PR #67 integration gate is superseded, not passed.

## Guidance Completed Through Task-092

`TASK-076` provider-key exposure and restriction guidance is incorporated in
the frozen documentation merged through PR #94. The manuals explain credential
ownership, browser visibility, API scoping, quotas/monitoring/rotation, and the
current Google one-key application-restriction limitation. No separate code
task is selected unless final package testing reveals a new ambiguity.

## Required Or Evidence-Selected Follow-On Work

| Priority | Task | Status | Entry criterion / required outcome |
| ---: | --- | --- | --- |
| 1 | `TASK-077` Public Release Manifest And Asset Import Hardening | EVIDENCE_SELECTED | Select only for a demonstrated manifest/import/integrity gap in W01/W09 |
| 2 | `TASK-027` Enhanced Error Handling | CONDITIONAL | Select only a reproduced user-facing release blocker not owned by W02-W08 |
| 3 | `TASK-070` Restricted-Network Package Enhancements | CONDITIONAL | Select only if the claimed deployment environment requires offline/restricted distribution |
| 4 | `TASK-094` Evidence-Gated Support Snapshot | EVIDENCE_GATED | Add only if current sanitized status/log procedures cannot resolve real support cases |
| 5 | `TASK-026` CPU Optimization | CONDITIONAL | Select only for a measured supported-host bottleneck; preserve outputs and memory limits |

## Explicitly Deferred Beyond The Delivery Window

| Task | Disposition |
| --- | --- |
| `TASK-087` / PRs #64/#67 | Archived and closed without merge. Preserve the tagged history and [final disposition](./context/archive/2026-09/TASK-087-PR64-PR67-FINAL-DISPOSITION-2026-09-24.md); any future reconsideration requires an owner-selected task and a fresh branch from current `main`. |
| `TASK-096` User-Initiated Exit And Container Stop | Preserve for a future owner decision. Use the tested command-based lifecycle now. |
| `TASK-058` Background Detection Jobs | Future architecture; current work permits only minimal whole-job admission and reproduced recovery fixes. |
| `TASK-059` Backend Layer Decomposition | Future architecture; not a one-week release gate. |
| `TASK-060` Frontend Build Modernization | Maintenance after release unless the current build itself blocks acceptance. |
| `TASK-061` Coordinated NumPy 2 Migration | Future dependency track; no dependency/model migration this week. |
| `TASK-078` Permissive Apache-Only Runtime Migration | Future release track. |
| `TASK-029` Multi-Provider Fallback | Future product work after provider policy/error behavior is stable. |
| `TASK-028` Mobile Responsiveness | Parking lot. |

Also deferred: a new launcher, browser Exit helper, generic native-process
framework, new runtime-discovery or recovery-journal architecture, new in-image
self-test product surfaces, provider repackaging, speculative throughput work,
and bulk historical cleanup.

## Owner-Gated Work

| Task | Boundary |
| --- | --- |
| `TASK-089` cdcai Adoption And Ownership Transfer | Local reversible preparation may continue. Publication, repository mutation, and final adoption require owner qualification and explicit authorization. |

## Post-Day-7 Planning

Use the [suggested post-Day-7 guide](./context/status/Reprioritization%20Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md)
only after reconciling actual W00-W10 results. Finish unpassed deployment,
data-integrity, and security gates before optional backlog work. Maintain one
canonical active board and preserve task-ID history.
