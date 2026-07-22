# TASK-089: cdcai Adoption Preparation And Deferred Ownership Transfer

**Status**: DEFERRED / OWNER-GATED - do not change cdcai until pilot feedback is reviewed and the owner approves an adoption baseline
**Priority**: HIGH
**Type**: C
**Estimated Effort**: 0.5-1 day preparation now; 1-2 days execution after adoption approval
**Target Sprint**: Sprint 07
**Created**: 2026-07-08
**Owner**: TowerScout release owner / active agent support with cdcai maintainer participation
**Depends On**: completed `TASK-088` pilot closeout; pilot feedback review; explicit cdcai-owner adoption approval; cdcai write/package permissions at execution time; approved durable backlog destination

## Objective

Prepare a safe, reviewable adoption package without changing
`cdcai/TowerScout` during the pilot feedback hold. After feedback is reviewed
and the cdcai owner explicitly approves the version to adopt, transfer the
selected history, tags, image ownership, release assets, and durable context
without breaking source provenance or digest-pinned package behavior.

## Canonical Planning Sources

- `.agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`
- `.agent_work/context/status/Handoff-Planning/TowerScout-Implementation-Strategy.md` (historical release/migration runbook)
- `.agent_work/context/status/Handoff-Planning/TowerScout-Handoff-Review-Comprehensive-Analysis.md` (historical evidence base)

The pilot/adoption plan controls timing and authorization. The historical
runbook still supplies technical migration guardrails, but its July dates,
immediate-execution sequence, and `v0.1.0` commands are superseded. `TASK-089`
tracks preparation now and owner-approved execution later.

## Requirements (EARS Notation)

- WHEN migration execution begins, THE SYSTEM SHALL preserve git-source
  provenance, release-tag traceability, and digest-pinned package correctness.
- WHILE pilot feedback is pending, THE SYSTEM SHALL keep `cdcai/TowerScout`
  unchanged and SHALL NOT push source, tags, releases, images, issues, or
  repository banners there without explicit owner approval.
- WHEN the pilot is distributed, THE SYSTEM SHALL treat the fork-side
  `v0.1.2` release as the pilot download and SHALL NOT imply that the unchanged
  cdcai repository contains that pilot baseline.
- WHEN pilot feedback is collected, THE PROJECT SHALL maintain it in the
  project lead's fillable Word document outside the repository and SHALL notify
  the development team of actionable findings.
- IF feedback requires a package fix before adoption, THEN THE SYSTEM SHALL use
  a new fork-side version identity and validate the affected release surfaces.
- IF the project ends before adoption, THEN THE SYSTEM SHALL leave the cdcai
  owner a migration-ready handoff without modifying the official repository.
- WHEN selected history and tags are pushed to `cdcai/TowerScout`, THE SYSTEM
  SHALL avoid force-push, squash-merge, and bulk `--tags` behavior.
- WHEN runtime images are republished or copied to `ghcr.io/cdcai`, THE SYSTEM
  SHALL either preserve the validated digest or re-anchor validation against the
  new digest and rebuilt packages.
- WHEN the cdcai-side rebuild uses the owner-approved tagged tree, THE SYSTEM
  SHALL either explicitly accept fork-facing release URLs and image defaults in
  the cdcai-rebuilt packages with release-note disclosure, or use a later
  documented rewrite/point-release path instead of silently changing tag
  meaning.
- WHEN fork-side release publication moves to a follow-on stable identifier
  after `v0.1.0` tag-only history is preserved, THE SYSTEM SHALL treat that
  follow-on release as the migration baseline and SHALL NOT push the historical
  asset-less `v0.1.0` tag to cdcai as if it were the validated stable release.
- WHEN the fork-side `v0.1.2` release line has passed validation, THE SYSTEM
  SHALL treat `v0.1.2` as the current pilot baseline, not an automatically
  approved cdcai migration baseline. The owner may approve `v0.1.2` or a later
  validated successor after feedback review.
- WHEN backlog transfer is attempted, THE SYSTEM SHALL use cdcai Issues only if
  they are enabled, otherwise it SHALL use an explicitly approved alternate
  durable destination.
- WHEN cdcai release recreation completes, THE SYSTEM SHALL verify the rebuilt
  artifacts, public pulls, source traceability, and a clean package smoke path.

## Acceptance Criteria

- [x] The cdcai owner's feedback hold is recorded: the official repository
      remains unchanged until pilot feedback and adoption review complete.
- [x] The external Word-document feedback method and primary/backup support
      coverage are confirmed with appropriate access.
- [ ] A migration-ready handoff packet records the candidate source ref,
      selected tags, image/package choices, evidence, backlog, and verification
      sequence without executing them against cdcai.
- [ ] The cdcai owner explicitly approves the adoption baseline after feedback.
- [ ] cdcai collaborator write and package-publish ownership are confirmed for
      the approved execution window.
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
  asset-less `v0.1.0` and `v0.1.1` tags and instead uses the validated
  owner-approved baseline (`v0.1.2` or a later validated successor).
- [ ] Backlog transfer lands in cdcai Issues or an explicitly approved
      alternate durable destination.

## Dependencies

- `TASK-088` completed pilot distribution readiness and durable handoff
  custody on 2026-07-22.
- Pilot feedback must be collected and reviewed.
- The cdcai owner must explicitly approve the version to adopt; technical
  access alone does not authorize migration.
- cdcai maintainer decisions are required for collaborator write, GHCR package
  ownership, release publication, and issue-tracker destination.
- Registry copy versus rebuild must be decided based on the available tooling
  and permissions at execution time.

## Implementation Plan

1. Prepare the migration-ready handoff and record the exact candidate inputs;
   do not change cdcai.
2. Wait for pilot feedback review and explicit owner adoption approval.
3. Confirm execution-time repository, Actions, package, and feedback/backlog
   ownership.
4. Push only the approved history/tag set using the reviewed non-destructive
   sequence.
5. Copy or rebuild images under cdcai ownership and rebuild packages as needed.
6. Recreate the approved cdcai release and verify it from a fresh consumer
   path.
7. Transfer durable backlog/handoff context and close out the fork transition.

## Prepared Inputs During Feedback Hold

- Candidate baseline: fork-side `v0.1.2` at
  `718a56485a59182f060a537e8f11d4ce71a1f0d4`.
- Candidate release: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`.
- Historical `v0.1.0` and `v0.1.1` tags are not candidate adoption releases.
- Pilot intake, triage, and custody template:
  `.agent_work/context/status/Handoff-Planning/PILOT-OPERATIONS-PACKET.md`.
- Execution remains blocked by feedback review, baseline approval, repository
  and package permissions, and the approved durable backlog destination.

These inputs make the no-extension handoff migration-ready without performing
or implying any change to `cdcai/TowerScout`.

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

### 2026-07-08 - Historical v0.1.1 Disposition Added
**Objective**: Prevent the cdcai migration path from inheriting a second
tag-only release identity after PR #48 landed and the fork-side release line
moved again.
**Context**: The fork now has public historical `v0.1.0` and `v0.1.1` tags
with published images but no final GitHub Release assets. The active stable
publication path has advanced to `v0.1.2` after the post-merge Docker
image-identity fix.
**Decision**: Treat both `v0.1.0` and `v0.1.1` as historical fork-only tags
for traceability. Task-089 should migrate the validated `v0.1.2` release line
instead of carrying either historical tag into `cdcai/TowerScout` as the
stable baseline.
**Execution**: Recorded the `v0.1.1` historical-tag disposition in this task
file alongside the existing `v0.1.0` rule.
**Output**: The migration task now explicitly names the set of fork-side tags
that should remain historical and the `v0.1.2` line that should become the
cdcai stable baseline if validation and publication complete.
**Validation**: Pending later cdcai execution.
**Next**: After `v0.1.2` D4 validation and release publication complete,
record the exact tag/image/checksum set that Task-089 will recreate under
cdcai ownership.

### 2026-07-09 - v0.1.2 Validation Baseline Recorded
**Objective**: Update the blocked cdcai migration task with the exact validated
fork-side release baseline now that D4/full-matrix validation has passed.
**Context**: `v0.1.2` passed the validation prerelease matrix on 2026-07-09.
The cdcai owner-side blockers are unchanged, but the migration target is no
longer an unnamed follow-on release line.
**Decision**: Treat `v0.1.2` as the selected migration baseline unless a later
release-owner decision supersedes it with new validation evidence.
**Execution**: Recorded the validated source ref, image digests, asset checksum,
and release-evidence location in this task.
**Output**: Task-089 now points at:
- source ref `718a56485a59182f060a537e8f11d4ce71a1f0d4`
- CPU image digest
  `sha256:86c54bd723ff970f70f0883397a1f2f804db796507a461a5718aeab57258afe8`
- CUDA image digest
  `sha256:bab2eda26fa6cf0483780cfcdb0a10008fb67fe058ba99a28ebdd6212fda2214`
- shared asset ZIP checksum
  `00599cc4fe9f2bdb4708c669d7c3d9a8a570a0c3b547bc5c317026196c7bacbb`
- validation evidence under
  `.agent_work/context/status/Handoff-Planning/v0.1.2-Validation-Evidence/`
**Validation**: Evidence verdict is PASS in
`V012-FULL-MATRIX-QA-2026-07-09.md`; Task-089 remains blocked on cdcai access,
GHCR/package ownership, and backlog destination decisions.
**Next**: After the fork-side `v0.1.2` release is promoted/published, preserve
the final release URL and checksums here, then execute migration only after the
owner-side prerequisites are confirmed.

### 2026-07-09 - Fork-Side v0.1.2 Release URL Recorded
**Objective**: Preserve the published fork-side stable release URL that will
anchor later cdcai recreation or migration work.
**Context**: Task-088 promoted the validation prerelease in place after the
full matrix passed.
**Decision**: Treat the published fork-side `v0.1.2` release as the migration
source of truth until cdcai owner-side prerequisites allow recreation under
cdcai ownership.
**Execution**: Recorded the final release URL and verified state from GitHub.
**Output**: Published release:
`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`.
The release is titled `TowerScout v0.1.2`, is not a draft, is not a prerelease,
and is listed as latest.
**Validation**: `gh release view` confirmed the six validated assets remained
attached after promotion, and `gh release list` showed `TowerScout v0.1.2` as
`Latest`.
**Next**: Keep Task-089 blocked until cdcai collaborator write, GHCR/package
ownership, and backlog destination prerequisites are confirmed.

### 2026-07-10 - Migration Execution Deferred Pending Pilot Adoption Decision
**Objective**: Align Task-089 with the cdcai owner's request to preserve the
current official repository until user feedback is available.
**Context**: The validated fork-side `v0.1.2` package is scheduled for pilot
distribution on 2026-07-13. The project may end on 2026-07-15 or receive a
three-month extension, but neither outcome justifies overwriting the official
cdcai repository before the owner knows whether the pilot baseline needs fixes.
**Decision**: Keep `cdcai/TowerScout` unchanged during the feedback hold.
Reclassify `v0.1.2` as the current validated pilot baseline rather than an
automatically approved migration baseline. Prepare the handoff now, but execute
source/tag/image/release/backlog transfer only after feedback review and
explicit cdcai-owner adoption approval.
**Execution**: Added the canonical pilot/adoption plan and revised Task-089's
objective, requirements, gates, acceptance criteria, and implementation order.
**Output**: Task-089 now separates reversible preparation from the later
state-changing adoption step and supports both the extension and no-extension
project outcomes.
**Validation**: On `docs/task-088-pilot-feedback-handoff` from
`origin/main@718a564`, `.agent_work` validation passed, `git diff --check`
passed, the runtime/test diff remained clean, and the docs route suite passed
(`57 passed`).
**Next**: Record the owner-controlled feedback destination and backup owner,
prepare the migration-ready packet, and wait for the adoption decision.

### 2026-07-22 - Pilot Prerequisites And Extension Recorded
**Objective**: Update Task-089 prerequisites without beginning migration or
selecting new implementation work.
**Context**: The pilot email has been sent, feedback is maintained by the
project lead in an external fillable Word document, primary and backup support
contacts have appropriate access, and Task-088 is complete. The project ends
2026-10-31.
**Decision**: Close the feedback/support prerequisite while retaining all
adoption, permission, package-publication, and post-transfer verification
gates. The extension does not authorize cdcai changes.
**Execution**: Updated the Task-089 dependency and acceptance records and linked
them to the completed Task-088 launch/custody record.
**Output**: Task-089 remains deferred and owner-gated for feedback review and
explicit adoption approval.
**Validation**: Agent-work validation and `git diff --check` passed; no runtime
or test files changed; and the Flask docs/route contract suite passed
(`57 passed`).
**Next**: Wait for the project lead's actionable feedback summary and the
cdcai owner's adoption decision.

---

## Historical Implementation Log

The entry below records the task's original 2026-07-08 blocked/access-gated
state. It is superseded by the 2026-07-10 feedback-hold decision above and does
not authorize current migration execution.

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
**Test Status**: DEFERRED pending pilot feedback and owner adoption approval

### Acceptance Criteria Validation
- [x] **Owner feedback hold recorded**: cdcai remains unchanged during pilot
- [x] **Feedback/support method confirmed**: External fillable Word document;
      primary and backup support contacts confirmed with appropriate access
- [ ] **Migration-ready handoff packet completed**: Pending
- [ ] **Adoption baseline approved**: Pending feedback review
- [ ] **Execution permissions confirmed**: Pending approved execution window
- [ ] **History and tags pushed safely**: Pending
- [ ] **cdcai GHCR publication complete**: Pending
- [ ] **cdcai release recreated**: Pending
- [ ] **Post-transfer verification complete**: Pending
- [ ] **Backlog transfer destination completed**: Pending

### Issues Identified

- cdcai Issues enablement is not guaranteed, so backlog transfer needs a
  documented owner-controlled destination. Issues are not required during the
  feedback hold while the owner wants cdcai unchanged.
- Registry-copy versus rebuild remains a live execution choice driven by
  permissions and available tooling.
- The current pilot baseline is `v0.1.2`; the final migration baseline may be
  `v0.1.2` or a later validated successor selected after feedback.
- Technical access is no longer the first gate. Pilot feedback review and
  explicit owner adoption approval come first.

### Sign-off

Pending pilot feedback review, owner adoption approval, and later migration
execution/verification.
