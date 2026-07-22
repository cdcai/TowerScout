# TowerScout Pilot Feedback And cdcai Adoption Plan

**Decision Date**: 2026-07-10; updated 2026-07-22
**Status**: CURRENT - canonical release-transition and ownership plan
**Decision Owner**: TowerScout project lead with the `cdcai/TowerScout` owner
**Pilot Baseline**: validated fork-side `v0.1.2` release
**Pilot Distribution**: completed Monday, 2026-07-13
**Project End**: 2026-10-31 (hard end date; operational closeout 2026-10-30)

## Decision

Keep `cdcai/TowerScout` unchanged while the `v0.1.2` pilot is distributed and
user feedback is collected. The existing cdcai repository remains the official
repository for the currently adopted application. It must not be overwritten,
repointed, or presented as the source of the pilot package before the cdcai
owner reviews the pilot results and approves an adoption baseline.

Use the exact validated fork-side release as the pilot distribution:

- pilot download: `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`
- source ref: `718a56485a59182f060a537e8f11d4ce71a1f0d4`
- release assets: the existing six checksum-verified `v0.1.2` assets
- pilot description: **TowerScout v0.1.2 validated pilot release**

Do not rebuild, rename, replace, or silently modify the `v0.1.2` release assets
for the pilot. Any accepted fix must use a new version identity.

## Repository Roles During The Pilot

### `cdcai/TowerScout`

- Remains unchanged until the owner approves adoption after reviewing feedback.
- Continues to represent the application version currently adopted by cdcai.
- Must not be used as the pilot download location.
- Receives no source, tags, releases, images, backlog issues, or repository
  banner changes during the feedback hold unless the owner explicitly changes
  this decision.

### `J-Schulein/TowerScout`

- Hosts the exact validated `v0.1.2` pilot package and validation record.
- Remains the pilot development and fix-validation surface during the hold.
- Must be retained as a release/provenance archive even after later adoption.
- May produce a new pilot patch only when feedback justifies a change and the
  change receives proportionate package validation.

### Feedback And Support Channel

- Pilot feedback is captured by the project lead in a fillable Word document
  outside this repository.
- Feedback intake and tracking are not duplicated in `.agent_work`.
- The primary pilot support owner and backup contact are confirmed and have
  appropriate access.
- Their identities and contact details remain in the sent pilot communication
  and access-controlled project records, not in this public repository.

Do not enable cdcai Issues merely to satisfy the earlier migration plan while
the owner wants the official repository unchanged. Issues may be enabled later
as part of the adoption decision.

## Pilot Distribution Completion

1. The existing `v0.1.2` release and six-asset checksum record are frozen.
2. The pilot email was sent to the user group on 2026-07-13 and identifies the
   fork-side validated pilot rather than the unchanged cdcai repository.
3. The primary and backup support owners are confirmed with appropriate access.
4. Release assets, checksums, validation summaries, known findings, and
   troubleshooting material have durable custody through the public release
   and repository documentation.
5. `TASK-088` is complete. `TASK-089` remains preparation-only until feedback
   review and explicit owner adoption approval.

## During The Feedback Hold

- The project lead maintains feedback in the external fillable Word document
  and will notify the development team of actionable findings.
- Keep the cdcai repository unchanged.
- Do not enable the dark Task-087 browser-to-host repair flow as part of pilot
  support.
- If a fix is necessary, implement and validate it in the fork under a new
  version such as `v0.1.3`; never replace the existing `v0.1.2` bytes.

## Adoption Decision After Feedback

The cdcai owner selects one of these outcomes.

### Outcome A - Adopt The Validated Baseline

If feedback finds no adoption-blocking issue, approve `v0.1.2` or a reviewed
successor as the cdcai migration baseline, then execute `TASK-089`.

### Outcome B - Fix Before Adoption

If feedback identifies important defects, keep cdcai unchanged, fix and
validate a new fork-side pilot version, and adopt only the corrected baseline.

### Outcome C - Do Not Adopt Yet

If the pilot is not ready, preserve the fork, evidence, feedback, and prepared
handoff material. The owner can resume adoption work later without changing the
current cdcai repository.

## Confirmed Extension And Closeout Boundary

The project is extended through 2026-10-31. Use 2026-10-30 as the operational
closeout date because October 31 falls on a Saturday. This update does not
select the next implementation work.

- Continue to use new release identities for every changed package set.
- Keep the fork as the pilot and fix-validation surface until the owner
  approves an adoption baseline.
- Move official development and releases to cdcai only after approved adoption
  and migration validation.
- Complete final release, evidence, backlog, and operational ownership handoff
  before the operational closeout date.

## Task Ownership

- `TASK-088` owns pilot distribution readiness, guide/support wording,
  evidence custody, and fork-side closeout.
- `TASK-089` owns migration preparation now and migration execution only after
  pilot feedback plus explicit cdcai-owner adoption approval.
- `TASK-087` remains dark and deferred unless separately selected after the
  pilot/release transition.

## Superseded Instructions

This plan supersedes any earlier instruction to migrate immediately after
release publication or as soon as repository/package permissions become
available. Earlier strategy, decision, checklist, and review documents remain
valuable historical evidence, but their migration dates and `v0.1.0`/
`v0.1.1` execution commands are not current instructions.
