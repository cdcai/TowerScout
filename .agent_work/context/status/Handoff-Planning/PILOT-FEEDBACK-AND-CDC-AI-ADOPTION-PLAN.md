# TowerScout Pilot Feedback And cdcai Adoption Plan

**Decision Date**: July 10, 2026; rebaselined July 23, 2026
**Last Reconciled**: August 11, 2026
**Status**: CURRENT for the Pilot Package and cdcai hold
**Forward Development Plan**:
[`2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`](./2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md)
**Pilot Baseline**: validated fork-side `v0.1.2`
**Pilot Distribution**: completed July 13, 2026
**Operational Closeout**: October 30, 2026
**Hard Project End**: October 31, 2026

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
2. Complete required security, TLS, Exit/Stop, Podman, qualification,
   documentation, and handoff work in the fork.
3. Publish immutable candidates as `v0.1.3-rc.N`.
4. Continue to accept pilot feedback; blocker feedback takes priority.
5. Freeze a final candidate only after required gates pass.
6. Have the project lead and cdcai owner qualify the candidate.
7. Select the final cdcai tag and display title before the official build.
8. Execute Task-089 only after explicit owner adoption approval.

Task-087 may resume for the new candidate only after the Tasks 090/098 security
gate passes. This does not change the Pilot Package and does not authorize
enabling unvalidated behavior for pilot users.

Tasks 090/098 passed on July 27 and remain completed historical records.
GitHub disclosed four additional Dependabot advisories on August 4-5, and the
blocking npm audit added `GHSA-5p4m-2wfm-xmqj` on August 7 while Task-099 was
still active. Task-099 completed that follow-up on August 11 through PRs
#68/#69, successful main CI and root graph refresh, and alert closure without
dismissal. The inventory is back to the eight documented torch residuals.
Task-087 continues under its own remaining qualification gates.

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

- Task-087: guided Google/Azure application-provider TLS repair on Docker and
  Podman.
- Task-088: completed Pilot Package distribution and custody.
- Task-089: owner-gated cdcai adoption and ownership transfer.
- Task-090: completed bounded runtime/custom-image/dependency security
  investigation, including the 62-alert Trivy baseline.
- Tasks 091-095: qualification, docs, recovery, evidence-gated support, and
  governance/handoff.
- Task-096: user-confirmed Exit/Stop.
- Task-097: Podman CPU/GPU final-path qualification.
- Task-098: completed July 27 dependency remediation, compatibility
  validation, and release-risk disposition through PR #51 / `e499b50`.
- Task-099: completed August 11 for alerts `#72-#75` plus npm finding
  `GHSA-5p4m-2wfm-xmqj`; the critical/high gate and default-branch inventory
  reconciliation passed without reopening Task-098.

## Superseded Instructions

This plan supersedes earlier immediate-migration instructions, the earlier
"wait before selecting implementation" state, and any plan to use `v0.1.2` as
the automatic cdcai baseline. Older documents remain archived as historical
evidence.
