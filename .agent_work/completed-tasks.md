# Completed Tasks

**Last Updated**: August 11, 2026
**Current Retention Window**: Sprint 06 through current Sprint 09 completions
**Historical Snapshot**:
[`2026-07-23-pre-rebaseline-completed-tasks.md`](./context/archive/2026-07/2026-07-23-pre-rebaseline-completed-tasks.md)

This file is the concise completion source for recent work. Older detailed task
files remain under `tasks/completed/`, and older summaries are preserved under
`context/archive/`.

---

## Sprint 09 Completed Tasks (August 8-August 21, 2026)

### TASK-099: August Dependency Advisory Follow-Up

**Status**: COMPLETED
**Completed**: August 11, 2026
**Task File**:
[`TASK-099-august-dependency-advisory-follow-up.md`](./tasks/active/TASK-099-august-dependency-advisory-follow-up.md)

Key outcomes:

- Merged the narrow `aiohttp`, transitive `ip-address`, and transitive
  `js-yaml` remediation through PR #68 as `f460445`.
- Merged the comment-only root-manifest refresh through PR #69 as `0133b50`,
  allowing GitHub's native root graph submission to replace its stale
  `aiohttp==3.14.2` snapshot.
- Passed post-merge main CI, Task-087 compatibility, and dependency-graph run
  `31510493332`.
- Closed alert `#74` without dismissal and restored the inventory to the eight
  documented non-blocking torch advisories--three medium and five low.
- Cleared the Task-099 signing/candidate dependency gate without changing the
  qualified ML pair, application behavior, frozen pilot, or cdcai.

The Task-099 file remains under `tasks/active/` until Sprint 09 closeout.

---

## Sprint 08 Completed Tasks (July 23-August 7, 2026)

**Sprint Outcome**: Classified and remediated the original dependency-security
baseline, cleared that release gate for Task-087, and advanced the controlled
launcher proof without changing the frozen pilot or cdcai. Task-099 completed
after the sprint boundary and is recorded under Sprint 09.

### TASK-090: Runtime, Custom-Image, And Dependency Security Investigation

**Status**: COMPLETED
**Completed**: July 23, 2026
**Task File**:
[`TASK-090-runtime-custom-image-dependency-security.md`](./tasks/completed/TASK-090-runtime-custom-image-dependency-security.md)

Key outcomes:

- Reconciled and classified the 62-alert Trivy baseline by package,
  reachability, supported-runtime impact, and remediation direction.
- Identified five release-blocking alerts, one required-hardening alert, and
  the loopback-publication control.
- Produced and obtained approval for the separately governed Task-098 scope.

### TASK-098: Dependency Security Remediation And Release Gate

**Status**: COMPLETED
**Completed**: July 27, 2026
**Task File**:
[`TASK-098-dependency-security-remediation.md`](./tasks/completed/TASK-098-dependency-security-remediation.md)

Key outcomes:

- Merged the qualified dependency, local-input, model-trust, and CI-ratchet
  changes through PR #51 as `e499b50`.
- Passed Docker CPU/GPU compatibility, live Google/Azure workflows, model
  output/performance comparison, PR review remediation, and post-merge CI.
- At the July 27 closeout, reconciled Dependabot to eight open torch
  advisories—three medium and five low—with no open release-blocking
  critical/high alert and no manual dismissal at that checkpoint.
- Closed incompatible standalone torch PR #60; future torch upgrades must move
  with torchvision and repeat the coordinated ML qualification cycle.
- Cleared the security dependency for Task-087 to resume.

Post-closeout note: GitHub disclosed alerts `#72-#75` on August 4-5. They do
not reopen Task-098 or change its July evidence; the separately governed
[`TASK-099` follow-up](./tasks/active/TASK-099-august-dependency-advisory-follow-up.md)
owned their remediation together with npm audit finding
`GHSA-5p4m-2wfm-xmqj`, detected while Task-099 remained active. During its
execution Task-099 blocked signing and candidate inclusion, not ongoing
Task-087 non-release work.

Retrospective:
[`SPRINT-08-RETROSPECTIVE-ANALYSIS-2026-08-11.md`](./context/analysis/SPRINT-08-RETROSPECTIVE-ANALYSIS-2026-08-11.md)

---

## Sprint 07 Completed Tasks (July 2-July 23, 2026)

**Sprint Outcome**: Published and distributed the immutable fork-side
`v0.1.2` pilot, confirmed support and feedback custody, preserved the
feedback-gated cdcai boundary, and completed the planning work needed to begin
the October fix-first roadmap.

### TASK-088: Stable Release And Handoff Closeout

**Status**: COMPLETED
**Completed**: July 22, 2026
**Task File**:
[`TASK-088-stable-release-and-handoff-closeout.md`](./tasks/completed/TASK-088-stable-release-and-handoff-closeout.md)

Key outcomes:

- Published and froze the six validated `v0.1.2` pilot assets.
- Sent the pilot communication on July 13, 2026.
- Confirmed the external Word feedback process and primary/backup support
  coverage.
- Preserved release, checksum, validation, troubleshooting, and custody
  records.
- Kept `cdcai/TowerScout` unchanged pending owner approval of a future
  adoption baseline.

### Sprint 07 Carry-Forward

- `TASK-087` completed its merged non-mutating proof and is reselected for the
  fix-first candidate after `TASK-090`.
- `TASK-089` remains owner-gated; preparation may continue, but cdcai must not
  be changed before final owner qualification and adoption approval.
- `TASK-095` begins in Sprint 08 with the Phase A roadmap/workspace rebaseline.

Retrospective:
[`SPRINT-07-RETROSPECTIVE-ANALYSIS-2026-07-23.md`](./context/analysis/SPRINT-07-RETROSPECTIVE-ANALYSIS-2026-07-23.md)

---

## Sprint 06 Completed Tasks (May 11-July 2, 2026)

**Sprint Outcome**: Produced the Windows release-package baseline and validated
the `v0.1.2` predecessor release-candidate path across Docker, Podman, CPU,
CUDA, asset import, documentation, compliance, restore hardening, and
managed-network command-based provider TLS repair.

Completed task files:

- `TASK-065`, `TASK-066`, `TASK-067`, and `TASK-069`
- `TASK-071` through `TASK-075`
- `TASK-079` through `TASK-086`

Detailed task files remain in
[`tasks/completed/`](./tasks/completed/). The Sprint 06 retrospective is
[`SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md`](./context/analysis/SPRINT-06-RETROSPECTIVE-ANALYSIS-2026-07-02.md).

---

## Archive Notes

- The full pre-rebaseline completion record, including Sprint 01 through
  Sprint 06 detail, is preserved in the July 23 historical snapshot linked
  above.
- Individual artifacts older than three months remain under
  `context/archive/2026-05/tasks-older-than-3-months/`.
- Do not recreate completed tasks in the backlog. Create a new task number for
  any newly authorized follow-up.
