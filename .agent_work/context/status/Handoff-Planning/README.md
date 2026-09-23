# Handoff Planning - Current Navigation

## Read First

1. [`../Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md`](../Reprioritization%20Effort/2026-09-21-windows-deployment-prioritization-v2.md)
   - current delivery objectives and acceptance requirements
2. [`../Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md`](../Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)
   - current implementation sequence
3. [`../Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2-verification.md`](../Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2-verification.md)
   - static review scope and limits; not runtime evidence
4. [`../Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md`](../Reprioritization%20Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md)
   - suggested follow-on work after actual Day-7 results are reconciled
5. [`2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`](./2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)
   - dated historical roadmap; its PR #67 sequencing is superseded
6. [`PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`](./PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md)
   - current rules for the unchanged `v0.1.2` pilot and cdcai feedback hold
7. [`PILOT-OPERATIONS-PACKET.md`](./PILOT-OPERATIONS-PACKET.md)
   - completed July 13 pilot distribution, support, and custody record
8. [`GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md`](../../analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md)
   - 62-alert dependency inventory, applicability, and Tasks 090/098 gate
9. [`.agent_work/current-tasks.md`](../../../current-tasks.md)
10. [`HANDOFF.md`](../../../../HANDOFF.md)

## Current Decision

- Keep the six `v0.1.2` pilot assets immutable.
- Develop owner-requested fixes in the fork under `v0.1.3-rc.N`.
- Do not publish `v0.1.3` final prematurely.
- Keep `cdcai/TowerScout` unchanged until the owner-qualified final candidate
  receives explicit adoption approval.
- Qualify Docker CPU, Docker GPU, Podman CPU, and Podman GPU.
- Task-090 alert classification and Task-098 mandatory remediation remain
  complete as of their July 27 closeout.
- Task-099 completed alerts `#72-#75` plus npm finding
  `GHSA-5p4m-2wfm-xmqj` through PRs #68/#69. Alert `#74` closed without
  dismissal, and its August 11 closeout contained the eight documented torch
  residuals.
- High-severity development-transitive `extract-zip` alert `#76` opened after
  that closeout. Task-101's focused Node/Puppeteer remediation passed final PR
  and exact-main validation, PR #72 squash-merged as `0cc189c`, and the alert
  closed as fixed without dismissal.
- PR #67 and Task-087 launcher work are preserved and deferred outside the
  immediate delivery window. They are not release gates and receive no new
  reconciliation, implementation, or review work as a deployment prerequisite.
- Complete operational closeout by October 30, 2026.

## Active Validation Record

The frozen Pilot Package remains active while feedback is collected. Its
sanitized validation record remains under:

- [`v0.1.2-Validation-Evidence/`](./v0.1.2-Validation-Evidence/)

This evidence proves the Pilot Package; it does not certify a future candidate.

## Archived Planning And Release History

Superseded strategies, July 22 roadmap iterations, external reviews, and
v0.1.0-v0.1.2 publication checklists moved to:

- [`context/archive/2026-07/Handoff-Planning/`](../../archive/2026-07/Handoff-Planning/)

They are historical evidence only. Their dates, commands, and adoption
recommendations do not authorize current execution.
