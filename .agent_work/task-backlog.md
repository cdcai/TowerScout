# Task Backlog - Main-Based Windows Delivery

**Last Updated**: October 20, 2026 (owner handoff preparation)
**Current Decision**: [ADR-021](./decisions/021-main-based-windows-deployment-deadline.md)
**ML Runtime Amendment**: [ADR-022](./decisions/022-cuda128-blackwell-ml-runtime.md)
**Windows Package Policy**: [ADR-023](./decisions/023-unsigned-windows-package-support-boundary.md)
**RC5 Security Boundary**: [ADR-024](./decisions/024-rc5-security-gate-and-residual-boundary.md)
**Candidate Acceptance**: [ADR-026](./decisions/026-rc5-bounded-candidate-acceptance.md)
**Immediate Plan**: [September 21 v2 implementation plan](./context/status/Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)

The active board controls selected work. This backlog holds deferred,
conditional, and follow-on work. Task-087/096 launcher work is preserved but is
not a delivery prerequisite and has no automatic restart date. Task-087 PRs
#64/#67 are closed without merge; any restart begins from then-current `main`.

## Receiving-owner priorities

Chris accepted ongoing ownership after October 30. The outgoing lead owns
delivery preparation through closeout. The active board remains authoritative;
these groups organize the handoff rather than closing tasks.

| Priority | Owner / timing | Next action and completion condition |
| --- | --- | --- |
| Official delivery | Outgoing lead with Chris; target October 27 | Adopt reviewed source, pass official security/integrity/affected runtime checks, deliver wiki/video and owner packet, and record receipt. |
| Security follow-up (TASK-104) | Outgoing lead prepares; Chris maintains after closeout | Review the five exact residuals before October 31, 2026 23:59:59 UTC expiry; retain a documented fix or disposition before any publication relying on them. Never automatically renew. |
| ML bridge review (TASK-103) | Chris after closeout | Evaluate supported replacement and real-model/device regression evidence by January 31, 2027 or earlier ADR-022 trigger; record the decision. |
| Future improvements below | Chris selects | Prioritize a demonstrated user need, define a small acceptance condition, and open a fresh task before implementation. No automatic restart of deferred work. |

## Selected On The Active Board

| Task | Current outcome |
| --- | --- |
| `TASK-105` | Preserve accepted RC5 evidence; complete official adoption, changed-artifact qualification, and handoff under ADR-026 |
| `TASK-104` | Preserve merged security controls; run fresh official checks and record residual follow-up before expiry |
| `TASK-103` | Preserve accepted CPU/CUDA bridge evidence; qualify affected official runtime and hand off ADR-022 maintenance review |
| `TASK-095` | W00 direction, task-control, evidence, and eventual handoff alignment |
| `TASK-091` | W01/W05/W09/W10 owner-runnable package and model qualification |
| `TASK-097` | Podman CPU/GPU target, provider, CDI, and independent-host qualification |
| `TASK-092` | Frozen/merged content; validate packaged, running-image, Wiki, and exact-artifact documentation surfaces |
| `TASK-093` | Persistence, cancellation/error recovery, reboot, rollback, and repeated-run evidence |

Tasks 068, 099, and 101 are completed and moved to the completed-task record.
Task-101's former PR #67 integration gate is superseded, not passed.
RC9 independent-host findings remain owned by TASK-105 and must not be
duplicated as generic backlog work. Their current dispositions come from
ADR-026 and the RC5 closeout: tested correction, verified no-change decision,
or explicitly accepted limitation. Preserve each disposition; do not silently
drop a finding or reopen it solely from an older status snapshot.


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
| `TASK-089` cdcai Adoption And Ownership Transfer | Ownership, access, direction and name agreed October 20; preparation active. Reviewed source adoption, package permissions, official qualification, publication and receipt remain. |

## Post-Day-7 Planning

Use the [suggested post-Day-7 guide](./context/status/Reprioritization%20Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md)
only after reconciling actual W00-W10 results. Finish unpassed deployment,
data-integrity, and security gates before optional backlog work. Maintain one
canonical active board and preserve task-ID history.
