# Sprint 08 Retrospective Analysis

**Sprint**: July 23-August 7, 2026
**Status**: COMPLETE

## Goal

Classify and remediate the dependency-security baseline, clear the release
gate for Task-087, and advance the controlled Windows launcher proof without
changing the immutable pilot or cdcai.

## Completed Within Sprint 08

- Completed Task-090's 62-alert runtime and dependency-security investigation.
- Completed Task-098's approved dependency remediation and affected-runtime
  qualification through PR #51.
- Restored the July 27 inventory to eight documented non-blocking torch
  advisories without dismissing alerts.
- Resumed Task-087 and implemented the visible Windows launcher, exact-source
  package controls, and bounded native TLS-repair transaction on Draft PR #67.
- Kept `v0.1.2` immutable and left `cdcai/TowerScout` unchanged.

## Cross-Sprint Completion

Task-099 began in response to advisories disclosed on August 4-5, but its final
root dependency-graph refresh and alert reconciliation completed on August 11.
That completion is recorded in Sprint 09 rather than retroactively extending
Sprint 08.

## Carried Forward

- Task-087: reconcile Draft PR #67 with current `main`, rebuild the exact-source
  full-runnable package, complete provider/recovery and managed-endpoint gates,
  and record the August 14 decision.
- Task-089: remain owner-gated until final qualification and adoption approval.
- Task-095: continue governance and handoff maintenance through October 30.
- Task-096 and Task-097: remain the next required implementation sequence after
  Task-087 passes its decision gate.

## What Changed

The security work required two separately governed remediation lanes. Task-098
closed the original July baseline; Task-099 handled later disclosures and a
stale default-branch dependency graph without reopening the completed Task-098
evidence. Task-087 also pivoted from the dormant browser/helper design to a
visible package-local launcher with explicit confirmation and transactional
repair behavior.

## Lessons

- Completion dates must remain inside the declared sprint; cross-sprint work
  belongs to the succeeding sprint unless an extension is explicitly approved.
- Dependency source fixes and GitHub dependency-graph reconciliation are
  separate gates and both need evidence.
- Exact-source package provenance must precede signing or runtime acceptance.
- Managed endpoint policy can block a local build path without justifying an
  execution-policy bypass or an older-source package.
- Runtime mutation must remain fail-closed when the selected engine or Compose
  provider does not satisfy the approved boundary.

## Sprint 09 Recommendation

Finish the Task-087 decision sequence first. If it proceeds, select Task-096
and then Task-097 before owner qualification, documentation freeze, and
recovery rehearsal work.
