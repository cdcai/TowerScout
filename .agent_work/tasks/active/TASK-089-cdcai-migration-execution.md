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
- WHEN the cdcai-side rebuild still uses the tagged `v0.1.0` tree, THE SYSTEM
  SHALL either explicitly accept fork-facing release URLs and image defaults in
  the cdcai-rebuilt packages with release-note disclosure, or use a later
  documented post-tag rewrite or point-release path instead of silently
  changing tag meaning.
- WHEN fork-side release publication moves to a follow-on stable identifier
  after `v0.1.0` tag-only history is preserved, THE SYSTEM SHALL treat that
  follow-on release as the migration baseline and SHALL NOT push the historical
  asset-less `v0.1.0` tag to cdcai as if it were the validated stable release.
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
- [ ] The chosen cdcai package-facing release URL and image-default strategy is
  explicitly recorded and, if fork-facing values remain in the tagged tree,
  disclosed in the cdcai release notes.
- [ ] The selected cdcai migration tag/image set excludes the historical
  asset-less `v0.1.0` tag and instead uses the post-fix validated stable
  release line.
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

### 2026-07-08 - Namespace Carry-Forward Decision Recorded
**Objective**: Close the gap between Task-088's fork-side release-home decision
and Task-089's later cdcai rebuild responsibilities before the stable tag
exists.
**Context**: Task-088 intentionally keeps the fork-side stable release URLs and
image defaults on the J-Schulein side for the fork `v0.1.0` cut. Without an
explicit Task-089 follow-through rule, that choice would silently carry into a
later cdcai rebuild from the same tagged tree.
**Decision**: If Task-089 rebuilds cdcai packages directly from the tagged
`v0.1.0` tree, fork-facing URLs and image defaults are explicitly accepted as a
known carry-forward and must be disclosed in the cdcai release notes. A later
namespace rewrite may still happen in a post-tag follow-up or point release,
but it must not silently redefine what the `v0.1.0` tag means.
**Execution**: Added requirement and acceptance-criterion coverage for the
namespace carry-forward decision.
**Output**: The namespace consequence is now owned by Task-089 instead of
falling between the fork-side and cdcai-side task files.
**Validation**: Pending later cdcai execution.
**Next**: Preserve the fork-side stable release wording through the tag/build
flow, and revisit the cdcai-facing package wording only during Task-089.

### 2026-07-08 - Historical v0.1.0 Disposition Added
**Objective**: Prevent the cdcai migration path from inheriting a misleading
stable tag if the fork-side release line moves to a follow-on post-fix stable
identifier.
**Context**: The fork now has a public historical `v0.1.0` tag with published
images but no final release assets, while the agreed fork-side publication path
has shifted to a post-fix follow-on stable release (currently `v0.1.1`).
**Decision**: Treat the historical `v0.1.0` tag as fork-only history for
traceability and do not push it to `cdcai/TowerScout` as the stable migration
baseline. Task-089 should migrate the post-fix validated stable release line
instead.
**Execution**: Added requirement and acceptance-criterion coverage for the
historical `v0.1.0` disposition.
**Output**: The migration task now explicitly distinguishes between historical
fork tags and the actual validated stable line that should be recreated under
cdcai ownership.
**Validation**: Pending later cdcai execution.
**Next**: Once the follow-on stable release identifier is cut and validated,
record the exact tag/image set that Task-089 will push or recreate on the cdcai
side.

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
- If the fork publishes a follow-on stable release after `v0.1.0`, the exact
  cdcai tag/image set must be updated in the migration runbook before Task-089
  starts execution.

### Sign-off

Pending
