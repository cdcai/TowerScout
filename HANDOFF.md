# TowerScout Handoff Guide

**Last Updated**: August 19, 2026
**Operational Closeout**: October 30, 2026
**Hard Project End**: October 31, 2026

## Current State

The validated fork-side `v0.1.2` release is the immutable Pilot Package:

`https://github.com/J-Schulein/TowerScout/releases/tag/v0.1.2`

The cdcai owner selected a fix-first path:

- Keep pilot users on unchanged `v0.1.2`.
- Develop and qualify new candidates in `J-Schulein/TowerScout`.
- Name fork candidates `v0.1.3-rc.N`.
- Keep `cdcai/TowerScout` unchanged until owner qualification and explicit
  adoption approval.
- Select the official cdcai tag and display title before the official build.

The canonical forward plan is:

- `.agent_work/context/status/Handoff-Planning/2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md`

The current Pilot/cdcai hold is:

- `.agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md`

## Required Final Scope

- Task-090 runtime/custom-image/dependency security investigation: complete
- Task-098 approved dependency remediation and release-risk disposition:
  complete through PR #51 / `e499b50` with its exact July 27 closeout state
- Task-099 August dependency-advisory follow-up: complete through PRs #68/#69
  and `f460445`/`0133b50`; main CI and the root dependency graph passed,
  alert `#74` closed without dismissal, and its August 11 closeout inventory
  contained the eight documented torch residuals
- Task-101 high-severity development-transitive `extract-zip` remediation and
  release-gate disposition: PR #72 implementation-head checks pass; final PR,
  default-branch alert, and PR #67 gates remain active before Task-087 resumes
- Task-087 Google/Azure guided provider TLS repair on Docker/Podman: paused on
  Task-101 while Draft PR #67 remains open for reviewer input
- Task-096 user-confirmed Exit/Stop on Docker/Podman
- Task-097 Podman CPU/GPU final-path qualification
- Docker CPU, Docker GPU, Podman CPU, and Podman GPU qualification
- owner-runnable qualification, documentation, recovery, governance, backlog,
  and handoff work
- external Setup Guide and demo video refresh

Task-058/059 are conditional stretch work and cannot displace required scope.

## Reading `.agent_work`

1. `.agent_work/current-tasks.md`
2. canonical roadmap linked above
3. Pilot/cdcai plan linked above
4. `.agent_work/task-backlog.md`
5. `.agent_work/requirements.md`
6. `.agent_work/design.md`
7. `.agent_work/completed-tasks.md`
8. `.agent_work/tasks/active/` and `.agent_work/tasks/completed/`
9. `.agent_work/decisions/`

Superseded handoff strategies, July roadmap iterations, release checklists, and
external reviews are under
`.agent_work/context/archive/2026-07/Handoff-Planning/`.

The July 23 code-scanning baseline is recorded in
`.agent_work/context/analysis/GITHUB-CODE-SCANNING-READINESS-ASSESSMENT-2026-07-23.md`.
Task-098's merged closeout and the eight documented medium/low torch residuals
are recorded in
`.agent_work/tasks/active/TASK-098-dependency-security-remediation.md`.
Task-099 records the completed post-closeout advisory remediation, including
the later js-yaml npm audit finding and root graph reconciliation, in
`.agent_work/tasks/active/TASK-099-august-dependency-advisory-follow-up.md`.
Alert `#76` opened after that closeout and is owned by active Task-101 in
`.agent_work/tasks/active/TASK-101-extract-zip-advisory-release-gate.md`.
Task-087 remains preserved and reviewable in PR #67, but new implementation,
merge, and candidate publication wait for PR #72 merge, alert `#76` closure
without dismissal, semantic integration into PR #67, and green checks at that
branch's new exact head. Its other package, signing, provider/recovery, Podman,
and representative managed-endpoint gates remain closed.

## Runtime And Package Model

Normal release delivery uses:

- GitHub Release control package
- digest-pinned GHCR image
- checksummed shared Model & Data Package
- Docker- and Podman-compatible Compose paths

The final support matrix requires:

- Docker CPU
- Docker GPU
- Podman CPU
- Podman GPU/CDI

The existing Pilot validation record remains under
`.agent_work/context/status/Handoff-Planning/v0.1.2-Validation-Evidence/`.
Future candidates require new evidence.

## Runtime Startup Coordination

Before runtime-dependent work, the active agent must:

1. Tell the user whether Docker Desktop, Podman, or both are required.
2. Ask the user to start the required runtime.
3. Wait for confirmation before validation.
4. Allow time for a computer restart when Docker Desktop requires it.

Static review, planning, and documentation work do not require runtime startup.

## Safety And Custody

- Do not replace released `v0.1.2` assets.
- Do not publish `v0.1.3` final prematurely.
- Do not modify cdcai without explicit owner authorization.
- Do not mount Docker/Podman sockets into the application container.
- Do not delete named volumes during normal stop or upgrade.
- Do not store provider keys, helper tokens, certificate details, private AOIs,
  raw traces, or unsanitized logs in repository evidence.

The Model & Data Package cannot be reconstructed from source alone. Preserve
release assets, SHA-256 sidecars, `webapp/asset_manifest.v1.json`, and
`docs/release/release-asset-bundle-contract.md`.

## Final Handoff Gate

Before October 30:

- final candidate is qualified and accepted
- official cdcai identity is selected and built consistently
- release, rollback/reject, recovery, and cleanup are rehearsed by the owner
- repository, Actions, package, documentation, video, and backlog custody are
  confirmed
- tool-neutral maintenance guidance is complete
- remaining tasks and risks are explicitly dispositioned
- every code-scanning alert is dispositioned and no release-blocking
  critical/high dependency risk remains unresolved
- no planned work depends on the outgoing developer after October 31
