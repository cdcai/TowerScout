# TowerScout Pilot Feedback And cdcai Adoption Plan

**Decision Date**: July 10, 2026; rebaselined July 23, 2026
**Last Reconciled**: September 22, 2026
**Status**: CURRENT for the Pilot Package and cdcai hold
**Forward Development Plan**:
[`2026-09-21-windows-deployment-hardening-v2.md`](../Reprioritization%20Effort/2026-09-21-windows-deployment-hardening-v2.md)
**Pilot Baseline**: validated fork-side `v0.1.2`
**Pilot Distribution**: completed July 13, 2026
**Operational Closeout**: October 30, 2026
**Hard Project End**: October 31, 2026

The pilot and cdcai hold remain unchanged. For current development, PR #67 and
Task-087/096 launcher work are preserved but deferred and are not dependencies
of the main-based package qualification.

## Pilot Decision

Keep `cdcai/TowerScout` unchanged while users test the `v0.1.2` Pilot Package
and while the fork develops and qualifies a fix-first successor.

Pilot identity:

- Download:
  `https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`
- Source ref: `718a56485a59182f060a537e8f11d4ce71a1f0d4`
- Assets: existing six checksum-verified `v0.1.2` release assets
- Description: **TowerScout v0.1.2 validated pilot release**

Do not rebuild, rename, replace, or silently modify these assets.

## Repository Roles

### `J-Schulein/TowerScout`

- Hosts the immutable Pilot Package.
- Hosts new development and `v0.1.3-rc.N` candidates.
- Retains pilot and source-provenance history after handoff.

### `cdcai/TowerScout`

- Continues to represent the currently adopted application.
- Is not the `v0.1.2` pilot download.
- Receives no new source, tags, releases, images, issues, or banner changes
  during the hold without explicit owner authorization.
- Will host the official final release after qualification and adoption.

## Feedback And Support

- The project lead maintains feedback in a fillable Word document outside the
  repository and will notify the development team of actionable findings.
- `.agent_work` does not duplicate intake or tracking.
- Primary and backup support owners are confirmed with appropriate access.
- Their contact details remain in the sent communication and access-controlled
  records, not this public repository.

## Fix-First Development During The Pilot

The cdcai owner selected the fix-first path:

1. Preserve `v0.1.2`.
2. Execute the main-based W00-W10 deployment, qualification, documentation,
   and handoff work through the existing command-based package path. PR #67
   launcher/TLS-control and Task-096 browser Exit work remain deferred.
3. Publish immutable candidates as `v0.1.3-rc.N`.
4. Continue to accept pilot feedback; blocker feedback takes priority.
5. Freeze a final candidate only after required gates pass.
6. Have the project lead and cdcai owner qualify the candidate.
7. Select the final cdcai tag and display title before the official build.
8. Execute Task-089 only after explicit owner adoption approval.

The original July Task-087 resume sequence is preserved as history, not as the
current release gate. Tasks 090/098 passed on July 27, Task-099 completed its
post-closeout advisory follow-up on August 11, and Task-101's focused PR #72
remediation later merged as `0cc189c`; alert `#76` closed as fixed without
dismissal and exact-main checks passed. ADR-021 supersedes Task-101's former
downstream PR #67 integration condition. Task-087/PR #67 evidence remains valid
for the bytes it evaluated, but the launcher work receives no new merge,
reconciliation, implementation, or review work during this delivery window.

## Release Naming Boundary

- `v0.1.3-rc.N` is the fork candidate convention.
- No `v0.1.3` final release is implied or authorized by that convention.
- The final cdcai tag and display title are decided before the official build.
- The official image, package, manifests, checksums, filenames, and docs must
  be rebuilt consistently; candidate ZIPs are not simply renamed.

## Adoption Gate

Task-089 remains blocked until:

1. Pilot feedback and candidate findings are reviewed.
2. Required four-profile qualification passes.
3. The project lead and cdcai owner qualify the final candidate.
4. The owner explicitly approves adoption.
5. Repository, Actions, package, release, and backlog ownership are ready.
6. The official identity and rebuild/verification plan are approved.

If the final candidate is not ready, preserve the fork, evidence, feedback,
backlog, and migration-ready handoff without changing cdcai.

## Task Ownership

- Task-087: preserved and deferred launcher/guided-repair history; not a
  current release dependency.
- Task-088: completed Pilot Package distribution and custody.
- Task-089: owner-gated cdcai adoption and ownership transfer.
- Task-090: completed bounded runtime/custom-image/dependency security
  investigation, including the 62-alert Trivy baseline.
- Tasks 091-095: qualification, docs, recovery, evidence-gated support, and
  governance/handoff.
- Task-096: deferred browser Exit/helper design; use the tested command-based
  stop/start lifecycle.
- Task-097: Podman CPU/GPU final-path qualification.
- Task-098: completed July 27 dependency remediation, compatibility
  validation, and release-risk disposition through PR #51 / `e499b50`.
- Task-099: completed August 11 for alerts `#72-#75` plus npm finding
  `GHSA-5p4m-2wfm-xmqj`; the critical/high gate and default-branch inventory
  reconciliation passed without reopening Task-098.
- Task-101: completed focused remediation on accepted `main`; its former PR
  #67 reconciliation/exact-head condition is superseded rather than passed.

## Superseded Instructions

This plan supersedes earlier immediate-migration instructions, the earlier
"wait before selecting implementation" state, and any plan to use `v0.1.2` as
the automatic cdcai baseline. Older documents remain archived as historical
evidence.
