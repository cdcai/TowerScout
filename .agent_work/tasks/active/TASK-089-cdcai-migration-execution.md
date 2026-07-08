# TASK-089: cdcai Migration Execution And Ownership Transfer

**Status**: BLOCKED
**Priority**: HIGH
**Type**: C
**Estimated Effort**: 1-2 days once prerequisites are satisfied
**Target Sprint**: Sprint 07
**Created**: 2026-07-08
**Owner**: TowerScout release owner / active agent support with cdcai maintainer participation
**Depends On**: `TASK-088` stable fork release completion; cdcai write access; cdcai GHCR publish ownership; cdcai Issues enablement or an approved alternate backlog destination

## Objective

Execute the actual migration of the validated stable release line from the
fork back to `cdcai/TowerScout`, including selected git history, tags, image
ownership, release assets, backlog transfer, and post-transfer verification.

## Canonical Planning Sources

- `.agent_work/context/status/Handoff-Planning/TowerScout-Implementation-Strategy.md`
- `.agent_work/context/status/Handoff-Planning/TowerScout-Handoff-Review-Comprehensive-Analysis.md`

`TASK-089` should not reinterpret the reviewed migration runbook. Its purpose is
to track the owner-gated execution, record the final repo/registry choices, and
capture anything that diverges from the dry-run-validated plan.

## Requirements (EARS Notation)

- WHEN migration execution begins, THE SYSTEM SHALL preserve git-source
  provenance, release-tag traceability, and digest-pinned package correctness.
- WHEN selected history and tags are pushed to `cdcai/TowerScout`, THE SYSTEM
  SHALL avoid force-push, squash-merge, and bulk `--tags` behavior.
- WHEN runtime images are republished or copied to `ghcr.io/cdcai`, THE SYSTEM
  SHALL either preserve the validated digest or re-anchor validation against the
  new digest and rebuilt packages.
- WHEN backlog transfer is attempted, THE SYSTEM SHALL use cdcai Issues only if
  they are enabled, otherwise it SHALL use an explicitly approved alternate
  durable destination.
- WHEN cdcai release recreation completes, THE SYSTEM SHALL verify the rebuilt
  artifacts, public pulls, source traceability, and a clean package smoke path.

## Acceptance Criteria

- [ ] cdcai collaborator write and package-publish ownership are confirmed.
- [ ] The selected stable history and tags are pushed without force or bulk-tag
      mistakes.
- [ ] `ghcr.io/cdcai/towerscout` publishes the intended stable images and the
      visibility/linkage requirements are satisfied.
- [ ] The cdcai-side stable release is recreated from validated artifacts.
- [ ] Post-transfer verification confirms clone, pull, package, and source-ref
      integrity.
- [ ] Backlog transfer lands in cdcai Issues or an explicitly approved
      alternate durable destination.

## Dependencies

- `TASK-088` must establish the stable fork baseline first.
- cdcai maintainer decisions are required for collaborator write, GHCR package
  ownership, release publication, and issue-tracker destination.
- Registry copy versus rebuild must be decided based on the available tooling
  and permissions at execution time.

## Implementation Plan

1. Confirm owner-side prerequisites and keep them recorded in one place.
2. Push the selected history/tag set to cdcai using the reviewed non-destructive
   sequence.
3. Copy or rebuild images under cdcai ownership and rebuild packages as needed.
4. Recreate the stable cdcai release and verify it from a fresh consumer path.
5. Transfer backlog/handoff context and close out the fork-side transition
   notes.

---

## Implementation Log

### 2026-07-08 - Task Creation In Blocked State
**Objective**: Create a formal migration execution task without pretending the
owner-side prerequisites are already satisfied.
**Context**: The reviewed handoff plan separates fork-side stable release work
from cdcai-side migration execution, and the analysis confirms that access,
Issues, and GHCR ownership remain external blockers.
**Decision**: Create `TASK-089` as a blocked Sprint 07 task so the migration
work has a durable owner and acceptance criteria, but do not mark it active for
execution until prerequisites are confirmed.
**Execution**: Added sprint/backlog references and created this task file with
explicit external prerequisites and verification criteria.
**Output**: Formal migration task coverage aligned to the reviewed runbook.
**Validation**: Pending `.agent_work` validator run after all task-tracking
edits complete.
**Next**: Re-review the Handoff-Planning docs and verify that every owner-gated
or migration-only step is now captured here rather than implied.

---

## Validation Results

### Test Summary
**Test Date**: Pending
**Test Environment**: Pending
**Test Status**: BLOCKED

### Acceptance Criteria Validation
- [ ] **Owner prerequisites confirmed**: Pending
- [ ] **History and tags pushed safely**: Pending
- [ ] **cdcai GHCR publication complete**: Pending
- [ ] **cdcai release recreated**: Pending
- [ ] **Post-transfer verification complete**: Pending
- [ ] **Backlog transfer destination completed**: Pending

### Issues Identified

- cdcai Issues enablement is not guaranteed, so backlog transfer needs a
  documented fallback destination.
- Registry-copy versus rebuild remains a live execution choice driven by
  permissions and available tooling.

### Sign-off

Pending